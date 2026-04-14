#!/usr/bin/env python3
"""
Auto-colometry formatter for SBLGNT text.

Takes raw SBLGNT source files and applies rule-based colometric line-breaking.
This is a "v1" automated pass — a starting point for hand-editing, not the final word.

Usage:
    py -3 scripts/auto_colometry.py                     # format all books
    py -3 scripts/auto_colometry.py --book Mark         # format one book
    py -3 scripts/auto_colometry.py --book Mark --chapter 4   # format one chapter

Input:  data/text-files/sblgnt-source/*.txt
Output: data/text-files/v1-colometric/{NN-book}/*.txt
"""

import re
import os
import sys
import argparse

# ---------- configuration ----------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'sblgnt-source')
OUTPUT_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v1-colometric')

# Book metadata: filename -> (display name, abbreviation, chapter count)
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

# Map from output abbreviation -> NN-book subfolder name (e.g. 'mark' -> '02-mark').
# Position within BOOKS (canonical NT order) supplies the NN prefix.
BOOK_SUBDIR = {
    abbrev: f'{idx:02d}-{abbrev}'
    for idx, (_display, abbrev, _count) in enumerate(BOOKS.values(), start=1)
}


def book_output_dir(abbrev):
    """Return the per-book output subfolder under OUTPUT_DIR for a given abbrev."""
    return os.path.join(OUTPUT_DIR, BOOK_SUBDIR[abbrev])


# ---------- text cleaning ----------

def clean_text(text):
    """Remove SBLGNT apparatus markers, normalize whitespace."""
    # Remove apparatus markers: ⸀ ⸁ ⸂ ⸃ ⸄ ⸅
    text = re.sub(r'[⸀⸁⸂⸃⸄⸅]', '', text)
    # Normalize whitespace
    text = re.sub(r'  +', ' ', text)
    return text.strip()

# ---------- colometric breaking ----------

# Subordinating conjunctions / clause introducers that earn a line break BEFORE them
BREAK_BEFORE = [
    r'ἵνα\b',          # purpose
    r'ὥστε\b',         # result
    r'ὅταν\b',         # temporal (whenever)
    r'ὅτε\b',          # temporal (when)
    r'ἐπειδὴ\b',       # causal (since)
    r'ἐπεὶ\b',         # causal (since)
    r'διότι\b',        # causal (because)
    r'καθότι\b',       # causal (inasmuch as)
    r'καθὼς\b',        # comparative (just as)
    r'ὥσπερ\b',        # comparative (just as)
    r'ἐὰν\b',          # conditional
    r'(?<!\S)εἰ(?!τε\b|δ[εέ]|σ)\s',  # conditional "if" — not εἴτε, εἰδέ, εἰς
    r'εἴπερ\b',        # conditional (if indeed)
    r'ἐάνπερ\b',       # conditional (if indeed, subjunctive)
    r'εἴγε\b',         # conditional (if indeed)
    r'μήποτε\b',       # lest
    r'ἕως\b',          # until (when followed by clause)
    r'ἄχρι\b',         # until
    r'μέχρι\b',        # until
    r'πρὶν\b',         # before
    r'διό\b',          # inferential (therefore/wherefore)
    r'ὅπως\b',         # purpose (in order that)
    r'ὅπου\b',         # local (where)
]

# Postpositive conjunctions — break goes before the PRECEDING word, not before these
POSTPOSITIVE_CONJUNCTIONS = [
    'γάρ', 'γὰρ',      # explanatory (for)
    'οὖν',              # inferential/transitional (therefore/then)
]

# Discourse markers that introduce a new line
DISCOURSE_MARKERS = [
    r'ἀλλ[ὰά]\b',     # but/rather
    r'πλὴν\b',         # nevertheless
    r'οὐδὲ\b',         # nor / not even
    r'μηδὲ\b',         # nor
    r'ἄρα\b',          # inferential (therefore)
]

# Patterns for speech introductions
SPEECH_INTRO = re.compile(
    r'((?:καὶ\s+)?'
    r'(?:ἔλεγεν|λέγει|εἶπεν|εἶπαν|ἔφη|λέγων|λέγοντες|λέγουσιν|ἀπεκρίθη|ἀποκριθεὶς\s+εἶπεν)'
    r'(?:\s+αὐτοῖς|\s+αὐτῷ|\s+πρὸς\s+αὐτ[οό][νύ]ς?)?'
    r'\s*[·;]?\s*)'
)

def is_finite_verb_nearby(text, pos, window=4):
    """Heuristic: check if a finite verb is likely within the next few words after pos."""
    # Common finite verb endings in Greek
    verb_patterns = [
        r'\b\w+(?:ει|εν|ον|αν|ην|ες|ουσιν|εται|ονται|ατο|ετο|ησεν|ωσιν|ησαν)\b',
    ]
    words_after = text[pos:].split()[:window]
    chunk = ' '.join(words_after)
    for pat in verb_patterns:
        if re.search(pat, chunk):
            return True
    return False


def break_at_major_punct(text):
    """Break at major punctuation: · (ano teleia) and . (period) mid-verse."""
    parts = []
    # Split on · (Greek semicolon/colon) and . (period) but keep the punct
    # Don't split at end-of-verse period
    segments = re.split(r'([·])\s+', text)

    result = []
    for i, seg in enumerate(segments):
        if seg == '·':
            if result:
                result[-1] = result[-1] + '·'
        elif seg.strip():
            result.append(seg.strip())

    if not result:
        return [text]
    return result


def break_verse(text):
    """Apply colometric line-breaking to a single verse's text."""
    text = clean_text(text)
    if not text:
        return []

    # Step 1: Break at major punctuation (· and mid-sentence periods)
    segments = break_at_major_punct(text)

    # Step 2: Apply grammatical breaking to each segment
    lines = []
    for segment in segments:
        sub_lines = break_segment(segment)
        lines.extend(sub_lines)

    # Step 3: Clean up — merge very short fragments (< 15 chars) with neighbors
    lines = merge_short_lines(lines)

    return lines


def break_segment(text):
    """Break a punctuation-delimited segment at grammatical joints."""
    if len(text) < 30:
        return [text]

    lines = [text]

    # Pass 1: Break before subordinating conjunctions
    lines = apply_break_patterns(lines, BREAK_BEFORE)

    # Pass 2: Break before discourse markers (ἀλλά, πλήν, ἄρα, etc.)
    lines = apply_break_patterns(lines, DISCOURSE_MARKERS)

    # Pass 2b: Break before postpositive conjunctions (γάρ, οὖν)
    lines = apply_postpositive_breaks(lines, POSTPOSITIVE_CONJUNCTIONS)

    # Pass 2c: Stack μέν…δέ correlative pairs
    lines = apply_men_de_stacking(lines)

    # Pass 3: Break at speech introductions
    lines = apply_speech_breaks(lines)

    # Pass 3b: Break at vocative phrases
    lines = apply_vocative_breaks(lines)

    # Pass 4: Break before coordinating καί when it introduces a new clause
    # (heuristic: καί at start or after comma, followed within ~4 words by a verb)
    lines = apply_kai_breaks(lines)

    # Pass 5: Break before ὅτι (content/causal) — careful, can be recitativum
    lines = apply_hoti_breaks(lines)

    # Pass 5b: Break before δέ clause boundaries (long lines only)
    lines = apply_de_breaks(lines)

    # Pass 6: Break before relative pronouns introducing substantial clauses
    lines = apply_relative_breaks(lines)

    # Pass 7: Stack parallel structures (repeated καί + noun patterns)
    lines = apply_parallel_stacking(lines)

    return lines


def apply_break_patterns(lines, patterns):
    """Break lines before any of the given patterns."""
    for pat in patterns:
        new_lines = []
        for line in lines:
            # Split before the pattern when preceded by space or comma
            regex = re.compile(r'(?<=[,\s])\s*(?=' + pat + r')')
            parts = regex.split(line)
            for p in parts:
                p = p.strip()
                if p:
                    new_lines.append(p)
        lines = new_lines
    return lines


def apply_speech_breaks(lines):
    """Break at speech introductions — speech intro on one line, speech on next."""
    result = []
    for line in lines:
        match = SPEECH_INTRO.search(line)
        if match and match.end() < len(line) - 5:
            before = line[:match.end()].rstrip()
            after = line[match.end():].strip()
            if before:
                result.append(before)
            if after:
                result.append(after)
        else:
            result.append(line)
    return result


def apply_kai_breaks(lines):
    """Break before καί when it likely introduces a new clause (after comma)."""
    result = []
    for line in lines:
        if len(line) < 45:
            result.append(line)
            continue

        # Split at ", καὶ" — break before καὶ, keep comma with previous
        parts = re.split(r',\s+(?=καὶ\s)', line)
        if len(parts) >= 2:
            for i, p in enumerate(parts):
                p = p.strip()
                if p:
                    if i < len(parts) - 1:
                        result.append(p + ',')
                    else:
                        result.append(p)
        else:
            result.append(line)
    return result


def apply_hoti_breaks(lines):
    """Break before ὅτι when it introduces a content or causal clause."""
    result = []
    for line in lines:
        if len(line) < 40:
            result.append(line)
            continue

        # Break before ὅτι, but not when it's the first word
        match = re.search(r'(\s)(ὅτι\s)', line)
        if match and match.start() > 10:
            before = line[:match.start()].strip()
            after = line[match.start():].strip()
            if before and after:
                result.append(before)
                result.append(after)
                continue
        result.append(line)
    return result


def apply_relative_breaks(lines):
    """Break before relative pronouns introducing substantial clauses."""
    result = []
    for line in lines:
        if len(line) < 50:
            result.append(line)
            continue

        # Look for relative pronouns: ὅς, ἥ, ὅ, οἵ, αἵ, ἅ, ὅστις, ἥτις, etc.
        # But only after comma + space
        match = re.search(r',\s+(ὅ[ςἥ]|ἥτις|οἵτινες|ὅστις|ᾧ|ᾗ|οὗ|ἧς|οἷς|αἷς|ὧν)\s', line)
        if match and match.start() > 15:
            before = line[:match.start()+1].strip()  # include comma
            after = line[match.start()+2:].strip()
            if before and after:
                result.append(before)
                result.append(after)
                continue
        result.append(line)
    return result


def apply_parallel_stacking(lines):
    """Stack parallel structures: repeated καὶ + article + noun patterns."""
    result = []
    for line in lines:
        if len(line) < 60:
            result.append(line)
            continue

        # Look for triple+ καὶ patterns (lists)
        kai_positions = [m.start() for m in re.finditer(r'\bκαὶ\b', line)]
        if len(kai_positions) >= 3:
            # Check if they're roughly evenly spaced (list pattern)
            parts = re.split(r'\s+(καὶ\s)', line)
            if len(parts) >= 5:  # at least 3 καί segments
                rebuilt = []
                for i, part in enumerate(parts):
                    p = part.strip()
                    if p and p != 'καὶ':
                        if p.startswith('καὶ '):
                            rebuilt.append(p)
                        elif rebuilt and not rebuilt[-1].startswith('καὶ'):
                            rebuilt.append(p)
                        else:
                            rebuilt.append(p)
                if len(rebuilt) > 2:
                    result.extend(rebuilt)
                    continue

        result.append(line)
    return result


def apply_postpositive_breaks(lines, postpositive_words):
    """Break before the word PRECEDING a postpositive conjunction (γάρ, οὖν).

    Postpositives appear as the 2nd word in their clause, so the real clause
    boundary is before the word that precedes them.  E.g. in
    "πολλοὶ γὰρ ἦλθον" the break goes before "πολλοὶ".

    If the postpositive is already the first word of a line, break before it
    normally (rare but possible).
    """
    pat = re.compile(
        r'(?<=\s)(\S+\s+(?:' + '|'.join(re.escape(w) for w in postpositive_words) + r'))\b'
    )
    result = []
    for line in lines:
        if len(line) < 35:
            result.append(line)
            continue
        m = pat.search(line)
        if m and m.start() > 8:
            before = line[:m.start()].strip()
            after = line[m.start():].strip()
            if before and after:
                result.append(before)
                result.append(after)
                continue
        result.append(line)
    return result


def apply_men_de_stacking(lines):
    """Split μέν…δέ correlative pairs so each half gets its own line.

    Looks for μέν followed later by δέ within the same line.  The split
    point is the comma-space boundary between the two halves.
    """
    men_pat = re.compile(r'\bμ[ὲέ]ν\b')
    de_pat = re.compile(r'\bδ[ὲέ]\b')
    result = []
    for line in lines:
        if not men_pat.search(line) or not de_pat.search(line):
            result.append(line)
            continue
        # Try to split at ", " before the δέ clause
        # Find the δέ position and look for the nearest preceding comma
        de_match = de_pat.search(line)
        if de_match:
            # Walk backward from δέ to find ", "
            prefix = line[:de_match.start()]
            comma_pos = prefix.rfind(', ')
            if comma_pos > 5:
                before = line[:comma_pos + 1].strip()
                after = line[comma_pos + 2:].strip()
                if before and after:
                    result.append(before)
                    result.append(after)
                    continue
        result.append(line)
    return result


def apply_vocative_breaks(lines):
    """Detect vocative phrases and give them their own line.

    Patterns: ὦ + word (+ optional second word before comma), Ἄνδρες + noun.
    """
    # ὦ + one word, optionally a second non-comma word, then optional comma
    # e.g. "ὦ Θεόφιλε," or "ὦ γενεὰ ἄπιστος,"
    vocative_pat = re.compile(r'(ὦ\s+[^,\s]+(?:\s+[^,\s]+)?),?')
    result = []
    for line in lines:
        m = vocative_pat.search(line)
        if m and len(line) > 30:
            # Determine the full vocative span including trailing comma
            voc_start = m.start()
            voc_end = m.end()
            # If the match ends with comma, include it; if next char is comma, grab it
            if voc_end < len(line) and line[voc_end] == ',':
                voc_end += 1
            voc_text = line[voc_start:voc_end].strip()
            # Skip trailing whitespace after the vocative
            rest_start = voc_end
            while rest_start < len(line) and line[rest_start] == ' ':
                rest_start += 1

            before = line[:voc_start].strip()
            after = line[rest_start:].strip()

            if before:
                result.append(before)
            result.append(voc_text)
            if after:
                result.append(after)
        else:
            result.append(line)
    return result


def apply_de_breaks(lines):
    """Break before δέ clause boundaries on long lines.

    δέ is postpositive, so the break goes before the word preceding δέ.
    Only applied when line > 50 chars to avoid over-splitting connective δέ.
    """
    de_pat = re.compile(r'(?<=\s)(\S+\s+δ[ὲέ]\b)')
    result = []
    for line in lines:
        if len(line) < 50:
            result.append(line)
            continue
        m = de_pat.search(line)
        if m and m.start() > 10:
            before = line[:m.start()].strip()
            after = line[m.start():].strip()
            if before and after:
                result.append(before)
                result.append(after)
                continue
        result.append(line)
    return result


def merge_short_lines(lines):
    """Merge very short lines (< 15 chars) with their neighbor."""
    if len(lines) <= 1:
        return lines

    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # If very short and not a dramatic standalone (imperative, vocative)
        if len(line) < 12 and i > 0 and result and not is_standalone(line):
            # Merge with previous line
            result[-1] = result[-1] + ' ' + line
        elif len(line) < 12 and i == 0 and i + 1 < len(lines) and not is_standalone(line):
            # Merge with next line
            lines[i+1] = line + ' ' + lines[i+1]
        else:
            result.append(line)
        i += 1
    return result


def is_standalone(text):
    """Check if a short line should stand alone (imperative, vocative, dramatic)."""
    standalone_patterns = [
        r'^[ἈΑ]κούετε',     # "Listen!"
        r'^[Σσ]ιώπα',       # "Be silent!"
        r'^[Ἄἄ]νδρες',      # "Men of..."
        r'^[Ἀἀ]γνώστ',      # "To an unknown..."
        r'^[Δδ]ιέλθωμεν',   # "Let us cross!"
        r'^ἰδοὺ',           # "Behold!"
        r'^Ἀμὴν',           # "Amen"
        r'^ὦ\s+\S+',        # Vocative with ὦ
        r'^ἀδελφοί',        # "Brothers"
    ]
    for pat in standalone_patterns:
        if re.search(pat, text):
            return True
    return False


# ---------- file processing ----------

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
            if not book_title and not line.startswith(('Matt', 'Mark', 'Luke', 'John',
                    'Acts', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col',
                    '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb',
                    'Jas', '1Pet', '2Pet', '1John', '2John', '3John', 'Jude', 'Rev')):
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


def format_chapter(book_name, chapter_num, verses):
    """Format a chapter into colometric sense-lines."""
    lines = []

    for verse_num in sorted(verses.keys()):
        text = verses[verse_num]
        cola = break_verse(text)

        lines.append(f'{chapter_num}:{verse_num}')
        for colon in cola:
            lines.append(colon)
        lines.append('')  # blank line between verses

    return '\n'.join(lines)


def process_book(book_key, chapter_filter=None):
    """Process a single book from source to colometric output."""
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
        output = format_chapter(display_name, chapter_num, verses)

        # Output filename: mark-04.txt, acts-17.txt, etc.
        # Written under the per-book subfolder, e.g. v1-colometric/02-mark/mark-04.txt
        ch_str = str(chapter_num).zfill(2)
        out_filename = f'{abbrev}-{ch_str}.txt'
        out_subdir = book_output_dir(abbrev)
        os.makedirs(out_subdir, exist_ok=True)
        out_path = os.path.join(out_subdir, out_filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)

    print(f'  {display_name}: {len(chapters_to_process)} chapter(s) formatted')


def main():
    parser = argparse.ArgumentParser(description='Auto-colometry formatter for SBLGNT')
    parser.add_argument('--book', help='Process a single book (e.g., Mark, Acts)')
    parser.add_argument('--chapter', type=int, help='Process a single chapter (requires --book)')
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.book:
        if args.book not in BOOKS:
            print(f'Unknown book: {args.book}')
            print(f'Valid books: {", ".join(sorted(BOOKS.keys()))}')
            sys.exit(1)
        process_book(args.book, args.chapter)
    else:
        print('Auto-colometry: formatting all 27 books...')
        for book_key in BOOKS:
            process_book(book_key)
        print('Done.')


if __name__ == '__main__':
    main()
