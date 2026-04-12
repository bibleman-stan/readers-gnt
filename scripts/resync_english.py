#!/usr/bin/env python3
"""Resync English glosses to match Greek v4-editorial line counts.

For each verse where Greek and English have different line counts,
redistributes the English words across the correct number of lines.
Uses simple proportional distribution — not a fresh translation,
but ensures line counts match so the site doesn't break.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/resync_english.py          # apply
    PYTHONIOENCODING=utf-8 py -3 scripts/resync_english.py --dry-run # report only
"""
import re, os, sys

def get_verses(filepath):
    lines = open(filepath, encoding='utf-8').read().splitlines()
    verses = {}
    order = []
    current = None
    cur_lines = []
    for line in lines:
        m = re.match(r'^(\d+:\d+)$', line.strip())
        if m:
            if current is not None:
                verses[current] = [l for l in cur_lines if l.strip()]
            current = m.group(1)
            order.append(current)
            cur_lines = []
        elif current is not None:
            cur_lines.append(line)
    if current is not None:
        verses[current] = [l for l in cur_lines if l.strip()]
    return verses, order

def redistribute(en_lines, target_count):
    """Redistribute English words across target_count lines."""
    all_words = ' '.join(en_lines).split()
    if not all_words or target_count <= 0:
        return [''] * target_count
    if target_count == 1:
        return [' '.join(all_words)]
    
    words_per_line = len(all_words) / target_count
    result = []
    for i in range(target_count):
        start = round(words_per_line * i)
        end = round(words_per_line * (i + 1))
        result.append(' '.join(all_words[start:end]))
    return result

dry_run = '--dry-run' in sys.argv
total_fixes = 0
files_fixed = 0

for book_dir in sorted(os.listdir('data/text-files/v4-editorial')):
    book_path = os.path.join('data/text-files/v4-editorial', book_dir)
    if not os.path.isdir(book_path): continue
    for f in sorted(os.listdir(book_path)):
        if not f.endswith('.txt'): continue
        gk_path = os.path.join('data/text-files/v4-editorial', book_dir, f)
        en_path = os.path.join('data/text-files/eng-gloss', book_dir, f)
        if not os.path.exists(en_path): continue

        gk_verses, gk_order = get_verses(gk_path)
        en_verses, en_order = get_verses(en_path)

        changed = False
        for v in gk_order:
            gk_count = len(gk_verses.get(v, []))
            en_count = len(en_verses.get(v, []))
            if gk_count != en_count and gk_count > 0:
                old_en = en_verses.get(v, [])
                if not old_en:
                    en_verses[v] = ['[translation needed]'] * gk_count
                else:
                    en_verses[v] = redistribute(old_en, gk_count)
                changed = True
                total_fixes += 1
                if dry_run:
                    print(f'  {f} {v}: EN {en_count}->{gk_count}')

        if changed:
            files_fixed += 1
            if not dry_run:
                # Rebuild the file
                out = []
                for v in gk_order:
                    out.append(v)
                    for line in en_verses.get(v, []):
                        out.append(line)
                    out.append('')
                open(en_path, 'w', encoding='utf-8').write('\n'.join(out))

mode = 'DRY RUN' if dry_run else 'APPLIED'
print(f'\n{mode}: {total_fixes} verse fixes across {files_fixed} files')
