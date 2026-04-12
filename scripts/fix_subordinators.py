#!/usr/bin/env python3
"""
Fix mid-line subordinating conjunctions in v4-editorial files.
Breaks lines so that subordinators start new lines.
Single-pass: only fixes the FIRST mid-line subordinator per line,
then moves to the next line.
"""
import os
import re
import sys

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "text-files", "v4-editorial")

# Subordinators to fix (NOT including hoti)
SUBORDINATORS = [
    "\u1f35\u03bd\u03b1",      # ina
    "\u1f45\u03c4\u03b1\u03bd",  # hotan
    "\u1f10\u03ac\u03bd",      # ean
    "\u1f45\u03c0\u03bf\u03c5",  # hopou
    "\u1f45\u03c0\u03c9\u03c2",  # hopos
    "\u1f65\u03c3\u03c4\u03b5",  # hoste
    "\u1f65\u03c3\u03c0\u03b5\u03c1",  # hosper
    "\u03bc\u03ae\u03c0\u03bf\u03c4\u03b5",  # mepote
    "\u03ba\u03b1\u03b8\u03ce\u03c2",  # kathos
    "\u1f21\u03bd\u03af\u03ba\u03b1",  # henika
]

# Conjunctions that should not dangle at line end (stripped of punct)
CONJ_NODANGLE = {
    "\u03ba\u03b1\u03af", "\u03ba\u03b1\u1f76",  # kai
    "\u03b1\u03bb\u03bb\u03ac", "\u03b1\u03bb\u03bb\u1f70",  # alla (plain alpha)
    "\u1f00\u03bb\u03bb\u03ac", "\u1f00\u03bb\u03bb\u1f70",  # alla (alpha w/ smooth breathing)
    "\u03b1\u03bb\u03bb\u02bc", "\u1f00\u03bb\u03bb\u02bc",  # all' (both variants)
    "\u03b4\u03ad", "\u03b4\u1f72",  # de
    "\u03b3\u03ac\u03c1", "\u03b3\u1f70\u03c1",  # gar
}

# Single words/phrases that when alone before a subordinator mean "skip"
# (the subordinator is effectively at line start)
SKIP_ALONE_BEFORE = {
    "\u03ba\u03b1\u03af", "\u03ba\u03b1\u1f76",  # kai
    "\u03b1\u03bb\u03bb\u02bc", "\u03b1\u03bb\u03bb\u1f70",  # all'/alla (plain alpha)
    "\u1f00\u03bb\u03bb\u02bc", "\u1f00\u03bb\u03bb\u1f70",  # all'/alla (alpha w/ smooth breathing)
    "\u03bf\u1f50\u03c7", "\u03bf\u1f50",  # ouch, ou
    "\u1f35\u03bd\u03b1",  # ina
}

SKIP_PHRASES_BEFORE = {
    "\u03bc\u1fb6\u03bb\u03bb\u03bf\u03bd \u03b4\u1f72",  # mallon de
    "\u03bf\u1f50 \u03b3\u1f70\u03c1",  # ou gar
    "\u1f35\u03bd\u03b1 \u03bc\u1f74",  # ina me
    "\u03bf\u1f50\u03c7 \u1f35\u03bd\u03b1",  # ouch ina (ouch, ina)
    "\u03bc\u1f72\u03bd \u03bf\u1f56\u03bd",  # men oun
}


def is_verse_ref(line):
    return bool(re.match(r'^\d+:\d+$', line.strip()))


def strip_trailing_punct(word):
    return word.rstrip(',;.\u00b7\u0387\u037e')


def find_first_midline_subordinator(line):
    """
    Find the first mid-line subordinator in the line.
    Returns (split_pos, bring_conj) or None.
    split_pos: index in line where to split (everything from split_pos onward goes to new line)
    bring_conj: if True, include the preceding conjunction in the new line
    """
    for sub in SUBORDINATORS:
        # Find all occurrences of " sub " or " sub," or " sub." etc.
        idx = 0
        while True:
            # Look for space + subordinator
            pos = line.find(' ' + sub, idx)
            if pos == -1:
                break
            # Check what follows: must be space, comma, semicolon, period, or end of line
            end_pos = pos + 1 + len(sub)
            if end_pos < len(line):
                next_char = line[end_pos]
                if next_char not in ' ,;.\u00b7\u0387\u037e':
                    idx = pos + 1
                    continue

            # Found a candidate at pos+1 (the subordinator starts at pos+1)
            before = line[:pos].strip()
            before_no_punct = strip_trailing_punct(before)

            # Check if before is just a skip-alone word
            if before_no_punct in SKIP_ALONE_BEFORE:
                idx = pos + 1
                continue

            # Check if before is a skip phrase
            if before in SKIP_PHRASES_BEFORE or before_no_punct in SKIP_PHRASES_BEFORE:
                idx = pos + 1
                continue

            # Check for conjunction dangling
            words = before.split()
            if words:
                last_word_clean = strip_trailing_punct(words[-1])
                if last_word_clean in CONJ_NODANGLE and len(words) > 1:
                    # Bring the conjunction along - find where the last word starts
                    # We need to split before the conjunction
                    last_word_with_punct = words[-1]
                    conj_start = before.rfind(last_word_with_punct)
                    return (conj_start, True, pos + 1)
                elif last_word_clean in CONJ_NODANGLE and len(words) == 1:
                    # The only thing before is a conjunction - skip (effectively at line start)
                    idx = pos + 1
                    continue
                # Also handle negation particle ouch before subordinator
                if last_word_clean in {"\u03bf\u1f50\u03c7", "\u03bf\u1f50"} and len(words) > 1:
                    last_word_with_punct = words[-1]
                    neg_start = before.rfind(last_word_with_punct)
                    return (neg_start, True, pos + 1)
                elif last_word_clean in {"\u03bf\u1f50\u03c7", "\u03bf\u1f50"} and len(words) == 1:
                    idx = pos + 1
                    continue

            # Normal split: break before the subordinator
            return (pos + 1, False, pos + 1)

    return None


def process_file(filepath):
    """Process a single file, applying fixes. Returns number of fixes."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    fixes = 0
    examples = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        i += 1

        if not line or is_verse_ref(line):
            new_lines.append(line + '\n')
            continue

        # Keep splitting this line until no more mid-line subordinators
        current = line
        split_happened = True
        while split_happened:
            split_happened = False
            result = find_first_midline_subordinator(current)
            if result:
                split_pos, bring_conj, sub_pos = result
                before_part = current[:split_pos].rstrip()
                after_part = current[split_pos:].lstrip() if bring_conj else current[sub_pos:].lstrip()

                if not bring_conj:
                    after_part = current[sub_pos:].lstrip()
                else:
                    after_part = current[split_pos:].lstrip()

                if before_part and after_part:
                    new_lines.append(before_part + '\n')
                    current = after_part
                    fixes += 1
                    if len(examples) < 5:
                        examples.append((line, before_part, after_part))
                    split_happened = True
                else:
                    break

        new_lines.append(current + '\n')

    if fixes > 0:
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.writelines(new_lines)

    return fixes, examples


# Process each book directory
dirs = [
    ('06-rom', 'Romans'),
    ('07-1cor', '1 Corinthians'),
    ('08-2cor', '2 Corinthians'),
    ('09-gal', 'Galatians'),
    ('10-eph', 'Ephesians'),
    ('11-phil', 'Philippians'),
    ('12-col', 'Colossians'),
]

grand_total = 0
all_examples = []

for dirname, bookname in dirs:
    dirpath = os.path.join(BASE, dirname)
    book_total = 0
    print(f"\n{bookname}:")
    for filename in sorted(os.listdir(dirpath)):
        if not filename.endswith('.txt'):
            continue
        filepath = os.path.join(dirpath, filename)
        fixes, examples = process_file(filepath)
        if fixes > 0:
            print(f"  {filename}: {fixes} fixes")
            book_total += fixes
            all_examples.extend([(filename, *ex) for ex in examples])
    print(f"  Total: {book_total} fixes")
    grand_total += book_total

print(f"\n{'='*60}")
print(f"Grand total: {grand_total} fixes across all books")
print(f"\nSample before/after:")
for fn, orig, before, after in all_examples[:8]:
    print(f"\n  {fn}:")
    print(f"    BEFORE: {orig}")
    print(f"    AFTER:  {before}")
    print(f"            {after}")
