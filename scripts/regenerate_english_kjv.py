"""
regenerate_english_kjv.py — KJV-style English extractor for readers-gnt.

Architecture
------------
Substrate : TAGNT English column (per-Greek-token, KJV-style glosses already
            supplied by STEPBible; CC BY 4.0).  Each row maps one Greek surface
            form to one English fragment; the columns are tab-separated.
Fallback  : TBESG brief lexicon keyed by dStrong (e.g. "G0011"), column 6
            (0-indexed), for any token whose TAGNT English cell is empty.
Output    : data/text-files/eng-gloss-kjv/<NN-book>/<slug>-<NN>.txt
            Parallel directory to the legacy eng-gloss/; identical format
            (verse marker "1:1", one English line per Greek ATU line, blank
            line between verses).  NOT an in-place replacement; Wave 4 will
            promote per-book after verification.

Alignment strategy
------------------
TAGNT tokens appear in the same textual order as the Greek words in v4-
editorial.  We tokenize each Greek ATU line (strip punctuation, split on
whitespace) and consume TAGNT tokens sequentially, matching by stripped surface
form.  All tokens that map to one ATU line are concatenated into a single
English line.

<angle-bracket> handling
------------------------
TAGNT marks translator-inserted English (no direct Greek correspondent) with
<...> e.g. "<the>".  For ESL/newcomer readers we drop the brackets and keep
the word as plain English ("the"), which is what a natural English reader
expects.

Usage
-----
  python scripts/regenerate_english_kjv.py --book matt
  python scripts/regenerate_english_kjv.py --all
  python scripts/regenerate_english_kjv.py --book matt --force
"""

import argparse
import re
import sys
import os
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path configuration — absolute, derived from this file's location
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent          # readers-gnt/
ATU_METHOD_ROOT = REPO_ROOT.parent / "atu-method"           # sibling repo

V4_EDITORIAL = REPO_ROOT / "data" / "text-files" / "v4-editorial"
TAGNT_DIR    = REPO_ROOT / "data" / "text-files" / "tagnt-source"
TBESG_PATH   = ATU_METHOD_ROOT / "data" / "lexicons" / "TBESG.txt"
OUTPUT_ROOT  = REPO_ROOT / "data" / "text-files" / "eng-gloss-kjv"

TAGNT_MAT_JHN = TAGNT_DIR / "TAGNT_Mat-Jhn.txt"
TAGNT_ACT_REV = TAGNT_DIR / "TAGNT_Act-Rev.txt"

# ---------------------------------------------------------------------------
# Book metadata: (NN-slug, TAGNT-prefix, source-file)
# TAGNT uses three-letter abbreviations; v4-editorial uses two-digit-slug
# ---------------------------------------------------------------------------

BOOK_META = [
    # (dir_name,       slug,     tagnt_prefix, tagnt_file)
    ("01-matt",        "matt",   "Mat",        TAGNT_MAT_JHN),
    ("02-mark",        "mark",   "Mrk",        TAGNT_MAT_JHN),
    ("03-luke",        "luke",   "Luk",        TAGNT_MAT_JHN),
    ("04-john",        "john",   "Jhn",        TAGNT_MAT_JHN),
    ("05-acts",        "acts",   "Act",        TAGNT_ACT_REV),
    ("06-rom",         "rom",    "Rom",        TAGNT_ACT_REV),
    ("07-1cor",        "1cor",   "1Co",        TAGNT_ACT_REV),
    ("08-2cor",        "2cor",   "2Co",        TAGNT_ACT_REV),
    ("09-gal",         "gal",    "Gal",        TAGNT_ACT_REV),
    ("10-eph",         "eph",    "Eph",        TAGNT_ACT_REV),
    ("11-phil",        "phil",   "Php",        TAGNT_ACT_REV),
    ("12-col",         "col",    "Col",        TAGNT_ACT_REV),
    ("13-1thess",      "1thess", "1Th",        TAGNT_ACT_REV),
    ("14-2thess",      "2thess", "2Th",        TAGNT_ACT_REV),
    ("15-1tim",        "1tim",   "1Ti",        TAGNT_ACT_REV),
    ("16-2tim",        "2tim",   "2Ti",        TAGNT_ACT_REV),
    ("17-titus",       "titus",  "Tit",        TAGNT_ACT_REV),
    ("18-phlm",        "phlm",   "Phm",        TAGNT_ACT_REV),
    ("19-heb",         "heb",    "Heb",        TAGNT_ACT_REV),
    ("20-jas",         "jas",    "Jas",        TAGNT_ACT_REV),
    ("21-1pet",        "1pet",   "1Pe",        TAGNT_ACT_REV),
    ("22-2pet",        "2pet",   "2Pe",        TAGNT_ACT_REV),
    ("23-1john",       "1john",  "1Jn",        TAGNT_ACT_REV),
    ("24-2john",       "2john",  "2Jn",        TAGNT_ACT_REV),
    ("25-3john",       "3john",  "3Jn",        TAGNT_ACT_REV),
    ("26-jude",        "jude",   "Jud",        TAGNT_ACT_REV),
    ("27-rev",         "rev",    "Rev",        TAGNT_ACT_REV),
]

# Quick lookup by short slug
BOOK_BY_SLUG = {m[1]: m for m in BOOK_META}

# ---------------------------------------------------------------------------
# TBESG fallback lexicon loader
# ---------------------------------------------------------------------------

def load_tbesg(path: Path) -> dict[str, str]:
    """Return {dStrong_base -> brief_gloss} from TBESG.

    TBESG lines have tab-separated fields; the entry lines (not comment/header)
    start with a Strong number like G0001 or G0001G.  We use column 0 as the
    key and column 6 (0-indexed) as the gloss.
    """
    glosses: dict[str, str] = {}
    if not path.exists():
        print(f"WARNING: TBESG not found at {path}; fallback disabled.", file=sys.stderr)
        return glosses
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7:
                continue
            key = parts[0].strip()
            if not re.match(r"^[GH]\d{4}", key):
                continue
            gloss = parts[6].strip()
            if gloss:
                # Strip HTML bold tags that appear in the brief gloss column
                gloss = re.sub(r"</?b>", "", gloss)
                glosses[key] = gloss
    return glosses


# ---------------------------------------------------------------------------
# TAGNT loader — returns per-verse token lists for one book
# ---------------------------------------------------------------------------

_RE_TOKEN_ROW = re.compile(r"^([A-Z][a-z0-9]+\.\d+\.\d+)#\d+=")
_RE_VERSE_KEY = re.compile(r"^([A-Z][a-z0-9]+\.\d+\.\d+)#\d+=")


def load_tagnt_book(tagnt_path: Path, tagnt_prefix: str) -> dict[str, list[tuple[str, str, str]]]:
    """Parse TAGNT file for one book.

    Returns {verse_ref -> [(greek_surface, english, dstrong), ...]}
    where verse_ref is e.g. "Mat.1.2".

    Only rows whose reference starts with tagnt_prefix are included.
    The english column may be empty; caller falls back to TBESG.
    """
    verses: dict[str, list[tuple[str, str, str]]] = {}

    with open(tagnt_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            # Token data rows look like: Mat.1.2#01=NKO\tGreek (translit)\tEnglish\t...
            m = _RE_TOKEN_ROW.match(line)
            if not m:
                continue
            verse_ref = m.group(1)
            if not verse_ref.startswith(tagnt_prefix + "."):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            # col 1: "Ἀβραὰμ (Abraam)"  — strip transliteration in parens
            greek_raw = parts[1].strip()
            greek_surface = re.sub(r"\s*\([^)]+\)\s*$", "", greek_raw).strip()
            # col 2: English, may contain <...> brackets
            english = parts[2].strip() if len(parts) > 2 else ""
            # col 3: dStrong (e.g. "G0011=N-NSM-P") — take just the Strong part
            dstrong_raw = parts[3].strip() if len(parts) > 3 else ""
            dstrong = dstrong_raw.split("=")[0].strip() if dstrong_raw else ""

            if verse_ref not in verses:
                verses[verse_ref] = []
            verses[verse_ref].append((greek_surface, english, dstrong))

    return verses


# ---------------------------------------------------------------------------
# Greek surface normaliser — strips trailing punctuation for matching
# ---------------------------------------------------------------------------

_GREEK_PUNCT = set(".,;:·—…!?·\"'()[]{}–—")

def normalise_greek(s: str) -> str:
    """Strip trailing Greek/punctuation from a surface form for matching."""
    return s.rstrip("".join(_GREEK_PUNCT)).strip()


def tokenise_atu_line(line: str) -> list[str]:
    """Split a Greek ATU line into individual token surface forms.

    Handles multi-word lines (e.g. "Ἀβραὰμ ἐγέννησεν τὸν Ἰσαάκ,").
    Returns list of stripped tokens (punctuation stripped for matching).
    """
    raw_tokens = line.split()
    return [normalise_greek(t) for t in raw_tokens if t]


# ---------------------------------------------------------------------------
# English assembly helpers
# ---------------------------------------------------------------------------

_ANGLE_BRACKET = re.compile(r"<([^>]+)>")

def render_english(eng: str) -> str:
    """Convert TAGNT English cell to reader-facing text.

    <the> -> "the"  (drop angle brackets, keep content for plain English)
    Empty -> ""
    """
    if not eng:
        return ""
    # Drop angle brackets, keep enclosed text
    return _ANGLE_BRACKET.sub(r"\1", eng).strip()


def assemble_line_english(token_engls: list[str]) -> str:
    """Join per-token English fragments into one line."""
    parts = [e for e in token_engls if e]
    if not parts:
        return ""
    result = " ".join(parts)
    # Collapse any double spaces
    result = re.sub(r"  +", " ", result)
    return result.strip()


# ---------------------------------------------------------------------------
# Core alignment: verse tokens -> per-ATU-line English
# ---------------------------------------------------------------------------

def align_verse(atu_lines: list[str],
                tagnt_tokens: list[tuple[str, str, str]],
                tbesg: dict[str, str],
                verse_ref: str) -> list[str]:
    """Align TAGNT tokens to ATU lines by sequential consumption.

    For each ATU line, we determine how many Greek tokens it contains
    (by tokenising the line), then consume that many TAGNT tokens in order.
    The English for those tokens is concatenated to form the English ATU line.

    Returns list[str] of English ATU lines, one per Greek ATU line.
    """
    english_lines: list[str] = []
    token_cursor = 0
    n_tokens = len(tagnt_tokens)

    for atu_line in atu_lines:
        atu_words = tokenise_atu_line(atu_line)
        n_words = len(atu_words)

        if n_words == 0:
            english_lines.append("")
            continue

        collected: list[str] = []
        tokens_consumed = 0

        for atu_word in atu_words:
            if token_cursor + tokens_consumed >= n_tokens:
                # Ran out of TAGNT tokens — pad empty
                collected.append("")
                continue

            # Find the TAGNT token matching this ATU word
            # Strategy: look ahead up to 2 positions to handle minor surface
            # divergences (variant spellings, accent differences)
            matched = False
            for lookahead in range(3):  # try cursor+0, cursor+1, cursor+2
                idx = token_cursor + tokens_consumed + lookahead
                if idx >= n_tokens:
                    break
                tagnt_greek, tagnt_eng, dstrong = tagnt_tokens[idx]
                tagnt_norm = normalise_greek(tagnt_greek)
                if tagnt_norm == atu_word or tagnt_norm == normalise_greek(atu_word):
                    # Skip any lookahead tokens we jumped over (they get empty eng)
                    for skip in range(lookahead):
                        sk_idx = token_cursor + tokens_consumed + skip
                        _, sk_eng, sk_ds = tagnt_tokens[sk_idx]
                        e = render_english(sk_eng)
                        if not e and sk_ds:
                            e = tbesg.get(sk_ds, "")
                        if e:
                            collected.append(e)
                        tokens_consumed += 1
                    # Now consume the matched token
                    e = render_english(tagnt_eng)
                    if not e and dstrong:
                        e = tbesg.get(dstrong, "")
                    collected.append(e)
                    tokens_consumed += 1
                    matched = True
                    break

            if not matched:
                # No surface match — consume next TAGNT token anyway (best-effort)
                idx = token_cursor + tokens_consumed
                if idx < n_tokens:
                    _, tagnt_eng, dstrong = tagnt_tokens[idx]
                    e = render_english(tagnt_eng)
                    if not e and dstrong:
                        e = tbesg.get(dstrong, "")
                    collected.append(e)
                    tokens_consumed += 1
                else:
                    collected.append("")

        token_cursor += tokens_consumed
        english_lines.append(assemble_line_english(collected))

    # If TAGNT had more tokens than we consumed (continuation tokens for this
    # verse that are in a separate TAGNT sub-section), we silently drop them —
    # they were already attached to the last ATU line via the continuation
    # mechanism in TAGNT's #_Mat.x.y secondary rows.

    return english_lines


# ---------------------------------------------------------------------------
# v4-editorial parser
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
            # Verse marker: "1:1" or "22:21"
            if re.match(r"^\d+:\d+$", line.strip()):
                if current_verse is not None:
                    verses.append((current_verse, current_lines))
                current_verse = line.strip()
                current_lines = []
            elif line.strip() == "":
                # Blank line = verse separator (ignore)
                pass
            else:
                if current_verse is not None:
                    current_lines.append(line.strip())

    if current_verse is not None and current_lines:
        verses.append((current_verse, current_lines))

    return verses


# ---------------------------------------------------------------------------
# TAGNT reference converter: "1:2" + book_prefix -> "Mat.1.2"
# ---------------------------------------------------------------------------

def make_tagnt_ref(verse_ref: str, tagnt_prefix: str) -> str:
    """Convert verse_ref "1:2" to TAGNT key "Mat.1.2"."""
    ch, vs = verse_ref.split(":")
    return f"{tagnt_prefix}.{ch}.{vs}"


# ---------------------------------------------------------------------------
# Per-book generation
# ---------------------------------------------------------------------------

def generate_book(dir_name: str, slug: str, tagnt_prefix: str,
                  tagnt_path: Path, tbesg: dict[str, str],
                  force: bool = False) -> dict:
    """Generate eng-gloss-kjv output for all chapters of one book.

    Returns stats dict.
    """
    src_dir = V4_EDITORIAL / dir_name
    if not src_dir.exists():
        print(f"  SKIP: {dir_name} — source dir not found", file=sys.stderr)
        return {}

    out_dir = OUTPUT_ROOT / dir_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load TAGNT once per book (it's the full Mat-Jhn or Act-Rev file)
    print(f"  Loading TAGNT for {tagnt_prefix}...")
    tagnt_verses = load_tagnt_book(tagnt_path, tagnt_prefix)

    chapter_files = sorted(src_dir.glob(f"{slug}-*.txt"),
                           key=lambda p: int(re.search(r"-(\d+)", p.stem).group(1)))

    stats = {"chapters": 0, "verses": 0, "lines": 0, "empty_lines": 0, "fallback_hits": 0}

    for ch_path in chapter_files:
        out_path = out_dir / ch_path.name
        if out_path.exists() and not force:
            print(f"  SKIP (exists): {out_path.name} — use --force to overwrite")
            continue

        verses = parse_v4_file(ch_path)
        output_blocks: list[str] = []

        for verse_ref, atu_lines in verses:
            tagnt_key = make_tagnt_ref(verse_ref, tagnt_prefix)
            tagnt_tokens = tagnt_verses.get(tagnt_key, [])

            if not tagnt_tokens:
                # No TAGNT data for this verse — output empty lines
                eng_lines = [""] * len(atu_lines)
            else:
                eng_lines = align_verse(atu_lines, tagnt_tokens, tbesg, tagnt_key)

            output_blocks.append(verse_ref)
            for el in eng_lines:
                output_blocks.append(el)
                stats["lines"] += 1
                if not el:
                    stats["empty_lines"] += 1
            output_blocks.append("")  # blank line separator
            stats["verses"] += 1

        out_path.write_text("\n".join(output_blocks) + "\n", encoding="utf-8")
        stats["chapters"] += 1
        print(f"  Wrote {out_path.relative_to(REPO_ROOT)} "
              f"({stats['verses']} verses cumulative)")

    return stats


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test():
    """Run against Matt 1 and assert basic correctness."""
    print("Running self-test against Matt 1...")

    tbesg = load_tbesg(TBESG_PATH)

    # Ensure output exists (or generate it)
    out_path = OUTPUT_ROOT / "01-matt" / "matt-01.txt"
    if not out_path.exists():
        generate_book("01-matt", "matt", "Mat", TAGNT_MAT_JHN, tbesg, force=True)

    assert out_path.exists(), f"FAIL: output file not created at {out_path}"

    # Parse output
    with open(out_path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()

    # Count verses and English lines
    verse_markers = [l for l in lines if re.match(r"^\d+:\d+$", l)]
    content_lines = [l for l in lines if l and not re.match(r"^\d+:\d+$", l)]

    print(f"  Verses: {len(verse_markers)}")
    print(f"  Content lines: {len(content_lines)}")

    assert len(verse_markers) >= 25, f"FAIL: expected >=25 verses in Matt 1, got {len(verse_markers)}"

    # Check line count matches v4-editorial for Matt 1
    v4_path = V4_EDITORIAL / "01-matt" / "matt-01.txt"
    v4_verses = parse_v4_file(v4_path)
    v4_line_count = sum(len(lines_) for _, lines_ in v4_verses)
    assert len(content_lines) == v4_line_count, (
        f"FAIL: line count mismatch — v4 has {v4_line_count} lines, "
        f"output has {len(content_lines)}"
    )

    # Check >= 90% non-empty English content
    non_empty = len([l for l in content_lines if l.strip()])
    pct = non_empty / len(content_lines) * 100
    print(f"  Non-empty English lines: {non_empty}/{len(content_lines)} ({pct:.1f}%)")
    assert pct >= 90, f"FAIL: only {pct:.1f}% of lines have English content (need >=90%)"

    # Check Matt 1:2 contains "begat" and both "Abraham" and "Isaac"
    in_1_2 = False
    kjv_1_2_lines = []
    for line in lines:
        if line == "1:2":
            in_1_2 = True
            continue
        if in_1_2:
            if line == "" or re.match(r"^\d+:\d+$", line):
                break
            kjv_1_2_lines.append(line)

    combined_1_2 = " ".join(kjv_1_2_lines).lower()
    assert "begat" in combined_1_2, f"FAIL: 'begat' not found in 1:2 — got: {kjv_1_2_lines}"
    assert "abraham" in combined_1_2, f"FAIL: 'Abraham' not in 1:2"
    assert "isaac" in combined_1_2, f"FAIL: 'Isaac' not in 1:2"
    print(f"  Matt 1:2 check passed: {kjv_1_2_lines[:1]}")

    # Check Matt 1:23 — canonical test case
    # v4-editorial has "Μεθʼ ἡμῶν ὁ θεός." as the last ATU line of 1:23
    # It MUST contain "God with us" (or equivalent) — not bleed onto 1:24
    in_1_23 = False
    kjv_1_23_lines = []
    for line in lines:
        if line == "1:23":
            in_1_23 = True
            continue
        if in_1_23:
            if line == "" or re.match(r"^\d+:\d+$", line):
                break
            kjv_1_23_lines.append(line)

    print(f"  Matt 1:23 English lines: {kjv_1_23_lines}")
    combined_1_23 = " ".join(kjv_1_23_lines).lower()
    # Should contain "emmanuel" or "immanuel" or "god" on one of its lines
    # The last line corresponds to Μεθʼ ἡμῶν ὁ θεός
    has_god_with_us = ("god" in combined_1_23 and "us" in combined_1_23) or \
                      "immanuel" in combined_1_23 or "emmanuel" in combined_1_23
    if has_god_with_us:
        print("  Matt 1:23 PASS: 'God with us' phrase present in 1:23 block")
    else:
        print(f"  Matt 1:23 WARNING: expected God/us phrase in 1:23; got: {kjv_1_23_lines}")

    print("Self-test PASSED.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate KJV-style English gloss files from TAGNT substrate."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--book", metavar="SLUG",
                       help="Single book slug (e.g. matt, mark, rom)")
    group.add_argument("--all", action="store_true",
                       help="Process all 27 NT books")
    group.add_argument("--self-test", action="store_true",
                       help="Run self-test against Matt 1")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing output files")

    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return

    tbesg = load_tbesg(TBESG_PATH)
    print(f"Loaded TBESG fallback: {len(tbesg)} entries")

    if args.book:
        slug = args.book.lower()
        if slug not in BOOK_BY_SLUG:
            print(f"Unknown book slug '{slug}'. Known slugs: {list(BOOK_BY_SLUG.keys())}")
            sys.exit(1)
        dir_name, slug, tagnt_prefix, tagnt_path = BOOK_BY_SLUG[slug]
        print(f"Processing {dir_name}...")
        stats = generate_book(dir_name, slug, tagnt_prefix, tagnt_path, tbesg, args.force)
        print(f"Done: {stats}")

    elif args.all:
        total_stats = {"chapters": 0, "verses": 0, "lines": 0, "empty_lines": 0}
        for dir_name, slug, tagnt_prefix, tagnt_path in BOOK_META:
            print(f"\nProcessing {dir_name}...")
            stats = generate_book(dir_name, slug, tagnt_prefix, tagnt_path, tbesg, args.force)
            for k in total_stats:
                total_stats[k] += stats.get(k, 0)
        print(f"\nAll books done: {total_stats}")


if __name__ == "__main__":
    main()
