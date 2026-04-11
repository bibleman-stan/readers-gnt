#!/usr/bin/env python3
"""
Automatic mechanical fixer for v4-editorial colometric files.

Fixes four pattern-matchable violations:
  1. Dangling conjunctions (postpositives at line end or orphaned at line start)
  2. Vocative rule (vocatives not on their own line, using Macula XML data)
  3. Overlong lines with subordinating conjunctions (>80 chars with ἵνα/ὅτι/etc.)
  4. Ultra-long lines (>140 chars) split at structural boundaries

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


# ---------- main processing ----------

def process_file(filepath, vocatives, chapter_num, dry_run=False):
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

        fixes = process_file(filepath, chapter_vocs, chapter_num, dry_run=args.dry_run)

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
