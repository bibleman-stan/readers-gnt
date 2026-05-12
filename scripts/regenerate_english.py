"""
regenerate_english.py — KJV English extractor for readers-gnt.
Thin wrapper over atu_method.kjv_alignment.align_verse() (Wave 5b).

This is the sole English-generation script. KJV-verbatim English is the
only pipeline; the eflomal-based legacy (Wave 2) has been retired (Wave 6).

Architecture
------------
Substrate : viz.bible MetaV CSV (CC-BY-SA 3.0) — per-KJV-word Strong's
            tagging. Loaded once via load_kjv_strongs_index() and cached.
            Lives at ../atu-method/data/kjv-strongs/.
Source    : v4-editorial Greek ATU files (one Greek ATU line per line).
Token     : TAGNT rows for the verse; Strong's extracted via
            extract_strongs_from_tagnt_col(col3, col11, col12).
Algorithm : atu_method.kjv_alignment.align_verse() — per-verse KJV
            distribution preserving KJV word order within each ATU line.

Output
------
data/text-files/v4/eng-kjv/<NN-book>/<slug>-<NN>.txt
Format: verse marker "1:1", one English ATU line per Greek ATU line,
blank-line separator between verses. Identical to Wave 2 format.

Usage
-----
  python scripts/regenerate_english.py --book matt
  python scripts/regenerate_english.py --all
  python scripts/regenerate_english.py --book matt --force
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

REPO_ROOT    = Path(__file__).resolve().parent.parent       # readers-gnt/
ATU_METHOD   = REPO_ROOT.parent / "atu-method"              # sibling repo

V4_EDITORIAL = REPO_ROOT / "data" / "text-files" / "v4" / "grc"
TAGNT_DIR    = REPO_ROOT / "data" / "text-files" / "tagnt-source"
METAV_DIR    = ATU_METHOD / "data" / "kjv-strongs"
OUTPUT_ROOT  = REPO_ROOT / "data" / "text-files" / "v4" / "eng-kjv"

TAGNT_MAT_JHN = TAGNT_DIR / "TAGNT_Mat-Jhn.txt"
TAGNT_ACT_REV = TAGNT_DIR / "TAGNT_Act-Rev.txt"

# ---------------------------------------------------------------------------
# Wire in atu_method (sibling repo, no install needed)
# ---------------------------------------------------------------------------

sys.path.insert(0, str(ATU_METHOD))

from atu_method.kjv_alignment import (     # noqa: E402
    SourceToken,
    align_verse as _align_verse_universal,
    extract_strongs_from_tagnt_col,
    load_kjv_strongs_index,
)

# ---------------------------------------------------------------------------
# Book metadata (27 NT books)
# 4-tuple: (dir_name, slug, tagnt_prefix, tagnt_file)
# tagnt_prefix is the 3-letter TAGNT book code; align_verse() accepts both
# TAGNT aliases (Mat) and full OSIS (Matt) transparently.
# ---------------------------------------------------------------------------

BOOK_META = [
    ("01-matt",   "matt",   "Mat", TAGNT_MAT_JHN),
    ("02-mark",   "mark",   "Mrk", TAGNT_MAT_JHN),
    ("03-luke",   "luke",   "Luk", TAGNT_MAT_JHN),
    ("04-john",   "john",   "Jhn", TAGNT_MAT_JHN),
    ("05-acts",   "acts",   "Act", TAGNT_ACT_REV),
    ("06-rom",    "rom",    "Rom", TAGNT_ACT_REV),
    ("07-1cor",   "1cor",   "1Co", TAGNT_ACT_REV),
    ("08-2cor",   "2cor",   "2Co", TAGNT_ACT_REV),
    ("09-gal",    "gal",    "Gal", TAGNT_ACT_REV),
    ("10-eph",    "eph",    "Eph", TAGNT_ACT_REV),
    ("11-phil",   "phil",   "Php", TAGNT_ACT_REV),
    ("12-col",    "col",    "Col", TAGNT_ACT_REV),
    ("13-1thess", "1thess", "1Th", TAGNT_ACT_REV),
    ("14-2thess", "2thess", "2Th", TAGNT_ACT_REV),
    ("15-1tim",   "1tim",   "1Ti", TAGNT_ACT_REV),
    ("16-2tim",   "2tim",   "2Ti", TAGNT_ACT_REV),
    ("17-titus",  "titus",  "Tit", TAGNT_ACT_REV),
    ("18-phlm",   "phlm",   "Phm", TAGNT_ACT_REV),
    ("19-heb",    "heb",    "Heb", TAGNT_ACT_REV),
    ("20-jas",    "jas",    "Jas", TAGNT_ACT_REV),
    ("21-1pet",   "1pet",   "1Pe", TAGNT_ACT_REV),
    ("22-2pet",   "2pet",   "2Pe", TAGNT_ACT_REV),
    ("23-1john",  "1john",  "1Jn", TAGNT_ACT_REV),
    ("24-2john",  "2john",  "2Jn", TAGNT_ACT_REV),
    ("25-3john",  "3john",  "3Jn", TAGNT_ACT_REV),
    ("26-jude",   "jude",   "Jud", TAGNT_ACT_REV),
    ("27-rev",    "rev",    "Rev", TAGNT_ACT_REV),
]

BOOK_BY_SLUG = {m[1]: m for m in BOOK_META}

# ---------------------------------------------------------------------------
# TAGNT loader — returns per-verse token lists for one book
# Returns {verse_ref -> [(greek_surface, col3, col11, col12), ...]}
# where col3 = Strong's+morph, col11 = bare Strong's, col12 = alt Strong's
# ---------------------------------------------------------------------------

_RE_TOKEN_ROW = re.compile(r"^([0-9A-Z][a-zA-Z0-9]+\.\d+\.\d+)#\d+=")


def load_tagnt_book(
    tagnt_path: Path, tagnt_prefix: str
) -> dict[str, list[tuple[str, str, str, str]]]:
    """Parse TAGNT file for one book.

    Returns {verse_ref -> [(greek_surface, col3, col11, col12), ...]}
    verse_ref example: "Mat.1.2"
    Columns (0-indexed): 1=Greek(translit), 3=Strong+morph, 11=bare Strong, 12=alt Strong.
    """
    verses: dict[str, list[tuple[str, str, str, str]]] = {}
    with open(tagnt_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            m = _RE_TOKEN_ROW.match(line)
            if not m:
                continue
            verse_ref = m.group(1)
            if not verse_ref.startswith(tagnt_prefix + "."):
                continue
            parts = line.split("\t")
            if len(parts) < 12:
                continue
            # col1: "Ἀβραὰμ (Abraam)" — strip transliteration in parens
            greek_raw = parts[1].strip()
            greek_surface = re.sub(r"\s*\([^)]+\)\s*$", "", greek_raw).strip()
            col3  = parts[3].strip()  if len(parts) > 3  else ""  # G0011=N-NSM-P
            col11 = parts[11].strip() if len(parts) > 11 else ""  # G0011
            col12 = parts[12].strip() if len(parts) > 12 else ""  # alt Strong's (may be absent)
            if verse_ref not in verses:
                verses[verse_ref] = []
            verses[verse_ref].append((greek_surface, col3, col11, col12))
    return verses


# ---------------------------------------------------------------------------
# v4-editorial parser (unchanged from Wave 2 — format is stable)
# ---------------------------------------------------------------------------

def parse_v4_file(path: Path) -> list[tuple[str, list[str]]]:
    """Parse a v4-editorial chapter file.

    Returns list of (verse_ref, [atu_line, ...]) preserving order.
    verse_ref is e.g. "1:1".
    """
    verses: list[tuple[str, list[str]]] = []
    current_verse: Optional[str] = None
    current_lines: list[str] = []

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if re.match(r"^\d+:\d+$", line.strip()):
                if current_verse is not None:
                    verses.append((current_verse, current_lines))
                current_verse = line.strip()
                current_lines = []
            elif line.strip() == "":
                pass
            else:
                if current_verse is not None:
                    current_lines.append(line.strip())

    if current_verse is not None and current_lines:
        verses.append((current_verse, current_lines))

    return verses


# ---------------------------------------------------------------------------
# Greek surface normaliser (for token matching)
# ---------------------------------------------------------------------------

_GREEK_PUNCT = set(".,;:·—…!?·\"'()[]{}–—")


def normalise_greek(s: str) -> str:
    return s.rstrip("".join(_GREEK_PUNCT)).strip()


def tokenise_atu_line(line: str) -> list[str]:
    return [normalise_greek(t) for t in line.split() if t]


# ---------------------------------------------------------------------------
# Cross-verse line-fold markers (§5.1)
#
# v4-editorial uses superscript-digit runs to fold the start of the next
# canonical verse onto the current line for colometric readability. Example
# (Matt 3:1):
#
#     Ἐν δὲ ταῖς ἡμέραις … τῆς Ἰουδαίας ²καὶ λέγων·
#
# The ² marker means "καὶ λέγων· belongs to verse 3:2 in canonical
# versification." TAGNT/MetaV key those tokens under Mat.3.2, not Mat.3.1.
# The marker handler routes pre-marker tokens to the current verse's
# align_verse call and post-marker tokens to the target verse's call (as a
# phantom line 0), then folds the phantom's English back onto the original
# marked line. 22 instances across the NT corpus (inventory: 2026-05-12).
# ---------------------------------------------------------------------------

_SUPERSCRIPT_TO_DIGIT = {
    "⁰": 0, "¹": 1, "²": 2, "³": 3, "⁴": 4,
    "⁵": 5, "⁶": 6, "⁷": 7, "⁸": 8, "⁹": 9,
}
_SUPERSCRIPT_RE = re.compile(
    "[" + "".join(_SUPERSCRIPT_TO_DIGIT.keys()) + "]+"
)


def _superscript_run_to_int(s: str) -> int:
    return int("".join(str(_SUPERSCRIPT_TO_DIGIT[c]) for c in s))


def segment_atu_line(line: str, current_verse: int) -> list[tuple[int, str]]:
    """Split an ATU line at cross-verse markers.

    Returns a list of (target_verse, segment_text) tuples in textual order.
    Lines without markers return a single segment tagged with current_verse.
    A line that begins with a marker yields no leading current-verse segment.
    """
    segments: list[tuple[int, str]] = []
    cursor = 0
    target = current_verse
    for m in _SUPERSCRIPT_RE.finditer(line):
        pre = line[cursor:m.start()].strip()
        if pre:
            segments.append((target, pre))
        target = _superscript_run_to_int(m.group(0))
        cursor = m.end()
    tail = line[cursor:].strip()
    if tail:
        segments.append((target, tail))
    return segments


# ---------------------------------------------------------------------------
# Per-verse token alignment: maps TAGNT tokens onto ATU lines
# Returns list[list[SourceToken]] — one inner list per ATU line
# ---------------------------------------------------------------------------

def build_source_tokens_per_line(
    atu_lines: list[str],
    tagnt_tokens: list[tuple[str, str, str, str]],
) -> list[list[SourceToken]]:
    """Assign TAGNT tokens to ATU lines by sequential Greek-surface consumption.

    For each ATU line, count its Greek words, then consume that many TAGNT
    tokens in order. Each token becomes a SourceToken(text, strongs_list)
    where strongs_list comes from extract_strongs_from_tagnt_col(col3, col11, col12).

    Returns list[list[SourceToken]] — parallel to atu_lines.
    """
    result: list[list[SourceToken]] = []
    cursor = 0
    n_tagnt = len(tagnt_tokens)

    for atu_line in atu_lines:
        atu_words = tokenise_atu_line(atu_line)
        n_words = len(atu_words)
        line_tokens: list[SourceToken] = []

        consumed = 0
        for atu_word in atu_words:
            if cursor + consumed >= n_tagnt:
                # Ran out of TAGNT tokens; pad with empty SourceToken
                line_tokens.append(SourceToken(text=atu_word, strongs_list=()))
                continue

            # Try to match by surface form (with up to 2-position lookahead)
            matched = False
            for lookahead in range(3):
                idx = cursor + consumed + lookahead
                if idx >= n_tagnt:
                    break
                greek_surface, col3, col11, col12 = tagnt_tokens[idx]
                tagnt_norm = normalise_greek(greek_surface)
                if tagnt_norm == atu_word:
                    # Advance the cursor past any skipped tokens, but DON'T
                    # absorb their Strong's onto this line. Skipped tokens
                    # via lookahead-match are orphan-class — TAGNT has them
                    # but v4-editorial elides them (implicit subject, elided
                    # speech verb, etc.). Absorbing their Strong's claims KJV
                    # words whose vposes don't fit this line's range and
                    # breaks cross-line KJV reading order. By leaving them
                    # unclaimed, Pass C/D in distribute.py routes their KJV
                    # equivalents to the nearest-vpos line via positional
                    # proximity — which is the correct line by definition.
                    # Canonical cases: Matt 4:23 (ὁ Ἰησοῦς orphan),
                    # Acts 2:38 (φησὶν orphan).
                    for skip_idx in range(cursor + consumed, idx):
                        consumed += 1
                    # Consume the matched token
                    strongs = tuple(extract_strongs_from_tagnt_col(col3, col11, col12))
                    line_tokens.append(SourceToken(text=greek_surface, strongs_list=strongs))
                    consumed += 1
                    matched = True
                    break

            if not matched:
                # No surface match — consume next TAGNT token anyway (best-effort)
                if cursor + consumed < n_tagnt:
                    greek_surface, col3, col11, col12 = tagnt_tokens[cursor + consumed]
                    strongs = tuple(extract_strongs_from_tagnt_col(col3, col11, col12))
                    line_tokens.append(SourceToken(text=greek_surface, strongs_list=strongs))
                    consumed += 1
                else:
                    line_tokens.append(SourceToken(text=atu_word, strongs_list=()))

        cursor += consumed
        result.append(line_tokens)

    return result


# ---------------------------------------------------------------------------
# Per-book generation
# ---------------------------------------------------------------------------

def generate_book(
    dir_name: str,
    slug: str,
    tagnt_prefix: str,
    tagnt_path: Path,
    force: bool = False,
) -> dict:
    """Generate eng-gloss-kjv output for all chapters of one book."""
    src_dir = V4_EDITORIAL / dir_name
    if not src_dir.exists():
        print(f"  SKIP: {dir_name} — source dir not found", file=sys.stderr)
        return {}

    out_dir = OUTPUT_ROOT / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Loading TAGNT for {tagnt_prefix}...")
    tagnt_verses = load_tagnt_book(tagnt_path, tagnt_prefix)

    chapter_files = sorted(
        src_dir.glob(f"{slug}-*.txt"),
        key=lambda p: int(re.search(r"-(\d+)", p.stem).group(1)),
    )

    stats = {"chapters": 0, "verses": 0, "lines": 0, "empty_lines": 0}

    for ch_path in chapter_files:
        out_path = out_dir / ch_path.name
        if out_path.exists() and not force:
            print(f"  SKIP (exists): {out_path.name} — use --force to overwrite")
            continue

        verses = parse_v4_file(ch_path)

        # Pre-pass: segment every ATU line by cross-verse markers.
        # Most lines have no markers and produce a single segment tagged
        # with the current verse; lines with markers split into multiple
        # segments tagged with their target verses.
        segmented_by_verse: dict[str, list[list[tuple[int, str]]]] = {}
        for verse_ref, atu_lines in verses:
            current_vs = int(verse_ref.split(":")[1])
            segmented_by_verse[verse_ref] = [
                segment_atu_line(line, current_vs) for line in atu_lines
            ]

        # Phantom map: target_verse_ref -> [(source_verse_ref, source_line_idx, text), ...]
        # When a marker in source_verse_ref's line N targets a different
        # verse, the post-marker text becomes a phantom line for the
        # target verse's alignment call.
        phantoms_into: dict[str, list[dict]] = defaultdict(list)
        for verse_ref, segmented in segmented_by_verse.items():
            ch_str, vs_str = verse_ref.split(":")
            current_vs = int(vs_str)
            for line_idx, segments in enumerate(segmented):
                for tv, text in segments:
                    if tv != current_vs:
                        target_ref = f"{ch_str}:{tv}"
                        phantoms_into[target_ref].append({
                            "source_verse_ref": verse_ref,
                            "source_line_idx": line_idx,
                            "text": text,
                        })

        # Per-verse English buffer (rendered after all alignments complete).
        verse_eng: dict[str, list[str]] = {
            vr: [""] * len(atu_lines) for vr, atu_lines in verses
        }

        for verse_ref, atu_lines in verses:
            ch_str, vs_str = verse_ref.split(":")
            chapter = int(ch_str)
            verse   = int(vs_str)

            # Build the modified atu_lines for align_verse:
            # phantoms_from_prior_verses + current-verse-only segments per line.
            modified_atu_lines: list[str] = []
            # Each entry: ("phantom"|"current", target_verse_ref, target_line_idx)
            line_targets: list[tuple[str, str, int]] = []

            # Phantom lines first (in source-line order — TAGNT for this
            # verse keys these tokens at the start of the canonical verse).
            for phantom in phantoms_into.get(verse_ref, []):
                modified_atu_lines.append(phantom["text"])
                line_targets.append((
                    "phantom",
                    phantom["source_verse_ref"],
                    phantom["source_line_idx"],
                ))

            # Current-verse content per ATU line (skip marker-targeted segments).
            for line_idx, segments in enumerate(segmented_by_verse[verse_ref]):
                current_text = " ".join(
                    text for (tv, text) in segments if tv == verse
                )
                modified_atu_lines.append(current_text)
                line_targets.append(("current", verse_ref, line_idx))

            tagnt_key = f"{tagnt_prefix}.{chapter}.{verse}"
            tagnt_tokens = tagnt_verses.get(tagnt_key, [])

            if not tagnt_tokens or all(not t for t in modified_atu_lines):
                eng_lines = [""] * len(modified_atu_lines)
            else:
                source_tokens_per_line = build_source_tokens_per_line(
                    modified_atu_lines, tagnt_tokens
                )
                try:
                    eng_lines = _align_verse_universal(
                        tagnt_prefix,
                        chapter,
                        verse,
                        source_tokens_per_line,
                        METAV_DIR,
                    )
                except KeyError as e:
                    print(f"  WARNING: MetaV miss for {tagnt_key}: {e}", file=sys.stderr)
                    eng_lines = [""] * len(modified_atu_lines)

            while len(eng_lines) < len(modified_atu_lines):
                eng_lines.append("")
            eng_lines = eng_lines[: len(modified_atu_lines)]

            # Distribute eng_lines back to verse_eng buffer.
            # Phantom English appends to the source line (concatenates with
            # whatever pre-marker English already lives there); current
            # English fills the target line (may have a phantom already
            # appended if processing order has phantom first).
            for english, (kind, ref, line_idx) in zip(eng_lines, line_targets):
                existing = verse_eng[ref][line_idx]
                if kind == "phantom":
                    if existing and english:
                        verse_eng[ref][line_idx] = f"{existing} {english}"
                    elif english:
                        verse_eng[ref][line_idx] = english
                else:  # "current"
                    if existing and english:
                        verse_eng[ref][line_idx] = f"{english} {existing}"
                    elif english:
                        verse_eng[ref][line_idx] = english

        # Render the chapter output.
        output_blocks: list[str] = []
        for verse_ref, atu_lines in verses:
            output_blocks.append(verse_ref)
            for el in verse_eng[verse_ref]:
                output_blocks.append(el)
                stats["lines"] += 1
                if not el:
                    stats["empty_lines"] += 1
            output_blocks.append("")
            stats["verses"] += 1

        out_path.write_text("\n".join(output_blocks) + "\n", encoding="utf-8")
        stats["chapters"] += 1
        print(
            f"  Wrote {out_path.relative_to(REPO_ROOT)} "
            f"({stats['verses']} verses cumulative)"
        )

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate KJV-verbatim English gloss files via atu_method.kjv_alignment."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--book", metavar="SLUG",
                       help="Single book slug (e.g. matt, mark, rom)")
    group.add_argument("--all", action="store_true",
                       help="Process all 27 NT books")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing output files")

    args = parser.parse_args()

    # Warm the MetaV cache once before any book loop
    print(f"Loading MetaV KJV Strong's index from {METAV_DIR} …")
    load_kjv_strongs_index(METAV_DIR)
    print("MetaV cache warm.")

    if args.book:
        slug = args.book.lower()
        if slug not in BOOK_BY_SLUG:
            print(f"Unknown book slug '{slug}'. Known slugs: {list(BOOK_BY_SLUG.keys())}")
            sys.exit(1)
        dir_name, slug, tagnt_prefix, tagnt_path = BOOK_BY_SLUG[slug]
        print(f"\nProcessing {dir_name}...")
        stats = generate_book(dir_name, slug, tagnt_prefix, tagnt_path, args.force)
        print(f"Done: {stats}")

    elif args.all:
        total = {"chapters": 0, "verses": 0, "lines": 0, "empty_lines": 0}
        import time
        t0 = time.time()
        for dir_name, slug, tagnt_prefix, tagnt_path in BOOK_META:
            print(f"\nProcessing {dir_name}...")
            stats = generate_book(dir_name, slug, tagnt_prefix, tagnt_path, args.force)
            for k in total:
                total[k] += stats.get(k, 0)
        elapsed = time.time() - t0
        print(f"\nAll 27 books done in {elapsed:.1f}s: {total}")


if __name__ == "__main__":
    main()
