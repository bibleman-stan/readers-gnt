#!/usr/bin/env python3
"""
Automatic mechanical fixer for v4-editorial colometric files.

Fixes six pattern-matchable violations:
  1. Dangling conjunctions (postpositives at line end or orphaned at line start)
  2. Vocative rule (vocatives not on their own line, using Macula XML data)
  3. Overlong lines with subordinating conjunctions (>80 chars with ἵνα/ὅτι/etc.)
  4. Ultra-long lines (>140 chars) split at structural boundaries
  5. Overlong καί + finite verb split (>100 chars, uses MorphGNT morphology)
  6. Parallel list stacker (3+ repeated εἴτε/οὔτε/καί + same-case noun)

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/v4_auto_fix.py          # apply fixes
    PYTHONIOENCODING=utf-8 py -3 scripts/v4_auto_fix.py --dry-run # report only
"""

import re
import os
import sys
import argparse
import xml.etree.ElementTree as ET
from collections import defaultdict

# ---------- configuration ----------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v4-editorial')
MACULA_DIR = os.path.join(REPO_DIR, 'research', 'macula-greek', 'SBLGNT', 'lowfat')
MORPHGNT_DIR = os.path.join(REPO_DIR, 'research', 'morphgnt-sblgnt')

# Postpositive / coordinating conjunctions that should not dangle
POSTPOSITIVES = {'δέ', 'γάρ', 'οὖν', 'τε'}

# Subordinating conjunctions — break points for overlong lines
SUBORDINATORS = ['ἵνα', 'ὅτι', 'ὥστε', 'ὅταν', 'ὅτε', 'ἐάν', 'μήποτε', 'διότι', 'καθώς', 'καθὼς']

# Map from v4-editorial file prefix to Macula XML filename
PREFIX_TO_XML = {
    'matt':    '01-matthew.xml',
    'mark':    '02-mark.xml',
    'luke':    '03-luke.xml',
    'john':    '04-john.xml',
    'acts':    '05-acts.xml',
    'rom':     '06-romans.xml',
    '1cor':    '07-1corinthians.xml',
    '2cor':    '08-2corinthians.xml',
    'gal':     '09-galatians.xml',
    'eph':     '10-ephesians.xml',
    'phil':    '11-philippians.xml',
    'col':     '12-colossians.xml',
    '1thess':  '13-1thessalonians.xml',
    '2thess':  '14-2thessalonians.xml',
    '1tim':    '15-1timothy.xml',
    '2tim':    '16-2timothy.xml',
    'titus':   '17-titus.xml',
    'phlm':    '18-philemon.xml',
    'heb':     '19-hebrews.xml',
    'jas':     '20-james.xml',
    '1pet':    '21-1peter.xml',
    '2pet':    '22-2peter.xml',
    '1john':   '23-1john.xml',
    '2john':   '24-2john.xml',
    '3john':   '25-3john.xml',
    'jude':    '26-jude.xml',
    'rev':     '27-revelation.xml',
}

# Map from Macula book IDs to our file prefixes
MACULA_ID_TO_PREFIX = {
    'MAT': 'matt', 'MRK': 'mark', 'LUK': 'luke', 'JHN': 'john',
    'ACT': 'acts', 'ROM': 'rom', '1CO': '1cor', '2CO': '2cor',
    'GAL': 'gal', 'EPH': 'eph', 'PHP': 'phil', 'COL': 'col',
    '1TH': '1thess', '2TH': '2thess', '1TI': '1tim', '2TI': '2tim',
    'TIT': 'titus', 'PHM': 'phlm', 'HEB': 'heb', 'JAS': 'jas',
    '1PE': '1pet', '2PE': '2pet', '1JN': '1john', '2JN': '2john',
    '3JN': '3john', 'JUD': 'jude', 'REV': 'rev',
}

# Map from v4-editorial file prefix to MorphGNT filename
PREFIX_TO_MORPHGNT = {
    'matt':    '61-Mt-morphgnt.txt',
    'mark':    '62-Mk-morphgnt.txt',
    'luke':    '63-Lk-morphgnt.txt',
    'john':    '64-Jn-morphgnt.txt',
    'acts':    '65-Ac-morphgnt.txt',
    'rom':     '66-Ro-morphgnt.txt',
    '1cor':    '67-1Co-morphgnt.txt',
    '2cor':    '68-2Co-morphgnt.txt',
    'gal':     '69-Ga-morphgnt.txt',
    'eph':     '70-Eph-morphgnt.txt',
    'phil':    '71-Php-morphgnt.txt',
    'col':     '72-Col-morphgnt.txt',
    '1thess':  '73-1Th-morphgnt.txt',
    '2thess':  '74-2Th-morphgnt.txt',
    '1tim':    '75-1Ti-morphgnt.txt',
    '2tim':    '76-2Ti-morphgnt.txt',
    'titus':   '77-Tit-morphgnt.txt',
    'phlm':    '78-Phm-morphgnt.txt',
    'heb':     '79-Heb-morphgnt.txt',
    'jas':     '80-Jas-morphgnt.txt',
    '1pet':    '81-1Pe-morphgnt.txt',
    '2pet':    '82-2Pe-morphgnt.txt',
    '1john':   '83-1Jn-morphgnt.txt',
    '2john':   '84-2Jn-morphgnt.txt',
    '3john':   '85-3Jn-morphgnt.txt',
    'jude':    '86-Jud-morphgnt.txt',
    'rev':     '87-Re-morphgnt.txt',
}

# Finite verb moods in MorphGNT parse code (position index 3)
FINITE_MOODS = {'I', 'S', 'O', 'M'}  # Indicative, Subjunctive, Optative, Imperative

# Conjunction patterns for parallel list stacking
PARALLEL_CONJUNCTIONS = ['εἴτε', 'οὔτε', 'μήτε']


def strip_punctuation(word):
    """Strip Greek punctuation from a word for comparison."""
    return re.sub(r'[·;,.!?·:\'ʼ\u0387\u00B7\u2019\u02BC]+$', '', word).strip()


# ---------- Macula vocative extraction ----------

def load_vocatives_for_book(book_prefix):
    """
    Parse Macula XML for a book and return a dict:
      { "3:4": ["ἀδελφοί"], "9:20": ["ἄνθρωπε"], ... }
    Keys are "chapter:verse" strings. Values are lists of vocative normalized forms.
    Only includes nouns and adjectives (not articles/determiners or participles).
    """
    xml_file = PREFIX_TO_XML.get(book_prefix)
    if not xml_file:
        return {}
    xml_path = os.path.join(MACULA_DIR, xml_file)
    if not os.path.exists(xml_path):
        return {}

    vocatives = defaultdict(list)
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for w in root.iter('w'):
            if w.get('case') == 'vocative':
                word_class = w.get('class', '')
                # Only include nouns and adjectives — not articles (det) or participles (verb)
                if word_class not in ('noun', 'adj'):
                    continue
                ref = w.get('ref', '')
                m = re.match(r'\w+ (\d+:\d+)', ref)
                if m:
                    verse_ref = m.group(1)
                    normalized = w.get('normalized', w.text or '')
                    if normalized:
                        vocatives[verse_ref].append(normalized)
    except ET.ParseError:
        print(f"  WARNING: Could not parse {xml_path}", file=sys.stderr)

    return dict(vocatives)


# ---------- MorphGNT loading ----------

def load_morphgnt_for_book(book_prefix):
    """
    Parse MorphGNT data for a book and return a dict keyed by verse ref:
      { "1:1": [{'form': 'Βίβλος', 'pos': 'N-', 'parse': '----NSF-', 'lemma': 'βίβλος'}, ...], ... }

    Each entry has: form, pos (part-of-speech), parse (8-char), lemma.
    """
    mgnt_file = PREFIX_TO_MORPHGNT.get(book_prefix)
    if not mgnt_file:
        return {}
    mgnt_path = os.path.join(MORPHGNT_DIR, mgnt_file)
    if not os.path.exists(mgnt_path):
        return {}

    verses = defaultdict(list)
    try:
        with open(mgnt_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 7:
                    continue
                bcv = parts[0]
                pos = parts[1]
                parse = parts[2]
                form = parts[3]
                lemma = parts[6]
                # Decode bcv: BBCCVV
                book_num = bcv[:2]
                chapter = str(int(bcv[2:4]))
                verse = str(int(bcv[4:6]))
                ref = f"{chapter}:{verse}"
                verses[ref].append({
                    'form': form,
                    'pos': pos,
                    'parse': parse,
                    'lemma': lemma,
                })
    except Exception as e:
        print(f"  WARNING: Could not parse {mgnt_path}: {e}", file=sys.stderr)

    return dict(verses)


def is_finite_verb(word_entry):
    """Check if a MorphGNT word entry is a finite verb."""
    if not word_entry['pos'].startswith('V'):
        return False
    parse = word_entry['parse']
    if len(parse) >= 4:
        mood = parse[3]
        return mood in FINITE_MOODS
    return False


def get_kai_finite_verb_positions(verse_words):
    """
    Find positions in a verse's word list where καί is immediately followed
    by a finite verb (or within 1-2 words of one).

    Returns list of indices (into verse_words) where καί occurs before a finite verb.
    """
    positions = []
    for i, w in enumerate(verse_words):
        if w['lemma'] != 'καί':
            continue
        # Check next 1-3 words for a finite verb
        for offset in range(1, 4):
            j = i + offset
            if j >= len(verse_words):
                break
            if is_finite_verb(verse_words[j]):
                positions.append(i)
                break
            # If we hit another conjunction or preposition before a verb, stop
            if verse_words[j]['pos'].startswith('C') or verse_words[j]['pos'].startswith('P'):
                break
    return positions


# ---------- file parsing ----------

def parse_v4_file(filepath):
    """
    Parse a v4-editorial file into a list of verse blocks.
    Each block is: { 'ref': '3:1', 'lines': ['line1', 'line2', ...] }
    Blank lines between verses are preserved as separators.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = []
    current_ref = None
    current_lines = []

    for line in content.split('\n'):
        # Check if this is a verse reference line (e.g. "3:1" or "12:34")
        stripped = line.strip()
        if re.match(r'^\d+:\d+$', stripped):
            if current_ref is not None:
                blocks.append({'ref': current_ref, 'lines': current_lines})
            current_ref = stripped
            current_lines = []
        elif stripped == '':
            # blank line — part of formatting
            if current_ref is not None:
                current_lines.append('')
        else:
            if current_ref is None:
                # Text before first verse ref — shouldn't happen but handle gracefully
                current_ref = '?'
                current_lines = []
            current_lines.append(line)

    if current_ref is not None:
        blocks.append({'ref': current_ref, 'lines': current_lines})

    return blocks


def blocks_to_text(blocks):
    """Convert parsed blocks back to file text."""
    parts = []
    for block in blocks:
        parts.append(block['ref'])
        for line in block['lines']:
            parts.append(line)
        parts.append('')  # blank line after each verse block
    # Join and ensure single trailing newline
    text = '\n'.join(parts)
    # Remove trailing blank lines, add one newline
    text = text.rstrip('\n') + '\n'
    return text


# ---------- Fix 1: Dangling conjunctions ----------

def fix_dangling_conjunctions(blocks):
    """
    Fix postpositives (δέ, γάρ, οὖν, τε) that dangle at line end
    or are orphaned at the start of the next line.
    """
    fixes = []

    for block in blocks:
        lines = block['lines']
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped:
                i += 1
                continue

            words = stripped.split()

            # Note: We do NOT fix postpositives at line-end when the line has a verb
            # or other content (e.g. "σωφρονήσατε οὖν" is a valid complete thought).
            # Only fix truly orphaned postpositives (Case 2 below).

            # Case 2: Line is a lone postpositive (single word that is a postpositive)
            # Actually, postpositives at line start with only 1 word means it's orphaned
            if len(words) == 1 and strip_punctuation(words[0]) in POSTPOSITIVES:
                # Merge up into previous line
                j = i - 1
                while j >= 0 and not lines[j].strip():
                    j -= 1
                if j >= 0:
                    prev_line = lines[j].strip()
                    new_line = prev_line + ' ' + stripped
                    old_prev = prev_line
                    lines[j] = new_line
                    lines.pop(i)
                    fixes.append({
                        'ref': block['ref'],
                        'type': 'dangling_conj_orphan',
                        'old': f"{old_prev} / {stripped}",
                        'new': [new_line],
                    })
                    continue  # don't increment, re-check position

            i += 1

    return fixes


# ---------- Fix 2: Vocative rule ----------

# Words that are part of vocative phrases but not vocatives themselves
VOCATIVE_COMPANIONS = {'μου', 'ἡμῶν', 'ὦ', 'Ὦ'}

def _build_vocative_phrase_pattern(voc_words):
    """
    Build a regex that matches a full vocative phrase including:
    - Optional leading ὦ/Ὦ particle
    - The vocative word(s) themselves (possibly joined by καί)
    - Optional trailing μου/ἡμῶν possessive
    - Trailing punctuation
    Uses word boundaries to avoid partial-word matches.
    """
    # Sort by length descending so longer forms match first
    sorted_vocs = sorted(set(voc_words), key=len, reverse=True)
    voc_alts = '|'.join(re.escape(v) for v in sorted_vocs)
    # Pattern: optional ὦ + vocative word(s) possibly with καί + optional μου/ἡμῶν + punct
    # Use (?<!\S) and (?!\S) as word boundaries since \b doesn't work well with Greek
    pattern = (
        r'(?:(?:^|(?<=\s))(?:[Ὦὦ])\s+)?'  # optional vocative particle
        r'(?:^|(?<=\s))'                     # word boundary before
        r'(?:' + voc_alts + r')'             # vocative word
        r'(?:\s+(?:καὶ|καί)\s+(?:' + voc_alts + r'))*'  # optional "καί + another vocative"
        r'(?:\s+(?:μου|ἡμῶν))?'             # optional possessive
        r'[,·;.!]?'                          # optional trailing punctuation
        r'(?=\s|$)'                           # word boundary after
    )
    return pattern


def _is_vocative_line(stripped, voc_words):
    """Check if a line consists entirely of vocative phrase(s)."""
    if not voc_words:
        return False
    words = stripped.split()
    clean_words = [strip_punctuation(w) for w in words]
    voc_set = set(voc_words) | VOCATIVE_COMPANIONS | {'καὶ', 'καί'}
    return all(w in voc_set for w in clean_words if w)


def fix_vocatives(blocks, vocatives_for_chapter, chapter_num):
    """
    Ensure vocative address forms are on their own line.

    Conservative approach: only splits when a vocative word (confirmed by Macula)
    appears at the START of a line followed by a comma, and the rest of the line
    has substantial content. Or when a vocative with comma appears mid-line after
    a clear break point.

    This avoids false positives from words that are vocative-case but embedded
    in larger syntactic structures.
    """
    fixes = []

    for block in blocks:
        verse_ref = block['ref']
        voc_words = vocatives_for_chapter.get(verse_ref, [])
        if not voc_words:
            continue

        # Deduplicate preserving order
        seen = set()
        unique_vocs = set()
        for v in voc_words:
            unique_vocs.add(v)

        lines = block['lines']
        new_lines = []
        changed = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue

            # Skip short lines — probably already fine
            if len(stripped) < 40:
                new_lines.append(stripped)
                continue

            line_modified = False

            # Pattern A: "Vocative, rest of line..." — vocative at line start with comma
            # e.g. "Κύριε, πάντοτε δὸς ἡμῖν τὸν ἄρτον τοῦτον."
            # Also handles "Ὦ Vocative, rest..."
            words = stripped.split()
            if len(words) >= 3:
                # Check first word (possibly with Ὦ prefix)
                first_idx = 0
                if words[0] in ('Ὦ', 'ὦ') and len(words) >= 4:
                    first_idx = 1

                first_word = words[first_idx]
                first_clean = strip_punctuation(first_word)

                # Check if first word is a known vocative followed by comma
                if first_clean in unique_vocs and first_word.endswith(','):
                    # Build vocative portion (possibly with Ὦ and μου)
                    voc_end = first_idx + 1
                    # Check for following possessive (μου, ἡμῶν)
                    if voc_end < len(words) and strip_punctuation(words[voc_end]) in ('μου', 'ἡμῶν'):
                        voc_end += 1

                    voc_portion = ' '.join(words[:voc_end])
                    rest = ' '.join(words[voc_end:])

                    if rest and len(rest) >= 10:
                        old_line = stripped
                        new_lines.append(voc_portion)
                        new_lines.append(rest)
                        changed = True
                        line_modified = True
                        fixes.append({
                            'ref': verse_ref,
                            'type': 'vocative_split',
                            'old': old_line,
                            'new': [voc_portion, rest],
                        })

            # Pattern B: "content, Vocative, content" — vocative mid-line with commas on both sides
            # e.g. "Εὐχαριστοῦμέν σοι, κύριε, ὁ θεός..."
            # e.g. "Σὺ κατʼ ἀρχάς, κύριε, τὴν γῆν..."
            if not line_modified and len(stripped) >= 40:
                for voc in unique_vocs:
                    # Look for ", vocative," pattern
                    pat = re.compile(
                        r',\s+(' + re.escape(voc) + r'(?:\s+(?:μου|ἡμῶν))?,)\s+'
                    )
                    match = pat.search(stripped)
                    if match:
                        before = stripped[:match.start()].strip()
                        voc_portion = match.group(1).strip()
                        after = stripped[match.end():].strip()

                        if before and after and len(before) >= 10 and len(after) >= 10:
                            old_line = stripped
                            new_lines.append(before)
                            new_lines.append(voc_portion)
                            new_lines.append(after)
                            changed = True
                            line_modified = True
                            fixes.append({
                                'ref': verse_ref,
                                'type': 'vocative_split',
                                'old': old_line,
                                'new': [before, voc_portion, after],
                            })
                            break

            if not line_modified:
                new_lines.append(stripped)

        if changed:
            block['lines'] = new_lines

    return fixes


# ---------- Fix 3: Overlong lines with subordinating conjunctions ----------

def fix_overlong_subordinators(blocks):
    """
    If a line > 80 chars contains a subordinating conjunction,
    split at the conjunction (conjunction starts new line).
    """
    fixes = []

    # Build regex that matches subordinating conjunctions as whole words
    # Sort by length descending to match longer ones first
    sorted_subs = sorted(SUBORDINATORS, key=len, reverse=True)
    sub_pattern = re.compile(
        r'(?<=\s)(' + '|'.join(re.escape(s) for s in sorted_subs) + r')(?=\s)'
    )

    for block in blocks:
        lines = block['lines']
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if len(stripped) <= 80 or not stripped:
                i += 1
                continue

            # Find subordinating conjunctions in this line
            match = sub_pattern.search(stripped)
            if not match:
                i += 1
                continue

            # Don't split if the conjunction is in the first 15 chars
            # (it's already at the start of a clause)
            if match.start() < 15:
                # Try to find a later one
                match2 = sub_pattern.search(stripped, match.end())
                if match2 and match2.start() >= 15:
                    match = match2
                else:
                    i += 1
                    continue

            split_pos = match.start()
            before = stripped[:split_pos].rstrip()
            after = stripped[split_pos:]

            if before and after:
                old_line = stripped
                lines[i] = before
                lines.insert(i + 1, after)
                fixes.append({
                    'ref': block['ref'],
                    'type': 'subordinator_split',
                    'old': old_line,
                    'new': [before, after],
                })
                # Don't increment — re-check the 'after' part
                i += 1

            i += 1

    return fixes


# ---------- Fix 4: Ultra-long lines (>140 chars) ----------

def fix_ultra_long(blocks):
    """
    Lines >140 chars: split at first καί + likely clause boundary,
    or at first subordinating conjunction, or at midpoint.
    """
    fixes = []

    sorted_subs = sorted(SUBORDINATORS, key=len, reverse=True)
    sub_pattern = re.compile(
        r'(?<=\s)(' + '|'.join(re.escape(s) for s in sorted_subs) + r')(?=\s)'
    )

    for block in blocks:
        lines = block['lines']
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if len(stripped) <= 140 or not stripped:
                i += 1
                continue

            old_line = stripped
            split_done = False

            # Strategy 1: Split at καί that's roughly in the middle third
            kai_positions = [m.start() for m in re.finditer(r'(?<=\s)καὶ(?=\s)', stripped)]
            if kai_positions:
                # Pick the καί closest to midpoint
                mid = len(stripped) // 2
                best = min(kai_positions, key=lambda p: abs(p - mid))
                # Only use if it's in the middle 60% of the line
                if len(stripped) * 0.2 < best < len(stripped) * 0.8:
                    before = stripped[:best].rstrip()
                    after = stripped[best:]
                    if before and after:
                        lines[i] = before
                        lines.insert(i + 1, after)
                        fixes.append({
                            'ref': block['ref'],
                            'type': 'ultra_long_kai',
                            'old': old_line,
                            'new': [before, after],
                        })
                        split_done = True

            # Strategy 2: subordinating conjunction
            if not split_done:
                match = sub_pattern.search(stripped)
                if match and match.start() >= 15:
                    before = stripped[:match.start()].rstrip()
                    after = stripped[match.start():]
                    if before and after:
                        lines[i] = before
                        lines.insert(i + 1, after)
                        fixes.append({
                            'ref': block['ref'],
                            'type': 'ultra_long_sub',
                            'old': old_line,
                            'new': [before, after],
                        })
                        split_done = True

            # Strategy 3: midpoint word boundary
            if not split_done:
                words = stripped.split()
                if len(words) >= 4:
                    mid_word = len(words) // 2
                    before = ' '.join(words[:mid_word])
                    after = ' '.join(words[mid_word:])
                    lines[i] = before
                    lines.insert(i + 1, after)
                    fixes.append({
                        'ref': block['ref'],
                        'type': 'ultra_long_midpoint',
                        'old': old_line,
                        'new': [before, after],
                    })

            i += 1

    return fixes


# ---------- Fix 5: Overlong lines — καί + finite verb split ----------

def fix_kai_finite_verb(blocks, morphgnt_data, chapter_num):
    """
    Lines >100 chars: if MorphGNT data shows καί immediately followed by
    a finite verb (indicative/subjunctive/optative/imperative), split the
    line before the καί.

    Uses morphological data to avoid splitting at καί that merely joins
    nouns or adjectives (e.g. "bread and fish" should stay together).
    """
    fixes = []

    for block in blocks:
        verse_ref = block['ref']
        # Get MorphGNT words for this verse
        # verse_ref is like "3:4", morphgnt_data keys are "3:4"
        verse_words = morphgnt_data.get(verse_ref, [])
        if not verse_words:
            continue

        # Find which καί forms precede finite verbs
        kai_fv_indices = get_kai_finite_verb_positions(verse_words)
        if not kai_fv_indices:
            continue

        # Collect the actual word forms at those positions (stripped of punctuation)
        # We need to match these in the text. The key signal is: the form of the
        # word AFTER the καί (the finite verb form) — since there may be multiple καί.
        kai_fv_verb_forms = set()
        for idx in kai_fv_indices:
            # Find the finite verb that follows
            for offset in range(1, 4):
                j = idx + offset
                if j < len(verse_words) and is_finite_verb(verse_words[j]):
                    kai_fv_verb_forms.add(verse_words[j]['form'])
                    break

        lines = block['lines']
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            if len(stripped) <= 100 or not stripped:
                i += 1
                continue

            # Find all καί positions in the line text
            kai_matches = list(re.finditer(r'(?<=\s)καὶ(?=\s)', stripped))
            if not kai_matches:
                i += 1
                continue

            best_split = None
            for m in kai_matches:
                # Don't split if καί is in the first 15 chars
                if m.start() < 15:
                    continue

                # Check if a finite verb form follows this καί in the text
                after_kai = stripped[m.end():].strip()
                after_words = after_kai.split()
                if not after_words:
                    continue

                # Check first 1-3 words after καί for a known finite verb form
                found_fv = False
                for check_idx in range(min(3, len(after_words))):
                    clean_word = strip_punctuation(after_words[check_idx])
                    if clean_word in kai_fv_verb_forms:
                        found_fv = True
                        break
                    # If we hit a conjunction, stop checking
                    if clean_word in ('καὶ', 'καί', 'ἀλλά', 'ἀλλὰ', 'δέ', 'δὲ'):
                        break

                if found_fv:
                    best_split = m.start()
                    break  # Take the first valid split point

            if best_split is not None:
                before = stripped[:best_split].rstrip()
                after = stripped[best_split:]
                if before and after:
                    old_line = stripped
                    lines[i] = before
                    lines.insert(i + 1, after)
                    fixes.append({
                        'ref': verse_ref,
                        'type': 'kai_finite_verb_split',
                        'old': old_line,
                        'new': [before, after],
                    })
                    # Re-check the new shorter lines
                    i += 1

            i += 1

    return fixes


# ---------- Fix 6: Parallel list stacker ----------

def fix_parallel_lists(blocks, morphgnt_data, chapter_num):
    """
    Stack parallel list items on their own lines when a verse contains
    3+ instances of the same conjunction pattern (εἴτε...εἴτε...εἴτε,
    οὔτε...οὔτε...οὔτε, μήτε...μήτε...μήτε, or repeated καί + same-case noun).

    Conservative: only applies when the pattern is unambiguous.
    """
    fixes = []

    for block in blocks:
        verse_ref = block['ref']
        verse_words = morphgnt_data.get(verse_ref, [])

        lines = block['lines']
        new_lines = []
        changed = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue

            line_modified = False

            # --- Pattern A: εἴτε / οὔτε / μήτε repeated 3+ times ---
            for conj in PARALLEL_CONJUNCTIONS:
                # Count occurrences as whole words
                conj_matches = list(re.finditer(
                    r'(?:^|(?<=\s))' + re.escape(conj) + r'(?=\s|$)', stripped
                ))
                if len(conj_matches) < 3:
                    continue

                # Split before each conjunction occurrence (except possibly the first
                # if it starts the line)
                parts = []
                prev_end = 0
                for j, cm in enumerate(conj_matches):
                    if j == 0 and cm.start() <= 2:
                        # First conjunction is at start of line — don't add empty before
                        continue
                    if cm.start() > prev_end:
                        segment = stripped[prev_end:cm.start()].strip()
                        if segment:
                            parts.append(segment)
                    prev_end = cm.start()

                # Add the final segment
                final = stripped[prev_end:].strip()
                if final:
                    parts.append(final)

                # Only apply if we actually got 3+ parts and they look similar-length
                if len(parts) >= 3:
                    # Check that parts are somewhat similar in length (within 3x of each other)
                    lengths = [len(p) for p in parts]
                    if max(lengths) <= min(lengths) * 4:
                        old_line = stripped
                        new_lines.extend(parts)
                        changed = True
                        line_modified = True
                        fixes.append({
                            'ref': verse_ref,
                            'type': 'parallel_list_stack',
                            'old': old_line,
                            'new': parts,
                        })
                        break

            # --- Pattern B: repeated καί + same-case noun (conservative) ---
            # Only applies when the line is a flat list: 3+ καί with no other
            # structural conjunctions (δέ, τε, μή, μηδέ, ἤ) between them.
            if not line_modified and verse_words:
                # Count καί in this line
                kai_line_matches = list(re.finditer(r'(?:^|(?<=\s))καὶ(?=\s)', stripped))
                if len(kai_line_matches) >= 3:
                    # Safety: reject if line contains structural disruptions between καί
                    # These indicate paired structure, not a flat list
                    disruptors = {'δὲ', 'δέ', 'τε', 'μὴ', 'μή', 'μηδὲ', 'μηδέ', 'ἤ', 'ἢ'}
                    line_words = [strip_punctuation(w) for w in stripped.split()]
                    has_disruptor = bool(disruptors & set(line_words))

                    if not has_disruptor:
                        # Check MorphGNT: are there 3+ καί each followed by a noun in the same case?
                        kai_noun_cases = []
                        for w_idx, w in enumerate(verse_words):
                            if w['lemma'] == 'καί' and w_idx + 1 < len(verse_words):
                                next_w = verse_words[w_idx + 1]
                                if next_w['pos'].startswith('N'):
                                    parse = next_w['parse']
                                    if len(parse) >= 5:
                                        case = parse[4]
                                        kai_noun_cases.append(case)

                        if len(kai_noun_cases) >= 3:
                            # Check if all same case
                            case_counts = defaultdict(int)
                            for c in kai_noun_cases:
                                case_counts[c] += 1
                            dominant_case = max(case_counts, key=case_counts.get)
                            dominant_count = case_counts[dominant_case]
                            if dominant_count >= 3:
                                # Split before each καί (except the first if at line start)
                                parts = []
                                prev_end = 0
                                for j, km in enumerate(kai_line_matches):
                                    if j == 0 and km.start() <= 2:
                                        continue
                                    if km.start() > prev_end:
                                        segment = stripped[prev_end:km.start()].strip()
                                        if segment:
                                            parts.append(segment)
                                    prev_end = km.start()
                                final = stripped[prev_end:].strip()
                                if final:
                                    parts.append(final)

                                if len(parts) >= 3:
                                    lengths = [len(p) for p in parts]
                                    if max(lengths) <= min(lengths) * 4:
                                        old_line = stripped
                                        new_lines.extend(parts)
                                        changed = True
                                        line_modified = True
                                        fixes.append({
                                            'ref': verse_ref,
                                            'type': 'parallel_kai_noun_stack',
                                            'old': old_line,
                                            'new': parts,
                                        })

            if not line_modified:
                new_lines.append(stripped)

        if changed:
            block['lines'] = new_lines

    return fixes


# ---------- main processing ----------

def process_file(filepath, vocatives, chapter_num, morphgnt_data=None, dry_run=False):
    """Process a single v4-editorial file. Returns list of fix records."""
    blocks = parse_v4_file(filepath)
    all_fixes = []
    filename = os.path.basename(filepath)

    # Fix 1: Dangling conjunctions
    fixes = fix_dangling_conjunctions(blocks)
    for f in fixes:
        f['file'] = filename
    all_fixes.extend(fixes)

    # Fix 2: Vocatives
    fixes = fix_vocatives(blocks, vocatives, chapter_num)
    for f in fixes:
        f['file'] = filename
    all_fixes.extend(fixes)

    # Fix 3: Overlong subordinators (>80 chars)
    fixes = fix_overlong_subordinators(blocks)
    for f in fixes:
        f['file'] = filename
    all_fixes.extend(fixes)

    # Fix 4: Ultra-long lines (>140 chars)
    fixes = fix_ultra_long(blocks)
    for f in fixes:
        f['file'] = filename
    all_fixes.extend(fixes)

    # Fix 5: Overlong lines — καί + finite verb split (>100 chars)
    if morphgnt_data:
        fixes = fix_kai_finite_verb(blocks, morphgnt_data, chapter_num)
        for f in fixes:
            f['file'] = filename
        all_fixes.extend(fixes)

    # Fix 6: Parallel list stacker
    if morphgnt_data:
        fixes = fix_parallel_lists(blocks, morphgnt_data, chapter_num)
        for f in fixes:
            f['file'] = filename
        all_fixes.extend(fixes)

    # Write back if not dry-run and there were fixes
    if all_fixes and not dry_run:
        text = blocks_to_text(blocks)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

    return all_fixes


def main():
    parser = argparse.ArgumentParser(description='Auto-fix mechanical colometric violations in v4-editorial files')
    parser.add_argument('--dry-run', action='store_true', help='Report only, do not write changes')
    args = parser.parse_args()

    if not os.path.isdir(V4_DIR):
        print(f"ERROR: v4-editorial directory not found: {V4_DIR}", file=sys.stderr)
        sys.exit(1)

    # Gather all v4-editorial files
    files = sorted([f for f in os.listdir(V4_DIR) if f.endswith('.txt')])
    print(f"Found {len(files)} v4-editorial files")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")
    else:
        print("LIVE RUN — files will be modified\n")

    # Pre-load vocatives for all books that have v4-editorial files
    book_vocatives = {}
    book_prefixes_seen = set()
    for fname in files:
        # Extract book prefix: "rom-03.txt" -> "rom"
        m = re.match(r'^([a-z0-9]+)-\d+\.txt$', fname)
        if m:
            book_prefixes_seen.add(m.group(1))

    print("Loading Macula vocative data...")
    for prefix in sorted(book_prefixes_seen):
        vocatives = load_vocatives_for_book(prefix)
        book_vocatives[prefix] = vocatives
        voc_count = sum(len(v) for v in vocatives.values())
        if voc_count:
            print(f"  {prefix}: {voc_count} vocative words in {len(vocatives)} verses")

    # Pre-load MorphGNT data for all books that have v4-editorial files
    book_morphgnt = {}
    print("Loading MorphGNT morphology data...")
    for prefix in sorted(book_prefixes_seen):
        mgnt = load_morphgnt_for_book(prefix)
        book_morphgnt[prefix] = mgnt
        if mgnt:
            word_count = sum(len(v) for v in mgnt.values())
            print(f"  {prefix}: {word_count} words in {len(mgnt)} verses")

    print()

    # Process each file
    all_fixes = []
    counts = defaultdict(int)

    for fname in files:
        filepath = os.path.join(V4_DIR, fname)
        m = re.match(r'^([a-z0-9]+)-(\d+)\.txt$', fname)
        if not m:
            continue
        book_prefix = m.group(1)
        chapter_num = m.group(2)

        vocatives = book_vocatives.get(book_prefix, {})
        # Filter vocatives to this chapter
        chapter_vocs = {}
        for ref, words in vocatives.items():
            ch, _ = ref.split(':')
            if ch == chapter_num or ch == str(int(chapter_num)):
                chapter_vocs[ref] = words

        # Filter MorphGNT data to this chapter
        morphgnt_all = book_morphgnt.get(book_prefix, {})
        chapter_morphgnt = {}
        for ref, words in morphgnt_all.items():
            ch, _ = ref.split(':')
            if ch == chapter_num or ch == str(int(chapter_num)):
                chapter_morphgnt[ref] = words

        fixes = process_file(filepath, chapter_vocs, chapter_num,
                             morphgnt_data=chapter_morphgnt, dry_run=args.dry_run)

        if fixes:
            print(f"--- {fname}: {len(fixes)} fix(es) ---")
            for fix in fixes:
                counts[fix['type']] += 1
                new_display = ' / '.join(fix['new']) if isinstance(fix['new'], list) else fix['new']
                print(f"  [{fix['type']}] {fix['ref']}")
                print(f"    OLD: {fix['old']}")
                print(f"    NEW: {new_display}")

        all_fixes.extend(fixes)

    # Summary
    print(f"\n{'='*60}")
    print(f"TOTAL FILES PROCESSED: {len(files)}")
    print(f"TOTAL FIXES: {len(all_fixes)}")
    print(f"\nBy type:")
    for fix_type, count in sorted(counts.items()):
        print(f"  {fix_type}: {count}")

    if args.dry_run:
        print(f"\nDry run complete. Re-run without --dry-run to apply changes.")
    else:
        print(f"\nAll changes written to {V4_DIR}")


if __name__ == '__main__':
    main()
