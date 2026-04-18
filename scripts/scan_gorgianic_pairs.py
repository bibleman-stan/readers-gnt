#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_gorgianic_pairs.py

Scans data/text-files/v4-editorial/ for gorgianic pair candidates:
N=2 coordinate members forming a unified rhetorical image (hendiadys)
that may be over-split — M1 merge candidates per the new merge doctrine.

Detection signature:
  - Two consecutive non-blank lines where:
    (a) Line 2 starts with καί (coordinate) OR is asyndetic continuation
    (b) Each line is short (≤ MAX_TOKENS Greek tokens)
    (c) Both lines share grammatical form (both nouns, both adjectives,
        both participles, both verbs in same register — heuristic only)
    (d) No additional structural marker interrupts them (no finite verb
        on line 1 that would make each independently predicated)
    (e) No third καί follows immediately (which would signal N≥3 series)
    (f) The pair is NOT embedded inside a known N≥3 governor span

Triage:
  CONFIRMED_DRIFT  — strong evidence of over-split hendiadys, should merge
  AMBIGUOUS        — structural signals mixed, judgment needed
  LIKELY_FP        — scanner flagged but legitimate split (series member,
                     independent predicates, different grammatical class, etc.)

Output:
  - Console: summary counts
  - File: private/scan-gorgianic-pairs-findings.md

Usage:
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_gorgianic_pairs.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ─── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
V4_DIR = REPO_ROOT / "data" / "text-files" / "v4-editorial"
OUTPUT_FILE = REPO_ROOT / "private" / "scan-gorgianic-pairs-findings.md"

# ─── parameters ───────────────────────────────────────────────────────────────
MAX_TOKENS = 5          # maximum Greek tokens per line to qualify as "short"
MIN_TOKENS = 1          # minimum tokens per line (exclude blank/verse-ref lines)

# ─── Greek morphological helpers ──────────────────────────────────────────────

# Tokens that count as structural markers signaling independent structure
# (if present on line 1, the pair likely has independent predication)
FINITE_VERB_ENDINGS = (
    "ει", "εις", "ομεν", "ετε", "ουσιν", "ουσι",
    "ω", "ης", "ῃ", "ωμεν", "ητε", "ωσιν",
    "εν", "ε", "αν", "ατε", "ασιν", "ας",
    "ην", "ης", "ην",
    "σω", "σεις", "σει", "σομεν", "σετε", "σουσιν",
    "θη", "θης", "θησαν", "θητε", "θωμεν",
    "ται", "νται", "σθαι", "μαι", "σαι",
)

# Structural subordinators — if line 1 ends with or line 2 starts with these,
# the split is structurally motivated
SUBORDINATORS = {
    "ἵνα", "ὅτι", "ὅτε", "ὅταν", "ὥστε", "ὡς", "εἰ", "ἐάν",
    "ὅπως", "ἕως", "πρίν", "μήποτε", "καθώς", "καθάπερ",
    "ἐπεί", "ἐπειδή", "διότι", "ὅθεν",
}

# Discourse markers that signal independent structure (not hendiadys connectors)
DISCOURSE_MARKERS = {
    "ἀλλά", "ἀλλ᾿", "ἀλλʼ", "γάρ", "δέ", "δὲ", "μέν", "μὲν",
    "οὖν", "τοίνυν", "ἄρα", "ὅμως", "πλήν",
}

# Particles that indicate N≥3 series continuation (scan context window)
KAI_VARIANTS = {"καί", "κἀγώ", "κἀκεῖ", "κἀκεῖθεν", "κἄν", "κἀντεῦθεν"}

# Noun/adjective inflectional endings (for heuristic POS matching)
# Rough heuristic — precision ~70% for nouns/adjectives
NOUN_ADJ_ENDINGS = (
    "ος", "ου", "ῳ", "ον", "ε", "οι", "ων", "οις", "ους",
    "η", "ης", "ῃ", "ην", "αι", "ων", "αις", "ας",
    "α", "ας", "ᾳ",
    "υς", "υ", "εως", "ει", "εις",
)

# Participle endings (for heuristic POS matching)
PARTICIPLE_ENDINGS = (
    "ων", "οντος", "οντι", "οντα", "οντες", "οντων", "ουσα", "ουσης",
    "ουσῃ", "ουσαν", "ουσαι",
    "ας", "αντος", "αντι", "αντα", "αντες", "αντων", "ασα", "ασης",
    "μενος", "μενη", "μενον", "μενου", "μενης", "μενους", "μενοις",
    "ομενος", "ομενη", "ομενον",
    "εις", "εντος", "εισα", "ειση", "εντα",
    "θεις", "θεντος", "θεισα",
    "ως", "οτος", "υια",
)

# Speech-introduction verbs: ἀπεκρίθη + εἶπεν pattern is NOT a gorgianic pair
# These are asyndetic hendiadys formulae in narration but the rule is to
# give speech-intro its OWN line (canon). So: line1 = speech-intro verb
# → filter out.
SPEECH_INTRO_STEMS = (
    "εἶπ", "λέγ", "ἔλεγ", "φη", "ἀπεκρίθ", "ἀποκρίθ", "ἀπεκρίν",
    "ἀπεκριν", "κράζ", "ἐκέλευσ", "παρεκάλ", "ἠρώτ", "ἐπηρώτ",
)

# Known near-synonym / binomial pair roots (partial match, Greek stems)
SEMANTIC_PAIRS = [
    # Near-synonyms
    {"γνόφ", "ζόφ"},       # darkness (Heb 12:18)
    {"κόπ", "μόχθ"},       # toil/labour (2 Cor 11:27)
    {"τολμη", "αὐθάδ"},    # boldness/arrogance (2 Pet 2:10)
    {"χαίρ", "εὐφραίν"},   # joy (various)
    {"θρῆν", "κλαί"},      # mourning/weeping (various)
    {"πένθ", "κλαυθμ"},    # grief/weeping
    {"ὀδύρ", "κλαί"},      # lament/weep
    {"ἁγί", "δίκαι"},      # holy/righteous (binomial)
    {"πιστ", "ἀγαθ"},      # faithful/good
    {"ταπειν", "πραΰ"},    # humble/gentle
    {"σοφ", "σύνεσ"},      # wisdom/understanding
    {"δύναμ", "ἰσχύ"},     # power/strength
    {"τιμ", "δόξ"},        # honour/glory
    {"εἰρήν", "χαρ"},      # peace/joy
    {"ἀγάπ", "χαρ"},       # love/joy
    {"ψαλμ", "ὕμν"},       # psalm/hymn
    {"ὕμν", "ᾠδ"},         # hymn/song
    {"ψαλμ", "ᾠδ"},        # psalm/song
    {"νηστεί", "προσευχ"},  # fasting/prayer
    {"ἐλπίδ", "ὑπομον"},   # hope/endurance
    {"πίστ", "ὑπομον"},    # faith/endurance
    {"θλῖψ", "στενοχωρ"},  # tribulation/anguish
    {"ὀργ", "θυμ"},        # wrath/anger
    {"κρίσ", "δικαιοσύν"}, # judgment/righteousness
]


def tokenize_greek(line: str) -> List[str]:
    """Return list of Greek word tokens, stripping punctuation."""
    # Strip verse references (e.g. "11:27" at start)
    line = re.sub(r'^\d+:\d+\s*', '', line.strip())
    # Split on whitespace, strip punctuation
    tokens = []
    for tok in line.split():
        tok = tok.strip('.,;:·—·\'\"''""«»()[]{}⌜⌝')
        tok = tok.strip()
        if tok:
            tokens.append(tok)
    return tokens


def is_verse_ref(line: str) -> bool:
    """Return True if line is a verse reference (e.g. '3:16')."""
    return bool(re.match(r'^\d+:\d+\s*$', line.strip()))


def starts_with_kai(line: str) -> bool:
    """Return True if line starts with καί or καὶ (with possible enclitic forms)."""
    tokens = tokenize_greek(line)
    if not tokens:
        return False
    return tokens[0] in ("καί", "καὶ", "Καί", "Καὶ")


def starts_with_discourse_marker(line: str) -> bool:
    """Return True if line starts with a discourse marker."""
    tokens = tokenize_greek(line)
    if not tokens:
        return False
    return tokens[0] in DISCOURSE_MARKERS


def starts_with_subordinator(line: str) -> bool:
    """Return True if line starts with a subordinating conjunction."""
    tokens = tokenize_greek(line)
    if not tokens:
        return False
    return tokens[0] in SUBORDINATORS


def get_last_token(line: str) -> Optional[str]:
    """Return the last token of a line."""
    tokens = tokenize_greek(line)
    return tokens[-1] if tokens else None


def guess_pos(token: str) -> str:
    """
    Rough POS guess: 'noun_adj', 'participle', 'verb', or 'other'.
    Greek heuristic based on endings. ~65% precision.
    """
    t = token.lower()
    # Strip augments / common prefixes for matching
    for end in PARTICIPLE_ENDINGS:
        if t.endswith(end):
            return 'participle'
    for end in NOUN_ADJ_ENDINGS:
        if t.endswith(end) and len(t) > 3:
            return 'noun_adj'
    return 'other'


def dominant_pos(tokens: List[str]) -> str:
    """Return the most common POS guess for a token list."""
    if not tokens:
        return 'other'
    counts = {'noun_adj': 0, 'participle': 0, 'verb': 0, 'other': 0}
    for t in tokens:
        counts[guess_pos(t)] += 1
    return max(counts, key=counts.get)


def forms_match_heuristic(tokens1: List[str], tokens2: List[str]) -> bool:
    """
    Heuristic: do the two lines share grammatical form?
    Returns True if dominant POS matches OR both very short (1-2 tokens, hard to classify).
    """
    if len(tokens1) <= 2 and len(tokens2) <= 2:
        # Very short — consider them form-compatible for the scanner;
        # adversarial audit will catch FPs
        return True
    pos1 = dominant_pos(tokens1)
    pos2 = dominant_pos(tokens2)
    if pos1 == pos2:
        return True
    # noun_adj and participle sometimes co-occur as bonded pairs
    if {pos1, pos2} <= {'noun_adj', 'participle'}:
        return True
    return False


def has_independent_predicate(tokens: List[str]) -> bool:
    """
    Return True if the line appears to contain an independent finite verb.
    Heuristic: look for augmented aorist or present-tense personal endings
    on tokens that are >= 4 chars and not clearly a noun/adjective.
    This is intentionally conservative — we prefer False negatives here
    (catch over-splits) and let adversarial audit catch FPs.
    """
    for tok in tokens:
        t = tok.lower()
        # Augment check: ε + consonant likely to be aorist
        # Very rough: if token ends in finite-ish ending AND is > 4 chars
        for end in ("εν", "σεν", "ηκεν", "ησεν", "ησαν", "ατο", "οντο",
                    "ετο", "ωκεν", "σωκεν"):
            if t.endswith(end) and len(t) > 4:
                return True
    return False


def check_semantic_pairing(tokens1: List[str], tokens2: List[str]) -> bool:
    """Return True if any token pair matches a known semantic pair."""
    stems1 = {t.lower()[:6] for t in tokens1}
    stems2 = {t.lower()[:6] for t in tokens2}
    for pair in SEMANTIC_PAIRS:
        p = list(pair)
        if (any(s.startswith(p[0]) for s in stems1) and
                any(s.startswith(p[1]) for s in stems2)):
            return True
        if (any(s.startswith(p[1]) for s in stems1) and
                any(s.startswith(p[0]) for s in stems2)):
            return True
    return False


def count_kai_in_window(lines: List[str], start: int, window: int = 4) -> int:
    """Count how many lines in [start+1 .. start+window] start with καί."""
    count = 0
    for i in range(start + 1, min(start + window, len(lines))):
        if lines[i].strip() and not is_verse_ref(lines[i]):
            if starts_with_kai(lines[i]):
                count += 1
    return count


def is_speech_intro_line(line: str) -> bool:
    """
    Return True if line looks like a speech-introduction line.
    Canon: speech-intro gets its own line; ἀπεκρίθη + καὶ εἶπεν is a
    canonical split that should NOT be flagged as gorgianic-pair drift.
    """
    tokens = tokenize_greek(line)
    for tok in tokens:
        t = tok.lower()
        for stem in SPEECH_INTRO_STEMS:
            if t.startswith(stem):
                return True
    return False


def is_in_series_context(lines: List[str], idx1: int, idx2: int) -> bool:
    """
    Return True if lines[idx1]/idx2 appear to be part of an N≥3 series.
    Checks whether a third consecutive line (after idx2) also starts with καί
    or continues the same structural pattern.

    Also checks for the 'imperative triad' pattern (Matt 7:7 type): if the
    line AFTER idx2 is a new short line (not καί) that mirrors line1 form,
    and the line after THAT starts with καί — the whole block is a triplet
    of (imperative + καί result) × 3, not a gorgianic pair.
    """
    # Look forward: is there a third non-blank line starting with καί?
    j = idx2 + 1
    while j < len(lines):
        stripped = lines[j].strip()
        if not stripped:
            break
        if is_verse_ref(stripped):
            j += 1
            continue
        if starts_with_kai(lines[j]):
            return True
        # Non-blank, non-kai line — check if it's the next imperative in a triad
        # i.e. another short line followed by a καί line
        j2 = j + 1
        while j2 < len(lines):
            s2 = lines[j2].strip()
            if not s2:
                break
            if is_verse_ref(s2):
                j2 += 1
                continue
            if starts_with_kai(lines[j2]):
                # Pattern: L1 + καί L2 / L3 + καί L4 → triplet, flag as series
                return True
            break
        break
    # Look backward: was there a line before idx1 that starts with καί
    # (meaning idx1 itself is already part of a series)?
    k = idx1 - 1
    while k >= 0:
        stripped = lines[k].strip()
        if not stripped:
            break
        if is_verse_ref(stripped):
            k -= 1
            continue
        if starts_with_kai(lines[k]):
            return True
        break
    return False


def triage(
    tokens1: List[str],
    tokens2: List[str],
    line1: str,
    line2: str,
    in_series: bool,
    semantic_match: bool,
    forms_match: bool,
    has_predicate_l1: bool,
    has_discourse_l1: bool,
    is_speech_intro_l1: bool = False,
) -> str:
    """
    Assign CONFIRMED_DRIFT / AMBIGUOUS / LIKELY_FP verdict.

    Strict hierarchy — LIKELY_FP first, then CONFIRMED_DRIFT, then AMBIGUOUS.
    """
    # Hard negatives → LIKELY_FP
    if in_series:
        return "LIKELY_FP"       # Part of N≥3 series
    if is_speech_intro_l1:
        return "LIKELY_FP"       # Speech-intro line (ἀπεκρίθη + εἶπεν pattern)
    if has_predicate_l1:
        return "LIKELY_FP"       # Line 1 has independent finite verb
    if has_discourse_l1:
        return "LIKELY_FP"       # Line 1 starts with discourse/adversative marker
    if not forms_match:
        return "LIKELY_FP"       # Different grammatical classes

    # Strong positives → CONFIRMED_DRIFT
    if semantic_match and len(tokens1) <= 3 and len(tokens2) <= 3:
        return "CONFIRMED_DRIFT"
    if len(tokens1) == 1 and len(tokens2) <= 2:
        return "CONFIRMED_DRIFT"
    if len(tokens2) == 1 and len(tokens1) <= 2:
        # Bare single-word καί + word — high confidence hendiadys
        return "CONFIRMED_DRIFT"
    if semantic_match and len(tokens1) <= 4 and len(tokens2) <= 4:
        return "CONFIRMED_DRIFT"

    # Medium — AMBIGUOUS
    return "AMBIGUOUS"


def scan_file(filepath: Path) -> List[Dict]:
    """Scan one v4-editorial file and return list of candidate dicts."""
    candidates = []
    try:
        text = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}", file=sys.stderr)
        return []

    lines = text.splitlines()
    book_chapter = filepath.stem  # e.g. "2cor-11"

    # Determine book from parent dir name
    book = filepath.parent.name  # e.g. "08-2cor"

    # Resolve current verse reference
    current_verse = "?"
    i = 0
    while i < len(lines) - 1:
        raw = lines[i]
        stripped = raw.strip()

        # Track verse reference
        if is_verse_ref(stripped):
            current_verse = stripped
            i += 1
            continue

        # Skip blank lines
        if not stripped:
            i += 1
            continue

        # Line 1 candidate
        tokens1 = tokenize_greek(stripped)
        if not (MIN_TOKENS <= len(tokens1) <= MAX_TOKENS):
            i += 1
            continue

        # Skip if line 1 starts with καί (would make it a series continuation,
        # not the first of a pair — we'd catch it from the prior line)
        if starts_with_kai(stripped):
            i += 1
            continue

        # Skip if line 1 starts with subordinator (not a bonded pair opener)
        if starts_with_subordinator(stripped):
            i += 1
            continue

        # Find line 2: next non-blank, non-verse-ref line
        j = i + 1
        while j < len(lines):
            s2 = lines[j].strip()
            if is_verse_ref(s2):
                j += 1
                continue
            if s2:
                break
            # blank line — pair broken, stop
            j = -1
            break
        else:
            j = -1

        if j < 0 or j >= len(lines):
            i += 1
            continue

        line2_raw = lines[j].strip()
        tokens2 = tokenize_greek(line2_raw)

        # Line 2 must start with καί
        if not starts_with_kai(line2_raw):
            i += 1
            continue

        # Line 2 token count (strip the leading καί for length check)
        tokens2_body = tokens2[1:] if tokens2 else []  # exclude the καί itself

        # Both parts (line1 content + line2 body) should be short
        # Line 2 body (excluding καί) ≤ MAX_TOKENS
        if len(tokens2) > MAX_TOKENS + 1:  # +1 for καί itself
            i += 1
            continue

        if len(tokens2_body) == 0:
            # καί dangling alone — not a gorgianic pair, a conjunction orphan
            i += 1
            continue

        # Check series context (is there a 3rd consecutive καί line?)
        in_series = is_in_series_context(lines, i, j)

        # Discourse/adversative marker on line 1?
        has_discourse_l1 = starts_with_discourse_marker(stripped)

        # Speech-introduction on line 1? (ἀπεκρίθη + καὶ εἶπεν pattern)
        is_speech_intro_l1 = is_speech_intro_line(stripped)

        # Independent predicate on line 1?
        has_predicate_l1 = has_independent_predicate(tokens1)

        # Form matching (line1 vs line2 body — ignore καί)
        forms_match = forms_match_heuristic(tokens1, tokens2_body)

        # Semantic pairing
        semantic_match = check_semantic_pairing(tokens1, tokens2_body)

        verdict = triage(
            tokens1=tokens1,
            tokens2=tokens2_body,
            line1=stripped,
            line2=line2_raw,
            in_series=in_series,
            semantic_match=semantic_match,
            forms_match=forms_match,
            has_predicate_l1=has_predicate_l1,
            has_discourse_l1=has_discourse_l1,
            is_speech_intro_l1=is_speech_intro_l1,
        )

        # Build context: 2 lines before + the pair + 2 lines after
        context_before = []
        cb = i - 1
        count = 0
        while cb >= 0 and count < 2:
            s = lines[cb].strip()
            if s:
                context_before.insert(0, s)
                count += 1
            cb -= 1

        context_after = []
        ca = j + 1
        count = 0
        while ca < len(lines) and count < 2:
            s = lines[ca].strip()
            if s:
                context_after.append(s)
                count += 1
            ca += 1

        candidates.append({
            "file": str(filepath.relative_to(REPO_ROOT)),
            "book": book,
            "verse": current_verse,
            "line1": stripped,
            "line2": line2_raw,
            "tokens1": tokens1,
            "tokens2": tokens2,
            "in_series": in_series,
            "semantic_match": semantic_match,
            "forms_match": forms_match,
            "has_predicate_l1": has_predicate_l1,
            "is_speech_intro_l1": is_speech_intro_l1,
            "verdict": verdict,
            "context_before": context_before,
            "context_after": context_after,
            "line1_no": i + 1,
            "line2_no": j + 1,
        })

        i += 1
        continue

    return candidates


def scan_corpus() -> List[Dict]:
    """Walk all v4-editorial files and collect candidates."""
    all_candidates = []
    txt_files = sorted(V4_DIR.glob("**/*.txt"))
    for fp in txt_files:
        candidates = scan_file(fp)
        all_candidates.extend(candidates)
    return all_candidates


def write_report(candidates: List[Dict]) -> None:
    """Write the findings report to OUTPUT_FILE."""
    confirmed = [c for c in candidates if c["verdict"] == "CONFIRMED_DRIFT"]
    ambiguous = [c for c in candidates if c["verdict"] == "AMBIGUOUS"]
    fp_cases = [c for c in candidates if c["verdict"] == "LIKELY_FP"]

    # Sort confirmed by token brevity (shortest pairs first = highest confidence)
    confirmed_sorted = sorted(confirmed, key=lambda c: len(c["tokens1"]) + len(c["tokens2"]))

    lines_out = []
    lines_out.append("# Gorgianic-Pair Scanner — Findings")
    lines_out.append("")
    lines_out.append("**Scanner:** `scripts/scan_gorgianic_pairs.py`")
    lines_out.append("**Run date:** 2026-04-17")
    lines_out.append("**Rule class:** M1 — N=2 gorgianic pairs (hendiadys) currently over-split")
    lines_out.append("")
    lines_out.append("---")
    lines_out.append("")
    lines_out.append("## Summary")
    lines_out.append("")
    lines_out.append(f"| Verdict | Count |")
    lines_out.append(f"|---------|-------|")
    lines_out.append(f"| CONFIRMED_DRIFT | {len(confirmed)} |")
    lines_out.append(f"| AMBIGUOUS | {len(ambiguous)} |")
    lines_out.append(f"| LIKELY_FP | {len(fp_cases)} |")
    lines_out.append(f"| **Total candidates** | **{len(candidates)}** |")
    lines_out.append("")

    # Book distribution for confirmed
    book_counts: Dict[str, int] = {}
    for c in confirmed:
        book_counts[c["book"]] = book_counts.get(c["book"], 0) + 1
    if book_counts:
        lines_out.append("### CONFIRMED_DRIFT by book")
        lines_out.append("")
        lines_out.append("| Book | Count |")
        lines_out.append("|------|-------|")
        for book, cnt in sorted(book_counts.items(), key=lambda x: -x[1]):
            lines_out.append(f"| {book} | {cnt} |")
        lines_out.append("")

    lines_out.append("---")
    lines_out.append("")
    lines_out.append("## CONFIRMED_DRIFT Cases")
    lines_out.append("")
    lines_out.append("Sorted by pair brevity (shortest = highest-confidence hendiadys).")
    lines_out.append("")

    for idx, c in enumerate(confirmed_sorted, 1):
        lines_out.append(f"### CD-{idx:03d} — {c['file']} | {c['verse']}")
        lines_out.append("")
        lines_out.append(f"**Verdict:** CONFIRMED_DRIFT")
        lines_out.append(f"**Tokens:** line 1 = {len(c['tokens1'])}, line 2 = {len(c['tokens2'])}")
        lines_out.append(f"**Semantic match:** {'yes' if c['semantic_match'] else 'no'}")
        lines_out.append(f"**In series:** {'yes' if c['in_series'] else 'no'}")
        lines_out.append("")
        lines_out.append("**Current structure:**")
        lines_out.append("```")
        for ctx in c["context_before"]:
            lines_out.append(f"  {ctx}")
        lines_out.append(f"→ {c['line1']}")
        lines_out.append(f"→ {c['line2']}")
        for ctx in c["context_after"]:
            lines_out.append(f"  {ctx}")
        lines_out.append("```")
        lines_out.append("")
        # Recommend merge
        merged = c["line1"] + " " + c["line2"]
        lines_out.append(f"**Recommended fix:** merge onto one line")
        lines_out.append(f"`{merged}`")
        lines_out.append("")

    lines_out.append("---")
    lines_out.append("")
    lines_out.append("## AMBIGUOUS Cases")
    lines_out.append("")
    lines_out.append("These candidates match the structural pattern but have ambiguous signals.")
    lines_out.append("Human judgment required before any fix is applied.")
    lines_out.append("")

    for idx, c in enumerate(ambiguous, 1):
        lines_out.append(f"### AMB-{idx:03d} — {c['file']} | {c['verse']}")
        lines_out.append("")
        lines_out.append(f"**Verdict:** AMBIGUOUS")
        lines_out.append(f"**Tokens:** line 1 = {len(c['tokens1'])}, line 2 = {len(c['tokens2'])}")
        lines_out.append(f"**Semantic match:** {'yes' if c['semantic_match'] else 'no'}")
        lines_out.append(f"**In series:** {'yes' if c['in_series'] else 'no'}")
        lines_out.append("")
        lines_out.append("**Current structure:**")
        lines_out.append("```")
        for ctx in c["context_before"]:
            lines_out.append(f"  {ctx}")
        lines_out.append(f"→ {c['line1']}")
        lines_out.append(f"→ {c['line2']}")
        for ctx in c["context_after"]:
            lines_out.append(f"  {ctx}")
        lines_out.append("```")
        lines_out.append("")

    lines_out.append("---")
    lines_out.append("")
    lines_out.append("## LIKELY_FP Cases (sample — first 30)")
    lines_out.append("")
    lines_out.append("Flagged by scanner but rejected on structural grounds.")
    lines_out.append("")

    for idx, c in enumerate(fp_cases[:30], 1):
        reason = []
        if c["in_series"]:
            reason.append("part of N≥3 series")
        if c.get("is_speech_intro_l1"):
            reason.append("speech-intro formula (ἀπεκρίθη+εἶπεν type)")
        if c["has_predicate_l1"]:
            reason.append("line1 has finite verb")
        if not c["forms_match"]:
            reason.append("grammatical forms differ")
        reason_str = "; ".join(reason) if reason else "structural context"
        lines_out.append(f"### FP-{idx:03d} — {c['file']} | {c['verse']} — *{reason_str}*")
        lines_out.append("")
        lines_out.append("```")
        lines_out.append(f"→ {c['line1']}")
        lines_out.append(f"→ {c['line2']}")
        lines_out.append("```")
        lines_out.append("")

    if len(fp_cases) > 30:
        lines_out.append(f"*... and {len(fp_cases) - 30} more LIKELY_FP cases omitted.*")
        lines_out.append("")

    lines_out.append("---")
    lines_out.append("")
    lines_out.append("## Scanner Heuristics Notes")
    lines_out.append("")
    lines_out.append("- Line length threshold: ≤5 tokens per line (both lines)")
    lines_out.append("- Series detection: checks for 3rd consecutive καί line forward/backward + imperative-triad pattern (Matt 7:7 type)")
    lines_out.append("- Speech-intro filter: ἀπεκρίθη/εἶπεν/λέγω/etc. on line 1 → LIKELY_FP (canon: speech-intro gets its own line)")
    lines_out.append("- POS matching: heuristic ending-based (~65% precision) — form mismatch is a hard FP signal but form match is weak positive only")
    lines_out.append("- Semantic pair list: 20 known near-synonym stems hardcoded; elevates short pairs to CONFIRMED_DRIFT")
    lines_out.append("- Finite-verb detection on line 1: conservative (prefers false negatives to avoid over-filtering genuine hendiadys)")
    lines_out.append("- Discourse-marker opener (ἀλλά, γάρ, δέ, μέν, etc.) on line 1 → LIKELY_FP")
    lines_out.append("- Does NOT detect asyndetic gorgianic pairs (no καί on line 2) — those require semantic analysis beyond this scanner's scope")
    lines_out.append("- Known limitation: AMBIGUOUS count inflated by verb-chain narrative sequences (e.g. healing/action sequences) where both lines are short verbs")
    lines_out.append("")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines_out), encoding='utf-8')


def main():
    print("Scanning corpus for gorgianic pair candidates (M1 merge doctrine)...")
    print(f"  Source: {V4_DIR}")
    print(f"  Output: {OUTPUT_FILE}")
    print()

    candidates = scan_corpus()

    confirmed = [c for c in candidates if c["verdict"] == "CONFIRMED_DRIFT"]
    ambiguous = [c for c in candidates if c["verdict"] == "AMBIGUOUS"]
    fp_cases = [c for c in candidates if c["verdict"] == "LIKELY_FP"]

    print(f"Scan complete.")
    print(f"  Total candidates:  {len(candidates)}")
    print(f"  CONFIRMED_DRIFT:   {len(confirmed)}")
    print(f"  AMBIGUOUS:         {len(ambiguous)}")
    print(f"  LIKELY_FP:         {len(fp_cases)}")
    print()

    if confirmed:
        # Sort by brevity for top-10 display
        top = sorted(confirmed, key=lambda c: len(c["tokens1"]) + len(c["tokens2"]))[:15]
        print("Top CONFIRMED_DRIFT cases (shortest pairs = highest confidence):")
        for c in top:
            sem = "sem+" if c["semantic_match"] else "     "
            print(f"  [{sem}] {c['file']} | {c['verse']}")
            print(f"         L1: {c['line1']}")
            print(f"         L2: {c['line2']}")
            print()

    write_report(candidates)
    print(f"Full report written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
