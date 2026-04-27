"""
morphgnt_lookup.py — MorphGNT word-level morphological lookup.

Loads MorphGNT SBLGNT data and provides functions to check whether
a given Greek word has a verbal element (finite verb, participle,
or infinitive).

Used by validators/common.py as the morphological backend for the
production validator suite (R2–R7, R11, R18, R19, etc.). Originally
written for the now-archived v3_colometry.py verbless-line merge pass.
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

# Cache: {book_slug: {cleaned_word: set(lemmas)}}
_word_lemma_cache = {}


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
    word_lemmas = defaultdict(set)

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
                word_lemmas[clean].add(lemma)

    _verse_cache[book_slug] = dict(verses)
    _word_pos_cache[book_slug] = dict(word_pos)
    _word_lemma_cache[book_slug] = dict(word_lemmas)
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


def word_is_participle(word, book_slug):
    """Check if a word is tagged as a participle in MorphGNT.

    MorphGNT parsing field position 3 (0-indexed) encodes mood:
    P = participle. We check V- POS words with parsing[3]='P'.

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as a participle in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if not pos.startswith('V'):
                continue
            w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
            if w_clean == clean and len(parsing) >= 4 and parsing[3] == 'P':
                return True
    return False


def word_has_lemma(word, book_slug, target_lemma):
    """Check if a word has a specific lemma in MorphGNT.

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')
        target_lemma: The lemma to check for (e.g., 'εἰμί')

    Returns:
        True if any MorphGNT entry for this word has the target lemma.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _word_lemma_cache:
        _load_book(book_slug)
    lemma_map = _word_lemma_cache.get(book_slug, {})
    return target_lemma in lemma_map.get(clean, set())


def word_is_imperative(word, book_slug):
    """Check if a word is tagged as an imperative verb in MorphGNT.

    MorphGNT parsing field position 3 (0-indexed) encodes mood:
    D = imperative.

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as an imperative in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if not pos.startswith('V'):
                continue
            w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
            if w_clean == clean and len(parsing) >= 4 and parsing[3] == 'D':
                return True
    return False


def get_imperative_words_on_line(line_text, book_slug):
    """Return a list of (word, position_in_line) for imperative verbs on a line.

    Args:
        line_text: A line of Greek text
        book_slug: Book identifier

    Returns:
        List of (cleaned_word, char_index) tuples for each imperative found.
    """
    results = []
    words = line_text.strip().split()
    if not words:
        return results

    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})

    # Build set of imperative words in this book
    imperative_words = set()
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if pos.startswith('V') and len(parsing) >= 4 and parsing[3] == 'D':
                w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
                if w_clean:
                    imperative_words.add(w_clean)

    # Find imperative words on this line, tracking character position
    pos = 0
    for w in words:
        clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
        if clean in imperative_words:
            results.append((clean, pos))
        pos += len(w) + 1  # +1 for the space

    return results


def word_is_noun(word, book_slug):
    """Check if a word is tagged as a noun (N-) in MorphGNT.

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as a noun in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    pos_map = _load_word_pos(book_slug)
    pos_tags = pos_map.get(clean, set())
    return any(p.startswith('N') for p in pos_tags)


def word_is_pronoun(word, book_slug):
    """Check if a word is tagged as a pronoun (R*) in MorphGNT.

    MorphGNT POS tags for pronouns: RP (personal), RD (demonstrative),
    RR (relative), RI (interrogative), RX (indefinite), RC (reciprocal).

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as a pronoun in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    pos_map = _load_word_pos(book_slug)
    pos_tags = pos_map.get(clean, set())
    return any(p.startswith('R') for p in pos_tags)


def word_is_noun_or_pronoun(word, book_slug):
    """Check if a word is a noun (N-) or pronoun (R*) in MorphGNT."""
    return word_is_noun(word, book_slug) or word_is_pronoun(word, book_slug)


def word_is_vocative(word, book_slug):
    """Check if a word can be vocative case in MorphGNT.

    MorphGNT parsing for nouns/pronouns: position 4 (0-indexed) is case.
    V = vocative.

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as vocative case in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if not (pos.startswith('N') or pos.startswith('R')):
                continue
            w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
            if w_clean == clean and len(parsing) >= 5 and parsing[4] == 'V':
                return True
    return False


def word_is_relative_pronoun(word, book_slug):
    """Check if a word is tagged as a relative pronoun (RR) in MorphGNT.

    MorphGNT POS tag RR = relative pronoun. This covers all forms of
    ὅς, ἥ, ὅ (and compounds like ὅστις, ἥτις, ὅ τι).

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as a relative pronoun in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    pos_map = _load_word_pos(book_slug)
    pos_tags = pos_map.get(clean, set())
    return 'RR' in pos_tags


def word_is_participle_accusative(word, book_slug):
    """Check if a word is an accusative participle in MorphGNT.

    MorphGNT parsing for verbs: position 3 = mood (P=participle),
    position 4 = case (when participle: A=accusative).

    Args:
        word: A Greek word (may include punctuation)
        book_slug: Book identifier (e.g., 'mark', 'acts')

    Returns:
        True if the word is tagged as an accusative participle in any verse.
    """
    clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', word)
    if not clean:
        return False
    if book_slug not in _verse_cache:
        _load_book(book_slug)
    verses = _verse_cache.get(book_slug, {})
    for (ch, vs), word_list in verses.items():
        for w, pos, parsing in word_list:
            if not pos.startswith('V'):
                continue
            w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
            if w_clean == clean and len(parsing) >= 5 and parsing[3] == 'P' and parsing[4] == 'A':
                return True
    return False


def clear_cache():
    """Clear all cached data."""
    _word_pos_cache.clear()
    _verse_cache.clear()
    _word_lemma_cache.clear()
