"""
macula_wordgroups.py — Sub-clause word-group boundary detection from Macula Greek Lowfat XML.

Parses <wg> (word group) elements in the SBLGNT Lowfat syntax trees to detect
sub-clause phrase boundaries within verses. Used to split mega-lines (>80 chars)
at natural grammatical boundaries.

The Lowfat XML has nested <wg> elements:
  - <wg class="cl"> — clause-level groups (already used for clause splitting)
  - <wg class="np"> — noun phrases
  - <wg class="pp"> — prepositional phrases
  - <wg> without class — other phrase-level word groups

Sibling <wg> boundaries within a clause represent natural breath points where
a long line can be split without breaking grammatical cohesion.

Usage:
    from macula_wordgroups import find_wg_split_points_in_line

    points = find_wg_split_points_in_line(line_text, "rev", 18, 12)
    # Returns list of (word_index, depth) where word_index is into line.split()
    # and depth is how deep in the tree the boundary occurs (lower = more major)
"""

import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from typing import Optional

# ---------------------------------------------------------------------------
# Path and book mappings (shared with other macula_*.py modules)
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_LOWFAT_DIR = os.path.join(_REPO_ROOT, "research", "macula-greek", "SBLGNT", "lowfat")

_SLUG_TO_MACULA = {
    "matt": "MAT", "mark": "MRK", "luke": "LUK", "john": "JHN",
    "acts": "ACT", "rom": "ROM", "1cor": "1CO", "2cor": "2CO",
    "gal": "GAL", "eph": "EPH", "phil": "PHP", "col": "COL",
    "1thess": "1TH", "2thess": "2TH", "1tim": "1TI", "2tim": "2TI",
    "titus": "TIT", "phlm": "PHM", "heb": "HEB", "jas": "JAS",
    "1pet": "1PE", "2pet": "2PE", "1john": "1JN", "2john": "2JN",
    "3john": "3JN", "jude": "JUD", "rev": "REV",
}

_MACULA_TO_FILE = {
    "MAT": "01-matthew.xml", "MRK": "02-mark.xml",
    "LUK": "03-luke.xml", "JHN": "04-john.xml",
    "ACT": "05-acts.xml", "ROM": "06-romans.xml",
    "1CO": "07-1corinthians.xml", "2CO": "08-2corinthians.xml",
    "GAL": "09-galatians.xml", "EPH": "10-ephesians.xml",
    "PHP": "11-philippians.xml", "COL": "12-colossians.xml",
    "1TH": "13-1thessalonians.xml", "2TH": "14-2thessalonians.xml",
    "1TI": "15-1timothy.xml", "2TI": "16-2timothy.xml",
    "TIT": "17-titus.xml", "PHM": "18-philemon.xml",
    "HEB": "19-hebrews.xml", "JAS": "20-james.xml",
    "1PE": "21-1peter.xml", "2PE": "22-2peter.xml",
    "1JN": "23-1john.xml", "2JN": "24-2john.xml",
    "3JN": "25-3john.xml", "JUD": "26-jude.xml",
    "REV": "27-revelation.xml",
}

# ---------------------------------------------------------------------------
# Text normalization (same as macula_sentences.py)
# ---------------------------------------------------------------------------

_STRIP_CHARS = str.maketrans('', '', '.,;·\u0387\u00B7\u2019\u02BC')


def _normalize_for_match(text: str) -> str:
    """Normalize a Greek word for matching between our text and Macula."""
    text = unicodedata.normalize('NFC', text)
    text = text.translate(_STRIP_CHARS)
    text = text.replace('\u02bc', '').replace('\u2019', '')
    text = text.replace('\u02bd', '').replace('\u1fbd', '')
    text = text.replace("'", '').replace('\u2032', '')
    return text.strip()


# ---------------------------------------------------------------------------
# Reference parsing
# ---------------------------------------------------------------------------

_REF_PATTERN = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_ref(ref_str):
    """Parse 'REV 1:5!20' -> (book, chapter, verse, word_pos)."""
    m = _REF_PATTERN.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


# ---------------------------------------------------------------------------
# Per-book cache: { macula_id: { (ch, vs): verse_word_list } }
# verse_word_list = [ (word_pos, normalized_text) ]
#
# Plus a separate boundary cache:
# { macula_id: { (ch, vs): [ (word_pos, depth) ] } }
# where word_pos is the position of the FIRST word after a sibling-wg boundary
# and depth is the tree depth at which the boundary occurs.
# ---------------------------------------------------------------------------

_word_cache: dict[str, dict[tuple[int, int], list[tuple[int, str]]]] = {}
_boundary_cache: dict[str, dict[tuple[int, int], list[tuple[int, int]]]] = {}


def _collect_boundaries(element, depth=0):
    """Recursively walk the tree and find all sibling-wg boundaries.

    At each level where an element has multiple <wg> children, we record
    a boundary at the word position of each <wg> child after the first.

    Returns: (list_of_words, list_of_boundaries)
      words: [(ref, normalized), ...] in document order
      boundaries: [(word_position_in_list, depth), ...]
    """
    all_words = []
    all_boundaries = []

    children = list(element)
    wg_children = [ch for ch in children if ch.tag == 'wg']

    # Check if this element has multiple wg children — those boundaries matter
    has_sibling_boundaries = len(wg_children) > 1

    wg_index = 0
    for child in children:
        if child.tag == 'w':
            ref = child.get('ref', '')
            normalized = child.get('normalized', '') or (child.text or '')
            all_words.append((ref, normalized))
        elif child.tag == 'wg':
            word_offset = len(all_words)
            sub_words, sub_boundaries = _collect_boundaries(child, depth + 1)

            # If this is the 2nd+ sibling wg, record boundary at its first word
            if has_sibling_boundaries and wg_index > 0 and sub_words:
                # The boundary is at the position of the first word of this wg
                boundary_pos = word_offset  # relative to current collection
                all_boundaries.append((boundary_pos, depth))

            all_words.extend(sub_words)
            # Adjust sub-boundary positions by offset
            for bpos, bdepth in sub_boundaries:
                all_boundaries.append((word_offset + bpos, bdepth))

            wg_index += 1
        elif child.tag in ('p', 'milestone'):
            continue
        else:
            # Other elements — recurse
            sub_words, sub_boundaries = _collect_boundaries(child, depth + 1)
            word_offset = len(all_words)
            all_words.extend(sub_words)
            for bpos, bdepth in sub_boundaries:
                all_boundaries.append((word_offset + bpos, bdepth))

    return all_words, all_boundaries


def _parse_book_wordgroups(macula_id: str):
    """Parse a book XML and extract per-verse word and boundary data."""
    if macula_id in _word_cache:
        return

    filename = _MACULA_TO_FILE.get(macula_id)
    if not filename:
        _word_cache[macula_id] = {}
        _boundary_cache[macula_id] = {}
        return

    filepath = os.path.join(_LOWFAT_DIR, filename)
    if not os.path.exists(filepath):
        _word_cache[macula_id] = {}
        _boundary_cache[macula_id] = {}
        return

    tree = ET.parse(filepath)
    root = tree.getroot()

    word_data: dict[tuple[int, int], list[tuple[int, str]]] = {}
    bnd_data: dict[tuple[int, int], list[tuple[int, int]]] = {}

    for sentence in root.iter('sentence'):
        words, boundaries = _collect_boundaries(sentence, depth=0)

        # Group words and boundaries by verse
        # First, parse all word refs
        parsed_words = []
        for ref, norm in words:
            _, ch, vs, pos = _parse_ref(ref)
            parsed_words.append((ch, vs, pos, _normalize_for_match(norm)))

        for i, (ch, vs, pos, norm) in enumerate(parsed_words):
            if ch is None:
                continue
            key = (ch, vs)
            if key not in word_data:
                word_data[key] = []
            word_data[key].append((pos, norm))

        # Map boundary positions (sentence-relative word index) to verse-relative
        # word positions
        for bnd_idx, depth in boundaries:
            if bnd_idx < len(parsed_words):
                ch, vs, pos, _ = parsed_words[bnd_idx]
                if ch is not None:
                    key = (ch, vs)
                    if key not in bnd_data:
                        bnd_data[key] = []
                    bnd_data[key].append((pos, depth))

    # Sort word data by position
    for key in word_data:
        word_data[key].sort(key=lambda x: x[0])
    # Sort boundary data by position
    for key in bnd_data:
        bnd_data[key].sort(key=lambda x: x[0])

    _word_cache[macula_id] = word_data
    _boundary_cache[macula_id] = bnd_data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_wg_split_points_in_line(line_text: str, book_slug: str,
                                  chapter: int, verse: int
                                  ) -> list[tuple[int, int]]:
    """Find word indices within line_text where word-group boundaries occur.

    Returns a list of (word_index, depth) tuples, where:
      - word_index is 0-based into line_text.split()
      - depth is the tree depth of the boundary (lower = more significant)

    Sorted by depth ascending (most significant first), then by closeness
    to midpoint.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return []

    _parse_book_wordgroups(macula_id)

    verse_words = _word_cache.get(macula_id, {}).get((chapter, verse), [])
    verse_boundaries = _boundary_cache.get(macula_id, {}).get((chapter, verse), [])
    if not verse_words or not verse_boundaries:
        return []

    words = line_text.split()
    if len(words) < 2:
        return []

    # Match line words to Macula words sequentially
    line_norms = [_normalize_for_match(w) for w in words]
    macula_norms = [(pos, norm) for pos, norm in verse_words]

    # matched_pos[i] = Macula word_pos for line word i, or None
    matched_pos: list[Optional[int]] = [None] * len(words)
    used = [False] * len(macula_norms)

    for i, ln in enumerate(line_norms):
        if not ln:
            continue
        for j, (pos, mn) in enumerate(macula_norms):
            if not used[j] and ln == mn:
                matched_pos[i] = pos
                used[j] = True
                break

    # Build set of Macula word positions that are boundary points
    boundary_at_pos: dict[int, int] = {}  # macula_pos -> min_depth
    for bpos, depth in verse_boundaries:
        if bpos not in boundary_at_pos or depth < boundary_at_pos[bpos]:
            boundary_at_pos[bpos] = depth

    # Find which line-word indices correspond to boundary positions
    result = []
    for i, mpos in enumerate(matched_pos):
        if mpos is not None and mpos in boundary_at_pos:
            result.append((i, boundary_at_pos[mpos]))

    return result


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Test Rev 18:12 — should show multiple word-group boundaries
    print("=== Rev 18:12 split points ===")
    data = find_wg_split_points_in_line(
        "γόμον χρυσοῦ καὶ ἀργύρου καὶ λίθου τιμίου καὶ μαργαριτῶν "
        "καὶ βυσσίνου καὶ πορφύρας καὶ σιρικοῦ καὶ κοκκίνου "
        "καὶ πᾶν ξύλον θύϊνον καὶ πᾶν σκεῦος ἐλεφάντινον",
        'rev', 18, 12)
    for idx, depth in sorted(data, key=lambda x: x[0]):
        test_words = ("γόμον χρυσοῦ καὶ ἀργύρου καὶ λίθου τιμίου καὶ μαργαριτῶν "
                      "καὶ βυσσίνου καὶ πορφύρας καὶ σιρικοῦ καὶ κοκκίνου "
                      "καὶ πᾶν ξύλον θύϊνον καὶ πᾶν σκεῦος ἐλεφάντινον").split()
        word_at = test_words[idx] if idx < len(test_words) else '?'
        print(f"  word_idx={idx} depth={depth} word={word_at}")

    print()

    # Test Eph 1:3
    print("=== Eph 1:3 split points ===")
    test = "Εὐλογητὸς ὁ θεὸς καὶ πατὴρ τοῦ κυρίου ἡμῶν Ἰησοῦ Χριστοῦ"
    data = find_wg_split_points_in_line(test, 'eph', 1, 3)
    for idx, depth in sorted(data, key=lambda x: x[0]):
        print(f"  word_idx={idx} depth={depth} word={test.split()[idx]}")
