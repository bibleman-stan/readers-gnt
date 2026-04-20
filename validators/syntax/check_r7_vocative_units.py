"""
check_r7_vocative_units.py — Layer 1 validator for Rule R7.

R7: Multi-word vocative units are indivisible.
  If 2+ consecutive tokens that are each in the vocative case appear on
  different lines, that is a split vocative unit — always MALFORMED.

Layer 1 break-legality row 13.

Note: R7 is narrower than R18 (Layer 3).  R18 asks whether a vocative should
get its own line or merge appositively.  R7 asks only: if a vocative unit
spans multiple words, are all of them on the same line?

Edge case: one-token vocative (e.g. Σίμων in Σίμων Ἰωάννου where Ἰωάννου is
genitive) — only one token is Voc, so no multi-word vocative unit exists in
morphological terms.  R7 does not flag.  R18 / editorial judgment covers
whether the genitive modifier should join the vocative on the same line.
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import List

from validators.common import (
    Candidate,
    Token,
    emit_candidate,
    is_vocative,
    load_macula_chapter,
    load_morphgnt_book,
    load_v4_editorial,
    map_tokens_to_lines,
    strip_punctuation,
)

RULE_ID = "R7"
ERROR_CLASS = "MALFORMED"

BOOKS: list[str] = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1corinthians", "2corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1thessalonians", "2thessalonians",
    "1timothy", "2timothy", "titus", "philemon",
    "hebrews", "james", "1peter", "2peter",
    "1john", "2john", "3john", "jude", "revelation",
]

# MorphGNT slugs differ from Macula slugs for some books; common.py BOOK_SLUGS
# maps file-number -> short slug.  load_morphgnt_book accepts the same short
# slugs that morphgnt_lookup._load_book uses.
_MACULA_TO_MORPHGNT: dict[str, str] = {
    "matthew": "matt", "mark": "mark", "luke": "luke", "john": "john",
    "acts": "acts", "romans": "rom", "1corinthians": "1cor",
    "2corinthians": "2cor", "galatians": "gal", "ephesians": "eph",
    "philippians": "phil", "colossians": "col",
    "1thessalonians": "1thess", "2thessalonians": "2thess",
    "1timothy": "1tim", "2timothy": "2tim", "titus": "titus",
    "philemon": "phlm", "hebrews": "heb", "james": "jas",
    "1peter": "1pet", "2peter": "2pet", "1john": "1john",
    "2john": "2john", "3john": "3john", "jude": "jude",
    "revelation": "rev",
}

_VERSE_RE = re.compile(r"(\d+):(\d+)$")


def _parse_verse_ref(verse_ref: str) -> tuple[int, int]:
    """Extract (chapter, verse) ints from a verse_ref string like 'Matt 4:1'."""
    m = _VERSE_RE.search(verse_ref)
    if m:
        return int(m.group(1)), int(m.group(2))
    return (0, 0)


def _build_context(v4, line_index: int) -> str:
    """Return up to 3 adjacent lines as a context string."""
    lines = v4.lines
    start = max(0, line_index - 1)
    end = min(len(lines), line_index + 2)
    return " | ".join(lines[i].text for i in range(start, end))


def _find_vocative_runs(annotated: list[tuple[Token, str, str]]) -> list[list[tuple[Token, str, str]]]:
    """Return groups of >= 2 consecutive (token, pos, parsing) tuples where
    each token is in vocative case.

    annotated: list of (Token, pos_str, parsing_str) in document order.
    """
    runs: list[list[tuple[Token, str, str]]] = []
    current: list[tuple[Token, str, str]] = []
    for item in annotated:
        tok, pos, parsing = item
        if tok.line_index == -1:
            # Unmapped token — break any current run
            if len(current) >= 2:
                runs.append(current)
            current = []
            continue
        if is_vocative(pos, parsing):
            current.append(item)
        else:
            if len(current) >= 2:
                runs.append(current)
            current = []
    if len(current) >= 2:
        runs.append(current)
    return runs


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R7 violations in this chapter."""
    macula = load_macula_chapter(book, chapter)
    v4 = load_v4_editorial(book, chapter)
    tokens = map_tokens_to_lines(v4, macula)

    # Load MorphGNT for morphological (case) data.
    morphgnt_slug = _MACULA_TO_MORPHGNT.get(book, book)
    morphgnt_book = load_morphgnt_book(morphgnt_slug)

    # Build per-(chapter, verse) ordered list of (pos, parsing) from MorphGNT.
    # morphgnt_book[(ch, vs)] = [(word, pos, parsing), ...]
    morphgnt_verse: dict[tuple[int, int], list[tuple[str, str, str]]] = {
        (ch, vs): entries for (ch, vs), entries in morphgnt_book.items()
        if ch == chapter
    }

    # Annotate each Token with (pos, parsing) from MorphGNT.
    # Strategy: group tokens by (chapter, verse), then match by position within
    # that verse using a sequential counter — same alignment approach as common.py.
    annotated: list[tuple[Token, str, str]] = []
    verse_token_counter: dict[tuple[int, int], int] = {}

    for tok in tokens:
        ch, vs = _parse_verse_ref(tok.verse_ref)
        key = (ch, vs)
        idx = verse_token_counter.get(key, 0)
        verse_token_counter[key] = idx + 1

        entries = morphgnt_verse.get(key, [])
        if idx < len(entries):
            _, pos, parsing = entries[idx]
        else:
            pos, parsing = "", ""

        annotated.append((tok, pos, parsing))

    # Find consecutive vocative runs and flag any that are split across lines.
    candidates: List[Candidate] = []
    for run in _find_vocative_runs(annotated):
        line_indices = {t.line_index for t, _, _ in run}
        if len(line_indices) > 1:
            words = " ".join(strip_punctuation(t.word) for t, _, _ in run)
            first_tok = run[0][0]
            context = _build_context(v4, first_tok.line_index)
            # Report on the first line of the split run
            safe_line_index = first_tok.line_index
            candidates.append(
                emit_candidate(
                    verse_ref=first_tok.verse_ref,
                    line_index=safe_line_index,
                    line_text=v4.lines[safe_line_index].text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"Multi-word vocative '{words}' split across "
                        f"lines {sorted(line_indices)}"
                    ),
                    context=context,
                )
            )

    return candidates


def _format_markdown(all_candidates: List[Candidate]) -> str:
    """Render candidates as a grouped markdown report."""
    if not all_candidates:
        return "## R7 violations\n\nNo violations found.\n"

    lines = ["## R7 violations\n"]
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
        description="R7 validator: multi-word vocative units must not be split across lines."
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
                    f"[R7] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_markdown(all_candidates)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R7] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
