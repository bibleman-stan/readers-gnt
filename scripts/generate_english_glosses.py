"""
Generate structural English glosses for Greek NT books.
One English line per Greek colometric line, preserving clause order.
Uses Macula lowfat XML for word-level glosses, then produces readable English.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/generate_english_glosses.py --books rom,1cor,2cor
    PYTHONIOENCODING=utf-8 py -3 scripts/generate_english_glosses.py --books mark
"""

import xml.etree.ElementTree as ET
import re
import os
import sys
import unicodedata

BASE = r"C:\Users\bibleman\repos\readers-gnt"
V4_DIR = os.path.join(BASE, "data", "text-files", "v4-editorial")
V3_DIR = os.path.join(BASE, "data", "text-files", "v3-colometric")
OUT_DIR = os.path.join(BASE, "data", "text-files", "eng-gloss")
MACULA_DIR = os.path.join(BASE, "research", "macula-greek", "SBLGNT", "lowfat")

os.makedirs(OUT_DIR, exist_ok=True)

# Book configuration: prefix -> (macula_xml, macula_book_id, num_chapters)
BOOK_CONFIG = {
    'matt': ('01-matthew.xml', 'MAT', 28),
    'mark': ('02-mark.xml', 'MRK', 16),
    'luke': ('03-luke.xml', 'LUK', 24),
    'john': ('04-john.xml', 'JHN', 21),
    'acts': ('05-acts.xml', 'ACT', 28),
    'rom': ('06-romans.xml', 'ROM', 16),
    '1cor': ('07-1corinthians.xml', '1CO', 16),
    '2cor': ('08-2corinthians.xml', '2CO', 13),
    'gal': ('09-galatians.xml', 'GAL', 6),
    'eph': ('10-ephesians.xml', 'EPH', 6),
    'phil': ('11-philippians.xml', 'PHP', 4),
    'col': ('12-colossians.xml', 'COL', 4),
    '1thess': ('13-1thessalonians.xml', '1TH', 5),
    '2thess': ('14-2thessalonians.xml', '2TH', 3),
    '1tim': ('15-1timothy.xml', '1TI', 6),
    '2tim': ('16-2timothy.xml', '2TI', 4),
    'titus': ('17-titus.xml', 'TIT', 3),
    'phlm': ('18-philemon.xml', 'PHM', 1),
    'heb': ('19-hebrews.xml', 'HEB', 13),
    'jas': ('20-james.xml', 'JAS', 5),
    '1pet': ('21-1peter.xml', '1PE', 5),
    '2pet': ('22-2peter.xml', '2PE', 3),
    '1john': ('23-1john.xml', '1JN', 5),
    '2john': ('24-2john.xml', '2JN', 1),
    '3john': ('25-3john.xml', '3JN', 1),
    'jude': ('26-jude.xml', 'JUD', 1),
    'rev': ('27-revelation.xml', 'REV', 22),
}


def strip_punctuation(word):
    """Remove punctuation from a Greek word for matching purposes."""
    return re.sub(r'[·;,.!?·\u0387\u00B7\u2019\u02BC\u0027ʼ\u037E]+', '', word).strip()


def normalize_greek(word):
    """Normalize a Greek word for fuzzy matching."""
    w = strip_punctuation(word)
    w = unicodedata.normalize('NFC', w)
    return w.lower()


def parse_macula(book_prefix):
    """Parse Macula XML for a given book. Returns dict: {verse_ref: [word_dicts]}"""
    macula_file, book_id, _ = BOOK_CONFIG[book_prefix]
    macula_path = os.path.join(MACULA_DIR, macula_file)

    print(f"  Parsing Macula XML: {macula_file}")
    tree = ET.parse(macula_path)
    root = tree.getroot()

    words_by_verse = {}

    for w_elem in root.iter('w'):
        ref = w_elem.get('ref', '')
        if not ref.startswith(book_id + ' '):
            continue
        parts = ref.split(' ')[1]  # "1:1!1"
        verse = parts.split('!')[0]  # "1:1"

        normalized = w_elem.get('normalized', '')
        gloss = w_elem.get('gloss', '')
        english = w_elem.get('english', '')
        unicode_form = w_elem.get('unicode', '')

        if verse not in words_by_verse:
            words_by_verse[verse] = []
        words_by_verse[verse].append({
            'normalized': normalized,
            'unicode': unicode_form,
            'gloss': gloss,
            'english': english,
            'ref': ref
        })

    return words_by_verse


def match_words_to_line(greek_line, verse_words, consumed_indices):
    """
    Match Greek words in a line to Macula word entries.
    Returns list of matched word dicts, updates consumed_indices.
    """
    tokens = greek_line.split()
    matched = []

    for token in tokens:
        norm_token = normalize_greek(token)
        if not norm_token:
            continue

        # Find the next unconsumed word that matches
        found = False
        for i, wd in enumerate(verse_words):
            if i in consumed_indices:
                continue
            norm_wd = normalize_greek(wd['normalized'])
            norm_uni = normalize_greek(wd['unicode'])
            if norm_token == norm_wd or norm_token == norm_uni:
                matched.append(wd)
                consumed_indices.add(i)
                found = True
                break

        if not found:
            # Try partial match (for elided forms etc.)
            for i, wd in enumerate(verse_words):
                if i in consumed_indices:
                    continue
                norm_wd = normalize_greek(wd['normalized'])
                norm_uni = normalize_greek(wd['unicode'])
                if len(norm_token) >= 3 and len(norm_wd) >= 3:
                    if norm_token.startswith(norm_wd[:3]) or norm_wd.startswith(norm_token[:3]):
                        matched.append(wd)
                        consumed_indices.add(i)
                        found = True
                        break

            if not found:
                # Sequential fallback: take the next unconsumed word
                for i, wd in enumerate(verse_words):
                    if i in consumed_indices:
                        continue
                    matched.append(wd)
                    consumed_indices.add(i)
                    found = True
                    break

                if not found:
                    matched.append({'gloss': '(?)', 'english': '(?)', 'normalized': token})

    return matched


def gloss_line(matched_words):
    """Produce a readable English gloss from matched word dicts."""
    parts = []
    for wd in matched_words:
        g = wd.get('gloss', '') or wd.get('english', '')
        if g:
            parts.append(g)

    if not parts:
        return "(no gloss available)"

    line = ' '.join(parts)
    line = re.sub(r'\s+', ' ', line).strip()
    line = naturalize(line)
    return line


def naturalize(line):
    """Clean up wooden gloss into more natural modern English."""
    # Remove bracketed articles
    line = re.sub(r'\[The\]\s*', 'The ', line)
    line = re.sub(r'\[the\]\s*', 'the ', line)
    line = re.sub(r'\[a\]\s*', 'a ', line)
    line = re.sub(r'\[an\]\s*', 'an ', line)
    # Keep other bracketed words but remove brackets
    line = re.sub(r'\[([^\]]+)\]', r'\1', line)

    # Remove stray hyphens used as placeholders
    line = re.sub(r'\s-\s', ' ', line)
    line = re.sub(r'^-\s', '', line)

    # Pronoun case fixes for non-initial position
    line = re.sub(r'\bof Me\b', 'of me', line)
    line = re.sub(r'\bof Him\b', 'of him', line)
    line = re.sub(r'\bof Her\b', 'of her', line)
    line = re.sub(r'\bof Them\b', 'of them', line)
    line = re.sub(r'\bto Him\b', 'to him', line)
    line = re.sub(r'\bto Her\b', 'to her', line)
    line = re.sub(r'\bto Them\b', 'to them', line)
    line = re.sub(r'\bto Me\b', 'to me', line)
    line = re.sub(r'\bfrom Him\b', 'from him', line)
    line = re.sub(r'\bfrom Her\b', 'from her', line)
    line = re.sub(r'\bwith Him\b', 'with him', line)
    line = re.sub(r'\bwith Them\b', 'with them', line)
    line = re.sub(r'\bafter Him\b', 'after him', line)
    line = re.sub(r'\bupon Him\b', 'upon him', line)
    line = re.sub(r'\babout Him\b', 'about him', line)
    line = re.sub(r'\bbefore Him\b', 'before him', line)
    line = re.sub(r'\bagainst Him\b', 'against him', line)
    line = re.sub(r'\bover Him\b', 'over him', line)

    # Common adjective-noun inversions
    adj_noun_fixes = [
        (r'\bspirit unclean\b', 'unclean spirit'),
        (r'\bSpirit Holy\b', 'Holy Spirit'),
        (r'\bspirit holy\b', 'holy spirit'),
        (r'\bspirits unclean\b', 'unclean spirits'),
        (r'\bson beloved\b', 'beloved son'),
        (r'\bSon beloved\b', 'beloved Son'),
        (r'\bstone large\b', 'large stone'),
        (r'\bread unleavened\b', 'unleavened bread'),
        (r'\bauthority having\b', 'having authority'),
        (r'\bbody mortal\b', 'mortal body'),
        (r'\bbodies mortal\b', 'mortal bodies'),
        (r'\blife eternal\b', 'eternal life'),
        (r'\bjudgment righteous\b', 'righteous judgment'),
        (r'\bwrath divine\b', 'divine wrath'),
    ]
    for pattern, replacement in adj_noun_fixes:
        line = re.sub(pattern, replacement, line)

    # Clean double spaces
    line = re.sub(r'\s+', ' ', line).strip()

    return line


def process_chapter(book_prefix, chapter_num, words_by_verse):
    """Process one chapter and return list of output lines."""
    ch_str = f"{chapter_num:02d}"

    # Determine source file
    v4_path = os.path.join(V4_DIR, book_prefix, f"{book_prefix}-{ch_str}.txt")
    v3_path = os.path.join(V3_DIR, f"{book_prefix}-{ch_str}.txt")

    if os.path.exists(v4_path):
        src_path = v4_path
    elif os.path.exists(v3_path):
        src_path = v3_path
    else:
        return None, None

    with open(src_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    current_verse = None
    consumed = {}  # verse -> set of consumed indices

    for line in lines:
        line = line.rstrip('\r\n')

        # Check if it's a verse reference
        if re.match(r'^\d+:\d+$', line.strip()):
            current_verse = line.strip()
            output_lines.append(line)
            if current_verse not in consumed:
                consumed[current_verse] = set()
            continue

        # Blank line
        if not line.strip():
            output_lines.append('')
            continue

        # Greek text line - produce English gloss
        if current_verse and current_verse in words_by_verse:
            verse_words = words_by_verse[current_verse]
            if current_verse not in consumed:
                consumed[current_verse] = set()
            matched = match_words_to_line(line, verse_words, consumed[current_verse])
            english = gloss_line(matched)
        else:
            english = "(verse not found in Macula)"

        output_lines.append(english)

    return output_lines, src_path


def process_book(book_prefix):
    """Process all chapters of a book."""
    if book_prefix not in BOOK_CONFIG:
        print(f"  ERROR: Unknown book '{book_prefix}'")
        return

    _, _, num_chapters = BOOK_CONFIG[book_prefix]

    print(f"  Loading Macula data...")
    words_by_verse = parse_macula(book_prefix)
    print(f"  Found {len(words_by_verse)} verses in Macula")

    total_ok = 0
    total_mismatch = 0

    for ch in range(1, num_chapters + 1):
        ch_str = f"{ch:02d}"
        result = process_chapter(book_prefix, ch, words_by_verse)

        if result[0] is None:
            print(f"    {book_prefix}-{ch_str}: SKIPPED (no source file)")
            continue

        output_lines, src_path = result

        out_dir = os.path.join(OUT_DIR, book_prefix)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{book_prefix}-{ch_str}.txt")
        with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(output_lines))
            f.write('\n')  # always end with newline to match source

        # Verify line counts
        with open(src_path, 'r', encoding='utf-8') as f:
            src_lines = f.readlines()
        with open(out_path, 'r', encoding='utf-8') as f:
            out_lines_check = f.readlines()

        src_count = len(src_lines)
        out_count = len(out_lines_check)

        if src_count == out_count:
            status = "OK"
            total_ok += 1
        else:
            status = f"MISMATCH (src={src_count}, out={out_count})"
            total_mismatch += 1

        print(f"    {book_prefix}-{ch_str}: {out_count} lines - {status}")

    print(f"  Summary: {total_ok} OK, {total_mismatch} mismatches")


def main():
    if '--books' in sys.argv:
        idx = sys.argv.index('--books')
        books_arg = sys.argv[idx + 1]
        books = [b.strip() for b in books_arg.split(',')]
    else:
        # Default to mark for backward compat
        books = ['mark']

    for book in books:
        print(f"\n{'='*60}")
        print(f"  Processing: {book.upper()}")
        print(f"{'='*60}")
        process_book(book)

    print(f"\nDone! Output in: {OUT_DIR}")


if __name__ == '__main__':
    main()
