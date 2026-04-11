#!/usr/bin/env python3
"""
Generate structural English glosses for Pauline epistles.
Uses Macula XML glosses directly (they are designed to read sequentially).
Minimal post-processing for readability.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_DIR = os.path.join(BASE, "data", "text-files", "v4-editorial")
V3_DIR = os.path.join(BASE, "data", "text-files", "v3-colometric")
V1_DIR = os.path.join(BASE, "data", "text-files", "v1-colometric")
WEB_DIR = os.path.join(BASE, "data", "text-files", "web-colometric")
MACULA_DIR = os.path.join(BASE, "research", "macula-greek", "SBLGNT", "lowfat")

BOOK_MAP = {
    'gal': ('09-galatians.xml', 'GAL'),
    'eph': ('10-ephesians.xml', 'EPH'),
    'phil': ('11-philippians.xml', 'PHP'),
    'col': ('12-colossians.xml', 'COL'),
    '1thess': ('13-1thessalonians.xml', 'TH1'),
    '2thess': ('14-2thessalonians.xml', 'TH2'),
    '1tim': ('15-1timothy.xml', 'TI1'),
    '2tim': ('16-2timothy.xml', 'TI2'),
    'titus': ('17-titus.xml', 'TIT'),
    'phlm': ('18-philemon.xml', 'PHM'),
}

CHAPTERS = {
    'gal': 6, 'eph': 6, 'phil': 4, 'col': 4,
    '1thess': 5, '2thess': 3, '1tim': 6, '2tim': 4,
    'titus': 3, 'phlm': 1,
}


def parse_macula(xml_path):
    """Parse Macula XML returning word data per verse."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    verses = {}
    for w in root.iter('w'):
        ref = w.get('ref', '')
        m = re.match(r'^(\w+)\s+(\d+):(\d+)!(\d+)$', ref)
        if not m:
            continue
        ch, vs, pos = m.group(2), m.group(3), int(m.group(4))
        verse_key = f"{ch}:{vs}"
        if verse_key not in verses:
            verses[verse_key] = []
        verses[verse_key].append({
            'pos': pos,
            'gloss': w.get('gloss', ''),
            'english': w.get('english', ''),
            'lemma': w.get('lemma', ''),
            'text': w.text or '',
            'class': w.get('class', ''),
            'case': w.get('case', ''),
        })
    for vk in verses:
        verses[vk].sort(key=lambda x: x['pos'])
    return verses


def parse_greek_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.replace('\r\n', '\n').split('\n')
    verses = OrderedDict()
    current = None
    for line in lines:
        s = line.rstrip()
        m = re.match(r'^(\d+:\d+)\s*$', s)
        if m:
            current = m.group(1)
            verses[current] = []
            continue
        if not s:
            continue
        if current:
            verses[current].append(s)
    return verses


def normalize_greek(word):
    # Strip trailing punctuation including apostrophes (elision marks)
    word = re.sub(r'[,;.\u00b7\u0387\u037E:!\?\u2019\u02BC\u0027\u0029\u005D\u00BB\u2018\u0060\u00B4]+$', '', word)
    word = re.sub(r'^[\u2018\u0028\u005B\u00AB]+', '', word)
    # Also handle the ʼ (U+02BC) used for elision in the middle of text references
    # and the right single quotation mark (U+2019) used similarly
    word = word.rstrip('\u02BC\u2019\u0027')
    return word


def match_line_to_words(greek_line, verse_words, start_idx, used_positions=None):
    if used_positions is None:
        used_positions = set()
    tokens = greek_line.split()
    matched = []
    idx = start_idx

    for token in tokens:
        norm = normalize_greek(token)
        if not norm:
            continue
        found = False
        for si in range(idx, min(idx + 12, len(verse_words))):
            if si in used_positions:
                continue
            mtext = normalize_greek(verse_words[si]['text'])
            if mtext == norm:
                matched.append(verse_words[si])
                used_positions.add(si)
                idx = si + 1
                found = True
                break
        if not found:
            # Search entire verse (handles reordered clauses in editorial text)
            for si in range(0, len(verse_words)):
                mtext = normalize_greek(verse_words[si]['text'])
                if mtext == norm and si not in used_positions:
                    matched.append(verse_words[si])
                    used_positions.add(si)
                    idx = si + 1
                    found = True
                    break
        if not found:
            matched.append({'gloss': '', 'english': '', 'lemma': norm,
                          'text': norm, 'class': 'unknown', 'case': ''})
    return matched, idx


def get_trailing_punct(greek_line):
    line = greek_line.rstrip()
    if not line:
        return ''
    last = line[-1]
    if last == '.':
        return '.'
    elif last == ',':
        return ','
    elif last in (';\u037E'):
        return '?'
    elif last in ('\u00b7\u0387'):
        return ';'
    elif last == ':':
        return ':'
    return ''


def build_english_line(matched_words, greek_line):
    """Build English by concatenating Macula glosses with cleanup."""
    if not matched_words:
        return '[...]'

    trailing_punct = get_trailing_punct(greek_line)

    parts = []
    for i, w in enumerate(matched_words):
        g = w.get('gloss', '') or w.get('english', '')
        if not g or g == '-':
            continue
        # Clean brackets but keep content
        g = g.replace('[the] ', 'the ')
        g = g.replace('[One]', 'one')
        g = g.replace('[one]', 'one')
        g = re.sub(r'\[([^\]]*)\]', r'\1', g)
        g = g.replace('~', '').strip()
        if g:
            parts.append(g)

    result = ' '.join(parts)

    # ---- READABILITY POST-PROCESSING ----

    # "of us" -> "our" (genitive first person plural)
    result = re.sub(r'\bof us\b', 'our', result)
    # "of me" -> "my"
    result = re.sub(r'\bof me\b', 'my', result)

    # Fix Greek possessive word order: "the NOUN our/my/your" -> "our/my/your NOUN"
    # Only apply when preceded by "the" (article + noun + possessive is the Greek pattern)
    result = re.sub(r'\bthe (\w+) our\b', r'our \1', result)
    result = re.sub(r'\bthe (\w+) my\b', r'my \1', result)
    result = re.sub(r'\bthe (\w+) your\b', r'your \1', result)
    result = re.sub(r'\bthe (\w+) his\b', r'his \1', result)
    result = re.sub(r'\bthe (\w+) her\b', r'her \1', result)
    # "of Him/Her" -> possessive
    result = re.sub(r'\bof Him\b', 'his', result)
    result = re.sub(r'\bof Her\b', 'her', result)
    # "sins/Lord/father + our/my" without article (common Macula pattern)
    result = re.sub(r'\b(sins|Lord|Father|mother|brothers|children|countrymen|traditions|grace|Son|Spirit) our\b', r'our \1', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(sins|Lord|Father|mother|brothers|children|countrymen|traditions|grace|Son|Spirit) my\b', r'my \1', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(sins|Lord|Father|mother|brothers|children|countrymen|traditions|grace|Son|Spirit) your\b', r'your \1', result, flags=re.IGNORECASE)
    result = re.sub(r'\b(sins|Lord|Father|mother|brothers|children|countrymen|traditions|grace|Son|Spirit) his\b', r'his \1', result, flags=re.IGNORECASE)

    # Fix "the one having" participles -> "who"
    result = re.sub(r'\bthe one having\b', 'who', result)
    result = re.sub(r'\bthe one who having\b', 'who', result)

    # Fix postpositive γάρ: "X for Y" at sentence start -> "For X Y"
    m = re.match(r'^([A-Z]\w*) for (.+)$', result)
    if m and m.group(1).lower() not in ('and', 'but', 'or', 'nor', 'so', 'as', 'if', 'look', 'behold', 'it'):
        result = f"For {m.group(1).lower()} {m.group(2)}"

    # Fix postpositive δέ: "X but/and Y" -> "But/And X Y"
    m = re.match(r'^([A-Z]\w*) but (.+)$', result)
    if m and m.group(1).lower() not in ('and', 'or', 'nor', 'not', 'so', 'as', 'if', 'for', 'but', 'all', 'nothing', 'no'):
        result = f"But {m.group(1).lower()} {m.group(2)}"

    # Fix "X however Y" postpositive δέ
    m = re.match(r'^([A-Z]\w*) however (.+)$', result)
    if m and m.group(1).lower() not in ('and', 'or', 'nor', 'not', 'so', 'as', 'if', 'for', 'but'):
        result = f"But {m.group(1).lower()} {m.group(2)}"

    # "the the" -> "the"
    result = re.sub(r'\bthe the\b', 'the', result)

    # Fix "the his/her/my/our/your NOUN" -> just "his/her/my/our/your NOUN"
    result = re.sub(r'\bthe (his|her|my|our|your|their)\b', r'\1', result)
    # Also fix "of the his/her" -> "of his/her"
    result = re.sub(r'\bof the (his|her|my|our|your|their)\b', r'of \1', result)

    # Fix "the God" -> "God"
    result = re.sub(r'\bthe God\b', 'God', result)

    # Fix "the Christ" -> "Christ"
    result = re.sub(r'\bthe Christ\b', 'Christ', result)

    # Fix "of having" -> "that has" (attributive participle in genitive)
    result = re.sub(r'\bof having come presently\b', 'of the present', result)
    result = re.sub(r'\bof having\b', 'who has', result)

    # Fix remaining word order issues for possessives after nouns
    POSS_NOUNS = r'(sins|father|mother|brothers|children|Lord|God|will|grace|pleasure|blood|son|spirit|heart|chains|prayers|sister|fellow\s+worker|fellow\s+soldier|supplication|love|faith|joy|word|body|glory|name|power|wisdom|knowledge|hope|life|death|flesh|work|house|church|hand|face|eye|mouth|head|feet|mind|soul|people|coming|day|way|kingdom)'
    result = re.sub(POSS_NOUNS + r' our\b', r'our \1', result, flags=re.IGNORECASE)
    result = re.sub(POSS_NOUNS + r' my\b', r'my \1', result, flags=re.IGNORECASE)
    result = re.sub(POSS_NOUNS + r' your\b', r'your \1', result, flags=re.IGNORECASE)
    result = re.sub(POSS_NOUNS + r' his\b', r'his \1', result, flags=re.IGNORECASE)
    result = re.sub(POSS_NOUNS + r' her\b', r'her \1', result, flags=re.IGNORECASE)

    # Fix "our our" double
    result = re.sub(r'\bour our\b', 'our', result)
    result = re.sub(r'\bmy my\b', 'my', result)
    result = re.sub(r'\bhis his\b', 'his', result)

    # Final pass: remove stray "the" before possessives (created by prior swaps)
    result = re.sub(r'\bthe (his|her|my|our|your|their)\b', r'\1', result)
    result = re.sub(r'\bof the of (his|her|my|our|your|their)\b', r'of \1', result)
    result = re.sub(r'\bof the (his|her|my|our|your|their)\b', r'of \1', result)
    # Fix "of of" double
    result = re.sub(r'\bof of\b', 'of', result)

    # Fix spacing
    result = re.sub(r'\s+', ' ', result).strip()

    # Capitalize first letter
    if result:
        result = result[0].upper() + result[1:]

    # Apply trailing punctuation
    if trailing_punct:
        result = result.rstrip('.,;:?!')
        result += trailing_punct

    # Fix punctuation spacing
    result = result.replace(' ,', ',').replace(' .', '.').replace(' ;', ';')
    result = result.replace(' :', ':').replace(' ?', '?').replace(' !', '!')

    return result if result else '[...]'


def generate_english_for_chapter(chapter_num, macula_verses, greek_verses):
    english_output = OrderedDict()
    ch_str = str(chapter_num)
    for verse_ref, greek_lines in greek_verses.items():
        if verse_ref.split(':')[0] != ch_str:
            continue
        verse_words = macula_verses.get(verse_ref, [])
        english_lines = []
        word_idx = 0
        used_positions = set()
        for gline in greek_lines:
            if not verse_words:
                english_lines.append('[gloss unavailable]')
                continue
            matched, word_idx = match_line_to_words(gline, verse_words, word_idx, used_positions)
            eng = build_english_line(matched, gline)
            english_lines.append(eng)
        english_output[verse_ref] = english_lines
    return english_output


def write_english_file(output_path, greek_file_path, english_verses):
    with open(greek_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.replace('\r\n', '\n').split('\n')
    output_lines = []
    current_verse = None
    line_idx_in_verse = 0
    for line in lines:
        s = line.rstrip()
        m = re.match(r'^(\d+:\d+)\s*$', s)
        if m:
            current_verse = m.group(1)
            line_idx_in_verse = 0
            output_lines.append(s)
            continue
        if not s:
            output_lines.append('')
            continue
        if current_verse and current_verse in english_verses:
            eng_lines = english_verses[current_verse]
            if line_idx_in_verse < len(eng_lines):
                output_lines.append(eng_lines[line_idx_in_verse])
            else:
                output_lines.append('')
            line_idx_in_verse += 1
        else:
            output_lines.append('')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(output_lines))


def get_source_path(book_prefix, chapter_num):
    fname = f"{book_prefix}-{chapter_num:02d}.txt"
    for d, label in [(V4_DIR, 'v4'), (V3_DIR, 'v3'), (V1_DIR, 'v1')]:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p, label
    return None, None


def main():
    os.makedirs(WEB_DIR, exist_ok=True)
    total_files = 0
    total_lines = 0
    mismatches = []

    for book_prefix, (xml_file, book_abbr) in BOOK_MAP.items():
        xml_path = os.path.join(MACULA_DIR, xml_file)
        if not os.path.exists(xml_path):
            print(f"WARNING: Macula XML not found: {xml_path}")
            continue
        print(f"Parsing Macula XML for {book_prefix}...")
        macula_verses = parse_macula(xml_path)
        for ch in range(1, CHAPTERS[book_prefix] + 1):
            src_path, src_version = get_source_path(book_prefix, ch)
            if not src_path:
                print(f"  SKIP {book_prefix}-{ch:02d}: no source found")
                continue
            greek_verses = parse_greek_file(src_path)
            english_verses = generate_english_for_chapter(ch, macula_verses, greek_verses)
            for vref, glines in greek_verses.items():
                if vref.split(':')[0] != str(ch):
                    continue
                elines = english_verses.get(vref, [])
                if len(glines) != len(elines):
                    mismatches.append(f"{book_prefix}-{ch:02d} {vref}: G={len(glines)} E={len(elines)}")
            out_path = os.path.join(WEB_DIR, f"{book_prefix}-{ch:02d}.txt")
            write_english_file(out_path, src_path, english_verses)
            ch_lines = sum(len(v) for v in english_verses.values())
            total_lines += ch_lines
            total_files += 1
            print(f"  {book_prefix}-{ch:02d}.txt ({src_version}) - {ch_lines} lines")

    print(f"\nDone: {total_files} files, {total_lines} total lines")
    if mismatches:
        print(f"\nLINE COUNT MISMATCHES ({len(mismatches)}):")
        for m in mismatches:
            print(f"  {m}")
    else:
        print("\nAll line counts verified: MATCH")


if __name__ == '__main__':
    main()
