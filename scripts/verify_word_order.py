#!/usr/bin/env python3
"""
verify_word_order.py — Verify v4-editorial word order matches SBLGNT source.

For each verse in v4-editorial, concatenate the colometric lines and compare
the word sequence against the canonical SBLGNT source. Any mismatch indicates
a line-order error, missing word, or extra word.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/verify_word_order.py
    PYTHONIOENCODING=utf-8 py -3 scripts/verify_word_order.py --book rom
"""

import argparse
import os
import re
import sys
import unicodedata
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
SOURCE_DIR = os.path.join(REPO_ROOT, "data", "text-files", "sblgnt-source")

# Map our book slug -> SBLGNT source filename (without .txt)
BOOK_TO_SOURCE = {
    "matt": "Matt", "mark": "Mark", "luke": "Luke", "john": "John",
    "acts": "Acts", "rom": "Rom",
    "1cor": "1Cor", "2cor": "2Cor",
    "gal": "Gal", "eph": "Eph", "phil": "Phil", "col": "Col",
    "1thess": "1Thess", "2thess": "2Thess",
    "1tim": "1Tim", "2tim": "2Tim", "titus": "Titus", "phlm": "Phlm",
    "heb": "Heb", "jas": "Jas",
    "1pet": "1Pet", "2pet": "2Pet",
    "1john": "1John", "2john": "2John", "3john": "3John",
    "jude": "Jude", "rev": "Rev",
}

VERSE_REF_RE = re.compile(r"^\d+:\d+[a-z]?$")

# Characters to strip when normalizing for comparison
PUNCT_CHARS = ",.;:·!?'\"()[]—-\u037E\u0387\u00B7\u2014\u2013⸀⸁⸂⸃⸄⸅⟦⟧"


def normalize_word(word):
    """Strip critical apparatus markers, punctuation, and accents.

    We strip accents so that grave/acute variants of the same word (e.g.
    θεός vs θεὸς from oxia/grave alternation) compare equal. We only care
    about word IDENTITY and ORDER, not accentuation, for this check.
    """
    # Remove critical apparatus markers and punctuation
    cleaned = "".join(c for c in word if c not in PUNCT_CHARS)
    # Decompose accents (NFD), strip combining marks, recompose (NFC)
    decomposed = unicodedata.normalize("NFD", cleaned)
    no_marks = "".join(c for c in decomposed if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", no_marks).strip().lower()


def words_from_text(text):
    """Extract a list of normalized Greek words from a text string."""
    # Split on whitespace, normalize each, drop empties
    return [w for w in (normalize_word(t) for t in text.split()) if w]


def load_source_verses(source_path, book_code):
    """Parse SBLGNT source file. Returns dict: verse_ref -> word list."""
    verses = {}
    with open(source_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line or "\t" not in line:
                continue
            ref_part, text = line.split("\t", 1)
            ref_part = ref_part.strip()
            # ref_part format: "Matt 1:1"
            if not ref_part.startswith(book_code + " "):
                continue
            verse_ref = ref_part[len(book_code) + 1:].strip()
            verses[verse_ref] = words_from_text(text)
    return verses


def load_v4_chapter(chapter_path):
    """Parse a v4-editorial chapter file. Returns dict: verse_ref -> word list."""
    verses = defaultdict(list)
    current_verse = None
    with open(chapter_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            if VERSE_REF_RE.match(stripped):
                current_verse = stripped
                continue
            if current_verse is None:
                continue  # header lines before first verse
            verses[current_verse].extend(words_from_text(stripped))
    return dict(verses)


def find_book_subdir(prefix):
    """Find numbered subdirectory for a book prefix (e.g. 'matt' -> '01-matt')."""
    if not os.path.isdir(V4_DIR):
        return None
    for entry in os.listdir(V4_DIR):
        if os.path.isdir(os.path.join(V4_DIR, entry)):
            parts = entry.split("-", 1)
            if len(parts) == 2 and parts[0].isdigit() and parts[1] == prefix:
                return entry
    return None


def diff_word_lists(v4_words, source_words):
    """Return a diff description if lists differ, or None if identical."""
    if v4_words == source_words:
        return None

    # Find first difference position
    minlen = min(len(v4_words), len(source_words))
    first_diff = None
    for i in range(minlen):
        if v4_words[i] != source_words[i]:
            first_diff = i
            break
    if first_diff is None:
        first_diff = minlen

    # Build a context window around the first diff
    start = max(0, first_diff - 2)
    v4_window = v4_words[start:first_diff + 5]
    src_window = source_words[start:first_diff + 5]

    return {
        "first_diff_position": first_diff,
        "v4_length": len(v4_words),
        "source_length": len(source_words),
        "v4_window": v4_window,
        "source_window": src_window,
    }


def check_book(book_slug):
    """Check one book. Returns list of (chapter_file, verse_ref, diff) tuples."""
    source_code = BOOK_TO_SOURCE.get(book_slug)
    if not source_code:
        return [], f"No source mapping for {book_slug}"

    source_path = os.path.join(SOURCE_DIR, source_code + ".txt")
    if not os.path.isfile(source_path):
        return [], f"Source file missing: {source_path}"

    source_verses = load_source_verses(source_path, source_code)

    subdir = find_book_subdir(book_slug)
    if subdir is None:
        return [], f"v4-editorial subdir not found for {book_slug}"

    book_dir = os.path.join(V4_DIR, subdir)
    chapter_files = sorted(
        f for f in os.listdir(book_dir) if f.endswith(".txt")
    )

    issues = []
    for cf in chapter_files:
        chapter_path = os.path.join(book_dir, cf)
        v4_verses = load_v4_chapter(chapter_path)
        for verse_ref, v4_words in v4_verses.items():
            source_words = source_verses.get(verse_ref)
            if source_words is None:
                issues.append((cf, verse_ref, {"error": "verse not in source"}))
                continue
            diff = diff_word_lists(v4_words, source_words)
            if diff:
                issues.append((cf, verse_ref, diff))
    return issues, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", default=None, help="Check only this book (e.g. 'rom')")
    args = parser.parse_args()

    if args.book:
        books = [args.book]
    else:
        books = sorted(BOOK_TO_SOURCE.keys())

    total_issues = 0
    book_summaries = []
    for book in books:
        issues, err = check_book(book)
        if err:
            print(f"[{book}] ERROR: {err}", file=sys.stderr)
            continue
        book_summaries.append((book, len(issues)))
        total_issues += len(issues)
        if issues:
            print(f"\n=== {book.upper()} ({len(issues)} issues) ===")
            for cf, verse_ref, diff in issues:
                if "error" in diff:
                    print(f"  {cf} {verse_ref}: {diff['error']}")
                    continue
                print(f"  {cf} {verse_ref}: lengths v4={diff['v4_length']} src={diff['source_length']} first_diff@{diff['first_diff_position']}")
                print(f"    v4 :  {' '.join(diff['v4_window'])}")
                print(f"    src:  {' '.join(diff['source_window'])}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for book, count in book_summaries:
        marker = " " if count == 0 else "!"
        print(f"  {marker} {book:8s} {count:4d} issues")
    print(f"\nTotal: {total_issues} verse-level discrepancies across {len(book_summaries)} books")


if __name__ == "__main__":
    main()
