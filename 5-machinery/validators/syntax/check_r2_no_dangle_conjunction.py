"""
check_r2_no_dangle_conjunction.py — Layer 1 validator for Rule R2.

R2: Never dangle a conjunction at line end.
  (a) A line must not END on a coordinating conjunction (CCONJ).
  (b) A line must not START on a postpositive enclitic.

Both conditions are MALFORMED-class violations; both produce STRONG-MERGE candidates.
"""

from __future__ import annotations

import argparse
import sys
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    load_macula_chapter,
    load_v4_editorial,
    map_tokens_to_lines,
    strip_punctuation,
    get_rule_attr,
)

RULE_ID = "R2"
ERROR_CLASS = "MALFORMED"

# Coordinating conjunctions that must not trail a line.
LINE_END_CCONJ_LEMMAS: frozenset[str] = frozenset({"καί", "δέ", "ἀλλά", "γάρ", "οὖν"})

# Postpositive enclitics that must not open a line.
# δέ, γάρ, οὖν, μέν are CCONJ or PART depending on tagging; τε is CCONJ; ἄν is PART.
LINE_START_POSTPOSITIVE_LEMMAS: frozenset[str] = frozenset(
    {"δέ", "γάρ", "οὖν", "μέν", "τε", "ἄν"}
)
LINE_START_POSTPOSITIVE_POS: frozenset[str] = frozenset({"CCONJ", "PART"})

# Canonical NT book list (27 books, abbrevs matching build pipeline convention).
BOOKS: list[str] = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1corinthians", "2corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1thessalonians", "2thessalonians",
    "1timothy", "2timothy", "titus", "philemon",
    "hebrews", "james", "1peter", "2peter",
    "1john", "2john", "3john", "jude", "revelation",
]


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R2 violations in this chapter."""
    macula = load_macula_chapter(book, chapter)
    v4 = load_v4_editorial(book, chapter)
    tokens = map_tokens_to_lines(v4, macula)

    # Group tokens by line_index so we know each line's length.
    lines_token_count: dict[int, int] = {}
    for tok in tokens:
        lines_token_count[tok.line_index] = (
            lines_token_count.get(tok.line_index, 0) + 1
        )

    candidates: List[Candidate] = []

    for tok in tokens:
        line_len = lines_token_count.get(tok.line_index, 1)
        lemma = strip_punctuation(tok.lemma) if hasattr(tok, "lemma") else ""

        # (a) Line-end CCONJ check.
        # Edge case: a one-token line that IS all-CCONJ is also a violation —
        # such a line is neither grammatically complete nor a valid colon.
        if (
            tok.position_in_line == line_len - 1
            and tok.pos == "CCONJ"
            and lemma in LINE_END_CCONJ_LEMMAS
        ):
            context = _build_context(v4, tok.line_index)
            candidates.append(
                emit_candidate(
                    verse_ref=tok.verse_ref,
                    line_index=tok.line_index,
                    line_text=v4.lines[tok.line_index].text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=f"Line ends on coordinating conjunction '{lemma}'",
                    context=context,
                )
            )

        # (b) Line-start postpositive check.
        if (
            tok.position_in_line == 0
            and tok.pos in LINE_START_POSTPOSITIVE_POS
            and lemma in LINE_START_POSTPOSITIVE_LEMMAS
        ):
            context = _build_context(v4, tok.line_index)
            candidates.append(
                emit_candidate(
                    verse_ref=tok.verse_ref,
                    line_index=tok.line_index,
                    line_text=v4.lines[tok.line_index].text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=f"Line starts on postpositive '{lemma}'",
                    context=context,
                )
            )

    return candidates


def _build_context(v4, line_index: int) -> str:
    """Return up to 3 adjacent lines as context string."""
    lines = v4.lines
    start = max(0, line_index - 1)
    end = min(len(lines), line_index + 2)
    return " | ".join(lines[i].text for i in range(start, end))


def _format_markdown(all_candidates: List[Candidate]) -> str:
    """Render candidates as a grouped markdown report."""
    if not all_candidates:
        return "## R2 violations\n\nNo violations found.\n"

    lines = ["## R2 violations\n"]
    current_book = None
    for c in all_candidates:
        book_label = getattr(c, "book", "")
        if book_label != current_book:
            current_book = book_label
            if book_label:
                lines.append(f"\n### {book_label}\n")
        lines.append(
            f"- **{c.verse_ref}** (line {c.line_index}) [{c.tag}] {c.rationale}\n"
            f"  > {c.line_text}\n"
        )
        if getattr(c, "context", ""):
            lines.append(f"  *context:* {c.context}\n")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R2 validator: no dangling conjunctions at line end or start."
    )
    parser.add_argument("--book", help="Restrict to one book (e.g. 'mark')")
    parser.add_argument(
        "--chapter", type=int, help="Restrict to one chapter (requires --book)"
    )
    parser.add_argument("--output", help="Write report to this file path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    books_to_run = [args.book] if args.book else BOOKS
    all_candidates: List[Candidate] = []

    for book in books_to_run:
        chapters_to_run: list[int] = (
            [args.chapter] if args.chapter
            else list(range(1, 200))  # common module raises on non-existent chapters
        )
        for ch in chapters_to_run:
            try:
                candidates = check_book_chapter(book, ch)
                for c in candidates:
                    if not hasattr(c, "book"):
                        object.__setattr__(c, "book", book) if hasattr(c, "__setattr__") else None
                        try:
                            c.book = book  # type: ignore[attr-defined]
                        except AttributeError:
                            pass
                all_candidates.extend(candidates)
            except FileNotFoundError:
                break  # chapter doesn't exist — move on to next book
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[R2] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_markdown(all_candidates)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R2] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
