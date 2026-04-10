#!/usr/bin/env python3
"""
ylt_align.py — Align YLT (Young's Literal Translation) text to GNT Reader
colometric line breaks.

Reads v3-colometric Greek text to determine line counts per verse, then splits
YLT English text into the same number of lines using clause-boundary heuristics.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py                # all books
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --book acts     # one book
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --test          # run test cases
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
V3_DIR = REPO / "data" / "text-files" / "v3-colometric"
YLT_OUT_DIR = REPO / "data" / "text-files" / "ylt-colometric"
YLT_RAW_DIR = REPO / "research" / "ylt" / "raw"
BOOKS_JSON = REPO / "research" / "ylt" / "books.json"

# ---------------------------------------------------------------------------
# Book number -> slug mapping (NT only, books 40-66)
# ---------------------------------------------------------------------------
BOOKNUM_TO_SLUG = {
    40: "matt", 41: "mark", 42: "luke", 43: "john", 44: "acts",
    45: "rom", 46: "1cor", 47: "2cor", 48: "gal", 49: "eph",
    50: "phil", 51: "col", 52: "1thess", 53: "2thess",
    54: "1tim", 55: "2tim", 56: "titus", 57: "phlm",
    58: "heb", 59: "jas", 60: "1pet", 61: "2pet",
    62: "1john", 63: "2john", 64: "3john", 65: "jude", 66: "rev",
}
SLUG_TO_BOOKNUM = {v: k for k, v in BOOKNUM_TO_SLUG.items()}

# Chapter counts per book (NT)
BOOK_CHAPTERS = {
    40: 28, 41: 16, 42: 24, 43: 21, 44: 28,
    45: 16, 46: 16, 47: 13, 48: 6, 49: 6,
    50: 4, 51: 4, 52: 5, 53: 3,
    54: 6, 55: 4, 56: 3, 57: 1,
    58: 13, 59: 5, 60: 5, 61: 3,
    62: 5, 63: 1, 64: 1, 65: 1, 66: 22,
}

# ---------------------------------------------------------------------------
# YLT data download / cache
# ---------------------------------------------------------------------------
def download_chapter(booknum, chapter):
    """Download a single chapter from bolls.life API and cache it."""
    raw_path = YLT_RAW_DIR / f"{booknum}_{chapter}.json"
    if raw_path.exists():
        return json.loads(raw_path.read_text(encoding="utf-8"))

    YLT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = f"https://bolls.life/get-chapter/YLT/{booknum}/{chapter}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR downloading {url}: {e}", file=sys.stderr)
        return []

    raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def ensure_ylt_data(booknum):
    """Ensure all chapters for a book are downloaded. Returns dict {chapter: {verse: text}}."""
    chapters = BOOK_CHAPTERS[booknum]
    book_data = {}  # {chapter_int: {verse_int: text}}
    for ch in range(1, chapters + 1):
        raw_path = YLT_RAW_DIR / f"{booknum}_{ch}.json"
        if raw_path.exists():
            verses_list = json.loads(raw_path.read_text(encoding="utf-8"))
        else:
            print(f"  Downloading {BOOKNUM_TO_SLUG[booknum]} ch {ch}...")
            verses_list = download_chapter(booknum, ch)
            time.sleep(0.3)  # polite rate limit
        verse_dict = {}
        for v in verses_list:
            verse_dict[v["verse"]] = v["text"].strip()
        book_data[ch] = verse_dict
    return book_data


# ---------------------------------------------------------------------------
# Parse v3-colometric Greek files
# ---------------------------------------------------------------------------
def parse_greek_chapter(filepath):
    """Parse a v3-colometric file. Returns {verse_num: [line1, line2, ...]}."""
    lines = Path(filepath).read_text(encoding="utf-8").splitlines()
    verses = {}
    current_verse = None
    current_lines = []

    verse_re = re.compile(r"^(\d+):(\d+)$")

    for line in lines:
        line = line.rstrip()
        m = verse_re.match(line)
        if m:
            # Save previous verse
            if current_verse is not None:
                # Strip trailing blank lines
                while current_lines and not current_lines[-1].strip():
                    current_lines.pop()
                verses[current_verse] = current_lines
            current_verse = int(m.group(2))
            current_lines = []
        elif current_verse is not None:
            if line.strip():  # skip blank lines within verse
                current_lines.append(line)

    # Save last verse
    if current_verse is not None:
        while current_lines and not current_lines[-1].strip():
            current_lines.pop()
        verses[current_verse] = current_lines

    return verses


# ---------------------------------------------------------------------------
# English text splitting
# ---------------------------------------------------------------------------

# Clause-introducing words that correspond to Greek conjunctions/subordinators.
# These are preferred split points. We split BEFORE these words.
CLAUSE_WORDS = [
    "and ", "but ", "for ", "that ", "which ", "who ", "whom ",
    "if ", "when ", "where ", "while ", "since ", "because ",
    "so that ", "in order that ", "lest ", "unless ", "until ",
    "after ", "before ", "though ", "although ", "whether ",
    "nor ", "or ", "yet ", "then ", "therefore ", "also ",
    "saying, ", "saying ",
]

# Punctuation that marks natural clause boundaries
PUNCT_SPLITS = ["; ", ", ", "-- ", " -- "]


def find_split_candidates(text):
    """Find all candidate split positions in text.

    Returns list of (position, priority) tuples.
    position = char index where the new line would START.
    priority = lower is better (clause words > punctuation > midpoint).
    """
    candidates = []

    # Priority 1: clause-introducing words (split before the word)
    for word in CLAUSE_WORDS:
        # Find all occurrences, but not at the very start
        start = 1
        while True:
            idx = text.lower().find(word.lower(), start)
            if idx <= 0:
                break
            # Only split if preceded by space or punctuation
            if idx > 0 and text[idx - 1] in " ,;:":
                # The split point is at idx (start of clause word)
                candidates.append((idx, 1))
            start = idx + 1

    # Priority 2: semicolons and commas
    for punct in PUNCT_SPLITS:
        start = 1
        while True:
            idx = text.find(punct, start)
            if idx < 0:
                break
            split_pos = idx + len(punct)
            if split_pos < len(text):
                candidates.append((split_pos, 2))
            start = idx + 1

    # Deduplicate by position, keeping best priority
    best = {}
    for pos, pri in candidates:
        if pos not in best or pri < best[pos]:
            best[pos] = pri
    return sorted(best.items(), key=lambda x: x[0])


def split_text_into_n(text, n):
    """Split text into exactly n lines, using clause boundaries when possible.

    Returns list of n strings.
    """
    text = text.strip()
    if n <= 1:
        return [text]

    candidates = find_split_candidates(text)
    if not candidates:
        # No natural breaks at all — split evenly by word
        return _split_evenly_by_words(text, n)

    # We need n-1 split points.
    # Strategy: pick the best n-1 splits from candidates.
    # "Best" = good priority + even distribution.
    splits = _pick_best_splits(text, candidates, n - 1)

    if len(splits) < n - 1:
        # Not enough natural breaks. Use what we have, then subdivide
        # the longest segments.
        segments = _apply_splits(text, splits)
        while len(segments) < n:
            segments = _subdivide_longest(segments)
        return segments

    return _apply_splits(text, splits)


def _pick_best_splits(text, candidates, needed):
    """Pick `needed` split points from candidates that distribute text evenly."""
    if len(candidates) <= needed:
        return [pos for pos, pri in candidates]

    total_len = len(text)
    ideal_segment = total_len / (needed + 1)

    # Greedy: for each target position, pick the nearest candidate
    used = set()
    result = []
    for i in range(1, needed + 1):
        target = ideal_segment * i
        best_pos = None
        best_dist = float("inf")
        best_pri = float("inf")
        for pos, pri in candidates:
            if pos in used:
                continue
            dist = abs(pos - target)
            # Prefer closer to target, break ties by priority
            if dist < best_dist or (dist == best_dist and pri < best_pri):
                best_pos = pos
                best_dist = dist
                best_pri = pri
        if best_pos is not None:
            used.add(best_pos)
            result.append(best_pos)

    result.sort()
    return result


def _apply_splits(text, split_positions):
    """Apply split positions to produce segments."""
    segments = []
    prev = 0
    for pos in sorted(split_positions):
        seg = text[prev:pos].strip()
        if seg:
            segments.append(seg)
        prev = pos
    # Last segment
    seg = text[prev:].strip()
    if seg:
        segments.append(seg)
    return segments


def _subdivide_longest(segments):
    """Split the longest segment at its midpoint (by words)."""
    if not segments:
        return segments

    # Find longest segment
    idx = max(range(len(segments)), key=lambda i: len(segments[i]))
    seg = segments[idx]

    # Try to find a natural break in this segment
    candidates = find_split_candidates(seg)
    if candidates:
        # Pick the one closest to midpoint
        mid = len(seg) / 2
        best_pos = min(candidates, key=lambda x: abs(x[0] - mid))[0]
        left = seg[:best_pos].strip()
        right = seg[best_pos:].strip()
    else:
        # Split at word boundary nearest midpoint
        words = seg.split()
        if len(words) < 2:
            return segments  # Can't split single word
        mid_idx = len(words) // 2
        left = " ".join(words[:mid_idx])
        right = " ".join(words[mid_idx:])

    if left and right:
        return segments[:idx] + [left, right] + segments[idx + 1:]
    return segments


def _split_evenly_by_words(text, n):
    """Split text into n roughly equal parts by word count."""
    words = text.split()
    if len(words) <= n:
        # More lines than words — some lines will be single words
        result = []
        for w in words:
            result.append(w)
        while len(result) < n:
            result.append("")
        return result

    per = len(words) / n
    result = []
    for i in range(n):
        start = round(per * i)
        end = round(per * (i + 1))
        result.append(" ".join(words[start:end]))
    return result


# ---------------------------------------------------------------------------
# Main alignment logic
# ---------------------------------------------------------------------------
def align_book(slug, verbose=False):
    """Align YLT text for one book. Returns stats dict."""
    booknum = SLUG_TO_BOOKNUM[slug]
    ylt_data = ensure_ylt_data(booknum)

    # Find all v3-colometric chapter files for this book
    chapter_files = sorted(V3_DIR.glob(f"{slug}-*.txt"))
    if not chapter_files:
        print(f"  WARNING: No v3-colometric files found for {slug}", file=sys.stderr)
        return {"total_verses": 0, "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    YLT_OUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"total_verses": 0, "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    for greek_file in chapter_files:
        # Extract chapter number from filename: e.g. "acts-09.txt" -> 9
        fname = greek_file.stem  # "acts-09"
        ch_str = fname.split("-")[-1]
        ch_num = int(ch_str)

        greek_verses = parse_greek_chapter(greek_file)
        ylt_ch = ylt_data.get(ch_num, {})

        out_lines = []

        for verse_num in sorted(greek_verses.keys()):
            greek_line_count = len(greek_verses[verse_num])
            ylt_text = ylt_ch.get(verse_num, "")

            stats["total_verses"] += 1

            if not ylt_text:
                stats["missing_ylt"] += 1
                # Write verse ref and placeholder
                out_lines.append(f"{ch_num}:{verse_num}")
                out_lines.append("[YLT text not available]")
                out_lines.append("")
                continue

            # Split YLT into same number of lines
            english_lines = split_text_into_n(ylt_text, greek_line_count)

            # Ensure exactly the right count
            while len(english_lines) < greek_line_count:
                english_lines.append("")
            if len(english_lines) > greek_line_count:
                # Merge extras onto last line
                english_lines = english_lines[:greek_line_count - 1] + [
                    " ".join(english_lines[greek_line_count - 1:])
                ]

            # Check if we needed forced splits
            candidates_in_text = find_split_candidates(ylt_text)
            natural_breaks_available = len(candidates_in_text)
            breaks_needed = greek_line_count - 1
            if breaks_needed > 0 and natural_breaks_available >= breaks_needed:
                stats["natural_splits"] += 1
            elif breaks_needed > 0:
                stats["forced_splits"] += 1
            else:
                stats["natural_splits"] += 1  # 1-line verse, trivially natural

            # Write output
            out_lines.append(f"{ch_num}:{verse_num}")
            for el in english_lines:
                out_lines.append(el)
            out_lines.append("")

        # Write output file with same filename
        out_path = YLT_OUT_DIR / greek_file.name
        out_path.write_text("\n".join(out_lines), encoding="utf-8")
        if verbose:
            print(f"  Wrote {out_path.name} ({len(greek_verses)} verses)")

    return stats


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------
def run_tests():
    """Run test cases on specific passages."""
    print("=" * 70)
    print("TEST: Acts 9:1-3")
    print("=" * 70)

    # Ensure Acts YLT data
    ylt_data = ensure_ylt_data(44)
    greek_file = V3_DIR / "acts-09.txt"
    greek_verses = parse_greek_chapter(greek_file)

    for v in [1, 2, 3]:
        greek_lines = greek_verses[v]
        ylt_text = ylt_data[9][v]
        english_lines = split_text_into_n(ylt_text, len(greek_lines))
        while len(english_lines) < len(greek_lines):
            english_lines.append("")
        if len(english_lines) > len(greek_lines):
            english_lines = english_lines[:len(greek_lines) - 1] + [
                " ".join(english_lines[len(greek_lines) - 1:])
            ]

        print(f"\n--- Acts 9:{v} ({len(greek_lines)} Greek lines) ---")
        print("GREEK:")
        for gl in greek_lines:
            print(f"  {gl}")
        print("YLT:")
        for el in english_lines:
            print(f"  {el}")

    print()
    print("=" * 70)
    print("TEST: 1 Timothy 3:16 (hymn — expecting 6+ Greek lines)")
    print("=" * 70)

    ylt_data_1tim = ensure_ylt_data(54)
    greek_file_1tim = V3_DIR / "1tim-03.txt"
    greek_verses_1tim = parse_greek_chapter(greek_file_1tim)

    v = 16
    greek_lines = greek_verses_1tim[v]
    ylt_text = ylt_data_1tim[3][v]
    english_lines = split_text_into_n(ylt_text, len(greek_lines))
    while len(english_lines) < len(greek_lines):
        english_lines.append("")
    if len(english_lines) > len(greek_lines):
        english_lines = english_lines[:len(greek_lines) - 1] + [
            " ".join(english_lines[len(greek_lines) - 1:])
        ]

    print(f"\n--- 1 Tim 3:16 ({len(greek_lines)} Greek lines) ---")
    print("GREEK:")
    for gl in greek_lines:
        print(f"  {gl}")
    print("YLT:")
    for el in english_lines:
        print(f"  {el}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Align YLT to GNT colometric line breaks")
    parser.add_argument("--book", type=str, help="Process single book by slug (e.g. 'acts')")
    parser.add_argument("--test", action="store_true", help="Run test cases")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.book:
        slug = args.book.lower()
        if slug not in SLUG_TO_BOOKNUM:
            print(f"ERROR: Unknown book slug '{slug}'", file=sys.stderr)
            print(f"Valid slugs: {', '.join(sorted(SLUG_TO_BOOKNUM.keys()))}", file=sys.stderr)
            sys.exit(1)
        slugs = [slug]
    else:
        slugs = [BOOKNUM_TO_SLUG[n] for n in sorted(BOOKNUM_TO_SLUG.keys())]

    grand_stats = {"total_verses": 0, "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    for slug in slugs:
        print(f"Processing {slug}...")
        stats = align_book(slug, verbose=args.verbose)
        for k in grand_stats:
            grand_stats[k] += stats[k]
        if stats["total_verses"] > 0:
            pct = stats["natural_splits"] / stats["total_verses"] * 100
            print(f"  {stats['total_verses']} verses: "
                  f"{stats['natural_splits']} natural ({pct:.1f}%), "
                  f"{stats['forced_splits']} forced, "
                  f"{stats['missing_ylt']} missing YLT")

    print()
    print("=" * 50)
    print("GRAND TOTALS")
    print("=" * 50)
    total = grand_stats["total_verses"]
    if total > 0:
        nat_pct = grand_stats["natural_splits"] / total * 100
        forced_pct = grand_stats["forced_splits"] / total * 100
        print(f"Total verses:    {total}")
        print(f"Natural splits:  {grand_stats['natural_splits']} ({nat_pct:.1f}%)")
        print(f"Forced splits:   {grand_stats['forced_splits']} ({forced_pct:.1f}%)")
        print(f"Missing YLT:     {grand_stats['missing_ylt']}")


if __name__ == "__main__":
    main()
