#!/usr/bin/env python3
"""gnt-equational-cola Round-4 prototype.

Round-3 used cltype in {Verbless,VerbElided,Minor} (precision=0.8, recall=1.0).
Round-4 drops Minor (verified=0 in substrate) and adds rule-role filter
requiring both 'S' and 'P' tokens in rule attribute to exclude single-role
fragments (P2CL, S2CL, O2CL, ADV2CL, ADV-S, S-ADV, ADV-ADV, ...).
"""
from __future__ import annotations
import os, re, sys
import xml.etree.ElementTree as ET
from glob import glob
from typing import Dict, List, Optional, Sequence, Tuple

MACULA_DIR = "C:/Users/bibleman/repos/readers-gnt/research/macula-greek/SBLGNT/lowfat/"
EQUATIONAL_CLTYPES = frozenset({"Verbless", "VerbElided"})
RULE_TOK_RE = re.compile(r"[A-Z0-9]+")


class EquationalLookup:
    def __init__(self) -> None:
        self._chain: Dict[str, List[Tuple[Optional[str], Optional[str], Optional[str]]]] = {}

    @classmethod
    def from_macula_dir(cls, macula_dir: str) -> "EquationalLookup":
        self = cls()
        files = sorted(f for f in glob(os.path.join(macula_dir, "*.xml"))
                       if os.path.basename(f)[0:2].isdigit())
        if not files:
            raise FileNotFoundError(f"No lowfat XML at {macula_dir}")
        for fp in files:
            self._index_file(fp)
        return self

    def _index_file(self, path: str) -> None:
        self._walk(ET.parse(path).getroot(), [])

    def _walk(self, node, clause_stack):
        if node.tag == "wg" and node.get("class") == "cl":
            clause_stack = clause_stack + [(node.get("cltype"), node.get("rule"), node.get("role"))]
        ref = node.get("ref")
        if ref:
            self._chain[ref] = list(reversed(clause_stack))
        for child in node:
            self._walk(child, clause_stack)

    def innermost_clause(self, ref: str):
        chain = self._chain.get(ref)
        return chain[0] if chain else None

    def covering_clause(self, refs: Sequence[str]):
        chains = [self._chain.get(r) for r in refs]
        if not chains or any(c is None for c in chains):
            return None
        as_sets = [set(map(tuple, c)) for c in chains]
        common = as_sets[0]
        for s in as_sets[1:]:
            common &= s
        if not common:
            return None
        for clause in chains[0]:
            if tuple(clause) in common:
                return clause
        return None


def _rule_has_S_and_P(rule: Optional[str]) -> bool:
    if not rule:
        return False
    toks = set(RULE_TOK_RE.findall(rule))
    return "S" in toks and "P" in toks


def is_equational_cola(verse_ref: str, cola_tokens: Sequence[str], lookup: EquationalLookup) -> bool:
    if not cola_tokens:
        return False
    clause = lookup.covering_clause(cola_tokens)
    if clause is None:
        return False
    cltype, rule, _role = clause
    if cltype not in EQUATIONAL_CLTYPES:
        return False
    return _rule_has_S_and_P(rule)


TRUTH_SET = [
    {"id": "ROM_1_15_A", "verse_ref": "ROM 1:15",
     "cola_refs": [f"ROM 1:15!{i}" for i in range(1, 9)],
     "expected_is_equational_cola": True,
     "note": "ADV-S-P Verbless predication"},
    {"id": "ROM_8_10_A", "verse_ref": "ROM 8:10",
     "cola_refs": [f"ROM 8:10!{i}" for i in range(1, 6)],
     "expected_is_equational_cola": True,
     "note": "S-P-ADV Verbless (round-2 anchor)"},
    {"id": "JHN_1_1_C", "verse_ref": "JHN 1:1",
     "cola_refs": ["JHN 1:1!9", "JHN 1:1!10", "JHN 1:1!11", "JHN 1:1!12"],
     "expected_is_equational_cola": False,
     "note": "overt copula clause - outside Verbless/VerbElided scope"},
    {"id": "ROM_FRAGMENT_P2CL", "verse_ref": "ROM 9:5",
     "cola_refs": ["ROM 9:5!13", "ROM 9:5!14", "ROM 9:5!15"],
     "expected_is_equational_cola": False,
     "note": "Round-3 FP: Verbless P2CL fragment - Round-4 rule-filter excludes"},
    {"id": "MAT_5_3_A", "verse_ref": "MAT 5:3",
     "cola_refs": [f"MAT 5:3!{i}" for i in range(1, 6)],
     "expected_is_equational_cola": True,
     "note": "Beatitude verbless predication P-S"},
]


def run_self_test() -> int:
    if not os.path.isdir(MACULA_DIR):
        print(f"SUBSTRATE MISSING: {MACULA_DIR}", file=sys.stderr)
        return 2
    print(f"Loading Macula lowfat from {MACULA_DIR} ...")
    lookup = EquationalLookup.from_macula_dir(MACULA_DIR)
    print(f"Indexed {len(lookup._chain):,} word @refs.")
    tp = fp = fn = tn = 0
    for case in TRUTH_SET:
        pred = is_equational_cola(case["verse_ref"], case["cola_refs"], lookup)
        gold = case["expected_is_equational_cola"]
        ok = (pred == gold)
        if gold and pred: tp += 1
        elif gold and not pred: fn += 1
        elif not gold and pred: fp += 1
        else: tn += 1
        marker = "OK " if ok else "BAD"
        print(f"  [{marker}] {case['id']:24s} pred={pred!s:5s} gold={gold!s:5s} - {case['note']}")
    p = tp / (tp + fp) if (tp + fp) else 1.0
    r = tp / (tp + fn) if (tp + fn) else 1.0
    print(f"\nRound-4 self-test: precision={p:.3f} recall={r:.3f} (tp={tp} fp={fp} fn={fn} tn={tn})")
    return 0 if (fp == 0 and fn == 0) else 1


if __name__ == "__main__":
    sys.exit(run_self_test())
