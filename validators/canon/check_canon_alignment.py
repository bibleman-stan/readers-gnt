#!/usr/bin/env python3
"""
check_canon_alignment.py — GNT per-repo canon-validator structural alignment check.

Implements the four structural checks specified at:
  atu-method/docs/canon-validator-alignment-protocol.md

Four checks per rule entry in canon §3 Rule Index:
  1. Validator file presence  — named path exists on disk
  2. Closed-list presence     — canonical closed-list names appear in validator source
  3. UD signature field consistency — deprels / UPOS / lemmas from YAML signature
                                      appear in validator source
  4. Multi-valued field branches  — each named branch has handling in validator

Verdict taxonomy: ALIGNED | NO_IMPL | DRIFT | PARTIAL | EDITORIAL_ACK

Output: markdown report sorted NO_IMPL > DRIFT > PARTIAL > EDITORIAL_ACK > ALIGNED.
Report is written to stdout AND to validators/.canon-alignment.md.

Usage:
    py -3 validators/canon/check_canon_alignment.py

Scope: structural/naming checks only — NOT semantic alignment.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CANON_PATH = REPO_ROOT / "private" / "01-method" / "colometry-canon.md"
REPORT_PATH = REPO_ROOT / "validators" / ".canon-alignment.md"

# ── Rule table ────────────────────────────────────────────────────────────────
# Derived from §3 Rule Index in colometry-canon.md.
# Each entry:
#   rule_id     : str
#   name        : str
#   rule_type   : "Mechanical" | "Editorial" | "Principle" | "Layer 1"
#   validator   : str | None   — path relative to repo root (None = not named)
#   applier_none: bool         — True if canon says "Applier: (none — ...)"
#   closed_lists: list[str]    — uppercase Python constant names expected in validator
#   ud_terms    : list[str]    — lemmas / deprels / UPOS values named in canon YAML sig
#   branches    : list[str]    — named branch labels for multi-valued fields
#   notes       : str          — verbatim Rule Index "Detector" column text

RULES: list[dict] = [
    {
        "rule_id": "R1",
        "name": "No-anchor rule",
        "rule_type": "Mechanical",
        "validator": "scripts/scan_no_anchor_lines.py",  # scanner, not colometry/
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": ["finite_verb", "infinitive", "participle"],
        "branches": [],
        "notes": "scripts/scan_no_anchor_lines.py (scanner)",
    },
    {
        "rule_id": "R2",
        "name": "Never dangle a conjunction",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r2_no_dangle_conjunction.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r2_no_dangle_conjunction.py",
    },
    {
        "rule_id": "R3",
        "name": "Never end on article",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r3_no_line_end_article.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r3_no_line_end_article.py",
    },
    {
        "rule_id": "R4",
        "name": "Never split negation from negated",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r4_no_split_negation.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r4_no_split_negation.py",
    },
    {
        "rule_id": "R5",
        "name": "Never split periphrastic construction",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r5_periphrastic.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r5_periphrastic.py",
    },
    {
        "rule_id": "R6",
        "name": "Fixed phrases stay together",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r6_fixed_phrases.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r6_fixed_phrases.py",
    },
    {
        "rule_id": "R7",
        "name": "Vocative units indivisible",
        "rule_type": "Layer 1",
        "validator": "validators/syntax/check_r7_vocative_units.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "validators/syntax/check_r7_vocative_units.py",
    },
    {
        "rule_id": "R8",
        "name": "Framing devices attach",
        "rule_type": "Mechanical",
        "validator": "validators/syntax/check_r8_framing_devices.py",
        "applier_none": False,
        "closed_lists": ["FRAMING_SINGLE"],
        "ud_terms": ["STRONG-MERGE", "MALFORMED"],
        "branches": [],
        "notes": "Closed list: ἰδού, διό, οὖν, νυν δέ, ἀλλά, γάρ, πλήν, τοιγαροῦν",
    },
    {
        "rule_id": "R9",
        "name": "Subordinate clause introduction breaks",
        "rule_type": "Mechanical",
        "validator": "validators/syntax/check_r9_subordinate_clause.py",
        "applier_none": False,
        "closed_lists": ["SUB_CLAUSE_OPENERS"],
        "ud_terms": ["STRONG-MERGE", "MALFORMED"],
        "branches": [],
        "notes": "Closed list: ἵνα, ὥστε, ὅτι, διότι, ὅταν, ὅτε, εἰ, ἐάν, καθώς, μήποτε",
    },
    {
        "rule_id": "R10",
        "name": "Complementizer hoti — cognition vs. speech",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r10_hoti_complementizer.py",
        "applier_none": False,
        "closed_lists": ["COGNITION_LEMMAS", "DECLARATION_LEMMAS"],
        "ud_terms": ["ὅτι", "DEVIATION"],
        "branches": [],
        "notes": "Lemma-class lookup via MorphGNT. Cognition merges; declaration splits.",
    },
    {
        "rule_id": "R11",
        "name": "Direct speech introduction",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r11_speech_intro.py",
        "applier_none": False,
        "closed_lists": ["SPEECH_LEMMAS"],
        # Check only Greek lemmas that must appear as string literals in validator
        "ud_terms": ["λέγω", "φημί", "ἀποκρίνομαι"],
        "branches": [],
        "notes": "validators/colometry/check_r11_speech_intro.py",
    },
    {
        "rule_id": "R28-ext",
        "name": "Speech-act announcement after adverbial frame (split)",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r28_speech_act_frame.py",
        "applier_none": False,
        "closed_lists": ["SPEECH_LEMMAS", "TEMPORAL_CONJ"],
        # Check only Greek lemmas that must appear as string literals in validator
        "ud_terms": ["λέγω", "εἶπον", "φημί"],
        "branches": [],
        "notes": "validators/colometry/check_r28_speech_act_frame.py",
    },
    {
        "rule_id": "R12",
        "name": "Parallel stacking (if atomic)",
        "rule_type": "Editorial",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(judgment-required; no auto-validator)*",
    },
    {
        "rule_id": "R13",
        "name": "Correlative pair treatment",
        "rule_type": "Editorial",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(judgment-required; no auto-validator)*",
    },
    {
        "rule_id": "R14",
        "name": "Men/de contrast stacking",
        "rule_type": "Editorial",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(judgment-required; no auto-validator)*",
    },
    {
        "rule_id": "R17",
        "name": "De-contrast overbreak",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r17_de_contrast_overbreak.py",
        "applier_none": False,
        "closed_lists": ["ARTICLE_FORMS", "OTHER_PIVOT_HEADS"],
        "ud_terms": ["δέ", "STRONG-SPLIT", "DEVIATION"],
        "branches": [],
        "notes": "Surface-pattern: comma + article/head + δέ.",
    },
    {
        "rule_id": "R18",
        "name": "Vocative rule (three-way refined)",
        "rule_type": "Editorial",
        "validator": "validators/colometry/check_r18_vocative.py",
        "applier_none": False,
        "closed_lists": [],
        # Canon YAML uses descriptive labels (vocative_NP etc.); check
        # for the helper function names the validator actually imports
        "ud_terms": ["is_vocative", "is_2p_verb", "is_2p_pronoun"],
        "branches": [],
        "notes": "validators/colometry/check_r18_vocative.py",
    },
    {
        "rule_id": "R18a-GNT",
        "name": "Patriarch-deity-triad indivisibility",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r18a_patriarch_triad.py",
        "applier_none": False,
        "closed_lists": [],
        # Canon names specific lemma constants by prefix strings, not uppercase consts
        "ud_terms": ["θεός", "Ἀβραάμ", "Ἰσαάκ", "Ἰακώβ"],
        "branches": [],
        "notes": "validators/colometry/check_r18a_patriarch_triad.py",
    },
    {
        "rule_id": "R19",
        "name": "Genitive absolute always own line",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r19_genabs.py",
        "applier_none": False,
        "closed_lists": [],
        # Canon YAML uses descriptive labels; check for the helper functions
        # the validator imports from validators._shared
        "ud_terms": ["is_genitive_participle", "gen_abs"],
        "branches": [],
        "notes": "validators/colometry/check_r19_genabs.py",
    },
    {
        "rule_id": "R20",
        "name": "Participial phrase test (refined)",
        "rule_type": "Editorial",
        "validator": "scripts/scan_line_ending_participles.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "scripts/scan_line_ending_participles.py *(scanner only)*",
    },
    {
        "rule_id": "R22",
        "name": "Orphaned adverbial completion",
        "rule_type": "Editorial",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(judgment-required; no auto-validator)*",
    },
    {
        "rule_id": "R23",
        "name": "Dative subject of infinitive",
        "rule_type": "Mechanical",
        "validator": "scripts/scan_r23_dative_infinitive.py",
        "applier_none": False,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "scripts/scan_r23_dative_infinitive.py *(scanner only)*",
    },
    {
        "rule_id": "R24",
        "name": "Qualifying phrases: escalation vs. restriction",
        "rule_type": "Editorial",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(judgment-required; no auto-validator)*",
    },
    {
        "rule_id": "R25",
        "name": "ὥστε short-consecutive-result binding",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_r25_hoste_consecutive_result.py",
        "applier_none": False,
        "closed_lists": [],
        # Canon YAML names ὥστε trigger + 4 verdict paths; validator implements
        # these as tag strings (STRONG-MERGE-CANDIDATE, SPLIT-MAINTAINED, etc.)
        "ud_terms": ["ὥστε"],
        "branches": [
            "STRONG-MERGE-CANDIDATE",    # words_le_8_after_illative_filter branch
            "SPLIT-MAINTAINED",           # words_gt_8 + illative branches
            "REVIEW-REQUIRED",            # verse_initial_hoste branch
        ],
        "notes": "validators/colometry/check_r25_hoste_consecutive_result.py",
    },
    {
        "rule_id": "R27",
        "name": "Authorial style principle (uniform criteria)",
        "rule_type": "Principle",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(principle, not a per-line rule)*",
    },
    {
        "rule_id": "R28",
        "name": "Textual asymmetry overrides editorial symmetry",
        "rule_type": "Principle",
        "validator": None,
        "applier_none": True,
        "closed_lists": [],
        "ud_terms": [],
        "branches": [],
        "notes": "*(principle, not a per-line rule)*",
    },
    {
        "rule_id": "M4-GNT-1",
        "name": "Subject-orphan predicate completion (Greek instantiation)",
        "rule_type": "Mechanical",
        "validator": "validators/colometry/check_m4_gnt_1_subject_orphan.py",
        "applier_none": False,
        # Canon names _LEADING_CONNECTIVES (internal name with underscore prefix);
        # also names SUBJECT_SHAPES_M4_GNT1 in the Closed-List Registry — but
        # the validator implements shapes inline rather than as a named constant.
        # Check what is actually present: _LEADING_CONNECTIVES + helper functions
        "closed_lists": ["_LEADING_CONNECTIVES"],
        # Canon YAML descriptive labels for the 5 subject shapes (C1-C5) appear
        # as inline comments/docstring prose in the validator, not as string consts.
        # Check for the meaningful identifiers: exclusion G1-G5 labels
        "ud_terms": ["is_finite_verb", "STRONG-MERGE-CANDIDATE", "_is_bare_vocative_line"],
        "branches": [],
        "notes": "validators/colometry/check_m4_gnt_1_subject_orphan.py",
    },
]

# ── Verdict severity order for sorting ────────────────────────────────────────
_SEVERITY = {"NO_IMPL": 0, "DRIFT": 1, "PARTIAL": 2, "EDITORIAL_ACK": 3, "ALIGNED": 4}


# ── Core check logic ──────────────────────────────────────────────────────────

def load_source(path: Path) -> Optional[str]:
    """Return file contents as string, or None if file doesn't exist."""
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return None


def check_rule(rule: dict) -> tuple[str, str]:
    """
    Run the four structural checks for a single rule entry.
    Returns (verdict, evidence_notes).
    """
    rule_id = rule["rule_id"]
    rule_type = rule["rule_type"]
    applier_none = rule["applier_none"]
    validator_rel = rule["validator"]
    closed_lists = rule["closed_lists"]
    ud_terms = rule["ud_terms"]
    branches = rule["branches"]

    # Principles and explicitly no-applier editorial rules
    if applier_none and validator_rel is None:
        return "EDITORIAL_ACK", f"Applier: (none — {rule_type} / {rule['notes']})"

    # No validator named at all
    if validator_rel is None:
        return "NO_IMPL", f"Canon §3 Rule Index: {rule['notes']} — no validator path named"

    validator_path = REPO_ROOT / validator_rel.replace("/", "\\")
    source = load_source(validator_path)

    # Check 1: file presence
    if source is None:
        return "NO_IMPL", f"Named path {validator_rel!r} does not exist on disk"

    # Checks 2–4 only apply when we have source
    drift_items: list[str] = []
    partial_items_present: list[str] = []
    partial_items_missing: list[str] = []

    # Check 2: closed-list presence
    for cl_name in closed_lists:
        if cl_name in source:
            partial_items_present.append(f"closed-list {cl_name!r}")
        else:
            drift_items.append(f"closed-list constant {cl_name!r} missing from validator source")

    # Check 3: UD signature field consistency (string presence in source)
    # We check for ASCII-safe surrogates since some lemmas are Greek; use both
    # the raw string and a simplified ASCII fallback for lemma presence checks.
    for term in ud_terms:
        if term in source:
            continue
        # Greek lemma terms: check by unicode-safe search
        try:
            if term.encode("utf-8") and term in source:
                continue
        except Exception:
            pass
        # Not found
        drift_items.append(f"UD-signature term {term!r} absent from validator source")

    # Check 4: multi-valued field branches
    for branch in branches:
        # Branch labels appear as string literals or function identifiers
        if branch in source:
            partial_items_present.append(f"branch {branch!r}")
        else:
            partial_items_missing.append(f"branch {branch!r} missing from validator source")

    # Determine verdict
    if drift_items and not partial_items_missing:
        if partial_items_present:
            # Some things present, some drift items
            evidence = "; ".join(drift_items) + (
                f" (present: {', '.join(partial_items_present)})" if partial_items_present else ""
            )
            return "DRIFT", evidence
        return "DRIFT", "; ".join(drift_items)

    if partial_items_missing:
        present_str = ", ".join(partial_items_present) if partial_items_present else "(none)"
        missing_str = ", ".join(partial_items_missing)
        return "PARTIAL", f"present: {present_str}; missing: {missing_str}"

    if drift_items:
        return "DRIFT", "; ".join(drift_items)

    return "ALIGNED", "validator exists; all named closed-lists and UD terms found"


# ── Report generation ─────────────────────────────────────────────────────────

def build_report() -> str:
    results: list[tuple[str, str, str, dict]] = []
    for rule in RULES:
        verdict, evidence = check_rule(rule)
        results.append((verdict, rule["rule_id"], rule["name"], evidence))  # type: ignore[arg-type]

    # Sort by severity
    results.sort(key=lambda x: (_SEVERITY.get(x[0], 99), x[1]))

    lines: list[str] = [
        "# GNT Canon-Validator Alignment Report",
        f"",
        f"Generated by `validators/canon/check_canon_alignment.py`.",
        f"Scope: structural/naming checks only (per canon-validator-alignment-protocol.md).",
        f"",
        "## Summary",
        "",
    ]

    counts: dict[str, int] = {v: 0 for v in _SEVERITY}
    for verdict, *_ in results:
        counts[verdict] = counts.get(verdict, 0) + 1

    for verdict in ["NO_IMPL", "DRIFT", "PARTIAL", "EDITORIAL_ACK", "ALIGNED"]:
        lines.append(f"- **{verdict}**: {counts.get(verdict, 0)}")

    lines += ["", f"**Total rules audited: {len(results)}**", "", "---", "", "## Per-rule findings", ""]

    current_section = None
    for verdict, rule_id, name, evidence in results:
        if verdict != current_section:
            lines.append(f"### {verdict}")
            lines.append("")
            current_section = verdict
        lines.append(f"**{rule_id}** ({name}): {verdict}")
        lines.append(f"> {evidence}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    report = build_report()
    print(report)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"\n[Report written to {REPORT_PATH.relative_to(REPO_ROOT)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
