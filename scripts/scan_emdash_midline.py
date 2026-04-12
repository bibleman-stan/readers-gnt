#!/usr/bin/env python3
"""
scan_emdash_midline.py — Find em-dashes mid-line in v4-editorial.

SBLGNT editorial em-dashes (— U+2014, – U+2013) mark parenthetical
boundaries in the base text. They are editorial signals from the
SBL edition's critical judgment that the text has just entered or
exited a parenthetical. Such boundaries are almost always compositional
break points that our colometric layout should honor.

An em-dash appearing at a line-interior (non-terminal) position is a
candidate for splitting at the dash. Example — Gal 2:6:
    πρόσωπον θεὸς ἀνθρώπου οὐ λαμβάνει— ἐμοὶ γὰρ οἱ δοκοῦντες ...
                                     ^^^ em-dash mid-line
This was missed by session-5 review and surfaced only on close reading.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_emdash_midline.py
"""
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")

EMDASH_CHARS = ("—", "–", "―")  # U+2014, U+2013, U+2015

VERSE_REF_RE = re.compile(r"^\d+:\d+[a-z]?$")


def check_line(line):
    """Return the em-dash character and its position if mid-line, else None."""
    stripped = line.rstrip()
    if not stripped:
        return None
    for i, ch in enumerate(stripped):
        if ch not in EMDASH_CHARS:
            continue
        # ch is an em-dash. Is it at a terminal position?
        # Terminal = nothing after it except optional whitespace.
        rest = stripped[i + 1:].strip()
        if not rest:
            return None  # em-dash at end of line — fine
        # Also skip if the dash is at position 0 (line STARTS with dash) —
        # that's a line-continuation signal, not a mid-line dash
        if i == 0:
            return None
        return {"char": ch, "position": i, "rest": rest}
    return None


def scan_file(filepath):
    findings = []
    current_verse = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            if VERSE_REF_RE.match(stripped):
                current_verse = stripped
                continue
            info = check_line(line)
            if info:
                findings.append({
                    "verse": current_verse,
                    "line_no": line_no,
                    "line": line,
                    "char": info["char"],
                    "position": info["position"],
                })
    return findings


def scan_all():
    results = []
    for book_entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, book_entry)
        if not os.path.isdir(book_path):
            continue
        for fname in sorted(os.listdir(book_path)):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, fname)
            findings = scan_file(filepath)
            for f in findings:
                results.append({
                    "file": f"{book_entry}/{fname}",
                    **f,
                })
    return results


def main():
    findings = scan_all()
    print(f"=== EM-DASH MID-LINE SCAN ===\n")
    print(f"Found {len(findings)} lines with mid-line em-dashes\n")
    for f in findings:
        print(f"{f['file']} {f['verse']} (line {f['line_no']}) [{f['char']}]:")
        print(f"  {f['line']}")
        print()


if __name__ == "__main__":
    main()
