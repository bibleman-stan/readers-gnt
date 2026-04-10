#!/usr/bin/env python3
"""
Parse downloaded YLT raw JSON files into a single ylt-verses.json.

Input:  research/ylt/raw/*.json  (from ylt_download.py)
Output: data/ylt-verses.json

Structure:
  {"matt": {"1": {"1": "verse text...", "2": "..."}}, ...}
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "research", "ylt", "raw")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "ylt-verses.json")

# bolls.life book ID -> project slug (lowercase, matching books/*.html)
BOOK_ID_TO_SLUG = {
    40: "matt",
    41: "mark",
    42: "luke",
    43: "john",
    44: "acts",
    45: "rom",
    46: "1cor",
    47: "2cor",
    48: "gal",
    49: "eph",
    50: "phil",
    51: "col",
    52: "1thess",
    53: "2thess",
    54: "1tim",
    55: "2tim",
    56: "titus",
    57: "phlm",
    58: "heb",
    59: "jas",
    60: "1pet",
    61: "2pet",
    62: "1john",
    63: "2john",
    64: "3john",
    65: "jude",
    66: "rev",
}

# Expected chapter counts per book
EXPECTED_CHAPTERS = {
    40: 28, 41: 16, 42: 24, 43: 21, 44: 28,
    45: 16, 46: 16, 47: 13, 48: 6, 49: 6,
    50: 4, 51: 4, 52: 5, 53: 3, 54: 6,
    55: 4, 56: 3, 57: 1, 58: 13, 59: 5,
    60: 5, 61: 3, 62: 5, 63: 1, 64: 1,
    65: 1, 66: 22,
}


def clean_text(text):
    """Clean verse text: normalize whitespace, strip leading/trailing space."""
    # Some API responses have extra whitespace or HTML entities
    t = text.strip()
    # Collapse multiple spaces
    while "  " in t:
        t = t.replace("  ", " ")
    return t


def main():
    result = {}
    total_verses = 0
    total_chapters = 0
    gaps = []
    empty_verses = []

    for book_id in sorted(BOOK_ID_TO_SLUG.keys()):
        slug = BOOK_ID_TO_SLUG[book_id]
        chapters = EXPECTED_CHAPTERS[book_id]
        result[slug] = {}

        for ch in range(1, chapters + 1):
            raw_file = os.path.join(RAW_DIR, f"{book_id}_{ch}.json")
            if not os.path.exists(raw_file):
                gaps.append(f"{slug} {ch} - raw file missing")
                continue

            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            ch_str = str(ch)
            result[slug][ch_str] = {}
            total_chapters += 1

            for entry in data:
                verse_num = str(entry["verse"])
                text = clean_text(entry["text"])
                if not text:
                    empty_verses.append(f"{slug} {ch}:{verse_num}")
                result[slug][ch_str][verse_num] = text
                total_verses += 1

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    # Report
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"=== YLT Parse Report ===")
    print(f"Books:    {len(result)}")
    print(f"Chapters: {total_chapters}")
    print(f"Verses:   {total_verses}")
    print(f"Output:   {OUTPUT_FILE}")
    print(f"Size:     {file_size:,} bytes ({file_size/1024:.1f} KB)")

    if gaps:
        print(f"\n--- GAPS ({len(gaps)}) ---")
        for g in gaps:
            print(f"  {g}")
    else:
        print(f"\nNo gaps found.")

    if empty_verses:
        print(f"\n--- EMPTY VERSES ({len(empty_verses)}) ---")
        for e in empty_verses:
            print(f"  {e}")
    else:
        print(f"No empty verses found.")

    # Verify verse continuity per chapter
    discontinuities = []
    for slug in result:
        for ch_str in result[slug]:
            verses = sorted(int(v) for v in result[slug][ch_str].keys())
            if verses:
                expected = list(range(verses[0], verses[-1] + 1))
                missing = set(expected) - set(verses)
                if missing:
                    discontinuities.append(
                        f"{slug} {ch_str}: missing verses {sorted(missing)}"
                    )

    if discontinuities:
        print(f"\n--- VERSE DISCONTINUITIES ({len(discontinuities)}) ---")
        for d in discontinuities:
            print(f"  {d}")
    else:
        print(f"No verse discontinuities found.")


if __name__ == "__main__":
    main()
