"""
check_r3_no_line_end_article.py — Layer 1 validator for Rule R3.

R3: A line must not end on a Greek article (ὁ, ἡ, τό and all declined forms).
    The article is syntactically bound to its noun phrase; splitting them is
    always MALFORMED.

Two checks (Layer 1 break-legality rows 3 and 4):
  CHECK 1 — Line-end DET: last token of a line has POS == DET.
  CHECK 2 — DET/N cross-line split: adjacent tokens span a line boundary where
             token_a.pos == DET and token_b.pos in {NOUN, PROPN, ADJ}.

Edge cases handled:
  Substantival adjectives (e.g. οἱ ἀγαθοί): check 2 covers DET + ADJ splits,
  so "article separated from its substantival adjective head" is flagged.

  Genitive adnominal splits (τοῦ θεοῦ following a noun on the next line): NOT
  an R3 violation. The article is with its own noun; only the genitive phrase
  is displaced. Check 2 only fires when DET and its immediately following
  N/PROPN/ADJ are on DIFFERENT lines — it does not look back at prior lines.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict, deque
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    load_morphgnt_book,
    parse_chapter_file,
    strip_punctuation,
)

RULE_ID = "R3"
ERROR_CLASS = "MALFORMED"

# MorphGNT POS → simplified POS used in checks
# RA = article (determiner), N- = noun, A- = adjective
# Proper nouns share POS "N-" in MorphGNT; we treat them as NOUN for the check.
_POS_MAP = {
    "RA": "DET",
    "N-": "NOUN",
    "A-": "ADJ",
}
_NOUN_LIKE = frozenset({"NOUN", "ADJ"})  # includes PROPN (also N-) and ADJ


def _bare(w: str) -> str:
    """Strip punctuation AND diacritics for accent-tolerant matching.

    MorphGNT and v4-editorial occasionally differ in accent (e.g. νυκτὶ vs
    νυκτί). Stripping all combining marks (category Mn) after NFD decomposition
    gives a bare consonant+vowel string suitable for matching identity.
    """
    nfd = unicodedata.normalize("NFD", strip_punctuation(w))
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn").lower()

BOOKS: list[tuple[str, int]] = [
    ("matt", 28), ("mark", 16), ("luke", 24), ("john", 21), ("acts", 28),
    ("rom", 16), ("1cor", 16), ("2cor", 13), ("gal", 6), ("eph", 6),
    ("phil", 4), ("col", 4), ("1thess", 5), ("2thess", 3),
    ("1tim", 6), ("2tim", 4), ("titus", 3), ("phlm", 1),
    ("heb", 13), ("jas", 5), ("1pet", 5), ("2pet", 3),
    ("1john", 5), ("2john", 1), ("3john", 1), ("jude", 1), ("rev", 22),
]


# ---------------------------------------------------------------------------
# Token binding: map MorphGNT verse tokens onto v4-editorial line indices
# ---------------------------------------------------------------------------

def _bind_verse_tokens(lines: list[str], morph_tokens: list[tuple]) -> list[dict]:
    """Assign MorphGNT tokens to line indices via sequential-consume queue.

    morph_tokens: list of (word, pos, parsing) from MorphGNT for the verse.
    Returns list of dicts with keys: word, pos_raw, pos, line_index, position_in_line.

    position_in_line is the rank of the token among MAPPED tokens on its line
    (0-based), so it stays consistent with tokens_per_line counts.
    """
    # Build ordered queue of (line_idx, bare_word) from v4 lines
    # bare_word is diacritic-stripped for accent-tolerant matching
    v4_queue: deque[tuple[int, str]] = deque()
    for line_idx, raw_line in enumerate(lines):
        for token in raw_line.split():
            bw = _bare(token)
            if bw:
                v4_queue.append((line_idx, bw))

    result: list[dict] = []
    for word, pos_raw, parsing in morph_tokens:
        cw = strip_punctuation(word)
        bw = _bare(word)
        if not bw:
            continue
        mapped_pos = _POS_MAP.get(pos_raw, pos_raw)
        # Scan the v4 queue for a matching surface form
        lookahead_buf: list[tuple[int, str]] = []
        matched = False
        for _ in range(6):  # lookahead up to 6 positions
            if not v4_queue:
                break
            entry = v4_queue.popleft()
            if entry[1] == bw:
                result.append({
                    "word": cw, "pos_raw": pos_raw, "pos": mapped_pos,
                    "line_index": entry[0], "position_in_line": -1,  # set in pass 2
                })
                matched = True
                # Restore remaining lookahead items to front of queue
                for item in reversed(lookahead_buf):
                    v4_queue.appendleft(item)
                break
            else:
                lookahead_buf.append(entry)
        if not matched:
            # Restore all lookahead items and emit unmapped token
            for item in reversed(lookahead_buf):
                v4_queue.appendleft(item)
            result.append({
                "word": cw, "pos_raw": pos_raw, "pos": mapped_pos,
                "line_index": -1, "position_in_line": -1,
            })

    # Pass 2: assign position_in_line as rank among mapped tokens per line
    line_rank: dict[int, int] = {}
    for tok in result:
        li = tok["line_index"]
        if li >= 0:
            tok["position_in_line"] = line_rank.get(li, 0)
            line_rank[li] = line_rank.get(li, 0) + 1

    return result


# ---------------------------------------------------------------------------
# Core chapter check
# ---------------------------------------------------------------------------

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return R3 violation candidates for one book/chapter."""
    morph_book = load_morphgnt_book(book)
    if not morph_book:
        return []

    try:
        v4_path = _find_v4_path(book, chapter)
    except FileNotFoundError:
        return []
    verses = parse_chapter_file(v4_path)

    # Build chapter-level line_index offset: track cumulative line count
    chapter_line_offset = 0
    chapter_line_texts: dict[int, str] = {}  # chapter-level line_index → text
    chapter_verse_refs: dict[int, str] = {}  # chapter-level line_index → verse_ref
    book_display = book[0].upper() + book[1:]
    for verse in verses:
        ch_str, vs_str = verse["ch"], verse["vs"]
        vref = f"{book_display} {ch_str}:{vs_str}"
        for local_idx, raw_line in enumerate(verse["lines"]):
            chapter_line_offset_here = chapter_line_offset + local_idx
            chapter_line_texts[chapter_line_offset_here] = raw_line.strip()
            chapter_verse_refs[chapter_line_offset_here] = vref
        chapter_line_offset += len(verse["lines"])

    # Flatten bound tokens across the chapter, preserving chapter-level line index
    all_tokens: list[dict] = []
    chapter_line_cursor = 0
    for verse in verses:
        ch, vs = verse["ch"], verse["vs"]
        morph_tokens = morph_book.get((ch, vs), [])
        bound = _bind_verse_tokens(verse["lines"], morph_tokens)
        # Shift local line_index by chapter_line_cursor
        for tok in bound:
            if tok["line_index"] >= 0:
                tok["line_index"] += chapter_line_cursor
        all_tokens.extend(bound)
        chapter_line_cursor += len(verse["lines"])

    # Count tokens per (chapter-level) line for position_in_line checks
    tokens_per_line: dict[int, int] = defaultdict(int)
    for tok in all_tokens:
        if tok["line_index"] >= 0:
            tokens_per_line[tok["line_index"]] += 1

    candidates: List[Candidate] = []
    mapped = [t for t in all_tokens if t["line_index"] >= 0]

    for i, tok in enumerate(mapped):
        line_idx = tok["line_index"]
        line_len = tokens_per_line[line_idx]

        # CHECK 1: line-end DET
        if tok["pos"] == "DET" and tok["position_in_line"] == line_len - 1:
            vref = chapter_verse_refs.get(line_idx, "")
            candidates.append(emit_candidate(
                verse_ref=vref,
                line_index=line_idx,
                line_text=chapter_line_texts.get(line_idx, ""),
                rule=RULE_ID,
                tag="STRONG-MERGE",
                error_class=ERROR_CLASS,
                rationale=f"Line ends on article {tok['word']}",
            ))

        # CHECK 2: DET + N/ADJ split across a line boundary
        if i + 1 < len(mapped):
            next_tok = mapped[i + 1]
            if (
                tok["pos"] == "DET"
                and next_tok["pos"] in _NOUN_LIKE
                and tok["line_index"] != next_tok["line_index"]
            ):
                vref = chapter_verse_refs.get(line_idx, "")
                candidates.append(emit_candidate(
                    verse_ref=vref,
                    line_index=line_idx,
                    line_text=chapter_line_texts.get(line_idx, ""),
                    rule=RULE_ID,
                    tag="STRONG-MERGE",
                    error_class=ERROR_CLASS,
                    rationale=(
                        f"Article {tok['word']} separated from its head "
                        f"{next_tok['word']} ({next_tok['pos']}) by line break"
                    ),
                ))

    return candidates


def _find_v4_path(book: str, chapter: int) -> str:
    """Locate the v4-editorial .txt file; raise FileNotFoundError if absent."""
    import os
    _here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(_here))
    v4_root = os.path.join(repo, "data", "text-files", "v4-editorial")
    for entry in os.listdir(v4_root):
        parts = entry.split("-", 1)
        slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else entry
        if slug == book:
            fpath = os.path.join(v4_root, entry, f"{book}-{chapter:02d}.txt")
            if os.path.exists(fpath):
                return fpath
    raise FileNotFoundError(f"v4-editorial not found: {book} ch.{chapter}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="R3 validator: no line-end article, no DET/N cross-line split."
    )
    parser.add_argument("--book", help="Restrict to one book slug (e.g. mark)")
    parser.add_argument("--chapter", type=int, help="Restrict to one chapter (requires --book)")
    parser.add_argument("--output", help="Write markdown report to this path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    books_to_run = [(args.book, 999)] if args.book else BOOKS
    all_candidates: List[Candidate] = []

    for book, max_ch in books_to_run:
        chapters = [args.chapter] if args.chapter else range(1, max_ch + 1)
        for ch in chapters:
            try:
                all_candidates.extend(check_book_chapter(book, ch))
            except FileNotFoundError:
                break
            except Exception as exc:
                print(f"[R3] WARNING: {book} ch.{ch} — {exc}", file=sys.stderr)

    report_lines = [f"# R3 violations — {len(all_candidates)} total\n"]
    for c in all_candidates:
        report_lines.append(
            f"- **{c.verse_ref}** line {c.line_index} [{c.tag}] {c.rationale}\n"
            f"  > {c.line_text}\n"
        )
    report = "\n".join(report_lines)

    if args.output:
        import os; os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R3] {len(all_candidates)} violations → {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
