"""
check_r25_hoste_consecutive_result.py — Layer 3 validator for Rule R25 (canon §3.14a).

R25 ὥστε Short-Consecutive-Result Binding:
  When a ὥστε-clause expresses the direct result of the preceding action AND meets
  all three conditions, the ὥστε-clause merges onto the same line as its matrix:
    1. ≤8 words (counting ὥστε itself)
    2. Co-referential subject (implied agent of infinitive = matrix subject)
    3. No camera shift

  ὥστε on its own line (split from matrix) with ≤8 words = STRONG-MERGE-CANDIDATE.
  ὥστε on its own line with >8 words = SPLIT-MAINTAINED (word-count-exceeded).
  ὥστε as verse-initial token (idx=0) = REVIEW-REQUIRED (cross-verse-defer).
  Illative-ὥστε markers detected by surface heuristics = SPLIT-MAINTAINED (illative-hoste).

  NOTE: Condition 2 (co-referential subject) and Condition 3 (no camera shift) are
  semantic/pragmatic and cannot be reliably determined by surface scan alone. The
  validator therefore emits STRONG-MERGE-CANDIDATE for ≤8-word cases after passing
  the illative-filter; per-item human review applies the semantic conditions. Known
  Phase A merges (already applied) are excluded from re-flagging via a skip-set.

Usage:
  PYTHONIOENCODING=utf-8 py -3 -m validators.colometry.check_r25_hoste_consecutive_result \\
      [--book SLUG] [--chapter N] [--output PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    parse_chapter_file,
    strip_punctuation,
)

RULE_ID = "R25"
ERROR_CLASS = "MERGE"  # Layer 3 editorial — merge candidate

# ─── Book slug table ──────────────────────────────────────────────────────────

_BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]

# ─── Phase A skip-set — already merged; do not re-flag ───────────────────────
# Format: (book, chapter, verse) — these loci had their ὥστε-clause merged
# onto the matrix line in Phase A (2026-05-11). The validator should not
# re-surface them as candidates.

_PHASE_A_APPLIED: frozenset[tuple[str, int, int]] = frozenset({
    ("matt",    8, 24),
    ("matt",   10,  1),
    ("matt",   12, 22),
    ("matt",   13,  2),
    ("matt",   13, 54),
    ("matt",   27,  1),
    ("matt",   27, 14),
    ("mark",    1, 27),
    ("mark",    3, 20),
    ("mark",    4,  1),
    ("mark",    4, 37),
    ("mark",   15,  5),
    ("luke",    4, 29),
    ("luke",    5,  7),
    ("luke",   12,  1),
    ("acts",   15, 39),
    ("1cor",   13,  2),
    ("2cor",    1,  8),
    ("2cor",    7,  7),
    ("1thess",  1,  8),
})

# ─── Phase C skip-set — cross-verse merges applied 2026-05-11 ────────────────
# These loci had their verse-initial ὥστε-clause merged onto the prior verse's
# last line per §3.17 cross-verse merge procedure (audit task aae0b801a5130b535).

_PHASE_C_APPLIED: frozenset[tuple[str, int, int]] = frozenset({
    ("matt",   15, 31),  # ὥστε τὸν ὄχλον θαυμάσαι → merged onto v.30 last line
    ("matt",   19,  6),  # ὥστε οὐκέτι εἰσὶν δύο → merged onto v.5 last line
    ("acts",    5, 15),  # ὥστε καὶ εἰς τὰς πλατείας → merged onto v.14 last line
    ("1cor",    1,  7),  # ὥστε ὑμᾶς μὴ ὑστερεῖσθαι → merged onto v.6 last line
    ("heb",    13,  6),  # ὥστε θαρροῦντας ἡμᾶς λέγειν → merged onto v.5 last line
})

# Combined skip-set used in the chapter checker
_ALL_APPLIED: frozenset[tuple[str, int, int]] = _PHASE_A_APPLIED | _PHASE_C_APPLIED

# ─── Known illative-ὥστε loci — emit SPLIT-MAINTAINED ────────────────────────
# These are unambiguous illative cases confirmed during Phase A audit.

_ILLATIVE_KNOWN: frozenset[tuple[str, int, int]] = frozenset({
    ("matt",  23, 31),  # ὥστε μαρτυρεῖτε — 2p imperative
    ("matt",  12, 12),  # ὥστε ἔξεστιν — new 3P declarative conclusion
    ("gal",    4,  7),  # ὥστε οὐκέτι εἶ δοῦλος — inferential 2P declarative
    ("gal",    4, 16),  # ὥστε ἐχθρὸς ὑμῶν γέγονα — rhetorical conclusion
    # Phase C newly-confirmed illatives (2026-05-11, audit task aae0b801a5130b535)
    ("mark",   2, 28),  # ὥστε κύριός ἐστιν — inferential declarative from argument
    ("rom",    7, 12),  # ὥστε ὁ νόμος ἅγιος — inferential summary conclusion
    ("rom",   13,  2),  # ὥστε ὁ ἀντιτασσόμενος — inferential consequence chain
    ("1cor",   3,  7),  # ὥστε οὔτε ὁ φυτεύων — inferential negation of prior claim
    ("1cor",   3, 21),  # ὥστε μηδεὶς καυχάσθω — 3p imperative conclusion
    ("1cor",   4,  5),  # ὥστε μὴ πρὸ καιροῦ — negative imperative
    ("1cor",   5,  8),  # ὥστε ἑορτάζωμεν — 1p hortatory subjunctive
    ("1cor",   7, 38),  # ὥστε καὶ ὁ γαμίζων — inferential declarative
    ("1cor",  10, 12),  # ὥστε ὁ δοκῶν ἑστάναι — warning-inferential declarative
    ("1cor",  14, 22),  # ὥστε αἱ γλῶσσαι — inferential declarative claim
    ("1cor",  14, 39),  # ὥστε ζηλοῦτε — 2p imperative exhortation
    ("2cor",   2,  7),  # ὥστε τοὐναντίον — inferential reversal
    ("2cor",   4, 12),  # ὥστε ὁ θάνατος — inferential contrast
    ("2cor",   5, 17),  # ὥστε εἴ τις ἐν Χριστῷ — inferential new-creation declaration
    ("gal",    3,  9),  # ὥστε οἱ ἐκ πίστεως — inferential conclusion to argument
    ("gal",    3, 24),  # ὥστε ὁ νόμος παιδαγωγός — inferential summary
    ("phil",   4,  1),  # ὥστε ἀδελφοί μου — vocative + 2p imperative
    ("1thess", 4, 18),  # ὥστε παρακαλεῖτε — 2p imperative exhortation
    ("1pet",   4, 19),  # ὥστε καὶ οἱ πάσχοντες — inferential hortatory
})

# ─── Illative surface heuristics ─────────────────────────────────────────────
# Applied when not in _ILLATIVE_KNOWN: if any of these patterns appear in
# the ὥστε-line, classify as illative rather than consecutive-result.

# 2nd-person imperative mood endings (surface form scan — not morphologically
# parsed; relies on common 2p imperative suffixes that follow ὥστε).
# This list targets the most common NT forms; a false negative simply means the
# item surfaces for manual review, which is acceptable.
_2P_IMPERATIVE_SUFFIXES = (
    "ατε", "ετε", "ωσιν", "ατω", "ωμεν",  # present/aorist active 2p pl imv
    "εσθε", "ασθε",                         # middle 2p pl imv
)

_VOCATIVE_MARKER_WORDS = {
    "ἀδελφοί", "ἀδελφέ", "τέκνα", "τεκνία", "πατέρες",
    "κύριε", "κύριοι", "θεέ", "ἄνδρες", "γύναι",
}


def _is_likely_illative(tokens_after_hoste: list[str]) -> bool:
    """
    Heuristic: is this ὥστε-clause likely illative rather than consecutive-result?

    Fires when:
      (a) vocative-marker word appears anywhere in the clause, OR
      (b) the first non-trivial token looks like a 2p imperative verb.

    Returns True = likely illative → SPLIT-MAINTAINED.
    """
    if not tokens_after_hoste:
        return False

    # Check for vocative marker
    stripped = {strip_punctuation(t) for t in tokens_after_hoste}
    if stripped & _VOCATIVE_MARKER_WORDS:
        return True

    # Check first token for 2p imperative ending
    first = strip_punctuation(tokens_after_hoste[0])
    for suffix in _2P_IMPERATIVE_SUFFIXES:
        if first.endswith(suffix) and len(first) > len(suffix):
            return True

    return False


# ─── Chapter-level checker ────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return R25 candidates for one chapter."""
    # Locate the chapter file
    chapter_path: str | None = None
    for slug, ch_num, fp in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_path = fp
            break
    if chapter_path is None:
        raise FileNotFoundError(
            f"v4/grc chapter not found: book={book!r} chapter={chapter}"
        )

    verses = parse_chapter_file(chapter_path)
    candidates: List[Candidate] = []

    for verse in verses:
        vs_ch = verse["ch"]
        vs_num = verse["vs"]
        lines: list[str] = verse["lines"]

        # Skip already-applied loci (Phase A + Phase C)
        if (book, vs_ch, vs_num) in _ALL_APPLIED:
            continue

        for idx, line in enumerate(lines):
            tokens = line.split()
            if not tokens:
                continue

            # Normalise: strip punctuation from first token to detect ὥστε
            first_stripped = strip_punctuation(tokens[0])

            # ὥστε must lead the line
            if first_stripped != "ὥστε":
                continue

            book_cap = book[0].upper() + book[1:]
            verse_ref = f"{book_cap} {vs_ch}:{vs_num}"

            # Known illative loci — checked BEFORE cross-verse-defer so that
            # verse-initial (idx=0) illatives classify as SPLIT-MAINTAINED rather
            # than REVIEW-REQUIRED (idx=0 preemption bug fixed 2026-05-11).
            if (book, vs_ch, vs_num) in _ILLATIVE_KNOWN:
                candidates.append(
                    emit_candidate(
                        verse_ref=verse_ref,
                        line_index=idx,
                        line_text=line.strip(),
                        rule=RULE_ID,
                        tag="SPLIT-MAINTAINED",
                        error_class=ERROR_CLASS,
                        rationale=(
                            "R25 illative-hoste (known): ὥστε functions as inferential "
                            "conjunction ('therefore'), not consecutive-result. "
                            "Split is correct per canon §3.14a exclusion."
                        ),
                    )
                )
                continue

            # Word count (entire line, including ὥστε)
            word_count = len(tokens)

            # Illative heuristic on unknown loci — also runs before cross-verse-defer
            # so verse-initial heuristic-illatives get SPLIT-MAINTAINED, not REVIEW-REQUIRED.
            tokens_after = tokens[1:]  # everything after ὥστε
            if _is_likely_illative(tokens_after):
                candidates.append(
                    emit_candidate(
                        verse_ref=verse_ref,
                        line_index=idx,
                        line_text=line.strip(),
                        rule=RULE_ID,
                        tag="SPLIT-MAINTAINED",
                        error_class=ERROR_CLASS,
                        rationale=(
                            "R25 illative-hoste (heuristic): surface markers suggest "
                            "ὥστε is inferential ('therefore'), not consecutive-result. "
                            "Verify manually; split is presumed correct."
                        ),
                    )
                )
                continue

            # Cross-verse case: ὥστε is verse-initial (idx == 0) — matrix in prior verse.
            # Placed after illative checks so illative idx=0 cases don't fall here.
            if idx == 0:
                candidates.append(
                    emit_candidate(
                        verse_ref=verse_ref,
                        line_index=idx,
                        line_text=line.strip(),
                        rule=RULE_ID,
                        tag="REVIEW-REQUIRED",
                        error_class=ERROR_CLASS,
                        rationale=(
                            "R25 cross-verse-defer: ὥστε is verse-initial (idx=0); "
                            "matrix clause lives in the prior verse. "
                            "Requires §3.17 cross-verse merge procedure — Phase C."
                        ),
                    )
                )
                continue

            if word_count > 8:
                candidates.append(
                    emit_candidate(
                        verse_ref=verse_ref,
                        line_index=idx,
                        line_text=line.strip(),
                        rule=RULE_ID,
                        tag="SPLIT-MAINTAINED",
                        error_class=ERROR_CLASS,
                        rationale=(
                            f"R25 word-count-exceeded: {word_count} words > 8-word threshold. "
                            "Phase B territory — Phase A limit is ≤8 words. Split is correct."
                        ),
                    )
                )
                continue

            # Clean consecutive-result candidate: ≤8 words, not illative, not cross-verse
            # Conditions 2 (co-referential subject) and 3 (no camera shift) require
            # semantic review — surfaced as STRONG-MERGE-CANDIDATE for editorial confirmation.
            candidates.append(
                emit_candidate(
                    verse_ref=verse_ref,
                    line_index=idx,
                    line_text=line.strip(),
                    rule=RULE_ID,
                    tag="STRONG-MERGE-CANDIDATE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"R25: ὥστε-clause ({word_count} word(s) ≤ 8) on its own line — "
                        "merge onto preceding matrix line if subject is co-referential "
                        "and no camera shift (canon §3.14a, conditions 2-3)."
                    ),
                )
            )

    return candidates


# ─── Report formatter ─────────────────────────────────────────────────────────

def _format_report(all_candidates: List[Candidate]) -> str:
    strong = [c for c in all_candidates if c.tag == "STRONG-MERGE-CANDIDATE"]
    split = [c for c in all_candidates if c.tag == "SPLIT-MAINTAINED"]
    review = [c for c in all_candidates if c.tag == "REVIEW-REQUIRED"]

    lines = ["## R25 ὥστε consecutive-result candidates\n"]
    lines.append(
        f"Summary: {len(strong)} STRONG-MERGE-CANDIDATE  |  "
        f"{len(split)} SPLIT-MAINTAINED  |  "
        f"{len(review)} REVIEW-REQUIRED\n"
    )

    if strong:
        lines.append("### STRONG-MERGE-CANDIDATE\n")
        for c in strong:
            lines.append(f"**{c.verse_ref}** (line {c.line_index}) [{c.tag}]")
            lines.append(f"  > {c.line_text}")
            lines.append(f"  {c.rationale}")
            lines.append("")

    if split:
        lines.append("### SPLIT-MAINTAINED\n")
        for c in split:
            lines.append(f"**{c.verse_ref}** (line {c.line_index}) [{c.tag}]")
            lines.append(f"  > {c.line_text}")
            lines.append(f"  {c.rationale}")
            lines.append("")

    if review:
        lines.append("### REVIEW-REQUIRED\n")
        for c in review:
            lines.append(f"**{c.verse_ref}** (line {c.line_index}) [{c.tag}]")
            lines.append(f"  > {c.line_text}")
            lines.append(f"  {c.rationale}")
            lines.append("")

    if not all_candidates:
        lines.append("No ὥστε-initial lines found (or all Phase A loci already merged).\n")

    return "\n".join(lines)


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "R25 validator: ὥστε short-consecutive-result binding. "
            "Flags ὥστε-initial lines that should merge onto their matrix."
        )
    )
    parser.add_argument("--book", help="Restrict to one book slug (e.g. 'mark', '1cor')")
    parser.add_argument(
        "--chapter", type=int, help="Restrict to one chapter (requires --book)"
    )
    parser.add_argument("--output", help="Write markdown report to this file path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    books_to_run = [args.book] if args.book else _BOOKS
    all_candidates: List[Candidate] = []

    for book in books_to_run:
        chapters_to_run = [args.chapter] if args.chapter else list(range(1, 200))
        for ch in chapters_to_run:
            try:
                candidates = check_book_chapter(book, ch)
                all_candidates.extend(candidates)
            except FileNotFoundError:
                break  # chapter doesn't exist — move on
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[R25] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_report(all_candidates)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        sys.stderr.write(
            f"[R25] Report written to {args.output} "
            f"({len(all_candidates)} candidates)\n"
        )
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(report)
        print(f"[R25] Total: {len(all_candidates)} candidate(s)")


if __name__ == "__main__":
    main()
