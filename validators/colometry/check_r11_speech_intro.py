"""
check_r11_speech_intro.py — Layer 2 colometry validator for Rule R11.

R11 (canon §3.6): finite speech verb (λέγω/φημί/ἀποκρίνομαι) + frame gets its
own line; quoted content begins on next line.

Violation: line has 3rd-person indicative speech verb + another finite/imperative,
no speech-boundary marker at end, no ὅτι (indirect speech → R10).

NOTE: load_morphgnt_book() returns (word, pos, parsing) 3-tuples — no lemma.
_load_morphgnt_with_lemma() bridges that gap directly from the MorphGNT file.
Once common.py exposes a lemma-aware loader this bridge can be removed.
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
    strip_punctuation,
    SLUG_TO_FILE_NUM,
)

RULE_ID = "R11"
ERROR_CLASS = "DEVIATION"

# Finite narrative speech-intro lemmas (3rd-person indicative only).
SPEECH_LEMMAS: frozenset[str] = frozenset({"λέγω", "φημί", "ἀποκρίνομαι"})

# ─── MorphGNT lemma-aware loader (bridge until common.py exposes lemma) ───────

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MORPHGNT_DIR = os.path.join(_REPO_ROOT, "research", "morphgnt-sblgnt")
_morph_cache: dict[str, dict] = {}


def _load_morphgnt_with_lemma(book_slug: str) -> dict:
    """Load MorphGNT for a book; returns {(ch, vs): [(cleaned_word, pos, parsing, lemma)]}.

    Bridge until validators.common exposes a lemma-aware MorphGNT loader.
    """
    if book_slug in _morph_cache:
        return _morph_cache[book_slug]
    file_num = SLUG_TO_FILE_NUM.get(book_slug)
    if not file_num or not os.path.isdir(_MORPHGNT_DIR):
        _morph_cache[book_slug] = {}
        return {}
    path = next(
        (os.path.join(_MORPHGNT_DIR, f) for f in os.listdir(_MORPHGNT_DIR)
         if f.startswith(file_num + "-") and f.endswith(".txt")),
        None,
    )
    if not path:
        _morph_cache[book_slug] = {}
        return {}
    verses: dict = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.strip().split(" ", 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, _text, word, _norm, lemma = parts
            cleaned = strip_punctuation(word)
            if cleaned:
                verses[(int(ref[2:4]), int(ref[4:6]))].append(
                    (cleaned, pos, parsing, lemma)
                )
    result = dict(verses)
    _morph_cache[book_slug] = result
    return result


# ─── Morphological predicates ────────────────────────────────────────────────

def _is_finite_speech_verb(pos: str, parsing: str, lemma: str) -> bool:
    """True for 3rd-person indicative forms of SPEECH_LEMMAS.

    Excludes 1p/2p (conversational), imperatives, subjunctives, optatives,
    participles. Tenses: aorist (A), imperfect (I), present (P).
    """
    if not pos.startswith("V"):
        return False
    if lemma not in SPEECH_LEMMAS:
        return False
    if len(parsing) < 4:
        return False
    person, tense, _voice, mood = parsing[0], parsing[1], parsing[2], parsing[3]
    return mood == "I" and person == "3" and tense in ("A", "I", "P")


def _is_finite_verb(pos: str, parsing: str) -> bool:
    """True for any finite verb (indicative / subjunctive / imperative / optative)."""
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in "ISDO"


def _is_imperative(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "D"


# ─── FP-filter helpers ────────────────────────────────────────────────────────

#: Negation particles that precede a verb to negate the speech act.
_NEGATIONS: frozenset[str] = frozenset({"οὐ", "οὐκ", "οὐχ", "μή", "οὐδέ", "μηδέ"})

#: Divine-authority nouns whose presence signals OT-attribution context.
_DIVINE_NOUNS: frozenset[str] = frozenset({"κύριος", "θεός", "πνεῦμα"})


def _has_preceding_negation(token_index: int, line_tokens: list) -> bool:
    """Return True if the token immediately before token_index is a negation particle.

    Class A filter: a speech verb preceded by οὐ/οὐκ/οὐχ/μή/οὐδέ/μηδέ is
    describing the NON-occurrence of speech (e.g. οὐκ ἀπεκρίνατο οὐδέν).
    R11 does not apply — no speech content is being introduced.
    """
    if token_index == 0:
        return False
    prev_word = line_tokens[token_index - 1][0]  # cleaned surface form
    prev_lemma = line_tokens[token_index - 1][3]  # lemma
    return prev_word in _NEGATIONS or prev_lemma in _NEGATIONS


def _is_ot_attribution(verb_index: int, line_tokens: list) -> bool:
    """Return True if this speech verb looks like an OT-attribution tag, not a speech-intro.

    Class B filter heuristic:
    - Verb is 3rd-person singular (the attribution-use form).
    - A divine-authority noun (κύριος / θεός / πνεῦμα) appears anywhere on the same line
      in nominative or genitive case (NOM case = '-N-----'; GEN = '-G-----' in MorphGNT).
    - The verb is NOT the first word on the line (attribution tags appear mid- or post-content).

    When matched, the validator should downgrade to REVIEW-REQUIRED rather than STRONG-SPLIT,
    because some first-occurrence speech verbs + κύριος are genuine (e.g. λέγει κύριος opening
    a new oracle).  Human review resolves the ambiguity.
    """
    _word, pos, parsing, _lemma = line_tokens[verb_index]
    # Must be 3rd-person singular indicative
    if not (pos.startswith("V") and len(parsing) >= 4
            and parsing[0] == "3" and parsing[3] == "I"):
        return False
    # Check whether it is not the first token (attribution appears after content)
    if verb_index == 0:
        return False
    # Look for divine-authority noun in NOM or GEN anywhere on the line.
    # MorphGNT noun parsing format: --------  positions 0-7
    # position 4 = case (N=nominative, G=genitive, D=dative, A=accusative, V=vocative)
    for word, npos, nparsing, nlemma in line_tokens:
        if nlemma in _DIVINE_NOUNS and npos == "N-" and len(nparsing) >= 5 and nparsing[4] in "NG":
            return True
    return False


# ─── Line helpers ─────────────────────────────────────────────────────────────

def _ends_with_speech_boundary(line: str) -> bool:
    """Does the line end on colon or ano teleia (speech-intro boundary)?"""
    s = line.rstrip()
    return s.endswith(":") or s.endswith("·") or s.endswith("\u0387") or s.endswith("\u00B7")


def _bind_line(line_text: str, verse_tokens: list) -> list:
    """Match surface words in line_text to morphological tuples in verse_tokens.

    Returns list of (cleaned_word, pos, parsing, lemma) matching line words.
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


def _build_context(v4_lines: list, line_index: int) -> str:
    start = max(0, line_index - 1)
    end = min(len(v4_lines), line_index + 2)
    return " | ".join(v4_lines[i].text for i in range(start, end))


# ─── Core checker ─────────────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return list of Candidate objects flagging R11 violations in this chapter."""
    v4 = load_v4_editorial(book, chapter)
    morph = _load_morphgnt_with_lemma(book)

    candidates: List[Candidate] = []

    for vline in v4.lines:
        # Determine verse (ch, vs) from verse_ref — e.g. "Mark 4:1" -> (4, 1)
        ref_match = re.search(r"(\d+):(\d+)$", vline.verse_ref)
        if not ref_match:
            continue
        cv = (int(ref_match.group(1)), int(ref_match.group(2)))
        verse_tokens = morph.get(cv, [])
        if not verse_tokens:
            continue

        lt = _bind_line(vline.text, verse_tokens)
        speech_verb_indices = [
            i for i, (w, pos, p, l) in enumerate(lt) if _is_finite_speech_verb(pos, p, l)
        ]
        if not speech_verb_indices:
            continue
        speech_verbs = [(lt[i][0], lt[i][3]) for i in speech_verb_indices]

        # ── Class A filter: negated non-answer verbs ──────────────────────────
        # If ALL speech verbs on this line are immediately preceded by a negation
        # particle, the line describes the non-occurrence of speech (e.g.
        # οὐκ ἀπεκρίνατο οὐδέν in Mark 14:61). No speech is being introduced.
        if all(_has_preceding_negation(i, lt) for i in speech_verb_indices):
            continue

        # Exclusion 1: line ends on speech boundary — frame is properly closed.
        if _ends_with_speech_boundary(vline.text):
            continue

        # Exclusion 2: ὅτι on the line — indirect speech (R10), not R11.
        has_hoti = any(strip_punctuation(w) == "ὅτι" for w in vline.text.split())
        if has_hoti:
            continue

        # Violation: line has speech verb AND additional finite verb or imperative.
        other_fins = [(w, l) for w, pos, p, l in lt
                      if _is_finite_verb(pos, p) and not _is_finite_speech_verb(pos, p, l)]
        imperatives = [(w, l) for w, pos, p, l in lt if _is_imperative(pos, p)]

        if not (other_fins or imperatives):
            continue

        # ── Class B filter: OT-attribution tags ──────────────────────────────
        # If any speech verb matches the OT-attribution heuristic (3rd sg + divine
        # noun on same line, verb not line-initial), downgrade to REVIEW-REQUIRED.
        # λέγει κύριος / φησίν [κύριος] mid-quotation are attribution, not intros.
        is_ot_attr = any(_is_ot_attribution(i, lt) for i in speech_verb_indices)

        # Classify: leaked imperative or finite verb = STRONG-SPLIT (or REVIEW-REQUIRED).
        leaked = other_fins + imperatives
        kind = "imperative(s)" if imperatives else "finite verb(s)"
        if is_ot_attr:
            tag = "REVIEW-REQUIRED"
            rationale = (
                f"R11: speech-intro line has leaked {kind} "
                f"{[w+'('+l+')' for w,l in leaked]}; "
                f"intro verbs: {[w+'('+l+')' for w,l in speech_verbs]} "
                f"[downgraded: possible OT-attribution tag (λέγει κύριος / φησίν), "
                f"needs human review]"
            )
        else:
            tag = "STRONG-SPLIT"
            rationale = (
                f"R11: speech-intro line has leaked {kind} "
                f"{[w+'('+l+')' for w,l in leaked]}; "
                f"intro verbs: {[w+'('+l+')' for w,l in speech_verbs]}"
            )

        context = _build_context(v4.lines, vline.line_index)
        candidates.append(emit_candidate(
            verse_ref=vline.verse_ref,
            line_index=vline.line_index,
            line_text=vline.text,
            rule=RULE_ID,
            tag=tag,
            error_class=ERROR_CLASS,
            rationale=rationale,
            context=context,
        ))

    return candidates


# ─── CLI ──────────────────────────────────────────────────────────────────────

def _format_report(candidates: List[Candidate]) -> str:
    if not candidates:
        return "## R11 direct-speech-introduction\n\nNo violations found.\n"
    lines = [f"## R11 direct-speech-introduction — {len(candidates)} violation(s)\n"]
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
        description="R11 validator: direct-speech introduction on its own line."
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
                print(f"[R11] WARNING: {args.book} ch.{ch} skipped — {exc}", file=sys.stderr)
                ch += 1
                if ch > 200:
                    break
    else:
        for slug, chapter_num, _fp in iter_v4_chapters():
            try:
                all_candidates.extend(check_book_chapter(slug, chapter_num))
            except Exception as exc:
                print(f"[R11] WARNING: {slug} ch.{chapter_num} skipped — {exc}", file=sys.stderr)

    report = _format_report(all_candidates)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R11] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
