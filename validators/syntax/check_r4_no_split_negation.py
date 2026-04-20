"""
check_r4_no_split_negation.py — Layer 1 validator for Rule R4.

R4: Never split negation from what it negates.
  A line ending on a negation particle (with the negated element on the next
  line) is always MALFORMED.

Layer 1 break-legality rows 5, 6, 7 — negation at line end requires merge.

Edge case: a one-token line that IS the negation (postposed answer-particle
"no" / echo use) is not a violation — skip when len(line.tokens) == 1.
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
)

RULE_ID = "R4"
ERROR_CLASS = "MALFORMED"

# Lemmas that are negation particles (covers full and apocopated forms via
# shared lemma, plus compounds).
NEG_LEMMAS: frozenset[str] = frozenset(
    {"οὐ", "μή", "οὐδέ", "μηδέ", "οὐκέτι", "μηκέτι", "μήποτε", "οὐχί", "μήτι"}
)

# Surface forms: handles apocopated forms (οὐκ, οὐχ) whose lemma resolves to
# οὐ in most taggers, but listed here as an explicit safety net.
NEG_SURFACE_FORMS: frozenset[str] = frozenset(
    {"οὐ", "οὐκ", "οὐχ", "μή", "οὐδέ", "μηδέ", "οὐκέτι", "μηκέτι", "μήποτε"}
)

# POS tags under which negation particles appear in Macula data.
NEG_POS: frozenset[str] = frozenset({"PART", "ADV"})

BOOKS: list[str] = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1corinthians", "2corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1thessalonians", "2thessalonians",
    "1timothy", "2timothy", "titus", "philemon",
    "hebrews", "james", "1peter", "2peter",
    "1john", "2john", "3john", "jude", "revelation",
]


def _is_negation(tok) -> bool:
    """Return True if token is a negation particle by lemma or surface form."""
    lemma = strip_punctuation(tok.lemma) if hasattr(tok, "lemma") else ""
    surface = strip_punctuation(tok.word) if hasattr(tok, "word") else ""
    pos_match = tok.pos in NEG_POS
    return (pos_match and lemma in NEG_LEMMAS) or surface in NEG_SURFACE_FORMS


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R4 violations in this chapter."""
    macula = load_macula_chapter(book, chapter)
    v4 = load_v4_editorial(book, chapter)
    tokens = map_tokens_to_lines(v4, macula)

    # Count tokens per line.
    line_token_count: dict[int, int] = {}
    for tok in tokens:
        line_token_count[tok.line_index] = line_token_count.get(tok.line_index, 0) + 1

    candidates: List[Candidate] = []

    for tok in tokens:
        line_len = line_token_count.get(tok.line_index, 1)

        # Edge case: one-token line = postposed answer particle; not a violation.
        if line_len == 1:
            continue

        # Violation: negation is last token of a multi-token line.
        if tok.position_in_line == line_len - 1 and _is_negation(tok):
            surface = strip_punctuation(tok.word) if hasattr(tok, "word") else tok.lemma
            context = _build_context(v4, tok.line_index)
            candidates.append(
                emit_candidate(
                    verse_ref=tok.verse_ref,
                    line_index=tok.line_index,
                    line_text=v4.lines[tok.line_index].text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"Line ends on negation particle '{surface}'; "
                        "separated from its scope"
                    ),
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
        return "## R4 violations\n\nNo violations found.\n"

    lines = ["## R4 violations\n"]
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
        description="R4 validator: no negation particle stranded at line end."
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
            [args.chapter] if args.chapter else list(range(1, 200))
        )
        for ch in chapters_to_run:
            try:
                candidates = check_book_chapter(book, ch)
                for c in candidates:
                    try:
                        c.book = book  # type: ignore[attr-defined]
                    except AttributeError:
                        pass
                all_candidates.extend(candidates)
            except FileNotFoundError:
                break
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[R4] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_markdown(all_candidates)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R4] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
