#!/usr/bin/env python3
"""
bezae_compare.py - Compare Codex Bezae manuscript line breaks with GNT Reader v3 colometric output.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/bezae_compare.py                                    # full report
    PYTHONIOENCODING=utf-8 py -3 scripts/bezae_compare.py --book mark                        # one book
    PYTHONIOENCODING=utf-8 py -3 scripts/bezae_compare.py --book mark --chapter 4 --side-by-side  # side by side
"""

import argparse
import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BEZAE_XML = PROJECT_DIR / "research" / "codex-bezae" / "Bezae-Greek.xml"

TIER_DIRS = {
    "v1": PROJECT_DIR / "data" / "text-files" / "v1-colometric",
    "v2": PROJECT_DIR / "data" / "text-files" / "v2-colometric",
    "v3": PROJECT_DIR / "data" / "text-files" / "v3-colometric",
    "v4": PROJECT_DIR / "data" / "text-files" / "v4-editorial",
}
V3_DIR = TIER_DIRS["v3"]  # default

NS = "http://www.tei-c.org/ns/1.0"
NS_MAP = {"t": NS}

# Bezae book codes -> our file prefix
BOOK_MAP = {
    "B01": "matt",
    "B02": "mark",
    "B03": "luke",
    "B04": "john",
    "B05": "acts",
}

# Reverse: file prefix -> Bezae book code
BOOK_MAP_REV = {v: k for k, v in BOOK_MAP.items()}

# Bezae book div n-attribute -> our prefix
BOOK_N_MAP = {
    "Matthew": "matt",
    "Mark": "mark",
    "Luke": "luke",
    "John": "john",
    "Acts": "acts",
}

# ---------------------------------------------------------------------------
# Unicode / text normalization
# ---------------------------------------------------------------------------

def strip_accents(text):
    """Remove all combining diacritical marks (accents, breathings, etc.)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) not in ("Mn", "Mc"))


def normalize_word(w):
    """Normalize a Greek word for fuzzy comparison: lowercase, strip accents,
    remove punctuation, normalize common spelling variants."""
    w = strip_accents(w)
    w = w.lower()
    # Remove non-letter characters
    w = re.sub(r"[^a-zα-ωϊϋ]", "", w)
    # Normalize common Bezae spellings
    w = w.replace("ϊ", "ι").replace("ϋ", "υ")
    return w


def extract_text_recursive(elem):
    """Recursively extract all text content from an element and its children."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(extract_text_recursive(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


# ---------------------------------------------------------------------------
# Parse Bezae XML
# ---------------------------------------------------------------------------

def tag(local):
    """Create a namespaced tag string."""
    return f"{{{NS}}}{local}"


def parse_bezae(xml_path, book_filter=None):
    """Parse Bezae-Greek.xml and extract line breaks per verse.

    Returns:
        dict: {book_prefix: {(chapter, verse): [line_words_list, ...]}}
        Each line_words_list is a list of word strings for that manuscript line.
        Also returns hang info:
        dict: {book_prefix: {(chapter, verse): [bool, ...]}}  -- True if line has rend=hang
    """
    print(f"Parsing {xml_path.name} ...", file=sys.stderr)

    # Read raw XML and handle custom entities
    with open(xml_path, "r", encoding="utf-8") as f:
        raw = f.read()

    # The XML has a DOCTYPE with custom entities. ET doesn't handle them well.
    # Replace the entities inline before parsing.
    # From the DOCTYPE: &ντ; -> ντ, &om; -> ⸆
    # But the DOCTYPE already defines them, so ET should handle it if we
    # use a custom parser. Let's try iterparse approach with entity expansion.

    # Actually, let's just strip the DOCTYPE and replace entities manually.
    # The entities are: &nt; -> "ντ"  and  &om; -> "⸆"
    raw = re.sub(r"<!DOCTYPE[^>]*\[.*?\]>", "", raw, flags=re.DOTALL)
    # Replace any remaining entity references that ET can't handle
    raw = raw.replace("&ντ;", "ντ")
    raw = raw.replace("&nt;", "ντ")
    raw = raw.replace("&om;", "⸆")

    root = ET.fromstring(raw)

    verses_data = {}   # {book: {(ch, vs): [ [words_in_line], ... ]}}
    hang_data = {}     # {book: {(ch, vs): [bool, ...]}}

    for book_div in root.iter(tag("div")):
        if book_div.get("type") != "book":
            continue
        book_name = book_div.get("n")  # e.g. "Matthew", "Mark"
        if book_name not in BOOK_N_MAP:
            continue
        book_prefix = BOOK_N_MAP[book_name]

        if book_filter and book_prefix != book_filter:
            continue

        verses_data[book_prefix] = {}
        hang_data[book_prefix] = {}

        # Iterate through all elements in document order within this book
        # We need to track: current verse, current line's words, and lb boundaries
        _parse_book_div(book_div, book_prefix, verses_data, hang_data)

    print(f"  Parsed {sum(len(v) for v in verses_data.values())} verses across {len(verses_data)} books.", file=sys.stderr)
    return verses_data, hang_data


def _parse_book_div(book_div, book_prefix, verses_data, hang_data):
    """Walk a book div and extract line breaks per verse.

    Strategy: iterate all elements in document order. Track current verse
    from <ab> elements. Track line breaks from <lb/> elements. Collect
    words from <w> elements (using original readings from <app>/<rdg>).
    """
    current_verse = None  # (chapter, verse) tuple
    current_line_words = []
    current_line_is_hang = False
    verse_lines = []      # list of [words] for current verse
    verse_hangs = []       # list of bool for current verse

    # We need to walk the entire tree in document order.
    # ET doesn't have a great "document order" iterator that includes
    # both start and end events for tracking context, so use iterparse-like manual walk.

    # Instead, let's flatten all relevant elements by iterating all elements
    # and using a stack approach. Actually, the simplest approach:
    # collect all <ab>, <lb>, <w>, <pc>, <app> in document order.

    def walk_and_collect(elem, in_orig_rdg=True, in_corr_rdg=False):
        """Yield (event_type, element) tuples in document order.
        Handles <app>/<rdg> by only yielding from type="orig" readings."""
        t = elem.tag

        if t == tag("app"):
            # Find orig and corr readings
            for rdg in elem:
                if rdg.tag == tag("rdg"):
                    rdg_type = rdg.get("type", "")
                    if rdg_type == "orig":
                        yield from walk_and_collect(rdg, in_orig_rdg=True, in_corr_rdg=False)
                    # Skip corr readings
            return

        if t == tag("rdg"):
            # Only process if we're in an orig reading context
            if not in_orig_rdg:
                return
            for child in elem:
                yield from walk_and_collect(child, in_orig_rdg=True)
            return

        if t == tag("ab"):
            yield ("ab", elem)
            for child in elem:
                yield from walk_and_collect(child, in_orig_rdg=in_orig_rdg)
            return

        if t == tag("lb"):
            yield ("lb", elem)
            return

        if t == tag("w"):
            yield ("w", elem)
            return

        if t == tag("pc"):
            yield ("pc", elem)
            return

        if t == tag("pb") or t == tag("cb"):
            # Skip page/column breaks
            return

        if t == tag("fw") or t == tag("note"):
            # Skip running titles, lectionary references, editorial notes
            return

        if t == tag("seg"):
            # Skip marginal content (running titles, chapter numbers, etc.)
            subtype = elem.get("subtype", "")
            if "margin" in (elem.get("type", "") + subtype):
                return

        # For other elements (div, etc.), recurse into children
        for child in elem:
            yield from walk_and_collect(child, in_orig_rdg=in_orig_rdg)

    def flush_verse():
        nonlocal current_verse, verse_lines, verse_hangs, current_line_words, current_line_is_hang
        if current_verse and (verse_lines or current_line_words):
            # Flush current line
            if current_line_words:
                verse_lines.append(current_line_words)
                verse_hangs.append(current_line_is_hang)
            verses_data[book_prefix][current_verse] = verse_lines
            hang_data[book_prefix][current_verse] = verse_hangs
        verse_lines = []
        verse_hangs = []
        current_line_words = []
        current_line_is_hang = False

    for event_type, elem in walk_and_collect(book_div):
        if event_type == "ab":
            n = elem.get("n", "")
            lang = elem.get("{http://www.w3.org/XML/1998/namespace}lang", "")
            if lang != "grc":
                continue
            # Parse verse ref: B02K4V3 -> chapter=4, verse=3
            m = re.match(r"B(\d+)K(\d+)V(\d+[a-z]?)", n)
            if not m:
                continue
            ch = int(m.group(2))
            vs = m.group(3)  # keep as string to handle "2a" etc.

            # Flush previous verse
            flush_verse()
            current_verse = (ch, vs)

        elif event_type == "lb":
            # An lb starts a new line. Flush current line words to verse.
            if current_line_words and current_verse:
                verse_lines.append(current_line_words)
                verse_hangs.append(current_line_is_hang)
                current_line_words = []
            current_line_is_hang = (elem.get("rend") == "hang")

        elif event_type == "w":
            word_text = extract_text_recursive(elem).strip()
            if word_text and word_text != "⸆":  # skip omission markers
                current_line_words.append(word_text)

        elif event_type == "pc":
            pass  # Skip punctuation for word-level comparison

    # Flush last verse
    flush_verse()


# ---------------------------------------------------------------------------
# Parse v3 colometric files
# ---------------------------------------------------------------------------

def parse_v3_chapter(filepath):
    """Parse a v3 colometric chapter file.

    Returns:
        dict: {(chapter, verse_str): [line_words_list, ...]}
        Each line_words_list is a list of word strings for that colometric line.
    """
    verses = {}
    current_verse = None
    current_lines = []

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n").rstrip("\r")

            # Verse reference line: "4:1" or "4:1a"
            m = re.match(r"^(\d+):(\d+[a-z]?)\s*$", line)
            if m:
                # Flush previous verse
                if current_verse and current_lines:
                    verses[current_verse] = current_lines
                ch = int(m.group(1))
                vs = m.group(2)
                current_verse = (ch, vs)
                current_lines = []
                continue

            # Blank line = verse separator (ignore)
            if not line.strip():
                continue

            # Text line - extract words
            words = line.split()
            if words:
                current_lines.append(words)

    # Flush last verse
    if current_verse and current_lines:
        verses[current_verse] = current_lines

    return verses


def load_v3_book(book_prefix, chapter_filter=None, input_dir=None):
    """Load all colometric chapters for a book from a given tier directory.

    Returns:
        dict: {(chapter, verse): [line_words_list, ...]}
    """
    src_dir = input_dir or V3_DIR
    all_verses = {}
    pattern = f"{book_prefix}-*.txt"
    for filepath in sorted(src_dir.glob(pattern)):
        # Extract chapter number from filename: mark-04.txt -> 4
        ch_match = re.search(r"-(\d+)\.txt$", filepath.name)
        if not ch_match:
            continue
        ch_num = int(ch_match.group(1))
        if chapter_filter is not None and ch_num != chapter_filter:
            continue

        chapter_verses = parse_v3_chapter(filepath)
        all_verses.update(chapter_verses)

    return all_verses


# ---------------------------------------------------------------------------
# Alignment and comparison
# ---------------------------------------------------------------------------

def get_break_positions(lines):
    """Given a list of lines (each a list of words), return the set of
    word positions where breaks occur.

    A break occurs after word position N (0-indexed cumulative) if there's
    a line boundary there. We return the set of positions after which breaks occur.
    """
    positions = set()
    cumulative = 0
    for i, line_words in enumerate(lines):
        if i > 0:
            positions.add(cumulative)  # break before this line = after position cumulative
        cumulative += len(line_words)
    return positions, cumulative


def normalize_word_list(words):
    """Normalize a flat list of words for comparison."""
    return [normalize_word(w) for w in words]


def flatten_lines(lines):
    """Flatten a list of lines into a single word list."""
    return [w for line in lines for w in line]


def compute_verse_agreement(bezae_lines, v3_lines, tolerance=1):
    """Compute break agreement between Bezae and v3 for a single verse.

    Returns:
        dict with:
            bezae_breaks: int - number of line breaks in Bezae
            v3_breaks: int - number of line breaks in v3
            agreed: int - number of v3 breaks that align with a Bezae break (within tolerance)
            agreement_rate: float - agreed / v3_breaks (or 1.0 if both have 0 breaks)
    """
    if not bezae_lines or not v3_lines:
        return None

    # Normalize words
    bezae_words = normalize_word_list(flatten_lines(bezae_lines))
    v3_words = normalize_word_list(flatten_lines(v3_lines))

    # Get break positions in terms of cumulative word indices
    bezae_breaks, bezae_total = get_break_positions(bezae_lines)
    v3_breaks, v3_total = get_break_positions(v3_lines)

    if not v3_breaks and not bezae_breaks:
        return {
            "bezae_breaks": 0,
            "v3_breaks": 0,
            "agreed": 0,
            "agreement_rate": 1.0,
        }

    if not v3_breaks:
        return {
            "bezae_breaks": len(bezae_breaks),
            "v3_breaks": 0,
            "agreed": 0,
            "agreement_rate": 0.0,
        }

    # For fuzzy alignment: the texts may have different numbers of words.
    # We need to map break positions from v3 word-space to Bezae word-space.
    # Simple approach: scale positions proportionally if word counts differ.
    # Better approach: use normalized word sequence alignment.

    # Use a simple proportional mapping when word counts differ
    if bezae_total > 0 and v3_total > 0:
        scale = bezae_total / v3_total
    else:
        scale = 1.0

    agreed = 0
    for v3_pos in v3_breaks:
        # Map v3 position to Bezae position space
        mapped_pos = v3_pos * scale
        # Check if any Bezae break is within tolerance
        for bez_pos in bezae_breaks:
            if abs(mapped_pos - bez_pos) <= tolerance + 0.5:
                agreed += 1
                break

    agreement_rate = agreed / len(v3_breaks) if v3_breaks else 1.0

    return {
        "bezae_breaks": len(bezae_breaks),
        "v3_breaks": len(v3_breaks),
        "agreed": agreed,
        "agreement_rate": min(agreement_rate, 1.0),
    }


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def book_summary_report(bezae_data, hang_data, book_prefix, chapter_filter=None, input_dir=None):
    """Generate comparison data for a single book.

    Returns list of per-verse results.
    """
    v3_data = load_v3_book(book_prefix, chapter_filter=chapter_filter, input_dir=input_dir)
    bezae_verses = bezae_data.get(book_prefix, {})

    results = []
    def verse_sort_key(v):
        """Sort verses numerically: (chapter, verse_num, verse_suffix)."""
        ch, vs = v
        m = re.match(r"(\d+)(.*)", vs)
        return (ch, int(m.group(1)) if m else 0, m.group(2) if m else vs)

    for verse_key in sorted(bezae_verses.keys(), key=verse_sort_key):
        if verse_key not in v3_data:
            continue
        if chapter_filter is not None and verse_key[0] != chapter_filter:
            continue

        agreement = compute_verse_agreement(bezae_verses[verse_key], v3_data[verse_key])
        if agreement is None:
            continue

        results.append({
            "verse": verse_key,
            "bezae_lines": bezae_verses[verse_key],
            "v3_lines": v3_data[verse_key],
            "hang_flags": hang_data.get(book_prefix, {}).get(verse_key, []),
            **agreement,
        })

    return results


def print_book_summary(results, book_prefix):
    """Print a summary for one book."""
    if not results:
        print(f"\n  {book_prefix}: no overlapping verses found")
        return

    total_v3_breaks = sum(r["v3_breaks"] for r in results)
    total_bezae_breaks = sum(r["bezae_breaks"] for r in results)
    total_agreed = sum(r["agreed"] for r in results)
    avg_agreement = total_agreed / total_v3_breaks if total_v3_breaks > 0 else 0.0

    print(f"\n  {book_prefix.upper():<8} "
          f"verses={len(results):<5} "
          f"v3_breaks={total_v3_breaks:<6} "
          f"bezae_breaks={total_bezae_breaks:<6} "
          f"agreed={total_agreed:<6} "
          f"agreement={avg_agreement:.1%}")


def print_chapter_detail(results, book_prefix, top_n=5):
    """Print per-chapter detail showing highest and lowest agreement verses."""
    if not results:
        return

    # Group by chapter
    by_chapter = defaultdict(list)
    for r in results:
        by_chapter[r["verse"][0]].append(r)

    for ch in sorted(by_chapter.keys()):
        ch_results = by_chapter[ch]
        ch_v3_breaks = sum(r["v3_breaks"] for r in ch_results)
        ch_agreed = sum(r["agreed"] for r in ch_results)
        ch_rate = ch_agreed / ch_v3_breaks if ch_v3_breaks > 0 else 0.0

        print(f"\n    Chapter {ch}: {len(ch_results)} verses, "
              f"agreement={ch_rate:.1%} "
              f"({ch_agreed}/{ch_v3_breaks} breaks)")

        # Sort by agreement rate
        rated = [(r["agreement_rate"], r) for r in ch_results if r["v3_breaks"] > 0]
        rated.sort(key=lambda x: x[0])

        if rated:
            # Lowest agreement
            low = rated[:min(top_n, len(rated))]
            if low and low[0][0] < 1.0:
                print(f"      Lowest:  ", end="")
                print(", ".join(
                    f"{r['verse'][0]}:{r['verse'][1]}({rate:.0%})"
                    for rate, r in low if rate < 1.0
                ))

            # Highest agreement
            high = rated[-min(top_n, len(rated)):]
            high.reverse()
            if high and high[0][0] > 0.0:
                print(f"      Highest: ", end="")
                print(", ".join(
                    f"{r['verse'][0]}:{r['verse'][1]}({rate:.0%})"
                    for rate, r in high if rate > 0.0
                ))


def print_side_by_side(results, book_prefix, chapter):
    """Print side-by-side comparison for a specific chapter."""
    ch_results = [r for r in results if r["verse"][0] == chapter]
    if not ch_results:
        print(f"\n  No results for {book_prefix} chapter {chapter}")
        return

    col_width = 45
    print(f"\n{'=' * (col_width * 2 + 7)}")
    print(f"  SIDE-BY-SIDE: {book_prefix.upper()} CHAPTER {chapter}")
    print(f"  {'CODEX BEZAE':<{col_width}}  |  {'GNT READER v3':<{col_width}}")
    print(f"{'=' * (col_width * 2 + 7)}")

    for r in ch_results:
        ch, vs = r["verse"]
        print(f"\n  [{ch}:{vs}]  (agreement: {r['agreement_rate']:.0%}, "
              f"Bezae={r['bezae_breaks']} breaks, v3={r['v3_breaks']} breaks)")
        print(f"  {'-' * (col_width * 2 + 3)}")

        bezae_lines = r["bezae_lines"]
        v3_lines = r["v3_lines"]
        max_lines = max(len(bezae_lines), len(v3_lines))

        for i in range(max_lines):
            if i < len(bezae_lines):
                bz = " ".join(bezae_lines[i])
                # Mark hang lines
                hang_marker = "[H] " if (i < len(r["hang_flags"]) and r["hang_flags"][i]) else "    "
                bz_display = hang_marker + bz
            else:
                bz_display = ""

            if i < len(v3_lines):
                v3 = " ".join(v3_lines[i])
            else:
                v3 = ""

            # Truncate if too long
            if len(bz_display) > col_width:
                bz_display = bz_display[:col_width - 3] + "..."
            if len(v3) > col_width:
                v3 = v3[:col_width - 3] + "..."

            print(f"  {bz_display:<{col_width}}  |  {v3}")


def run_full_report(bezae_data, hang_data, book_filter=None, chapter_filter=None,
                    input_dir=None, tier_label="v3"):
    """Run the full comparison report."""
    books = [book_filter] if book_filter else list(BOOK_MAP.values())

    all_results = {}
    for book in books:
        if book not in bezae_data:
            continue
        results = book_summary_report(bezae_data, hang_data, book,
                                      chapter_filter=chapter_filter, input_dir=input_dir)
        all_results[book] = results

    # Per-book summary
    print("\n" + "=" * 80)
    print(f"  BEZAE vs GNT READER {tier_label} — BREAK AGREEMENT REPORT")
    print("=" * 80)

    grand_v3 = 0
    grand_agreed = 0
    for book in books:
        if book not in all_results:
            continue
        results = all_results[book]
        print_book_summary(results, book)
        grand_v3 += sum(r["v3_breaks"] for r in results)
        grand_agreed += sum(r["agreed"] for r in results)

    if len(all_results) > 1:
        overall = grand_agreed / grand_v3 if grand_v3 > 0 else 0.0
        print(f"\n  {'OVERALL':<8} agreement={overall:.1%} ({grand_agreed}/{grand_v3} breaks)")

    # Per-chapter detail
    print("\n" + "-" * 80)
    print("  PER-CHAPTER DETAIL")
    print("-" * 80)

    for book in books:
        if book not in all_results:
            continue
        results = all_results[book]
        if results:
            print(f"\n  {book.upper()}")
            print_chapter_detail(results, book)

    return all_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare Codex Bezae line breaks with GNT Reader v3 colometric output."
    )
    parser.add_argument("--book", type=str, default=None,
                        help="Book to analyze (matt, mark, luke, john, acts)")
    parser.add_argument("--chapter", type=int, default=None,
                        help="Chapter number (requires --book)")
    parser.add_argument("--side-by-side", action="store_true",
                        help="Show side-by-side comparison (requires --book and --chapter)")
    parser.add_argument("--tier", type=str, default="v4", choices=["v1", "v2", "v3", "v4"],
                        help="Which colometric tier to compare (default: v4)")
    parser.add_argument("--all-tiers", action="store_true",
                        help="Compare all four tiers against Bezae in a summary table")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")
    if args.side_by_side and (not args.book or not args.chapter):
        parser.error("--side-by-side requires both --book and --chapter")

    # Validate book
    if args.book:
        if args.book not in BOOK_MAP_REV:
            parser.error(f"Unknown book: {args.book}. Choose from: {', '.join(BOOK_MAP.values())}")

    # Parse Bezae
    bezae_data, hang_data = parse_bezae(BEZAE_XML, book_filter=args.book)

    if args.all_tiers:
        # Run all three tiers and show a comparison table
        print("\n" + "=" * 80)
        print("  BEZAE AGREEMENT — ALL TIERS COMPARISON")
        print("=" * 80)
        all_tier_names = ["v1", "v2", "v3", "v4"]
        header = f"  {'BOOK':<8}" + "".join(f" {t:>8}" for t in all_tier_names)
        separator = f"  {'----':<8}" + "".join(f" {'----':>8}" for _ in all_tier_names)
        print(f"\n{header}")
        print(separator)

        tier_totals = {t: {"breaks": 0, "agreed": 0} for t in all_tier_names}
        books = [args.book] if args.book else list(BOOK_MAP.values())

        for book in books:
            if book not in bezae_data:
                continue
            row = f"  {book.upper():<8}"
            for tier in all_tier_names:
                tier_dir = TIER_DIRS[tier]
                results = book_summary_report(bezae_data, hang_data, book,
                                              chapter_filter=args.chapter,
                                              input_dir=tier_dir)
                total_breaks = sum(r["v3_breaks"] for r in results)
                total_agreed = sum(r["agreed"] for r in results)
                rate = total_agreed / total_breaks if total_breaks > 0 else 0.0
                row += f" {rate:>7.1%}"
                tier_totals[tier]["breaks"] += total_breaks
                tier_totals[tier]["agreed"] += total_agreed
            print(row)

        if len(books) > 1:
            row = f"  {'OVERALL':<8}"
            for tier in all_tier_names:
                t = tier_totals[tier]
                rate = t["agreed"] / t["breaks"] if t["breaks"] > 0 else 0.0
                row += f" {rate:>7.1%}"
            print(f"  {'-------':<8}" + "".join(f" {'-------':>8}" for _ in all_tier_names))
            print(row)

        print()
    else:
        # Single tier report
        input_dir = TIER_DIRS[args.tier]

        # Run report
        all_results = run_full_report(bezae_data, hang_data,
                                      book_filter=args.book,
                                      chapter_filter=args.chapter,
                                      input_dir=input_dir,
                                      tier_label=args.tier)

        # Side-by-side
        if args.side_by_side:
            results = all_results.get(args.book, [])
            print_side_by_side(results, args.book, args.chapter)

        print()


if __name__ == "__main__":
    main()
