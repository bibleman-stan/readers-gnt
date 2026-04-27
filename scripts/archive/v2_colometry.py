#!/usr/bin/env python3
"""
v2 colometric formatter — Macula syntax-tree clause boundaries + SBLGNT text.

Uses Macula Greek Lowfat XML syntax trees as the primary source of clause
boundaries, with cleanup/merging rules to handle fragments. The SBLGNT source
text provides the actual words (preserving all punctuation, accents, breathing
marks exactly).

Usage:
    py -3 scripts/archive/v2_colometry.py                              # all books
    py -3 scripts/archive/v2_colometry.py --book Acts                  # one book
    py -3 scripts/archive/v2_colometry.py --book Acts --chapter 1      # one chapter

Input:
    data/text-files/sblgnt-source/*.txt   (canonical text)
    research/macula-greek/SBLGNT/lowfat/  (clause boundaries via macula_clauses)
Output:
    data/text-files/v2-colometric/{NN-book}/*.txt
"""

import re
import os
import sys
import argparse
from collections import defaultdict

# Ensure sibling imports work when run as script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from macula_clauses import (
    get_chapter_clauses_detailed,
    ClauseInfo,
    _parse_ref,
    _resolve_book,
    _SLUG_TO_MACULA,
)

try:
    from morphgnt_lookup import line_has_verbal_element
    _HAS_MORPHGNT = True
except ImportError:
    _HAS_MORPHGNT = False

# ---------- configuration ----------

SOURCE_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'sblgnt-source')
OUTPUT_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v2-colometric')

# Book metadata: source filename -> (display name, output abbreviation, chapter count)
# Same as auto_colometry.py
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

# Map from output slug to source filename key
_SLUG_TO_BOOK_KEY = {v[1]: k for k, v in BOOKS.items()}

# Map from output abbreviation -> NN-book subfolder name (e.g. 'mark' -> '02-mark').
# Position within BOOKS (canonical NT order) supplies the NN prefix.
BOOK_SUBDIR = {
    abbrev: f'{idx:02d}-{abbrev}'
    for idx, (_display, abbrev, _count) in enumerate(BOOKS.values(), start=1)
}


def book_output_dir(abbrev):
    """Return the per-book output subfolder under OUTPUT_DIR for a given abbrev."""
    return os.path.join(OUTPUT_DIR, BOOK_SUBDIR[abbrev])

# Apparatus markers to strip from output text
APPARATUS_RE = re.compile(r'[⸀⸁⸂⸃⸄⸅]')

# Particles / conjunctions that should not stand alone as a line
MERGE_PARTICLES = {
    'μέν', 'μὲν', 'δέ', 'δὲ', 'καί', 'καὶ', 'τε', 'γάρ', 'γὰρ',
    'οὖν', 'ἀλλά', 'ἀλλὰ', 'ἤ', 'ἢ', 'οὔτε', 'μήτε', 'εἴτε',
}


# ---------- SBLGNT source parsing ----------

def parse_source_file(filepath):
    """Parse an SBLGNT source file into {chapter: {verse: text}}."""
    chapters = {}
    book_title = ''

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # First line is the book title in Greek
            if not book_title and not re.match(
                r'(?:Matt|Mark|Luke|John|Acts|Rom|[123]?(?:Cor|Thess|Tim|Pet|John)'
                r'|Gal|Eph|Phil|Col|Titus|Phlm|Heb|Jas|Jude|Rev)\s',
                line
            ):
                book_title = line
                continue

            # Parse verse line: "Book Chapter:Verse\ttext"
            match = re.match(r'\S+\s+(\d+):(\d+)\t(.+)', line)
            if match:
                chapter = int(match.group(1))
                verse = int(match.group(2))
                text = match.group(3)
                if chapter not in chapters:
                    chapters[chapter] = {}
                chapters[chapter][verse] = text

    return book_title, chapters


def clean_apparatus(text):
    """Remove SBLGNT apparatus markers, normalize whitespace."""
    text = APPARATUS_RE.sub('', text)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def get_sblgnt_words(verse_text):
    """Split SBLGNT verse text into positional words (1-indexed).

    Returns list of (position, raw_word) where raw_word still has punctuation
    but apparatus markers are stripped.
    """
    cleaned = clean_apparatus(verse_text)
    words = cleaned.split()
    return [(i + 1, w) for i, w in enumerate(words)]


# ---------- Macula → SBLGNT alignment ----------

def get_clause_word_positions(clause_info, chapter, verse):
    """Extract word positions belonging to a specific verse from a ClauseInfo.

    Returns sorted list of word positions (1-indexed) that fall in the given
    chapter:verse.
    """
    positions = []
    for ref, _text in clause_info.words:
        book, ch, vs, pos = _parse_ref(ref)
        if ch == chapter and vs == verse and pos is not None:
            positions.append(pos)
    positions.sort()
    return positions


def build_verse_cola(sblgnt_words, clause_infos, chapter, verse):
    """Build colometric lines for one verse.

    Strategy: assign each word position a clause label, then find break points
    where the label changes. Each contiguous run of words becomes one line.
    This guarantees output lines are always contiguous surface-order text.

    Args:
        sblgnt_words: [(pos, raw_word), ...] from SBLGNT source
        clause_infos: [ClauseInfo, ...] from Macula for this verse
        chapter: chapter number
        verse: verse number

    Returns:
        List of text lines (cola) using SBLGNT words.
    """
    if not sblgnt_words:
        return []

    pos_to_word = {pos: word for pos, word in sblgnt_words}
    all_positions = sorted(pos_to_word.keys())
    n = len(all_positions)

    if not clause_infos:
        return [' '.join(pos_to_word[p] for p in all_positions)]

    # For each clause, get the word positions in THIS verse
    clause_pos_sets = []
    for ci_idx, ci in enumerate(clause_infos):
        positions = get_clause_word_positions(ci, chapter, verse)
        if positions:
            clause_pos_sets.append((ci_idx, positions))

    if not clause_pos_sets:
        return [' '.join(pos_to_word[p] for p in all_positions)]

    # Assign each position a clause label. If multiple clauses claim the
    # same position, use the first one (lowest ci_idx).
    pos_label = {}
    for ci_idx, positions in clause_pos_sets:
        for pos in positions:
            if pos not in pos_label:
                pos_label[pos] = ci_idx

    # Any unclaimed positions: inherit label from the nearest preceding
    # claimed position (or following if at the start).
    for i, pos in enumerate(all_positions):
        if pos not in pos_label:
            # Look backward
            for j in range(i - 1, -1, -1):
                if all_positions[j] in pos_label:
                    pos_label[pos] = pos_label[all_positions[j]]
                    break
            # If still unassigned, look forward
            if pos not in pos_label:
                for j in range(i + 1, n):
                    if all_positions[j] in pos_label:
                        pos_label[pos] = pos_label[all_positions[j]]
                        break
            # Last resort
            if pos not in pos_label:
                pos_label[pos] = 0

    # Find break points: positions where the label changes
    lines = []
    current_words = [pos_to_word[all_positions[0]]]
    current_label = pos_label[all_positions[0]]

    for i in range(1, n):
        pos = all_positions[i]
        label = pos_label[pos]
        if label != current_label:
            lines.append(' '.join(current_words))
            current_words = [pos_to_word[pos]]
            current_label = label
        else:
            current_words.append(pos_to_word[pos])

    if current_words:
        lines.append(' '.join(current_words))

    return lines


# Greek articles — lines should never end with a bare article
_ARTICLES = {'ὁ', 'ἡ', 'τό', 'τὸ', 'τοῦ', 'τῆς', 'τῷ', 'τῇ', 'τόν', 'τὸν',
             'τήν', 'τὴν', 'οἱ', 'αἱ', 'τά', 'τὰ', 'τῶν', 'τοῖς', 'ταῖς',
             'τούς', 'τοὺς', 'τάς', 'τὰς'}

# Prepositions that should not end a line (they need their object)
_PREPOSITIONS = {'ἐν', 'εἰς', 'ἐκ', 'ἐξ', 'ἀπό', 'ἀπὸ', 'πρός', 'πρὸς',
                 'διά', 'διὰ', 'κατά', 'κατὰ', 'μετά', 'μετὰ', 'περί', 'περὶ',
                 'ὑπέρ', 'ὑπὲρ', 'ὑπό', 'ὑπὸ', 'σύν', 'σὺν', 'παρά', 'παρὰ',
                 'ἐπί', 'ἐπὶ', 'πρό', 'πρὸ', 'ἀντί', 'ἀντὶ', 'διʼ', 'ἐφʼ',
                 'ἀφʼ', 'μετʼ', 'κατʼ', 'ἐπʼ', 'ὑπʼ', 'παρʼ'}

# Conjunctions / subordinators that should not end a line
_CONJUNCTIONS_NO_DANGLE = {'εἰ', 'ὅτι', 'ἵνα', 'ὅταν', 'ὅτε', 'ἐάν', 'ἐὰν',
                           'ὥστε', 'ὅπως', 'ὅπου', 'ἕως', 'πρίν', 'πρὶν',
                           'ἄχρι', 'μέχρι', 'ὡς', 'καθώς', 'καθὼς',
                           'ἐπεί', 'ἐπεὶ', 'ἐπειδή', 'ἐπειδὴ', 'διότι',
                           'ὥσπερ', 'μήποτε'}


# ---------- Fragment merging / cleanup ----------

def _strip_punct(word):
    """Strip trailing punctuation from a word for comparison purposes."""
    return re.sub(r'[,·;.\s—·]', '', word)


def _ends_with_dangler(line):
    """Check if a line ends with a word that should not be at line end
    (article, preposition, bare conjunction before next clause)."""
    words = line.split()
    if not words:
        return False
    last = _strip_punct(words[-1])
    last_lc = last.lower()
    return (last in _ARTICLES or last_lc in _ARTICLES
            or last in _PREPOSITIONS or last_lc in _PREPOSITIONS
            or last in _CONJUNCTIONS_NO_DANGLE or last_lc in _CONJUNCTIONS_NO_DANGLE)


def merge_fragments(lines, book_slug=None):
    """Merge very short fragments and fix dangling articles/prepositions.

    Applied in multiple passes:
    1. Merge isolated particle lines into next clause
    2. Merge very short lines (<=2 words, <15 chars) — but protect lines
       containing a finite verb (they are complete clauses)
    3. Fix lines ending with a dangling article or preposition
    """
    if len(lines) <= 1:
        return lines

    # --- Pass 1: merge isolated particles into next clause ---
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        words = line.split()
        stripped_words = [_strip_punct(w) for w in words]
        all_function_words = all(
            w in MERGE_PARTICLES or w in _ARTICLES
            or w.lower() in MERGE_PARTICLES or w.lower() in _ARTICLES
            for w in stripped_words if w
        )

        if all_function_words and len(words) <= 3:
            if i + 1 < len(lines):
                lines[i + 1] = line + ' ' + lines[i + 1]
            elif merged:
                merged[-1] = merged[-1] + ' ' + line
            else:
                merged.append(line)
            i += 1
            continue
        merged.append(line)
        i += 1
    lines = merged

    # --- Pass 2: merge short fragments (<=2 words, <15 chars) ---
    if len(lines) > 1:
        merged = []
        i = 0
        while i < len(lines):
            line = lines[i]
            words = line.split()
            # Protect lines with a verbal element — a finite verb is a complete clause
            has_verb = (_HAS_MORPHGNT and book_slug
                        and line_has_verbal_element(line, book_slug))
            if len(words) <= 2 and len(line) < 15 and not _is_standalone(line) and not has_verb:
                if i + 1 < len(lines):
                    lines[i + 1] = line + ' ' + lines[i + 1]
                elif merged:
                    merged[-1] = merged[-1] + ' ' + line
                else:
                    merged.append(line)
                i += 1
                continue
            merged.append(line)
            i += 1
        lines = merged

    # --- Pass 3: fix dangling articles/prepositions at line end ---
    # If a line ends with an article or preposition, steal the first word(s)
    # from the next line and append them, OR merge with next line entirely.
    if len(lines) > 1:
        merged = [lines[0]]
        for i in range(1, len(lines)):
            if _ends_with_dangler(merged[-1]) and lines[i].strip():
                # Merge the next line into this one
                merged[-1] = merged[-1] + ' ' + lines[i]
            else:
                merged.append(lines[i])
        lines = merged

    # --- Pass 4: one more pass to catch any remaining very short lines ---
    # Protect single-word lines that contain a finite verb (complete clauses)
    if len(lines) > 1:
        merged = []
        i = 0
        while i < len(lines):
            line = lines[i]
            words = line.split()
            has_verb = (_HAS_MORPHGNT and book_slug
                        and line_has_verbal_element(line, book_slug))
            if len(words) == 1 and not _is_standalone(line) and not has_verb:
                if i + 1 < len(lines):
                    lines[i + 1] = line + ' ' + lines[i + 1]
                elif merged:
                    merged[-1] = merged[-1] + ' ' + line
                else:
                    merged.append(line)
                i += 1
                continue
            merged.append(line)
            i += 1
        lines = merged

    return lines


def _is_standalone(text):
    """Check if a short line should stand alone."""
    text = text.strip().rstrip(',·;.')
    standalone = [
        r'^ἰδού$', r'^ἰδοὺ$', r'^Ἀμήν$', r'^Ἀμὴν$',
        r'^ὦ\s+\S+', r'^Ἄνδρες', r'^ἀδελφοί',
    ]
    for pat in standalone:
        if re.search(pat, text):
            return True
    return False


# ---------- Chapter formatting ----------

def format_chapter(book_slug, chapter_num, verses):
    """Format a chapter using Macula clause boundaries + SBLGNT text.

    Args:
        book_slug: project slug (e.g., 'acts', 'mark')
        chapter_num: chapter number
        verses: {verse_num: raw_sblgnt_text}

    Returns:
        Formatted string for the chapter file.
    """
    # Get all Macula clause data for this chapter
    try:
        macula_data = get_chapter_clauses_detailed(book_slug, chapter_num)
    except (ValueError, FileNotFoundError) as e:
        print(f'  WARNING: Macula data unavailable for {book_slug} {chapter_num}: {e}')
        print(f'  Falling back to simple output (no clause breaking)')
        macula_data = {}

    output_lines = []

    for verse_num in sorted(verses.keys()):
        raw_text = verses[verse_num]
        sblgnt_words = get_sblgnt_words(raw_text)
        clause_infos = macula_data.get(verse_num, [])

        cola = build_verse_cola(sblgnt_words, clause_infos, chapter_num, verse_num)
        cola = merge_fragments(cola, book_slug=book_slug)

        # Safety: if merging collapsed everything, output whole verse
        if not cola:
            cleaned = clean_apparatus(raw_text)
            cola = [cleaned]

        output_lines.append(f'{chapter_num}:{verse_num}')
        for colon in cola:
            output_lines.append(colon)
        output_lines.append('')  # blank line between verses

    return '\n'.join(output_lines)


# ---------- Book processing ----------

def process_book(book_key, chapter_filter=None):
    """Process a single book from source to v2 colometric output."""
    source_path = os.path.join(SOURCE_DIR, f'{book_key}.txt')
    if not os.path.exists(source_path):
        print(f'  ERROR: Source file not found: {source_path}')
        return

    display_name, abbrev, chapter_count = BOOKS[book_key]
    book_title, chapters = parse_source_file(source_path)

    chapters_to_process = sorted(chapters.keys())
    if chapter_filter is not None:
        chapters_to_process = [c for c in chapters_to_process if c == chapter_filter]

    for chapter_num in chapters_to_process:
        verses = chapters[chapter_num]
        output = format_chapter(abbrev, chapter_num, verses)

        ch_str = str(chapter_num).zfill(2)
        out_filename = f'{abbrev}-{ch_str}.txt'
        out_subdir = book_output_dir(abbrev)
        os.makedirs(out_subdir, exist_ok=True)
        out_path = os.path.join(out_subdir, out_filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    print(f'  {display_name}: {len(chapters_to_process)} chapter(s) formatted')


def main():
    parser = argparse.ArgumentParser(
        description='v2 colometric formatter (Macula syntax trees + SBLGNT text)')
    parser.add_argument('--book', help='Process a single book (e.g., Mark, Acts)')
    parser.add_argument('--chapter', type=int,
                        help='Process a single chapter (requires --book)')
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.book:
        if args.book not in BOOKS:
            print(f'Unknown book: {args.book}')
            print(f'Valid books: {", ".join(sorted(BOOKS.keys()))}')
            sys.exit(1)
        process_book(args.book, args.chapter)
    else:
        print('v2 colometry: formatting all 27 books...')
        for book_key in BOOKS:
            process_book(book_key)
        print('Done.')


if __name__ == '__main__':
    main()
