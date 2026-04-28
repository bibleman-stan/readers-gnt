"""
macula_clauses.py — Extract clause boundaries from Macula Greek Lowfat XML.

Parses the SBLGNT Lowfat syntax trees to identify clause boundaries
for use in colometric line-breaking. Provides per-verse clause lists
with metadata about participles and genitive absolutes.

Usage:
    from macula_clauses import get_verse_clauses, get_chapter_clauses

    clauses = get_chapter_clauses('acts', 1)
    for v, cls in sorted(clauses.items()):
        print(f"  {v}: {cls}")
"""

import os
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Path to Macula Lowfat XML files
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
_LOWFAT_DIR = os.path.join(_REPO_ROOT, "research", "macula-greek", "SBLGNT", "lowfat")

# ---------------------------------------------------------------------------
# Book abbreviation mappings
# ---------------------------------------------------------------------------

_MACULA_TO_SLUG = {
    "MAT": "matt", "MRK": "mark", "LUK": "luke", "JHN": "john",
    "ACT": "acts", "ROM": "rom", "1CO": "1cor", "2CO": "2cor",
    "GAL": "gal", "EPH": "eph", "PHP": "phil", "COL": "col",
    "1TH": "1thess", "2TH": "2thess", "1TI": "1tim", "2TI": "2tim",
    "TIT": "titus", "PHM": "phlm", "HEB": "heb", "JAS": "jas",
    "1PE": "1pet", "2PE": "2pet", "1JN": "1john", "2JN": "2john",
    "3JN": "3john", "JUD": "jude", "REV": "rev",
}

_SLUG_TO_MACULA = {v: k for k, v in _MACULA_TO_SLUG.items()}

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
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ClauseInfo:
    """A single clause extracted from the syntax tree."""
    text: str
    words: list          # [(ref, normalized_text), ...] in surface order
    has_participle: bool = False
    is_genitive_absolute: bool = False
    clause_type: str = ""   # clauseType attribute if present
    rule: str = ""          # rule attribute if present

    def __repr__(self):
        ga = " [GenAbs]" if self.is_genitive_absolute else ""
        ptc = " [Ptc]" if self.has_participle and not self.is_genitive_absolute else ""
        return f"ClauseInfo({self.text!r}{ptc}{ga})"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

_REF_PATTERN = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_ref(ref_str):
    """Parse 'ACT 1:1!8' -> (book, chapter, verse, word_pos)."""
    m = _REF_PATTERN.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


def _word_sort_key(ref_str):
    """Sort key for surface order: (chapter, verse, word_position)."""
    _, ch, vs, pos = _parse_ref(ref_str)
    return (ch or 0, vs or 0, pos or 0)


# ---------------------------------------------------------------------------
# Core extraction: linearize the tree into an ordered sequence of
# (word_info, clause_id) pairs, then group by clause_id.
#
# The approach:
#   - Walk the tree depth-first.
#   - Track the innermost enclosing <wg class="cl"> for each word.
#   - Words whose innermost clause ancestor is the same belong together.
#   - Words with NO clause ancestor get prepended to the next clause
#     (they are typically conjunctions introducing the clause).
# ---------------------------------------------------------------------------

def _linearize_words(element, clause_stack=None):
    """
    Yield (w_element, clause_element_or_None) for every <w> in document order.
    clause_element is the innermost <wg class="cl"> ancestor, or None.
    """
    if clause_stack is None:
        clause_stack = []

    if element.tag == 'w':
        current_clause = clause_stack[-1] if clause_stack else None
        yield (element, current_clause)
    else:
        is_clause = (element.tag == 'wg' and element.get('class') == 'cl')
        if is_clause:
            clause_stack.append(element)
        for child in element:
            yield from _linearize_words(child, clause_stack)
        if is_clause:
            clause_stack.pop()


def _detect_genitive_absolute(word_elements):
    """Genitive absolute = genitive participle + genitive noun/pronoun."""
    has_gen_ptc = False
    has_gen_noun = False
    for w in word_elements:
        case = w.get('case', '')
        if w.get('mood') == 'participle' and case == 'genitive':
            has_gen_ptc = True
        if case == 'genitive' and w.get('class') in ('noun', 'pron'):
            has_gen_noun = True
    return has_gen_ptc and has_gen_noun


def _has_participle(word_elements):
    return any(w.get('mood') == 'participle' for w in word_elements)


def _build_clause_infos(root):
    """
    Build a list of ClauseInfo from the XML tree.

    Returns list of ClauseInfo in document order.
    """
    # Step 1: linearize all words with their clause assignment
    word_clause_pairs = list(_linearize_words(root))

    if not word_clause_pairs:
        return []

    # Step 2: group into runs of same clause_element.
    # Words with clause=None are "floating" (usually conjunctions).
    # Attach them to the next clause they precede.
    #
    # We do this in two passes:
    #   Pass 1: group into raw segments (clause_elem, [words])
    #   Pass 2: merge None-segments into following clause segment

    raw_segments = []  # (clause_elem_or_None, [w_element, ...])
    current_clause = 'SENTINEL'  # unique object to detect first
    current_words = []

    for w_elem, cl_elem in word_clause_pairs:
        cl_id = id(cl_elem) if cl_elem is not None else None
        prev_id = id(current_clause) if current_clause not in ('SENTINEL', None) else current_clause

        if current_clause == 'SENTINEL':
            current_clause = cl_elem
            current_words = [w_elem]
        elif cl_id == prev_id:
            current_words.append(w_elem)
        else:
            raw_segments.append((current_clause, current_words))
            current_clause = cl_elem
            current_words = [w_elem]

    if current_words:
        raw_segments.append((current_clause, current_words))

    # Pass 2: merge None (floating) segments into the next clause segment
    merged_segments = []
    pending_float = []

    for cl_elem, words in raw_segments:
        if cl_elem is None:
            pending_float.extend(words)
        else:
            merged_words = pending_float + words
            pending_float = []
            merged_segments.append((cl_elem, merged_words))

    # If there are trailing floating words, attach to last clause
    if pending_float and merged_segments:
        cl_elem, words = merged_segments[-1]
        merged_segments[-1] = (cl_elem, words + pending_float)
    elif pending_float:
        # Entire tree has no clauses — make one pseudo-clause
        merged_segments.append((None, pending_float))

    # Step 3: build ClauseInfo objects
    clause_infos = []
    for cl_elem, words in merged_segments:
        word_data = []
        for w in words:
            ref = w.get('ref', '')
            text = w.get('normalized', '') or (w.text or '')
            word_data.append((ref, text, w))

        # Sort by surface order
        word_data.sort(key=lambda x: _word_sort_key(x[0]))

        clause_text = ' '.join(t for _, t, _ in word_data)
        w_elems = [w for _, _, w in word_data]

        ci = ClauseInfo(
            text=clause_text,
            words=[(ref, text) for ref, text, _ in word_data],
            has_participle=_has_participle(w_elems),
            is_genitive_absolute=_detect_genitive_absolute(w_elems),
            clause_type=(cl_elem.get('clauseType', '') if cl_elem is not None else ''),
            rule=(cl_elem.get('rule', '') if cl_elem is not None else ''),
        )
        clause_infos.append(ci)

    return clause_infos


# ---------------------------------------------------------------------------
# Book-level parsing with cache
# ---------------------------------------------------------------------------

_book_cache: dict[str, dict[tuple[int, int], list[ClauseInfo]]] = {}


def _parse_book(macula_id):
    """Parse a book XML and return {(chapter, verse): [ClauseInfo, ...]}."""
    if macula_id in _book_cache:
        return _book_cache[macula_id]

    filename = _MACULA_TO_FILE.get(macula_id)
    if not filename:
        raise ValueError(f"Unknown Macula book ID: {macula_id}")

    filepath = os.path.join(_LOWFAT_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Macula XML file not found: {filepath}")

    tree = ET.parse(filepath)
    root = tree.getroot()

    clause_infos = _build_clause_infos(root)

    # Assign clauses to verses
    verse_clauses: dict[tuple[int, int], list[ClauseInfo]] = defaultdict(list)

    for ci in clause_infos:
        if not ci.words:
            continue
        verses_in_clause = set()
        for ref, _ in ci.words:
            _, ch, vs, _ = _parse_ref(ref)
            if ch is not None and vs is not None:
                verses_in_clause.add((ch, vs))
        for cv in verses_in_clause:
            verse_clauses[cv].append(ci)

    # Sort clauses within each verse by first word position in that verse
    for cv in verse_clauses:
        ch, vs = cv
        verse_clauses[cv].sort(
            key=lambda ci: _first_word_pos_in_verse(ci, ch, vs)
        )

    result = dict(verse_clauses)
    _book_cache[macula_id] = result
    return result


def _first_word_pos_in_verse(clause_info, chapter, verse):
    """Position of first word of clause within a specific verse."""
    for ref, _ in clause_info.words:
        _, ch, vs, pos = _parse_ref(ref)
        if ch == chapter and vs == verse:
            return pos or 0
    return 9999


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _resolve_book(book_abbrev):
    """Resolve a book slug or Macula ID to a Macula ID."""
    upper = book_abbrev.upper()
    if upper in _MACULA_TO_FILE:
        return upper
    lower = book_abbrev.lower()
    if lower in _SLUG_TO_MACULA:
        return _SLUG_TO_MACULA[lower]
    raise ValueError(
        f"Unknown book abbreviation: {book_abbrev!r}. "
        f"Use a project slug (e.g., 'acts', 'mark') or Macula ID (e.g., 'ACT', 'MRK')."
    )


def get_verse_clauses(book_abbrev: str, chapter: int, verse: int) -> list[str]:
    """
    Return ordered list of clause texts for a given verse.

    Args:
        book_abbrev: Project slug ('acts', 'mark') or Macula ID ('ACT', 'MRK')
        chapter: Chapter number
        verse: Verse number

    Returns:
        List of clause text strings in surface-text order.
    """
    macula_id = _resolve_book(book_abbrev)
    book_data = _parse_book(macula_id)
    clauses = book_data.get((chapter, verse), [])
    return [c.text for c in clauses]


def get_verse_clauses_detailed(book_abbrev: str, chapter: int, verse: int) -> list[ClauseInfo]:
    """
    Return ordered list of ClauseInfo objects for a given verse.

    Like get_verse_clauses but includes metadata (participles, gen. absolutes).
    """
    macula_id = _resolve_book(book_abbrev)
    book_data = _parse_book(macula_id)
    return book_data.get((chapter, verse), [])


def get_chapter_clauses(book_abbrev: str, chapter: int) -> dict[int, list[str]]:
    """
    Return {verse_num: [clause_text, ...]} for all verses in a chapter.

    Args:
        book_abbrev: Project slug ('acts', 'mark') or Macula ID ('ACT', 'MRK')
        chapter: Chapter number

    Returns:
        Dict mapping verse number to list of clause text strings.
    """
    macula_id = _resolve_book(book_abbrev)
    book_data = _parse_book(macula_id)
    result = {}
    for (ch, vs), clauses in book_data.items():
        if ch == chapter:
            result[vs] = [c.text for c in clauses]
    return result


def get_chapter_clauses_detailed(book_abbrev: str, chapter: int) -> dict[int, list[ClauseInfo]]:
    """
    Return {verse_num: [ClauseInfo, ...]} for all verses in a chapter.

    Like get_chapter_clauses but includes metadata.
    """
    macula_id = _resolve_book(book_abbrev)
    book_data = _parse_book(macula_id)
    result = {}
    for (ch, vs), clauses in book_data.items():
        if ch == chapter:
            result[vs] = clauses
    return result


def clear_cache():
    """Clear the parsed book cache."""
    _book_cache.clear()


# ---------------------------------------------------------------------------
# CLI entry point for quick testing
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    book = sys.argv[1] if len(sys.argv) > 1 else 'acts'
    chapter = int(sys.argv[2]) if len(sys.argv) > 2 else 1

    print(f"Clauses for {book} {chapter}:\n")
    clauses = get_chapter_clauses_detailed(book, chapter)
    for vs in sorted(clauses.keys()):
        cls = clauses[vs]
        print(f"  {chapter}:{vs}")
        for i, c in enumerate(cls, 1):
            flags = []
            if c.is_genitive_absolute:
                flags.append("GenAbs")
            elif c.has_participle:
                flags.append("Ptc")
            if c.clause_type:
                flags.append(c.clause_type)
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            print(f"    {i}. {c.text}{flag_str}")
        print()
