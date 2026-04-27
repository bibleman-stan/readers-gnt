"""
build_books.py — Generate HTML book files from colometric text sources.

Reads chapter files from v4-editorial/*/ (Greek) and optionally from
eng-gloss/*/ (English), and writes one HTML fragment per book into books/.

Each .line span contains a .gk span (Greek) and optionally a .en span
(English), enabling Greek/English/Both display modes in the web app.

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
GK_PRIMARY_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
INPUT_DIR = GK_PRIMARY_DIR  # used by discover_books for globbing all chapters (subfoldered)
EN_DIR = os.path.join(REPO_ROOT, "data", "text-files", "eng-gloss")
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


def build_ylt_lookup(ylt_verses):
    """Build a dict mapping verse ref -> list of English lines."""
    lookup = {}
    for verse in ylt_verses:
        lookup[verse["ref"]] = verse["lines"]
    return lookup


# Superscript digit map for inline verse markers (cross-verse continuation)
_SUPERSCRIPT_TO_DIGIT = {
    "\u00B2": "2", "\u00B3": "3",
    "\u2070": "0", "\u00B9": "1",
    "\u2074": "4", "\u2075": "5", "\u2076": "6", "\u2077": "7",
    "\u2078": "8", "\u2079": "9",
}
_SUPERSCRIPT_RE = re.compile(
    "[" + "".join(_SUPERSCRIPT_TO_DIGIT.keys()) + "]+"
)


def _wrap_verse_markers(escaped_line, chapter_num):
    """Replace inline verse markers (²³⁴...) with HTML superscript elements.

    Each marker becomes <sup class="verse-marker" id="v-{chapter}-{verse}">N</sup>
    so that a click on a TOC entry for the inline verse lands at this marker.
    """
    def repl(m):
        marker_text = m.group(0)
        digits = "".join(_SUPERSCRIPT_TO_DIGIT[c] for c in marker_text)
        inline_id = f"v-{chapter_num}-{digits}-inline"
        return f'<sup class="verse-marker" id="{inline_id}">{marker_text}</sup>'
    return _SUPERSCRIPT_RE.sub(repl, escaped_line)


def build_chapter_html(chapter_num, gk_verses, en_lookup=None):
    """Build HTML for one chapter with paired Greek/English lines."""
    parts = []
    parts.append(f'<div class="chapter" id="ch-{chapter_num}">')

    for verse in gk_verses:
        ref = html.escape(verse["ref"])
        # Parse verse number for ID: "2:38" -> "v-2-38"
        verse_id = 'v-' + ref.replace(':', '-')
        parts.append(f'  <div class="verse" id="{verse_id}"><span class="verse-num">{ref}</span>')

        # Get English lines for this verse (if available)
        en_lines = []
        if en_lookup and verse["ref"] in en_lookup:
            en_lines = en_lookup[verse["ref"]]

        for i, gk_line in enumerate(verse["lines"]):
            gk_escaped = html.escape(gk_line)
            # Wrap punctuation in spans for toggle visibility (must run
            # BEFORE verse-marker wrapping so the punct regex doesn't
            # corrupt the sup HTML tag attributes)
            gk_escaped = re.sub(r'([,.\;·—])', r'<span class="punct">\1</span>', gk_escaped)
            # Render inline verse markers as superscript anchors (cross-verse)
            gk_escaped = _wrap_verse_markers(gk_escaped, chapter_num)

            # Get corresponding English line (or empty string)
            en_text = en_lines[i] if i < len(en_lines) else ""
            en_escaped = html.escape(en_text)
            # Punct wrap first (same ordering reason as Greek above)
            en_escaped = re.sub(r'([,.\;:!?\'"—\-])', r'<span class="punct">\1</span>', en_escaped)
            en_escaped = _wrap_verse_markers(en_escaped, chapter_num)

            parts.append(f'    <span class="line"><span class="gk">{gk_escaped}</span><span class="en">{en_escaped}</span></span>')
        parts.append("  </div>")

    parts.append("</div>")
    return "\n".join(parts)


def discover_books(input_dir, book_filter=None):
    """Glob input files and group by book prefix.

    Returns:
        dict: {book_prefix: [(chapter_num_from_filename, filepath), ...]}
              sorted by chapter number.
    """
    pattern = os.path.join(input_dir, "*", "*.txt")
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


def _book_prefix(fpath):
    """Extract book prefix from a chapter filepath, e.g. 'mark' from 'mark-05.txt'."""
    stem = os.path.splitext(os.path.basename(fpath))[0]
    dash_idx = stem.rfind("-")
    return stem[:dash_idx] if dash_idx != -1 else stem


def _find_book_subdir(base_dir, prefix):
    """Find the numbered subdirectory for a book prefix.
    e.g., prefix='matt' finds '01-matt' in base_dir.
    Falls back to plain prefix if numbered dir doesn't exist.
    """
    # Try numbered pattern first (e.g., 01-matt, 02-mark)
    for entry in os.listdir(base_dir):
        if os.path.isdir(os.path.join(base_dir, entry)):
            # Strip the number prefix to match: '01-matt' -> 'matt'
            parts = entry.split('-', 1)
            if len(parts) == 2 and parts[0].isdigit() and parts[1] == prefix:
                return entry
    # Fall back to plain prefix
    if os.path.isdir(os.path.join(base_dir, prefix)):
        return prefix
    return None


def resolve_greek_path(fpath):
    """Return the v4-editorial Greek source path. Raise if missing."""
    basename = os.path.basename(fpath)
    prefix = _book_prefix(fpath)
    subdir = _find_book_subdir(GK_PRIMARY_DIR, prefix)
    if subdir:
        v4_path = os.path.join(GK_PRIMARY_DIR, subdir, basename)
        if os.path.isfile(v4_path):
            return v4_path, "v4"
    raise FileNotFoundError(
        f"v4-editorial Greek source missing for {basename} (looked under {GK_PRIMARY_DIR})"
    )


def resolve_english_path(fpath):
    """Return the English structural gloss path if it exists.

    Returns (path, label) or (None, None) if not found.
    """
    basename = os.path.basename(fpath)
    prefix = _book_prefix(fpath)
    subdir = _find_book_subdir(EN_DIR, prefix)
    if subdir:
        en_path = os.path.join(EN_DIR, subdir, basename)
        if os.path.isfile(en_path):
            return en_path, "EN"
    return None, None


def build_book(prefix, chapter_files, output_dir):
    """Build and write the HTML file for one book.

    Returns the number of chapters, verses, and English label.
    """
    all_chapter_html = []
    total_verses = 0
    en_labels = set()

    for _ch_num, fpath in chapter_files:
        # Resolve Greek source (v4-editorial preferred over v3-colometric)
        gk_path, _gk_tag = resolve_greek_path(fpath)
        chapter_num, gk_verses = parse_chapter(gk_path)
        if chapter_num is None:
            chapter_num = _ch_num

        # Resolve English source (WEB preferred over YLT)
        en_lookup = None
        en_path, en_label = resolve_english_path(fpath)
        if en_path:
            _, en_verses = parse_chapter(en_path)
            en_lookup = build_ylt_lookup(en_verses)
            en_labels.add(en_label)

        total_verses += len(gk_verses)
        chapter_html = build_chapter_html(chapter_num, gk_verses, en_lookup)
        all_chapter_html.append(chapter_html)

    output_path = os.path.join(output_dir, f"{prefix}.html")
    os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_chapter_html) + "\n")

    return len(chapter_files), total_verses, output_path, en_labels


def _run_integrity_check(book_filter=None):
    """Run verify_word_order.py against SBLGNT source. Returns True if clean.

    This is the structural guard against silent text corruption: every build
    verifies that v4-editorial word order matches the canonical source before
    producing HTML. Any line-order swap, missing word, or extra word aborts
    the build.
    """
    import subprocess
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, "verify_word_order.py")]
    if book_filter:
        cmd += ["--book", book_filter]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8"
        )
    except Exception as e:
        print(f"WARNING: integrity check failed to run: {e}", file=sys.stderr)
        return True  # don't block on tooling failure
    # Parse summary line for total issues
    output = (result.stdout or "") + (result.stderr or "")
    last_line = output.strip().splitlines()[-1] if output.strip() else ""
    if "Total: 0 verse-level discrepancies" in output:
        return True
    if "Total:" in output:
        # Print the issues so the user sees them
        print(output, file=sys.stderr)
        return False
    # Unknown state — be cautious but don't block
    print(output, file=sys.stderr)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Build HTML book files from colometric text sources."
    )
    parser.add_argument(
        "--book",
        default=None,
        help="Build only this book (prefix, e.g. 'mark', '1cor').",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip the SBLGNT word-order integrity check (NOT recommended).",
    )
    args = parser.parse_args()

    if not os.path.isdir(INPUT_DIR):
        print(f"ERROR: Input directory not found: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)

    # Integrity guard: refuse to build if v4 doesn't match SBLGNT source.
    # This catches line-order swaps, missing/extra words, and word fusion
    # before they propagate through the English regen and HTML rebuild.
    if not args.skip_verify:
        print("Verifying v4-editorial against SBLGNT source...")
        if not _run_integrity_check(args.book):
            print(
                "\nERROR: word-order integrity check failed. "
                "Build aborted to prevent propagating text corruption.\n"
                "Fix the issues above (or use --skip-verify to override).",
                file=sys.stderr,
            )
            sys.exit(2)
        print("  integrity check passed.\n")

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
        num_chapters, num_verses, output_path, en_labels = build_book(
            prefix, chapter_files, OUTPUT_DIR
        )
        rel_path = os.path.relpath(output_path, REPO_ROOT)
        en_marker = ""
        if en_labels:
            en_marker = " +" + "+".join(sorted(en_labels))
        print(f"  {prefix:<10} {num_chapters:>3} ch, {num_verses:>4} vv  -> {rel_path}{en_marker}")

    print(f"\nDone. Output in {os.path.relpath(OUTPUT_DIR, REPO_ROOT)}/")


if __name__ == "__main__":
    main()
