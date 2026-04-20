"""
check_r6_fixed_phrases.py — Layer 1 validator for Rule R6.

R6: Fixed phrases stay together.
  Certain multi-word Greek expressions are idiomatic units; splitting them
  across v4-editorial lines is MALFORMED.

Layer 1 break-legality rows 16, 17.

Only v4-editorial surface forms are needed — no Macula token mapping.
Longer phrases are checked before shorter sub-phrases to avoid duplicate flags.
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    load_v4_editorial,
    strip_punctuation,
)

RULE_ID = "R6"
ERROR_CLASS = "MALFORMED"

# Longer phrases must come before any phrase that is a sub-sequence of them.
# Each inner list is a sequence of NFC-normalized, punctuation-stripped tokens
# (lower-cased for matching).  Elision forms (κατ', καθ') have the apostrophe
# stripped by strip_punctuation already, so we store the bare stem.
FIXED_PHRASES: list[list[str]] = [
    ["εἰς", "τοὺς", "αἰῶνας", "τῶν", "αἰώνων"],  # 5-token; before 3-token sub-phrase
    ["εἰς", "τὸν", "αἰῶνα"],
    ["ἐπὶ", "τὸ", "αὐτό"],
    ["διὰ", "τοῦτο"],
    ["κατ", "ἰδίαν"],   # κατ' → κατ after apostrophe strip
    ["καθ", "ἡμέραν"],  # καθ' → καθ after apostrophe strip
    ["ἐν", "χριστῷ"],   # lower-cased for match; original is Χριστῷ
]

BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]


def _normalize(word: str) -> str:
    """Strip punctuation, NFC-normalize, and lower-case for phrase matching."""
    return strip_punctuation(unicodedata.normalize("NFC", word)).lower()


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R6 violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)

    # Build a flat token list: (norm_word, line_index, position_in_line, verse_ref)
    flat: list[tuple[str, int, int, str]] = []
    for vline in v4.lines:
        for pos, raw_tok in enumerate(vline.tokens):
            flat.append((_normalize(raw_tok), vline.line_index, pos, vline.verse_ref))

    n = len(flat)
    candidates: List[Candidate] = []

    # Track positions already covered by a longer-phrase flag to avoid
    # double-firing a sub-phrase on the same span.
    flagged_starts: set[int] = set()

    for phrase in FIXED_PHRASES:
        ph_len = len(phrase)

        for i in range(n - ph_len + 1):
            # Check whether the phrase matches starting at position i
            if any(flat[i + k][0] != phrase[k] for k in range(ph_len)):
                continue

            # Skip if already covered by a longer phrase flagged at the same start
            if i in flagged_starts:
                continue

            # All tokens match — check whether they share a line_index
            line_indices = [flat[i + k][1] for k in range(ph_len)]
            if len(set(line_indices)) == 1:
                continue  # all on the same line — fine

            # Split detected: flag at the line of the first token
            first_line_idx = line_indices[0]
            verse_ref = flat[i][3]
            line_text = v4.lines[first_line_idx].text

            # Build context: up to 2 lines after the first token's line
            ctx_end = min(len(v4.lines), first_line_idx + ph_len + 1)
            context = " | ".join(v4.lines[j].text for j in range(first_line_idx, ctx_end))

            # Reconstruct a readable display form (using raw tokens from v4 lines)
            display_tokens = []
            for k in range(ph_len):
                li = line_indices[k]
                pi = flat[i + k][2]
                display_tokens.append(v4.lines[li].tokens[pi])
            phrase_display = " ".join(display_tokens)

            candidates.append(
                emit_candidate(
                    verse_ref=verse_ref,
                    line_index=first_line_idx,
                    line_text=line_text,
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"Fixed phrase '{phrase_display}' split across lines"
                    ),
                    context=context,
                )
            )
            flagged_starts.add(i)

    return candidates


def _format_markdown(all_candidates: List[Candidate]) -> str:
    """Render candidates as a grouped markdown report."""
    if not all_candidates:
        return "## R6 violations\n\nNo violations found.\n"

    lines = ["## R6 — fixed phrases split across lines\n"]
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
        description="R6 validator: fixed Greek phrases must not be split across lines."
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
                    f"[R6] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_markdown(all_candidates)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R6] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
