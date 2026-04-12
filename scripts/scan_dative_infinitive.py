#!/usr/bin/env python3
"""
scan_dative_infinitive.py — Find dative-subject-of-infinitive constructions
that are split across lines.

When a Greek speech/cognition/command verb (Λέγω, παραγγέλλω, παρακαλῶ, etc.)
takes a dative indirect object that also functions as the SEMANTIC SUBJECT of
an infinitive complement, the dative is doing double duty:
    - indirect object of the speech verb
    - subject of the infinitive

Showcase example — Rom 12:3:
    Λέγω γὰρ διὰ τῆς χάριτος τῆς δοθείσης μοι
    παντὶ τῷ ὄντι ἐν ὑμῖν μὴ ὑπερφρονεῖν παρʼ ὃ δεῖ φρονεῖν,

Here παντὶ τῷ ὄντι ἐν ὑμῖν (dative) is BOTH the indirect object of Λέγω AND
the subject of the infinitive ὑπερφρονεῖν. The dative belongs WITH the
infinitive content, not separated by a line break.

Pattern detected: speech-verb + dative + infinitive, where the dative and
infinitive are SPLIT across lines. The line break between them is the bug.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_dative_infinitive.py
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
OUTPUT_PATH = os.path.join(REPO_DIR, "private", "dative-infinitive-scan.txt")

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

# Speech / command / cognition verbs that take dative + infinitive
SPEECH_COMMAND_LEMMAS = {
    "λέγω",
    "παραγγέλλω",
    "παρακαλέω",
    "παραινέω",
    "κελεύω",
    "ἐντέλλομαι",
    "ἐντέλλω",
    "διαστέλλω",
    "διαστέλλομαι",
    "ἐπιτάσσω",
    "παρίστημι",
    "βουλεύομαι",
    "νομοθετέω",
    # Closely related dative-+-infinitive triggers
    "ἐπιτρέπω",
    "συμβουλεύω",
    "γράφω",
    "δίδωμι",
    "ἀπαγγέλλω",
    "διατάσσω",
}


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
        for tok_idx, line in enumerate(f):
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
                "pos": pos,
                "parsing": parsing,
                "lemma": lemma,
                "case": parsing[4] if len(parsing) > 4 else "-",
                "mood": parsing[3] if len(parsing) > 3 else "-",
            })
    _verse_morph[book_slug] = dict(verses)
    return dict(verses)


def _is_dative_nominal(tok):
    """True if token is a nominal/pronoun/adjective/article in the dative."""
    if tok["pos"].startswith("V"):
        return False
    return tok["case"] == "D"


def _is_infinitive(tok):
    return tok["pos"].startswith("V") and tok["mood"] == "N"


def _is_speech_verb(tok):
    """True if token is a finite/imperative/etc. verb with a speech lemma."""
    if not tok["pos"].startswith("V"):
        return False
    # Any verb form with a speech lemma counts (finite, participle, etc.).
    # Exclude infinitives — we want a governing verb taking the infinitive.
    if tok["mood"] == "N":
        return False
    return tok["lemma"] in SPEECH_COMMAND_LEMMAS


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


def _line_index_for_each_token(verse_lines, verse_tokens):
    """For each verse token (in order), determine which line it sits on.

    Walks left-to-right through verse lines and matches cleaned word forms in
    sequence against the verse_tokens list. Returns list of line indices the
    same length as verse_tokens (or None if a token couldn't be matched).
    """
    line_idx_for_token = [None] * len(verse_tokens)
    tok_cursor = 0
    for li, line_text in enumerate(verse_lines):
        for raw in line_text.split():
            cleaned = _clean(raw)
            if not cleaned:
                continue
            # Find next matching token at-or-after cursor
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
            # If no match, leave it (could be apparatus / punctuation artifact)
    return line_idx_for_token


def _find_constructions(verse_tokens):
    """Find sequences (speech_idx, dative_idx, inf_idx) in this verse.

    Pattern: a speech verb token followed (later in the verse) by a dative
    nominal token followed (later still) by an infinitive token.

    To avoid combinatorial explosion, for each speech verb we take the
    NEAREST following dative, then the NEAREST following infinitive after
    that dative. We also bound the search: speech-verb -> infinitive must be
    within 25 tokens (one verse-sized window) and we stop searching past a
    new finite verb of a non-speech lemma (signals a clause boundary).
    """
    constructions = []
    n = len(verse_tokens)
    for i, tok in enumerate(verse_tokens):
        if not _is_speech_verb(tok):
            continue
        # Find nearest following dative within window
        dative_idx = None
        for j in range(i + 1, min(n, i + 26)):
            jt = verse_tokens[j]
            # Hard stop at another finite/imperative verb (not infinitive,
            # not participle) — that starts a new clause.
            if jt["pos"].startswith("V") and jt["mood"] in ("I", "S", "D", "O"):
                # but allow if it's also a speech lemma? still a new clause
                break
            if _is_dative_nominal(jt):
                dative_idx = j
                break
        if dative_idx is None:
            continue
        # Find nearest following infinitive within window from the dative
        inf_idx = None
        for k in range(dative_idx + 1, min(n, dative_idx + 20)):
            kt = verse_tokens[k]
            if kt["pos"].startswith("V") and kt["mood"] in ("I", "S", "D", "O"):
                break
            if _is_infinitive(kt):
                inf_idx = k
                break
        if inf_idx is None:
            continue
        constructions.append((i, dative_idx, inf_idx))
    return constructions


def scan_all():
    """Scan every chapter file. Returns (constructions_total, properly_chunked,
    split_findings)."""
    total = 0
    chunked = 0
    split_findings = []

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
                constructions = _find_constructions(verse_tokens)
                if not constructions:
                    continue
                line_idx = _line_index_for_each_token(v["lines"], verse_tokens)

                for speech_i, dat_i, inf_i in constructions:
                    total += 1
                    dat_line = line_idx[dat_i]
                    inf_line = line_idx[inf_i]
                    if dat_line is None or inf_line is None:
                        # Couldn't locate — skip silently
                        total -= 1
                        continue
                    if dat_line == inf_line:
                        chunked += 1
                        continue
                    # SPLIT — dative and infinitive on different lines
                    split_findings.append({
                        "file": chapter_file,
                        "ref": v["ref"],
                        "speech": verse_tokens[speech_i]["cleaned"],
                        "speech_lemma": verse_tokens[speech_i]["lemma"],
                        "dative": verse_tokens[dat_i]["cleaned"],
                        "infinitive": verse_tokens[inf_i]["cleaned"],
                        "dat_line": dat_line,
                        "inf_line": inf_line,
                        "lines": v["lines"],
                    })

    return total, chunked, split_findings


def format_report(total, chunked, split_findings):
    out = []
    out.append("=== DATIVE SUBJECT OF INFINITIVE SCAN ===")
    out.append("")
    out.append(f"Total speech-verb + dative + infinitive constructions found: {total}")
    out.append(f"Properly chunked (dative+infinitive on same line): {chunked}")
    out.append(f"SPLIT (dative separated from its infinitive): {len(split_findings)}")
    out.append("")
    if split_findings:
        out.append("SPLIT CASES:")
        out.append("")
        for f in split_findings:
            out.append(f"{f['file']} {f['ref']}:")
            out.append(f"  speech verb: {f['speech']} (lemma: {f['speech_lemma']})")
            out.append(f"  dative: {f['dative']} (line {f['dat_line'] + 1})")
            out.append(f"  infinitive: {f['infinitive']} (line {f['inf_line'] + 1})")
            out.append(f"  current:")
            lo = min(f["dat_line"], f["inf_line"])
            hi = max(f["dat_line"], f["inf_line"])
            for li in range(lo, hi + 1):
                out.append(f"    {f['lines'][li]}")
            out.append(f"  recommended: chunk dative+infinitive together")
            out.append("")
    return "\n".join(out)


def main():
    total, chunked, split_findings = scan_all()
    report = format_report(total, chunked, split_findings)
    print(report)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSaved report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
