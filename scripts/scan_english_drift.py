#!/usr/bin/env python3
"""
scan_english_drift.py — Find probable English-alignment drift sites.

The English glosses in data/text-files/eng-gloss/ are supposed to have
a 1:1 line correspondence with the Greek v4-editorial files. Over the
project's history, multiple passes of proportional-regen have
introduced mechanical splits that break English phrases mid-sentence:

  "I am telling the truth in Christ, I am"          <-- line ends with dangling "I am"
  "not lying, with my conscience bearing me..."     <-- line starts with continuation

This scanner uses string-level heuristics to find probable drift sites.
It does NOT verify semantic correctness — that's a separate (agent-
driven) audit. This scanner is fast, deterministic, and catches the
mechanical-split class of bugs.

Heuristics (each flag has a tag):

  1. LINE-END-DANGLING: line ends with a dangling function word that
     almost never ends a breath unit:
     - articles: the, a, an
     - prepositions: of, in, to, for, from, by, with, at, on, as,
       into, over, under, upon, through, against, before, after,
       among, beside, between, without, within, across, toward
     - conjunctions: and, or, but, nor, yet
     - auxiliaries: has, have, had, was, were, is, are, am, be,
       been, being, will, can, may, might, should, would, must,
       shall, do, does, did
     - common incomplete markers: very, so, too, this, that, these,
       those, which, who, whom, whose

  2. LINE-START-CONTINUATION: a lowercase line begins with a word that
     is a likely continuation of the previous line. We're less strict
     here because poetic/parallel lines can legitimately start with
     "and" or "but" at the start of a colon.

  3. SPLIT-PHRASE: line-end word + line-start word together form a
     natural English phrase ("the / gospel", "of / the", etc.). This
     is the strongest drift signal.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_english_drift.py
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_english_drift.py --book rom
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_english_drift.py --summary-only
"""
import os
import re
import argparse
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
ENG_DIR = os.path.join(REPO_ROOT, "data", "text-files", "eng-gloss")
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")

# Articles — never legitimately end an English line
ARTICLES = {"the", "a", "an"}

# Prepositions that are drift only when followed by an article or
# possessive/demonstrative on the next line
PREPS = {
    "of", "in", "to", "for", "from", "by", "with", "at", "on",
    "into", "over", "under", "upon", "through", "against", "before",
    "after", "among", "beside", "between", "without", "within",
    "across", "toward", "towards", "beyond", "around", "about",
    "above", "below", "behind",
}

# Determiners that signal the start of a noun phrase
NEXT_NP_STARTERS = {
    "the", "a", "an",
    "my", "your", "his", "her", "its", "our", "their",
    "this", "that", "these", "those",
}

# Auxiliaries — drift only when followed by a verb-form or adverb
# on the next line
AUXES = {
    "has", "have", "had", "having",
    "is", "are", "was", "were", "am", "be", "been", "being",
    "will", "can", "may", "might", "should", "would", "must",
    "shall",
}

# Suffixes suggesting a verb form / past participle / gerund
_VERBY_SUFFIX_RE = re.compile(r'(ed|en|ing|own|ought|orn|aid|old|one)$')

# Coordinating conjunctions — dangling at line end is low-confidence drift
COORD_CONJS = {"and", "or", "but", "nor"}

# Strip line-final punctuation before checking the last word
_END_PUNCT = re.compile(r'[,.\;:!?·—–\-\'\"]+$')


def _last_word(line):
    line = line.strip()
    line = _END_PUNCT.sub("", line).strip()
    if not line:
        return ("", "")
    parts = line.split()
    if not parts:
        return ("", "")
    raw = parts[-1]
    return (raw.lower(), raw)


def _first_word(line):
    line = line.strip()
    if not line:
        return ("", "")
    parts = line.split()
    if not parts:
        return ("", "")
    w = parts[0]
    w = re.sub(r'^[\"\'\(\[—–\-]+', "", w)
    return (w.lower(), w)


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)")


def _parse_chapter(filepath):
    """Return list of verses, each {ref, chapter, verse, lines}."""
    verses = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            m = VERSE_REF_RE.match(stripped)
            if m and stripped == m.group(0):
                if current:
                    verses.append(current)
                current = {
                    "ref": stripped,
                    "chapter": int(m.group(1)),
                    "verse": int(m.group(2)),
                    "lines": [],
                }
                continue
            if current is None:
                continue
            current["lines"].append(line)
    if current:
        verses.append(current)
    return verses


_POSSESSIVES = {"my", "your", "his", "her", "its", "our", "their"}


def _classify_drift(last, last_raw, next_first, next_first_raw):
    """Return (flag, confidence) or None if not drift.
    Confidence: 'high' (almost certainly broken), 'med' (probably broken),
    'low' (borderline).

    `last` / `next_first` are lowercased and punctuation-stripped.
    `last_raw` / `next_first_raw` retain original casing for proper-noun
    detection.
    """
    if not last or not next_first:
        return None

    # Article at line end — always broken
    if last in ARTICLES:
        return ("ARTICLE-SPLIT", "high")

    # Preposition + article/possessive/demonstrative on next line
    if last in PREPS and next_first in NEXT_NP_STARTERS:
        return ("PREP-NP-SPLIT", "high")

    # Auxiliary + verb-form on next line
    if last in AUXES:
        if _VERBY_SUFFIX_RE.search(next_first) or next_first in {
            "not", "no", "never"
        }:
            return ("AUX-VERB-SPLIT", "high")

    # Participle (-ing / -ed form) at line end + NP-starter on next line.
    # Narrative Greek participles translate as English -ing forms that
    # take direct objects; splitting the participle from its object
    # breaks the clause (Matt 2:11 "opening / their treasures").
    # Only flag if the last word isn't a common adjectival -ing/-ed word
    # that can legitimately end a line.
    if (last.endswith("ing") or last.endswith("ed")) and next_first in NEXT_NP_STARTERS:
        # Exclude very short -ing words that are usually adjectival
        if len(last) > 4 and last not in {"being", "having", "doing"}:
            return ("PTC-NP-SPLIT", "high")
        if last in {"being", "having", "doing"} and next_first in NEXT_NP_STARTERS:
            # "having" / "being" + NP-starter is almost always drift
            return ("PTC-NP-SPLIT", "high")

    # Proper noun at line end + possessive on next line — appositive split
    # (Matt 2:11 "with Mary / his mother"). Detect by capitalized last
    # word + possessive first word. Exclude cases where the line ends
    # with punctuation (already filtered upstream).
    if (last_raw and last_raw[0].isupper() and last_raw.lower() == last
            and next_first in _POSSESSIVES):
        return ("APPOSITIVE-SPLIT", "high")

    # Coordinating conjunction dangling — low confidence
    if last in COORD_CONJS:
        return ("DANGLING-CONJ", "low")

    return None


def scan_all(book_filter=None, min_confidence="med"):
    results = []
    conf_rank = {"low": 0, "med": 1, "high": 2}
    threshold = conf_rank.get(min_confidence, 1)
    for book_entry in sorted(os.listdir(ENG_DIR)):
        book_path = os.path.join(ENG_DIR, book_entry)
        if not os.path.isdir(book_path):
            continue
        parts = book_entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else book_entry
        if book_filter and book_slug != book_filter:
            continue
        for fname in sorted(os.listdir(book_path)):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, fname)
            verses = _parse_chapter(filepath)
            for v in verses:
                n = len(v["lines"])
                if n < 2:
                    continue
                for i in range(n - 1):
                    line = v["lines"][i]
                    if line.rstrip().endswith((",", ".", ";", ":", "!", "?", "—", "–", "·")):
                        continue
                    last, last_raw = _last_word(line)
                    next_first, next_first_raw = _first_word(v["lines"][i + 1])
                    classification = _classify_drift(last, last_raw, next_first, next_first_raw)
                    if classification is None:
                        continue
                    flag, confidence = classification
                    if conf_rank[confidence] < threshold:
                        continue
                    results.append({
                        "file": f"{book_entry}/{fname}",
                        "ref": v["ref"],
                        "line_idx": i,
                        "total_lines": n,
                        "line_text": line,
                        "next_line": v["lines"][i + 1],
                        "flag": flag,
                        "confidence": confidence,
                        "detail": f"ends with '{last}' + next starts with '{next_first}'",
                    })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--context", action="store_true",
                    help="Print full verse context for each flagged line")
    ap.add_argument("--min-confidence", default="high",
                    choices=["low", "med", "high"],
                    help="Minimum confidence level to report (default: high)")
    args = ap.parse_args()

    findings = scan_all(book_filter=args.book, min_confidence=args.min_confidence)
    print(f"=== ENGLISH DRIFT SCAN ===\n")
    print(f"Total flagged lines: {len(findings)}\n")

    by_book = defaultdict(int)
    for f in findings:
        by_book[f["file"].split("/")[0]] += 1
    for book, n in sorted(by_book.items()):
        print(f"  {book}: {n}")
    print()

    if args.summary_only:
        return

    for f in findings[:200]:  # print first 200 max
        print(f"{f['file']} {f['ref']} (line {f['line_idx']+1}/{f['total_lines']}):")
        print(f"  >>> {f['line_text']}")
        print(f"      {f['next_line']}")
        print(f"  [{f['flag']}: {f['detail']}]")
        print()

    if len(findings) > 200:
        print(f"... ({len(findings) - 200} more)")


if __name__ == "__main__":
    main()
