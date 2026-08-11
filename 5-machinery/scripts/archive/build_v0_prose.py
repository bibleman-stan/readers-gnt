#!/usr/bin/env python3
"""
build_v0_prose.py — Chapter-split the SBLGNT source files into the v0-prose tier.

Reads:  data/text-files/sblgnt-source/*.txt  (27 files, one per NT book)
Writes: data/text-files/v0-prose/{NN-book}/{abbrev}-{NN}.txt  (260 chapter files)

v0-prose is a faithful slice of the published SBLGNT: one verse per line,
preserving the original `{BookRef} {chapter}:{verse}\\t{greek text}` format
and all apparatus markers (⸀ ⸁ ⸂ ⸃ ⸄ ⸅). The book title line is dropped
(book-level, not chapter-level). Stripping/normalization happens at the v1 step.
"""

import os
import re
import sys
from collections import defaultdict

# -----------------------------------------------------------------------------
# Book table: source filename -> (NN-book subfolder, abbrev, expected chapters)
# -----------------------------------------------------------------------------
BOOKS = [
    ("Matt.txt",    "01-matt",    "matt",    28),
    ("Mark.txt",    "02-mark",    "mark",    16),
    ("Luke.txt",    "03-luke",    "luke",    24),
    ("John.txt",    "04-john",    "john",    21),
    ("Acts.txt",    "05-acts",    "acts",    28),
    ("Rom.txt",     "06-rom",     "rom",     16),
    ("1Cor.txt",    "07-1cor",    "1cor",    16),
    ("2Cor.txt",    "08-2cor",    "2cor",    13),
    ("Gal.txt",     "09-gal",     "gal",      6),
    ("Eph.txt",     "10-eph",     "eph",      6),
    ("Phil.txt",    "11-phil",    "phil",     4),
    ("Col.txt",     "12-col",     "col",      4),
    ("1Thess.txt",  "13-1thess",  "1thess",   5),
    ("2Thess.txt",  "14-2thess",  "2thess",   3),
    ("1Tim.txt",    "15-1tim",    "1tim",     6),
    ("2Tim.txt",    "16-2tim",    "2tim",     4),
    ("Titus.txt",   "17-titus",   "titus",    3),
    ("Phlm.txt",    "18-phlm",    "phlm",     1),
    ("Heb.txt",     "19-heb",     "heb",     13),
    ("Jas.txt",     "20-jas",     "jas",      5),
    ("1Pet.txt",    "21-1pet",    "1pet",     5),
    ("2Pet.txt",    "22-2pet",    "2pet",     3),
    ("1John.txt",   "23-1john",   "1john",    5),
    ("2John.txt",   "24-2john",   "2john",    1),
    ("3John.txt",   "25-3john",   "3john",    1),
    ("Jude.txt",    "26-jude",    "jude",     1),
    ("Rev.txt",     "27-rev",     "rev",     22),
]

# Verse-line pattern: "{BookRef} {chapter}:{verse}\t{greek}"
# BookRef may include a leading digit (e.g. "1Cor", "2John", "3John")
VERSE_RE = re.compile(r"^([1-3]?[A-Za-z]+)\s+(\d+):(\d+)\t(.*)$")

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_DIR = os.path.join(REPO_ROOT, "data", "text-files", "sblgnt-source")
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v0-prose")


def split_book(source_path):
    """Read a source file, return dict {chapter_int: [verse_line, ...]}.

    verse_line is the raw line from the source (minus trailing newline),
    preserving apparatus markers and the original BookRef/tab format.
    """
    chapters = defaultdict(list)
    with open(source_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if not line:
                continue
            m = VERSE_RE.match(line)
            if not m:
                # Title line (e.g., ΚΑΤΑ ΜΑΘΘΑΙΟΝ) or non-verse — skip.
                continue
            chapter_num = int(m.group(2))
            chapters[chapter_num].append(line)
    return chapters


def write_chapter(out_dir, abbrev, chapter_num, verse_lines):
    fname = f"{abbrev}-{chapter_num:02d}.txt"
    fpath = os.path.join(out_dir, fname)
    with open(fpath, "w", encoding="utf-8", newline="\n") as f:
        for vl in verse_lines:
            f.write(vl + "\n")
    return fpath


def main():
    if not os.path.isdir(SOURCE_DIR):
        print(f"ERROR: source dir not found: {SOURCE_DIR}", file=sys.stderr)
        return 2
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_files = 0
    failures = []
    print("Building v0-prose tier from SBLGNT source...")
    print(f"  source: {SOURCE_DIR}")
    print(f"  output: {OUTPUT_DIR}")
    print()

    for src_name, sub, abbrev, expected in BOOKS:
        src_path = os.path.join(SOURCE_DIR, src_name)
        if not os.path.isfile(src_path):
            failures.append(f"{src_name}: source file missing")
            print(f"  [MISS] {src_name}: source file not found")
            continue

        chapters = split_book(src_path)
        out_dir = os.path.join(OUTPUT_DIR, sub)
        os.makedirs(out_dir, exist_ok=True)

        chapter_nums = sorted(chapters.keys())
        for cn in chapter_nums:
            write_chapter(out_dir, abbrev, cn, chapters[cn])

        n = len(chapter_nums)
        total_files += n

        # Validate: chapter count matches expected, and chapter numbers are 1..expected.
        ok = (n == expected) and (chapter_nums == list(range(1, expected + 1)))
        status = "OK " if ok else "BAD"
        print(f"  [{status}] {sub:<12} {n:>3} chapters  (expected {expected})")
        if not ok:
            failures.append(
                f"{src_name}: got {n} chapters {chapter_nums!r}, expected {expected}"
            )

    print()
    print(f"Total chapter files written: {total_files}")
    print(f"Expected total: 260")
    if failures:
        print()
        print("VALIDATION FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    if total_files != 260:
        print(f"ERROR: total file count {total_files} != 260", file=sys.stderr)
        return 1
    print("All books validated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
