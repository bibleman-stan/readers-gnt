#!/usr/bin/env python3
"""
scan_ideou_subject_anticipation.py — find v4/grk lines matching the R1+M4
violation pattern Stan called out 2026-05-13 on Matt 2:1.

Pattern (mechanical):
  Line A starts with `ἰδοὺ` (or `Ἰδοὺ`) + contains a nominative substantive
  head + has NO finite verb on the same line.
  Line B (immediately next v4/grk line, possibly across editorial verse-marker)
  starts with a finite verb (no leading connective) and has no independent
  nominative subject NP on it (its subject is the line-A NP).

This is the R1 No-Anchor + M4-GNT-1 subject-orphan pattern that the historical
sweeps missed because R1's "substantive head" heuristic was too lax (it only
filtered noun lines CONTINUING a prior predicate, not noun lines ANTICIPATING
a following predicate).

Output: STRONG-MERGE-CANDIDATE per match. Per canon §3 Autonomy Boundary,
this is rule-derivative Category A — apply mechanically.

Run:
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_ideou_subject_anticipation.py
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_ideou_subject_anticipation.py --book matt
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from validators.common import (
    iter_v4_chapters,
    load_morphgnt_book_with_lemma,
    parse_chapter_file,
    strip_punctuation,
    is_finite_verb,
)

_LEADING_CONNECTIVES: frozenset[str] = frozenset({
    "καί", "δέ", "γάρ", "οὖν", "ἀλλά", "ἤ", "εἰ", "ὅτι", "ἵνα",
    "ὅταν", "ὅτε", "ὡς", "ὥστε", "ὅπου",
    # Also article-leads (don't merge if line B starts with article)
    "ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά",
})


def _bind_line(text: str, verse_tokens: list) -> list:
    """Positionally match line words to verse morphology tokens. Returns
    list of (surface, pos, parsing, lemma) in line order.
    """
    pool: dict[str, list] = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    out = []
    for raw in text.split():
        c = strip_punctuation(raw)
        if c in pool and pool[c]:
            out.append(pool[c].pop(0))
        else:
            # Stripping ἰδοὺ punctuation/diacritics — try lowercased match
            for k in list(pool.keys()):
                if strip_punctuation(k).lower() == c.lower() and pool[k]:
                    out.append(pool[k].pop(0))
                    break
    return out


def _is_nominative_substantive(pos: str, parsing: str) -> bool:
    """N-/RP/RD/A- in nominative case."""
    return pos in ("N-", "RP", "RD", "A-") and len(parsing) >= 5 and parsing[4] == "N"


def _line_starts_with_ideou(line_text: str) -> bool:
    if not line_text.strip():
        return False
    first = strip_punctuation(line_text.split()[0])
    return first.lower() == "ἰδοὺ" or first == "ἰδοὺ" or first == "Ἰδοὺ"


def _line_has_finite_verb(line_tokens: list) -> bool:
    return any(is_finite_verb(t[1], t[2]) for t in line_tokens)


def _line_first_finite_token(line_tokens: list) -> tuple | None:
    """Return the first finite verb token on the line, or None."""
    for t in line_tokens:
        if is_finite_verb(t[1], t[2]):
            return t
    return None


def _line_starts_with_finite_verb(line_text: str, line_tokens: list) -> bool:
    if not line_tokens or not line_text.split():
        return False
    first_surface = strip_punctuation(line_text.split()[0])
    first_token = line_tokens[0]
    return (
        strip_punctuation(first_token[0]) == first_surface
        and is_finite_verb(first_token[1], first_token[2])
    )


def _line_has_independent_subject_nominative(line_tokens: list) -> bool:
    """Does the line have a nominative substantive that could be its own subject?
    (Not the participle subject of an agreeing matrix predicate.)"""
    return any(_is_nominative_substantive(t[1], t[2]) for t in line_tokens)


def _line_starts_with_leading_connective(line_text: str) -> bool:
    if not line_text.strip():
        return False
    first = strip_punctuation(line_text.split()[0]).lower()
    return first in {x.lower() for x in _LEADING_CONNECTIVES}


def _find_nominative_substantive(line_tokens: list) -> tuple | None:
    for t in line_tokens:
        if _is_nominative_substantive(t[1], t[2]):
            return t
    return None


def check_book_chapter(book_slug: str, chapter_filepath: str) -> list[dict]:
    """Scan one chapter; return list of candidate dicts."""
    morph = load_morphgnt_book_with_lemma(book_slug)
    verses = parse_chapter_file(chapter_filepath)
    candidates = []

    # Flatten the chapter's lines in linear order with per-line tokens.
    flat_lines: list[tuple] = []  # (verse_ref, line_idx_in_verse, line_text, tokens)
    for verse in verses:
        ch, vs = verse["ch"], verse["vs"]
        verse_tokens = morph.get((ch, vs), [])
        norm = []
        for entry in verse_tokens:
            if len(entry) >= 4:
                w, pos, p, lemma = entry[0], entry[1], entry[2], entry[3]
            elif len(entry) == 3:
                w, pos, p = entry
                lemma = ""
            else:
                continue
            norm.append((strip_punctuation(w), pos, p, lemma))

        for i, line in enumerate(verse["lines"]):
            line_tokens = _bind_line(line, norm)
            flat_lines.append((f"{ch}:{vs}", i, line, line_tokens))

    for idx in range(len(flat_lines) - 1):
        ref_a, lia, text_a, tok_a = flat_lines[idx]
        ref_b, lib, text_b, tok_b = flat_lines[idx + 1]

        # Line A criteria
        if not _line_starts_with_ideou(text_a):
            continue
        nom = _find_nominative_substantive(tok_a)
        if nom is None:
            continue
        if _line_has_finite_verb(tok_a):
            continue  # already has its own predicate; not orphan

        # Line B criteria
        if not _line_starts_with_finite_verb(text_b, tok_b):
            continue
        if _line_starts_with_leading_connective(text_b):
            continue

        # Agreement filter: line B's leading finite verb must be INDICATIVE
        # 3rd-person, with number matching line A's nominative subject.
        # This filters out cases where line B is a different clause with its
        # own subject (imperatives like Matt 25:6 ἐξέρχεσθε; optatives like
        # Luke 1:38 γένοιτο). When the subject of line B's verb is the line-A
        # NP, person=3 and number agreement are required.
        verb_token = _line_first_finite_token(tok_b)
        if verb_token is None:
            continue
        verb_pos, verb_parsing = verb_token[1], verb_token[2]
        if len(verb_parsing) < 6:
            continue
        # parsing[0]=person, parsing[3]=mood, parsing[5]=number
        if verb_parsing[3] != "I":   # indicative only
            continue
        if verb_parsing[0] != "3":   # 3p verb takes nominative subject
            continue
        nom_parsing = nom[2]
        if len(nom_parsing) < 6:
            continue
        if verb_parsing[5] != nom_parsing[5]:  # number must match
            continue

        # Independent subject NP on line B blocks merge (already separate clause)
        if _line_has_independent_subject_nominative(tok_b):
            tag = "REVIEW-REQUIRED"
        else:
            tag = "STRONG-MERGE-CANDIDATE"

        candidates.append({
            "book": book_slug,
            "ref_a": ref_a,
            "line_a_idx": lia,
            "line_a_text": text_a.strip(),
            "ref_b": ref_b,
            "line_b_idx": lib,
            "line_b_text": text_b.strip(),
            "ideou_nom": f"{nom[0]} ({nom[3]})",
            "matrix_verb": (
                f"{_line_first_finite_token(tok_b)[0]} ({_line_first_finite_token(tok_b)[3]})"
                if _line_first_finite_token(tok_b) else "?"
            ),
            "tag": tag,
        })

    return candidates


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--book", help="Restrict to one book slug")
    p.add_argument("--output", help="Write markdown report to this path")
    args = p.parse_args()

    all_candidates = []
    for slug, ch, fp in iter_v4_chapters():
        if args.book and slug != args.book:
            continue
        try:
            all_candidates.extend(check_book_chapter(slug, fp))
        except Exception as e:
            print(f"[ideou] {slug} ch.{ch}: {e}", file=sys.stderr)

    strong = [c for c in all_candidates if c["tag"] == "STRONG-MERGE-CANDIDATE"]
    review = [c for c in all_candidates if c["tag"] == "REVIEW-REQUIRED"]

    print(f"ideou-subject-anticipation scan: {len(all_candidates)} candidates")
    print(f"  STRONG-MERGE: {len(strong)}")
    print(f"  REVIEW:       {len(review)}")
    print()

    for c in strong + review:
        print(f"  [{c['tag']}] {c['book']} {c['ref_a']} (line {c['line_a_idx']}) "
              f"+ {c['ref_b']} (line {c['line_b_idx']})")
        print(f"    A: {c['line_a_text']}  [nom: {c['ideou_nom']}]")
        print(f"    B: {c['line_b_text']}  [verb: {c['matrix_verb']}]")

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        lines = ["# ideou-subject-anticipation scan\n",
                 f"Total: {len(all_candidates)} ({len(strong)} STRONG, {len(review)} REVIEW)\n"]
        for c in strong + review:
            lines.append(f"\n**{c['book']} {c['ref_a']} → {c['ref_b']}** [{c['tag']}]")
            lines.append(f"- A (line {c['line_a_idx']}): `{c['line_a_text']}` — nom: {c['ideou_nom']}")
            lines.append(f"- B (line {c['line_b_idx']}): `{c['line_b_text']}` — verb: {c['matrix_verb']}")
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")
        print(f"\nReport written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
