#!/usr/bin/env python3
"""
ylt_align_lcs.py — LCS-based YLT alignment prototype.

For each verse:
1. Build a "Macula English" sequence: for each Greek word in verse order,
   collect its gloss/english attributes. Each entry knows which colometric
   line it belongs to.
2. Tokenize the YLT verse text.
3. Run word-level LCS between Macula English tokens and YLT tokens,
   using synonym-aware matching.
4. Each matched YLT word inherits the line number of its matched Macula word.
5. Unmatched YLT words get assigned the line of their nearest matched
   neighbor (bias toward FOLLOWING anchor).
6. Cut between the last YLT word assigned to line K and first assigned to K+1.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align_lcs.py --book mark --chapter 4
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align_lcs.py --book mark --chapter 4 --verses 1,4,9,19,21,26,32
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Import shared utilities from ylt_align.py
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ylt_align import (
    _are_synonyms,
    _stem_english,
    _normalize,
    _normalize_greek,
    _gloss_to_tokens,
    _build_word_line_map,
    load_macula_book,
    parse_greek_chapter,
    ensure_ylt_data,
    SLUG_TO_BOOKNUM,
    BOOKNUM_TO_SLUG,
    REPO,
    V3_DIR,
    YLT_RAW_DIR,
)

V4_DIR = REPO / "data" / "text-files" / "v4-editorial"


# ---------------------------------------------------------------------------
# LCS matching helpers
# ---------------------------------------------------------------------------

def _words_match(a, b):
    """Check if two normalized English words match (exact, stem, or synonym)."""
    if a == b:
        return True
    a_stem = _stem_english(a)
    b_stem = _stem_english(b)
    if a_stem == b_stem and len(a_stem) >= 3:
        return True
    if _are_synonyms(a, b):
        return True
    if a_stem != a and _are_synonyms(a_stem, b):
        return True
    if b_stem != b and _are_synonyms(a, b_stem):
        return True
    # Substring for compound forms (e.g. "thirtyfold" contains "thirty")
    if len(a) >= 6 and a in b:
        return True
    if len(b) >= 6 and b in a:
        return True
    return False


def _lcs_align(macula_tokens, ylt_tokens):
    """Run LCS alignment between Macula English tokens and YLT tokens.

    Args:
        macula_tokens: list of (normalized_word, line_index) from Macula
        ylt_tokens: list of normalized YLT words

    Returns:
        list of (ylt_index, macula_index) pairs — the LCS matches
    """
    n = len(macula_tokens)
    m = len(ylt_tokens)

    # Build DP table
    # dp[i][j] = length of LCS of macula_tokens[:i] and ylt_tokens[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        mw = macula_tokens[i - 1][0]
        for j in range(1, m + 1):
            yw = ylt_tokens[j - 1]
            if _words_match(mw, yw):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find the actual aligned pairs
    pairs = []
    i, j = n, m
    while i > 0 and j > 0:
        mw = macula_tokens[i - 1][0]
        yw = ylt_tokens[j - 1]
        if _words_match(mw, yw):
            pairs.append((j - 1, i - 1))  # (ylt_index, macula_index)
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    pairs.reverse()
    return pairs


def split_ylt_by_lcs(greek_lines, macula_words, ylt_text):
    """Split YLT text to match Greek colometric line structure using LCS alignment.

    Args:
        greek_lines: list of Greek colometric line strings for the verse
        macula_words: list of (word_pos, greek_text, gloss, english) for the verse
        ylt_text: raw YLT verse text

    Returns:
        list of YLT line strings matching the colometric structure,
        or None if alignment fails
    """
    if not greek_lines or not macula_words or not ylt_text:
        return None

    num_lines = len(greek_lines)

    # Step 1: Map each Macula word to its colometric line
    word_line_map = _build_word_line_map(greek_lines, macula_words)
    if not word_line_map:
        return None

    # Step 2: Build Macula English token sequence
    # For each Macula word, gather gloss AND english tokens, all tagged with the line index
    macula_tokens = []  # [(normalized_word, line_index), ...]
    for line_idx, gloss, english in word_line_map:
        # Use both gloss and english for better coverage
        # Prefer english tokens (closer to YLT), but add gloss tokens too
        seen = set()
        for source in [english, gloss]:
            for token in _gloss_to_tokens(source):
                if token and token not in seen:
                    seen.add(token)
                    macula_tokens.append((token, line_idx))

    if not macula_tokens:
        return None

    # Step 3: Tokenize YLT text
    ylt_raw_tokens = re.findall(r'\S+', ylt_text)
    ylt_norm = [_normalize(w) for w in ylt_raw_tokens]

    if not ylt_norm:
        return None

    # Step 4: Run LCS alignment
    pairs = _lcs_align(macula_tokens, ylt_norm)

    # Step 5: Assign line numbers to YLT words
    # matched_lines[i] = line_index for ylt word i, or -1 if unmatched
    matched_lines = [-1] * len(ylt_norm)
    for ylt_idx, macula_idx in pairs:
        matched_lines[ylt_idx] = macula_tokens[macula_idx][1]

    # Step 6: Fill in unmatched words
    # Bias toward FOLLOWING anchor (English function words precede their head)
    assigned_lines = list(matched_lines)

    # Forward fill from following anchor
    for i in range(len(assigned_lines)):
        if assigned_lines[i] == -1:
            # Look forward for next matched word
            found = False
            for j in range(i + 1, len(assigned_lines)):
                if assigned_lines[j] != -1:
                    assigned_lines[i] = assigned_lines[j]
                    found = True
                    break
            if not found:
                # No forward match — use last matched word's line
                for j in range(i - 1, -1, -1):
                    if assigned_lines[j] != -1:
                        assigned_lines[i] = assigned_lines[j]
                        found = True
                        break
            if not found:
                # No matches at all — put everything on line 0
                assigned_lines[i] = 0

    # Step 7: Enforce monotonicity — line assignments should never decrease
    # (since English generally follows Greek word order at the clause level)
    for i in range(1, len(assigned_lines)):
        if assigned_lines[i] < assigned_lines[i - 1]:
            assigned_lines[i] = assigned_lines[i - 1]

    # Step 8: Build output lines by cutting at line transitions
    output_lines = []
    current_line_idx = assigned_lines[0] if assigned_lines else 0
    current_words = []

    for i, raw_word in enumerate(ylt_raw_tokens):
        line_idx = assigned_lines[i]
        if line_idx != current_line_idx:
            # Emit current line
            output_lines.append(' '.join(current_words))
            # Fill any skipped lines with empty strings
            for gap in range(current_line_idx + 1, line_idx):
                output_lines.append('')
            current_line_idx = line_idx
            current_words = [raw_word]
        else:
            current_words.append(raw_word)

    # Emit final line
    if current_words:
        output_lines.append(' '.join(current_words))

    # Pad to match Greek line count if needed
    while len(output_lines) < num_lines:
        output_lines.append('')

    return output_lines


# ---------------------------------------------------------------------------
# Main test driver
# ---------------------------------------------------------------------------

def load_greek_chapter(slug, chapter):
    """Load Greek colometric lines, preferring v4-editorial over v3-colometric."""
    ch_str = f"{chapter:02d}"
    v4_path = V4_DIR / f"{slug}-{ch_str}.txt"
    v3_path = V3_DIR / f"{slug}-{ch_str}.txt"

    if v4_path.exists():
        print(f"  Using v4-editorial: {v4_path.name}")
        return parse_greek_chapter(v4_path)
    elif v3_path.exists():
        print(f"  Using v3-colometric: {v3_path.name}")
        return parse_greek_chapter(v3_path)
    else:
        print(f"  ERROR: No colometric file found for {slug} ch {chapter}", file=sys.stderr)
        return {}


def run_test(slug, chapter, verses=None):
    """Run LCS alignment test on a chapter."""
    booknum = SLUG_TO_BOOKNUM[slug]

    print(f"\n{'='*60}")
    print(f"LCS Alignment Test: {slug.upper()} {chapter}")
    print(f"{'='*60}")

    # Load Greek colometric data
    greek_verses = load_greek_chapter(slug, chapter)
    if not greek_verses:
        print("  No Greek data loaded.")
        return

    # Load Macula data
    macula_data = load_macula_book(slug)
    if not macula_data:
        print("  No Macula data loaded.")
        return

    # Load YLT data
    ylt_book = ensure_ylt_data(booknum)
    if chapter not in ylt_book:
        print(f"  No YLT data for chapter {chapter}.")
        return
    ylt_verses = ylt_book[chapter]

    # Determine which verses to test
    if verses:
        test_verses = verses
    else:
        test_verses = sorted(greek_verses.keys())

    problems = []

    for v in test_verses:
        if v not in greek_verses:
            print(f"\n  Verse {v} not in Greek data, skipping.")
            continue
        if v not in ylt_verses:
            print(f"\n  Verse {v} not in YLT data, skipping.")
            continue
        if (chapter, v) not in macula_data:
            print(f"\n  Verse {v} not in Macula data, skipping.")
            continue

        gk_lines = greek_verses[v]
        mw = macula_data[(chapter, v)]
        ylt_text = ylt_verses[v]

        en_lines = split_ylt_by_lcs(gk_lines, mw, ylt_text)

        print(f"\n=== {slug.capitalize()} {chapter}:{v} ===")
        if en_lines is None:
            print("  ALIGNMENT FAILED")
            problems.append((v, "alignment failed"))
            continue

        # Print side-by-side
        max_lines = max(len(gk_lines), len(en_lines))
        for i in range(max_lines):
            gk = gk_lines[i] if i < len(gk_lines) else ""
            en = en_lines[i] if i < len(en_lines) else ""
            print(f"  GK: {gk}")
            print(f"  EN: {en}")

        # Check for issues
        if len(en_lines) != len(gk_lines):
            problems.append((v, f"line count mismatch: {len(en_lines)} EN vs {len(gk_lines)} GK"))

        # Check for empty EN lines (might indicate alignment issues)
        for i, line in enumerate(en_lines):
            if not line.strip() and i < len(gk_lines) and gk_lines[i].strip():
                problems.append((v, f"empty EN line {i+1} but GK has content"))

    if problems:
        print(f"\n{'='*60}")
        print("PROBLEMS FOUND:")
        for v, issue in problems:
            print(f"  Verse {v}: {issue}")
    else:
        print(f"\n{'='*60}")
        print("No problems detected.")

    return problems


def main():
    parser = argparse.ArgumentParser(description="LCS-based YLT alignment test")
    parser.add_argument("--book", required=True, help="Book slug (e.g., mark)")
    parser.add_argument("--chapter", required=True, type=int, help="Chapter number")
    parser.add_argument("--verses", help="Comma-separated verse numbers (default: all)")
    args = parser.parse_args()

    if args.book not in SLUG_TO_BOOKNUM:
        print(f"Unknown book: {args.book}", file=sys.stderr)
        sys.exit(1)

    verses = None
    if args.verses:
        verses = [int(v.strip()) for v in args.verses.split(',')]

    run_test(args.book, args.chapter, verses)


if __name__ == "__main__":
    main()
