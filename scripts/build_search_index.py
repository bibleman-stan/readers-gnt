#!/usr/bin/env python3
"""
Build a prebuilt search index for gnt-reader.com.

WHY: the page used to build its search index in the browser at runtime —
fetching all 27 book HTML files and DOMParser-parsing each (Luke 840KB,
Matthew 810KB) on the main thread, walking every interlinear .verse/.line/.gk
node. That synchronous parse froze the UI for seconds on first search. This
script does the extraction once at build time; the page loads one JSON.

The extraction MIRRORS the runtime walk exactly (gk text with .punct removed,
space-joined; en text space-joined per verse), so search results are
identical. Raw text only — the page computes the diacritic-stripped and
lowercased forms at load (keeping stripDiacritics() the single JS source of
truth, so there is zero Python/JS parity risk).

Output: data/search_index.json
  { "version": 1,
    "entries": [ {book, bookName, chapter, verse, text, enText}, ... ] }

Usage: PYTHONIOENCODING=utf-8 python scripts/build_search_index.py
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / 'index.html'
BOOKS_DIR = ROOT / 'books'
OUT = ROOT / 'data' / 'search_index.json'


def parse_books():
    """Pull the BOOKS object (slug -> display name), in order, from index.html
    so this builder can never drift from the page's book list."""
    html = INDEX_HTML.read_text(encoding='utf-8')
    m = re.search(r'const BOOKS\s*=\s*\{(.*?)\n  \};', html, re.S)
    if not m:
        sys.exit('BOOKS literal not found in index.html')
    books = []
    for row in re.finditer(r"'([^']+)':\s*\{\s*name:\s*'([^']+)'", m.group(1)):
        books.append((row.group(1), row.group(2)))
    if not books:
        sys.exit('parsed zero books')
    return books


def extract(slug, bookname, html):
    """Mirror the runtime DOM walk: per .verse (id v-CH-VS), join .gk text
    (with .punct stripped) and .en text across its .line spans."""
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for verse in soup.select('.verse'):
        vid = verse.get('id', '')
        m = re.match(r'^v-(\d+)-(\d+)$', vid)
        if not m:
            continue
        ch, vn = int(m.group(1)), int(m.group(2))
        gk_parts, en_parts = [], []
        for line in verse.select('.line'):
            gk = line.find('span', class_='gk')
            en = line.find('span', class_='en')
            if gk:
                clone = BeautifulSoup(str(gk), 'html.parser')
                for p in clone.select('.punct'):
                    p.extract()
                t = clone.get_text().strip()
                if t:
                    gk_parts.append(t)
            if en:
                t = en.get_text().strip()
                if t:
                    en_parts.append(t)
        gk_text = ' '.join(gk_parts)
        en_text = ' '.join(en_parts)
        if gk_text or en_text:
            out.append({
                'book': slug, 'bookName': bookname,
                'chapter': ch, 'verse': vn,
                'text': gk_text, 'enText': en_text,
            })
    return out


def main():
    books = parse_books()
    entries = []
    per_book = {}
    for slug, name in books:
        fp = BOOKS_DIR / (slug + '.html')
        if not fp.exists():
            print(f'  WARN missing {fp.name}')
            continue
        rows = extract(slug, name, fp.read_text(encoding='utf-8'))
        per_book[slug] = len(rows)
        entries.extend(rows)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({'version': 1, 'entries': entries},
                              ensure_ascii=False, separators=(',', ':')),
                   encoding='utf-8')
    kb = OUT.stat().st_size / 1024
    print(f'wrote {OUT.relative_to(ROOT)}: {len(entries)} verses, {kb:.0f}KB')
    for slug, name in books:
        if slug in per_book:
            print(f'  {slug:8} {per_book[slug]:5} verses')


if __name__ == '__main__':
    main()
