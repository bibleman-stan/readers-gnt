"""
run_eflomal_alignment.py — Run eflomal bilingual alignment on v4-editorial
Greek verses paired with eng-gloss English verses.

Usage:
    py -3.12 scripts/run_eflomal_alignment.py --books matt mark luke --output data/alignment/gospels.json
    py -3.12 scripts/run_eflomal_alignment.py --all --output data/alignment/corpus-alignment.json

Output JSON shape:
    {
        "matt": {
            "1:1": [[gi, ei], [gi, ei], ...],
            "1:2": [...],
            ...
        },
        "mark": {...},
        ...
    }
    — gi is Greek token index, ei is English token index (both 0-based,
      after NFC-normalize + strip-punctuation + lowercase + whitespace-split).

Preprocessing:
  Greek: NFC normalize, strip Greek + ASCII punctuation, lowercase, whitespace split
  English: strip punctuation, lowercase, whitespace split

Requires:
  - Python 3.12 (per project toolchain — eflomal built against 3.12)
  - eflomal installed via `CC=gcc py -3.12 -m pip install eflomal`
  - v4-editorial + eng-gloss corpora present under data/text-files/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Optional

# Make validators.common importable (for v4-parsing helpers)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from validators.common import (  # noqa: E402
    BOOK_SLUGS,
    SLUG_TO_FILE_NUM,
    iter_v4_chapters,
    parse_chapter_file,
)

try:
    from eflomal import Aligner
except ImportError:
    sys.exit(
        "eflomal is not installed on this Python. "
        "Run: CC=gcc py -3.12 -m pip install eflomal"
    )

# Directory roots
_V4_ROOT = _REPO_ROOT / "data" / "text-files" / "v4-editorial"
_ENG_ROOT = _REPO_ROOT / "data" / "text-files" / "eng-gloss"

# Punctuation to strip from tokens before alignment.
# Greek-specific + ASCII + Unicode variants.
_PUNCT_CHARS = ''.join([
    '.', ',', ';', ':', '·', '?', '!',
    '(', ')', '[', ']', '{', '}',
    '—', '–', '-',
    '"', "'", '`',
    '\u02BC',  # modifier letter apostrophe
    '\u0387',  # Greek ano teleia
    '\u037E',  # Greek question mark
    '\u2014',  # em dash
    '\u2013',  # en dash
    '\u2018', '\u2019',  # left/right single quote
    '\u201C', '\u201D',  # left/right double quote
])
_PUNCT_RE = re.compile("[" + re.escape(_PUNCT_CHARS) + "]")
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str, *, greek: bool) -> str:
    """Normalize for alignment: NFC (Greek) → strip punct → lowercase → collapse ws."""
    if greek:
        text = unicodedata.normalize("NFC", text)
    text = _PUNCT_RE.sub(" ", text)
    text = text.lower()
    text = _WS_RE.sub(" ", text).strip()
    return text


def load_book_verses(book: str, root: Path) -> dict[tuple[int, int], str]:
    """Load all verses of a book from root (either _V4_ROOT or _ENG_ROOT).

    Returns {(chapter, verse): joined_text}. Joins all sense-lines for a verse
    into one string before tokenization (eflomal aligns verse-level, not line-level).
    """
    file_num = SLUG_TO_FILE_NUM.get(book)
    if not file_num:
        raise ValueError(f"Unknown book slug: {book}")

    # Find the book's directory (NN-slug format)
    target_dir: Optional[Path] = None
    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue
        parts = entry.name.split("-", 1)
        if len(parts) == 2 and parts[0].isdigit() and parts[1] == book:
            target_dir = entry
            break
        elif entry.name == book:
            target_dir = entry
            break
    if target_dir is None:
        raise FileNotFoundError(f"Book directory not found: {book} under {root}")

    result: dict[tuple[int, int], str] = {}
    for chapter_file in sorted(target_dir.iterdir()):
        if not chapter_file.name.endswith(".txt"):
            continue
        verses = parse_chapter_file(str(chapter_file))
        for v in verses:
            key = (v["ch"], v["vs"])
            # Join all sense-lines with a space; we align at verse level.
            joined = " ".join(v["lines"])
            result[key] = joined
    return result


def align_book(book: str) -> dict[str, list[list[int]]]:
    """Run eflomal alignment on one book's Greek ↔ English verses.

    Returns {"ch:vs": [[gi, ei], ...]} for every verse pair that exists in
    both corpora.
    """
    greek_verses = load_book_verses(book, _V4_ROOT)
    english_verses = load_book_verses(book, _ENG_ROOT)

    # Pair verses present in both; preserve verse-ref ordering.
    shared_keys = sorted(set(greek_verses.keys()) & set(english_verses.keys()))
    pairs: list[tuple[tuple[int, int], str, str]] = []
    for key in shared_keys:
        g = normalize_text(greek_verses[key], greek=True)
        e = normalize_text(english_verses[key], greek=False)
        if g and e:
            pairs.append((key, g, e))

    if not pairs:
        return {}

    # Write src/trg sentence pairs to temp files (eflomal expects file-based input)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"eflomal_{book}_"))
    src_path = tmp_dir / "src.txt"
    trg_path = tmp_dir / "trg.txt"
    fwd_path = tmp_dir / "fwd.align"
    rev_path = tmp_dir / "rev.align"

    try:
        with src_path.open("w", encoding="utf-8") as fsrc, \
             trg_path.open("w", encoding="utf-8") as ftrg:
            for _, g, e in pairs:
                fsrc.write(g + "\n")
                ftrg.write(e + "\n")

        aligner = Aligner()
        with src_path.open(encoding="utf-8") as fsrc, \
             trg_path.open(encoding="utf-8") as ftrg:
            aligner.align(
                fsrc,
                ftrg,
                links_filename_fwd=str(fwd_path),
                # NOTE: skipping reverse alignment — the eflomal binary
                # segfaults on Windows when writing rev.align (0xC0000005).
                # We only need forward (Greek→English) lookups anyway.
                links_filename_rev=None,
                quiet=True,
            )

        result: dict[str, list[list[int]]] = {}
        with fwd_path.open(encoding="utf-8") as f:
            alignment_lines = f.readlines()

        if len(alignment_lines) != len(pairs):
            print(
                f"  WARNING {book}: pair count {len(pairs)} != alignment line count "
                f"{len(alignment_lines)}",
                file=sys.stderr,
            )

        for (key, _, _), line in zip(pairs, alignment_lines):
            pair_list: list[list[int]] = []
            for tok in line.strip().split():
                if "-" in tok:
                    g_s, e_s = tok.split("-", 1)
                    try:
                        pair_list.append([int(g_s), int(e_s)])
                    except ValueError:
                        continue
            result[f"{key[0]}:{key[1]}"] = pair_list
        return result

    finally:
        # Clean up temp files
        for p in [src_path, trg_path, fwd_path, rev_path]:
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            tmp_dir.rmdir()
        except OSError:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run eflomal alignment on Greek ↔ English verse pairs."
    )
    parser.add_argument(
        "--books",
        nargs="+",
        help="Book slugs to align (e.g. matt mark luke). Use --all for all 27 books.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Align all 27 books.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON path (e.g. data/alignment/gospels.json).",
    )
    args = parser.parse_args()

    if args.all:
        books = list(SLUG_TO_FILE_NUM.keys())
    elif args.books:
        books = args.books
    else:
        parser.error("Specify either --books <list> or --all")

    result: dict[str, dict[str, list[list[int]]]] = {}
    for book in books:
        print(f"Aligning {book}...", file=sys.stderr, flush=True)
        try:
            book_alignment = align_book(book)
            result[book] = book_alignment
            print(
                f"  {book}: {len(book_alignment)} verse alignments",
                file=sys.stderr,
                flush=True,
            )
        except Exception as e:
            print(f"  {book}: FAILED — {e}", file=sys.stderr)
            result[book] = {}

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    total_verses = sum(len(v) for v in result.values())
    print(
        f"Wrote alignments for {len(result)} books "
        f"({total_verses} verses total) to {output_path}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
