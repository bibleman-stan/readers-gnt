"""
check_r10_hoti_complementizer.py — Layer 3 validator for Rule R10.

R10 (canon §3.5): ὅτι complementizer treatment depends on verb class.

  Cognition / perception / belief verbs → MERGE (ὅτι-clause is syntactic object).
  Declaration / speech / writing verbs  → SPLIT (ὅτι leads its own line).

Two violation patterns:
  (A) MERGE-CANDIDATE: cognition-class verb ends line N AND next line begins
      with ὅτι — the two should be on the SAME line (complement integrity).
  (B) SPLIT-CANDIDATE: declaration-class verb ends line N AND ὅτι begins the
      same line (ὅτι should open a NEW line, not trail the verb).

Closed lists (Closed-List Registry §3.5):
  Cognition: οἶδα, γινώσκω, ὁράω/εἶδον/βλέπω/θεωρέω, πιστεύω, ἐπίσταμαι,
             νομίζω/δοκέω, εὑρίσκω, ἀκούω, συνίημι
  Declaration: λέγω, εἶπον, γράφω, μαρτυρέω, ὁμολογέω, διδάσκω, κηρύσσω,
               ἀπαγγέλλω, καταγγέλλω, ἀναγγέλλω, ἐπαγγέλλομαι, προφητεύω

Note on ἀποκρίνομαι (per §3.5 speech-intro frame): verb + ὅτι merges as a
complex speech-intro frame → treated like cognition-class for merge purposes.

Uses MorphGNT lemma lookup (4-tuple loader) — verb class is a lemma question,
not a surface-string question.

Layer: 3 (DEVIATION).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from typing import List

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    load_v4_editorial,
    load_morphgnt_book_with_lemma,
    strip_punctuation,
)

RULE_ID = "R10"
ERROR_CLASS = "DEVIATION"

# ─── Verb class closed lists (canon §3.5 + Registry) ─────────────────────────

# Cognition / perception / belief — merge ὅτι complement onto same line.
# ὁράω covers its aorist suppletive stem εἶδον; all these inflect under one lemma
# or under listed alternative lemmas.
COGNITION_LEMMAS: frozenset[str] = frozenset({
    "οἶδα",
    "γινώσκω",
    "ὁράω",       # present stem (blepo / theoreo listed as separate lemmas below)
    "εἶδον",      # aorist suppletive of ὁράω (some MorphGNT editions list as own lemma)
    "βλέπω",
    "θεωρέω",
    "πιστεύω",
    "ἐπίσταμαι",
    "νομίζω",
    "δοκέω",
    "εὑρίσκω",
    "ἀκούω",
    "συνίημι",
    # ἀποκρίνομαι: speech-intro frame class — ὅτι merges as complex intro (§3.5)
    "ἀποκρίνομαι",
})

# Declaration / speech / writing — ὅτι should SPLIT (lead its own line).
DECLARATION_LEMMAS: frozenset[str] = frozenset({
    "λέγω",
    "εἶπον",      # aorist suppletive of λέγω; listed separately in MorphGNT
    "γράφω",
    "μαρτυρέω",
    "ὁμολογέω",
    "διδάσκω",
    "κηρύσσω",
    "ἀπαγγέλλω",
    "καταγγέλλω",
    "ἀναγγέλλω",
    "ἐπαγγέλλομαι",
    "προφητεύω",
})

# Surface tokens recognized as ὅτι (NFC-stripped).
_HOTI_FORMS: frozenset[str] = frozenset({"ὅτι"})


# ─── MorphGNT binding helper ──────────────────────────────────────────────────

def _bind_line_lemmas(line_text: str, verse_tokens: list) -> list:
    """Match surface words in line_text to morphological 4-tuples from the verse.

    verse_tokens: list of (cleaned_word, pos, parsing, lemma) from
    load_morphgnt_book_with_lemma.
    Returns list of matched (cleaned_word, pos, parsing, lemma) in line order.
    """
    pool: dict[str, list] = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    result = []
    for raw in line_text.split():
        c = strip_punctuation(raw)
        if c in pool and pool[c]:
            result.append(pool[c].pop(0))
    return result


def _line_ends_with_verb_class(
    line_tokens: list,
    verb_class: frozenset,
) -> tuple[bool, str]:
    """Return (True, lemma) if the last VERB on the line is in verb_class.

    We look at the LAST verb token on the line (rightmost), which is the
    governing verb that the following ὅτι will complement.
    Returns (False, "") if no matching verb found.
    """
    # Walk backwards to find the last verb on the line
    for tok in reversed(line_tokens):
        _word, pos, _parsing, lemma = tok
        if pos.startswith("V"):
            return (lemma in verb_class), lemma
    return False, ""


def _line_starts_with_hoti(line_tokens: list) -> bool:
    """Return True if the first non-empty token on the line is ὅτι."""
    if not line_tokens:
        return False
    first_word = line_tokens[0][0]
    return first_word in _HOTI_FORMS


def _line_contains_hoti(line_tokens: list) -> bool:
    """Return True if ὅτι appears anywhere on this line."""
    return any(tok[0] in _HOTI_FORMS for tok in line_tokens)


# ─── Core checker ─────────────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R10 violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)
    morph = load_morphgnt_book_with_lemma(book)

    candidates: List[Candidate] = []
    lines = v4.lines

    for i, vline in enumerate(lines):
        # Determine (chapter, verse) for MorphGNT lookup.
        ref_match = re.search(r"(\d+):(\d+)$", vline.verse_ref)
        if not ref_match:
            continue
        cv = (int(ref_match.group(1)), int(ref_match.group(2)))
        verse_tokens = morph.get(cv, [])
        if not verse_tokens:
            continue

        lt = _bind_line_lemmas(vline.text, verse_tokens)
        if not lt:
            continue

        # ── Pattern A: cognition-class verb ends this line AND next line opens ὅτι
        # This should be a merge — the ὅτι clause is the syntactic complement.
        if i + 1 < len(lines):
            is_cog, cog_lemma = _line_ends_with_verb_class(lt, COGNITION_LEMMAS)
            if is_cog:
                next_line = lines[i + 1]
                next_cv_match = re.search(r"(\d+):(\d+)$", next_line.verse_ref)
                if next_cv_match:
                    next_cv = (int(next_cv_match.group(1)), int(next_cv_match.group(2)))
                    next_verse_tokens = morph.get(next_cv, [])
                    next_lt = _bind_line_lemmas(next_line.text, next_verse_tokens)
                    if _line_starts_with_hoti(next_lt):
                        context = _build_context(lines, i)
                        candidates.append(
                            emit_candidate(
                                verse_ref=vline.verse_ref,
                                line_index=vline.line_index,
                                line_text=vline.text,
                                rule=RULE_ID,
                                tag="MERGE-CANDIDATE",
                                error_class=ERROR_CLASS,
                                rationale=(
                                    f"R10: cognition-class verb '{cog_lemma}' ends line; "
                                    f"next line opens ὅτι — complement should merge onto "
                                    f"same line (ὅτι clause is syntactic object)"
                                ),
                                context=context,
                            )
                        )

        # ── Pattern B: declaration-class verb on this line AND ὅτι also on same line
        # The ὅτι should lead the NEXT line, not appear on the same line as the verb.
        is_decl, decl_lemma = _line_ends_with_verb_class(lt, DECLARATION_LEMMAS)
        if is_decl and _line_contains_hoti(lt):
            # Only flag if ὅτι is NOT the first token (then it would be leading correctly)
            # and the declaration verb appears BEFORE ὅτι on the line.
            hoti_idx = next(
                (j for j, tok in enumerate(lt) if tok[0] in _HOTI_FORMS), -1
            )
            decl_verb_idx = max(
                (j for j, tok in enumerate(lt) if tok[1].startswith("V")
                 and tok[3] in DECLARATION_LEMMAS),
                default=-1,
            )
            # Violation: declaration verb precedes ὅτι on SAME line
            # (ὅτι should open next line, not be on the verb's line)
            if decl_verb_idx >= 0 and hoti_idx > decl_verb_idx:
                context = _build_context(lines, i)
                candidates.append(
                    emit_candidate(
                        verse_ref=vline.verse_ref,
                        line_index=vline.line_index,
                        line_text=vline.text,
                        rule=RULE_ID,
                        tag="SPLIT-CANDIDATE",
                        error_class=ERROR_CLASS,
                        rationale=(
                            f"R10: declaration-class verb '{decl_lemma}' and ὅτι on same line — "
                            f"ὅτι should lead the next line (declaration verb stands alone)"
                        ),
                        context=context,
                    )
                )

    return candidates


def _build_context(v4_lines: list, line_index: int) -> str:
    start = max(0, line_index - 1)
    end = min(len(v4_lines), line_index + 2)
    return " | ".join(v4_lines[i].text for i in range(start, end))


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _format_report(candidates: List[Candidate]) -> str:
    if not candidates:
        return "## R10 hoti-complementizer\n\nNo violations found.\n"
    merge_c = [c for c in candidates if c.tag == "MERGE-CANDIDATE"]
    split_c = [c for c in candidates if c.tag == "SPLIT-CANDIDATE"]
    lines = [
        f"## R10 hoti-complementizer — {len(candidates)} violation(s) "
        f"({len(merge_c)} MERGE-CANDIDATE, {len(split_c)} SPLIT-CANDIDATE)\n"
    ]
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
        description="R10 validator: ὅτι complementizer — cognition vs. declaration verbs."
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
                print(f"[R10] WARNING: {args.book} ch.{ch} skipped — {exc}", file=sys.stderr)
                ch += 1
                if ch > 200:
                    break
    else:
        for slug, chapter_num, _fp in iter_v4_chapters():
            try:
                all_candidates.extend(check_book_chapter(slug, chapter_num))
            except Exception as exc:
                print(f"[R10] WARNING: {slug} ch.{chapter_num} skipped — {exc}", file=sys.stderr)

    report = _format_report(all_candidates)
    print(f"[R10] {len(all_candidates)} violation(s) found.", file=sys.stderr)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R10] Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
