"""
check_r18a_patriarch_triad.py — Layer 3 colometry validator for Rule R18a-GNT.

R18a-GNT (canon §8 Frozen divine triads, Patriarch-deity-triad sub-entry):
The Exodus 3:6 LXX citation ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ
(and its anchor-shared variants) MUST keep the spanning sequence
θεός→Ἀβραάμ→Ἰσαάκ→Ἰακώβ whole on a single line within a verse-block.

Ported from BoFM R18a (codified 2026-05-11; readers-bofm commit 2e4767e).

The triad surfaces in the GNT at 5 loci: Matt 22:32, Mark 12:26, Luke 20:37,
Acts 3:13, Acts 7:32. Variants attested:
  - Fully-distributed: ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ
  - Anchor-shared (accusative + bare gen): τὸν θεὸν Ἀβραάμ καὶ θεὸν Ἰσαάκ καὶ θεὸν Ἰακώβ
  - Compressed (θεός once, names bare): ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ
  - Extended-lead (ὁ θεὸς τῶν πατέρων σου, + triad)

Detection (surface-pattern, verse-block-scoped):
  For each verse-block, find the spanning sequence
  θεός-lemma → Ἀβραάμ → Ἰσαάκ → Ἰακώβ (in order, accent-normalized).
  If the spanning sequence exists in the verse-block but does NOT fit on
  any single line, emit STRONG-MERGE-CANDIDATE.

Exclusions:
  - Personal-name list without θεός anchor (Acts 7:8 patriarchal genealogy)
  - Lead-in title phrases on separate lines (Acts 3:13 ὁ θεὸς τῶν πατέρων ἡμῶν, line 60
    is appositional continuation; not part of the triad span)

Usage:
  PYTHONIOENCODING=utf-8 py -3 -m validators.colometry.check_r18a_patriarch_triad [--book SLUG] [--chapter N] [--output PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    parse_chapter_file,
    write_candidates,
)


RULE_ID = "R18a"
ERROR_CLASS = "DEVIATION"   # Layer 3 editorial — patriarch-triad merge


# Lemma forms of θεός (all case/accent variants; NFC-normalized).
def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


THEOS_PREFIXES = (
    _nfc("θεός"), _nfc("θεὸς"), _nfc("θεόν"), _nfc("θεὸν"),
    _nfc("θεοῦ"), _nfc("θεῷ"), _nfc("θεέ"),
)
ABRAHAM_PREFIXES = (_nfc("Ἀβραάμ"), _nfc("Ἀβραὰμ"))
ISAAC_PREFIXES = (_nfc("Ἰσαάκ"), _nfc("Ἰσαὰκ"))
JACOB_PREFIXES = (_nfc("Ἰακώβ"), _nfc("Ἰακὼβ"))


def _strip_trailing_punct(tok: str) -> str:
    """Strip punctuation from a token for comparison."""
    return tok.strip("·,;:.·;·\"'()[]{}—–")


def _tokenize(line: str) -> list[str]:
    return [_strip_trailing_punct(t) for t in line.split() if t]


def _triad_spans_tokens(tokens: list[str]) -> bool:
    """Detect whether θεός→Ἀβραάμ→Ἰσαάκ→Ἰακώβ in order is present in flat tokens."""
    state = "want_theos_abraham"
    seen_theos_at = -1
    for i, raw in enumerate(tokens):
        tok = _nfc(raw)
        if state == "want_theos_abraham":
            if tok in THEOS_PREFIXES:
                seen_theos_at = i
            elif tok in ABRAHAM_PREFIXES and seen_theos_at >= 0 and i - seen_theos_at <= 3:
                # θεός ... Ἀβραάμ within 3 tokens (allows for article + θεός + Ἀβραάμ shape)
                state = "want_isaac"
        elif state == "want_isaac":
            if tok in ISAAC_PREFIXES:
                state = "want_jacob"
        elif state == "want_jacob":
            if tok in JACOB_PREFIXES:
                return True
    return False


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return R18a-GNT candidates for one chapter. Conforms to run_all.py contract."""
    chapter_path: str | None = None
    for slug, ch_num, fp in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_path = fp
            break
    if chapter_path is None:
        return []
    return _scan_chapter(book, chapter, chapter_path)


def _scan_chapter(book: str, chapter: int, filepath: str) -> List[Candidate]:
    """Scan one chapter for R18a-GNT violations."""
    candidates: List[Candidate] = []
    try:
        verses = parse_chapter_file(filepath)
    except FileNotFoundError:
        return candidates

    # Group verses into verse_ref blocks: each verse is its own block, lines per verse.
    # parse_chapter_file returns a list of dicts with keys like 'verse_ref' and 'lines'.
    # If it returns a different shape we adapt.
    for verse_obj in verses:
        if not isinstance(verse_obj, dict):
            continue
        # parse_chapter_file yields {"ref": "4:1", "ch": 4, "vs": 1, "lines": [...]}
        ref = verse_obj.get("ref")
        lines = verse_obj.get("lines")
        if not ref or not lines:
            continue
        book_display = book[0].upper() + book[1:] if book else book
        verse_ref = f"{book_display} {ref}"

        # Gather all tokens across the verse-block
        per_line_tokens = [_tokenize(ln) for ln in lines]
        all_tokens: list[str] = []
        for line_toks in per_line_tokens:
            all_tokens.extend(line_toks)

        if not _triad_spans_tokens(all_tokens):
            continue  # no triad in this verse

        # Triad present. Does it fit on any single line?
        fits_on_single_line = any(
            _triad_spans_tokens(line_toks) for line_toks in per_line_tokens
        )
        if fits_on_single_line:
            continue  # compliant

        # Triad spans multiple lines — violation
        violation_text = " / ".join(ln.strip() for ln in lines if ln.strip())
        candidates.append(emit_candidate(
            verse_ref=verse_ref,
            line_index=0,
            line_text=violation_text[:120],
            rule=RULE_ID,
            tag="STRONG-MERGE",
            error_class=ERROR_CLASS,
            rationale="patriarch-deity-triad spans multiple lines; merge required (R18a-GNT)",
        ))
    return candidates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", help="restrict to one book slug (e.g. luke)")
    parser.add_argument("--chapter", type=int, help="restrict to one chapter")
    parser.add_argument("--output", help="write a candidates markdown report to PATH")
    args = parser.parse_args(argv)

    all_candidates: List[Candidate] = []
    for slug, chapter, filepath in iter_v4_chapters():
        if args.book and slug != args.book:
            continue
        if args.chapter and chapter != args.chapter:
            continue
        all_candidates.extend(_scan_chapter(slug, chapter, filepath))

    if args.output:
        write_candidates(all_candidates, args.output, title="R18a-GNT validator report")

    print(f"R18a-GNT: {len(all_candidates)} candidates")
    for c in all_candidates:
        print(f"  {c.verse_ref}: {c.line_text[:80]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
