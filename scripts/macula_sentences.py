"""
macula_sentences.py — Sentence boundary detection from Macula Greek Lowfat XML.

Parses <sentence> elements in the SBLGNT Lowfat syntax trees to detect
sentence boundaries within verses. Used as a post-processing guard in the
colometric formatter to prevent merges that cross sentence boundaries.

The Lowfat XML wraps clauses in <sentence> elements. Words in different
<sentence> elements belong to different sentences.

Usage:
    from macula_sentences import get_word_sentence_ids, words_cross_sentence_boundary

    ids = get_word_sentence_ids('rev', 1, 5)
    # {1: 3, 2: 3, ..., 19: 3, 20: 4, 21: 4, ...}

    crossed = words_cross_sentence_boundary(
        "τῆς γῆς.", "Τῷ ἀγαπῶντι ἡμᾶς", 'rev', 1, 5)
    # True — these belong to different Macula sentences
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
# Text normalization (same as macula_valency.py)
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
# Per-book cache: { macula_id: { (chapter, verse): [ (word_pos, normalized, sentence_idx) ] } }
# ---------------------------------------------------------------------------

_sentence_cache: dict[str, dict[tuple[int, int], list[tuple[int, str, int]]]] = {}


def _parse_book_sentences(macula_id: str):
    """Parse a book XML and extract per-verse word-to-sentence mappings.

    Each word gets a sentence index (integer) that is unique within the book.
    Words in the same <sentence> element share the same index.
    """
    if macula_id in _sentence_cache:
        return

    filename = _MACULA_TO_FILE.get(macula_id)
    if not filename:
        _sentence_cache[macula_id] = {}
        return

    filepath = os.path.join(_LOWFAT_DIR, filename)
    if not os.path.exists(filepath):
        _sentence_cache[macula_id] = {}
        return

    tree = ET.parse(filepath)
    root = tree.getroot()

    verse_data: dict[tuple[int, int], list[tuple[int, str, int]]] = {}

    for sent_idx, sentence in enumerate(root.iter('sentence')):
        for w in sentence.iter('w'):
            ref = w.get('ref', '')
            _, ch, vs, pos = _parse_ref(ref)
            if ch is None:
                continue
            normalized = w.get('normalized', '') or (w.text or '')
            key = (ch, vs)
            if key not in verse_data:
                verse_data[key] = []
            verse_data[key].append((pos, normalized, sent_idx))

    # Sort each verse's words by position
    for key in verse_data:
        verse_data[key].sort(key=lambda x: x[0])

    _sentence_cache[macula_id] = verse_data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_word_sentence_ids(book_slug: str, chapter: int, verse: int) -> dict[int, int]:
    """Return {word_position: sentence_id} for all words in a verse.

    sentence_id is a sequential integer unique within the book — words sharing
    the same id belong to the same Macula <sentence>.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return {}

    _parse_book_sentences(macula_id)

    verse_words = _sentence_cache.get(macula_id, {}).get((chapter, verse), [])
    return {pos: sent_idx for pos, _norm, sent_idx in verse_words}


def words_cross_sentence_boundary(line1_text: str, line2_text: str,
                                   book_slug: str, chapter: int, verse: int) -> bool:
    """Check if merging line1 and line2 would cross a Macula sentence boundary.

    Matches words from both lines to the verse's Macula words, then checks
    whether the last word of line1 and the first word of line2 belong to
    different sentences.

    Returns False (safe to merge) if Macula data is unavailable or if
    either line can't be matched.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return False

    _parse_book_sentences(macula_id)

    verse_words = _sentence_cache.get(macula_id, {}).get((chapter, verse), [])
    if not verse_words:
        return False

    # Build normalized lookup: sequential match of line words to Macula words
    combined_text = line1_text.rstrip() + ' ' + line2_text.lstrip()
    all_words = combined_text.split()
    line1_word_count = len(line1_text.split())

    if line1_word_count == 0 or line1_word_count >= len(all_words):
        return False

    # Match all_words to verse_words sequentially
    matched_sids = _match_words_to_sentences(all_words, verse_words)

    if not matched_sids:
        return False

    # Check: does the sentence ID change at the line1/line2 boundary?
    # Find the last matched sentence ID in line1 and first in line2
    last_line1_sid = None
    for i in range(line1_word_count - 1, -1, -1):
        if matched_sids[i] is not None:
            last_line1_sid = matched_sids[i]
            break

    first_line2_sid = None
    for i in range(line1_word_count, len(matched_sids)):
        if matched_sids[i] is not None:
            first_line2_sid = matched_sids[i]
            break

    if last_line1_sid is None or first_line2_sid is None:
        return False

    return last_line1_sid != first_line2_sid


def find_sentence_boundary_in_line(line_text: str, book_slug: str,
                                    chapter: int, verse: int) -> Optional[int]:
    """Find the word index where a sentence boundary occurs within a line.

    Returns the index of the first word that belongs to a DIFFERENT sentence
    than the line's first word, or None if no boundary exists.

    Used by the post-processing splitter.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return None

    _parse_book_sentences(macula_id)

    verse_words = _sentence_cache.get(macula_id, {}).get((chapter, verse), [])
    if not verse_words:
        return None

    words = line_text.split()
    if len(words) < 2:
        return None

    matched_sids = _match_words_to_sentences(words, verse_words)

    # Find the first word whose sentence ID differs from the first matched word
    first_sid = None
    for sid in matched_sids:
        if sid is not None:
            first_sid = sid
            break

    if first_sid is None:
        return None

    for i, sid in enumerate(matched_sids):
        if sid is not None and sid != first_sid:
            return i

    return None


def _match_words_to_sentences(line_words: list[str],
                               verse_words: list[tuple[int, str, int]]
                               ) -> list[Optional[int]]:
    """Match line words to Macula verse words and return sentence IDs.

    Returns a list parallel to line_words where each element is either a
    sentence index or None if no match was found.
    """
    line_norms = [_normalize_for_match(w) for w in line_words]
    macula_norms = [_normalize_for_match(norm) for _pos, norm, _sid in verse_words]

    result: list[Optional[int]] = [None] * len(line_words)
    used = [False] * len(verse_words)

    for i, ln in enumerate(line_norms):
        if not ln:
            continue
        for j, mn in enumerate(macula_norms):
            if not used[j] and ln == mn:
                result[i] = verse_words[j][2]  # sentence_idx
                used[j] = True
                break

    return result


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Test Rev 1:5 — should show sentence boundary between γῆς and Τῷ
    print("=== Rev 1:5 word-to-sentence mapping ===")
    ids = get_word_sentence_ids('rev', 1, 5)
    if ids:
        macula_id = _SLUG_TO_MACULA['rev']
        verse_words = _sentence_cache[macula_id][(1, 5)]
        for pos, norm, sid in verse_words:
            print(f"  !{pos} {norm:20s} sentence={sid}")
    else:
        print("  No data found")

    print()
    print("=== Cross-sentence boundary test ===")
    crossed = words_cross_sentence_boundary(
        "τῆς γῆς.", "Τῷ ἀγαπῶντι ἡμᾶς", 'rev', 1, 5)
    print(f"  'τῆς γῆς.' + 'Τῷ ἀγαπῶντι ἡμᾶς' crosses boundary: {crossed}")

    same = words_cross_sentence_boundary(
        "ὁ μάρτυς ὁ πιστός", "ὁ πρωτότοκος τῶν νεκρῶν", 'rev', 1, 5)
    print(f"  'ὁ μάρτυς ὁ πιστός' + 'ὁ πρωτότοκος τῶν νεκρῶν' crosses boundary: {same}")

    print()
    print("=== In-line boundary detection ===")
    idx = find_sentence_boundary_in_line(
        "τῆς γῆς. Τῷ ἀγαπῶντι ἡμᾶς", 'rev', 1, 5)
    print(f"  Boundary at word index: {idx}")
    if idx is not None:
        words = "τῆς γῆς. Τῷ ἀγαπῶντι ἡμᾶς".split()
        print(f"  Line1: {' '.join(words[:idx])}")
        print(f"  Line2: {' '.join(words[idx:])}")
