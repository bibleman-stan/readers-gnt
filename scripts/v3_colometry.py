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
    # Verbs of obligation (δεῖ takes infinitive directly, usually not split)
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

# Global counter for reporting
_periphrastic_merge_count = 0


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
    ; (question mark).
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in '.·;'


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
            # This line has no verbal element and no predicate — merge forward
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


# ---------- Pattern 2: Standalone imperatives/exclamations ----------

# Patterns for short imperatives/exclamations that should be their own line
STANDALONE_PATTERNS = [
    # Single-word commands followed by punctuation
    re.compile(r'^(Ἀκούετε[.·;!])\s+(.+)$'),
    re.compile(r'^(ἰδο[ὺύ][.·;!,]?)\s+(.+)$', re.IGNORECASE),
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
        if 'ἵνα' in line and ' ἢ ' in line and len(line) > 50:
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
        r'^ἰδο[ὺύ]',
        r'^Ἰδο[ὺύ]',
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


def apply_all_patterns(verse_lines, book_slug=None, verse_ref=None):
    """Apply all rhetorical patterns to a verse's lines."""
    lines = list(verse_lines)

    # Fix dangling conjunctions at line end (v2 tree artifact) — must run first
    lines = apply_dangling_conjunction_fix(lines)

    # Pattern 0a: Periphrastic construction merge (εἰμί + participle = one verb form)
    lines = apply_periphrastic_merge(lines, book_slug=book_slug)

    # Pattern 0: Infinitive merge-back (dependent infinitives can't begin a colon)
    lines = apply_infinitive_merge_back(lines)

    # Pattern 0b: Verbless line merge (lines with no verbal element can't be cola)
    lines = apply_verbless_line_merge(lines, book_slug=book_slug, verse_ref=verse_ref)

    # Pattern 0c: Valency satisfaction merge (participles with unsatisfied transitivity)
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

    global _periphrastic_merge_count
    _periphrastic_merge_count = 0

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

    if _periphrastic_merge_count > 0:
        print(f'Periphrastic merges (εἰμί + participle): {_periphrastic_merge_count}')


if __name__ == '__main__':
    main()
