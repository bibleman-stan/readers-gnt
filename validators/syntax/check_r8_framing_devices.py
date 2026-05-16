"""
check_r8_framing_devices.py — Layer 1 validator for Rule R8.

R8 (canon §3.3): Framing devices attach to their content — they must LEAD what
follows, never trail a line. When found line-final, the framing device is orphaned
from its content and must merge forward.

Closed list (Closed-List Registry §3.3):
  ἰδού, διό, οὖν, νυν δέ, ἀλλά, γάρ, πλήν, τοιγαροῦν

Note on "νυν δέ": the two-token phrase can trail a line only if BOTH tokens are
the last two tokens. We detect it as a two-token sequence. Single-token members
are checked as the last token.

Layer: 1 (MALFORMED) — pure Koine syntax facts.
Action: STRONG-MERGE forward (the content line follows).
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

RULE_ID = "R8"
ERROR_CLASS = "MALFORMED"

# Single-token framing devices that must not trail a line.
# Accent variants: νῦν / νυν — strip_punctuation does NFC but leaves accents.
# We use the NFC lemma form as it appears in v4/grk text.
_FRAMING_SINGLE: frozenset[str] = frozenset({
    "ἰδού",
    "διό",
    "οὖν",
    "ἀλλά",
    "γάρ",
    "πλήν",
    "τοιγαροῦν",
})

# Two-token phrase: "νῦν δέ" (or "νυν δε" with accent variants).
# Both tokens must appear consecutively at end of line.
_NUN_VARIANTS: frozenset[str] = frozenset({"νῦν", "νυν", "νύν"})
_DE_VARIANTS: frozenset[str] = frozenset({"δέ", "δε"})

_BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R8 framing-device violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)
    candidates: List[Candidate] = []

    for vline in v4.lines:
        tokens = vline.tokens  # already punctuation-stripped, NFC
        if not tokens:
            continue

        # ----- single-token check -----
        last_token = tokens[-1]
        if last_token in _FRAMING_SINGLE:
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
                        f"R8: framing device '{last_token}' trails line — "
                        f"must lead its content (merge forward)"
                    ),
                    context=context,
                )
            )
            continue  # already flagged; no need to check two-token phrase

        # ----- two-token "νῦν δέ" check -----
        if len(tokens) >= 2:
            second_last = tokens[-2]
            if second_last in _NUN_VARIANTS and last_token in _DE_VARIANTS:
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
                            f"R8: framing device 'νῦν δέ' trails line — "
                            f"must lead its content (merge forward)"
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
        return "## R8 framing-devices-attach\n\nNo violations found.\n"
    lines = [f"## R8 framing-devices-attach — {len(candidates)} violation(s)\n"]
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
        description="R8 validator: framing devices must not trail a line."
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
                print(f"[R8] WARNING: {args.book} ch.{ch} skipped — {exc}", file=sys.stderr)
                ch += 1
                if ch > 200:
                    break
    else:
        for slug, chapter_num, _fp in iter_v4_chapters():
            try:
                all_candidates.extend(check_book_chapter(slug, chapter_num))
            except Exception as exc:
                print(f"[R8] WARNING: {slug} ch.{chapter_num} skipped — {exc}", file=sys.stderr)

    report = _format_report(all_candidates)
    print(f"[R8] {len(all_candidates)} violation(s) found.", file=sys.stderr)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R8] Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
