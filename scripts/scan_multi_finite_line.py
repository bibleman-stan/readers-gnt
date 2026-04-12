#!/usr/bin/env python3
"""
scan_multi_finite_line.py — Find lines containing 2+ finite verbs.

A line with multiple finite verbs is a candidate for splitting: each
finite verb typically introduces a new predication, and concatenating
two independent clauses on one line violates the atomic-thought rule.

Some multi-finite-verb lines are legitimate (periphrastic constructions,
tightly-bound coordinate verbs, question+answer in direct speech). The
scanner flags all of them; human review determines which should split.

Example — Gal 2:6:
    πρόσωπον θεὸς ἀνθρώπου οὐ λαμβάνει— ἐμοὶ γὰρ οἱ δοκοῦντες οὐδὲν προσανέθεντο,
Two finite verbs (λαμβάνει, προσανέθεντο) separated by em-dash + γάρ,
introducing two distinct main clauses. Should split.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_multi_finite_line.py
"""
import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_ROOT, "research", "morphgnt-sblgnt")

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

_verse_morph = {}


def _clean(word):
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]',
        '',
        word,
    )


def _load_morphgnt(book_slug):
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


def _is_finite(pos, parsing):
    """Finite verb: mood in {I, S, D, O} (indicative/subjunctive/imperative/optative)."""
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] in ("I", "S", "D", "O")


def _line_finite_verbs(line_text, verse_words):
    """Return list of (word, lemma) for finite verbs on the line."""
    consumable = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        consumable[cw].append((pos, parsing, lemma))
    found = []
    for raw in line_text.split():
        cleaned = _clean(raw)
        if not cleaned:
            continue
        matches = consumable.get(cleaned)
        if not matches:
            continue
        pos, parsing, lemma = matches.pop(0)
        if _is_finite(pos, parsing):
            found.append((cleaned, lemma))
    return found


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)")


def _parse_chapter(filepath):
    verses = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            m = VERSE_REF_RE.match(stripped)
            if m and stripped == m.group(0):
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
    results = []
    for book_entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, book_entry)
        if not os.path.isdir(book_path):
            continue
        parts = book_entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else book_entry
        morph = _load_morphgnt(book_slug)
        for fname in sorted(os.listdir(book_path)):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, fname)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = morph.get((v["chapter"], v["verse"]), [])
                if not verse_words:
                    continue
                for line_text in v["lines"]:
                    finites = _line_finite_verbs(line_text, verse_words)
                    if len(finites) >= 2:
                        results.append({
                            "file": f"{book_entry}/{fname}",
                            "ref": v["ref"],
                            "line": line_text,
                            "finite_count": len(finites),
                            "finites": finites,
                        })
    return results


def main():
    findings = scan_all()
    print(f"=== MULTI-FINITE-VERB LINE SCAN ===\n")
    print(f"Found {len(findings)} lines with 2+ finite verbs\n")
    # Sort by count desc for triage
    findings.sort(key=lambda x: -x["finite_count"])
    for f in findings:
        verb_list = ", ".join(f"{w}({l})" for w, l in f["finites"])
        print(f"{f['file']} {f['ref']} [{f['finite_count']} finite verbs]:")
        print(f"  {f['line']}")
        print(f"  verbs: {verb_list}")
        print()


if __name__ == "__main__":
    main()
