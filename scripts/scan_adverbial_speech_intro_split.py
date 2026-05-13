#!/usr/bin/env python3
"""
scan_adverbial_speech_intro_split.py — find v4/grk lines where a λέγω-family
participle (adverbial participle of attendant circumstance) is split off
onto its own line from its matrix verb on a prior line.

Pattern Stan flagged 2026-05-13 on Matt 2:19-20:
  Line A: contains the matrix finite verb + its subject NP
  Line B: starts with λέγων/λέγοντες/λέγοντος/λέγουσα (participle of λέγω),
          case-agreeing with line A's subject; the rest of line B is the
          participle alone (possibly with ὅτι or a colon)

The participle is functioning as adverbial-of-attendant-circumstance modifying
the matrix verb, NOT as a standalone speech-act predication. Per canon §3.6:
R11 covers finite speech verbs only; participial speech-intros are not
J3-frame-equivalent unless they're the whole speech-act apparatus. When the
participle is bound to a matrix verb on a prior line, it should merge.

Output: STRONG-MERGE-CANDIDATE per match (cross-record fold marker may
apply per canon §3.17 if line B is in a different MetaV record from line A).

Run:
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_adverbial_speech_intro_split.py
"""
from __future__ import annotations

import argparse
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


def _bind_line(text: str, verse_tokens: list) -> list:
    pool: dict[str, list] = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    out = []
    for raw in text.split():
        c = strip_punctuation(raw)
        if c in pool and pool[c]:
            out.append(pool[c].pop(0))
        else:
            for k in list(pool.keys()):
                if strip_punctuation(k).lower() == c.lower() and pool[k]:
                    out.append(pool[k].pop(0))
                    break
    return out


def _is_lego_participle(pos: str, parsing: str, lemma: str) -> bool:
    """λέγω-family participle: lemma λέγω, POS V, mood=P (participle)."""
    return (
        pos.startswith("V")
        and len(parsing) >= 4
        and parsing[3] == "P"
        and lemma == "λέγω"
    )


def _case_number_gender(parsing: str) -> tuple[str, str, str]:
    """Return (case, number, gender) chars from parsing or empty tuple."""
    if len(parsing) < 7:
        return ("", "", "")
    return (parsing[4], parsing[5], parsing[6])


def _is_substantive(pos: str) -> bool:
    return pos in ("N-", "RP", "RD", "A-")


def _line_first_lego_participle(line_tokens: list) -> tuple | None:
    """If line's first content token is a λέγω-family participle, return it."""
    if not line_tokens:
        return None
    t = line_tokens[0]
    if _is_lego_participle(t[1], t[2], t[3]):
        return t
    return None


def _line_has_finite_verb(line_tokens: list) -> bool:
    return any(is_finite_verb(t[1], t[2]) for t in line_tokens)


def _line_finite_verb_token(line_tokens: list) -> tuple | None:
    for t in line_tokens:
        if is_finite_verb(t[1], t[2]):
            return t
    return None


def _find_agreeing_substantive(line_tokens: list, case: str, number: str, gender: str) -> tuple | None:
    """Find a substantive on this line matching case/number/gender."""
    for t in line_tokens:
        if not _is_substantive(t[1]):
            continue
        c, n, g = _case_number_gender(t[2])
        if c == case and n == number and g == gender:
            return t
    return None


def _line_is_just_participle(line_text: str, line_tokens: list) -> bool:
    """Line consists of only the participle + maybe ὅτι or a punctuation tail."""
    surface_words = [strip_punctuation(w) for w in line_text.split()]
    surface_words = [w for w in surface_words if w]
    if not surface_words:
        return False
    # First token is the participle. Allow up to 1 additional content word
    # (e.g., ὅτι recitative, or a dative addressee like αὐτοῖς).
    return len(surface_words) <= 2


def check_book_chapter(book_slug: str, chapter_filepath: str) -> list[dict]:
    morph = load_morphgnt_book_with_lemma(book_slug)
    verses = parse_chapter_file(chapter_filepath)

    flat_lines: list[tuple] = []
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

    candidates = []
    for idx in range(1, len(flat_lines)):
        ref_a, lia, text_a, tok_a = flat_lines[idx - 1]
        ref_b, lib, text_b, tok_b = flat_lines[idx]

        # Line B criteria: starts with λέγω-family participle, minimal content
        ptc = _line_first_lego_participle(tok_b)
        if ptc is None:
            continue
        if not _line_is_just_participle(text_b, tok_b):
            continue

        ptc_case, ptc_num, ptc_gen = _case_number_gender(ptc[2])
        if not ptc_case:
            continue

        # Line A criteria: contains a matrix finite verb + an agreeing
        # substantive (the participle's grammatical anchor)
        if not _line_has_finite_verb(tok_a):
            continue
        anchor = _find_agreeing_substantive(tok_a, ptc_case, ptc_num, ptc_gen)
        if anchor is None:
            continue

        matrix_verb = _line_finite_verb_token(tok_a)
        candidates.append({
            "book": book_slug,
            "ref_a": ref_a,
            "line_a_idx": lia,
            "line_a_text": text_a.strip(),
            "ref_b": ref_b,
            "line_b_idx": lib,
            "line_b_text": text_b.strip(),
            "participle": f"{ptc[0]} ({ptc[3]}, {ptc_case}{ptc_num}{ptc_gen})",
            "anchor_NP": f"{anchor[0]} ({anchor[3]}, {anchor[2][4:7] if len(anchor[2]) >= 7 else '?'})",
            "matrix_verb": (
                f"{matrix_verb[0]} ({matrix_verb[3]})" if matrix_verb else "?"
            ),
            "tag": "STRONG-MERGE-CANDIDATE",
            "cross_record": ref_a != ref_b,
        })

    return candidates


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--book", help="Restrict to one book slug")
    p.add_argument("--output", help="Write markdown report")
    args = p.parse_args()

    all_candidates = []
    for slug, ch, fp in iter_v4_chapters():
        if args.book and slug != args.book:
            continue
        try:
            all_candidates.extend(check_book_chapter(slug, fp))
        except Exception as e:
            print(f"[adverbial-speech-intro] {slug} ch.{ch}: {e}", file=sys.stderr)

    print(f"adverbial-speech-intro-split scan: {len(all_candidates)} candidates")
    print()

    for c in all_candidates:
        xrec = " [CROSS-RECORD]" if c["cross_record"] else ""
        print(f"  [{c['tag']}]{xrec} {c['book']} {c['ref_a']} (line {c['line_a_idx']}) "
              f"→ {c['ref_b']} (line {c['line_b_idx']})")
        print(f"    A: {c['line_a_text']}")
        print(f"       verb: {c['matrix_verb']}, anchor: {c['anchor_NP']}")
        print(f"    B: {c['line_b_text']}")
        print(f"       ptc: {c['participle']}")

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        lines = ["# adverbial-speech-intro-split scan\n",
                 f"Total: {len(all_candidates)} STRONG-MERGE candidates\n"]
        for c in all_candidates:
            xrec = " [CROSS-RECORD]" if c["cross_record"] else ""
            lines.append(f"\n**{c['book']} {c['ref_a']} → {c['ref_b']}** [{c['tag']}]{xrec}")
            lines.append(f"- A (line {c['line_a_idx']}): `{c['line_a_text']}`")
            lines.append(f"  - matrix verb: {c['matrix_verb']}")
            lines.append(f"  - anchor NP: {c['anchor_NP']}")
            lines.append(f"- B (line {c['line_b_idx']}): `{c['line_b_text']}`")
            lines.append(f"  - participle: {c['participle']}")
        Path(args.output).write_text("\n".join(lines), encoding="utf-8")
        print(f"\nReport written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
