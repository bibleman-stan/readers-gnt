#!/usr/bin/env python3
"""
scan_prep_catenae.py — Find chains of 3+ prepositional phrases strung together.

Paul (especially in Ephesians 1, Colossians 1, Romans 8-11) piles prepositional
phrases as parallel modifiers of the same head. When compressed flat they are
unreadable. Stacking each prep phrase on its own line makes the architectural
buildup visible.

Detection: a sequence of 3+ prepositional phrases (preposition + case-marked
object) that appear consecutively on the SAME line or span only 1-2 lines,
WITHOUT each phrase being its own line.

A prepositional phrase = one preposition (MorphGNT POS starts with 'P-') plus
its governed object (run of articles / nouns / pronouns / adjectives in the
case governed by the preposition, until the next preposition, verb, or
conjunction breaks the run).

The detection is purely grammatical, not theological.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_prep_catenae.py
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
OUTPUT_PATH = os.path.join(REPO_DIR, "private", "prep-catenae-scan.txt")

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
    """Return dict keyed by (chapter, verse) -> ordered list of token dicts."""
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
            if not cleaned:
                continue
            verses[(ch, vs)].append({
                "cleaned": cleaned,
                "display": word,
                "pos": pos,
                "parsing": parsing,
                "lemma": lemma,
                "case": parsing[4] if len(parsing) > 4 else "-",
                "mood": parsing[3] if len(parsing) > 3 else "-",
            })
    _verse_morph[book_slug] = dict(verses)
    return dict(verses)


def _is_preposition(tok):
    return tok["pos"].startswith("P-")


# Mapping preposition lemma -> governed case(s). From standard Greek grammar.
# A preposition can govern multiple cases (ἐν=D only, διά=G,A, κατά=G,A, etc).
# We use this to determine the head case of the prep-phrase object.
_PREP_CASES = {
    "ἐν": {"D"},
    "εἰς": {"A"},
    "ἐκ": {"G"}, "ἐξ": {"G"},
    "ἀπό": {"G"},
    "πρό": {"G"},
    "πρός": {"D", "A", "G"},
    "παρά": {"G", "D", "A"},
    "περί": {"G", "A"},
    "ὑπέρ": {"G", "A"},
    "ὑπό": {"G", "A"},
    "κατά": {"G", "A"},
    "μετά": {"G", "A"},
    "διά": {"G", "A"},
    "ἀντί": {"G"},
    "σύν": {"D"},
    "ἐπί": {"G", "D", "A"},
    "ἄνευ": {"G"},
    "ἔμπροσθεν": {"G"},
    "ἔναντι": {"G"},
    "ἔνεκα": {"G"}, "ἕνεκα": {"G"}, "εἵνεκεν": {"G"}, "ἕνεκεν": {"G"},
    "ἐντός": {"G"},
    "ἐκτός": {"G"},
    "ἔξω": {"G"},
    "χωρίς": {"G"},
    "ἐνώπιον": {"G"},
    "ἀμφί": {"G", "D", "A"},
    "ἄχρι": {"G"}, "ἄχρις": {"G"},
    "μέχρι": {"G"}, "μέχρις": {"G"},
    "πλήν": {"G"},
    "ὀπίσω": {"G"},
    "ἐγγύς": {"G"},
}


def _object_head_case(tok):
    """Return case code for a token that could serve as a prep-object head."""
    if tok["pos"].startswith("V"):
        return None
    c = tok.get("case")
    if c in ("N", "G", "D", "A", "V"):
        return c
    return None


def _is_case_agreeing_nominal(tok, target_cases):
    """Article / noun / adjective / pronoun / substantival participle that
    agrees in case with the prep's governed case."""
    pos = tok["pos"]
    if pos.startswith("V") and tok["mood"] == "P":
        return tok["case"] in target_cases
    if pos.startswith("N-") or pos.startswith("A-") or pos.startswith("RA") or \
       pos.startswith("RD") or pos.startswith("RP") or pos.startswith("RR") or \
       pos.startswith("RI") or pos.startswith("RX") or pos.startswith("RC"):
        return tok["case"] in target_cases
    return False


def _is_genitive_modifier(tok):
    """A genitive nominal that can attach to a preceding noun as a modifier
    (e.g., τοῦ πατρός in ἐν ἡμέραις Ἡρῴδου τοῦ βασιλέως). Excludes relative
    pronouns (RR) since those introduce clauses rather than modifying."""
    pos = tok["pos"]
    if pos.startswith("N-") or pos.startswith("A-") or pos.startswith("RA") or \
       pos.startswith("RD") or pos.startswith("RP"):
        return tok["case"] == "G"
    return False


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


def _token_line_indices(verse_lines, verse_tokens):
    """For each verse token, determine which line it sits on (0-indexed)."""
    line_idx_for_token = [None] * len(verse_tokens)
    tok_cursor = 0
    for li, line_text in enumerate(verse_lines):
        for raw in line_text.split():
            cleaned = _clean(raw)
            if not cleaned:
                continue
            j = tok_cursor
            matched = None
            while j < len(verse_tokens):
                if verse_tokens[j]["cleaned"] == cleaned:
                    matched = j
                    break
                j += 1
            if matched is not None:
                line_idx_for_token[matched] = li
                tok_cursor = matched + 1
    return line_idx_for_token


def _extract_prep_phrases(verse_tokens, line_idx_for_token):
    """Return list of prep-phrase dicts: {prep_i, obj_end_i, text, line_start,
    line_end}.

    Case-aware: the object runs until the head-case is satisfied, allowing
    optional trailing genitive modifiers (τοῦ X) that attach to a noun head.
    """
    phrases = []
    n = len(verse_tokens)
    i = 0
    while i < n:
        tok = verse_tokens[i]
        if not _is_preposition(tok):
            i += 1
            continue
        prep_lemma = tok["lemma"]
        target_cases = _PREP_CASES.get(prep_lemma)
        prep_i = i
        j = i + 1
        saw_head = False  # have we seen the head nominal matching governed case?
        obj_end_i = None

        # If we don't know the preposition's case constraints, fall back to a
        # simple "take one nominal" heuristic.
        if not target_cases:
            if j < n:
                nxt = verse_tokens[j]
                if nxt["pos"].startswith(("N-", "RP", "RR", "RD")):
                    obj_end_i = j
                    j += 1
        else:
            # Phase 1: collect article + adjective + head-case nominal.
            while j < n:
                nxt = verse_tokens[j]
                if _is_preposition(nxt) or nxt["pos"].startswith("V") or \
                   nxt["pos"].startswith("C") or nxt["pos"].startswith("I"):
                    break
                if _is_case_agreeing_nominal(nxt, target_cases):
                    # This is part of the head-case nominal group.
                    # It's a "head" candidate if it's a noun/pronoun (not a pure
                    # article/adjective, though those count too if followed by
                    # no further nominal).
                    obj_end_i = j
                    if nxt["pos"].startswith("N-") or nxt["pos"].startswith("R"):
                        saw_head = True
                    j += 1
                    continue
                break
            # Peel back any trailing article left at the end of phase 1
            # (e.g., the τοῦ in ἔμπροσθεν τοῦ πατρός μου τοῦ — the second τοῦ
            # opens a new substantival and shouldn't belong to this phrase).
            while obj_end_i is not None and obj_end_i > prep_i + 1 and \
                  verse_tokens[obj_end_i]["pos"].startswith("RA"):
                obj_end_i -= 1

            # Phase 2: trailing genitive modifier(s) on the noun head.
            # Only accept a trailing genitive run if it contains a noun/pronoun
            # (not just dangling articles) and does not end on a standalone
            # article before another preposition (that's a new substantival).
            if saw_head and obj_end_i is not None:
                k = obj_end_i + 1
                gen_run_start = k
                gen_end = obj_end_i
                gen_has_head = False
                while k < n:
                    nxt = verse_tokens[k]
                    if _is_preposition(nxt) or nxt["pos"].startswith("V") or \
                       nxt["pos"].startswith("C") or nxt["pos"].startswith("I"):
                        break
                    if _is_genitive_modifier(nxt):
                        gen_end = k
                        if nxt["pos"].startswith("N-") or \
                           nxt["pos"].startswith("RP") or \
                           nxt["pos"].startswith("RD") or \
                           nxt["pos"].startswith("RR"):
                            gen_has_head = True
                        k += 1
                        continue
                    break
                # Peel back trailing articles that don't govern a noun.
                while gen_end > obj_end_i and \
                      verse_tokens[gen_end]["pos"].startswith("RA"):
                    gen_end -= 1
                if gen_has_head and gen_end > obj_end_i:
                    obj_end_i = gen_end

        if obj_end_i is None:
            i += 1
            continue

        text_parts = [verse_tokens[k]["display"] for k in range(prep_i, obj_end_i + 1)]
        text = " ".join(text_parts)
        line_start = line_idx_for_token[prep_i]
        line_end = line_idx_for_token[obj_end_i]
        phrases.append({
            "prep_i": prep_i,
            "obj_end_i": obj_end_i,
            "text": text,
            "line_start": line_start,
            "line_end": line_end,
        })
        i = obj_end_i + 1
    return phrases


def _find_catenae(phrases, verse_tokens):
    """Group consecutive prep phrases into catenae (chains of 3+).

    Two phrases are "consecutive" if no finite verb / infinitive / participle
    (clause boundary) falls strictly between them. Small gaps of conjunctions
    (esp. καί / τε / δέ), articles, and particles are allowed — these are the
    normal connectors within a prep-phrase chain like ἐν X καὶ ἐν Y.
    """
    catenae = []
    if not phrases:
        return catenae
    cur = [phrases[0]]
    for p in phrases[1:]:
        prev = cur[-1]
        gap_start = prev["obj_end_i"] + 1
        gap_end = p["prep_i"] - 1
        gap_ok = True
        if gap_end >= gap_start:
            if gap_end - gap_start + 1 > 4:
                gap_ok = False
            else:
                for k in range(gap_start, gap_end + 1):
                    tk = verse_tokens[k]
                    pos = tk["pos"]
                    # Verbs (any form) in the gap mean we crossed a clause.
                    if pos.startswith("V"):
                        gap_ok = False
                        break
                    # Allowed fillers: conjunctions (C-), particles (X-),
                    # articles (RA), pronouns (R*), adverbs (D-), adjectives (A-).
                    if pos.startswith("C") or pos.startswith("X") or \
                       pos.startswith("R") or pos.startswith("D") or \
                       pos.startswith("A") or pos.startswith("N"):
                        continue
                    gap_ok = False
                    break
        if gap_ok:
            cur.append(p)
        else:
            if len(cur) >= 3:
                catenae.append(cur)
            cur = [p]
    if len(cur) >= 3:
        catenae.append(cur)
    return catenae


def _catena_is_stacked(catena):
    """True if every phrase in the catena sits on its own distinct line AND
    each phrase's start == its end (phrase not wrapped across lines)."""
    seen_lines = set()
    for p in catena:
        if p["line_start"] is None or p["line_end"] is None:
            return False
        if p["line_start"] != p["line_end"]:
            return False
        if p["line_start"] in seen_lines:
            return False
        seen_lines.add(p["line_start"])
    return True


def _catena_line_span(catena):
    starts = [p["line_start"] for p in catena if p["line_start"] is not None]
    ends = [p["line_end"] for p in catena if p["line_end"] is not None]
    if not starts or not ends:
        return None, None
    return min(starts), max(ends)


def scan_all():
    findings = []
    clean_count = 0
    total_catenae = 0
    chapters_with_catenae = set()

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
                verse_tokens = morph.get((v["chapter"], v["verse"]), [])
                if not verse_tokens:
                    continue
                line_idx = _token_line_indices(v["lines"], verse_tokens)
                phrases = _extract_prep_phrases(verse_tokens, line_idx)
                catenae = _find_catenae(phrases, verse_tokens)
                for cat in catenae:
                    total_catenae += 1
                    chapters_with_catenae.add((entry, chapter_file))
                    if _catena_is_stacked(cat):
                        clean_count += 1
                        continue
                    # Flag criteria:
                    #   (a) a single line carries 3+ prep phrases of the catena
                    #       (truly compressed flat line), OR
                    #   (b) a single line carries 2 prep phrases and the catena
                    #       only spans 1-2 lines (partial compression).
                    lo, hi = _catena_line_span(cat)
                    if lo is None or hi is None:
                        continue
                    span = hi - lo + 1
                    per_line = defaultdict(int)
                    for p in cat:
                        if p["line_start"] is not None and \
                           p["line_start"] == p["line_end"]:
                            per_line[p["line_start"]] += 1
                    max_per_line = max(per_line.values()) if per_line else 0
                    flag = False
                    if max_per_line >= 3:
                        flag = True
                    elif max_per_line >= 2 and span <= 2:
                        flag = True
                    if flag:
                        findings.append({
                            "book_dir": entry,
                            "file": chapter_file,
                            "ref": v["ref"],
                            "chapter": v["chapter"],
                            "verse": v["verse"],
                            "phrases": cat,
                            "lines": v["lines"],
                            "line_lo": lo,
                            "line_hi": hi,
                        })
    return findings, clean_count, total_catenae, chapters_with_catenae


def format_report(findings, clean_count, total_catenae, chapters_with_catenae):
    out = []
    out.append("=== PREPOSITIONAL CATENA SCAN ===")
    out.append("")
    out.append(f"Total prep-phrase catenae (3+ consecutive) detected: {total_catenae}")
    out.append(f"Already stacked (CLEAN, not flagged): {clean_count}")
    out.append(f"Flagged for stacking: {len(findings)}")
    out.append(f"Chapters containing at least one catena: {len(chapters_with_catenae)}")
    out.append("")

    # Group findings by book
    by_book = defaultdict(list)
    for f in findings:
        by_book[f["book_dir"]].append(f)

    out.append("=== FLAGGED CATENAE BY BOOK ===")
    out.append("")
    for book in sorted(by_book.keys()):
        items = by_book[book]
        out.append(f"--- {book} ({len(items)} flagged) ---")
        out.append("")
        for f in items:
            out.append(f"{f['file']} {f['ref']}:")
            out.append("  Current layout:")
            for li in range(f["line_lo"], f["line_hi"] + 1):
                out.append(f"    {f['lines'][li]}")
            out.append(f"  Detected catena ({len(f['phrases'])} prepositions):")
            for p in f["phrases"]:
                out.append(f"    - {p['text']}")
            out.append("  Recommendation: stack each prep phrase as its own line")
            out.append("")
    return "\n".join(out)


def main():
    findings, clean_count, total_catenae, chapters_with_catenae = scan_all()
    report = format_report(findings, clean_count, total_catenae, chapters_with_catenae)
    print(report)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSaved report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
