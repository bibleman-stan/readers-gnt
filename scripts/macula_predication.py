"""
macula_predication.py — Complete predication test using Macula syntax tree hierarchy.

Checks whether a colometric line contains a complete predication — a verbal
element that governs (not is governed by) another verb. This is the fundamental
structural test for colometric line completeness.

The principle: every line must contain either:
  1. A finite verb that governs its own predication
  2. A participle whose governing finite verb is on the SAME line
  3. An implied copula (Macula role=p predicate) — verbless but complete
  4. A standalone unit (vocative, exclamation, etc.)

If a line has only a participle and its governing finite verb is on a DIFFERENT
line, the predication is incomplete and the line should merge forward.

Usage:
    from macula_predication import check_line_completeness, PredicationResult

    result = check_line_completeness("οἱ δὲ προσαπειλησάμενοι", "acts", 4, 21)
    if not result.complete:
        print(f"Merge: {result.reason}")
"""

import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Paths and mappings
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

_FINITE_MOODS = frozenset({'indicative', 'subjunctive', 'imperative', 'optative'})

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PredicationResult:
    """Result of a predication completeness check for a single line."""
    complete: bool = True
    reason: str = ""
    participle_text: str = ""    # the participle that lacks a governor on this line
    governor_text: str = ""      # the governing finite verb (on another line)


@dataclass
class WordInfo:
    """A word from the Macula XML with tree-position info."""
    ref: str               # e.g. "ACT 4:21!3"
    word_pos: int          # the !N position within the verse
    normalized: str        # normalized form
    mood: str              # participle, indicative, etc.
    role: str              # s, v, o, p, adv, etc.
    word_class: str        # verb, noun, conj, etc.
    xml_id: str            # xml:id attribute for identity
    element: object        # the <w> ET element itself


# ---------------------------------------------------------------------------
# Text normalization for matching (reused from macula_valency.py)
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
# Ref parsing
# ---------------------------------------------------------------------------

_REF_PATTERN = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_ref(ref_str):
    """Parse 'ACT 1:1!8' -> (book, chapter, verse, word_pos)."""
    m = _REF_PATTERN.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


# ---------------------------------------------------------------------------
# Book-level parsing with cache
# ---------------------------------------------------------------------------

# Cache: macula_id -> (tree_root, parent_map, verse_words)
_book_cache: dict[str, tuple] = {}


def _parse_book(macula_id: str):
    """Parse a book XML and build the parent map and verse-word index.

    Returns (root, parent_map, verse_words) where:
      - root: the ET root element
      - parent_map: {child_element: parent_element} for tree traversal
      - verse_words: {(chapter, verse): [WordInfo, ...]} sorted by word_pos
    """
    if macula_id in _book_cache:
        return _book_cache[macula_id]

    filename = _MACULA_TO_FILE.get(macula_id)
    if not filename:
        return None, None, None

    filepath = os.path.join(_LOWFAT_DIR, filename)
    if not os.path.exists(filepath):
        return None, None, None

    tree = ET.parse(filepath)
    root = tree.getroot()

    # Build parent map for upward tree traversal
    parent_map = {child: parent for parent in root.iter() for child in parent}

    # Build verse-word index
    verse_words: dict[tuple[int, int], list[WordInfo]] = {}

    for w_elem in root.iter('w'):
        ref = w_elem.get('ref', '')
        _, ch, vs, pos = _parse_ref(ref)
        if ch is None:
            continue

        wi = WordInfo(
            ref=ref,
            word_pos=pos or 0,
            normalized=w_elem.get('normalized', '') or (w_elem.text or ''),
            mood=w_elem.get('mood', ''),
            role=w_elem.get('role', ''),
            word_class=w_elem.get('class', ''),
            xml_id=w_elem.get('{http://www.w3.org/XML/1998/namespace}id', ''),
            element=w_elem,
        )

        key = (ch, vs)
        if key not in verse_words:
            verse_words[key] = []
        verse_words[key].append(wi)

    # Sort by word position
    for key in verse_words:
        verse_words[key].sort(key=lambda wi: wi.word_pos)

    result = (root, parent_map, verse_words)
    _book_cache[macula_id] = result
    return result


# ---------------------------------------------------------------------------
# Tree traversal: find governing finite verb for a participle
# ---------------------------------------------------------------------------

def _find_innermost_clause(w_elem, parent_map):
    """Walk up from a <w> element to find its innermost enclosing <wg class='cl'>."""
    current = w_elem
    while current in parent_map:
        current = parent_map[current]
        if current.tag == 'wg' and current.get('class') == 'cl':
            return current
    return None


def _find_finite_verb_in_element(elem, exclude_xml_ids=None):
    """Search an element (and descendants) for a <w> with finite mood.

    Returns the first finite verb <w> element found, or None.
    Excludes words in exclude_xml_ids (to avoid matching the participle itself).
    """
    if exclude_xml_ids is None:
        exclude_xml_ids = set()

    for w in elem.iter('w'):
        mood = w.get('mood', '')
        if mood in _FINITE_MOODS:
            xml_id = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
            if xml_id not in exclude_xml_ids:
                return w
    return None


def _find_governing_finite_verb(w_elem, parent_map):
    """For a participle <w>, find its governing finite verb by walking up the tree.

    Algorithm:
    1. Find the participle's innermost enclosing clause
    2. Walk up to the parent of that clause
    3. Search the parent (and higher ancestors) for a finite verb
       that is NOT inside the participle's own clause

    Returns the governing finite verb <w> element, or None.
    """
    ptc_xml_id = w_elem.get('{http://www.w3.org/XML/1998/namespace}id', '')

    # Step 1: find innermost clause containing this participle
    inner_clause = _find_innermost_clause(w_elem, parent_map)
    if inner_clause is None:
        return None

    # Step 2: walk up from the inner clause to find ancestor elements
    # that contain a finite verb
    current = inner_clause
    while current in parent_map:
        parent = parent_map[current]

        # Search the parent for finite verbs, but skip words inside our
        # inner_clause (and its descendants) — we want verbs OUTSIDE our clause
        # The simplest approach: search the parent, then check that the found
        # verb is not inside the inner_clause.

        # Collect xml:ids of all words inside the inner clause (to exclude)
        inner_word_ids = set()
        for w in inner_clause.iter('w'):
            wid = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
            if wid:
                inner_word_ids.add(wid)

        # Search parent for a finite verb not in the inner clause
        finite_verb = _find_finite_verb_in_element(parent, exclude_xml_ids=inner_word_ids)
        if finite_verb is not None:
            return finite_verb

        # If parent is itself a clause, use it as new inner_clause for next iteration
        if parent.tag == 'wg' and parent.get('class') == 'cl':
            inner_clause = parent
        current = parent

    return None


def _find_governing_verb_for_participle(w_elem, parent_map):
    """For a participle, find any governing verb (finite or another participle higher up).

    This is a broader search than _find_governing_finite_verb — it also finds
    cases where a participle is governed by another participle in a higher clause
    (chain of participial subordination). The key question is: does a finite verb
    exist in an ancestor clause?

    Returns (governing_verb_element, is_finite_verb).
    """
    finite = _find_governing_finite_verb(w_elem, parent_map)
    if finite is not None:
        return finite, True
    return None, False


# ---------------------------------------------------------------------------
# Word matching: align line words to Macula words
# ---------------------------------------------------------------------------

def _match_line_words(line_text: str, verse_words: list[WordInfo]) -> list[Optional[WordInfo]]:
    """Match words in a colometric line to Macula words in the verse.

    Returns a list parallel to the words in line_text.
    """
    line_words = line_text.split()
    if not line_words or not verse_words:
        return [None] * len(line_words)

    line_norms = [_normalize_for_match(w) for w in line_words]
    macula_norms = [_normalize_for_match(wi.normalized) for wi in verse_words]

    result = [None] * len(line_words)
    used = [False] * len(verse_words)

    for i, ln in enumerate(line_norms):
        if not ln:
            continue
        for j, mn in enumerate(macula_norms):
            if not used[j] and ln == mn:
                result[i] = verse_words[j]
                used[j] = True
                break

    return result


# ---------------------------------------------------------------------------
# Core predication check
# ---------------------------------------------------------------------------

def check_line_completeness(
    line_text: str,
    book_slug: str,
    chapter: int,
    verse: int,
) -> PredicationResult:
    """Check if a colometric line contains a complete predication.

    A line is complete if:
      - It contains a finite verb (indicative, subjunctive, imperative, optative)
      - It contains a participle whose governing finite verb is also on this line
      - It contains a predicate role (role=p — implied copula)
      - It has no verbal element at all (handled elsewhere by verbless rule)

    A line is INCOMPLETE if:
      - It contains a participle but NO finite verb, AND the governing finite
        verb (found by walking UP the Macula syntax tree) is NOT on this line.

    Args:
        line_text: The colometric line text (Greek).
        book_slug: Project slug (e.g., 'acts', 'mark').
        chapter: Chapter number.
        verse: Verse number.

    Returns:
        PredicationResult with complete=False if the line should be merged.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return PredicationResult()  # No data — assume complete

    root, parent_map, all_verse_words = _parse_book(macula_id)
    if root is None:
        return PredicationResult()

    verse_words = all_verse_words.get((chapter, verse), [])
    if not verse_words:
        return PredicationResult()

    # Match line words to Macula words
    matched = _match_line_words(line_text, verse_words)

    # Collect xml:ids of words on this line
    line_xml_ids = set()
    for wi in matched:
        if wi is not None and wi.xml_id:
            line_xml_ids.add(wi.xml_id)

    # Classify verbal elements on this line
    finite_verbs_on_line = []
    participles_on_line = []
    infinitives_on_line = []
    has_predicate_role = False

    for wi in matched:
        if wi is None:
            continue
        if wi.mood in _FINITE_MOODS:
            finite_verbs_on_line.append(wi)
        elif wi.mood == 'participle':
            participles_on_line.append(wi)
        elif wi.mood == 'infinitive':
            infinitives_on_line.append(wi)
        if wi.role == 'p':
            has_predicate_role = True

    # Case 1: Finite verb present → complete predication (the line governs its own clause)
    if finite_verbs_on_line:
        return PredicationResult(complete=True)

    # Case 3: Infinitive present (with or without participle)
    # An infinitive provides a local verbal governor for any participles on the
    # same line (e.g., ὥστε + accusative + participle + infinitive is one result
    # clause). The line has its own verbal structure.
    if infinitives_on_line:
        return PredicationResult(complete=True)

    # Case 4: No verbal element at all
    # → handled by existing verbless rule; we consider it complete here
    if not participles_on_line and not infinitives_on_line:
        # Check for predicate role (implied copula)
        if has_predicate_role:
            return PredicationResult(complete=True)
        # No verbal element — let verbless rule handle it
        return PredicationResult(complete=True)

    # Case 2: Participle(s) present, no finite verb on this line
    # → Check if the governing finite verb is on this line
    for ptc_wi in participles_on_line:
        gov_verb = _find_governing_finite_verb(ptc_wi.element, parent_map)
        if gov_verb is None:
            # No governing verb found in tree — might be a main-verb participle
            # (rare but possible, e.g., narrative participle). Treat as complete.
            continue

        gov_xml_id = gov_verb.get('{http://www.w3.org/XML/1998/namespace}id', '')
        if gov_xml_id not in line_xml_ids:
            # The governing finite verb is NOT on this line → incomplete predication
            gov_text = gov_verb.get('normalized', '') or (gov_verb.text or '')
            return PredicationResult(
                complete=False,
                reason=f"participle '{ptc_wi.normalized}' governed by '{gov_text}' which is not on this line",
                participle_text=ptc_wi.normalized,
                governor_text=gov_text,
            )

    # All participles have their governing verbs on this line → complete
    return PredicationResult(complete=True)


def line_has_complete_predication(line_text: str, book_slug: str,
                                  chapter: int, verse: int) -> bool:
    """Convenience wrapper: returns True if the line is a complete predication."""
    return check_line_completeness(line_text, book_slug, chapter, verse).complete


def find_participle_governor_on_other_line(
    line_text: str,
    other_line_text: str,
    book_slug: str,
    chapter: int,
    verse: int,
) -> str:
    """Check if the first word (participle) on line_text is governed by a verb on other_line_text.

    This walks the Macula syntax tree from the participle upward to find its
    governing finite verb, then checks whether that verb appears on other_line_text.

    Args:
        line_text: The line starting with a participle.
        other_line_text: The candidate line that may contain the governing verb.
        book_slug: Project slug (e.g., 'acts').
        chapter: Chapter number.
        verse: Verse number.

    Returns:
        The governor verb text if found on other_line_text, else empty string.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return ""

    root, parent_map, all_verse_words = _parse_book(macula_id)
    if root is None:
        return ""

    verse_words = all_verse_words.get((chapter, verse), [])
    if not verse_words:
        return ""

    # Match line_text words to Macula
    matched = _match_line_words(line_text, verse_words)

    # Find the first participle on line_text
    ptc_wi = None
    for wi in matched:
        if wi is not None and wi.mood == 'participle':
            ptc_wi = wi
            break
    if ptc_wi is None:
        return ""

    # Match other_line_text words to Macula for checking
    other_matched = _match_line_words(other_line_text, verse_words)
    other_xml_ids = set()
    for wi in other_matched:
        if wi is not None and wi.xml_id:
            other_xml_ids.add(wi.xml_id)

    # Search for ANY finite verb in the tree ancestry of this participle
    # that appears on the other line. This handles both:
    # (a) governing verbs in ancestor clauses (circumstantial participles)
    # (b) governing verbs in the same clause (complement participles like ζῶντα)
    ptc_xml_id = ptc_wi.xml_id
    inner_clause = _find_innermost_clause(ptc_wi.element, parent_map)
    if inner_clause is None:
        return ""

    current = inner_clause
    inner_word_ids = set()
    for w in inner_clause.iter('w'):
        wid = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
        if wid:
            inner_word_ids.add(wid)

    while current in parent_map:
        parent = parent_map[current]
        if parent.tag == 'sentence' or parent.tag not in ('wg',):
            # Don't search beyond the sentence
            if parent.tag != 'wg':
                break

        # Search for ALL finite verbs in the parent, excluding inner clause words
        for w in parent.iter('w'):
            mood = w.get('mood', '')
            if mood not in _FINITE_MOODS:
                continue
            wid = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
            if wid in inner_word_ids:
                continue
            # Check if this finite verb is on the other line
            if wid in other_xml_ids:
                gov_text = w.get('normalized', '') or (w.text or '')
                return gov_text

        # Update inner_clause for next iteration
        if parent.tag == 'wg' and parent.get('class') == 'cl':
            inner_clause = parent
            inner_word_ids = set()
            for w in inner_clause.iter('w'):
                wid = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
                if wid:
                    inner_word_ids.add(wid)

        current = parent

    return ""


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

def clear_cache():
    """Clear the parsed book cache."""
    _book_cache.clear()


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    test_cases = [
        # (line_text, book, chapter, verse, expected_description)
        ("οἱ δὲ προσαπειλησάμενοι", "acts", 4, 21,
         "MERGE — participle separated from governing ἀπέλυσαν"),
        ("ἀπέλυσαν αὐτούς,", "acts", 4, 21,
         "KEEP — has finite verb ἀπέλυσαν"),
        ("ἀκούσας δὲ", "matt", 2, 3,
         "MERGE — participle separated from governing ἐταράχθη"),
        ("ὁ βασιλεὺς Ἡρῴδης ἐταράχθη", "matt", 2, 3,
         "KEEP — has finite verb ἐταράχθη"),
        ("καὶ ταῦτα εἰπὼν", "acts", 1, 9,
         "CHECK — participle with object, but governor may be in different sentence"),
        ("βλεπόντων αὐτῶν", "acts", 1, 9,
         "CHECK — genitive absolute, check governing verb"),
        ("ἐπήρθη", "acts", 1, 9,
         "KEEP — finite verb"),
        ("Καὶ ὑμνήσαντες", "mark", 14, 26,
         "MERGE — participle separated from governing ἐξῆλθον"),
        ("ἐξῆλθον εἰς τὸ Ὄρος τῶν Ἐλαιῶν.", "mark", 14, 26,
         "KEEP — has finite verb ἐξῆλθον"),
        ("ἔδοξε κἀμοὶ παρηκολουθηκότι ἄνωθεν πᾶσιν ἀκριβῶς", "luke", 1, 3,
         "KEEP — finite verb ἔδοξε present"),
        ("Καὶ πάλιν ἤρξατο διδάσκειν παρὰ τὴν θάλασσαν.", "mark", 4, 1,
         "KEEP — finite verb ἤρξατο present"),
    ]

    print("Predication completeness test results:\n")
    for line, book, ch, vs, expected in test_cases:
        result = check_line_completeness(line, book, ch, vs)
        status = "KEEP" if result.complete else "MERGE"
        reason = f" — {result.reason}" if result.reason else ""
        print(f"  {book.title()} {ch}:{vs}  [{status}]  '{line}'")
        print(f"    Expected: {expected}")
        if reason:
            print(f"    Reason: {reason}")
        print()
