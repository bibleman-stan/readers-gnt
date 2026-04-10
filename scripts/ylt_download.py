#!/usr/bin/env python3
"""
Download YLT New Testament text from bolls.life API.
Saves raw JSON responses to research/ylt/raw/.
"""

import json
import os
import time
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "research", "ylt", "raw")

# NT books: bolls.life book ID -> (name, chapters)
NT_BOOKS = {
    40: ("Matthew", 28),
    41: ("Mark", 16),
    42: ("Luke", 24),
    43: ("John", 21),
    44: ("Acts", 28),
    45: ("Romans", 16),
    46: ("1 Corinthians", 16),
    47: ("2 Corinthians", 13),
    48: ("Galatians", 6),
    49: ("Ephesians", 6),
    50: ("Philippians", 4),
    51: ("Colossians", 4),
    52: ("1 Thessalonians", 5),
    53: ("2 Thessalonians", 3),
    54: ("1 Timothy", 6),
    55: ("2 Timothy", 4),
    56: ("Titus", 3),
    57: ("Philemon", 1),
    58: ("Hebrews", 13),
    59: ("James", 5),
    60: ("1 Peter", 5),
    61: ("2 Peter", 3),
    62: ("1 John", 5),
    63: ("2 John", 1),
    64: ("3 John", 1),
    65: ("Jude", 1),
    66: ("Revelation", 22),
}

API_BASE = "https://bolls.life/get-text/YLT"


def download_chapter(book_id, chapter):
    """Download a single chapter from the API."""
    url = f"{API_BASE}/{book_id}/{chapter}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    total_chapters = sum(ch for _, ch in NT_BOOKS.values())
    downloaded = 0

    for book_id, (name, chapters) in NT_BOOKS.items():
        book_data = {}
        for ch in range(1, chapters + 1):
            out_file = os.path.join(RAW_DIR, f"{book_id}_{ch}.json")
            if os.path.exists(out_file):
                print(f"  [cached] {name} {ch}")
                downloaded += 1
                continue

            try:
                data = download_chapter(book_id, ch)
                with open(out_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                downloaded += 1
                print(f"  [{downloaded}/{total_chapters}] {name} {ch} - {len(data)} verses")
                time.sleep(0.3)  # Be polite to the API
            except Exception as e:
                print(f"  ERROR: {name} {ch}: {e}")

    print(f"\nDone. Downloaded {downloaded}/{total_chapters} chapters to {RAW_DIR}")


if __name__ == "__main__":
    main()
