"""
check_r9_subordinate_clause.py — Layer 1 validator for Rule R9.

R9 (canon §3.4): Subordinate-clause-opener particles must LEAD their content —
they must never trail a line. When found line-final, the opener is severed from
the clause it governs and must merge forward.

Closed list (Closed-List Registry §3.4 "R9 subordinate-clause openers"):
  ἵνα, ὥστε, ὅτι, διότι, ὅταν, ὅτε, εἰ, ἐάν, καθώς, μήποτε

Note on ὅτι: R10 handles the cognition-vs-declaration split-vs-merge decision
WITHIN a line (or across lines for the merged/split state). R9 enforces only
the "never line-final" piece — a trailing ὅτι is MALFORMED regardless of the
verb class that precedes it.

Note on εἰ / ἐάν: these are common single-character particles and may generate
some false positives in contexts where εἰ is used as a discourse marker rather
than a conditional opener. The rule is Layer 1 (syntax fact) so we emit
STRONG-MERGE; editorial review catches edge cases.

Layer: 1 (MALFORMED) — pure Koine syntax facts.
Action: STRONG-MERGE forward.
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    load_v4_editorial,
    strip_punctuation,
)

RULE_ID = "R9"
ERROR_CLASS = "MALFORMED"

# Subordinate-clause openers that must never trail a line.
# Forms are the NFC-normalized surface forms as they appear in v4/grk after
# strip_punctuation (which is already applied to V4Line.tokens).
_SUB_CLAUSE_OPENERS: frozenset[str] = frozenset({
    "ἵνα",
    "ὥστε",
    "ὅτι",
    "διότι",
    "ὅταν",
    "ὅτε",
    "εἰ",
    "ἐάν",
    "καθώς",
    "μήποτε",
})

_BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R9 violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)
    candidates: List[Candidate] = []

    for vline in v4.lines:
        tokens = vline.tokens  # punctuation-stripped NFC tokens
        if not tokens:
            continue

        last_token = tokens[-1]
        if last_token in _SUB_CLAUSE_OPENERS:
            context = _build_context(v4.lines, vline.line_index)
            candidates.append(
                emit_candidate(
                    verse_ref=vline.verse_ref,
                    line_index=vline.line_index,
                    line_text=vline.text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"R9: subordinate-clause opener '{last_token}' trails line — "
                        f"must lead its clause (merge forward)"
                    ),
                    context=context,
                )
            )

    return candidates


def _build_context(v4_lines: list, line_index: int) -> str:
    """Return up to 3 adjacent lines as context string."""
    start = max(0, line_index - 1)
    end = min(len(v4_lines), line_index + 2)
    return " | ".join(v4_lines[i].text for i in range(start, end))


def _format_report(candidates: List[Candidate]) -> str:
    if not candidates:
        return "## R9 subordinate-clause-introduction\n\nNo violations found.\n"
    lines = [f"## R9 subordinate-clause-introduction — {len(candidates)} violation(s)\n"]
    for c in candidates:
        lines.append(
            f"- **{c.verse_ref}** (line {c.line_index}) [{c.tag}]\n"
            f"  > {c.line_text}\n"
            f"  {c.rationale}\n"
        )
        if c.context:
            lines.append(f"  *context:* {c.context}\n")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R9 validator: subordinate-clause openers must not trail a line."
    )
    parser.add_argument("--book", help="Restrict to one book slug (e.g. 'mark')")
    parser.add_argument("--chapter", type=int, help="Restrict to one chapter (requires --book)")
    parser.add_argument("--output", help="Write markdown report to this path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    all_candidates: List[Candidate] = []

    if args.book and args.chapter:
        all_candidates = check_book_chapter(args.book, args.chapter)
    elif args.book:
        ch = 1
        while True:
            try:
                all_candidates.extend(check_book_chapter(args.book, ch))
                ch += 1
            except FileNotFoundError:
                break
            except Exception as exc:
                print(f"[R9] WARNING: {args.book} ch.{ch} skipped — {exc}", file=sys.stderr)
                ch += 1
                if ch > 200:
                    break
    else:
        for slug, chapter_num, _fp in iter_v4_chapters():
            try:
                all_candidates.extend(check_book_chapter(slug, chapter_num))
            except Exception as exc:
                print(f"[R9] WARNING: {slug} ch.{chapter_num} skipped — {exc}", file=sys.stderr)

    report = _format_report(all_candidates)
    print(f"[R9] {len(all_candidates)} violation(s) found.", file=sys.stderr)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R9] Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
