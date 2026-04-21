"""
check_cascade_alignment.py — post-cascade misalignment warning checker.

Scans data/text-files/eng-gloss/ against v4-editorial/ for mechanical
signatures of misalignment. Flags candidates for manual review.
Does NOT modify any file.

Usage:
    py -3 scripts/check_cascade_alignment.py                    # all books
    py -3 scripts/check_cascade_alignment.py --book matt        # one book
    py -3 scripts/check_cascade_alignment.py --book matt --chapter 4
    py -3 scripts/check_cascade_alignment.py --output /tmp/warnings.md
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_V4_ROOT = _REPO_ROOT / "data" / "text-files" / "v4-editorial"
_ENG_ROOT = _REPO_ROOT / "data" / "text-files" / "eng-gloss"

# ---------------------------------------------------------------------------
# Heuristic helpers
# ---------------------------------------------------------------------------

# Pattern: sentence-terminating punctuation followed by a continuation word.
# Captures constructions like ". And", "? But", "; Then", etc.
_SENT_MID = re.compile(
    r'[.?;]\s+(And|But|Then|Therefore|Yes|No)\b',
    re.IGNORECASE,
)

# Greek continuation markers that legitimately start a line
_GK_CONTINUATION = re.compile(r'^(καί|καὶ|δέ|δὲ|ἀλλά|ἀλλὰ|γάρ|γὰρ|οὖν|τότε|ὅτι)')

# English lowercase CONJUNCTION starters only (not articles/prepositions)
# Case-sensitive: lowercase "and/but/or" is the signal; uppercase "And/But" at
# verse-start or after speech-intro is expected.
_ENG_CONJ_LOWERCASE = re.compile(r'^(and|but|or)\b')

# Greek full-stop only (period, not ano teleia which is ≈ colon/semicolon)
# Use only for the most unambiguous mismatch cases.
_GK_FULL_STOP = re.compile(r'\.$')

# English full-stop terminal
_ENG_FULL_STOP = re.compile(r'[.?!]$')

# Greek line ending in a bare word (no punctuation at all) — mid-clause continuation
_GK_BARE_END = re.compile(r'[^\W·:.,;?!\s]$', re.UNICODE)


def _word_count(line: str) -> int:
    """Count whitespace-delimited tokens (strips punctuation from count boundary)."""
    return len(line.split())


def has_sentence_end_mid_line(eng_line: str) -> bool:
    """Detect a sentence terminator followed by a continuation word on the same line."""
    return bool(_SENT_MID.search(eng_line))


def has_word_count_imbalance(g_line: str, e_line: str) -> tuple[bool, str]:
    """
    Return (flagged, reason_string).
    Flags if English is >3x+2 Greek words (too long) or <Greek/4 (too short).
    """
    g_len = _word_count(g_line)
    e_len = _word_count(e_line)
    if e_len > 3 * g_len + 2:
        return True, f"eng {e_len}w >> gk {g_len}w"
    if g_len > 0 and e_len < g_len / 4:
        return True, f"eng {e_len}w << gk {g_len}w"
    return False, ""


def has_punct_mismatch(g_line: str, e_line: str) -> bool:
    """
    Flag only high-signal asymmetries to avoid ·/:/ ; false positives.

    The Greek ano teleia (·) maps to English colon or semicolon — NOT a mismatch.
    The Greek comma maps to English comma — NOT a mismatch.

    We flag:
    1. English ends with a full stop/question/exclamation mark but Greek ends
       with a bare word (no punct) — English over-closes a continuing clause.
    2. Greek ends with a period (full stop) but English doesn't end with any
       sentence-terminal — unusual enough to flag.
    """
    gk_bare = bool(_GK_BARE_END.search(g_line.rstrip()))
    eng_strong = bool(_ENG_FULL_STOP.search(e_line))
    gk_full_stop = bool(_GK_FULL_STOP.search(g_line))

    if eng_strong and gk_bare:
        return True
    if gk_full_stop and not eng_strong:
        return True
    return False


def has_orphan_start(g_line: str, e_line: str) -> bool:
    """
    Flag if English starts with a lowercase continuation word (and/or/but/the…)
    but the Greek line starts with an UPPERCASE letter (indicating an independent
    clause / sentence start, not a continuation).

    This catches content that leaked from the previous line onto this one,
    producing misaligned continuation phrasing under an independent-clause Greek line.
    """
    eng_stripped = e_line.strip()
    gk_stripped = g_line.strip()
    if not eng_stripped or not gk_stripped:
        return False
    # Lowercase "and/but/or" at line start — strict conjunction check
    eng_cont = bool(_ENG_CONJ_LOWERCASE.match(eng_stripped))
    if not eng_cont:
        return False
    # Greek starts with uppercase → independent clause; lowercase-conjunction English
    # here may indicate content that leaked from the prior line.
    if not gk_stripped[0].isupper():
        return False
    # Exception: Greek has a second-position postpositive (δέ, δὲ, γάρ, γὰρ, μέν, μὲν)
    # which IS a continuation marker even though the line starts uppercase.
    gk_tokens = gk_stripped.split()
    if len(gk_tokens) >= 2 and gk_tokens[1] in ("δέ", "δὲ", "γάρ", "γὰρ", "μέν", "μὲν", "οὖν"):
        return False
    return True


# ---------------------------------------------------------------------------
# Verse parser
# ---------------------------------------------------------------------------

_VERSE_REF = re.compile(r'^\d+:\d+$')


def _parse_verses(text: str) -> list[tuple[str, list[str]]]:
    """
    Parse a chapter file into [(verse_ref, [lines]), ...].
    Verse reference lines (e.g. "4:1") act as section headers.
    Empty lines between verses are discarded.
    """
    verses: list[tuple[str, list[str]]] = []
    current_ref: str | None = None
    current_lines: list[str] = []

    for raw in text.splitlines():
        line = raw.strip()
        if _VERSE_REF.match(line):
            if current_ref is not None:
                verses.append((current_ref, current_lines))
            current_ref = line
            current_lines = []
        elif line == "":
            continue
        else:
            if current_ref is not None:
                current_lines.append(line)

    if current_ref is not None:
        verses.append((current_ref, current_lines))

    return verses


# ---------------------------------------------------------------------------
# Warning dataclass
# ---------------------------------------------------------------------------

@dataclass
class Warning:
    heuristic: str          # "sentence-end-mid-line" | "word-count-imbalance" | etc.
    book: str
    chapter: int
    verse: str              # "4:3" style
    line_idx: int           # 1-based index within the verse
    greek_line: str
    eng_line: str
    detail: str             # human-readable explanation


# ---------------------------------------------------------------------------
# Core checker
# ---------------------------------------------------------------------------

def check_verse(
    book: str,
    chapter: int,
    verse_ref: str,
    greek_lines: list[str],
    english_lines: list[str],
) -> list[Warning]:
    warnings: list[Warning] = []

    # Line-count mismatch: only per-line checks are meaningful when counts match.
    # Still run sentence-end check on all English lines regardless.
    for idx, e_line in enumerate(english_lines, start=1):
        if has_sentence_end_mid_line(e_line):
            warnings.append(Warning(
                heuristic="sentence-end-mid-line",
                book=book,
                chapter=chapter,
                verse=verse_ref,
                line_idx=idx,
                greek_line=greek_lines[idx - 1] if idx - 1 < len(greek_lines) else "",
                eng_line=e_line,
                detail=f'sentence-terminal followed by continuation word: "{e_line}"',
            ))

    # Per-paired-line checks (only when counts match)
    if len(greek_lines) == len(english_lines):
        for idx, (g_line, e_line) in enumerate(zip(greek_lines, english_lines), start=1):
            flagged, reason = has_word_count_imbalance(g_line, e_line)
            if flagged:
                warnings.append(Warning(
                    heuristic="word-count-imbalance",
                    book=book,
                    chapter=chapter,
                    verse=verse_ref,
                    line_idx=idx,
                    greek_line=g_line,
                    eng_line=e_line,
                    detail=reason,
                ))

            if has_punct_mismatch(g_line, e_line):
                warnings.append(Warning(
                    heuristic="punctuation-mismatch",
                    book=book,
                    chapter=chapter,
                    verse=verse_ref,
                    line_idx=idx,
                    greek_line=g_line,
                    eng_line=e_line,
                    detail=f'gk ends "{g_line[-1] if g_line else ""}" / eng ends "{e_line[-1] if e_line else ""}"',
                ))

            if has_orphan_start(g_line, e_line):
                warnings.append(Warning(
                    heuristic="orphan-start",
                    book=book,
                    chapter=chapter,
                    verse=verse_ref,
                    line_idx=idx,
                    greek_line=g_line,
                    eng_line=e_line,
                    detail=f'English starts with continuation word but Greek does not: "{e_line[:40]}"',
                ))
    else:
        # Line-count mismatch is itself a structural flag
        if greek_lines or english_lines:
            warnings.append(Warning(
                heuristic="line-count-mismatch",
                book=book,
                chapter=chapter,
                verse=verse_ref,
                line_idx=0,
                greek_line=" | ".join(greek_lines),
                eng_line=" | ".join(english_lines),
                detail=f"Greek has {len(greek_lines)} lines, English has {len(english_lines)} lines",
            ))

    return warnings


def check_book_chapter(book: str, gk_path: Path, eng_path: Path) -> list[Warning]:
    """Check one chapter file pair; return all warnings."""
    if not gk_path.exists():
        print(f"  SKIP (missing Greek): {gk_path}", file=sys.stderr)
        return []
    if not eng_path.exists():
        print(f"  SKIP (missing English): {eng_path}", file=sys.stderr)
        return []

    gk_text = gk_path.read_text(encoding="utf-8")
    eng_text = eng_path.read_text(encoding="utf-8")

    # Extract chapter number from filename, e.g. "matt-04.txt" → 4
    stem = gk_path.stem  # "matt-04"
    parts = stem.rsplit("-", 1)
    try:
        chapter_num = int(parts[-1])
    except ValueError:
        chapter_num = 0

    gk_verses = dict(_parse_verses(gk_text))
    eng_verses = dict(_parse_verses(eng_text))

    all_refs = sorted(set(gk_verses) | set(eng_verses),
                      key=lambda r: int(r.split(":")[1]))

    warnings: list[Warning] = []
    for ref in all_refs:
        gk_lines = gk_verses.get(ref, [])
        eng_lines = eng_verses.get(ref, [])
        warnings.extend(check_verse(book, chapter_num, ref, gk_lines, eng_lines))

    return warnings


# ---------------------------------------------------------------------------
# Book/chapter discovery
# ---------------------------------------------------------------------------

def _book_dir_name(book: str) -> str | None:
    """Match a short book name (e.g. 'matt') to a directory like '01-matt'."""
    for d in _V4_ROOT.iterdir():
        if d.is_dir() and d.name.endswith(f"-{book}"):
            return d.name
    return None


def _collect_chapter_pairs(
    book_filter: str | None,
    chapter_filter: int | None,
) -> list[tuple[str, Path, Path]]:
    """
    Return list of (book_short, gk_path, eng_path) for all matching chapters.
    """
    pairs: list[tuple[str, Path, Path]] = []

    if book_filter:
        dir_name = _book_dir_name(book_filter)
        if dir_name is None:
            print(f"ERROR: no directory found for book '{book_filter}'", file=sys.stderr)
            sys.exit(1)
        book_dirs = [(_V4_ROOT / dir_name, _ENG_ROOT / dir_name, book_filter)]
    else:
        book_dirs = []
        for d in sorted(_V4_ROOT.iterdir()):
            if d.is_dir():
                short = d.name.split("-", 1)[1]  # "01-matt" → "matt"
                book_dirs.append((d, _ENG_ROOT / d.name, short))

    for gk_book_dir, eng_book_dir, book_short in book_dirs:
        for gk_file in sorted(gk_book_dir.glob("*.txt")):
            stem = gk_file.stem  # e.g. "matt-04"
            parts = stem.rsplit("-", 1)
            try:
                ch = int(parts[-1])
            except ValueError:
                continue

            if chapter_filter is not None and ch != chapter_filter:
                continue

            eng_file = eng_book_dir / gk_file.name
            pairs.append((book_short, gk_file, eng_file))

    return pairs


# ---------------------------------------------------------------------------
# Report formatter
# ---------------------------------------------------------------------------

HEURISTIC_ORDER = [
    "sentence-end-mid-line",
    "word-count-imbalance",
    "punctuation-mismatch",
    "orphan-start",
    "line-count-mismatch",
]

HEURISTIC_LABELS = {
    "sentence-end-mid-line":  "1. Sentence-end-mid-line",
    "word-count-imbalance":   "2. Word-count imbalance",
    "punctuation-mismatch":   "3. Punctuation mismatch",
    "orphan-start":           "4. Orphan-start",
    "line-count-mismatch":    "5. Line-count mismatch",
}


def _format_report(warnings: list[Warning]) -> str:
    by_heuristic: dict[str, list[Warning]] = {h: [] for h in HEURISTIC_ORDER}
    for w in warnings:
        by_heuristic.setdefault(w.heuristic, []).append(w)

    verses_flagged = len({(w.book, w.chapter, w.verse) for w in warnings})
    lines: list[str] = ["# Cascade Alignment Warnings", ""]

    for key in HEURISTIC_ORDER:
        group = by_heuristic.get(key, [])
        label = HEURISTIC_LABELS.get(key, key)
        lines.append(f"## {label} ({len(group)} flags)")
        lines.append("")
        if not group:
            lines.append("_(none)_")
        else:
            for w in group:
                ref = f"{w.book.capitalize()} {w.verse}"
                line_tag = f"line {w.line_idx}" if w.line_idx else "line-count"
                lines.append(f"- {ref} {line_tag} — {w.detail}")
                if w.greek_line:
                    lines.append(f"  - GK: `{w.greek_line}`")
                if w.eng_line:
                    lines.append(f"  - EN: `{w.eng_line}`")
        lines.append("")

    lines.append(f"Total: {len(warnings)} warnings across {verses_flagged} verses.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Post-cascade misalignment warning checker. Read-only."
    )
    parser.add_argument("--book", metavar="BOOK",
                        help="Short book name, e.g. matt, mark, john")
    parser.add_argument("--chapter", metavar="N", type=int,
                        help="Chapter number (requires --book)")
    parser.add_argument("--output", metavar="FILE",
                        help="Write markdown report to FILE (default: stdout)")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    pairs = _collect_chapter_pairs(args.book, args.chapter)
    if not pairs:
        print("No chapter files matched.", file=sys.stderr)
        sys.exit(1)

    all_warnings: list[Warning] = []
    for book_short, gk_path, eng_path in pairs:
        chapter_warnings = check_book_chapter(book_short, gk_path, eng_path)
        all_warnings.extend(chapter_warnings)

    report = _format_report(all_warnings)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
        # Summary to stdout
        verses_flagged = len({(w.book, w.chapter, w.verse) for w in all_warnings})
        print(f"{len(all_warnings)} warnings across {verses_flagged} verses.")
    else:
        print(report)


if __name__ == "__main__":
    main()
