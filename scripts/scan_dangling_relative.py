#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_dangling_relative.py

Detects relative pronouns stranded alone (or nearly alone) on a line —
a no-anchor violation where a verse boundary or colometric split left the
relative pronoun without any predicate or clause material on its line.

GRAMMATICAL BASIS:
  A relative pronoun (ὅς, ἥ, ὅ, etc.) is a clause-opener that always belongs
  with the clause it introduces. A relative pronoun alone on a line has no
  atomic thought — it is syntactically incomplete. It must merge with the
  line that follows (its own relative clause) or, rarely, the line that
  precedes (if resumptive).

  This is a subclass of the no-anchor problem specifically for relative
  pronouns. The no-anchor scanner (scan_no_anchor.py) covers articles /
  prepositions / particles; this scanner covers the relative-pronoun gap.

HOW IT HAPPENED:
  Auto-colometry places line breaks at verse boundaries. When a verse opens
  with a relative pronoun (resuming an antecedent from the prior verse),
  the pronoun lands on its own line with nothing else. The no-anchor scanner
  did not include relative pronoun forms in its detection set.

DETECTION:
  For each text line in v4-editorial, strip punctuation and check:
    - HIGH: line content is exactly one token and that token is a relative
      pronoun form (rough-breathing ὅς-paradigm)
    - REVIEW: line content is exactly two tokens where the first is a
      relative pronoun and the second is a particle (δέ, γάρ, οὖν, καί,
      τε, μέν, ἀλλά, etc.) — the particle may be legitimate but warrants
      a human eye

Usage:
  py -3 scripts/scan_dangling_relative.py

Output:
  Console summary + private/scan-dangling-relative-findings.md
"""

import unicodedata
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict

# ─── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent
V4_DIR      = REPO_ROOT / "data" / "text-files" / "v4-editorial"
PRIVATE_DIR = REPO_ROOT / "private"
OUT_FILE    = PRIVATE_DIR / "scan-dangling-relative-findings.md"

# ─── relative pronoun forms (ὅς/ἥ/ὅ paradigm, with rough breathing) ──────────
# These are the forms that appear WITH rough breathing (distinguishing them
# from the definite article ὁ/ἡ/τό which has smooth breathing).
# Includes accent variants that appear in actual SBLGNT text.

RELATIVE_PRONOUNS = {
    # singular nominative — acute (pausal) and grave (pre-word) forms
    "ὅς", "ὃς",   # masc
    "ἥ",  "ἣ",    # fem
    "ὅ",  "ὃ",    # neut
    # singular genitive (circumflex — no accent alternation)
    "οὗ", "ἧς",
    # singular dative (circumflex — no accent alternation)
    "ᾧ", "ᾗ",
    # singular accusative — acute and grave
    "ὅν", "ὃν",   # masc
    "ἥν", "ἣν",   # fem
    # plural nominative — acute and grave
    "οἵ", "οἳ",   # masc
    "αἵ", "αἳ",   # fem
    "ἅ",  "ἃ",    # neut
    # plural genitive (circumflex — no accent alternation)
    "ὧν",
    # plural dative (circumflex — no accent alternation)
    "οἷς", "αἷς",
    # plural accusative — acute and grave
    "οὕς", "οὓς",  # masc
    "ἅς",  "ἃς",   # fem
}

# Particles that commonly appear after a relative pronoun as postpositives
# (e.g. ὅς δέ, ἥν γάρ) — these make REVIEW candidates
POSTPOSITIVE_PARTICLES = {
    "δέ", "δε", "γάρ", "γαρ", "οὖν", "ουν", "τε", "μέν", "μεν",
    "καί", "και", "ἀλλά", "αλλα", "πλήν", "πλην",
}

# ─── helpers ──────────────────────────────────────────────────────────────────

def line_tokens(line: str) -> List[str]:
    """Return word tokens from a line, stripping punctuation characters."""
    return re.findall(r"[\w\u0300-\u036f\u1f00-\u1fff\u0370-\u03ff]+", line, re.UNICODE)


def is_verse_ref(line: str) -> bool:
    """True if line looks like a verse reference (e.g. '4:1')."""
    return bool(re.match(r"^\d+:\d+\s*$", line.strip()))


def classify_line(tokens: List[str]) -> str:
    """
    Returns 'HIGH', 'REVIEW', or '' based on token content.
    HIGH  = single relative pronoun token
    REVIEW = relative pronoun + one postpositive particle
    """
    if not tokens:
        return ""
    if len(tokens) == 1 and tokens[0] in RELATIVE_PRONOUNS:
        return "HIGH"
    if (len(tokens) == 2
            and tokens[0] in RELATIVE_PRONOUNS
            and tokens[1] in POSTPOSITIVE_PARTICLES):
        return "REVIEW"
    return ""

# ─── scanner ──────────────────────────────────────────────────────────────────

def scan_file(path: Path) -> List[Dict]:
    """Scan one chapter file; return list of candidate dicts."""
    candidates = []
    lines = path.read_text(encoding="utf-8").splitlines()
    book = path.parent.name   # e.g. "01-matt"
    chapter = path.stem       # e.g. "matt-13"

    current_verse = None
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if is_verse_ref(stripped):
            current_verse = stripped
            continue

        toks = line_tokens(stripped)
        confidence = classify_line(toks)
        if not confidence:
            continue

        # Gather context: 2 lines before and after (non-empty)
        ctx_before = [l.strip() for l in lines[max(0, i-3):i] if l.strip() and not is_verse_ref(l.strip())]
        ctx_after  = [l.strip() for l in lines[i+1:i+4]       if l.strip() and not is_verse_ref(l.strip())]

        candidates.append({
            "book":       book,
            "chapter":    chapter,
            "verse":      current_verse,
            "line_no":    i + 1,
            "content":    stripped,
            "confidence": confidence,
            "ctx_before": ctx_before[-2:],
            "ctx_after":  ctx_after[:2],
        })

    return candidates


def scan_corpus() -> List[Dict]:
    """Scan all v4-editorial chapter files."""
    all_candidates = []
    for book_dir in sorted(V4_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        for chapter_file in sorted(book_dir.glob("*.txt")):
            all_candidates.extend(scan_file(chapter_file))
    return all_candidates

# ─── report ───────────────────────────────────────────────────────────────────

def write_report(candidates: List[Dict]) -> None:
    high   = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]

    by_book: Dict[str, List[Dict]] = defaultdict(list)
    for c in candidates:
        by_book[c["book"]].append(c)

    lines = [
        "# Dangling Relative Pronoun Scan — Findings",
        "",
        f"**Total candidates:** {len(candidates)}  ",
        f"**HIGH (single relative pronoun on line):** {len(high)}  ",
        f"**REVIEW (relative + particle):** {len(review)}  ",
        "",
        "---",
        "",
        "## By Book",
        "",
    ]

    for book in sorted(by_book):
        book_cands = by_book[book]
        h = sum(1 for c in book_cands if c["confidence"] == "HIGH")
        r = sum(1 for c in book_cands if c["confidence"] == "REVIEW")
        lines.append(f"- **{book}**: {len(book_cands)} ({h} HIGH, {r} REVIEW)")

    lines += ["", "---", "", "## All Candidates", ""]

    for c in candidates:
        lines.append(f"### {c['chapter']} {c['verse']} — line {c['line_no']} [{c['confidence']}]")
        lines.append("")
        if c["ctx_before"]:
            for b in c["ctx_before"]:
                lines.append(f"    {b}")
        lines.append(f"  **→ {c['content']}**")
        if c["ctx_after"]:
            for a in c["ctx_after"]:
                lines.append(f"    {a}")
        lines.append("")

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {OUT_FILE}")


def main():
    print("Scanning corpus for dangling relative pronouns...")
    candidates = scan_corpus()

    high   = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]

    print(f"  Total candidates: {len(candidates)}")
    print(f"  HIGH (solo relative):        {len(high)}")
    print(f"  REVIEW (relative+particle):  {len(review)}")

    by_book: Dict[str, int] = defaultdict(int)
    for c in candidates:
        by_book[c["book"]] += 1
    print("\nTop books:")
    for book, count in sorted(by_book.items(), key=lambda x: -x[1])[:10]:
        print(f"  {book}: {count}")

    write_report(candidates)


if __name__ == "__main__":
    main()
