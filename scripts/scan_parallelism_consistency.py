#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_parallelism_consistency.py

Walks data/text-files/v4-editorial/ looking for spans where N >= 3 parallel
coordinate members under a shared governor are broken into M != 1 different
stack patterns (different line-counts per member), PLUS six structural-jam
classes that detect list members crammed onto single lines.

Eleven governor classes (v2):
  --- Consistency classes (existing v1) ---
  1. prep   — Preposition-initial catenae (ἐν, διά/διὰ, κατά/κατὰ, ἐπί/ἐπὶ, etc.)
  2. eite   — Disjunctive conditional chains (εἴτε)
  3. hos    — Correlative chains (ὡς, καθώς, καθάπερ)
  4. neg    — Negation-disjunction chains (οὔτε, μήτε, μή/Μή, οὐδέ/οὐδὲ, μηδέ/μηδὲ)
  5. noun   — Repeated noun-phrase chains (same first content-word N >= 3 consecutive lines)

  --- Structural-jam classes (new v2) ---
  6. kai_verb_jam   — καί-repetition with trailing verb-jam (Eph 4:31 pre-fix canonical)
  7. head_list_jam  — Head-of-list jam: governing verb + list-members jammed on line 1
  8. mid_asym       — Mid-list asymmetric grouping (Rev 5:12 pre-fix canonical)
  9. bare_asyndeton — Bare asyndetic virtue/vice lists (1 Pet 3:8 canonical)
 10. ordinal_chain  — Ordinal chains (1 Cor 12:28 pre-fix canonical)
 11. gen_dep        — Genitive-dependency chains (Rom 1:29 pre-fix canonical)

Key design constraints (v1 classes):
  - Blank lines terminate member continuations (members do not span verse breaks)
  - A cross-class governor token terminates the current span
  - Members: gov_line + up to MAX_CONTINUATION non-governor continuation lines
  - Only M > 1 (inconsistent member sizes) generates a candidate

Output:
  - Console: one summary line per CONFIRMED_DRIFT candidate
  - File:    private/scan-parallelism-v2-findings.md (full report)

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
OUTPUT_FILE = REPO_ROOT / "private" / "scan-parallelism-v2-findings.md"

# ─── parameters ───────────────────────────────────────────────────────────────
MIN_MEMBERS = 3       # minimum parallel members to constitute a span (v1 classes)
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
        while i < n:
            r = records[i]

            if r['type'] == 'blank':
                break

            if r['type'] == 'verse_ref':
                break

            # r is a text line
            if any(r['content'].startswith(p) for p in our_prefixes):
                break

            if starts_with_any_governor(r['content']):
                span_terminated = True
                break

            continuations = len(member) - 1
            if continuations >= MAX_CONTINUATION:
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
    CONFIRMED_DRIFT — clear inconsistency, likely real
    AMBIGUOUS       — marginal case, human review needed
    LIKELY_FP       — probable false positive
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
    return "CONFIRMED_DRIFT"


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

        members: List[List[dict]] = []
        current_member: List[dict] = [rec]
        j = i + 1
        span_terminated = False

        while j < n and not span_terminated:
            r = records[j]

            if r['type'] in ('blank', 'verse_ref'):
                if r['type'] == 'blank':
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
                        break
                else:
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
                if current_member:
                    members.append(current_member)
                current_member = [r]
                j += 1
            elif starts_with_any_governor(r['content']):
                span_terminated = True
                break
            else:
                continuations = len(current_member) - 1
                if continuations >= MAX_CONTINUATION:
                    span_terminated = True
                    break
                current_member.append(r)
                j += 1

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

        i = j if j > i else i + 1

    return candidates


# ─── v2 helper utilities ──────────────────────────────────────────────────────

# Greek connective particles — presence on a line disqualifies bare-asyndeton detection
CONNECTORS: Set[str] = {
    'καί', 'καὶ', 'ἤ', 'ἢ', 'οὔτε', 'μήτε', 'οὐδέ', 'οὐδὲ', 'μηδέ', 'μηδὲ',
    'τε', 'ἀλλά', 'ἀλλὰ', 'δέ', 'δὲ', 'γάρ', 'γὰρ', 'οὖν', 'ἄρα',
}

# Ordinal markers (Greek)
ORDINALS: List[str] = [
    'πρῶτον', 'δεύτερον', 'τρίτον', 'τέταρτον', 'πέμπτον',
    'ἕκτον', 'ἕβδομον', 'ὄγδοον', 'ἔνατον', 'δέκατον',
    'ἔπειτα', 'εἶτα',
]

# Head words for genitive-dependency chains
GEN_HEAD_WORDS: Set[str] = {
    'μεστούς', 'μεστοὺς', 'μεστός', 'μεστὸς', 'μεστή', 'μεστὴ',
    'πλήρης', 'πλήρεις', 'πλήρη',
    'πεπληρωμένους', 'πεπληρωμένη', 'πεπληρωμένος', 'πεπληρωμένοι',
    'γέμουσαι', 'γέμοντα', 'γέμων',
}

# Greek list markers that signal parallel list membership
LIST_MARKERS: List[str] = [
    'καὶ ', 'καί ', 'ἤ ', 'ἢ ', 'εἴτε ', 'οὔτε ', 'μήτε ',
]

# Verb-like endings that signal a finite verb / infinitive in Greek
# (heuristic suffix check — not full morphology)
VERB_ENDINGS = re.compile(
    r'(?:'
    r'[αε]ι$|'        # 3sg pres/imperf act
    r'[οε]υ?ν$|'      # 3pl pres/fut act, or infinitive -ειν -ον
    r'ε(?:τε|τω|σθε|σθω)$|'  # 2/3 imperative/present
    r'ατε$|αντο$|ατω$|'
    r'ε(?:ιν|σθαι)$|'  # infinitives
    r'[θσ]αι$|'        # aorist infinitives
    r'[αη]ναι$|'       # perfect / passive infinitives
    r'[αεη]σεται$|[αεη]σονται$|'  # future
    r'[θη][τη]?ι$|'    # passive 3sg
    r'ετ[οω]$|'
    r'ωσιν?$|'
    r'ομεν$|ετε$'
    r')'
)


def line_word_count(content: str) -> int:
    """Return number of whitespace-delimited tokens."""
    return len(content.split())


def line_has_verb_heuristic(content: str) -> bool:
    """
    Heuristic: does the line contain something that looks like a finite verb
    or infinitive?  Uses suffix patterns only — not morphology.
    """
    tokens = content.split()
    for tok in tokens:
        # Strip punctuation
        tok_clean = tok.rstrip('·,;.·—»«"\'').lstrip('"\'«»')
        if len(tok_clean) >= 4 and VERB_ENDINGS.search(tok_clean):
            return True
    return False


def make_jam_candidate(
    gov_class_id: str,
    gov_class_name: str,
    gov_key: str,
    lines: List[dict],         # the relevant line records
    n_members: int,
    m_patterns: int,
    current_stack_pattern: str,
    verdict: str,
) -> dict:
    """Build a candidate dict for v2 jam classes (no members list — line-level)."""
    start = lines[0]
    end = lines[-1]
    return {
        'gov_class_id': gov_class_id,
        'gov_class_name': gov_class_name,
        'gov_key': gov_key,
        'lines': lines,
        'members': [],           # not used for jam classes
        'line_counts': [],       # not used
        'n_members': n_members,
        'm_patterns': m_patterns,
        'distinct_patterns': [],
        'current_stack_pattern': current_stack_pattern,
        'verdict': verdict,
        'start_verse': start['verse'],
        'end_verse': end['verse'],
        'start_line': start['line_no'],
        'file_path': None,
        'book': None,
        'chapter': None,
    }


# ─── Class 6: καί-repetition with trailing verb-jam ──────────────────────────

def find_kai_verb_jam(records: List[dict]) -> List[dict]:
    """
    Class 6: N >= 3 consecutive lines starting with καί where the FINAL
    line is significantly longer than the preceding ones (verb + objects
    jammed alongside the last list member).

    Canonical pre-fix pattern (Eph 4:31 before session-18 fix):
      πᾶσα πικρία
      καὶ θυμὸς
      καὶ ὀργὴ
      καὶ κραυγὴ
      καὶ βλασφημία
      ἀρθήτω ἀφʼ ὑμῶν σὺν πάσῃ κακίᾳ.   ← verb line following the list

    Also detects jam-on-final-καί-line:
      καὶ Α
      καὶ Β
      καὶ Γ καὶ Δ verb-phrase    ← final member jammed with extra content

    Detection logic:
      - Find runs of N >= 3 lines starting with καί/καὶ
      - If the last member line is >= VERB_JAM_WORD_EXCESS words longer than
        the median of the preceding lines, flag it
      - OR if a non-καί line immediately follows a καί run of N >= 3 and
        that following line has a verb heuristic with word count >= 3
        (trailing verb-jam after the list)
    """
    KAI_PREFIXES = ('καὶ ', 'καί ')
    VERB_JAM_WORD_EXCESS = 3  # final member must be this many words longer than median
    candidates: List[dict] = []
    n = len(records)
    i = 0

    while i < n:
        rec = records[i]
        if rec['type'] != 'text':
            i += 1
            continue

        # Start of a καί run?
        if not any(rec['content'].startswith(p) for p in KAI_PREFIXES):
            i += 1
            continue

        # Collect the run
        run: List[dict] = [rec]
        j = i + 1
        while j < n and records[j]['type'] == 'text' and any(
            records[j]['content'].startswith(p) for p in KAI_PREFIXES
        ):
            run.append(records[j])
            j += 1

        if len(run) >= 3:
            wcs = [line_word_count(r['content']) for r in run]
            # Check: final line significantly longer (verb-jam on final member)
            median_pre = sorted(wcs[:-1])[len(wcs[:-1]) // 2]
            final_wc = wcs[-1]
            if final_wc >= median_pre + VERB_JAM_WORD_EXCESS and line_has_verb_heuristic(run[-1]['content']):
                stack_pattern = f"first {len(run)-1} lines short (≤{median_pre} words), final line {final_wc} words with verb"
                verdict = "CONFIRMED_DRIFT"
                candidates.append(make_jam_candidate(
                    'kai_verb_jam', 'καί-repetition with trailing verb-jam',
                    'καί', run, len(run), 2, stack_pattern, verdict
                ))
                i = j
                continue

            # Check: trailing verb line AFTER the run (non-καί line with verb)
            if j < n and records[j]['type'] == 'text':
                next_line = records[j]
                next_wc = line_word_count(next_line['content'])
                if (not any(next_line['content'].startswith(p) for p in KAI_PREFIXES)
                        and next_wc >= 3
                        and line_has_verb_heuristic(next_line['content'])):
                    # Ambiguous: could be natural continuation after list
                    # Only flag if preceding line is very short (pure noun member)
                    pre_wcs = [line_word_count(r['content']) for r in run]
                    if all(wc <= 3 for wc in pre_wcs) and next_wc >= 5:
                        trailing = run + [next_line]
                        stack_pattern = f"{len(run)} short καί-members, trailing verb line ({next_wc} words)"
                        verdict = "AMBIGUOUS"
                        candidates.append(make_jam_candidate(
                            'kai_verb_jam', 'καί-repetition with trailing verb-jam',
                            'καί', trailing, len(run) + 1, 2, stack_pattern, verdict
                        ))
                        i = j + 1
                        continue

        i = j if j > i else i + 1

    return candidates


# ─── Class 7: head-of-list jam ────────────────────────────────────────────────

def find_head_list_jam(records: List[dict]) -> List[dict]:
    """
    Class 7: Governing verb + first 1-2 list members crammed onto line 1,
    with subsequent members each on their own line.

    Canonical example (2 Cor 11:20):
      ἀνέχεσθε γὰρ            ← governor (verb already here, no list marker yet)
      εἴ τις ὑμᾶς καταδουλοῖ,
      εἴ τις κατεσθίει,       ← but these are εἴτε class — detected separately

    Real head-jam detection targets patterns like:
      ἀνέχεσθε γάρ + εἴ τις X, εἴ τις Y    (verb + 2 members on line 1)
      followed by: εἴ τις Z, εἴ τις W       (solo members each line)

    More general heuristic:
      Line 1: contains a list marker (καὶ/ἤ/εἴ τις/εἴτε) AND has word count
              significantly higher than subsequent lines that use the same marker.
      Subsequent N >= 2 lines each have exactly one list marker and are shorter.

    This detects: verb + list-marker-X + list-marker-Y / list-marker-Z (split) / list-marker-W (split)
    """
    LIST_MARKER_RE = re.compile(
        r'(?:^|(?<=\s))(?:καὶ|καί|ἤ|ἢ|εἴτε|εἴ\s+τις|οὔτε|μήτε)\s',
    )

    candidates: List[dict] = []
    n = len(records)
    i = 0

    while i < n:
        rec = records[i]
        if rec['type'] != 'text':
            i += 1
            continue

        content = rec['content']
        # Count list markers on this line
        markers_on_line = LIST_MARKER_RE.findall(content)
        if len(markers_on_line) < 2:
            i += 1
            continue

        # This line has 2+ list markers (candidate head-jam)
        first_marker = markers_on_line[0].strip()
        line1_wc = line_word_count(content)

        # Look ahead for subsequent lines each using ONE of the same markers
        subsequent: List[dict] = []
        j = i + 1
        while j < n and records[j]['type'] == 'text':
            r = records[j]
            sub_markers = LIST_MARKER_RE.findall(r['content'])
            # Line with exactly one list marker and shorter than line 1
            if len(sub_markers) == 1 and line_word_count(r['content']) < line1_wc:
                subsequent.append(r)
                j += 1
            else:
                break

        # Need at least 1 subsequent (N >= 2 total members including head-jam)
        # spec says N >= 2 for head-jam class
        if len(subsequent) >= 1:
            all_lines = [rec] + subsequent
            total_members = 1 + len(subsequent)  # head counts as 1 jammed member
            stack_pattern = (
                f"line 1 has {len(markers_on_line)} list markers ({line1_wc} words), "
                f"{len(subsequent)} subsequent solo-marker lines"
            )
            verdict = "CONFIRMED_DRIFT" if len(markers_on_line) >= 2 and len(subsequent) >= 2 else "AMBIGUOUS"
            candidates.append(make_jam_candidate(
                'head_list_jam', 'Head-of-list jam',
                first_marker, all_lines, total_members, 2, stack_pattern, verdict
            ))
            i = j
            continue

        i += 1

    return candidates


# ─── Class 8: mid-list asymmetric grouping ────────────────────────────────────

def find_mid_asym(records: List[dict]) -> List[dict]:
    """
    Class 8: N >= 5 members under a shared governor, split into uneven groups
    (e.g. 2+2+1+1+1 rather than uniform 1+1+1+1+1+1+1).

    Detect: consecutive lines with the SAME governor-marker (καί, ἤ, ἐν, etc.)
    but different member counts per line (i.e., some lines contain 2+ members
    of the list while others contain only 1).

    Concretely: a line with a governor-marker that ALSO contains a SECOND
    occurrence of that same marker (or a related connector) signals that
    2 members are jammed on one line.

    Example (Rev 5:12 pre-fix):
      τὴν δύναμιν καὶ πλοῦτον   ← 2 members on one line
      καὶ σοφίαν                 ← 1 member
      καὶ ἰσχὺν                  ← 1 member

    Detection:
      - Find runs of N >= 5 lines that each START with the same marker
        (or contain only that marker's content words)
      - OR find runs where a line starting with the marker ALSO contains
        a second instance of that marker, flanked by single-marker lines
    """
    # Look for runs of καί-led lines where some lines have internal καί
    KAI_START = re.compile(r'^(?:καὶ|καί)\s+')
    KAI_INTERNAL = re.compile(r'\s(?:καὶ|καί)\s')

    candidates: List[dict] = []
    n = len(records)
    i = 0

    while i < n:
        rec = records[i]
        if rec['type'] != 'text':
            i += 1
            continue

        if not KAI_START.match(rec['content']):
            i += 1
            continue

        # Collect run of καί-starting lines
        run: List[dict] = [rec]
        j = i + 1
        while j < n and records[j]['type'] == 'text' and KAI_START.match(records[j]['content']):
            run.append(records[j])
            j += 1

        if len(run) >= 4:
            # Check if any line in the run has internal καί (multi-member line)
            multi_member_lines = [r for r in run if KAI_INTERNAL.search(r['content'])]
            solo_member_lines = [r for r in run if not KAI_INTERNAL.search(r['content'])]

            if multi_member_lines and solo_member_lines:
                # Asymmetric grouping
                multi_counts = [len(KAI_INTERNAL.findall(r['content'])) + 1
                                for r in multi_member_lines]
                total_members = sum(multi_counts) + len(solo_member_lines)
                if total_members >= 5:
                    stack_pattern = (
                        f"{len(multi_member_lines)} multi-member line(s) "
                        f"({multi_counts} members each) + "
                        f"{len(solo_member_lines)} solo-member lines; "
                        f"est. {total_members} total members"
                    )
                    verdict = "CONFIRMED_DRIFT" if len(multi_member_lines) >= 1 and total_members >= 5 else "AMBIGUOUS"
                    candidates.append(make_jam_candidate(
                        'mid_asym', 'Mid-list asymmetric grouping',
                        'καί', run, total_members, 2, stack_pattern, verdict
                    ))

        i = j if j > i else i + 1

    return candidates


# ─── Class 9: bare asyndetic virtue/vice lists ────────────────────────────────

def find_bare_asyndeton(records: List[dict]) -> List[dict]:
    """
    Class 9: Single line with N >= 3 nominative/accusative adjectives or nouns
    separated by commas, no connectors (καί/ἤ/οὔτε etc.) between them.

    Canonical example (1 Pet 3:8 pre-fix would be if all on one line):
      ὁμόφρονες, συμπαθεῖς, φιλάδελφοι, εὔσπλαγχνοι, ταπεινόφρονες

    Since the current file already has 1 Pet 3:8 split, we look for
    cases where comma-separated short items appear on the SAME line.

    Heuristic:
      - Split line on commas
      - 3+ parts
      - Each part is 1-3 words
      - No connector words (from CONNECTORS set) anywhere in the line
      - Not a verse reference
      - Not a vocative address (e.g. "Κύριε, σῶσον" — short imperative)
        — exclude by requiring all parts to look like nominals (no imperatives/vocatives)

    Anti-FP filters:
      - Exclude lines beginning with a vocative-like pattern (capitalized noun + comma)
      - Exclude lines that are clearly speech addresses
      - Require total word count >= 4 (single-word items, plural)
    """
    VOCATIVE_PATTERNS = re.compile(
        r'^(?:Κύριε|Κύριος|Πάτερ|πάτερ|Ἀββᾶ|κύριε|Ἰσραήλ|Ναί|ναί|Μὴ|Μακάριος|Θαρσεῖτε|Τέκνον)\b'
    )

    candidates: List[dict] = []

    for rec in records:
        if rec['type'] != 'text':
            continue
        content = rec['content']

        # Quick reject: must contain at least 2 commas
        if content.count(',') < 2:
            continue

        # No connectors
        tokens_set = set(t.strip('·,;.·—»«"\'') for t in content.split())
        if tokens_set & CONNECTORS:
            continue

        # Split on commas, filter empty
        parts = [p.strip() for p in content.split(',') if p.strip()]
        if len(parts) < 3:
            continue

        # Each part must be short (1-4 words max)
        if not all(1 <= len(p.split()) <= 4 for p in parts):
            continue

        # No vocative patterns
        if VOCATIVE_PATTERNS.match(content):
            continue

        # Exclude lines that are likely imperative speech / exhortations
        # (heuristic: if the line ends with a period and starts with a capital
        #  that's a complete sentence, not a list item)
        # Require total word count >= 4 to exclude very short lines
        total_wc = line_word_count(content)
        if total_wc < 4:
            continue

        # Require at least 3 of the parts to look like adjective/noun forms
        # (heuristic: each part ends in a nominal-ish ending, no verb endings)
        verb_like_parts = sum(1 for p in parts if line_has_verb_heuristic(p))
        if verb_like_parts > 1:
            continue

        # Candidate found
        stack_pattern = f"{len(parts)} comma-separated parts, no connectors, on 1 line"
        verdict = "CONFIRMED_DRIFT" if len(parts) >= 4 else "AMBIGUOUS"
        candidates.append(make_jam_candidate(
            'bare_asyndeton', 'Bare asyndetic virtue/vice lists',
            f'(asyndeton-{len(parts)})',
            [rec], len(parts), 1, stack_pattern, verdict
        ))

    return candidates


# ─── Class 10: ordinal chains ─────────────────────────────────────────────────

def find_ordinal_chains(records: List[dict]) -> List[dict]:
    """
    Class 10: Two or more ordinal markers (πρῶτον, δεύτερον, τρίτον, ἔπειτα, εἶτα,
    etc.) appearing on the SAME line — signals that ordinal list members are jammed.

    Canonical pre-fix: a line like
      πρῶτον ἀποστόλους, δεύτερον προφήτας, τρίτον διδασκάλους
    (currently 1 Cor 12:28 is already split, so this catches remaining cases)

    Also catches: ἔπειτα X, εἶτα Y on the same line (1 Cor 15:5-8 area).
    """
    candidates: List[dict] = []

    for rec in records:
        if rec['type'] != 'text':
            continue
        content = rec['content']
        tokens = content.split()

        found_ordinals = [o for o in ORDINALS if o in tokens]
        if len(found_ordinals) >= 2:
            stack_pattern = f"ordinals on same line: {found_ordinals}"
            # If 3+ ordinals crammed = high confidence
            verdict = "CONFIRMED_DRIFT" if len(found_ordinals) >= 3 else "AMBIGUOUS"
            candidates.append(make_jam_candidate(
                'ordinal_chain', 'Ordinal chains',
                '+'.join(found_ordinals),
                [rec], len(found_ordinals), 1, stack_pattern, verdict
            ))

    return candidates


# ─── Class 11: genitive-dependency chains ─────────────────────────────────────

def find_gen_dep_chains(records: List[dict]) -> List[dict]:
    """
    Class 11: Line starting with or containing a 'head word' (participial adjective
    taking genitive complement: μεστούς, πεπληρωμένους, πλήρης, γέμων, etc.)
    followed by N >= 3 genitive nouns separated by commas (without καί).

    Canonical pre-fix (Rom 1:29 before fix):
      πεπληρωμένους πάσῃ ἀδικίᾳ, πονηρίᾳ, πλεονεξίᾳ, κακίᾳ

    Heuristic:
      - Line contains one of the GEN_HEAD_WORDS
      - Line has 3+ commas
      - Tokens between commas look like single nouns (short)
      - No καί connectors
    """
    candidates: List[dict] = []

    for rec in records:
        if rec['type'] != 'text':
            continue
        content = rec['content']

        # Check for head word
        tokens = content.split()
        clean_tokens = {t.rstrip('·,;.·—»«"\'').lstrip('"\'«»') for t in tokens}
        if not (clean_tokens & GEN_HEAD_WORDS):
            continue

        # Must have 3+ commas (4+ parts)
        if content.count(',') < 3:
            continue

        # No καί connectors
        if any(t.strip('·,;.·') in ('καὶ', 'καί') for t in tokens):
            continue

        parts = [p.strip() for p in content.split(',') if p.strip()]
        if len(parts) < 4:
            continue

        # All parts short
        if not all(len(p.split()) <= 4 for p in parts):
            continue

        head_word = next((t for t in clean_tokens if t in GEN_HEAD_WORDS), '?')
        stack_pattern = f"head '{head_word}' + {len(parts)} comma-delimited genitives on 1 line"
        verdict = "CONFIRMED_DRIFT"
        candidates.append(make_jam_candidate(
            'gen_dep', 'Genitive-dependency chains',
            head_word,
            [rec], len(parts), 1, stack_pattern, verdict
        ))

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

            # v1 classes
            for gov_class in GOVERNOR_CLASSES:
                spans = find_spans_for_class(records, gov_class)
                chapter_candidates.extend(spans)

            noun_spans = find_repeated_noun_spans(records)
            chapter_candidates.extend(noun_spans)

            # v2 classes
            chapter_candidates.extend(find_kai_verb_jam(records))
            chapter_candidates.extend(find_head_list_jam(records))
            chapter_candidates.extend(find_mid_asym(records))
            chapter_candidates.extend(find_bare_asyndeton(records))
            chapter_candidates.extend(find_ordinal_chains(records))
            chapter_candidates.extend(find_gen_dep_chains(records))

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


def format_lines(lines: List[dict]) -> str:
    """Format the raw lines for a v2 jam candidate."""
    out = []
    for l in lines:
        out.append(f"      [{l['verse']}:{l['line_no']}]  {l['content']}")
    return "\n".join(out)


def candidate_to_report_block(c: dict, rank: int) -> str:
    header = (
        f"### Candidate {rank}: `{c['book']}` — {c['chapter']} "
        f"— {c['start_verse']}–{c['end_verse']}"
    )
    stack_pat = c.get('current_stack_pattern', '')
    meta_items = [
        f"",
        f"- **File:** `{c['file_path']}` (line {c['start_line']})",
        f"- **Governor class:** {c['gov_class_id']} — {c['gov_class_name']}",
        f"- **Governor instance:** `{c['gov_key']}`",
        f"- **N members / items:** {c['n_members']}",
        f"- **M patterns:** {c['m_patterns']}",
        f"- **Stack pattern:** {stack_pat}" if stack_pat else "",
        f"- **Distinct patterns:** {c['distinct_patterns']}" if c['distinct_patterns'] else "",
        f"- **Scanner verdict:** {c['verdict']}",
        f"",
    ]
    meta = "\n".join(l for l in meta_items if l is not None)

    if c['members']:
        content_block = "**Members:**\n" + "\n".join(
            format_member(m, i) for i, m in enumerate(c['members'])
        )
    elif c.get('lines'):
        content_block = "**Lines:**\n" + format_lines(c['lines'])
    else:
        content_block = "*(no line detail)*"

    return f"{header}\n{meta}\n{content_block}\n"


def rank_candidates(candidates: List[dict]) -> List[dict]:
    def sort_key(c):
        verdict_rank = 0 if c['verdict'] == 'CONFIRMED_DRIFT' else (1 if c['verdict'] == 'AMBIGUOUS' else 2)
        return (verdict_rank, -c['m_patterns'], -c['n_members'])
    return sorted(candidates, key=sort_key)


CLASS_NAMES = {
    'prep':          'Preposition-initial catenae',
    'eite':          'Disjunctive conditional chains (εἴτε)',
    'hos':           'Correlative chains (ὡς / καθώς)',
    'neg':           'Negation-disjunction chains',
    'noun':          'Repeated noun-phrase chains',
    'kai_verb_jam':  'καί-repetition with trailing verb-jam',
    'head_list_jam': 'Head-of-list jam',
    'mid_asym':      'Mid-list asymmetric grouping',
    'bare_asyndeton':'Bare asyndetic virtue/vice lists',
    'ordinal_chain': 'Ordinal chains',
    'gen_dep':       'Genitive-dependency chains',
}


def write_report(candidates: List[dict], output_path: Path) -> None:
    ranked = rank_candidates(candidates)
    confirmed = [c for c in ranked if c['verdict'] == 'CONFIRMED_DRIFT']
    ambiguous = [c for c in ranked if c['verdict'] == 'AMBIGUOUS']
    likely_fp = [c for c in ranked if c['verdict'] == 'LIKELY_FP']

    by_class: Dict[str, int] = defaultdict(int)
    by_book: Dict[str, int] = defaultdict(int)
    for c in candidates:
        by_class[c['gov_class_id']] += 1
        by_book[c['book']] += 1

    lines = [
        "# Parallelism Consistency Scan — Findings Report (v2)",
        "",
        "**Generated:** 2026-04-17",
        "**Scanner version:** v2 (eleven governor classes; six new jam-detection classes)",
        "**Corpus:** data/text-files/v4-editorial/ — all 260 chapters",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"- **Total candidates:** {len(candidates)}",
        f"- **CONFIRMED_DRIFT:** {len(confirmed)}",
        f"- **AMBIGUOUS (require human review):** {len(ambiguous)}",
        f"- **LIKELY_FP:** {len(likely_fp)}",
        "",
        "### Breakdown by governor class",
        "",
    ]
    for cid, cname in CLASS_NAMES.items():
        cnt = by_class.get(cid, 0)
        confirmed_cnt = sum(1 for c in confirmed if c['gov_class_id'] == cid)
        lines.append(f"- **{cid}** ({cname}): {cnt} total, {confirmed_cnt} CONFIRMED_DRIFT")

    top_books = sorted(by_book.items(), key=lambda x: -x[1])[:15]
    lines += [
        "",
        "### Breakdown by book (top 15)",
        "",
    ]
    for book, count in top_books:
        lines.append(f"- {book}: {count}")

    lines += [
        "",
        "---",
        "",
        "## CONFIRMED_DRIFT candidates",
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

    if likely_fp:
        lines += [
            "",
            "---",
            "",
            "## LIKELY_FP (probable false positives)",
            "",
            f"Total: {len(likely_fp)}",
            "",
        ]
        for i, c in enumerate(likely_fp):
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
        "This scanner reveals inconsistency in member line-counts within parallel spans",
        "and structural jams where list members appear crammed onto single lines.",
        "It does NOT prescribe the correct line-count. The adversarial audit",
        "(Stan's 'imposing vs revealing' test) is mandatory before treating any",
        "candidate as a confirmed fix target.",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding='utf-8')


def print_summary(candidates: List[dict]) -> None:
    ranked = rank_candidates(candidates)
    confirmed = [c for c in ranked if c['verdict'] == 'CONFIRMED_DRIFT']
    ambiguous = [c for c in ranked if c['verdict'] == 'AMBIGUOUS']

    print(f"\n{'='*72}")
    print(f"PARALLELISM CONSISTENCY SCAN v2 — RESULTS")
    print(f"{'='*72}")
    print(f"Total candidates:   {len(candidates)}")
    print(f"CONFIRMED_DRIFT:    {len(confirmed)}")
    print(f"AMBIGUOUS:          {len(ambiguous)}")
    print(f"{'='*72}")

    print("\nBy class:")
    for cid, cname in CLASS_NAMES.items():
        total = sum(1 for c in candidates if c['gov_class_id'] == cid)
        conf = sum(1 for c in confirmed if c['gov_class_id'] == cid)
        if total > 0:
            print(f"  {cid:16s}  total={total:3d}  confirmed={conf:3d}  ({cname})")

    by_book: Dict[str, int] = defaultdict(int)
    for c in confirmed:
        by_book[c['book']] += 1
    top_books = sorted(by_book.items(), key=lambda x: -x[1])[:10]
    print("\nConfirmed drift by book (top 10):")
    for book, count in top_books:
        print(f"  {book}: {count}")

    if confirmed:
        print("\nCONFIRMED_DRIFT top cases:")
        for i, c in enumerate(confirmed[:20], 1):
            stack = c.get('current_stack_pattern', '')
            if not stack and c.get('line_counts'):
                stack = str(c['line_counts'])
            print(
                f"  {i:3}. [{c['gov_class_id']:16s}] {c['book']}/{c['chapter']} "
                f"{c['start_verse']}  "
                f"gov={c['gov_key']}  N={c['n_members']}  "
                f"ln={c['start_line']}"
            )
            if stack:
                print(f"       {stack[:90]}")
        if len(confirmed) > 20:
            print(f"  ... and {len(confirmed) - 20} more (see report file)")

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
