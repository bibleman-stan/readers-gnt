"""
diagnostic_scanner.py — Colometric diagnostic scanner.

Tests every content line of a v3 colometric chapter against the framework's
forces:

  1. Atomic thought — does the line contain a verbal element, and if it
     has a finite verb, are its core arguments on the same line?
  2. Single image  — does the line have 2+ finite verbs (over-merge)?

(A prior breath-unit test based on syllable count was removed 2026-04-26
following the canon-wide purge of the retired Breath criterion. See
canon §10 entry "2026-04-20 (later³) — H3: Breath Criterion Retired".)

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/archive/diagnostic_scanner.py --chapter mark-04
    PYTHONIOENCODING=utf-8 py -3 scripts/archive/diagnostic_scanner.py --all-mark
    PYTHONIOENCODING=utf-8 py -3 scripts/archive/diagnostic_scanner.py --book mark
"""

import argparse
import os
import re
import sys

# ---------------------------------------------------------------------------
# Setup imports from sibling modules
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
sys.path.insert(0, _SCRIPT_DIR)

from morphgnt_lookup import (
    line_has_verbal_element,
    line_has_finite_verb,
    _load_book as morphgnt_load_book,
    _verse_cache as morphgnt_verse_cache,
)
from macula_valency import (
    check_line_valency,
    check_stranded_finite_verb,
)

# ---------------------------------------------------------------------------
# Finite verb counting (uses morphgnt verse data)
# ---------------------------------------------------------------------------

def count_finite_verbs_on_line(line_text, book_slug):
    """Count the number of distinct finite verbs on a line.

    Returns (count, list_of_verb_forms).
    """
    if book_slug not in morphgnt_verse_cache:
        morphgnt_load_book(book_slug)
    verses = morphgnt_verse_cache.get(book_slug, {})

    # Collect cleaned words on the line
    line_words = []
    for w in line_text.strip().split():
        clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅\u0387\u00B7]', '', w)
        if clean:
            line_words.append(clean)

    if not line_words:
        return 0, []

    # Build a set of finite verb forms that appear in this book
    # Map: cleaned_word -> set of moods
    word_moods = {}
    for (ch, vs), word_list in verses.items():
        for word, pos, parsing in word_list:
            if not pos.startswith('V'):
                continue
            if len(parsing) >= 4 and parsing[3] in ('I', 'S', 'D', 'O'):
                clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅\u0387\u00B7]', '', word)
                if clean:
                    if clean not in word_moods:
                        word_moods[clean] = set()
                    word_moods[clean].add(parsing[3])

    # Count finite verbs on this line
    found = []
    for w in line_words:
        if w in word_moods:
            found.append(w)

    return len(found), found


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------

_V3_DIR = os.path.join(_REPO_ROOT, "data", "text-files", "v3-colometric")

# Book slug -> chapter count (for --book and --all-mark)
_BOOK_CHAPTERS = {
    "matt": 28, "mark": 16, "luke": 24, "john": 21,
    "acts": 28, "rom": 16, "1cor": 16, "2cor": 13,
    "gal": 6, "eph": 6, "phil": 4, "col": 4,
    "1thess": 5, "2thess": 3, "1tim": 6, "2tim": 4,
    "titus": 3, "phlm": 1, "heb": 13, "jas": 5,
    "1pet": 5, "2pet": 3, "1john": 5, "2john": 1,
    "3john": 1, "jude": 1, "rev": 22,
}

_VERSE_REF_RE = re.compile(r'^(\d+):(\d+)$')


def parse_colometric_file(filepath):
    """Parse a v3 colometric file into (verse_ref, content_lines) groups.

    Yields: (chapter_num, verse_num, [line1, line2, ...])
    """
    current_chapter = None
    current_verse = None
    content_lines = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n').rstrip('\r')

            # Check for verse reference
            m = _VERSE_REF_RE.match(line.strip())
            if m:
                # Yield previous verse's lines
                if current_chapter is not None and content_lines:
                    yield (current_chapter, current_verse, content_lines)
                current_chapter = int(m.group(1))
                current_verse = int(m.group(2))
                content_lines = []
                continue

            # Skip blank lines
            if not line.strip():
                continue

            # Content line
            content_lines.append(line)

    # Yield final verse
    if current_chapter is not None and content_lines:
        yield (current_chapter, current_verse, content_lines)


# ---------------------------------------------------------------------------
# Violation types
# ---------------------------------------------------------------------------

FLAG_NO_VERBAL     = "NO_VERBAL"       # no verbal element at all
FLAG_MULTI_FINITE  = "MULTI_FINITE"    # 2+ finite verbs (over-merge)
FLAG_STRANDED_VERB = "STRANDED_VERB"   # finite verb separated from arguments
FLAG_UNSAT_VALENCY = "UNSAT_VALENCY"   # participle valency unsatisfied


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_chapter(filepath, book_slug):
    """Scan a single chapter file. Returns list of diagnostic results."""
    results = []

    # Collect all lines with context (for stranded verb prev/next)
    all_entries = []  # [(chapter, verse, line_text), ...]
    for ch, vs, lines in parse_colometric_file(filepath):
        for line in lines:
            all_entries.append((ch, vs, line))

    for idx, (ch, vs, line_text) in enumerate(all_entries):
        flags = []
        details = {}

        # --- Test 1a: Verbal element ---
        has_verbal = line_has_verbal_element(line_text, book_slug)
        has_finite = line_has_finite_verb(line_text, book_slug)

        if not has_verbal:
            flags.append(FLAG_NO_VERBAL)

        # --- Test 1b: Valency (participle missing arguments) ---
        if has_verbal:
            val_result = check_line_valency(line_text, book_slug, ch, vs)
            if val_result.unsatisfied:
                flags.append(FLAG_UNSAT_VALENCY)
                details['valency'] = val_result.reason

        # --- Test 1c: Stranded finite verb ---
        if has_finite:
            prev_line = all_entries[idx - 1][2] if idx > 0 else ""
            next_line = all_entries[idx + 1][2] if idx < len(all_entries) - 1 else ""
            strand_result = check_stranded_finite_verb(
                line_text, prev_line, next_line, book_slug, ch, vs
            )
            if strand_result.stranded:
                flags.append(FLAG_STRANDED_VERB)
                details['stranded'] = strand_result.reason

        # --- Test 2: Multiple finite verbs (over-merge) ---
        fv_count, fv_forms = count_finite_verbs_on_line(line_text, book_slug)
        if fv_count >= 2:
            flags.append(FLAG_MULTI_FINITE)
            details['finite_verbs'] = fv_forms

        results.append({
            'chapter': ch,
            'verse': vs,
            'text': line_text,
            'flags': flags,
            'details': details,
        })

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(results, label=""):
    """Print a per-line diagnostic report and summary."""
    if label:
        print(f"\n{'='*70}")
        print(f"  DIAGNOSTIC SCAN: {label}")
        print(f"{'='*70}\n")

    total_lines = len(results)
    flagged_lines = 0
    violation_counts = {}

    for r in results:
        if r['flags']:
            flagged_lines += 1
            # Print flagged line
            ref = f"{r['chapter']}:{r['verse']}"
            syl = r['details'].get('syllables', '?')
            print(f"  {ref:<8} [{syl:>2} syl]  {r['text']}")
            for flag in r['flags']:
                violation_counts[flag] = violation_counts.get(flag, 0) + 1
                extra = ""
                if flag == FLAG_MULTI_FINITE:
                    verbs = r['details'].get('finite_verbs', [])
                    extra = f"  verbs: {', '.join(verbs)}"
                elif flag == FLAG_UNSAT_VALENCY:
                    extra = f"  {r['details'].get('valency', '')}"
                elif flag == FLAG_STRANDED_VERB:
                    extra = f"  {r['details'].get('stranded', '')}"
                print(f"           -> {flag}{extra}")
            print()

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total content lines:    {total_lines}")
    print(f"  Lines with violations:  {flagged_lines}")
    pct = (flagged_lines / total_lines * 100) if total_lines else 0
    print(f"  Violation rate:         {pct:.1f}%")
    print()
    print(f"  Violation breakdown:")
    for flag in [FLAG_NO_VERBAL, FLAG_MULTI_FINITE,
                 FLAG_STRANDED_VERB, FLAG_UNSAT_VALENCY]:
        count = violation_counts.get(flag, 0)
        if count:
            print(f"    {flag:<20} {count:>4}")
    print()

    return total_lines, flagged_lines, violation_counts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def resolve_chapters(args):
    """Resolve CLI arguments into a list of (filepath, book_slug, label) tuples."""
    chapters = []

    if args.chapter:
        # e.g., "mark-04"
        slug_ch = args.chapter
        parts = slug_ch.rsplit('-', 1)
        if len(parts) != 2:
            print(f"Error: --chapter must be in format 'book-NN', got '{slug_ch}'",
                  file=sys.stderr)
            sys.exit(1)
        book_slug = parts[0]
        ch_str = parts[1]
        filepath = os.path.join(_V3_DIR, f"{slug_ch}.txt")
        if not os.path.exists(filepath):
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        chapters.append((filepath, book_slug, f"{book_slug.title()} {int(ch_str)}"))

    elif args.all_mark:
        book_slug = "mark"
        for ch in range(1, _BOOK_CHAPTERS["mark"] + 1):
            fname = f"mark-{ch:02d}.txt"
            filepath = os.path.join(_V3_DIR, fname)
            if os.path.exists(filepath):
                chapters.append((filepath, book_slug, f"Mark {ch}"))

    elif args.book:
        book_slug = args.book.lower()
        num_chapters = _BOOK_CHAPTERS.get(book_slug)
        if not num_chapters:
            print(f"Error: unknown book slug '{book_slug}'", file=sys.stderr)
            sys.exit(1)
        for ch in range(1, num_chapters + 1):
            fname = f"{book_slug}-{ch:02d}.txt"
            filepath = os.path.join(_V3_DIR, fname)
            if os.path.exists(filepath):
                chapters.append((filepath, book_slug, f"{book_slug.title()} {ch}"))

    else:
        print("Error: specify --chapter, --all-mark, or --book", file=sys.stderr)
        sys.exit(1)

    return chapters


def main():
    parser = argparse.ArgumentParser(
        description="Colometric diagnostic scanner — tests lines against three criteria"
    )
    parser.add_argument('--chapter', type=str,
                        help='Single chapter to scan, e.g. mark-04')
    parser.add_argument('--all-mark', action='store_true',
                        help='Scan all chapters of Mark')
    parser.add_argument('--book', type=str,
                        help='Scan all chapters of a book, e.g. mark')
    args = parser.parse_args()

    chapters = resolve_chapters(args)

    grand_total = 0
    grand_flagged = 0
    grand_violations = {}

    for filepath, book_slug, label in chapters:
        results = scan_chapter(filepath, book_slug)
        total, flagged, violations = print_report(results, label=label)
        grand_total += total
        grand_flagged += flagged
        for k, v in violations.items():
            grand_violations[k] = grand_violations.get(k, 0) + v

    # Grand summary if multiple chapters
    if len(chapters) > 1:
        print(f"\n{'='*70}")
        print(f"  GRAND TOTAL ({len(chapters)} chapters)")
        print(f"{'='*70}")
        print(f"  Total content lines:    {grand_total}")
        print(f"  Lines with violations:  {grand_flagged}")
        pct = (grand_flagged / grand_total * 100) if grand_total else 0
        print(f"  Violation rate:         {pct:.1f}%")
        print()
        print(f"  Violation breakdown:")
        for flag in [FLAG_NO_VERBAL, FLAG_MULTI_FINITE,
                     FLAG_STRANDED_VERB, FLAG_UNSAT_VALENCY]:
            count = grand_violations.get(flag, 0)
            if count:
                print(f"    {flag:<20} {count:>4}")
        print()


if __name__ == '__main__':
    main()
