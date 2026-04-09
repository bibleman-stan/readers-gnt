#!/usr/bin/env python3
"""
Build a lemma-to-forms index from MorphGNT SBLGNT data.

Reads all 27 MorphGNT files, maps each lemma to its set of inflected
surface forms (diacritic-stripped), and outputs data/lemma_index.json.

MorphGNT format (space-separated):
  BBCCVV  POS  PARSING  TEXT  WORD  NORMALIZED  LEMMA

Usage:
  PYTHONIOENCODING=utf-8 py -3 scripts/build_lemma_index.py
"""

import json
import os
import re
import unicodedata
from collections import defaultdict

MORPHGNT_DIR = os.path.join(os.path.dirname(__file__), '..', 'research', 'morphgnt-sblgnt')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'lemma_index.json')


def strip_diacritics(s):
    """Match the JS stripDiacritics: NFD normalize, remove U+0300-U+036F, lowercase."""
    nfd = unicodedata.normalize('NFD', s)
    stripped = re.sub(r'[\u0300-\u036f]', '', nfd)
    return stripped.lower()


def strip_apparatus(s):
    """Remove apparatus markers like parenthesized alternates: ἐγέννησε(ν) -> ἐγέννησεν"""
    # Remove parentheses but keep their content
    return s.replace('(', '').replace(')', '')


def main():
    lemma_to_forms = defaultdict(set)

    files = sorted(f for f in os.listdir(MORPHGNT_DIR) if f.endswith('.txt'))
    print(f'Processing {len(files)} MorphGNT files...')

    word_count = 0
    for fname in files:
        fpath = os.path.join(MORPHGNT_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 7:
                    continue

                normalized = parts[5]  # NORMALIZED column
                lemma = parts[6]       # LEMMA column

                # Strip apparatus markers
                normalized = strip_apparatus(normalized)
                lemma_clean = strip_apparatus(lemma)

                # Diacritic-strip both
                form_stripped = strip_diacritics(normalized)
                lemma_stripped = strip_diacritics(lemma_clean)

                lemma_to_forms[lemma_stripped].add(form_stripped)
                word_count += 1

    # Build form_to_lemma (reverse mapping)
    form_to_lemma = {}
    for lemma, forms in lemma_to_forms.items():
        for form in forms:
            # If a form maps to multiple lemmas, keep the first one
            # (rare edge case for homographs)
            if form not in form_to_lemma:
                form_to_lemma[form] = lemma

    # Convert sets to sorted lists for JSON
    lemma_to_forms_json = {k: sorted(v) for k, v in sorted(lemma_to_forms.items())}

    output = {
        'lemma_to_forms': lemma_to_forms_json,
        'form_to_lemma': dict(sorted(form_to_lemma.items()))
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    n_lemmas = len(lemma_to_forms_json)
    n_forms = len(form_to_lemma)
    file_size = os.path.getsize(OUTPUT_FILE)

    print(f'Done.')
    print(f'  Total words processed: {word_count:,}')
    print(f'  Unique lemmas: {n_lemmas:,}')
    print(f'  Unique forms: {n_forms:,}')
    print(f'  Output: {OUTPUT_FILE}')
    print(f'  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)')


if __name__ == '__main__':
    main()
