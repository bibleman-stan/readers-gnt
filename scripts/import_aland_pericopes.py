#!/usr/bin/env python3
"""
import_aland_pericopes.py — Parse the Aland pericope table from
Stan's vault and emit a canonical JSON file for the synoptic
analysis infrastructure.

Source: ANT Pericopae.md (in my_brain vault), 367 numbered pericopes
with parallel references across Matt, Mark, Luke, John.

Each row of the source table is:

    | [[ANT-NNN]] | [[wiki-link|Title]] | Mt. CC.VV-VV; Mk. CC.VV; ... |

Reference grammar (from observation of the table):

    ref      := book_ref (SEP book_ref)*
    book_ref := BOOK '.' range (SEP range)*         // book marker once, ranges follow
               | range                               // continuation of previous book
    range    := VERSE ('-' VERSE)?
    VERSE    := chapter? '.' verse_num suffix?      // chapter optional on continuation
    BOOK     := 'Mt' | 'Mk' | 'Lk' | 'Jn'
    SEP      := ';' | ','
    suffix   := 'a' | 'b' | 'c' (half-verse markers, rare)

Edge cases handled:
- Leading zeros (01.01) → stripped
- Cross-chapter ranges (Mt. 04.24-05.2) → two chapter/verse boundaries
- Half-verse suffixes (Lk. 04.14b-15) → captured as strings
- Duplicate pericope numbering (ANT-050|ANT-077 means "display 077, link 050")
- Trailing ranges without a book marker (continuation of previous book)

Output: data/synoptic/aland_pericopes.json

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/import_aland_pericopes.py
"""
import os
import re
import json
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SOURCE_FILE = r"C:\vaults-nano\my_brain\05-Bible\Passages\Pericopae\ANT Pericopae.md"
OUTPUT_PATH = os.path.join(REPO_ROOT, "data", "synoptic", "aland_pericopes.json")

BOOK_MAP = {
    "Mt": "matt", "Mk": "mark", "Lk": "luke", "Jn": "john",
}

# Match a table row for an ANT entry. Captures:
#   1: ANT number (possibly with pipe-alias like "ANT-050|ANT-077")
#   2: title (possibly with pipe-alias)
#   3: references column
_ROW_RE = re.compile(
    r'^\|\s*\[\[(ANT-[\d|A-Z\-]+)\]\]\s*\|\s*\[\[([^\]]+)\]\]\s*\|\s*(.*?)\s*\|\s*$'
)

# Match a book marker: Mt. / Mk. / Lk. / Jn.
_BOOK_RE = re.compile(r'\b(Mt|Mk|Lk|Jn)\.')

# Match a chapter.verse(-chapter.verse)? reference with optional a/b/c suffixes
_REF_RE = re.compile(
    r'(\d+)\.(\d+)([a-c])?(?:-(?:(\d+)\.)?(\d+)([a-c])?)?'
)


def _normalize_ant_cell(raw):
    """Turn 'ANT-050|ANT-077' into {primary: 'ANT-050', display: 'ANT-077'}.
    For simple 'ANT-020', returns {primary: 'ANT-020', display: 'ANT-020'}."""
    if "|" in raw:
        parts = raw.split("|", 1)
        return {"primary": parts[0].strip(), "display": parts[1].strip()}
    return {"primary": raw.strip(), "display": raw.strip()}


def _normalize_title_cell(raw):
    """Unwrap wiki-link notation. [[ANT-050|Occasion of the Sermon]] -> 'Occasion of the Sermon'.
    [[The Temptation]] -> 'The Temptation'."""
    raw = raw.strip()
    if "|" in raw:
        return raw.split("|", 1)[1].strip()
    return raw.strip()


def _parse_refs(refs_text):
    """Parse the references column into {book: [ranges]}.

    Returns a dict with keys matt/mark/luke/john mapping to lists of
    range dicts. Each range dict has:
        chapter: int           (start chapter)
        start: int             (start verse)
        end_chapter: int       (end chapter, same as start if within one chapter)
        end: int               (end verse, same as start if single verse)
        start_suffix: str      ('a'/'b'/'c' or '')
        end_suffix: str        ('a'/'b'/'c' or '')
    """
    result = {"matt": [], "mark": [], "luke": [], "john": []}
    # Split on semicolons (primary separator)
    chunks = [c.strip() for c in refs_text.split(";") if c.strip()]

    current_book = None  # tracks book for continuations like "Lk. 09.2-5; 10.3"
    for chunk in chunks:
        # Does this chunk start with a book marker?
        m = _BOOK_RE.match(chunk)
        if m:
            current_book = BOOK_MAP[m.group(1)]
            # Strip the book marker and following "."
            chunk_body = chunk[m.end():].strip()
        else:
            # Continuation — use current_book
            chunk_body = chunk

        if current_book is None:
            # Can't parse — skip
            continue

        # Parse all ranges within the chunk. The chunk may contain
        # multiple ranges separated by commas or additional spaces.
        # We split on commas first, then run the regex on each piece.
        pieces = [p.strip() for p in chunk_body.split(",") if p.strip()]
        for piece in pieces:
            m = _REF_RE.search(piece)
            if not m:
                continue
            start_ch = int(m.group(1))
            start_vs = int(m.group(2))
            start_suffix = m.group(3) or ""
            end_ch_str = m.group(4)
            end_vs_str = m.group(5)
            end_suffix = m.group(6) or ""

            if end_vs_str is None:
                # Single verse
                end_ch = start_ch
                end_vs = start_vs
                end_suffix = start_suffix
            else:
                end_vs = int(end_vs_str)
                end_ch = int(end_ch_str) if end_ch_str else start_ch

            result[current_book].append({
                "chapter": start_ch,
                "start": start_vs,
                "start_suffix": start_suffix,
                "end_chapter": end_ch,
                "end": end_vs,
                "end_suffix": end_suffix,
            })
    return result


def _tradition_type(parallels):
    """Classify the pericope by which books are present."""
    present = [b for b in ("matt", "mark", "luke", "john") if parallels[b]]
    present_set = set(present)
    if len(present) == 1:
        return f"single_{present[0]}"
    if present_set == {"matt", "mark", "luke", "john"}:
        return "quadruple"
    if present_set == {"matt", "mark", "luke"}:
        return "triple_synoptic"
    if "john" in present_set:
        # Some combination with John
        others = sorted(present_set - {"john"})
        return "john_plus_" + "_".join(others)
    # Double tradition among synoptics
    if present_set == {"matt", "mark"}:
        return "matt_mark"
    if present_set == {"matt", "luke"}:
        return "matt_luke"  # Q candidate
    if present_set == {"mark", "luke"}:
        return "mark_luke"
    return "other"


def parse_file(path):
    pericopes = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            # Unescape the markdown-table pipe escapes (\|) so wiki-link
            # aliases inside [[...]] can be parsed. Source has
            # [[ANT-050\|ANT-077]] which means "link to ANT-050, display
            # as ANT-077" — after unescaping, the | is available for
            # _normalize_ant_cell to split on.
            line = line.replace("\\|", "|")
            m = _ROW_RE.match(line)
            if not m:
                continue
            ant_cell = _normalize_ant_cell(m.group(1))
            title = _normalize_title_cell(m.group(2))
            refs_text = m.group(3)
            parallels = _parse_refs(refs_text)
            present_in = [b for b in ("matt", "mark", "luke", "john") if parallels[b]]
            pericopes.append({
                "aland_id": ant_cell["display"],
                "primary_id": ant_cell["primary"],
                "title": title,
                "parallels": parallels,
                "present_in": present_in,
                "tradition_type": _tradition_type(parallels),
                "refs_raw": refs_text,
            })
    return pericopes


def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"ERROR: source file not found: {SOURCE_FILE}")
        sys.exit(1)

    pericopes = parse_file(SOURCE_FILE)
    print(f"Parsed {len(pericopes)} pericopes")

    # Bucket by tradition type for sanity
    from collections import Counter
    tt = Counter(p["tradition_type"] for p in pericopes)
    for t, n in sorted(tt.items()):
        print(f"  {t}: {n}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump({
            "source": "Kurt Aland, Synopsis Quattuor Evangeliorum, via my_brain/Pericopae/ANT Pericopae.md",
            "pericope_count": len(pericopes),
            "pericopes": pericopes,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
