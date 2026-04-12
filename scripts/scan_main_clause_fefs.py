#!/usr/bin/env python3
"""
scan_main_clause_fefs.py — Find main-clause participles without a main-clause
finite verb.

This catches the blind spot both participle_merge.py and scan_line_ending_
participles.py share: a line with a main-clause participle where the line
ALSO contains a finite verb — but that finite verb is inside a subordinate
clause (after ὅτι/ἵνα/ὅτε/etc.), so it doesn't resolve the participle.

Example — Matt 2:16:
    Τότε Ἡρῴδης ἰδὼν ὅτι ἐνεπαίχθη ὑπὸ τῶν μάγων   ← ἐνεπαίχθη is INSIDE the ὅτι clause
    ἐθυμώθη λίαν,                                   ← the real resolving verb

The main-clause participle ἰδών has no main-clause finite verb on line 1.
The resolving verb ἐθυμώθη is on line 2. This is an FEF that should merge.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_main_clause_fefs.py
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")

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

# Subordinators — any finite verb AFTER one of these on the same line is
# inside the subordinate clause and doesn't resolve a main-clause participle.
# (ὅτι excluded from recitative position — handled below)
SUBORDINATORS = {
    "ὅτι", "ἵνα", "ὅταν", "ὅτε", "ἐάν", "ὅπως", "ὥστε", "ὥσπερ",
    "μήποτε", "ἕως", "ὅπου", "καθώς", "ἡνίκα", "ἐπεί", "ἐπειδή",
    "πρίν", "ἄν",
}

# Speech lemmas — ὅτι after these is recitative, introduces direct speech
SPEECH_LEMMAS = {"λέγω", "ἀποκρίνομαι", "φημί", "γράφω", "φωνέω"}


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


def _is_participle(pos, parsing):
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "P"


def _is_finite(pos, parsing):
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in ("I", "S", "D", "O")


def _is_infinitive(pos, parsing):
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "N"


def _line_words_with_morph(line_text, verse_words):
    """Walk the line left-to-right and annotate each Greek word with morphology.

    Returns list of dicts: {text, cleaned, pos, parsing, lemma, is_ptc, is_fin, is_sub}
    where is_sub = True if the cleaned word is a subordinator.
    """
    # Build a consumable lookup of verse words (handle duplicates by position)
    verse_queue = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        verse_queue[cw].append((pos, parsing, lemma))
    # Copy per-word lists since we'll pop
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
            "is_ptc": False,
            "is_fin": False,
            "is_inf": False,
            "is_sub": cleaned in SUBORDINATORS,
        }
        matches = consumable.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry.update(pos=pos, parsing=parsing, lemma=lemma)
            entry["is_ptc"] = _is_participle(pos, parsing)
            entry["is_fin"] = _is_finite(pos, parsing)
            entry["is_inf"] = _is_infinitive(pos, parsing)
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


def analyze_line(line_text, verse_words, prev_line_text=None):
    """Return a flag dict if this line has a main-clause FEF pattern, else None.

    Pattern: line contains a participle BEFORE the first subordinator, and NO
    finite verb before that subordinator. Any finite verb on the line must be
    AFTER the subordinator (inside the subordinate clause), so it doesn't
    resolve the main-clause participle.
    """
    words = _line_words_with_morph(line_text, verse_words)
    if not words:
        return None

    # Find first subordinator index
    sub_idx = None
    for i, w in enumerate(words):
        if w["is_sub"]:
            # Skip recitative ὅτι after a speech lemma earlier on this line
            # (λέγων ὅτι, εἰπὼν ὅτι, etc. — the ὅτι just introduces quoted
            # speech and doesn't mark a subordinate clause boundary for FEF
            # analysis)
            if w["cleaned"] == "ὅτι":
                prev_on_line_lemmas = {
                    ww["lemma"] for ww in words[:i] if ww["lemma"]
                }
                if SPEECH_LEMMAS & prev_on_line_lemmas:
                    continue
            sub_idx = i
            break

    if sub_idx is None:
        return None  # no subordinator — handled by existing scanners

    # Main clause segment = words before the subordinator
    main_words = words[:sub_idx]
    if not main_words:
        return None  # subordinator at line start — line is all subordinate

    main_has_ptc = any(w["is_ptc"] for w in main_words)
    main_has_fin = any(w["is_fin"] for w in main_words)
    main_has_inf = any(w["is_inf"] for w in main_words)

    if not main_has_ptc:
        return None  # no main-clause participle
    if main_has_fin or main_has_inf:
        return None  # main clause already has its own verb

    # Heuristic: if there are MULTIPLE finite verbs after the subordinator,
    # the main clause likely resumes with one of them (e.g. Matt 2:16:
    # "ἰδὼν ὅτι ἐνεπαίχθη... ἐθυμώθη" — ἐνεπαίχθη is inside the ὅτι clause,
    # ἐθυμώθη is the main-clause resumption). Skip these to avoid false
    # positives. Only flag lines where the subordinate clause contains the
    # only finite verb(s) and there's no resumption signal.
    sub_words = words[sub_idx + 1:]
    sub_finite_count = sum(1 for w in sub_words if w["is_fin"])
    if sub_finite_count >= 2:
        return None  # main clause likely resumes on this line

    # Collect participle lemmas for reporting
    ptc_lemmas = [w["lemma"] for w in main_words if w["is_ptc"] and w["lemma"]]
    subordinator = words[sub_idx]["cleaned"]
    return {
        "participle_lemmas": ptc_lemmas,
        "subordinator": subordinator,
    }


def scan_all():
    """Scan every chapter file for main-clause FEFs."""
    findings = []
    for entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, entry)
        if not os.path.isdir(book_path):
            continue
        # Derive book slug from dir name (e.g. "01-matt" -> "matt")
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
                for idx, line_text in enumerate(v["lines"]):
                    flag = analyze_line(line_text, verse_words)
                    if not flag:
                        continue
                    # Require a resolving line after
                    if idx + 1 >= len(v["lines"]):
                        continue
                    next_line_text = v["lines"][idx + 1]
                    next_words = _line_words_with_morph(next_line_text, verse_words)
                    next_has_fin = any(w["is_fin"] for w in next_words)
                    if not next_has_fin:
                        continue
                    findings.append({
                        "file": chapter_file,
                        "ref": v["ref"],
                        "line": line_text,
                        "next_line": next_line_text,
                        "participle_lemmas": flag["participle_lemmas"],
                        "subordinator": flag["subordinator"],
                    })
    return findings


def main():
    findings = scan_all()
    print(f"Found {len(findings)} main-clause FEF candidates\n")
    for f in findings:
        print(f"{f['file']} {f['ref']}:")
        print(f"  {f['line']}")
        print(f"  + {f['next_line']}")
        print(
            f"  participle(s): {f['participle_lemmas']} "
            f"| subordinator: {f['subordinator']}"
        )
        print()


if __name__ == "__main__":
    main()
