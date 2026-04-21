"""
check_r18_vocative.py — Layer 3 validator for Rule R18 (canon §3.9).

R18 three-way refined treatment:
  DEFAULT  — vocative owns its line (verse-initial, verse-final, post-speech-intro,
             stacked parallel).
  SUBJECT-APPOSITIVE MERGE — vocative names implicit subject of a 2p finite verb.
  OBJECT-APPOSITIVE MERGE  — vocative restates an explicit 2p pronoun (σύ/ὑμεῖς).
  DISCOURSE-FRAME CLUSTER  — frame particle (Loipon etc.) + vocative co-lined: OK.

Violation (DEVIATION / STRONG-SPLIT): vocative + non-2p finite verb + no 2p element.

Usage:
  PYTHONIOENCODING=utf-8 py -3 -m validators.colometry.check_r18_vocative [--book SLUG] [--chapter N] [--output PATH]
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    load_morphgnt_book_with_lemma,
    parse_chapter_file,
    strip_punctuation,
    is_finite_verb,
    is_2p_verb,
    is_vocative,
    is_2p_pronoun,
)

RULE_ID = "R18"
ERROR_CLASS = "DEVIATION"   # Layer 3 editorial

# ─── Book slug table (matches v4-editorial dir names) ────────────────────────

_BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]

# ─── Discourse-frame markers (canon §3.9 cluster rule) ───────────────────────
# Frame particle as first token on a vocative line = correctly-formed cluster.

_FRAME_LEMMAS: frozenset[str] = frozenset({
    "λοιπόν", "λοιπός",   # Loipon / To loipon / Loipon oun
    "τοῦτο",              # Tauta de patterns
    "κἀγώ",               # Kago
    "οὖν",                # Loipon oun (postpositive — guard fires only at pos 0)
})


_morph_cache: dict[str, dict] = {}


def _get_morph(slug: str) -> dict:
    if slug not in _morph_cache:
        # Use the lemma-aware loader so is_2p_pronoun (lemma == "σύ") fires correctly.
        _morph_cache[slug] = load_morphgnt_book_with_lemma(slug)
    return _morph_cache[slug]


# ─── Line-level classifier ────────────────────────────────────────────────────

def _classify_line(
    text: str,
    words: list[tuple],  # (surface, pos, parsing, lemma)
) -> tuple[list, list, list, list]:
    """Return (vocs, fins_non2p, twop_verbs, twop_pronouns) as (word, lemma) lists."""
    pool: dict[str, list] = defaultdict(list)
    for w, pos, p, lemma in words:
        pool[w].append((pos, p, lemma))

    vocs: list = []
    fins_non2p: list = []
    twop_v: list = []
    twop_p: list = []

    for raw in text.split():
        c = strip_punctuation(raw)
        if c and c in pool and pool[c]:
            pos, p, lemma = pool[c].pop(0)
            if is_vocative(pos, p):
                vocs.append((c, lemma))
            if is_2p_verb(pos, p):
                twop_v.append((c, lemma))
            elif is_finite_verb(pos, p):
                fins_non2p.append((c, lemma))
            if is_2p_pronoun(pos, p, lemma, surface=c):
                twop_p.append((c, lemma))

    return vocs, fins_non2p, twop_v, twop_p


def _has_discourse_frame_prefix(text: str, words: list[tuple]) -> bool:
    """True if first token on the line is a sentence-initial discourse-frame marker."""
    tokens = text.split()
    if not tokens:
        return False
    first = strip_punctuation(tokens[0])
    pool: dict[str, list] = defaultdict(list)
    for w, pos, p, lemma in words:
        pool[w].append((pos, p, lemma))
    if first in pool and pool[first]:
        _, _, lemma = pool[first][0]
        return lemma in _FRAME_LEMMAS
    # Surface-form fallback when lemma lookup fails
    return first in {"Λοιπόν", "λοιπόν", "Λοιπός", "λοιπός", "κἀγώ"}


# ─── Chapter-level checker ────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return R18 DEVIATION candidates for one chapter."""
    morph = _get_morph(book)

    # Locate the chapter file via iter_v4_chapters
    chapter_path: str | None = None
    for slug, ch_num, fp in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_path = fp
            break
    if chapter_path is None:
        raise FileNotFoundError(
            f"v4-editorial chapter not found: book={book!r} chapter={chapter}"
        )

    verses = parse_chapter_file(chapter_path)
    candidates: List[Candidate] = []
    global_line_index = 0  # track 0-based line index across the chapter

    # Stacked-parallel-vocative tracking: True if the previous line's first
    # token was a vocative (canon §3.9 boundary: τεκνία / πατέρες / νεανίσκοι).
    prev_line_starts_with_voc: bool = False

    for verse in verses:
        ch_num = verse["ch"]
        vs_num = verse["vs"]
        verse_words = morph.get((ch_num, vs_num), [])
        normalized_words: list[tuple] = []
        for entry in verse_words:
            if len(entry) >= 4:
                w, pos, p, lemma = entry[0], entry[1], entry[2], entry[3]
            elif len(entry) == 3:
                w, pos, p = entry; lemma = ""
            else:
                continue
            normalized_words.append((strip_punctuation(w), pos, p, lemma))

        if not normalized_words:
            global_line_index += len(verse["lines"])
            prev_line_starts_with_voc = False
            continue

        for line in verse["lines"]:
            vocs, fins, twop_v, twop_p = _classify_line(line, normalized_words)

            # Check whether this line's first token is a vocative (for stacked-stack tracking).
            line_first_token_is_voc = bool(vocs) and bool(line.split()) and \
                strip_punctuation(line.split()[0]) in {w for w, _ in vocs}

            if vocs and fins and not twop_v and not twop_p:
                # Guard 1: discourse-frame cluster (Loipon + vocative).
                # Guard 2: stacked parallel vocatives — if prior line started with a
                #           vocative, this line is part of an address stack; do not flag.
                if (not _has_discourse_frame_prefix(line, normalized_words)
                        and not prev_line_starts_with_voc):
                    voc_str = ", ".join(f"{w}({l})" for w, l in vocs)
                    fin_str = ", ".join(f"{w}({l})" for w, l in fins)
                    book_cap = book[0].upper() + book[1:]
                    verse_ref = f"{book_cap} {ch_num}:{vs_num}"
                    candidates.append(
                        emit_candidate(
                            verse_ref=verse_ref,
                            line_index=global_line_index,
                            line_text=line.strip(),
                            rule=RULE_ID,
                            tag="STRONG-SPLIT",
                            error_class=ERROR_CLASS,
                            rationale=(
                                f"R18 default violated: vocative [{voc_str}] shares line "
                                f"with non-2p finite verb [{fin_str}] but has no 2p element "
                                f"(verb or pronoun) that would justify subject-appositive or "
                                f"object-appositive merge (canon §3.9)."
                            ),
                        )
                    )

            prev_line_starts_with_voc = line_first_token_is_voc
            global_line_index += 1

    return candidates


# ─── Report formatter ─────────────────────────────────────────────────────────

def _format_report(all_candidates: List[Candidate]) -> str:
    if not all_candidates:
        return "## R18 vocative candidates\n\nNo violations found.\n"
    lines = [
        "## R18 vocative candidates\n",
        f"{len(all_candidates)} STRONG-SPLIT candidate(s) — vocative + non-2p verb, no 2p element:\n",
    ]
    for c in all_candidates:
        lines.append(f"**{c.verse_ref}** (line {c.line_index}) [{c.tag}]")
        lines.append(f"  > {c.line_text}")
        lines.append(f"  {c.rationale}")
        lines.append("")
    return "\n".join(lines)


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="R18 validator: vocative must own its line unless appositive merge applies."
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
                    f"[R18] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_report(all_candidates)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R18] Report written to {args.output} ({len(all_candidates)} candidates)")
    else:
        print(report)
        print(f"[R18] Total: {len(all_candidates)} candidate(s)")


if __name__ == "__main__":
    main()
