#!/usr/bin/env python3
"""
gnt-matrix-finite Round 4 prototype.
4-tier matrix-vs-embedded finite-verb detection over Macula sblgnt-lowfat XML.
"""
from __future__ import annotations
import os, sys, glob
from xml.etree import ElementTree as ET
from typing import Optional, Iterable

LOWFAT_DIR = r"C:/Users/bibleman/repos/readers-gnt/research/macula-greek/SBLGNT/lowfat"

FINITE_LOWFAT = {"indicative", "subjunctive", "imperative", "optative"}
NOMINAL_MOODS = {"participle", "infinitive"}
EMBEDDED_ROLES = {"s", "o", "o2", "io", "adv", "p", "topic", "vc"}
CL_NEG_CLTYPES = {"Verbless", "VerbElided", "Minor"}


def _is_cl_wg(el) -> bool:
    return el.tag == "wg" and (el.get("class") == "cl" or el.get("cltype"))


def _direct_verbs(el):
    for c in el:
        if c.tag == "w" and c.get("class") == "verb":
            yield c


def _head_verb(el) -> Optional[ET.Element]:
    for w in _direct_verbs(el):
        if w.get("role") == "v":
            return w
    return None


def _rule_has_V_slot(rule: Optional[str]) -> bool:
    if not rule:
        return False
    slots = [s.strip() for s in rule.split("-")]
    return any(s == "V" for s in slots)


def _is_embedded_wg(el) -> bool:
    return (el.get("role") or "") in EMBEDDED_ROLES


def _verb_in_embedded_descendant(el, w) -> bool:
    parent_chain = []
    def walk(node, chain):
        nonlocal parent_chain
        for c in node:
            chain.append(c)
            if c is w:
                parent_chain = list(chain)
                return True
            if walk(c, chain):
                return True
            chain.pop()
        return False
    walk(el, [])
    for anc in parent_chain[:-1]:
        if anc.tag != "wg":
            continue
        if _is_cl_wg(anc) and anc is not el:
            return True
        if (anc.get("role") or "") in EMBEDDED_ROLES:
            return True
    return False


def matrix_finite_predicate(cl_node: ET.Element) -> bool:
    # Tier 1
    cltype = cl_node.get("cltype")
    if cltype in CL_NEG_CLTYPES:
        return False
    # Tier 2
    head = _head_verb(cl_node)
    if head is not None:
        m = head.get("mood")
        if m in FINITE_LOWFAT:
            return True
        if m in NOMINAL_MOODS:
            pass
    # Tier 3
    if _is_embedded_wg(cl_node):
        return False
    rule = cl_node.get("rule")
    has_v_slot = _rule_has_V_slot(rule)
    if head is None and not has_v_slot:
        return False
    # Tier 4
    for w in cl_node.iter("w"):
        if w.get("class") != "verb":
            continue
        if w.get("mood") not in FINITE_LOWFAT:
            continue
        if w is head:
            return True
        if _verb_in_embedded_descendant(cl_node, w):
            continue
        if w.get("role") in {"v", None}:
            return True
    return False


_BOOK_FILE = {
    "MAT": "01-matthew.xml", "MRK": "02-mark.xml", "LUK": "03-luke.xml",
    "JHN": "04-john.xml",    "ACT": "05-acts.xml", "ROM": "06-romans.xml",
    "1CO": "07-1corinthians.xml", "2CO": "08-2corinthians.xml",
    "GAL": "09-galatians.xml", "EPH": "10-ephesians.xml",
    "PHP": "11-philippians.xml", "COL": "12-colossians.xml",
}

_TREE_CACHE: dict = {}


def _load(book: str) -> ET.ElementTree:
    if book not in _TREE_CACHE:
        fn = os.path.join(LOWFAT_DIR, _BOOK_FILE[book])
        _TREE_CACHE[book] = ET.parse(fn)
    return _TREE_CACHE[book]


def find_innermost_cl(anchor_ref: str) -> Optional[ET.Element]:
    """Find the innermost <wg class='cl' or with cltype> ancestor of the
    token whose @ref == anchor_ref."""
    book = anchor_ref.split(" ")[0]
    tree = _load(book)
    root = tree.getroot()
    # Walk to find the token and remember its ancestor chain of cl-wgs.
    found_chain = []
    def walk(node, chain):
        for c in node:
            new_chain = chain + [c]
            if c.tag == "w" and c.get("ref") == anchor_ref:
                # The innermost cl-wg ancestor:
                found_chain.extend(new_chain)
                return True
            if walk(c, new_chain):
                return True
        return False
    walk(root, [])
    if not found_chain:
        return None
    # Find innermost (deepest) wg in chain that is a cl-wg
    innermost = None
    for anc in found_chain:
        if anc.tag == "wg" and _is_cl_wg(anc):
            innermost = anc
    return innermost


# Truth set
TRUTH = [
    {"case_id": "ROM_2_7_A", "anchor": "ROM 2:7!1", "expected": False},
    {"case_id": "ROM_2_7_INNER", "anchor": "ROM 2:7!12", "expected": False},
    {"case_id": "ROM_8_5_A", "anchor": "ROM 8:5!9", "expected": True},
    {"case_id": "ROM_8_5_B", "anchor": "ROM 8:5!13", "expected": False},
    {"case_id": "1CO_12_8_A", "anchor": "1CO 12:8!7", "expected": True},
]


def main():
    print(f"Substrate dir: {LOWFAT_DIR}")
    print(f"Exists: {os.path.isdir(LOWFAT_DIR)}")
    print()
    results = []
    for case in TRUTH:
        cl = find_innermost_cl(case["anchor"])
        if cl is None:
            actual = None
            tier_info = "NO-CL-FOUND"
        else:
            actual = matrix_finite_predicate(cl)
            tier_info = (
                f"class={cl.get('class')} cltype={cl.get('cltype')} "
                f"clauseType={cl.get('clauseType')} role={cl.get('role')} "
                f"rule={cl.get('rule')}"
            )
        expected = case["expected"]
        status = "PASS" if actual == expected else "FAIL"
        results.append({
            "case_id": case["case_id"],
            "anchor": case["anchor"],
            "expected": expected,
            "actual": actual,
            "status": status,
            "info": tier_info,
        })
        print(f"[{status}] {case['case_id']:<18} anchor={case['anchor']:<16} "
              f"expected={expected!s:<5} actual={actual!s:<5} | {tier_info}")
    print()
    passes = sum(1 for r in results if r["status"] == "PASS")
    fails = sum(1 for r in results if r["status"] == "FAIL")
    print(f"PASSES: {passes}/{len(results)}")
    print(f"FAILS:  {fails}/{len(results)}")

    # Precision / recall on the "True" class
    tp = sum(1 for r in results if r["expected"] is True and r["actual"] is True)
    fp = sum(1 for r in results if r["expected"] is False and r["actual"] is True)
    fn = sum(1 for r in results if r["expected"] is True and r["actual"] is False)
    tn = sum(1 for r in results if r["expected"] is False and r["actual"] is False)
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    print(f"TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")


if __name__ == "__main__":
    main()
