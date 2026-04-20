"""
check_r5_periphrastic.py — Layer 1 validator for Rule R5.

R5: Never split periphrastic constructions.
  A periphrastic verb is a single verbal unit (auxiliary + non-finite head).
  Splitting the pair across lines is always MALFORMED.

Three construction types:
  1. εἰμί (finite indicative) + participle  — e.g. ἦν διδάσκων
  2. μέλλω (finite) + infinitive             — e.g. μέλλει ἔρχεσθαι
  3. ἄρχομαι (finite) + infinitive           — e.g. ἤρξατο διδάσκειν

Layer 1 break-legality rows 8, 9, 10.
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

RULE_ID = "R5"
ERROR_CLASS = "MALFORMED"

BOOKS: list[str] = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1corinthians", "2corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1thessalonians", "2thessalonians",
    "1timothy", "2timothy", "titus", "philemon",
    "hebrews", "james", "1peter", "2peter",
    "1john", "2john", "3john", "jude", "revelation",
]

# Finite mood markers (substring match against morph or mood attribute).
_FINITE = frozenset({"ind", "imp", "sub", "opt"})


def _is_finite(tok) -> bool:
    s = ((getattr(tok, "mood", "") or "") + (getattr(tok, "morph", "") or "")).lower()
    return any(m in s for m in _FINITE)


def _is_participle(tok) -> bool:
    s = ((getattr(tok, "morph", "") or "") + (getattr(tok, "mood", "") or "")
         + (getattr(tok, "role", "") or "")).lower()
    return "part" in s


def _is_infinitive(tok) -> bool:
    s = ((getattr(tok, "morph", "") or "") + (getattr(tok, "mood", "") or "")
         + (getattr(tok, "role", "") or "")).lower()
    return "inf" in s


def _find_ahead(tokens, start: int, predicate, window: int):
    """Scan up to `window` tokens ahead for predicate match.
    Returns (token, certain) — certain=True if within half the window."""
    half = window // 2
    for j in range(start + 1, min(start + 1 + window, len(tokens))):
        if predicate(tokens[j]):
            return tokens[j], (j - start) <= half
    return None, False


def _build_context(v4, line_index: int) -> str:
    lines = v4.lines
    start = max(0, line_index - 1)
    end = min(len(lines), line_index + 2)
    return " | ".join(lines[i].text for i in range(start, end))


# (lemma, non-finite predicate, window, description)
_CONSTRUCTIONS = [
    ("εἰμί",    _is_participle,  6, "participle"),
    ("μέλλω",   _is_infinitive,  4, "infinitive"),
    ("ἄρχομαι", _is_infinitive,  4, "infinitive"),
]


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R5 violations in this chapter."""
    macula = load_macula_chapter(book, chapter)
    v4 = load_v4_editorial(book, chapter)
    tokens = map_tokens_to_lines(v4, macula)

    candidates: List[Candidate] = []

    for i, tok in enumerate(tokens):
        if getattr(tok, "pos", "") not in {"VERB", "AUX"}:
            continue
        if not _is_finite(tok):
            continue
        lemma = strip_punctuation(getattr(tok, "lemma", "") or "")

        for aux_lemma, nonfinite_pred, window, head_label in _CONSTRUCTIONS:
            if lemma != aux_lemma:
                continue
            partner, certain = _find_ahead(tokens, i, nonfinite_pred, window)
            if partner is None or partner.line_index == tok.line_index:
                break  # no split — no violation
            tag = "STRONG-MERGE" if certain else "REVIEW-REQUIRED"
            candidates.append(
                emit_candidate(
                    verse_ref=tok.verse_ref,
                    line_index=tok.line_index,
                    line_text=v4.lines[tok.line_index].text,
                    rule=RULE_ID,
                    tag=tag,
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"{aux_lemma} ({tok.word}) split from {head_label} "
                        f"({partner.word}) across lines"
                    ),
                    context=_build_context(v4, tok.line_index),
                )
            )
            break  # one construction matched — don't double-check

    return candidates


def _format_markdown(all_candidates: List[Candidate]) -> str:
    if not all_candidates:
        return "## R5 violations\n\nNo violations found.\n"
    lines = ["## R5 violations\n"]
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
        description="R5 validator: no split periphrastic constructions."
    )
    parser.add_argument("--book", help="Restrict to one book (e.g. 'mark')")
    parser.add_argument("--chapter", type=int, help="Restrict to one chapter (requires --book)")
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
                print(f"[R5] WARNING: {book} ch.{ch} skipped — {exc}", file=sys.stderr)

    report = _format_markdown(all_candidates)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R5] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
