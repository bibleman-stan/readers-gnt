#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_parallelism_consistency.py

Walks data/text-files/v4-editorial/ looking for spans where N >= 3 parallel
coordinate members under a shared governor are broken into M != 1 different
stack patterns (different line-counts per member).

Five governor classes (v1):
  1. prep   — Preposition-initial catenae (ἐν, διά/διὰ, κατά/κατὰ, ἐπί/ἐπὶ, etc.)
  2. eite   — Disjunctive conditional chains (εἴτε)
  3. hos    — Correlative chains (ὡς, καθώς, καθάπερ)
  4. neg    — Negation-disjunction chains (οὔτε, μήτε, μή/Μή, οὐδέ/οὐδὲ, μηδέ/μηδὲ)
  5. noun   — Repeated noun-phrase chains (same first content-word N >= 3 consecutive lines)

Key design constraints:
  - Blank lines terminate member continuations (members do not span verse breaks)
  - A cross-class governor token terminates the current span
  - Members: gov_line + up to MAX_CONTINUATION non-governor continuation lines
  - Only M > 1 (inconsistent member sizes) generates a candidate

Output:
  - Console: one summary line per CONFIRMED DRIFT candidate
  - File:    private/scan-parallelism-consistency-findings.md (full report)

Usage:
  py -3 scripts/scan_parallelism_consistency.py
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Optional, Tuple, Set

# ─── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
V4_DIR = REPO_ROOT / "data" / "text-files" / "v4-editorial"
OUTPUT_FILE = REPO_ROOT / "private" / "scan-parallelism-consistency-findings.md"

# ─── parameters ───────────────────────────────────────────────────────────────
MIN_MEMBERS = 3       # minimum parallel members to constitute a span
MAX_CONTINUATION = 2  # max extra (non-governor) lines per member beyond the governor line itself

# ─── governor class definitions ───────────────────────────────────────────────
# token_map: canonical_key -> list of line-start prefixes that trigger this governor.
# Prefixes include trailing space to avoid partial matches (ἐν should not match ἐνός).

GOVERNOR_CLASSES = [
    {
        "id": "prep",
        "name": "Preposition-initial catenae",
        "token_map": {
            "ἐν":   ["ἐν "],
            "διά":  ["διά ", "διὰ "],
            "κατά": ["κατά ", "κατὰ "],
            "ἐπί":  ["ἐπί ", "ἐπὶ "],
            "πρός": ["πρός ", "πρὸς "],
            "ἀπό":  ["ἀπό ", "ἀπὸ "],
            "εἰς":  ["εἰς "],
            "ἐκ":   ["ἐκ "],
            "ἐξ":   ["ἐξ "],
            "ὑπό":  ["ὑπό ", "ὑπὸ "],
            "παρά": ["παρά ", "παρὰ "],
            "μετά": ["μετά ", "μετὰ "],
        },
    },
    {
        "id": "eite",
        "name": "Disjunctive conditional chains (εἴτε)",
        "token_map": {
            "εἴτε": ["εἴτε "],
        },
    },
    {
        "id": "hos",
        "name": "Correlative chains (ὡς / καθώς / καθάπερ)",
        "token_map": {
            "ὡς":      ["ὡς "],
            "καθώς":   ["καθὼς "],
            "καθάπερ": ["καθάπερ "],
            "ὥσπερ":   ["ὥσπερ "],
        },
    },
    {
        "id": "neg",
        "name": "Negation-disjunction chains (οὔτε / μήτε / οὐδέ / μηδέ / μή / οὐ)",
        "token_map": {
            "οὔτε": ["οὔτε "],
            "μήτε": ["μήτε "],
            "οὐδέ": ["οὐδέ ", "οὐδὲ "],
            "μηδέ": ["μηδέ ", "μηδὲ "],
            "μή":   ["μή ", "μὴ ", "Μὴ ", "Μή "],
            "οὐ":   ["οὐ ", "Οὐ ", "οὐκ ", "Οὐκ ", "οὐχ ", "Οὐχ "],
        },
    },
]

# Words excluded from Class 5 (noun) repeated-first-word detection.
# These are handled by other classes OR are too common/structural to be
# meaningful parallelism governors.
# Using lowercase for comparison (first_word is lowercased before checking).
CLASS5_EXCLUSIONS: Set[str] = {
    # Class 1: prepositions
    "ἐν", "διά", "διὰ", "κατά", "κατὰ", "ἐπί", "ἐπὶ", "πρός", "πρὸς",
    "ἀπό", "ἀπὸ", "εἰς", "ἐκ", "ἐξ", "ὑπό", "ὑπὸ", "παρά", "παρὰ",
    "μετά", "μετὰ",
    # Class 2
    "εἴτε",
    # Class 3
    "ὡς", "καθὼς", "καθάπερ", "ὥσπερ",
    # Class 4: negation
    "οὔτε", "μήτε", "οὐδέ", "οὐδὲ", "μηδέ", "μηδὲ",
    "μή", "μὴ", "οὐ", "οὐκ", "οὐχ",
    # Conditional particles
    "εἰ", "εἴ", "ἐάν",
    # Relative/demonstrative pronouns
    "ὃ", "ὅ", "ἅ", "ὅς", "ἥ", "οἵ", "αἵ", "ὧν", "οὗ", "οἷς", "ἥν", "ὅν",
    # Common conjunctions / discourse markers
    "καί", "καὶ", "δέ", "δὲ", "γάρ", "γὰρ", "ἀλλά", "ἀλλὰ", "ἀλλʼ",
    "οὖν", "μέν", "μὲν", "ὅτι", "ἵνα", "ὥστε", "ὅτε", "ὅταν",
    "ἤ", "ἢ", "τε", "διό", "διὸ", "διότι",
    # Pronouns (personal/demonstrative)
    "ἐγώ", "ἐγὼ", "σύ", "αὐτός", "αὐτὸς", "αὐτοί", "ἡμεῖς", "ὑμεῖς",
    "οὗτος", "ταῦτα", "τοῦτο", "ἐκεῖνος",
    # Articles (should not appear at line start normally, but just in case)
    "ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά",
    # Interjections / demonstratives
    "ἰδού", "ἰδοὺ",
    # Temporal/locative adverbs
    "νῦν", "τότε", "ὅπου", "ὅθεν", "ἐκεῖ",
}

# ─── parsing ──────────────────────────────────────────────────────────────────

VERSE_REF_RE = re.compile(r'^\d+:\d+$')


def parse_file(filepath: Path) -> List[dict]:
    """
    Parse a v4-editorial chapter file into a list of line records.

    Record fields:
      line_no  — 1-based line number in file
      content  — stripped content
      type     — 'verse_ref' | 'blank' | 'text'
      verse    — current verse reference (e.g. '1:3')
    """
    records = []
    current_verse = None

    with open(filepath, encoding='utf-8') as f:
        for line_no, raw in enumerate(f, 1):
            content = raw.rstrip('\n').strip()

            if VERSE_REF_RE.match(content):
                current_verse = content
                records.append({
                    'line_no': line_no,
                    'content': content,
                    'type': 'verse_ref',
                    'verse': current_verse,
                })
            elif content == '':
                records.append({
                    'line_no': line_no,
                    'content': '',
                    'type': 'blank',
                    'verse': current_verse,
                })
            else:
                records.append({
                    'line_no': line_no,
                    'content': content,
                    'type': 'text',
                    'verse': current_verse,
                })

    return records


# ─── governor detection ───────────────────────────────────────────────────────

def match_governor(content: str, token_map: dict) -> Optional[str]:
    """
    Return the canonical governor key if the line starts with a governor token.
    Returns None if no match.
    """
    for key, prefixes in token_map.items():
        for prefix in prefixes:
            if content.startswith(prefix):
                return key
    return None


def build_all_governor_prefixes(classes: List[dict]) -> Set[str]:
    """Build a set of ALL governor prefixes across all structural classes."""
    result: Set[str] = set()
    for gc in classes:
        for prefixes in gc['token_map'].values():
            for p in prefixes:
                result.add(p)
    return result


ALL_GOVERNOR_PREFIXES: Set[str] = build_all_governor_prefixes(GOVERNOR_CLASSES)


# ─── span detection (records-based) ───────────────────────────────────────────

def starts_with_any_governor(content: str) -> bool:
    """Return True if the line starts with ANY governor prefix across all classes."""
    for p in ALL_GOVERNOR_PREFIXES:
        if content.startswith(p):
            return True
    return False


def build_members(records: List[dict], start_i: int,
                  gov_key: str, token_map: dict) -> Tuple[List[List[dict]], int]:
    """
    Build parallel members for a governor span starting at records[start_i].

    Constraints:
      - Member = gov_line + up to MAX_CONTINUATION non-governor continuation lines
      - Blank lines terminate member continuations (members don't span verse breaks)
      - A cross-class governor token on a continuation line terminates the member
        AND the span
      - Span continues across blank+verse_ref pairs to find next gov line
      - Span terminates when next content line does not start with our gov token

    Returns (members, next_i) where next_i is position to resume outer scan.
    """
    our_prefixes = token_map[gov_key]
    members: List[List[dict]] = []
    i = start_i
    n = len(records)
    span_terminated = False

    while i < n and not span_terminated:
        # Skip blanks and verse_refs to find next content line
        while i < n and records[i]['type'] in ('blank', 'verse_ref'):
            i += 1

        if i >= n:
            break

        rec = records[i]
        # Is this a governor line for our key?
        if not any(rec['content'].startswith(p) for p in our_prefixes):
            # Not our governor — span ends here
            break

        # Start a new member
        member: List[dict] = [rec]
        i += 1

        # Collect continuation lines
        # Rules: stop at blank, stop at same gov token (new member), stop at cross-class gov
        while i < n:
            r = records[i]

            if r['type'] == 'blank':
                # Blank terminates continuation. The span may continue (outer loop skips blank).
                break

            if r['type'] == 'verse_ref':
                # Verse ref mid-content (rare in this format) — treat as soft stop
                break

            # r is a text line
            # Check: is it another governor of our type?
            if any(r['content'].startswith(p) for p in our_prefixes):
                # New member starts here — don't consume, let outer loop handle
                break

            # Check: is it a cross-class governor?
            if starts_with_any_governor(r['content']):
                # End span entirely — a new structural class has started
                span_terminated = True
                break

            # Add as continuation if within limit
            continuations = len(member) - 1
            if continuations >= MAX_CONTINUATION:
                # Too many continuations — end span
                span_terminated = True
                break

            member.append(r)
            i += 1

        members.append(member)

    return members, i


def find_spans_for_class(records: List[dict], gov_class: dict) -> List[dict]:
    """
    Find all drift candidates for a single governor class in the given records.
    """
    token_map = gov_class['token_map']
    candidates: List[dict] = []
    i = 0
    n = len(records)

    while i < n:
        rec = records[i]

        if rec['type'] != 'text':
            i += 1
            continue

        gov_key = match_governor(rec['content'], token_map)
        if gov_key is None:
            i += 1
            continue

        # Build span from this governor line
        members, next_i = build_members(records, i, gov_key, token_map)

        if len(members) >= MIN_MEMBERS:
            line_counts = [len(m) for m in members]
            distinct = sorted(set(line_counts))

            if len(distinct) > 1:
                verdict = _classify_verdict(line_counts, gov_class['id'])
                candidates.append({
                    'gov_class_id': gov_class['id'],
                    'gov_class_name': gov_class['name'],
                    'gov_key': gov_key,
                    'members': members,
                    'line_counts': line_counts,
                    'n_members': len(members),
                    'm_patterns': len(distinct),
                    'distinct_patterns': distinct,
                    'verdict': verdict,
                    'start_verse': members[0][0]['verse'],
                    'end_verse': members[-1][-1]['verse'],
                    'start_line': members[0][0]['line_no'],
                    'file_path': None,
                    'book': None,
                    'chapter': None,
                })

        i = next_i if next_i > i else i + 1

    return candidates


def _classify_verdict(line_counts: List[int], class_id: str) -> str:
    """
    Assign a preliminary verdict.
    CONFIRMED DRIFT — clear inconsistency, likely real
    AMBIGUOUS       — marginal case, human review needed
    """
    n = len(line_counts)
    distinct = set(line_counts)
    m = len(distinct)
    max_count = max(line_counts.count(lc) for lc in distinct)
    outlier_count = n - max_count

    # Single outlier in a large span — might be intentional semantic variation
    if outlier_count == 1 and n >= 5:
        return "AMBIGUOUS"
    # All 1-2 line members with just one slightly longer — could be register variation
    if m == 2 and min(distinct) == 1 and max(distinct) == 2 and outlier_count <= 1:
        return "AMBIGUOUS"
    return "CONFIRMED DRIFT"


# ─── Class 5: repeated noun-phrase chains ─────────────────────────────────────

def first_word_lower(content: str) -> str:
    """
    Return the first whitespace-delimited token, lowercased and stripped of
    trailing Greek punctuation.
    """
    parts = content.split()
    if not parts:
        return ''
    word = parts[0].rstrip('·,;.·—»«"\'')
    return word.lower()


def find_repeated_noun_spans(records: List[dict]) -> List[dict]:
    """
    Class 5: find spans of N >= MIN_MEMBERS consecutive text lines starting
    with the same first content word (case-insensitive, punctuation-stripped).

    Uses blank-line boundaries for continuation (same as other classes).
    Excludes words in CLASS5_EXCLUSIONS.
    """
    candidates: List[dict] = []
    n = len(records)
    i = 0

    while i < n:
        rec = records[i]
        if rec['type'] != 'text':
            i += 1
            continue

        fw = first_word_lower(rec['content'])
        if not fw or fw in CLASS5_EXCLUSIONS:
            i += 1
            continue

        # Build span for repeated first-word governor
        # Treat fw as the governor key; build members using the same
        # blank-boundary logic as structural classes

        members: List[List[dict]] = []
        current_member: List[dict] = [rec]
        j = i + 1
        span_terminated = False

        while j < n and not span_terminated:
            r = records[j]

            if r['type'] in ('blank', 'verse_ref'):
                if r['type'] == 'blank':
                    # Blank: close current member, continue span search
                    members.append(current_member)
                    current_member = []

                    # Skip to next content line
                    j += 1
                    while j < n and records[j]['type'] in ('blank', 'verse_ref'):
                        j += 1

                    if j >= n:
                        break

                    # Is next content line the same first word?
                    next_rec = records[j]
                    nfw = first_word_lower(next_rec['content'])
                    if nfw == fw and nfw not in CLASS5_EXCLUSIONS:
                        # Continue span with new member
                        current_member = [next_rec]
                        j += 1
                    else:
                        span_terminated = True
                        break
                else:
                    # verse_ref mid-block: soft stop for continuation
                    members.append(current_member)
                    current_member = []
                    j += 1
                    while j < n and records[j]['type'] in ('blank', 'verse_ref'):
                        j += 1
                    if j >= n:
                        break
                    next_rec = records[j]
                    nfw = first_word_lower(next_rec['content'])
                    if nfw == fw and nfw not in CLASS5_EXCLUSIONS:
                        current_member = [next_rec]
                        j += 1
                    else:
                        span_terminated = True
                continue

            # Text line
            rfw = first_word_lower(r['content'])

            if rfw == fw and rfw not in CLASS5_EXCLUSIONS:
                # New member with same governor word
                if current_member:
                    members.append(current_member)
                current_member = [r]
                j += 1
            elif starts_with_any_governor(r['content']):
                # Cross-class governor — end span
                span_terminated = True
                break
            else:
                # Non-governor continuation
                continuations = len(current_member) - 1
                if continuations >= MAX_CONTINUATION:
                    span_terminated = True
                    break
                current_member.append(r)
                j += 1

        # Save last member
        if current_member:
            members.append(current_member)

        if len(members) >= MIN_MEMBERS:
            line_counts = [len(m) for m in members]
            distinct = sorted(set(line_counts))

            if len(distinct) > 1:
                verdict = _classify_verdict(line_counts, 'noun')
                candidates.append({
                    'gov_class_id': 'noun',
                    'gov_class_name': 'Repeated noun-phrase chains',
                    'gov_key': fw,
                    'members': members,
                    'line_counts': line_counts,
                    'n_members': len(members),
                    'm_patterns': len(distinct),
                    'distinct_patterns': distinct,
                    'verdict': verdict,
                    'start_verse': members[0][0]['verse'],
                    'end_verse': members[-1][-1]['verse'],
                    'start_line': members[0][0]['line_no'],
                    'file_path': None,
                    'book': None,
                    'chapter': None,
                })

        # Advance past the span
        i = j if j > i else i + 1

    return candidates


# ─── corpus scan ──────────────────────────────────────────────────────────────

def scan_corpus() -> List[dict]:
    """Walk all v4-editorial chapters and collect drift candidates."""
    all_candidates: List[dict] = []

    book_dirs = sorted(V4_DIR.iterdir())

    for book_dir in book_dirs:
        if not book_dir.is_dir():
            continue
        book_name = book_dir.name

        for chapter_file in sorted(book_dir.glob('*.txt')):
            chapter_name = chapter_file.stem
            records = parse_file(chapter_file)

            chapter_candidates: List[dict] = []

            for gov_class in GOVERNOR_CLASSES:
                spans = find_spans_for_class(records, gov_class)
                chapter_candidates.extend(spans)

            noun_spans = find_repeated_noun_spans(records)
            chapter_candidates.extend(noun_spans)

            for c in chapter_candidates:
                c['file_path'] = str(chapter_file.relative_to(REPO_ROOT))
                c['book'] = book_name
                c['chapter'] = chapter_name

            all_candidates.extend(chapter_candidates)

    return all_candidates


# ─── reporting ────────────────────────────────────────────────────────────────

def format_member(member: List[dict], idx: int) -> str:
    verse = member[0]['verse']
    body = "\n".join(f"      {l['content']}" for l in member)
    return f"  Member {idx+1} [{verse}, {len(member)} line(s)]:\n{body}"


def candidate_to_report_block(c: dict, rank: int) -> str:
    header = (
        f"### Candidate {rank}: `{c['book']}` — {c['chapter']} "
        f"— {c['start_verse']}–{c['end_verse']}"
    )
    meta = "\n".join([
        f"",
        f"- **File:** `{c['file_path']}` (line {c['start_line']})",
        f"- **Governor class:** {c['gov_class_id']} — {c['gov_class_name']}",
        f"- **Governor instance:** `{c['gov_key']}`",
        f"- **N members:** {c['n_members']}",
        f"- **M patterns:** {c['m_patterns']} — line counts: {c['line_counts']}",
        f"- **Distinct patterns:** {c['distinct_patterns']}",
        f"- **Scanner verdict:** {c['verdict']}",
        f"",
        f"**Members:**",
    ])
    member_strs = "\n".join(format_member(m, i) for i, m in enumerate(c['members']))
    return f"{header}\n{meta}\n{member_strs}\n"


def rank_candidates(candidates: List[dict]) -> List[dict]:
    def sort_key(c):
        verdict_rank = 0 if c['verdict'] == 'CONFIRMED DRIFT' else 1
        return (verdict_rank, -c['m_patterns'], -c['n_members'])
    return sorted(candidates, key=sort_key)


def write_report(candidates: List[dict], output_path: Path) -> None:
    ranked = rank_candidates(candidates)
    confirmed = [c for c in ranked if c['verdict'] == 'CONFIRMED DRIFT']
    ambiguous = [c for c in ranked if c['verdict'] == 'AMBIGUOUS']

    by_class: Dict[str, int] = defaultdict(int)
    by_book: Dict[str, int] = defaultdict(int)
    for c in candidates:
        by_class[c['gov_class_id']] += 1
        by_book[c['book']] += 1

    class_names = {
        'prep': 'Preposition-initial catenae',
        'eite': 'Disjunctive conditional chains (εἴτε)',
        'hos':  'Correlative chains (ὡς / καθώς)',
        'neg':  'Negation-disjunction chains',
        'noun': 'Repeated noun-phrase chains',
    }

    lines = [
        "# Parallelism Consistency Scan — Findings Report",
        "",
        "**Generated:** 2026-04-15",
        "**Scanner version:** v1 (five governor classes; blank-boundary continuations; cross-class span termination)",
        "**Corpus:** data/text-files/v4-editorial/ — all 260 chapters",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total candidates before adversarial audit:** {len(candidates)}",
        f"- **CONFIRMED DRIFT:** {len(confirmed)}",
        f"- **AMBIGUOUS (require human review):** {len(ambiguous)}",
        "",
        "### Breakdown by governor class",
        "",
    ]
    for cid, cname in class_names.items():
        cnt = by_class.get(cid, 0)
        lines.append(f"- {cname}: {cnt}")

    top_books = sorted(by_book.items(), key=lambda x: -x[1])[:10]
    lines += [
        "",
        "### Breakdown by book (top 10)",
        "",
    ]
    for book, count in top_books:
        lines.append(f"- {book}: {count}")

    lines += [
        "",
        "---",
        "",
        "## CONFIRMED DRIFT candidates",
        "",
        f"Total: {len(confirmed)}",
        "",
    ]
    for i, c in enumerate(confirmed):
        lines.append(candidate_to_report_block(c, i + 1))

    lines += [
        "",
        "---",
        "",
        "## AMBIGUOUS candidates",
        "",
        f"Total: {len(ambiguous)} — require human review before any fix",
        "",
    ]
    for i, c in enumerate(ambiguous):
        lines.append(candidate_to_report_block(c, i + 1))

    lines += [
        "",
        "---",
        "",
        "## Adversarial audit notes",
        "",
        "*(To be filled in after adversarial sub-agent review.)*",
        "",
        "---",
        "",
        "## Scanner anti-imposition notes",
        "",
        "This scanner reveals inconsistency in member line-counts within parallel spans.",
        "It does NOT prescribe the correct line-count. Consistent multi-line members",
        "are NOT flagged — only inconsistency between members is flagged.",
        "The adversarial audit (Stan's 'imposing vs revealing' test) is mandatory",
        "before treating any candidate as a confirmed fix target.",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding='utf-8')


def print_summary(candidates: List[dict]) -> None:
    ranked = rank_candidates(candidates)
    confirmed = [c for c in ranked if c['verdict'] == 'CONFIRMED DRIFT']
    ambiguous = [c for c in ranked if c['verdict'] == 'AMBIGUOUS']

    print(f"\n{'='*72}")
    print(f"PARALLELISM CONSISTENCY SCAN — RESULTS")
    print(f"{'='*72}")
    print(f"Total candidates:   {len(candidates)}")
    print(f"CONFIRMED DRIFT:    {len(confirmed)}")
    print(f"AMBIGUOUS:          {len(ambiguous)}")
    print(f"{'='*72}")

    if confirmed:
        print("\nCONFIRMED DRIFT (ranked by confidence):")
        for i, c in enumerate(confirmed[:30], 1):
            print(
                f"  {i:3}. [{c['gov_class_id']:5}] {c['book']}/{c['chapter']} "
                f"{c['start_verse']}–{c['end_verse']}  "
                f"gov={c['gov_key']}  N={c['n_members']}  M={c['m_patterns']}  "
                f"counts={c['line_counts']}  ln={c['start_line']}"
            )
        if len(confirmed) > 30:
            print(f"  ... and {len(confirmed) - 30} more (see report file)")

    if ambiguous:
        print(f"\nAMBIGUOUS (top 10):")
        for i, c in enumerate(ambiguous[:10], 1):
            print(
                f"  {i:3}. [{c['gov_class_id']:5}] {c['book']}/{c['chapter']} "
                f"{c['start_verse']}–{c['end_verse']}  "
                f"gov={c['gov_key']}  N={c['n_members']}  M={c['m_patterns']}  "
                f"counts={c['line_counts']}"
            )
        if len(ambiguous) > 10:
            print(f"  ... and {len(ambiguous) - 10} more (see report file)")

    print(f"\nFull report: {OUTPUT_FILE}")
    print(f"{'='*72}\n")


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    if not V4_DIR.exists():
        print(f"ERROR: v4-editorial directory not found: {V4_DIR}", file=sys.stderr)
        sys.exit(1)

    print("Scanning corpus...", flush=True)
    candidates = scan_corpus()
    print(f"Scan complete. {len(candidates)} candidates found.", flush=True)

    print_summary(candidates)
    write_report(candidates, OUTPUT_FILE)
    print(f"Report written to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
