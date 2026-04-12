#!/usr/bin/env python3
"""
scan_acc_absolutes.py — Detect accusative absolute constructions.

The accusative absolute is a rare Greek construction (~5-10 instances in the
NT) where an impersonal neuter accusative participle stands as a grammatically
independent frame, much like a genitive absolute. Common examples:

    ἐξόν     ("it being permitted")     — from ἔξεστι
    δέον     ("it being necessary")     — from δεῖ
    δυνατόν  (with implicit ὄν)         — "it being possible"
    τυχόν    ("if it happens / perhaps")
    παρόν    ("it being present")
    ἀδύνατον ὄν                          — "being impossible"

We use MorphGNT to identify accusative neuter participles via the parsing
field: position [3]=mood (P=participle), [4]=case (A=accusative),
[6]=gender (N=neuter).

Output:
  - Total accusative neuter participles found
  - How many already sit alone on a line (correct treatment)
  - How many are absorbed into larger lines (need review)

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_acc_absolutes.py
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
OUTPUT_PATH = os.path.join(REPO_DIR, "private", "acc-absolute-scan.txt")

_FILE_MAP = {
    "61": "matt", "62": "mark", "63": "luke", "64": "john",
    "65": "acts", "66": "rom", "67": "1cor", "68": "2cor",
    "69": "gal", "70": "eph", "71": "phil", "72": "col",
    "73": "1thess", "74": "2thess", "75": "1tim", "76": "2tim",
    "77": "titus", "78": "phlm", "79": "heb", "80": "jas",
    "81": "1pet", "82": "2pet", "83": "1john", "84": "2john",
    "85": "3john", "86": "jude", "87": "rev",
}
_SLUG_TO_FILE = {v: k for k, v in _FILE_MAP.items()}


def _clean(word):
    """Strip punctuation and critical apparatus markers."""
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]',
        '',
        word,
    )


_verse_morph = {}


def _load_morphgnt(book_slug):
    """Return dict keyed by (chapter, verse) -> list of (cleaned, pos, parsing, lemma)."""
    if book_slug in _verse_morph:
        return _verse_morph[book_slug]
    file_num = _SLUG_TO_FILE.get(book_slug)
    if not file_num:
        _verse_morph[book_slug] = {}
        return {}
    filepath = None
    for fname in os.listdir(MORPHGNT_DIR):
        if fname.startswith(file_num + "-"):
            filepath = os.path.join(MORPHGNT_DIR, fname)
            break
    if not filepath:
        _verse_morph[book_slug] = {}
        return {}

    verses = defaultdict(list)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, _text, word, _norm, lemma = parts
            ch = int(ref[2:4])
            vs = int(ref[4:6])
            cleaned = _clean(word)
            if cleaned:
                verses[(ch, vs)].append((cleaned, pos, parsing, lemma))
    _verse_morph[book_slug] = dict(verses)
    return dict(verses)


# Lemmas that form impersonal participles used in accusative absolute
# constructions. This is essentially a closed list — the accusative absolute
# is rare and conventional. NOTE: MorphGNT lemma forms are quirky:
#   - ἔξεστι is stored as "ἔξεστι(ν)"
#   - δεῖ is stored as "δέω" (the active verb root that supplies impersonal δεῖ)
# Be sure to use the lemma exactly as MorphGNT records it.
IMPERSONAL_LEMMAS = {
    "ἔξεστι(ν)",  # ἐξόν   "it being permitted"
    "δέω",         # δέον   "it being necessary"  (MorphGNT lemma quirk)
    "τυγχάνω",    # τυχόν  "perhaps / if it happens"
    "πάρειμι",    # παρόν  "it being present"
    "πρέπω",      # πρέπον "it being fitting"
    "δοκέω",      # δόξαν  "it seeming good" (rare)
}

# The MorphGNT lemma "δέω" actually covers two homographic verbs:
#   1. δέω "bind" (transitive — perfect passive δεδεμένον "bound")
#   2. δεῖ  "it is necessary" (impersonal — participle δέον)
# Only the second is relevant. Restrict δέω hits to the participial form δέον.
ALLOWED_FORMS_BY_LEMMA = {
    "δέω": {"δέον"},
}

# Although the construction is called "accusative absolute," MorphGNT parses
# the impersonal forms ἐξόν / δέον as NOMINATIVE neuter singular (since the
# verbs are impersonal and take no subject). Real accusative-marked instances
# (παρόν Heb 12:11, τυχόν 1 Cor 16:6) are tagged accusative. We accept both
# nom-sg-neut and acc-sg-neut participles for the impersonal lemma set.
def _is_impersonal_ptc_form(pos, parsing):
    """Participle, neuter, singular, in nominative or accusative.

    MorphGNT parsing field positions:
        [3] mood     (P = participle)
        [4] case     (N or A acceptable)
        [5] number   (S = singular)
        [6] gender   (N = neuter)
    """
    if not pos.startswith("V"):
        return False
    if len(parsing) < 7:
        return False
    return (
        parsing[3] == "P"
        and parsing[4] in ("N", "A")
        and parsing[5] == "S"
        and parsing[6] == "N"
    )


def _line_words_with_morph(line_text, verse_words):
    """Walk line left-to-right, returning each Greek word with its morphology."""
    verse_queue = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        verse_queue[cw].append((pos, parsing, lemma))
    consumable = {k: list(v) for k, v in verse_queue.items()}

    result = []
    for raw in line_text.split():
        cleaned = _clean(raw)
        if not cleaned:
            continue
        entry = {
            "text": raw,
            "cleaned": cleaned,
            "pos": None,
            "parsing": None,
            "lemma": None,
            "is_impersonal_ptc_form": False,
            "is_impersonal_lemma": False,
            "is_article": False,
        }
        matches = consumable.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry.update(pos=pos, parsing=parsing, lemma=lemma)
            entry["is_impersonal_ptc_form"] = _is_impersonal_ptc_form(pos, parsing)
            entry["is_impersonal_lemma"] = lemma in IMPERSONAL_LEMMAS
            # RA = article in MorphGNT POS coding
            entry["is_article"] = pos == "RA"
        result.append(entry)
    return result


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)$")


def _parse_chapter(filepath):
    """Return list of {ref, chapter, verse, lines}."""
    verses = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            m = VERSE_REF_RE.match(stripped)
            if m:
                if current:
                    verses.append(current)
                current = {
                    "ref": stripped,
                    "chapter": int(m.group(1)),
                    "verse": int(m.group(2)),
                    "lines": [],
                }
                continue
            if current is None:
                continue
            current["lines"].append(line)
    if current:
        verses.append(current)
    return verses


def scan_all():
    """Scan every chapter for accusative neuter participles.

    Returns:
        standalone: list of dicts (participle is the only Greek word on the line)
        absorbed:   list of dicts (participle on a line with other content)
    """
    standalone = []
    absorbed = []

    for entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, entry)
        if not os.path.isdir(book_path):
            continue
        parts = entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else entry
        morph = _load_morphgnt(book_slug)

        for chapter_file in sorted(os.listdir(book_path)):
            if not chapter_file.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, chapter_file)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = morph.get((v["chapter"], v["verse"]), [])
                if not verse_words:
                    continue
                for line_text in v["lines"]:
                    words = _line_words_with_morph(line_text, verse_words)
                    if not words:
                        continue
                    for i, w in enumerate(words):
                        if not w["is_impersonal_ptc_form"]:
                            continue
                        if not w["is_impersonal_lemma"]:
                            continue
                        # For lemmas that homographically cover a non-impersonal
                        # verb (e.g. δέω "bind"), restrict to the impersonal
                        # participial form only.
                        allowed_forms = ALLOWED_FORMS_BY_LEMMA.get(w["lemma"])
                        if allowed_forms and w["cleaned"] not in allowed_forms:
                            continue
                        # Skip if directly preceded by an article — that's
                        # substantival ("the X"), not the impersonal frame use.
                        # e.g. τὸ παρόν "the present" in Heb 12:11.
                        if i > 0 and words[i - 1]["is_article"]:
                            continue
                        record = {
                            "file": chapter_file,
                            "ref": v["ref"],
                            "line": line_text.strip(),
                            "word": w["cleaned"],
                            "lemma": w["lemma"],
                            "case": w["parsing"][4] if w["parsing"] else "?",
                            "line_word_count": len(words),
                        }
                        if len(words) == 1:
                            standalone.append(record)
                        else:
                            absorbed.append(record)
    return standalone, absorbed


def format_report(standalone, absorbed):
    out = []
    total = len(standalone) + len(absorbed)
    out.append("=== ACCUSATIVE ABSOLUTE SCAN ===")
    out.append("")
    out.append(f"Total accusative neuter participles found: {total}")
    out.append(f"Already on own line: {len(standalone)}")
    out.append(f"Absorbed in larger lines (need review): {len(absorbed)}")
    out.append("")

    out.append("ABSORBED CASES:")
    if not absorbed:
        out.append("  (none)")
    else:
        for r in absorbed:
            out.append(f"{r['file']} {r['ref']}:")
            out.append(f"  {r['line']}")
            out.append(
                f"  participle: {r['word']} | lemma: {r['lemma']} "
                f"| case: {r['case']}"
            )
            out.append("")

    out.append("")
    out.append("STANDALONE CASES (already on own line — verify treatment):")
    if not standalone:
        out.append("  (none)")
    else:
        for r in standalone:
            out.append(f"{r['file']} {r['ref']}:")
            out.append(f"  {r['line']}")
            out.append(
                f"  participle: {r['word']} | lemma: {r['lemma']} "
                f"| case: {r['case']}"
            )
            out.append("")

    return "\n".join(out)


def main():
    standalone, absorbed = scan_all()
    report = format_report(standalone, absorbed)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(report)
    print()
    print(f"Full output saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
