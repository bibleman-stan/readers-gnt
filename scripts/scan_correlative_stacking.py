#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_correlative_stacking.py

Detects correlative pairs/series (εἴτε/εἴτε, οὔτε/οὔτε, μήτε/μήτε) that are
jammed on a single line when they should be stacked as separate lines.

RULE (established 2026-04-15, refined same session):
  Each correlative member that has its own DISTINCT predicate (its own finite
  verb, explicit or gapped by ellipsis) is a separate proposition and belongs
  on its own line.

  Correlative members that SHARE a single predicate (compound subjects,
  compound objects, or compound qualifiers over one verb) are one proposition
  and may stay on one line.

  Correlative PHRASES (prepositional, nominal) with no finite verbs are
  qualifiers of a head noun/verb and may legitimately stay on one line.

  Examples of the distinction:
    SPLIT: οὔτε γαμοῦσιν οὔτε γαμίζονται  ← two predicates, each member owns one
    STAY:  οὔτε σὴς οὔτε βρῶσις ἀφανίζει  ← one shared predicate, compound subjects

DETECTION:
  A line is flagged when it contains 2+ occurrences of the same correlative
  marker (εἴτε, οὔτε, μήτε) AND the members each have their own finite verb.

  HIGH: 2+ correlative markers on one line, AND each member segment contains
        its own finite verb → distinct predicates → needs stacking
  REVIEW: 2+ correlative markers on one line, finite verb present but shared
          (only one segment has it, i.e. compound subj/obj) OR no finite verb
          (prepositional/nominal series) — human eye needed

Usage:
  py -3 scripts/scan_correlative_stacking.py

Output:
  Console summary + private/scan-correlative-stacking-findings.md
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

REPO_ROOT   = Path(__file__).parent.parent
V4_DIR      = REPO_ROOT / "data" / "text-files" / "v4-editorial"
PRIVATE_DIR = REPO_ROOT / "private"
OUT_FILE    = PRIVATE_DIR / "scan-correlative-stacking-findings.md"

# Correlative markers to detect
CORRELATIVE_MARKERS = {"εἴτε", "οὔτε", "μήτε"}

# Finite verb endings — a token ending with these is likely a finite verb form
# (present/imperfect/aorist/future indicative/subjunctive/optative/imperative)
# Excludes infinitive (-ειν, -ναι, -εσθαι, -σθαι) and participle (-ων, -ούσα, -ον, etc.)
FINITE_ENDINGS = (
    "ω", "εις", "ει", "ομεν", "ετε", "ουσιν", "ουσι",
    "ς", "σιν", "σι",
    "ομαι", "ῃ", "εται", "ομεθα", "εσθε", "ονται",
    "ώ", "ῇς", "ῇ", "ῶμεν", "ῆτε", "ῶσιν", "ῶσι",
    "ην", "ης", "η", "ημεν", "ητε", "ησαν",
    "μεν", "τε", "σαν",
    # copula forms
    "ειμι", "εἰμι", "εστιν", "ἐστιν", "εστι", "ἐστι",
    "εισιν", "εἰσιν", "εισι", "ἐισι",
    "ην", "ἦν", "ησαν", "ἦσαν",
    "εσται", "ἔσται",
)

# Tokens that look like finite verbs (common short forms)
KNOWN_FINITE = {
    "εἶ", "ἐστιν", "ἐστί", "εἰσιν", "εἰσί",
    "ἦν", "ἦσαν", "ἔσται",
    "ἐσθίετε", "πίνετε", "ποιεῖτε",
    "γαμοῦσιν", "γαμίζονται",
    "γρηγορῶμεν", "καθεύδωμεν",
    "ἰσχύει", "ἥμαρτον",
    "ζῶμεν", "κηρύσσομεν",
}

# Tokens that are clearly NOT finite verbs (prepositions, articles, particles, dative nouns)
NON_FINITE_TOKENS = {
    "ἐν", "εἰς", "ἐκ", "ἐξ", "διά", "διʼ", "πρός", "ἀπό", "ἀπʼ",
    "ὑπό", "ὑπʼ", "περί", "κατά", "κατʼ", "μετά", "μετʼ",
    "ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά",
    "τοῦ", "τῆς", "τῷ", "τῇ", "τόν", "τήν",
    "τῶν", "τοῖς", "ταῖς", "τούς", "τάς",
    "λόγου", "πνεύματος", "ἐπιστολῆς", "ζωῆς", "θανάτου",
    "οὐρανῷ", "γῆς", "ἀληθείᾳ", "προφάσει",
    # 3rd-declension dative nouns ending in -ει (would falsely match -ει finite ending)
    "ὄρει", "πόλει", "χάριτι", "δυνάμει", "σαρκί",
}


def line_tokens(line: str) -> List[str]:
    return re.findall(r"[\w\u0300-\u036f\u1f00-\u1fff\u0370-\u03ff]+", line, re.UNICODE)


def is_verse_ref(line: str) -> bool:
    return bool(re.match(r"^\d+:\d+\s*$", line.strip()))


def token_is_finite(tok: str) -> bool:
    """
    Heuristic: does this single token look like a finite verb?
    Returns True for tokens that appear to be finite verbs.
    """
    if tok in CORRELATIVE_MARKERS:
        return False
    if tok in KNOWN_FINITE:
        return True
    if tok in NON_FINITE_TOKENS:
        return False
    # Skip very short tokens (particles, articles)
    if len(tok) <= 2:
        return False
    # Exclude infinitives and participles
    if (tok.endswith("ειν") or tok.endswith("ναι") or
            tok.endswith("σθαι") or tok.endswith("εσθαι")):
        return False  # infinitive
    if (tok.endswith("ων") or tok.endswith("ουσα") or tok.endswith("ον") or
            tok.endswith("ώς") or tok.endswith("υῖα")):
        return False  # likely participle
    # Check for typical finite verb endings.
    # Also includes contracted forms: -οῦνται, -οῦμεν, etc. — these use precomposed
    # circumflex characters, so a plain "ονται" endswith check would miss them.
    for ending in ("ει", "εις", "ουσιν", "ουσι", "ομεν", "ετε",
                    "εται", "ονται", "ομαι", "ωμεν", "ωσιν",
                    "ατε", "ασιν", "ωσι", "σιν",
                    # contracted 3rd-plural middle/passive (omicron-contract)
                    "οῦνται", "οῦμεν", "οῦσιν", "οῦσι",
                    "εῖται", "εῖσθε", "εῖτε",
                    "ῶνται", "ῶμεν", "ῶσιν"):
        if tok.endswith(ending) and len(tok) > len(ending) + 1:
            return True
    return False


def split_into_members(tokens: List[str], marker: str) -> List[List[str]]:
    """
    Split a token list into correlative members at each occurrence of `marker`.
    Returns a list of segments (each is a list of non-marker tokens).
    The pre-first-marker segment is included if non-empty (it may hold a frame verb).
    """
    members: List[List[str]] = []
    current: List[str] = []
    in_member = False
    for tok in tokens:
        if tok == marker:
            if in_member:
                members.append(current)
                current = []
            else:
                # Discard pre-marker frame (not a member)
                current = []
            in_member = True
        else:
            current.append(tok)
    if current and in_member:
        members.append(current)
    return members


def has_distinct_predicates(tokens: List[str], marker: str) -> bool:
    """
    TRUE if each correlative member has its own distinct finite verb.
    This is the decisive test for stacking:
      - DISTINCT predicates (each member has its own verb) → separate propositions → stack
      - SHARED predicate (single verb after all members, or verb only in one member)
        → compound subject/object → one proposition → stay

    Method: split tokens at each occurrence of `marker` to get per-member segments.
    Count how many segments contain a finite verb token. If 2+ segments have their
    own verb, the predicates are distinct. If ≤1, the predicate is shared or absent.
    """
    members = split_into_members(tokens, marker)
    if len(members) < 2:
        return False  # can't have distinct predicates with <2 members
    members_with_verb = sum(1 for m in members if any(token_is_finite(t) for t in m))
    return members_with_verb >= 2


def has_finite_verb(tokens: List[str], marker_positions: List[int]) -> bool:
    """
    Heuristic: does the line contain any finite verb?
    Used as a pre-filter before the distinct-predicate test.
    """
    return any(token_is_finite(tok) for tok in tokens)


def count_marker_occurrences(tokens: List[str]) -> Dict[str, int]:
    """Count occurrences of each correlative marker in the token list."""
    counts: Dict[str, int] = defaultdict(int)
    for tok in tokens:
        if tok in CORRELATIVE_MARKERS:
            counts[tok] += 1
    return dict(counts)


def scan_file(path: Path) -> List[Dict]:
    candidates = []
    lines = path.read_text(encoding="utf-8").splitlines()
    book = path.parent.name
    chapter = path.stem

    current_verse = None
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            continue
        if is_verse_ref(stripped):
            current_verse = stripped
            continue

        tokens = line_tokens(stripped)
        marker_counts = count_marker_occurrences(tokens)

        # Need at least one marker appearing 2+ times, OR two different markers
        total_markers = sum(marker_counts.values())
        if total_markers < 2:
            continue

        # Check for same marker appearing 2+
        has_repeated = any(v >= 2 for v in marker_counts.values())
        if not has_repeated:
            continue

        # Determine marker type and count
        for marker, count in marker_counts.items():
            if count >= 2:
                # HIGH: each member has its own DISTINCT predicate → needs stacking
                # REVIEW: finite verb present but shared across members (compound subj/obj)
                #         OR no finite verb at all (prepositional/nominal qualifiers)
                distinct = has_distinct_predicates(tokens, marker)
                if distinct:
                    confidence = "HIGH"
                elif has_finite_verb(tokens, []):
                    confidence = "REVIEW"
                else:
                    confidence = "REVIEW"

                ctx_before = [l.strip() for l in lines[max(0, i-3):i]
                              if l.strip() and not is_verse_ref(l.strip())]
                ctx_after  = [l.strip() for l in lines[i+1:i+4]
                              if l.strip() and not is_verse_ref(l.strip())]

                candidates.append({
                    "book":       book,
                    "chapter":    chapter,
                    "verse":      current_verse,
                    "line_no":    i + 1,
                    "content":    stripped,
                    "confidence": confidence,
                    "marker":     marker,
                    "count":      count,
                    "ctx_before": ctx_before[-2:],
                    "ctx_after":  ctx_after[:2],
                })
                break  # report once per line

    return candidates


def scan_corpus() -> List[Dict]:
    all_candidates = []
    for book_dir in sorted(V4_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        for chapter_file in sorted(book_dir.glob("*.txt")):
            all_candidates.extend(scan_file(chapter_file))
    return all_candidates


def write_report(candidates: List[Dict]) -> None:
    high   = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]

    by_book = defaultdict(list)
    for c in candidates:
        by_book[c["book"]].append(c)

    lines = [
        "# Correlative Stacking Scan — Findings",
        "",
        "**Rule:** Correlative members with own finite verbs = separate propositions = stack.",
        "Correlative phrases (prepositional/nominal) = qualifiers = may stay together.",
        "",
        f"**Total candidates:** {len(candidates)}  ",
        f"**HIGH (finite verb detected — likely needs stacking):** {len(high)}  ",
        f"**REVIEW (no finite verb — may be correct as-is):** {len(review)}  ",
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
        lines.append(
            f"### {c['chapter']} {c['verse']} — line {c['line_no']} "
            f"[{c['confidence']}] ({c['marker']} ×{c['count']})"
        )
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
    print("Scanning corpus for jammed correlative pairs...")
    candidates = scan_corpus()

    high   = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]

    print(f"  Total candidates: {len(candidates)}")
    print(f"  HIGH (needs stacking):  {len(high)}")
    print(f"  REVIEW (may be OK):     {len(review)}")

    by_book = defaultdict(int)
    for c in candidates:
        by_book[c["book"]] += 1
    print("\nBy book:")
    for book, count in sorted(by_book.items(), key=lambda x: -x[1]):
        print(f"  {book}: {count}")

    write_report(candidates)


if __name__ == "__main__":
    main()
