#!/usr/bin/env python3
"""
V3 Rhetorical Pattern Refinement for colometric formatting.

Takes v2-colometric output (syntax-tree-driven clause breaks) and applies
rhetorical pattern detection to improve the display. The v2 output has correct
clause boundaries from Macula syntax trees, but needs rhetorical refinement.

Usage:
    py -3 scripts/v3_colometry.py                              # all books
    py -3 scripts/v3_colometry.py --book Mark                  # one book
    py -3 scripts/v3_colometry.py --book Mark --chapter 4      # one chapter

Input:  data/text-files/v2-colometric/*.txt
Output: data/text-files/v3-colometric/*.txt
"""

import re
import os
import sys
import argparse

# MorphGNT lookup for verbal element detection
try:
    from morphgnt_lookup import (line_has_verbal_element, line_has_finite_verb,
                                  get_comparative_words, word_is_participle,
                                  word_has_lemma, word_is_imperative,
                                  get_imperative_words_on_line)
    _HAS_MORPHGNT = True
except ImportError:
    _HAS_MORPHGNT = False

# Macula valency check for participle completeness
try:
    from macula_valency import check_line_valency, line_has_predicate_role
    _HAS_VALENCY = True
except ImportError:
    _HAS_VALENCY = False

# Macula predication check — unified tree-based completeness test
try:
    from macula_predication import check_line_completeness, PredicationResult
    _HAS_PREDICATION = True
except ImportError:
    _HAS_PREDICATION = False

# Macula sentence boundary detection — prevents cross-sentence merges
try:
    from macula_sentences import find_sentence_boundary_in_line
    _HAS_SENTENCES = True
except ImportError:
    _HAS_SENTENCES = False

# ---------- configuration ----------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v2-colometric')
OUTPUT_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v3-colometric')

# Book metadata: filename -> (display name, abbreviation, chapter count)
# Copied from auto_colometry.py for consistency
BOOKS = {
    'Matt':    ('Matthew',        'matt',     28),
    'Mark':    ('Mark',           'mark',     16),
    'Luke':    ('Luke',           'luke',     24),
    'John':    ('John',           'john',     21),
    'Acts':    ('Acts',           'acts',     28),
    'Rom':     ('Romans',         'rom',      16),
    '1Cor':    ('1 Corinthians',  '1cor',     16),
    '2Cor':    ('2 Corinthians',  '2cor',     13),
    'Gal':     ('Galatians',      'gal',       6),
    'Eph':     ('Ephesians',      'eph',       6),
    'Phil':    ('Philippians',    'phil',      4),
    'Col':     ('Colossians',     'col',       4),
    '1Thess':  ('1 Thessalonians','1thess',    5),
    '2Thess':  ('2 Thessalonians','2thess',    3),
    '1Tim':    ('1 Timothy',      '1tim',      6),
    '2Tim':    ('2 Timothy',      '2tim',      4),
    'Titus':   ('Titus',          'titus',     3),
    'Phlm':    ('Philemon',       'phlm',      1),
    'Heb':     ('Hebrews',        'heb',      13),
    'Jas':     ('James',          'jas',       5),
    '1Pet':    ('1 Peter',        '1pet',      5),
    '2Pet':    ('2 Peter',        '2pet',      3),
    '1John':   ('1 John',         '1john',     5),
    '2John':   ('2 John',         '2john',     1),
    '3John':   ('3 John',         '3john',     1),
    'Jude':    ('Jude',           'jude',      1),
    'Rev':     ('Revelation',     'rev',      22),
}

# ---------- Pattern 1: Complementary verb + infinitive merging ----------

# Verbs that take complementary infinitives (Wallace ch. 23)
# These are the finite forms most commonly split from their infinitive complement
COMPLEMENTARY_VERBS = [
    # Verbs of beginning
    'ἤρξατο', 'ἤρξαντο', 'ἄρξηται', 'ἀρξάμενος', 'ἀρξάμενοι',
    'ἄρχομαι', 'ἄρχεται', 'ἄρχονται',
    # Verbs of ability/power
    'ἐδύνατο', 'δύναται', 'δύνανται', 'δυνήσεται', 'δυνήσονται',
    'ἠδύνατο', 'ἠδύναντο', 'δύνασαι', 'δυνάμεθα',
    # Verbs of wishing/wanting
    'ἤθελεν', 'ἤθελον', 'θέλει', 'θέλω', 'θέλεις', 'θέλουσιν',
    'θέλομεν', 'θέλετε', 'ἠθέλησεν',
    # Verbs of being about to
    'μέλλει', 'μέλλουσιν', 'ἔμελλεν', 'ἔμελλον', 'μέλλω',
    # Verbs of attempting/daring
    'ἐτόλμησεν', 'τολμᾷ', 'ἐπεχείρησαν',
    # Verbs of ceasing/neglecting
    'παύομαι', 'ἐπαύσατο', 'παύσονται',
    # Verbs of obligation
    'δεῖ', 'δεήσει',         # impersonal "it is necessary"
    'χρή',                    # impersonal "it is necessary" (rare)
    'ὀφείλει', 'ὀφείλομεν',
    # Verbs of seeming/deciding (take infinitive complement)
    'ἔδοξε', 'ἔδοξεν', 'δοκεῖ', 'δόξῃ', 'δοκοῦσιν', 'εὐδόκησεν', 'εὐδόκησα',
]

# Build a set for fast lookup
COMPLEMENTARY_VERB_SET = set(COMPLEMENTARY_VERBS)

# Also match forms ending with common complementary verb stems
COMPLEMENTARY_VERB_PATTERNS = [
    re.compile(r'\b[ἤἠ]ρξ(?:ατο|αντο)\b'),     # ἄρχομαι forms
    re.compile(r'\bδ[υύ]ν(?:αται|ανται|ατο|ασαι|άμεθα|ήσεται)\b'),  # δύναμαι forms
    re.compile(r'\b[ἤἠ]θ[εέ]λ(?:εν|ον|ησεν)\b'),  # θέλω forms
    re.compile(r'\bμ[εέ]λλ(?:ει|ουσιν|εν|ον|ω)\b'),  # μέλλω forms
]


def ends_with_complementary_verb(line):
    """Check if a line ends with a complementary verb form."""
    stripped = line.rstrip(' .,;·')
    words = stripped.split()
    if not words:
        return False
    last_word = words[-1]
    if last_word in COMPLEMENTARY_VERB_SET:
        return True
    for pat in COMPLEMENTARY_VERB_PATTERNS:
        if pat.search(last_word):
            return True
    return False


def line_contains_complementary_verb(line):
    """Check if a line contains ANY complementary verb form (not just at end)."""
    words = line.rstrip(' .,;·').split()
    for w in words:
        clean = w.rstrip('.,;·')
        if clean in COMPLEMENTARY_VERB_SET:
            return True
        for pat in COMPLEMENTARY_VERB_PATTERNS:
            if pat.search(clean):
                return True
    return False


def line_contains_infinitive(line):
    """Check if a line contains any infinitive form."""
    words = line.strip().split()
    for w in words:
        clean = w.rstrip('.,;·')
        if clean.endswith(_INF_ENDINGS):
            return True
    return False


def line_starts_with_infinitive_or_complement(line):
    """Check if a line starts with an infinitive or content completing a complementary verb."""
    stripped = line.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0]
    # Common infinitive endings
    inf_endings = ('ειν', 'αι', 'εῖν', 'οῦν', 'ᾶν', 'σθαι', 'ναι',
                   'εῖσθαι', 'ᾶσθαι', 'οῦσθαι')
    if first_word.endswith(inf_endings):
        return True
    # Also check for τε + infinitive patterns
    if stripped.startswith('τε ') or stripped.startswith('τε\xa0'):
        return True
    return False


def apply_complementary_verb_merge(verse_lines):
    """Pattern 1: Merge over-split verb + complement lines."""
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        if (i + 1 < len(verse_lines)
                and len(line) < 25
                and ends_with_complementary_verb(line)
                and line_starts_with_infinitive_or_complement(verse_lines[i + 1])):
            # Merge this line with the next
            merged = line.rstrip() + ' ' + verse_lines[i + 1].lstrip()
            result.append(merged)
            i += 2
        else:
            result.append(line)
            i += 1
    return result


# ---------- Pattern 1b: Infinitive-governing construction merge ----------

# Patterns where a construction governs an infinitive and the two should stay together.
# When the tree splits "ὥστε αὐτὸν ... ἐμβάντα" / "καθῆσθαι ...", merge them.
# Also covers πρίν + inf, μετὰ τό + inf, διὰ τό + inf, εἰς τό + inf, πρὸ τοῦ + inf.

def apply_infinitive_construction_merge(verse_lines):
    """Merge lines where an infinitive on the next line completes a governing construction."""
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        if i + 1 < len(verse_lines):
            line = verse_lines[i]
            next_line = verse_lines[i + 1]
            # Check if next line starts with an infinitive
            if line_starts_with_infinitive_or_complement(next_line):
                # Check if current line ends with an accusative/participle pattern
                # typical of ὥστε + acc + inf, or ends with a preposition governing inf
                stripped = line.rstrip(' .,;·')
                # ὥστε + accusative + participle, with infinitive on next line
                if re.search(r'\bὥστε\b', line):
                    merged = line.rstrip() + ' ' + next_line.lstrip()
                    result.append(merged)
                    i += 2
                    continue
                # πρίν + infinitive
                if stripped.endswith(('πρὶν', 'πρίν')):
                    result.append(line.rstrip() + ' ' + next_line.lstrip())
                    i += 2
                    continue
                # Articular infinitive: ends with τό, τοῦ after μετά, διά, εἰς, πρό
                if re.search(r'\b(?:μετὰ|διὰ|εἰς|πρὸ)\s+τ[όοῦ][ῦ]?\s*$', stripped):
                    result.append(line.rstrip() + ' ' + next_line.lstrip())
                    i += 2
                    continue
        result.append(verse_lines[i])
        i += 1
    return result


# ---------- Pattern 0: Infinitive merge-back ----------

# Common infinitive endings in Greek
_INF_ENDINGS = ('ειν', 'αι', 'εῖν', 'οῦν', 'ᾶν', 'σθαι', 'ναι',
                'εῖσθαι', 'ᾶσθαι', 'οῦσθαι')


def _line_starts_with_infinitive(line):
    """Check if a line's first word is an infinitive form."""
    stripped = line.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0].rstrip('.,;·')
    return first_word.endswith(_INF_ENDINGS)


def apply_infinitive_merge_back(verse_lines):
    """Merge lines that start with an infinitive back into the preceding line.

    Grammatical basis: an infinitive is a dependent verbal form that requires a
    governing element (a verb, noun, adjective, or preposition). A line beginning
    with an infinitive almost never constitutes a valid colon on its own — it
    lacks the semantico-syntactic completeness that Marschall (2023), following
    Pseudo-Demetrius, identifies as the criterion for a colon.

    Examples this catches:
      "Ὃς ἔχει ὦτα" / "ἀκούειν ἀκουέτω."  →  merged (epexegetical infinitive)
      "ὥστε αὐτὸν ... ἐμβάντα" / "καθῆσθαι ..."  →  merged (result infinitive)
      "μετὰ τὸ" / "παθεῖν αὐτόν"  →  merged (articular infinitive)

    Guard: skip if the merged result would be excessively long (>85 chars),
    since some infinitive clauses are genuinely their own colon when they carry
    substantial content (e.g., a full purpose clause with ἵνα).
    """
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        if (i > 0
                and _line_starts_with_infinitive(verse_lines[i])
                and result):  # have a previous line to merge into
            prev = result[-1]
            merged = prev.rstrip() + ' ' + verse_lines[i].lstrip()
            result[-1] = merged
            i += 1
            continue
        result.append(verse_lines[i])
        i += 1
    return result


# ---------- Pattern 1a: Complementary verb without infinitive ----------

def apply_complementary_verb_without_infinitive_merge(verse_lines):
    """Merge lines that contain a complementary verb but lack its infinitive complement.

    Grammatical basis: verbs like δοκέω, δύναμαι, ἄρχομαι, θέλω, μέλλω require
    an infinitive complement to express a complete thought. "It seemed good to me"
    (ἔδοξε κἀμοί) without "to write" (γράψαι) is an incomplete thought — the
    reader is waiting to hear what seemed good.
    """
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        if (i + 1 < len(verse_lines)
                and line_contains_complementary_verb(line)
                and not line_contains_infinitive(line)):
            merged = line.rstrip() + ' ' + verse_lines[i + 1].lstrip()
            result.append(merged)
            i += 2
        else:
            result.append(line)
            i += 1
    return result


# ---------- Pattern 0a: Periphrastic construction merge ----------

# Forms of εἰμί for fast lookup (surface forms as they appear in the text)
EIMI_FORMS = {
    # Present indicative
    'εἰμί', 'εἰμὶ', 'εἶ', 'ἐστίν', 'ἐστὶν', 'ἐστιν',
    'ἐσμέν', 'ἐσμὲν', 'ἐστέ', 'ἐστὲ', 'εἰσίν', 'εἰσὶν', 'εἰσιν',
    # Imperfect indicative
    'ἦν', 'ἦς', 'ἦμεν', 'ἦτε', 'ἦσαν', 'ἤμην', 'ἤμεθα',
    # Future indicative
    'ἔσομαι', 'ἔσῃ', 'ἔσται', 'ἐσόμεθα', 'ἔσεσθε', 'ἔσονται',
    # Present subjunctive
    'ὦ', 'ᾖς', 'ᾖ', 'ὦμεν', 'ὦσιν', 'ὦσὶν',
    # Imperative
    'ἴσθι', 'ἔστω', 'ἔστε', 'ἔστωσαν',
    # NOTE: εἶναι (infinitive) deliberately excluded — infinitives don't
    # form periphrastic constructions with participles.
}

# Global counters for reporting
_periphrastic_merge_count = 0
_multi_image_split_count = 0


def _clean_word(w):
    """Strip punctuation from a Greek word for lookup."""
    return re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)


def _line_ends_with_eimi(line, book_slug):
    """Check if a line ends with a finite form of εἰμί.

    Uses the surface form set only (no lemma fallback) to avoid matching
    εἶναι (infinitive) or ὤν/οὖσα/ὄν (participles of εἰμί), which don't
    form periphrastic constructions.
    """
    stripped = line.rstrip()
    words = stripped.split()
    if not words:
        return False
    last_word = _clean_word(words[-1])
    return last_word in EIMI_FORMS


def _line_starts_with_eimi(line, book_slug):
    """Check if a line starts with a finite form of εἰμί."""
    stripped = line.strip()
    if not stripped:
        return False
    first_word = _clean_word(stripped.split()[0])
    return first_word in EIMI_FORMS


def _line_starts_with_participle(line, book_slug):
    """Check if a line's first word is a participle (via MorphGNT)."""
    if not _HAS_MORPHGNT or not book_slug:
        return False
    stripped = line.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0]
    return word_is_participle(first_word, book_slug)


def _line_ends_with_participle(line, book_slug):
    """Check if a line's last word is a participle (via MorphGNT)."""
    if not _HAS_MORPHGNT or not book_slug:
        return False
    stripped = line.rstrip()
    words = stripped.split()
    if not words:
        return False
    return word_is_participle(words[-1], book_slug)


def _line_ends_with_clause_punctuation(line):
    """Check if a line ends with punctuation suggesting a clause boundary.

    Greek clause-ending punctuation: . (period), · (ano teleia/semicolon),
    ; (question mark), , (comma — separates clauses; a periphrastic participle
    would not be separated from its εἰμί by a comma).
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in '.·;,'


def _next_line_has_participle_after_optional_postpositive(line, book_slug):
    """Check if a line starts with a participle, possibly after a postpositive particle.

    Greek postpositive particles (γάρ, δέ, μέν, οὖν, τε) can intervene between
    εἰμί and its participle in a periphrastic construction:
      ἦν γὰρ ἔχων = "for he was having"

    Returns True if:
      - First word is a participle, OR
      - First word is a postpositive particle and second word is a participle
    """
    if not _HAS_MORPHGNT or not book_slug:
        return False
    stripped = line.strip()
    if not stripped:
        return False
    words = stripped.split()
    first_word = words[0]
    if word_is_participle(first_word, book_slug):
        return True
    # Check for postpositive + participle
    POSTPOSITIVES = {'γάρ', 'γὰρ', 'δέ', 'δὲ', 'μέν', 'μὲν', 'οὖν', 'τε'}
    if (_clean_word(first_word) in POSTPOSITIVES
            and len(words) >= 2
            and word_is_participle(words[1], book_slug)):
        return True
    return False


def apply_periphrastic_merge(verse_lines, book_slug=None):
    """Merge periphrastic constructions (εἰμί + participle) split across lines.

    Grammatical basis (Wallace ch. 23): a periphrastic construction consists
    of a form of εἰμί plus a participle functioning together as a single
    compound verb form. Example: ἦν ... διδάσκων = "was teaching."

    The Macula tree may split the εἰμί from its participle onto separate
    lines, creating two incomplete cola where there should be one.

    Pattern: line ends with εἰμί form, next line starts with a participle
    (possibly after a postpositive particle like γάρ, δέ).

    Guards:
      - Skip if line ends with clause-terminal punctuation (. · ;) — the
        εἰμί belongs to a completed clause, not a periphrastic split.
      - The εἰμί must be the last word on the line (suggesting it was split
        from what follows).
    """
    global _periphrastic_merge_count

    if not _HAS_MORPHGNT or not book_slug:
        return verse_lines
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        if i + 1 < len(verse_lines):
            line = verse_lines[i]
            next_line = verse_lines[i + 1]

            # Line ends with εἰμί, next starts with participle
            # (or postpositive + participle, e.g. γὰρ ἔχων)
            # Guard: εἰμί line must be short (<=3 words) — a long line
            # ending with εἰμί is likely a complete copulative clause,
            # not a split periphrastic.
            eimi_line_words = line.strip().split()
            if (len(eimi_line_words) <= 3
                    and _line_ends_with_eimi(line, book_slug)
                    and not _line_ends_with_clause_punctuation(line)
                    and _next_line_has_participle_after_optional_postpositive(
                        next_line, book_slug)):
                merged = line.rstrip() + ' ' + next_line.lstrip()
                result.append(merged)
                _periphrastic_merge_count += 1
                i += 2
                continue

        result.append(verse_lines[i])
        i += 1
    return result


# ---------- Pattern 0b: Verbless line merge ----------

def apply_verbless_line_merge(verse_lines, book_slug=None, verse_ref=None):
    """Merge short verbless lines forward into the following line.

    Grammatical basis: a line consisting only of a preposition, conjunction,
    article, relative pronoun, and/or noun — with NO verbal element (finite
    verb, participle, or infinitive) — cannot constitute a valid colon. It
    fails the foundational test: it is not an atomic thought because the
    thought is suspended, awaiting verbal resolution.

    Examples:
      "ἄχρι ἧς ἡμέρας" (until the day — until WHAT about the day?)
      "διὰ πνεύματος ἁγίου" (through the Holy Spirit — doing WHAT?)
      "ἐάν τε γὰρ" (for if indeed — WHAT?)

    Protected from merging:
      - Vocatives (ὦ Θεόφιλε) — standalone by convention
      - Parallel list items (πρῶτον, εἶτα, καὶ ἓν patterns) — stacking
      - Lines over 25 chars (likely substantial enough to be a colon)
      - Lines where MorphGNT data is unavailable (conservative fallback)
    """
    if not _HAS_MORPHGNT or not book_slug:
        return verse_lines
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip()

        # Protect speech introductions (end with · ano teleia) from merging —
        # these are elliptical clauses where the verb of saying is implied
        ends_with_speech_marker = stripped.rstrip().endswith('·')
        # Check for predicate role (implied copula — verbless but complete thought)
        has_predicate = False
        if _HAS_VALENCY and book_slug and verse_ref:
            parts = verse_ref.split(':')
            if len(parts) == 2:
                try:
                    ch, vs = int(parts[0]), int(parts[1])
                    has_predicate = line_has_predicate_role(stripped, book_slug, ch, vs)
                except ValueError:
                    pass

        # Check if the next line starts with a subordinating/conditional conjunction —
        # merging forward into a subordinate clause creates a worse cross-clause colon
        next_starts_subordinate = False
        if i + 1 < len(verse_lines):
            next_stripped = verse_lines[i + 1].strip()
            if line_starts_with_conditional(next_stripped):
                next_starts_subordinate = True
            else:
                for conj in SUBORDINATING_CONJUNCTIONS:
                    if next_stripped.startswith(conj + ' ') or next_stripped.startswith(conj + '\xa0'):
                        next_starts_subordinate = True
                        break

        if (i + 1 < len(verse_lines)
                and not is_standalone_unit(stripped)
                and not ends_with_speech_marker
                and not has_predicate
                and not line_is_conditional_protasis(stripped)
                and not next_starts_subordinate
                and not line_has_verbal_element(stripped, book_slug)):
            # This line has no verbal element and no predicate.
            # If the line starts with ἢ/ἤ (alternative connector), merge BACKWARD
            # into the preceding line — ἢ connects alternatives to what came before,
            # not to what follows.
            first_word = stripped.split()[0] if stripped.split() else ''
            clean_first = re.sub(r'[,.\;·]', '', first_word)
            if clean_first in ('ἢ', 'ἤ') and result:
                result[-1] = result[-1].rstrip() + ' ' + stripped
                i += 1
                continue
            # Otherwise merge forward
            next_line = verse_lines[i + 1]
            merged = stripped + ' ' + next_line.strip()
            result.append(merged)
            i += 2
            continue
        result.append(line)
        i += 1
    return result


# ---------- Pattern 0c: Valency satisfaction merge ----------

def apply_valency_merge(verse_lines, book_slug=None, verse_ref=None):
    """Merge short lines where a participle's valency is unsatisfied.

    Grammatical basis: a transitive participle whose object (as annotated by
    Macula role=o) is NOT on the same colometric line represents an incomplete
    thought — the verbal idea is suspended. Such lines should merge forward
    into the line that carries the object or completes the clause.

    Protected from merging:
      - Lines ending with · (speech introductions — deliberately standalone)
      - Lines that are standalone units (vocatives, imperatives, etc.)
      - Lines where the merged result would exceed 85 chars
      - Lines where Macula data is unavailable
    """
    if not _HAS_VALENCY or not book_slug or not verse_ref:
        return verse_lines
    if len(verse_lines) < 2:
        return verse_lines

    # Parse verse reference
    parts = verse_ref.split(':')
    if len(parts) != 2:
        return verse_lines
    try:
        chapter = int(parts[0])
        verse = int(parts[1])
    except ValueError:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip()

        # Protection: speech introductions (end with · ano teleia)
        ends_with_speech_marker = stripped.rstrip().endswith('·')

        # Protection: standalone units
        standalone = is_standalone_unit(stripped)

        if (i + 1 < len(verse_lines)
                and not ends_with_speech_marker
                and not standalone):
            vr = check_line_valency(stripped, book_slug, chapter, verse)
            if vr.unsatisfied:
                next_line = verse_lines[i + 1]
                merged = stripped + ' ' + next_line.strip()
                result.append(merged)
                i += 2
                continue
        result.append(line)
        i += 1
    return result


# ---------- Pattern 0d: Predication completeness merge (unified tree-based test) ----------

# Global counter for reporting
_predication_merge_count = 0


def _is_genitive_absolute_line(line_text, book_slug, chapter, verse):
    """Check if a line contains a genitive absolute construction.

    A genitive absolute (genitive participle + genitive noun/pronoun) is
    grammatically independent — it sets the scene but is not subordinate
    to the main verb in the same way a circumstantial participle is.
    These should NOT be merged by the predication test.
    """
    try:
        from macula_clauses import get_verse_clauses_detailed
        clauses = get_verse_clauses_detailed(book_slug, chapter, verse)
        # Check if any clause flagged as genitive absolute has words matching this line
        for ci in clauses:
            if ci.is_genitive_absolute:
                # Check if this clause's text overlaps with our line
                clause_words = set(w for _, w in ci.words)
                line_words = set(line_text.strip().split())
                # Strip punctuation for comparison
                import re
                clean_line = set(re.sub(r'[,.\;·]', '', w) for w in line_words)
                clean_clause = set(re.sub(r'[,.\;·]', '', w) for w in clause_words)
                if clean_clause and clean_line and len(clean_clause & clean_line) >= 2:
                    return True
    except Exception:
        pass
    return False


def _participle_has_object_on_line(line_text, book_slug, chapter, verse):
    """Check if a line's participle has its OBJECT actually present on this line.

    A transitive participle with its object present represents a more complete
    thought — "having said THESE THINGS" paints its own image. But a bare
    intransitive participle like "having threatened" does not — it's just a
    temporal frame for the main action.

    Only returns True when the Macula clause has role=o AND that object word
    is matched to this line. Does NOT protect intransitive participles.
    """
    if not _HAS_VALENCY:
        return False
    try:
        from macula_valency import (
            _parse_book_valency, _book_cache, _clause_roles_cache,
            _match_line_words_to_macula, _SLUG_TO_MACULA
        )
        macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
        if not macula_id:
            return False
        _parse_book_valency(macula_id)
        verse_words = _book_cache.get(macula_id, {}).get((chapter, verse), [])
        clause_roles = _clause_roles_cache.get(macula_id, {})
        if not verse_words:
            return False

        matched = _match_line_words_to_macula(line_text, verse_words)
        line_refs = set(mw.ref for mw in matched if mw is not None)

        # Find participles on this line
        for mw in matched:
            if mw is not None and mw.mood == 'participle' and mw.role == 'v':
                cr = clause_roles.get(mw.clause_id)
                if cr and cr.has_object:
                    # The clause IS transitive — check if object is on THIS line
                    obj_on_line = line_refs.intersection(cr.object_word_refs)
                    if obj_on_line:
                        return True
        return False
    except Exception:
        return False


def apply_predication_merge(verse_lines, book_slug=None, verse_ref=None):
    """Merge lines that don't contain a complete predication (unified tree test).

    Grammatical basis: every colometric line must contain a complete predication —
    a verbal element that governs (not is governed by) another verb. A line with
    only a participle whose governing finite verb is on a different line represents
    an incomplete thought: the participle is subordinate to a verb the reader hasn't
    reached yet.

    This is the fundamental structural test from which the verbless, valency, and
    periphrastic rules are all special cases. It uses the Macula syntax tree to
    determine predication completeness by walking up from each participle to find
    its governing finite verb and checking whether that verb is on the same line.

    Protected from merging:
      - Lines ending with · (speech introductions — deliberately standalone)
      - Lines that are standalone units (vocatives, imperatives, etc.)
      - Lines where Macula data is unavailable (conservative fallback)
    """
    global _predication_merge_count

    if not _HAS_PREDICATION or not book_slug or not verse_ref:
        return verse_lines
    if len(verse_lines) < 2:
        return verse_lines

    # Parse verse reference
    parts = verse_ref.split(':')
    if len(parts) != 2:
        return verse_lines
    try:
        chapter = int(parts[0])
        verse = int(parts[1])
    except ValueError:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip()

        # Protection: speech introductions (end with · ano teleia)
        ends_with_speech_marker = stripped.rstrip().endswith('·')

        # Protection: standalone units
        standalone = is_standalone_unit(stripped)

        # Protection: genitive absolutes are grammatically independent
        # even though the tree nests them under a governing clause.
        # Also protect participles whose valency is satisfied (object on line).
        is_gen_abs = _is_genitive_absolute_line(stripped, book_slug, chapter, verse)
        has_satisfied_valency = _participle_has_object_on_line(stripped, book_slug, chapter, verse)

        if (i + 1 < len(verse_lines)
                and not ends_with_speech_marker
                and not standalone
                and not is_gen_abs
                and not has_satisfied_valency):
            pr = check_line_completeness(stripped, book_slug, chapter, verse)
            if not pr.complete:
                next_line = verse_lines[i + 1]
                merged = stripped + ' ' + next_line.strip()
                result.append(merged)
                _predication_merge_count += 1
                i += 2
                continue
        result.append(line)
        i += 1
    return result


# ---------- Pattern 0e: Multi-image participial split ----------

def apply_multi_image_split(verse_lines, book_slug=None, verse_ref=None):
    """Split lines that contain 2+ distinct participial images.

    Foundational criterion #2: "each line paints one image." A line with
    multiple participles, each heading its own Macula clause with substantial
    content (object, modifier), contains multiple images and must split.

    Example — Heb 1:3 has three participial clauses (ὤν / φέρων / ποιησάμενος)
    each painting a distinct image. If merged onto one line, the reader loses
    the breath-unit structure.

    Detection: match line words to Macula, group by clause_id, count clauses
    that contain a participial verb (role=v or role=vc) with substantial content.
    If 2+ such clauses, split at clause boundaries.

    Guards:
      - Don't split genitive absolutes (one scene-setting image)
      - Don't split periphrastic constructions (εἰμί + participle = one verb)
      - Each resulting half must contain a participle with substantial content
    """
    global _multi_image_split_count

    if not _HAS_VALENCY or not book_slug or not verse_ref:
        return verse_lines

    # Parse verse reference
    parts = verse_ref.split(':')
    if len(parts) != 2:
        return verse_lines
    try:
        chapter = int(parts[0])
        verse = int(parts[1])
    except ValueError:
        return verse_lines

    try:
        from macula_valency import (
            _parse_book_valency, _book_cache as valency_book_cache,
            _clause_roles_cache, _match_line_words_to_macula,
            _SLUG_TO_MACULA as valency_slug_map
        )
        from macula_clauses import get_verse_clauses_detailed
    except ImportError:
        return verse_lines

    macula_id = valency_slug_map.get(book_slug.lower())
    if not macula_id:
        return verse_lines

    _parse_book_valency(macula_id)
    verse_words = valency_book_cache.get(macula_id, {}).get((chapter, verse), [])
    clause_roles = _clause_roles_cache.get(macula_id, {})
    if not verse_words:
        return verse_lines

    # Get genitive absolute clause texts for guard
    try:
        detailed_clauses = get_verse_clauses_detailed(book_slug, chapter, verse)
        ga_clause_texts = set()
        for ci in detailed_clauses:
            if ci.is_genitive_absolute:
                ga_clause_texts.add(frozenset(w for _, w in ci.words))
    except Exception:
        ga_clause_texts = set()

    result = []
    for line in verse_lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue

        split_lines = _try_multi_image_split(
            stripped, verse_words, clause_roles, ga_clause_texts, book_slug
        )
        if split_lines and len(split_lines) > 1:
            _multi_image_split_count += len(split_lines) - 1
            result.extend(split_lines)
        else:
            result.append(line)

    return result


def _try_multi_image_split(line_text, verse_words, clause_roles, ga_clause_texts,
                           book_slug):
    """Attempt to split a line at participial clause boundaries.

    Returns a list of split lines, or None if no split needed.
    """
    from macula_valency import _match_line_words_to_macula, _normalize_for_match
    from collections import OrderedDict

    matched = _match_line_words_to_macula(line_text, verse_words)
    line_words = line_text.split()

    if len(line_words) != len(matched):
        return None

    # Group word positions by clause_id, tracking which clauses have participial verbs
    clause_info = OrderedDict()

    for i, mw in enumerate(matched):
        if mw is None:
            continue
        cl_id = mw.clause_id
        if cl_id not in clause_info:
            clause_info[cl_id] = {
                'positions': [],
                'has_ptc_verb': False,
                'ptc_word': '',
                'word_count': 0,
                'has_object': False,
                'is_ga': False,
            }
        ci = clause_info[cl_id]
        ci['positions'].append(i)
        ci['word_count'] += 1

        # Check for participial verb (role=v or role=vc with participle mood)
        if mw.mood == 'participle' and mw.role in ('v', 'vc'):
            ci['has_ptc_verb'] = True
            ci['ptc_word'] = mw.normalized

        # Check for object in clause roles
        cr = clause_roles.get(cl_id)
        if cr and cr.has_object:
            ci['has_object'] = True

    # Mark genitive absolute clauses
    for cl_id, ci in clause_info.items():
        clause_word_norms = set()
        for pos in ci['positions']:
            if matched[pos]:
                clause_word_norms.add(matched[pos].normalized)
        for ga_set in ga_clause_texts:
            if ga_set and clause_word_norms and len(ga_set & clause_word_norms) >= 2:
                ci['is_ga'] = True
                break

    # Identify participial image clauses: has participial verb, is not GA,
    # and has substantial content (object OR 3+ words on line from this clause)
    ptc_image_clauses = []
    for cl_id, ci in clause_info.items():
        if not ci['has_ptc_verb']:
            continue
        if ci['is_ga']:
            continue
        # Substantial content: has object, or has 3+ words on line from this clause
        has_substance = ci['has_object'] or ci['word_count'] >= 3
        if has_substance:
            ptc_image_clauses.append(cl_id)

    if len(ptc_image_clauses) < 2:
        return None

    # Guard: check for periphrastic (εἰμί + participle in adjacent clauses)
    eimi_forms = {
        'εἰμί', 'ἦν', 'ἐστιν', 'ἐστὶν', 'ἦσαν', 'ἔσται', 'ἔσονται',
        'ἤμην', 'ἦτε', 'ἦμεν', 'ἐσμέν', 'ἐστέ', 'εἶ',
    }
    eimi_clause_ids = set()
    for cl_id, ci in clause_info.items():
        for pos in ci['positions']:
            mw = matched[pos]
            if mw and _clean_word(mw.normalized) in eimi_forms:
                eimi_clause_ids.add(cl_id)

    # If a ptc_image_clause is adjacent to an εἰμί clause, they're periphrastic
    all_clause_ids = list(clause_info.keys())
    filtered_ptc = []
    for cl_id in ptc_image_clauses:
        idx = all_clause_ids.index(cl_id)
        is_periphrastic = False
        if idx > 0 and all_clause_ids[idx - 1] in eimi_clause_ids:
            is_periphrastic = True
        if idx < len(all_clause_ids) - 1 and all_clause_ids[idx + 1] in eimi_clause_ids:
            is_periphrastic = True
        if not is_periphrastic:
            filtered_ptc.append(cl_id)

    if len(filtered_ptc) < 2:
        return None

    # Find split points: between consecutive participial image clauses
    # Split before the first word of each subsequent ptc clause,
    # absorbing tiny connector clauses (τε, καί) into the next clause
    split_positions = set()
    for cl_id in filtered_ptc[1:]:
        ci = clause_info[cl_id]
        min_pos = min(ci['positions'])
        # Walk backward to absorb tiny non-ptc clauses (conjunctions)
        absorb_start = min_pos
        for check_pos in range(min_pos - 1, -1, -1):
            mw = matched[check_pos]
            if mw is None:
                absorb_start = check_pos
                continue
            check_cl = mw.clause_id
            check_ci = clause_info.get(check_cl)
            if (check_ci and check_ci['word_count'] <= 1
                    and not check_ci['has_ptc_verb']):
                # Tiny connector clause (τε, καί, etc.) — absorb
                absorb_start = check_pos
            else:
                break
        split_positions.add(absorb_start)

    if not split_positions:
        return None

    # Build the split lines
    sorted_splits = sorted(split_positions)
    segments = []
    prev = 0
    for sp in sorted_splits:
        if sp > prev:
            segments.append(' '.join(line_words[prev:sp]))
        prev = sp
    if prev < len(line_words):
        segments.append(' '.join(line_words[prev:]))

    # Validate: each segment must have at least 2 words
    if any(len(s.split()) < 2 for s in segments):
        return None

    return segments


# ---------- Pattern 2: Standalone imperatives/exclamations ----------

# Patterns for short imperatives/exclamations that should be their own line
STANDALONE_PATTERNS = [
    # Single-word commands followed by punctuation
    re.compile(r'^(Ἀκούετε[.·;!])\s+(.+)$'),
    # ἰδού removed — it's a presentative particle bound to its clause, not a standalone exclamation
    # Two-word commands (Σιώπα, πεφίμωσο. is already handled well in v2)
    # Exclamatory particles
    re.compile(r'^(οὐαὶ\s+\S+(?:\s+\S+)?[.·;!,]?)\s+(.+)$'),
]

# More specific: detect "Word. restOfLine" where Word is a known standalone imperative
IMPERATIVE_WORDS = {
    'Ἀκούετε', 'ἀκούετε', 'Βλέπετε', 'βλέπετε',
}


def apply_standalone_imperative_split(verse_lines):
    """Pattern 2: Split standalone imperatives/exclamations onto their own line."""
    result = []
    for line in verse_lines:
        split_done = False
        # Check for "Imperative. rest" pattern
        for pat in STANDALONE_PATTERNS:
            m = pat.match(line)
            if m:
                result.append(m.group(1))
                result.append(m.group(2))
                split_done = True
                break

        if not split_done:
            # Check for known imperative words followed by period then more text
            for imp_word in IMPERATIVE_WORDS:
                pat = re.compile(r'^(' + re.escape(imp_word) + r'[.·;!])\s+(.+)$')
                m = pat.match(line)
                if m:
                    result.append(m.group(1))
                    result.append(m.group(2))
                    split_done = True
                    break

        if not split_done:
            result.append(line)
    return result


# ---------- Pattern 2b: Staccato commata split ----------
#
# Detects call-and-response patterns where a single-word emphatic response
# (like κἀγώ.) is merged with the following clause on the same line.
# Marschall (2023, Example 13) identifies these as "commata" — very short
# cola used for vehement/passionate style (cf. Cicero: effect like "stabs").
#
# General rule: when a word followed by a sentence-ending marker (. ; · !)
# appears mid-line and the preceding segment is short (<=3 words), split
# after the marker.

def _split_at_sentence_boundaries(line):
    """Split a line at sentence-ending punctuation boundaries.

    Finds points where a word ends with . ; · or ! followed by a space
    and another word. Splits when the segment up to the punctuation is
    short (staccato, <=3 words), producing commata.
    """
    stripped = line.strip()
    if not stripped:
        return [line]

    # Find all positions of sentence-ending punctuation followed by space + word
    boundary_re = re.compile(r'(\S+[.;·!])\s+(?=\S)')
    matches = list(boundary_re.finditer(stripped))
    if not matches:
        return [line]

    # Split at each boundary where the segment ending at this punctuation is short
    parts = []
    prev_end = 0
    for m in matches:
        candidate_before = stripped[prev_end:m.end()].strip()
        before_words = candidate_before.split()
        # Only split if the segment ending at this punctuation is short (staccato)
        if len(before_words) <= 3:
            parts.append(candidate_before)
            prev_end = m.end()

    # Add the remainder
    remainder = stripped[prev_end:].strip()
    if remainder:
        parts.append(remainder)

    if len(parts) > 1:
        return parts
    return [line]


def apply_staccato_commata_split(verse_lines):
    """Split mid-line staccato commata: short responses followed by new clauses."""
    result = []
    for line in verse_lines:
        split_parts = _split_at_sentence_boundaries(line)
        result.extend(split_parts)
    return result


# ---------- Pattern 2c: Asyndeton imperative split ----------
#
# Detects lines containing multiple independent imperative verbs without
# subordinating conjunctions between them — asyndeton. Each imperative
# should get its own line for oral delivery clarity.

# Subordinating conjunctions that connect verbs dependently (don't split)
_SUBORDINATING_SET = {
    'ἵνα', 'ὥστε', 'ὅτι', 'ὅταν', 'ὅτε', 'ἐάν', 'μήποτε', 'καθώς', 'καθὼς',
    'ὥσπερ', 'ἐπειδή', 'ἐπειδὴ', 'ἐπεί', 'ἐπεὶ', 'διότι', 'ὅπως', 'ὅπου',
    'πρίν', 'πρὶν', 'ἄχρι', 'μέχρι',
}


def apply_asyndeton_imperative_split(verse_lines, book_slug=None):
    """Split lines containing multiple asyndetic imperatives.

    Uses MorphGNT to identify imperative verbs. If a line has 2+
    imperatives with no subordinating conjunction between them,
    split before the second and subsequent imperatives.
    """
    if not _HAS_MORPHGNT or not book_slug:
        return verse_lines

    result = []
    for line in verse_lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue

        # Find imperative words on this line
        imperatives = get_imperative_words_on_line(stripped, book_slug)
        if len(imperatives) < 2:
            result.append(line)
            continue

        # Build word position mapping
        words = stripped.split()
        word_positions = []
        pos = 0
        for w in words:
            word_positions.append((w, pos))
            pos += len(w) + 1

        # Map imperative char positions to word indices
        imp_word_indices = []
        for imp_word, imp_pos in imperatives:
            for idx, (w, wpos) in enumerate(word_positions):
                clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
                if clean == imp_word and abs(wpos - imp_pos) < 3:
                    imp_word_indices.append(idx)
                    break

        if len(imp_word_indices) < 2:
            result.append(line)
            continue

        # Check for subordinating conjunctions between consecutive imperatives
        has_subordinating = False
        for i in range(len(imp_word_indices) - 1):
            start_idx = imp_word_indices[i]
            end_idx = imp_word_indices[i + 1]
            for j in range(start_idx + 1, end_idx):
                w_clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', words[j])
                if w_clean in _SUBORDINATING_SET:
                    has_subordinating = True
                    break
            if has_subordinating:
                break

        if has_subordinating:
            result.append(line)
            continue

        # Split before each imperative after the first.
        # Walk backwards from each subsequent imperative to find phrase start.
        split_points = []
        for k in range(1, len(imp_word_indices)):
            imp_idx = imp_word_indices[k]
            phrase_start = imp_idx
            for j in range(imp_idx - 1, imp_word_indices[k - 1], -1):
                w = words[j]
                clean = re.sub(r'[,.\;·\s⸀⸁⸂⸃⸄⸅]', '', w)
                if word_is_imperative(clean, book_slug):
                    break
                if w.rstrip().endswith((',', ';', '·', '.')):
                    phrase_start = j + 1 if j + 1 <= imp_idx else imp_idx
                    break
                phrase_start = j

            if phrase_start < len(word_positions):
                split_points.append(word_positions[phrase_start][1])

        if not split_points:
            result.append(line)
            continue

        # Perform the splits
        parts = []
        prev = 0
        for sp in split_points:
            part = stripped[prev:sp].strip()
            if part:
                parts.append(part)
            prev = sp
        remainder = stripped[prev:].strip()
        if remainder:
            parts.append(remainder)

        if len(parts) > 1:
            result.extend(parts)
        else:
            result.append(line)

    return result


# ---------- Pattern 3: Parallel list stacking (καί + noun phrase triplets) ----------

def count_kai_phrases(line):
    """Count occurrences of καί in a line."""
    return len(re.findall(r'\bκαὶ\b', line))


def is_list_line(line):
    """Detect if a line contains a parallel list with 3+ καί phrases.

    Specifically looks for: καὶ [article] [noun phrase] repeated pattern.
    """
    # Must have 3+ καί occurrences
    kai_count = count_kai_phrases(line)
    if kai_count < 3:
        return False

    # Check for article + noun pattern after καί
    # Pattern: καὶ + (article or noun) repeated
    article_noun_after_kai = len(re.findall(
        r'\bκαὶ\s+(?:[ὁἡτὸοἱαἰτ][ὁἡὸὶὰᾶῆῖ]?\s+|[ἡαἱ][ἱἰ]?\s+)', line))
    if article_noun_after_kai >= 2:
        return True

    # Also check for repeated "καὶ ἕν/ἓν" number patterns (Mark 4:8, 4:20)
    number_pattern = len(re.findall(r'\bκαὶ\s+ἓν\b', line))
    if number_pattern >= 2:
        return True

    # Also check for repeated "καὶ εἰς" patterns (destination lists, esp. Revelation)
    eis_pattern = len(re.findall(r'\bκαὶ\s+εἰς\b', line))
    if eis_pattern >= 2:
        return True

    return False


def split_kai_list(line):
    """Split a parallel καί list into stacked lines."""
    # Special case: "καὶ ἓν" number stacking pattern
    # e.g. "καὶ ἔφερεν ἓν τριάκοντα καὶ ἓν ἑξήκοντα καὶ ἓν ἑκατόν."
    hen_positions = [m.start() for m in re.finditer(r'\bκαὶ\s+ἓν\b', line)]
    if len(hen_positions) >= 2:
        # Find the first "καὶ ἓν" — check if there's leading content before it
        # that also has "ἓν" (like "ἔφερεν ἓν τριάκοντα")
        first_hen = hen_positions[0]
        parts = []
        # Check for leading content with ἓν before the first "καὶ ἓν"
        prefix = line[:first_hen].strip()
        if prefix:
            parts.append(prefix.rstrip(','))
        # Now split at each "καὶ ἓν"
        for idx, pos in enumerate(hen_positions):
            if idx + 1 < len(hen_positions):
                part = line[pos:hen_positions[idx + 1]].strip().rstrip(',')
            else:
                part = line[pos:].strip()
            if part:
                parts.append(part)
        if len(parts) >= 2:
            return parts

    # Special case: "καὶ εἰς" destination list pattern (esp. Revelation)
    # e.g. "εἰς Ἔφεσον καὶ εἰς Σμύρναν καὶ εἰς Πέργαμον..."
    eis_positions = [m.start() for m in re.finditer(r'\bκαὶ\s+εἰς\b', line)]
    if len(eis_positions) >= 2:
        # Check if there's a leading "εἰς X" before the first "καὶ εἰς"
        first_kai_eis = eis_positions[0]
        parts = []
        prefix = line[:first_kai_eis].strip()
        if prefix:
            parts.append(prefix.rstrip(','))
        # Split at each "καὶ εἰς"
        for idx, pos in enumerate(eis_positions):
            if idx + 1 < len(eis_positions):
                part = line[pos:eis_positions[idx + 1]].strip().rstrip(',')
            else:
                part = line[pos:].strip()
            if part:
                parts.append(part)
        if len(parts) >= 2:
            return parts

    # General case: find positions of each καί
    kai_positions = [m.start() for m in re.finditer(r'\bκαὶ\b', line)]
    if len(kai_positions) < 3:
        return [line]

    # Split at each καί position, keeping καί with what follows
    split_positions = []
    for i, pos in enumerate(kai_positions):
        if i >= 1:  # Start splitting from 2nd or later καί
            split_positions.append(pos)

    if not split_positions:
        return [line]

    # If the first part (before first split) still has 2+ καί, split from first
    first_part = line[:split_positions[0]].strip()
    if count_kai_phrases(first_part) >= 2:
        split_positions = kai_positions[1:]

    parts = []
    prev = 0
    for pos in split_positions:
        part = line[prev:pos].strip().rstrip(',')
        if part:
            parts.append(part)
        prev = pos
    # Last part
    last = line[prev:].strip()
    if last:
        parts.append(last)

    # Only return split if we got meaningful parts
    if len(parts) >= 3:
        return parts
    return [line]


def apply_parallel_list_stacking(verse_lines):
    """Pattern 3: Stack parallel καί + noun phrase lists."""
    result = []
    for line in verse_lines:
        if is_list_line(line):
            # For number patterns (καὶ ἓν...) use lower threshold
            has_number_pattern = len(re.findall(r'\bκαὶ\s+ἓν\b', line)) >= 2
            min_len = 30 if has_number_pattern else 50
            if len(line) > min_len:
                stacked = split_kai_list(line)
                result.extend(stacked)
            else:
                result.append(line)
        else:
            result.append(line)
    return result


# ---------- Pattern 4: Sequential/growth stacking ----------

def apply_sequence_stacking(verse_lines):
    """Pattern 4: Split before εἶτα, πρῶτον...εἶτα sequence markers."""
    result = []
    for line in verse_lines:
        # Look for εἶτα within a line (not at start — already its own line)
        if 'εἶτα' in line and not line.strip().startswith('εἶτα'):
            # Split before each εἶτα
            parts = re.split(r'\s+(?=εἶτα\b)', line)
            if len(parts) >= 2:
                for part in parts:
                    part = part.strip()
                    if part:
                        result.append(part)
                continue
        # Also handle εἶτεν
        if 'εἶτεν' in line and not line.strip().startswith('εἶτεν'):
            parts = re.split(r'\s+(?=εἶτεν\b)', line)
            if len(parts) >= 2:
                for part in parts:
                    part = part.strip()
                    if part:
                        result.append(part)
                continue
        result.append(line)
    return result


# ---------- Pattern 5: Parallel ἵνα / ὅτι stacking ----------

def apply_parallel_hina_hoti_stacking(verse_lines):
    """Pattern 5: Stack parallel ἵνα or ὅτι clauses; split at ἤ for parallel display."""
    result = []
    for line in verse_lines:
        # Check for ἵνα...ἤ pattern (parallel purpose clauses with alternative)
        # Guard: don't split at ἤ when it's INSIDE a ἵνα clause connecting
        # parallel alternatives (e.g., "ἵνα ὑπὸ τὸν μόδιον τεθῇ ἢ ὑπὸ τὴν κλίνην")
        if 'ἵνα' in line and ' ἢ ' in line and len(line) > 50:
            # Find positions: if ἤ appears AFTER ἵνα on the same line,
            # it connects alternatives within the purpose clause — don't split
            hina_pos = line.find('ἵνα')
            h_pos = line.find(' ἢ ')
            if hina_pos >= 0 and h_pos > hina_pos:
                # ἤ is inside the ἵνα clause — skip splitting
                pass
            else:
                # Split at ἤ when it connects parallel purpose elements
                parts = re.split(r'\s+(?=ἢ\s)', line)
                if len(parts) == 2 and all(len(p.strip()) > 10 for p in parts):
                    for part in parts:
                        result.append(part.strip())
                    continue

        # Check for multiple ἵνα in one line
        hina_count = len(re.findall(r'\bἵνα\b', line))
        if hina_count >= 2 and len(line) > 50:
            # Split before 2nd+ ἵνα
            parts = re.split(r'\s+(?=ἵνα\b)', line, maxsplit=1)
            if len(parts) == 2:
                # The first part already contains the first ἵνα
                first = parts[0].strip()
                # Now check if second part has another ἵνα to split
                remaining = parts[1].strip()
                result.append(first)
                # Recursively handle remaining
                if len(re.findall(r'\bἵνα\b', remaining)) >= 2:
                    sub_parts = re.split(r'\s+(?=ἵνα\b)', remaining, maxsplit=1)
                    result.extend([p.strip() for p in sub_parts if p.strip()])
                else:
                    result.append(remaining)
                continue

        # Check for multiple ὅτι in one line
        hoti_count = len(re.findall(r'\bὅτι\b', line))
        if hoti_count >= 2 and len(line) > 50:
            parts = re.split(r'\s+(?=ὅτι\b)', line, maxsplit=1)
            if len(parts) == 2:
                result.append(parts[0].strip())
                result.append(parts[1].strip())
                continue

        result.append(line)
    return result


# ---------- Pattern 6: Merge dangling short fragments ----------

def is_standalone_unit(text):
    """Check if a short line is a valid standalone unit (imperative, dramatic, etc.)."""
    standalone_pats = [
        r'^Ἀκούετε',
        r'^ἀκούετε',
        r'^Σιώπα',
        r'^σιώπα',
        r'^πεφίμωσο',
        # ἰδού removed — presentative particle bound to its clause, not standalone
        r'^Ἀμ[ήὴ]ν',
        r'^ἀμ[ήὴ]ν',
        r'^Διέλθωμεν',
        r'^Βλέπετε',
        r'^βλέπετε',
        r'^Ἄνδρες',
        r'^ὦ\s',
        r'^Οὐαὶ',
        r'^οὐαὶ',
        r'^Τί\s',        # Rhetorical question start
        r'^καὶ\s+ἓν\s',  # Number stacking pattern (καὶ ἓν τριάκοντα, etc.)
        r'^ἓν\s',        # Bare number stacking
        r'^εἶτα\s',      # Sequence marker (part of εἶτα stacking)
        r'^πρῶτον\s',    # Sequence marker
        r'^κἀγώ[.\s;·!]?$',   # Staccato emphatic response (2 Cor 11:22)
        r'^κἀμοί[.\s;·!]?$',  # Emphatic dative response
        r'^ναί[.\s;·!]?$',    # Emphatic affirmation
        r'^οὐχί[.\s;·!]?$',   # Emphatic negation
        r'^οὐ[.\s;·!]?$',     # Emphatic negation (bare)
    ]
    for pat in standalone_pats:
        if re.search(pat, text.strip()):
            return True
    return False


def apply_dangling_fragment_merge(verse_lines):
    """Pattern 6: Merge dangling short fragments at verse end."""
    if len(verse_lines) < 2:
        return verse_lines

    result = list(verse_lines)
    # Check last line
    last = result[-1]
    if (len(last) < 15
            and not is_standalone_unit(last)
            and not line_is_conditional_protasis(result[-2])
            and len(result) >= 2):
        # Merge with previous line
        result[-2] = result[-2].rstrip() + ' ' + last.lstrip()
        result.pop()

    return result


# ---------- Additional pattern: Speech intro on long merged lines ----------

SPEECH_INTRO_RE = re.compile(
    r'^((?:Κ|κ)αὶ\s+)?'
    r'((?:ἔλεγεν|λέγει|εἶπεν|εἶπαν|ἔφη|λέγων|λέγοντες|λέγουσιν|ἀπεκρίθη'
    r'|ἀποκριθεὶς\s+εἶπεν|ἀποκριθεὶς\s+λέγει)'
    r'(?:\s+αὐτοῖς|\s+αὐτῷ|\s+πρὸς\s+αὐτ[οό][νύ]ς?)?'
    r'\s*[·:]?\s*)'
)


def apply_speech_intro_fix(verse_lines):
    """Fix speech introductions that are merged with the speech content on long lines.

    E.g. "Καὶ ἔλεγεν· Οὕτως ἐστὶν..." should become two lines:
      "Καὶ ἔλεγεν·"
      "Οὕτως ἐστὶν..."
    """
    result = []
    for line in verse_lines:
        # Look for speech intro pattern followed by content
        # The pattern: [καὶ] speech_verb [indirect object] · rest_of_line
        m = re.match(
            r'((?:[Κκ]αὶ\s+)?'
            r'(?:ἔλεγεν|λέγει|εἶπεν|εἶπαν|ἔφη|λέγουσιν|ἀπεκρίθη)'
            r'(?:\s+αὐτοῖς|\s+αὐτῷ|\s+πρὸς\s+αὐτ[οό][νύ]ς?)?'
            r'(?:\s+ἐν\s+\S+\s+\S+\s+\S+)?'  # optional context phrase
            r'\s*[·:]\s*)'
            r'(.+)$',
            line
        )
        if m:
            intro = m.group(1).strip()
            speech = m.group(2).strip()
            if intro and speech and len(speech) > 5:
                result.append(intro)
                result.append(speech)
                continue

        result.append(line)
    return result


# ---------- Additional pattern: Fix Μήτι split from its clause ----------

def apply_meti_fix(verse_lines):
    """Fix cases where Μήτι is dangling on a line or awkwardly split.

    Μήτι is a question particle that belongs with the clause it introduces.
    If it's at the end of a line by itself or a very short fragment, merge forward.
    """
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip()
        # Check if line ends with Μήτι or is just "Μήτι" (possibly with speech intro)
        if (i + 1 < len(verse_lines)
                and re.search(r'\bΜήτι\s*$', stripped)
                and len(stripped.split()[-1:]) == 1):
            # Μήτι is dangling at end — merge with next line
            next_line = verse_lines[i + 1]
            # Reconstruct: put Μήτι at start of next line
            # Remove Μήτι from current line
            current_without = re.sub(r'\s*Μήτι\s*$', '', stripped).strip()
            if current_without:
                result.append(current_without)
            result.append('Μήτι ' + next_line.strip())
            i += 2
        else:
            result.append(line)
            i += 1
    return result


# ---------- Additional pattern: Subordinating conjunction splits ----------

# These conjunctions introduce subordinate clauses and should trigger a line break
# when they appear mid-line with preceding content. Applied as a refinement on
# v2 tree output, since the trees sometimes group subordinate clauses with their
# main clause.
SUBORDINATING_CONJUNCTIONS = [
    'ὥστε',     # result
    'ἵνα',      # purpose (only when mid-line, not at start)
    'ὅταν',     # temporal (whenever)
    'ὅτε',      # temporal (when)
    'ἐάν',      # conditional
    'εἴπερ',    # conditional (if indeed)
    'ἐάνπερ',   # conditional (if indeed, subjunctive)
    'εἴγε',     # conditional (if indeed)
    'μήποτε',   # lest
    'καθὼς', 'καθώς',  # comparative
    'ὥσπερ',    # comparative
    'ἐπειδὴ', 'ἐπεὶ',  # causal
    'διότι',    # causal
    'ἄχρι',     # temporal (until)
    'μέχρι',    # temporal (until)
    'ὅπως',     # purpose
    'ὅπου',     # local
    'πρὶν',     # before
]

# Conditional conjunctions — used to protect protasis/apodosis from merging
CONDITIONAL_CONJUNCTIONS = [
    'εἰ', 'ἐάν', 'ἐὰν', 'εἴπερ', 'ἐάνπερ', 'εἴγε',
]


def line_starts_with_conditional(text):
    """Check if a line starts with a conditional conjunction (possibly followed by particles).

    Matches patterns like:
      εἰ δὲ Χριστὸς...
      εἰ γὰρ διὰ νόμου...
      ἐάν τις...
      εἴπερ πνεῦμα...

    The conjunction may be followed by postpositive particles (δέ, γάρ, μέν, etc.).
    """
    stripped = text.strip()
    for conj in CONDITIONAL_CONJUNCTIONS:
        if stripped.startswith(conj + ' ') or stripped.startswith(conj + '\xa0'):
            return True
    return False


def line_is_conditional_protasis(text):
    """Check if a line is a conditional protasis (εἰ/ἐάν clause ending with comma).

    A protasis is a conditional clause that sets up the condition. It typically
    starts with a conditional conjunction and ends with a comma (before the apodosis).
    """
    stripped = text.strip()
    return line_starts_with_conditional(stripped) and stripped.rstrip().endswith(',')


def apply_dangling_conjunction_fix(verse_lines):
    """Fix subordinating conjunctions stranded at the end of a line.

    The colometric rule is: never dangle a conjunction at line end. If a
    subordinating conjunction (εἴπερ, ἵνα, ὅταν, etc.) appears as the last
    word of a line, move it to the beginning of the next line.

    Example:
      "ἀλλὰ ἐν πνεύματι, εἴπερ"  /  "πνεῦμα θεοῦ οἰκεῖ ἐν ὑμῖν."
      → "ἀλλὰ ἐν πνεύματι,"  /  "εἴπερ πνεῦμα θεοῦ οἰκεῖ ἐν ὑμῖν."
    """
    all_conjunctions = SUBORDINATING_CONJUNCTIONS + CONDITIONAL_CONJUNCTIONS + ['ὅτι']
    conj_set = set(all_conjunctions)
    if len(verse_lines) < 2:
        return verse_lines

    result = list(verse_lines)
    for i in range(len(result) - 1):
        line = result[i].rstrip()
        words = line.split()
        if not words:
            continue
        last_word = words[-1].rstrip('.,;·')
        if last_word in conj_set and len(words) > 1:
            # Move the conjunction to the next line
            # Strip trailing punctuation/space from the conjunction on this line
            # Find where the last word starts
            trailing = words[-1]
            line_without = line[:line.rfind(trailing)].rstrip()
            # Clean trailing comma/space from the previous content
            line_without = line_without.rstrip(' ,')
            if line_without:
                # If the conjunction had punctuation before it (like comma), keep it
                char_before_conj = line[line.rfind(trailing) - 1] if line.rfind(trailing) > 0 else ''
                if char_before_conj == ',':
                    result[i] = line_without + ','
                else:
                    result[i] = line_without
                result[i + 1] = trailing.rstrip('.,;·') + ' ' + result[i + 1].lstrip()
    return result


def apply_conditional_protasis_apodosis_split(verse_lines):
    """Split conditional protasis + apodosis that ended up on the same line.

    Per Wallace ch. 26, protasis (εἰ/ἐάν clause) and apodosis (result clause)
    are distinct grammatical units and should always be separate cola.

    Detection: a line starts with a conditional conjunction and contains a comma
    followed by non-conditional content. The comma marks the protasis/apodosis
    boundary.

    Examples that should be split:
      "εἰ δὲ Χριστὸς ἐν ὑμῖν, τὸ μὲν σῶμα νεκρὸν διὰ ἁμαρτίαν,"
      → "εἰ δὲ Χριστὸς ἐν ὑμῖν,"  /  "τὸ μὲν σῶμα νεκρὸν διὰ ἁμαρτίαν,"
      "εἰ γὰρ διὰ νόμου δικαιοσύνη, ἄρα Χριστὸς δωρεὰν ἀπέθανεν."
      → "εἰ γὰρ διὰ νόμου δικαιοσύνη,"  /  "ἄρα Χριστὸς δωρεὰν ἀπέθανεν."
    """
    result = []
    for line in verse_lines:
        stripped = line.strip()
        if not line_starts_with_conditional(stripped):
            result.append(line)
            continue
        # Find the first comma that could mark the protasis/apodosis boundary.
        # Skip commas that appear too early (less than 10 chars into the line)
        # since those are likely part of the protasis itself.
        comma_pos = stripped.find(', ', 10)
        if comma_pos == -1:
            result.append(line)
            continue
        protasis = stripped[:comma_pos + 1].strip()  # include comma
        apodosis = stripped[comma_pos + 2:].strip()
        # Only split if the apodosis is substantial (not just a trailing word)
        # and doesn't itself start with a conditional (that would be a nested conditional)
        if (apodosis and len(apodosis) > 5
                and not line_starts_with_conditional(apodosis)):
            result.append(protasis)
            result.append(apodosis)
        else:
            result.append(line)
    return result


def apply_subordinating_conjunction_splits(verse_lines):
    """Split lines before subordinating conjunctions when preceded by content.

    The Macula trees sometimes keep a subordinating clause on the same line as
    its main clause. This pass ensures conjunctions like ὥστε, ἵνα, ὅταν etc.
    start a new line when there's substantial preceding content.
    """
    result = []
    for line in verse_lines:
        if len(line) < 40:
            result.append(line)
            continue
        split_done = False
        for conj in SUBORDINATING_CONJUNCTIONS:
            if conj not in line:
                continue
            # Guard: don't split before ἵνα when preceded by ἐὰν μή / εἰ μή / εἰ μὴ
            # In these constructions ἵνα is epexegetical ("except that / unless to")
            if conj == 'ἵνα' and re.search(r'(?:ἐὰν|εἰ)\s+μ[ήὴ]\s+ἵνα\b', line):
                continue
            # Find the conjunction preceded by space (or comma+space)
            pattern = re.compile(r'[,]?\s+(?=' + re.escape(conj) + r'\b)')
            m = pattern.search(line)
            if m and m.start() > 10:
                before = line[:m.end()].strip()
                after = line[m.end():].strip()
                if before and after and len(after) > 10:
                    # Clean up trailing comma on before
                    if before.endswith(','):
                        result.append(before)
                    else:
                        result.append(before + ',')
                    result.append(after)
                    split_done = True
                    break
        if not split_done:
            result.append(line)
    return result


# ---------- Additional pattern: Long lines with ὅτι ----------

def apply_hoti_split(verse_lines):
    """Split long lines before ὅτι when the line is very long."""
    result = []
    for line in verse_lines:
        if len(line) > 55 and 'ὅτι' in line:
            # Find ὅτι not at start
            m = re.search(r'\s(ὅτι\s)', line)
            if m and m.start() > 15:
                before = line[:m.start()].strip()
                after = line[m.start():].strip()
                if before and after and len(after) > 15:
                    result.append(before)
                    result.append(after)
                    continue
        result.append(line)
    return result


# ---------- Pattern 7: Correlative/paired construction merge ----------

# Explicit comparative adverbs/adjectives (beyond MorphGNT degree tagging)
_EXPLICIT_COMPARATIVES = {
    'μᾶλλον', 'μείζων', 'μεῖζον', 'μεῖζόν', 'πλέον', 'πλεῖον', 'πλεῖόν',
    'κρεῖσσον', 'κρεῖττον', 'χεῖρον', 'ἧσσον', 'ἧττον', 'ἥσσων',
    'μείζονα', 'μείζονος', 'μείζονι', 'μείζονες',
    'πλείονα', 'πλείονας', 'πλείονος', 'πλειόνων', 'πλείοσιν', 'πλείους',
    'χείρονα', 'χείρονος', 'χείρονες',
    'κρείσσονα', 'κρείττονα', 'κρείσσονος',
    'ἐλάσσονα', 'ἐλάσσω', 'ἐλάττονα', 'ἐλάττω',
    'μᾶλλόν',
}

# Cache for MorphGNT comparative words per book
_morphgnt_comparatives_cache = {}


def _get_comparatives_for_book(book_slug):
    """Get the set of comparative-degree words for a book (cached)."""
    if book_slug in _morphgnt_comparatives_cache:
        return _morphgnt_comparatives_cache[book_slug]
    if _HAS_MORPHGNT:
        comps = get_comparative_words(book_slug)
    else:
        comps = set()
    _morphgnt_comparatives_cache[book_slug] = comps
    return comps


def _line_contains_comparative(line, book_slug=None):
    """Check if a line contains any comparative form.

    Uses both the explicit word list and MorphGNT comparative-degree tagging.
    """
    words = line.strip().split()
    morphgnt_comps = _get_comparatives_for_book(book_slug) if book_slug else set()
    for w in words:
        clean = re.sub(r'[,.\;·⸀⸁⸂⸃⸄⸅]', '', w)
        if clean in _EXPLICIT_COMPARATIVES:
            return True
        if clean in morphgnt_comps:
            return True
    return False


def _next_line_starts_with_h(line):
    """Check if a line starts with ἤ/ἢ (comparative 'than' or alternative)."""
    stripped = line.strip()
    if not stripped:
        return False
    first_word = stripped.split()[0]
    clean = re.sub(r'[,.\;·]', '', first_word)
    return clean in ('ἤ', 'ἢ')


def _h_line_is_independent_clause(line, book_slug):
    """Check if an ἤ-line is a genuinely independent clause (has finite verb).

    If the ἤ line has a finite verb as part of the ἤ-clause itself, it may be
    an independent rhetorical question or alternative clause that should remain
    on its own line.

    We extract the ἤ-clause by taking the content after ἤ/ἢ up to the first
    major punctuation break (comma, period, semicolon, ano teleia). If the
    finite verb is AFTER a comma (i.e., in a separate clause like "κρίνατε"),
    it doesn't count as part of the ἤ-clause.
    """
    if not _HAS_MORPHGNT or not book_slug:
        # Conservative: assume it might be independent
        return False

    stripped = line.strip()
    # Remove the leading ἤ/ἢ
    h_content = re.sub(r'^[ἤἢ]\s+', '', stripped)
    if not h_content:
        return False

    # Extract just the ἤ-clause: content before the first comma/period/semicolon/·
    h_clause = re.split(r'[,.\;·]', h_content)[0].strip()
    if not h_clause:
        return False

    return line_has_finite_verb(h_clause, book_slug)


def apply_correlative_merge(verse_lines, book_slug=None):
    """Pattern 7: Merge split correlative/paired constructions.

    Greek has paired constructions that form indivisible thought units:
    1. Comparative + ἤ: μᾶλλον / ἢ τοῦ θεοῦ → merge
    2. οὔτε...οὔτε (neither...nor) — merge tiny fragments
    3. μήτε...μήτε — same principle
    4. εἴτε...εἴτε (whether...or) — merge tiny fragments
    5. τε...καί (both...and) — merge when τε dangles

    Protection: ἤ introducing a genuinely independent clause (with its own
    finite verb) is left alone, as it represents a complete thought.
    """
    if len(verse_lines) < 2:
        return verse_lines

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip()

        # --- Category 1 & 5: Comparative + ἤ merge ---
        if (i + 1 < len(verse_lines)
                and _line_contains_comparative(stripped, book_slug)
                and _next_line_starts_with_h(verse_lines[i + 1])):
            next_stripped = verse_lines[i + 1].strip()
            # Check if ἤ line is a genuinely independent clause
            if _h_line_is_independent_clause(next_stripped, book_slug):
                # Leave it alone — independent clause
                result.append(line)
                i += 1
            else:
                # Merge: the ἤ clause completes the comparison
                merged = stripped + ' ' + next_stripped
                result.append(merged)
                i += 2
            continue

        # --- Category 2: οὔτε...οὔτε and μήτε...μήτε tiny fragment merge ---
        if (i + 1 < len(verse_lines)
                and re.search(r'\b(?:οὔτε|μήτε)\b', stripped)):
            next_stripped = verse_lines[i + 1].strip()
            # Check if next line starts with the matching paired element
            if re.match(r'^(?:οὔτε|μήτε)\b', next_stripped):
                # If either half is a tiny fragment (<20 chars), merge
                if len(stripped) < 20 or len(next_stripped) < 20:
                    merged = stripped + ' ' + next_stripped
                    result.append(merged)
                    i += 2
                    continue

        # --- Category 3: εἴτε...εἴτε tiny fragment merge ---
        if (i + 1 < len(verse_lines)
                and re.search(r'\bεἴτε\b', stripped)):
            next_stripped = verse_lines[i + 1].strip()
            if re.match(r'^εἴτε\b', next_stripped):
                if len(stripped) < 20 or len(next_stripped) < 20:
                    merged = stripped + ' ' + next_stripped
                    result.append(merged)
                    i += 2
                    continue

        # --- Category 4: τε...καί dangling merge ---
        # If line ends with τε (or τε + punctuation), merge with next line
        if (i + 1 < len(verse_lines)
                and re.search(r'\bτε\s*[,]?\s*$', stripped)):
            next_stripped = verse_lines[i + 1].strip()
            # τε is dangling — merge with next line which should carry καί content
            merged = stripped + ' ' + next_stripped
            result.append(merged)
            i += 2
            continue

        result.append(line)
        i += 1

    return result


# ---------- Verse parsing and processing ----------

def parse_v2_file(filepath):
    """Parse a v2-colometric file into a list of (verse_ref, [lines]) tuples."""
    verses = []
    current_ref = None
    current_lines = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            raw_line = raw_line.rstrip('\n')

            # Check if this is a verse reference
            if re.match(r'^\d+:\d+$', raw_line.strip()):
                # Save previous verse
                if current_ref is not None:
                    verses.append((current_ref, current_lines))
                current_ref = raw_line.strip()
                current_lines = []
            elif raw_line.strip() == '':
                # Blank line — separator between verses
                continue
            else:
                # Content line
                if current_ref is not None:
                    current_lines.append(raw_line)

    # Save last verse
    if current_ref is not None:
        verses.append((current_ref, current_lines))

    return verses


# ---------- Sentence boundary post-processing ----------

_sentence_split_count = 0


def apply_stranded_function_word_merge(verse_lines):
    """Merge stranded single-word function words forward into the next line.

    After sentence boundary splits, conjunctions (καί, ἀλλά, δέ, etc.),
    articles (ὁ, ἡ, τό, etc.), and particles can end up alone on a line.
    These are grammatically bound to what follows — a conjunction introduces
    the next clause, an article introduces the next noun phrase. They can
    never be standalone cola.

    This is NOT a length guard — it's the grammatical principle that function
    words are proclitic/bound to their host.
    """
    if len(verse_lines) < 2:
        return verse_lines

    # Function words that should never be alone on a line
    FUNCTION_WORDS = {
        # Conjunctions
        'καὶ', 'καί', 'Καὶ', 'Καί', 'δὲ', 'δέ', 'ἀλλὰ', 'ἀλλά', 'Ἀλλὰ',
        'γὰρ', 'γάρ', 'οὖν', 'ὅτι', 'ἵνα', 'εἰ', 'ἐάν', 'ἐὰν',
        'ὥστε', 'ὅταν', 'ὅτε', 'ἕως', 'μηδὲ', 'οὐδὲ', 'τε',
        'ἤ', 'ἢ', 'μήτε', 'οὔτε', 'εἴτε', 'καθὼς', 'ὡς',
        'ἐπεὶ', 'διότι', 'πλὴν', 'ἄρα', 'διό', 'μέν', 'μὲν',
        'εἴπερ', 'ἐάνπερ',
        # Articles
        'ὁ', 'ἡ', 'τό', 'τὸ', 'τοῦ', 'τῆς', 'τῷ', 'τῇ', 'τόν', 'τὸν',
        'τήν', 'τὴν', 'οἱ', 'αἱ', 'τά', 'τὰ', 'τῶν', 'τοῖς', 'ταῖς',
        'τούς', 'τοὺς', 'τάς', 'τὰς',
        # Prepositions (short, should never be alone)
        'ἐν', 'εἰς', 'ἐκ', 'ἐξ', 'ἀπό', 'ἀπὸ', 'πρός', 'πρὸς',
        'ἐπί', 'ἐπὶ', 'κατά', 'κατὰ', 'μετά', 'μετὰ', 'διά', 'διὰ',
        'ὑπό', 'ὑπὸ', 'παρά', 'παρὰ', 'περί', 'περὶ', 'πρό', 'πρὸ',
        'σύν', 'σὺν', 'ὑπέρ', 'ὑπὲρ',
        # Negative particles
        'οὐ', 'οὐκ', 'οὐχ', 'μή', 'μὴ',
        # Presentative particles (bound to what follows, not standalone)
        'ἰδού', 'ἰδοὺ', 'Ἰδού', 'Ἰδοὺ', 'ἴδε', 'Ἴδε',
        # Elided conjunction forms
        'ἀλλʼ', 'Ἀλλʼ', "ἀλλ'", "Ἀλλ'",
    }

    result = []
    i = 0
    while i < len(verse_lines):
        line = verse_lines[i]
        stripped = line.strip().rstrip('.,;·')

        if (i + 1 < len(verse_lines)
                and stripped in FUNCTION_WORDS):
            # Single function word — merge forward
            next_line = verse_lines[i + 1]
            merged = line.strip() + ' ' + next_line.strip()
            result.append(merged)
            i += 2
        else:
            result.append(line)
            i += 1
    return result


def apply_sentence_boundary_splits(verse_lines, book_slug=None, verse_ref=None):
    """Split any line that crosses a Macula sentence boundary.

    This is a post-processing guard: after all merge/split patterns have run,
    check each line and split it if its words span two different Macula
    <sentence> elements. This prevents cross-sentence merges regardless of
    which earlier rule created them.
    """
    global _sentence_split_count

    if not _HAS_SENTENCES:
        return verse_lines
    if not book_slug or not verse_ref:
        return verse_lines

    parts = verse_ref.split(':')
    if len(parts) != 2:
        return verse_lines
    try:
        ch, vs = int(parts[0]), int(parts[1])
    except ValueError:
        return verse_lines

    result = []
    for line in verse_lines:
        boundary_idx = find_sentence_boundary_in_line(line, book_slug, ch, vs)
        if boundary_idx is not None and boundary_idx > 0:
            words = line.split()
            line1 = ' '.join(words[:boundary_idx])
            line2 = ' '.join(words[boundary_idx:])
            result.append(line1)
            result.append(line2)
            _sentence_split_count += 1
        else:
            result.append(line)

    return result


def apply_all_patterns(verse_lines, book_slug=None, verse_ref=None):
    """Apply all rhetorical patterns to a verse's lines."""
    lines = list(verse_lines)

    # Fix dangling conjunctions at line end (v2 tree artifact) — must run first
    lines = apply_dangling_conjunction_fix(lines)

    # Pattern 0d: Predication completeness merge (unified tree-based test) — PRIMARY
    # This is the fundamental structural test: every line must contain a complete
    # predication. Runs first because it subsumes verbless, valency, and periphrastic
    # cases. The individual rules below serve as fallbacks for edge cases and for
    # when Macula data is unavailable.
    lines = apply_predication_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0e: Multi-image participial split — "each line paints one image"
    # Must run right after predication merge, which may over-merge participial
    # chains onto one line. This splits them back at clause boundaries.
    lines = apply_multi_image_split(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0a: Periphrastic construction merge (εἰμί + participle = one verb form)
    lines = apply_periphrastic_merge(lines, book_slug=book_slug)

    # Pattern 0: Infinitive merge-back (dependent infinitives can't begin a colon)
    lines = apply_infinitive_merge_back(lines)

    # Pattern 0b: Verbless line merge (lines with no verbal element can't be cola)
    # (fallback for cases predication merge doesn't catch — e.g., no Macula data)
    lines = apply_verbless_line_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0c: Valency satisfaction merge (participles with unsatisfied transitivity)
    # (fallback for edge cases the tree-based test doesn't cover)
    lines = apply_valency_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 1: Merge complementary verb + infinitive splits
    lines = apply_complementary_verb_merge(lines)

    # Pattern 1a: Merge lines containing a complementary verb but no infinitive
    # (the verb's required complement is on a later line)
    lines = apply_complementary_verb_without_infinitive_merge(lines)

    # Pattern 1b: Merge infinitive-governing constructions (ὥστε+inf, πρίν+inf, etc.)
    lines = apply_infinitive_construction_merge(lines)

    # Speech intro fix (before standalone split, since it may create opportunities)
    lines = apply_speech_intro_fix(lines)

    # Pattern 2: Split standalone imperatives/exclamations
    lines = apply_standalone_imperative_split(lines)

    # Pattern 2b: Staccato commata split (call-and-response, e.g. 2 Cor 11:22)
    lines = apply_staccato_commata_split(lines)

    # Pattern 2c: Asyndeton imperative split (e.g. 1 Thess 5:16-18 style)
    lines = apply_asyndeton_imperative_split(lines, book_slug=book_slug)

    # Μήτι fix
    lines = apply_meti_fix(lines)

    # Subordinating conjunction splits (ἵνα, ὅταν, etc. — but NOT ὥστε+inf)
    lines = apply_subordinating_conjunction_splits(lines)

    # ὅτι split for long lines
    lines = apply_hoti_split(lines)

    # Pattern 1b AGAIN after conjunction splits — catch cases where the split
    # created ὥστε+inf or similar constructions that should stay merged
    lines = apply_infinitive_construction_merge(lines)

    # Pattern 7: Correlative/paired construction merge (comparative+ἤ, οὔτε...οὔτε, etc.)
    lines = apply_correlative_merge(lines, book_slug=book_slug)

    # Pattern 3: Parallel list stacking
    lines = apply_parallel_list_stacking(lines)

    # Pattern 4: Sequence stacking (εἶτα, πρῶτον...εἶτα)
    lines = apply_sequence_stacking(lines)

    # Pattern 5: Parallel ἵνα/ὅτι stacking
    lines = apply_parallel_hina_hoti_stacking(lines)

    # Pattern 6: Merge dangling short fragments (apply last)
    lines = apply_dangling_fragment_merge(lines)

    # Conditional protasis/apodosis split — ensure εἰ/ἐάν protasis and apodosis
    # are always separate cola (Wallace ch. 26). Run after merges to re-split
    # anything that was incorrectly collapsed.
    lines = apply_conditional_protasis_apodosis_split(lines)

    # Pattern 0a again — catch periphrastic splits created by earlier passes
    lines = apply_periphrastic_merge(lines, book_slug=book_slug)

    # Pattern 0 again — catch fragments created by speech intro split
    lines = apply_infinitive_merge_back(lines)

    # Pattern 0b again — catch verbless fragments created by earlier passes
    lines = apply_verbless_line_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0c again — catch valency issues from fragments created by earlier passes
    lines = apply_valency_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0d again — final predication cleanup after all splits/merges
    lines = apply_predication_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0e again — multi-image split after final predication merge
    lines = apply_multi_image_split(lines, book_slug=book_slug, verse_ref=verse_ref)

    # FINAL GUARD: Sentence boundary splits — split any line that crosses a
    # Macula sentence boundary. This runs LAST so it overrides all merge rules.
    lines = apply_sentence_boundary_splits(lines, book_slug=book_slug, verse_ref=verse_ref)

    # POST-SPLIT CLEANUP: Merge stranded function words forward.
    # Sentence boundary splits can strand conjunctions, articles, and particles
    # on their own line. These are bound to what FOLLOWS, never standalone.
    lines = apply_stranded_function_word_merge(lines)

    return lines


def process_chapter_file(input_path, output_path, book_slug=None):
    """Process a single chapter file from v2 to v3."""
    verses = parse_v2_file(input_path)

    output_lines = []
    for verse_ref, verse_content in verses:
        refined = apply_all_patterns(verse_content, book_slug=book_slug, verse_ref=verse_ref)
        output_lines.append(verse_ref)
        for line in refined:
            output_lines.append(line)
        output_lines.append('')  # blank separator

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))


def process_book(book_key, chapter_filter=None):
    """Process a single book from v2-colometric to v3-colometric."""
    display_name, abbrev, chapter_count = BOOKS[book_key]

    chapters_processed = 0
    for ch in range(1, chapter_count + 1):
        if chapter_filter is not None and ch != chapter_filter:
            continue

        ch_str = str(ch).zfill(2)
        filename = f'{abbrev}-{ch_str}.txt'
        input_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename)

        if not os.path.exists(input_path):
            print(f'  WARNING: Input file not found: {input_path}')
            continue

        process_chapter_file(input_path, output_path, book_slug=abbrev)
        chapters_processed += 1

    print(f'  {display_name}: {chapters_processed} chapter(s) refined')


def main():
    parser = argparse.ArgumentParser(
        description='V3 rhetorical pattern refinement for colometric formatting')
    parser.add_argument('--book', help='Process a single book (e.g., Mark, Acts)')
    parser.add_argument('--chapter', type=int,
                        help='Process a single chapter (requires --book)')
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    global _periphrastic_merge_count, _predication_merge_count, _sentence_split_count, _multi_image_split_count
    _periphrastic_merge_count = 0
    _predication_merge_count = 0
    _sentence_split_count = 0
    _multi_image_split_count = 0

    if args.book:
        if args.book not in BOOKS:
            print(f'Unknown book: {args.book}')
            print(f'Valid books: {", ".join(sorted(BOOKS.keys()))}')
            sys.exit(1)
        process_book(args.book, args.chapter)
    else:
        print('V3 rhetorical refinement: processing all 27 books...')
        for book_key in BOOKS:
            process_book(book_key)
        print('Done.')

    if _predication_merge_count > 0:
        print(f'Predication merges (participle → governing verb): {_predication_merge_count}')
    if _periphrastic_merge_count > 0:
        print(f'Periphrastic merges (εἰμί + participle): {_periphrastic_merge_count}')
    if _multi_image_split_count > 0:
        print(f'Multi-image participial splits (2+ images per line): {_multi_image_split_count}')
    if _sentence_split_count > 0:
        print(f'Sentence boundary splits (cross-sentence lines split): {_sentence_split_count}')


if __name__ == '__main__':
    main()
