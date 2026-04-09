"""
morphgnt_lookup.py — MorphGNT word-level morphological lookup.

Loads MorphGNT SBLGNT data and provides functions to check whether
a given Greek word has a verbal element (finite verb, participle,
or infinitive).

Used by v3_colometry.py to detect verbless lines that should be merged.
"""

import os
import re
from collections import defaultdict

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_MORPHGNT_DIR = os.path.join(_REPO_ROOT, "research", "morphgnt-sblgnt")

# MorphGNT file number -> our book slug
_FILE_MAP = {
    "61": "matt", "62": "mark", "63": "luke", "64": "john",
    "65": "acts", "66": "rom", "67": "1cor", "68": "2cor",
    "69": "gal", "70": "eph", "71": "phil", "72": "col",
    "73": "1thess", "74": "2thess", "75": "1tim", "76": "2tim",
    "77": "titus", "78": "phlm", "79": "heb", "80": "jas",
    "81": "1pet", "82": "2pet", "83": "1john", "84": "2john",
    "85": "3john", "86": "jude", "87": "rev",
}

_SLUG_TO_FILE = {v: k for k, v in _FILE_MAP.items()}

# Cache: {book_slug: {normalized_word: set(POS codes)}}
_word_pos_cache = {}

# Cache: {book_slug: {(chapter, verse): [(word, pos, parsing), ...]}}
_verse_cache = {}


def _find_morphgnt_file(book_slug):
    """Find the MorphGNT file for a given book slug."""
    file_num = _SLUG_TO_FILE.get(book_slug)
    if not file_num:
        return None
    for fname in os.listdir(_MORPHGNT_DIR):
        if fname.startswith(file_num + "-"):
            return os.path.join(_MORPHGNT_DIR, fname)
    return None


def _load_book(book_slug):
    """Load MorphGNT data for a book. Returns verse-level data."""
    if book_slug in _verse_cache:
        return _verse_cache[book_slug]

    filepath = _find_morphgnt_file(book_slug)
    if not filepath:
        _verse_cache[book_slug] = {}
        _word_pos_cache[book_slug] = {}
        return {}

    verses = defaultdict(list)
    word_pos = defaultdict(set)

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, text, word, normalized, lemma = parts
            # ref format: BBCCVV (e.g., 050102 = book 05, chapter 01, verse 02)
            ch = int(ref[2:4])
            vs = int(ref[4:6])
            verses[(ch, vs)].append((word, pos, parsing))
            # Strip punctuation from word for lookup
            clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
            if clean:
                word_pos[clean].add(pos.strip())

    _verse_cache[book_slug] = dict(verses)
    _word_pos_cache[book_slug] = dict(word_pos)
    return dict(verses)


def _load_word_pos(book_slug):
    """Load the word->POS mapping for a book."""
    if book_slug not in _word_pos_cache:
        _load_book(book_slug)
    return _word_pos_cache.get(book_slug, {})


def word_is_verbal(word, book_slug):
    """Check if a word has any verbal POS tag in this book.

    Verbal = V- (verb, including participles and infinitives).
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    pos_map = _load_word_pos(book_slug)
    pos_tags = pos_map.get(clean, set())
    return any(p.startswith('V') for p in pos_tags)


def line_has_verbal_element(line_text, book_slug):
    """Check if a line of Greek text contains any verbal element.

    A verbal element is any word tagged as V- in MorphGNT (finite verb,
    participle, or infinitive).

    Args:
        line_text: A line of Greek text (may include punctuation)
        book_slug: Book identifier (e.g., 'acts', 'mark')

    Returns:
        True if the line contains at least one verbal element.
    """
    words = line_text.strip().split()
    for w in words:
        if word_is_verbal(w, book_slug):
            return True
    return False


def line_has_finite_verb(line_text, book_slug):
    """Check if a line contains a finite verb (indicative, subjunctive, or imperative).

    MorphGNT parsing field position 3 (0-indexed) encodes mood:
      I = indicative, S = subjunctive, D = imperative, O = optative.
    We check every word in the line against the book's verse data.
    """
    if book_slug not in _word_pos_cache:
        _load_book(book_slug)
    # We need to check individual word parsings, not just POS
    verses = _verse_cache.get(book_slug, {})
    # Build a set of words on this line
    line_words = set()
    for w in line_text.strip().split():
        clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
        if clean:
            line_words.add(clean)

    if not line_words:
        return False

    # Scan all verses for matching words with finite verb parsing
    for (ch, vs), word_list in verses.items():
        for word, pos, parsing in word_list:
            if not pos.startswith('V'):
                continue
            clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
            if clean not in line_words:
                continue
            # Check mood: parsing format is e.g. "3AAI-S--" or "-PAPNPM-"
            # Position 3 (0-indexed) is mood for finite verbs
            if len(parsing) >= 4 and parsing[3] in ('I', 'S', 'D', 'O'):
                return True
    return False


def word_is_comparative(word, book_slug):
    """Check if a word is tagged as comparative degree in MorphGNT.

    MorphGNT parsing field last character = 'C' for comparative degree.
    This applies to adjectives (A-) and some adverbs.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
            if w_clean == clean and parsing.endswith('C'):
                return True
    return False


def get_comparative_words(book_slug):
    """Return a set of all words tagged as comparative degree in a book."""
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    comparatives = set()
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if parsing.endswith('C'):
                clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
                if clean:
                    comparatives.add(clean)
    return comparatives


def clear_cache():
    """Clear all cached data."""
    _word_pos_cache.clear()
    _verse_cache.clear()
