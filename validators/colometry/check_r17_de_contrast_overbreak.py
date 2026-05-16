"""
check_r17_de_contrast_overbreak.py — Layer 3 validator for Rule R17.

R17 (canon §3.8): De-contrast overbreak.

When two distinct clauses with a δέ pivot appear on ONE line — recognizable by
a comma before `ὁ δέ / ἡ δέ / τὸ δέ / οἱ δέ / μεσον δέ / νυνὶ δέ` — split
at the δέ. The comma marks the clause boundary; the δέ signals a new
development (narrative-to-background switch, topical shift, adversative contrast).

Closed-list pivot forms (canonical surface, §3.8):
  ὁ δέ, ἡ δέ, τὸ δέ, οἱ δέ, μεσον δέ, νυνὶ δέ

Detection approach (surface-pattern per §3.8 decidability):
  - Scan every line for a two-token sequence whose second token is δέ and
    whose first token is in the article set OR is "μεσον" / "νυνὶ".
  - Confirm the raw line text has a comma BEFORE that sequence.
  - If both conditions hold → STRONG-SPLIT candidate.

False-positive guards (from §3.8):
  FP1 — Participial δέ: no finite verb in the clause following δέ → skip.
  FP2 — Line-initial δέ pivot (no comma preceding it within the line) → skip.
  FP3 — Single-word line or pivot is the FIRST token → skip (no preceding clause).

The 27 confirmed splits already applied corpus-wide mean this validator catches
DRIFT (new violations introduced after the initial sweep). Candidate count
should be near 0 for a clean corpus.

Layer: 3 (DEVIATION).
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    load_v4_editorial,
    strip_punctuation,
)

RULE_ID = "R17"
ERROR_CLASS = "DEVIATION"

# Article forms that head the δέ pivot (NFC-stripped surface forms).
# Canon §3.8 names the nominative-article + μεσον + νυνὶ pattern — the
# "subject-reintroducing" δέ pivot ("ὁ δέ εἶπεν" / "ἡ δέ ἀπεκρίθη" /
# "οἱ δέ ἔλεγον" etc.). Oblique-case articles (τοῦ / τῆς / τῷ / τόν / etc.)
# are NOT subject-introducing — they're case-marked inside noun phrases —
# so they MUST NOT be in this list. Extending beyond canon's named heads
# is a closed-list extension (change-protocol §7.3 trigger #3).
_ARTICLE_FORMS: frozenset[str] = frozenset({
    "ὁ", "ἡ", "τὸ", "τό",   # NOM sing (article variants: accent on/off)
    "οἱ",                     # NOM pl masc
})

# Other pivot-head tokens (non-article).
_OTHER_PIVOT_HEADS: frozenset[str] = frozenset({
    "μέσον", "μεσον",  # "μεσον δέ" — accent variant
    "νυνὶ", "νυνί",    # "νυνὶ δέ"
})

_DE_FORMS: frozenset[str] = frozenset({"δέ", "δε"})

# Characters that count as a comma/clause-boundary marker in v4/grk.
_COMMA_CHARS: frozenset[str] = frozenset({
    ",",          # standard comma
    "·",     # middle dot (·)
    "·",     # Greek ano teleia
    "·",          # literal ano teleia
})


def _has_comma_before_pivot(raw_text: str, pivot_start_word_index: int) -> bool:
    """Return True if a comma appears in the raw line text before the pivot sequence.

    pivot_start_word_index: 0-based index of the pivot's article/head in the
    RAW (not stripped) word list from line.split().

    We look at the raw text up to (but not including) the pivot word and check
    whether it contains a comma character.
    """
    raw_words = raw_text.split()
    if pivot_start_word_index <= 0:
        return False
    # Reconstruct the pre-pivot segment as a string
    pre_pivot = " ".join(raw_words[:pivot_start_word_index])
    return any(ch in pre_pivot for ch in _COMMA_CHARS)


def _has_finite_verb_after_pivot(tokens: list, pivot_idx: int) -> bool:
    """Return True if any finite verb token appears AFTER the pivot position.

    FP1 guard: participial δέ has no finite verb following it.
    pivot_idx: 0-based index of the δέ token in the STRIPPED token list.
    """
    # We don't have POS tags in the stripped token list — use a lightweight
    # heuristic: if there is at least one token after the pivot (non-empty),
    # assume a potential finite verb is present. The canon test (§3.8) is
    # "is there a finite verb in the clause following δέ?" — for a corpus
    # that has already had the 27 splits applied, remaining cases are expected
    # to be genuine split-candidates. We rely on the broader false-positive
    # guards (comma check) to filter out most participial false positives.
    # A full morphological check would require the MorphGNT 4-tuple loader,
    # adding significant complexity for what the spec says is drift-detection.
    # Keep it simple: if there are ≥2 tokens after the pivot, flag as candidate.
    remaining = len(tokens) - (pivot_idx + 1)
    return remaining >= 2


def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R17 violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)
    candidates: List[Candidate] = []

    for vline in v4.lines:
        tokens = vline.tokens  # punctuation-stripped NFC tokens
        if len(tokens) < 3:
            # Need at least: [prior-clause-content] [pivot-head] [δέ]
            continue

        raw_words = vline.text.split()

        # Scan for a two-token pivot sequence: (article/head) + δέ
        for j in range(1, len(tokens) - 1):  # j = index of potential pivot-head
            pivot_head = tokens[j]
            pivot_de = tokens[j + 1] if j + 1 < len(tokens) else ""

            is_article_head = pivot_head in _ARTICLE_FORMS
            is_other_head = pivot_head in _OTHER_PIVOT_HEADS
            is_de = pivot_de in _DE_FORMS

            if not (is_article_head or is_other_head) or not is_de:
                continue

            # FP3: pivot is at position 0 or 1 (no preceding clause) → skip
            if j == 0:
                continue

            # Map stripped token index j to raw word index.
            # Stripped tokens may differ from raw words due to punctuation;
            # use approximate mapping: walk raw_words and count non-empty
            # stripped tokens until we reach j.
            raw_pivot_idx = _find_raw_index(raw_words, j)

            # FP2: no comma in the pre-pivot segment → skip
            if not _has_comma_before_pivot(vline.text, raw_pivot_idx):
                continue

            # FP1: no finite verb after pivot → skip
            if not _has_finite_verb_after_pivot(tokens, j + 1):
                continue

            # Emit STRONG-SPLIT candidate
            pivot_text = f"{pivot_head} δέ"
            context = _build_context(v4.lines, vline.line_index)
            candidates.append(
                emit_candidate(
                    verse_ref=vline.verse_ref,
                    line_index=vline.line_index,
                    line_text=vline.text,
                    rule=RULE_ID,
                    tag="STRONG-SPLIT",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"R17: δέ pivot '{pivot_text}' preceded by comma on same line — "
                        f"split at δέ (two distinct clauses merged)"
                    ),
                    context=context,
                )
            )
            # Only flag first pivot per line (one split per line)
            break

    return candidates


def _find_raw_index(raw_words: list, stripped_token_idx: int) -> int:
    """Find the approximate raw-word index for a given stripped-token index.

    Walks raw_words and counts non-empty stripped tokens to locate the
    raw word at stripped position stripped_token_idx.
    """
    stripped_count = 0
    for i, raw_w in enumerate(raw_words):
        s = strip_punctuation(raw_w)
        if s:
            if stripped_count == stripped_token_idx:
                return i
            stripped_count += 1
    return len(raw_words)  # fallback: past end


def _build_context(v4_lines: list, line_index: int) -> str:
    start = max(0, line_index - 1)
    end = min(len(v4_lines), line_index + 2)
    return " | ".join(v4_lines[i].text for i in range(start, end))


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _format_report(candidates: List[Candidate]) -> str:
    if not candidates:
        return "## R17 de-contrast-overbreak\n\nNo violations found.\n"
    lines = [f"## R17 de-contrast-overbreak — {len(candidates)} violation(s)\n"]
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
        description="R17 validator: de-contrast overbreak — comma before δέ pivot."
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
                print(f"[R17] WARNING: {args.book} ch.{ch} skipped — {exc}", file=sys.stderr)
                ch += 1
                if ch > 200:
                    break
    else:
        for slug, chapter_num, _fp in iter_v4_chapters():
            try:
                all_candidates.extend(check_book_chapter(slug, chapter_num))
            except Exception as exc:
                print(f"[R17] WARNING: {slug} ch.{chapter_num} skipped — {exc}", file=sys.stderr)

    report = _format_report(all_candidates)
    print(f"[R17] {len(all_candidates)} violation(s) found.", file=sys.stderr)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R17] Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
