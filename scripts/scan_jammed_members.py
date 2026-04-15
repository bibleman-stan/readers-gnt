#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_jammed_members.py

Detects "jammed member" drift — the blind spot of scan_parallelism_consistency.py.
A jammed member is when two structural units that should be on separate lines
are collapsed onto one line, with or without the second unit's content orphaned
onto the next line.

NO PUNCTUATION DEPENDENCY. Two structural detection methods:

Method A — Structural particle mid-line occurrence:
  Scans for unambiguous structural particles (εἴτε, οὔτε, μήτε, ὡς, καθὼς,
  καθάπερ) appearing as non-first tokens in a line, when the same particle
  also starts at least one line within a WINDOW_LINES window. Confirms
  we are inside a parallel structure before flagging.

Method B — Terminal-phrase mid-line occurrence:
  For each verse, identifies "completion formulas" — token sequences (2–5
  tokens) that appear as the terminal of 2+ text lines in the verse.
  Then checks if that formula also appears mid-line (not as the final
  tokens) in any line of the same verse or an adjacent verse.

Usage:
  py -3 scripts/scan_jammed_members.py

Output:
  Console summary + private/scan-jammed-members-findings.md
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Optional, Tuple

# ─── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
V4_DIR    = REPO_ROOT / "data" / "text-files" / "v4-editorial"
OUTPUT    = REPO_ROOT / "private" / "scan-jammed-members-findings.md"

# ─── parameters ───────────────────────────────────────────────────────────────
WINDOW_LINES = 8     # how many neighboring text lines to check for same-particle start
MIN_TERMINAL_REPS = 2  # how many lines must share a terminal phrase before it's a "formula"
TERMINAL_NGRAM_SIZES = [2, 3, 4]  # token window sizes for terminal-phrase detection

# ─── structural particles for Method A ────────────────────────────────────────
# Only unambiguous structural particles that:
#   (a) reliably start parallel members, and
#   (b) don't commonly appear mid-clause in non-parallel roles.
# Prepositions excluded (too much false-positive noise).
STRUCTURAL_PARTICLES: List[str] = [
    "εἴτε",
    "οὔτε",
    "μήτε",
    "οὐδέ", "οὐδὲ",
    "μηδέ", "μηδὲ",
    "καθὼς", "καθώς",
    "καθάπερ",
    "ὥσπερ",
]

# Words that, when immediately following a particle mid-line, indicate
# the particle is functioning as a governor (not e.g. ὡς in a simile).
# For ὡς we require it to be followed by a predicate, not just any word.
# For εἴτε, οὔτε, μήτε: always structural. So we just list those.
ALWAYS_STRUCTURAL: Set[str] = {
    "εἴτε", "οὔτε", "μήτε", "οὐδέ", "οὐδὲ", "μηδέ", "μηδὲ",
}

# ─── parsing ──────────────────────────────────────────────────────────────────

VERSE_RE = re.compile(r'^\d+:\d+$')


def parse_file(path: Path) -> List[dict]:
    records = []
    verse = None
    with open(path, encoding='utf-8') as f:
        for line_no, raw in enumerate(f, 1):
            content = raw.rstrip('\n').strip()
            if VERSE_RE.match(content):
                verse = content
                records.append({'line_no': line_no, 'content': content,
                                 'type': 'verse_ref', 'verse': verse})
            elif not content:
                records.append({'line_no': line_no, 'content': '',
                                 'type': 'blank', 'verse': verse})
            else:
                records.append({'line_no': line_no, 'content': content,
                                 'type': 'text', 'verse': verse})
    return records


def text_lines_only(records: List[dict]) -> List[dict]:
    return [r for r in records if r['type'] == 'text']


# ─── tokenization ─────────────────────────────────────────────────────────────

def tokenize(content: str) -> List[str]:
    """Split on whitespace; strip trailing punctuation for matching purposes."""
    return content.split()


def token_normalized(tok: str) -> str:
    """Strip common trailing Greek punctuation for terminal-phrase matching."""
    return tok.rstrip('·,;.·—»«')


def normalized_tokens(content: str) -> List[str]:
    return [token_normalized(t) for t in tokenize(content)]


# ─── Method A: structural particle mid-line occurrence ───────────────────────

def find_particle_start_lines(text_lines: List[dict], window_around: int,
                               center_idx: int, particle: str) -> bool:
    """
    Return True if `particle` starts at least one text line within
    WINDOW_LINES positions of center_idx (excluding center_idx itself).
    """
    lo = max(0, center_idx - window_around)
    hi = min(len(text_lines), center_idx + window_around + 1)
    for j in range(lo, hi):
        if j == center_idx:
            continue
        toks = tokenize(text_lines[j]['content'])
        if toks and token_normalized(toks[0]) == particle:
            return True
    return False


def scan_method_a(records: List[dict]) -> List[dict]:
    """
    Method A: structural particle appears as a non-first token in a line,
    AND the same particle starts a neighboring line.
    """
    tlines = text_lines_only(records)
    candidates = []

    for i, line in enumerate(tlines):
        toks = tokenize(line['content'])
        if len(toks) < 3:
            continue  # too short to jam two members

        # Check each token position > 0 for a structural particle
        for pos, tok in enumerate(toks[1:], start=1):
            tok_norm = token_normalized(tok)
            if tok_norm not in STRUCTURAL_PARTICLES:
                continue

            # For particles that are only sometimes structural (ὡς),
            # require at least one neighbor line to start with the same particle
            # For always-structural particles, require the same
            if not find_particle_start_lines(tlines, WINDOW_LINES, i, tok_norm):
                continue

            # Build context: what appears before and after the mid-line particle
            before = ' '.join(toks[:pos])
            after  = ' '.join(toks[pos:])

            candidates.append({
                'method':      'A',
                'line_no':     line['line_no'],
                'verse':       line['verse'],
                'content':     line['content'],
                'particle':    tok_norm,
                'token_pos':   pos,
                'before_particle': before,
                'after_particle':  after,
                'verdict':     'JAMMED',
            })
            break  # one report per line

    return candidates


# ─── Method B: terminal-phrase mid-line occurrence ───────────────────────────

def get_terminal_ngrams(content: str, sizes: List[int]) -> List[Tuple[int, str]]:
    """
    Return (size, phrase) for each terminal ngram of the given sizes.
    Uses normalized tokens (punctuation stripped) joined by space.
    """
    toks = normalized_tokens(content)
    results = []
    for n in sizes:
        if len(toks) >= n:
            phrase = ' '.join(toks[-n:])
            results.append((n, phrase))
    return results


def scan_method_b(records: List[dict]) -> List[dict]:
    """
    Method B: for each verse, find terminal phrases shared by 2+ lines.
    Then check if that phrase appears mid-line (not at end) in any line
    of the same verse or one verse on either side.
    """
    # Group text lines by verse
    verse_lines: Dict[str, List[dict]] = defaultdict(list)
    for r in records:
        if r['type'] == 'text':
            verse_lines[r['verse']].append(r)

    # Build verse sequence for windowed lookups
    verse_order = list(dict.fromkeys(
        r['verse'] for r in records if r['type'] == 'text'
    ))

    candidates = []

    for v_idx, verse in enumerate(verse_order):
        lines = verse_lines[verse]
        if len(lines) < 2:
            continue

        # Gather terminal ngrams for all lines in this verse
        terminal_counts: Dict[str, int] = defaultdict(int)
        terminal_origins: Dict[str, List[dict]] = defaultdict(list)

        for line in lines:
            for size, phrase in get_terminal_ngrams(line['content'], TERMINAL_NGRAM_SIZES):
                if len(phrase.split()) < 2:
                    continue  # single-token terminals too noisy
                terminal_counts[phrase] += 1
                terminal_origins[phrase].append(line)

        # Identify "completion formulas": terminal phrases appearing in 2+ lines
        formulas = {ph for ph, cnt in terminal_counts.items()
                    if cnt >= MIN_TERMINAL_REPS}
        if not formulas:
            continue

        # For each formula, check if it appears MID-LINE in lines of this verse
        # or the adjacent verses (window: verse ± 1)
        adjacent_verses = [verse_order[v_idx]]
        if v_idx > 0:
            adjacent_verses.append(verse_order[v_idx - 1])
        if v_idx < len(verse_order) - 1:
            adjacent_verses.append(verse_order[v_idx + 1])

        all_lines_in_window = []
        for av in adjacent_verses:
            all_lines_in_window.extend(verse_lines[av])

        for formula in formulas:
            formula_toks = formula.split()
            n = len(formula_toks)

            for line in all_lines_in_window:
                toks = normalized_tokens(line['content'])
                if len(toks) <= n:
                    continue  # line isn't long enough to have the formula mid-line

                # Check: does formula appear in toks at any position
                # EXCEPT as the terminal n tokens?
                found_mid = False
                for start in range(0, len(toks) - n):
                    if toks[start:start + n] == formula_toks:
                        found_mid = True
                        before_toks = toks[:start]
                        after_toks  = toks[start + n:]
                        break

                if not found_mid:
                    continue

                # Confirm: this formula is actually a terminal phrase of 2+ OTHER lines
                # (not this line itself being one of the "origin" lines)
                origin_lines = terminal_origins[formula]
                other_origins = [ol for ol in origin_lines if ol['line_no'] != line['line_no']]
                if len(other_origins) < MIN_TERMINAL_REPS - 1:
                    continue

                candidates.append({
                    'method':     'B',
                    'line_no':    line['line_no'],
                    'verse':      line['verse'],
                    'content':    line['content'],
                    'formula':    formula,
                    'origin_lines': other_origins,
                    'before_formula': ' '.join(before_toks),
                    'after_formula':  ' '.join(after_toks),
                    'verdict':    'JAMMED',
                })

    # Deduplicate: same line_no may appear for multiple formula sizes
    seen = set()
    deduped = []
    for c in candidates:
        key = (c['line_no'], c['method'])
        if key not in seen:
            seen.add(key)
            deduped.append(c)

    return deduped


# ─── corpus scan ──────────────────────────────────────────────────────────────

def scan_corpus() -> List[dict]:
    all_candidates = []
    book_dirs = sorted(V4_DIR.iterdir())

    for book_dir in book_dirs:
        if not book_dir.is_dir():
            continue
        for chapter_file in sorted(book_dir.glob('*.txt')):
            records = parse_file(chapter_file)

            a_candidates = scan_method_a(records)
            b_candidates = scan_method_b(records)

            rel_path = str(chapter_file.relative_to(REPO_ROOT))
            book = book_dir.name
            chapter = chapter_file.stem

            for c in a_candidates + b_candidates:
                c['file_path'] = rel_path
                c['book']      = book
                c['chapter']   = chapter

            all_candidates.extend(a_candidates)
            all_candidates.extend(b_candidates)

    return all_candidates


# ─── reporting ────────────────────────────────────────────────────────────────

def candidate_block(c: dict, rank: int) -> str:
    method_label = {
        'A': 'Structural particle mid-line',
        'B': 'Terminal-phrase mid-line',
    }.get(c['method'], c['method'])

    lines = [
        f"### Candidate {rank}: `{c['book']}` — {c['chapter']} — {c['verse']}",
        f"",
        f"- **File:** `{c['file_path']}` (line {c['line_no']})",
        f"- **Method:** {c['method']} — {method_label}",
        f"- **Verse:** {c['verse']}",
        f"- **Scanner verdict:** {c['verdict']}",
        f"",
        f"**Flagged line:**",
        f"```",
        f"  {c['content']}",
        f"```",
    ]

    if c['method'] == 'A':
        lines += [
            f"",
            f"**Mid-line particle:** `{c['particle']}` at token position {c['token_pos']}",
            f"- Before: `{c['before_particle']}`",
            f"- From particle: `{c['after_particle']}`",
        ]
    elif c['method'] == 'B':
        lines += [
            f"",
            f"**Completion formula found mid-line:** `{c['formula']}`",
            f"- Before formula: `{c['before_formula']}`",
            f"- After formula: `{c['after_formula']}`",
            f"- Formula appears as terminal of {len(c['origin_lines'])} other line(s):",
        ]
        for ol in c['origin_lines'][:3]:
            lines.append(f"  - [{ol['verse']}] `{ol['content']}`")

    lines.append("")
    return "\n".join(lines)


def write_report(candidates: List[dict]) -> None:
    by_book: Dict[str, int] = defaultdict(int)
    by_method: Dict[str, int] = defaultdict(int)
    for c in candidates:
        by_book[c['book']] += 1
        by_method[c['method']] += 1

    top_books = sorted(by_book.items(), key=lambda x: -x[1])[:10]

    lines = [
        "# Jammed Member Scan — Findings Report",
        "",
        "**Generated:** 2026-04-15",
        "**Scanner version:** v1 (two methods; no punctuation dependency)",
        "**Corpus:** data/text-files/v4-editorial/ — all 260 chapters",
        "",
        "## Detection methods",
        "",
        "**Method A — Structural particle mid-line:**",
        "Flags lines where an unambiguous structural particle (εἴτε, οὔτε, μήτε, etc.)",
        "appears at a non-first token position, when the same particle starts a",
        "neighboring line. Zero punctuation dependency.",
        "",
        "**Method B — Terminal-phrase mid-line:**",
        "For each verse, identifies 'completion formulas' — token sequences that",
        "appear as the terminal of 2+ text lines. Flags lines where that formula",
        "appears mid-line (not at the end). Catches the 2 Cor 11:22 pattern.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total candidates:** {len(candidates)}",
        f"- **Method A (particle mid-line):** {by_method.get('A', 0)}",
        f"- **Method B (terminal-phrase mid-line):** {by_method.get('B', 0)}",
        "",
        "### By book (top 10)",
        "",
    ]
    for book, cnt in top_books:
        lines.append(f"- {book}: {cnt}")

    lines += [
        "",
        "---",
        "",
        "## Candidates",
        "",
        "*(Adversarial audit verdicts to be filled in below each candidate.)*",
        "",
    ]

    for i, c in enumerate(candidates):
        lines.append(candidate_block(c, i + 1))

    lines += [
        "---",
        "",
        "## Adversarial audit notes",
        "",
        "*(To be filled in after parallel sub-agent review.)*",
        "",
        "---",
        "",
        "## Scanner notes",
        "",
        "Both methods are heuristic: false positives are expected.",
        "Method A false positive pattern: particle in a non-parallel context",
        "(e.g. ὡς in a simile clause where a neighbor line happens to start with ὡς).",
        "Method B false positive pattern: common phrase coincidentally appearing",
        "mid-line without structural significance.",
        "Adversarial audit is mandatory before any fix is applied.",
    ]

    OUTPUT.write_text("\n".join(lines), encoding='utf-8')


def print_summary(candidates: List[dict]) -> None:
    by_method: Dict[str, int] = defaultdict(int)
    for c in candidates:
        by_method[c['method']] += 1

    print(f"\n{'='*68}")
    print(f"JAMMED MEMBER SCAN — RESULTS")
    print(f"{'='*68}")
    print(f"Total candidates:      {len(candidates)}")
    print(f"Method A (particle):   {by_method.get('A', 0)}")
    print(f"Method B (terminal):   {by_method.get('B', 0)}")
    print(f"{'='*68}")

    if candidates:
        print("\nAll candidates:")
        for i, c in enumerate(candidates[:50], 1):
            method_label = "particle" if c['method'] == 'A' else "terminal"
            detail = c.get('particle', c.get('formula', ''))[:30]
            print(
                f"  {i:3}. [M{c['method']}] {c['book']}/{c['chapter']} "
                f"{c['verse']}  ln={c['line_no']}  {method_label}={detail!r}"
            )
        if len(candidates) > 50:
            print(f"  ... and {len(candidates) - 50} more (see report)")

    print(f"\nReport: {OUTPUT}")
    print(f"{'='*68}\n")


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    if not V4_DIR.exists():
        print(f"ERROR: {V4_DIR}", file=sys.stderr)
        sys.exit(1)

    print("Scanning corpus for jammed members...", flush=True)
    candidates = scan_corpus()
    print(f"Scan complete. {len(candidates)} candidates.", flush=True)

    print_summary(candidates)
    write_report(candidates)
    print(f"Report written: {OUTPUT}")


if __name__ == '__main__':
    main()
