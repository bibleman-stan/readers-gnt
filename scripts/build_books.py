"""
build_books.py — Generate HTML book files from colometric text sources.

Reads chapter files from data/text-files/v1-colometric/ and writes
one HTML fragment per book into books/.

Usage:
    py -3 scripts/build_books.py              # build all books
    py -3 scripts/build_books.py --book mark  # build one book
"""

import argparse
import glob
import html
import os
import re
import sys
from collections import defaultdict

# Paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v2-colometric")
OUTPUT_DIR = os.path.join(REPO_ROOT, "books")

# Verse reference pattern: digits, colon, digits (e.g. "4:1", "17:33")
VERSE_REF_RE = re.compile(r"^\d+:\d+$")


def parse_chapter(filepath):
    """Parse a colometric chapter file into a list of verse dicts.

    Returns:
        chapter_num (int): The chapter number extracted from verse refs.
        verses (list): Each entry is {"ref": "4:1", "lines": ["...", ...]}.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    verses = []
    current_verse = None
    chapter_num = None
    in_verse = False  # True once we've seen our first verse reference

    for raw in raw_lines:
        line = raw.rstrip("\n").rstrip("\r")

        # Check for verse reference
        if VERSE_REF_RE.match(line.strip()):
            # Finish previous verse
            if current_verse is not None:
                verses.append(current_verse)

            ref = line.strip()
            if chapter_num is None:
                chapter_num = int(ref.split(":")[0])

            current_verse = {"ref": ref, "lines": []}
            in_verse = True
            continue

        # Blank line ends current verse block
        if line.strip() == "":
            if current_verse is not None and current_verse["lines"]:
                verses.append(current_verse)
                current_verse = None
            continue

        # If we haven't seen a verse ref yet, skip (header lines)
        if not in_verse:
            continue

        # Sense-line belonging to current verse
        if current_verse is not None:
            current_verse["lines"].append(line)

    # Don't forget the last verse if file doesn't end with blank line
    if current_verse is not None and current_verse["lines"]:
        verses.append(current_verse)

    return chapter_num, verses


def build_chapter_html(chapter_num, verses):
    """Build HTML for one chapter."""
    parts = []
    parts.append(f'<div class="chapter" id="ch-{chapter_num}">')

    for verse in verses:
        ref = html.escape(verse["ref"])
        parts.append(f'  <div class="verse"><span class="verse-num">{ref}</span>')
        for line in verse["lines"]:
            escaped = html.escape(line)
            parts.append(f'    <span class="line">{escaped}</span>')
        parts.append("  </div>")

    parts.append("</div>")
    return "\n".join(parts)


def discover_books(input_dir, book_filter=None):
    """Glob input files and group by book prefix.

    Returns:
        dict: {book_prefix: [(chapter_num_from_filename, filepath), ...]}
              sorted by chapter number.
    """
    pattern = os.path.join(input_dir, "*.txt")
    files = glob.glob(pattern)

    books = defaultdict(list)
    for fpath in files:
        basename = os.path.basename(fpath)           # e.g. "1cor-03.txt"
        stem = os.path.splitext(basename)[0]          # e.g. "1cor-03"

        # Split on last dash to get book prefix and chapter number
        dash_idx = stem.rfind("-")
        if dash_idx == -1:
            continue
        prefix = stem[:dash_idx]                      # e.g. "1cor"
        try:
            ch_num = int(stem[dash_idx + 1:])         # e.g. 3
        except ValueError:
            continue

        if book_filter and prefix != book_filter:
            continue

        books[prefix].append((ch_num, fpath))

    # Sort each book's chapters numerically
    for prefix in books:
        books[prefix].sort(key=lambda x: x[0])

    return dict(books)


def build_book(prefix, chapter_files, output_dir):
    """Build and write the HTML file for one book.

    Returns the number of chapters and verses processed.
    """
    all_chapter_html = []
    total_verses = 0

    for _ch_num, fpath in chapter_files:
        chapter_num, verses = parse_chapter(fpath)
        if chapter_num is None:
            # Fallback to filename chapter number if file was empty/unparseable
            chapter_num = _ch_num
        total_verses += len(verses)
        chapter_html = build_chapter_html(chapter_num, verses)
        all_chapter_html.append(chapter_html)

    output_path = os.path.join(output_dir, f"{prefix}.html")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_chapter_html) + "\n")

    return len(chapter_files), total_verses, output_path


def main():
    parser = argparse.ArgumentParser(
        description="Build HTML book files from colometric text sources."
    )
    parser.add_argument(
        "--book",
        default=None,
        help="Build only this book (prefix, e.g. 'mark', '1cor').",
    )
    args = parser.parse_args()

    if not os.path.isdir(INPUT_DIR):
        print(f"ERROR: Input directory not found: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)

    books = discover_books(INPUT_DIR, book_filter=args.book)

    if not books:
        if args.book:
            print(f"No files found for book '{args.book}' in {INPUT_DIR}")
        else:
            print(f"No .txt files found in {INPUT_DIR}")
        sys.exit(1)

    print(f"Building {len(books)} book(s)...\n")

    for prefix in sorted(books.keys()):
        chapter_files = books[prefix]
        num_chapters, num_verses, output_path = build_book(
            prefix, chapter_files, OUTPUT_DIR
        )
        rel_path = os.path.relpath(output_path, REPO_ROOT)
        print(f"  {prefix:<10} {num_chapters:>3} ch, {num_verses:>4} vv  -> {rel_path}")

    print(f"\nDone. Output in {os.path.relpath(OUTPUT_DIR, REPO_ROOT)}/")


if __name__ == "__main__":
    main()
