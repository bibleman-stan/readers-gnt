"""
check_r28_speech_act_frame.py — Layer 3 colometry validator for R28-ext.

R28-ext (canon §3.6 "Speech-Act Announcement After Frame"):
  When a finite speech verb (λέγω/εἶπον/φημί) that introduces direct speech
  co-occurs on the same v4-editorial line with a substantive preceding
  adverbial frame (temporal ὡς/ὅτε/ὅταν clause OR participial-absolute cluster
  ≥3 non-punctuation tokens), the line MUST be split: frame → line 1,
  speech verb + any dative-address → line 2.

Detection path (MorphGNT-only; no Macula dependency):
  1. Line ends with ano teleia (·) or colon (:) — confirms direct-speech intro
  2. Line contains a finite speech verb from SPEECH_LEMMAS (3rd-person indicative)
  3. Line also contains either:
     (a) A temporal-conjunction token from TEMPORAL_CONJ whose clause
         contains at least one additional finite verb (the frame verb)
     (b) A participial token with ≥3 token cluster before the speech verb
         (proxy for "substantive participial frame")

Exclusions applied (canon §3.6 R28-ext closed list):
  X1  ὅτι immediately after speech verb → R10 governs (indirect speech)
  X2  λέγων/εἰπών participial immediately before/after speech verb
      → ἀπεκρίθη+λέγων Hebraism, not a substantive frame
  X3  Frame already on prior line (only same-line co-occurrence in scope)
  X4  Speech verb is inside a subordinate clause (F1 filter from R11)

All violations are STRONG-SPLIT (no REVIEW-REQUIRED cases; the rule is mechanical).
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from typing import List, Optional

from validators.common import (
    Candidate,
    emit_candidate,
    iter_v4_chapters,
    load_morphgnt_book_with_lemma,
    parse_chapter_file,
    strip_punctuation,
    is_finite_verb,
)

RULE_ID = "R28ext"
ERROR_CLASS = "DEVIATION"

BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts", "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess", "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet", "1john", "2john", "3john", "jude", "rev",
]

# ─── Closed lists ─────────────────────────────────────────────────────────────

# 3rd-person finite speech-intro lemmas that can introduce direct speech.
SPEECH_LEMMAS: frozenset[str] = frozenset({"λέγω", "φημί", "εἶπον"})

# Temporal/causal conjunctions that head substantive adverbial frames.
# Excludes purpose/result subordinators (ἵνα/ὅπως/ὥστε) which are
# complement-introducing, not scene-setting.
TEMPORAL_CONJ: frozenset[str] = frozenset({
    "ὡς",    # as/when (most common in speech-intro frames; Luke 5:4)
    "ὅτε",   # when (narrative past-time frame)
    "ὅταν",  # whenever/when (generic temporal; Heb 1:6)
    "ἐπεί",  # since/when (causal-temporal)
    "ἐπειδή",  # since/after
    "ὅσον",  # as long as (temporal extent)
})

# Participial forms that mark speech-introduction manner markers → Exclusion 2.
# These participial lemmas function as redundant manner markers co-occurring
# with the finite speech verb; they are NOT substantive frames triggering R28-ext.
#   - λέγω / εἶπον: the ἀπεκρίθη+λέγων Hebraism (bare saying-continuation)
#   - ἀποκρίνομαι: the ubiquitous ἀποκριθείς+εἶπεν Hebraism in the Synoptics
#     (literally "answering, he said") — this is a single speech event, not frame+speech
HEBRAISM_PARTICIPLE_LEMMAS: frozenset[str] = frozenset({"λέγω", "εἶπον", "ἀποκρίνομαι"})

# Ano teleia and colon (end-of-speech-intro line markers).
_SPEECH_END: frozenset[str] = frozenset({"·", ":"})


# ─── Detection helpers ────────────────────────────────────────────────────────

def _line_ends_with_speech_marker(line: str) -> bool:
    """Return True if the raw line text ends with · or : (direct-speech opener)."""
    stripped = line.rstrip()
    return bool(stripped) and stripped[-1] in _SPEECH_END


def _is_3p_indicative_speech_verb(pos: str, parsing: str, lemma: str) -> bool:
    """True for 3rd-person indicative forms of SPEECH_LEMMAS.

    Excludes 1p/2p (conversational), imperatives, subjunctives, optatives,
    participles (those are filtered by exclusion X2).
    Tenses: aorist (A), imperfect (I), present (P).
    """
    if not pos.startswith("V"):
        return False
    if lemma not in SPEECH_LEMMAS:
        return False
    if len(parsing) < 4:
        return False
    person, tense, _voice, mood = parsing[0], parsing[1], parsing[2], parsing[3]
    return mood == "I" and person == "3" and tense in ("A", "I", "P")


def _is_participle(pos: str, parsing: str) -> bool:
    """True for any participle token (pos V-, mood P in parsing[3])."""
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "P"


def _has_temporal_conj(tokens: list) -> Optional[int]:
    """Return index of first temporal-conjunction token, or None."""
    for i, (_w, _pos, _parsing, lemma) in enumerate(tokens):
        if lemma in TEMPORAL_CONJ:
            return i
    return None


def _find_speech_verb(tokens: list) -> Optional[tuple]:
    """Return (index, word, lemma) for the first 3p-indicative speech verb, or None."""
    for i, (w, pos, parsing, lemma) in enumerate(tokens):
        if _is_3p_indicative_speech_verb(pos, parsing, lemma):
            return (i, w, lemma)
    return None


def _has_frame_finite_before_speech(
    tokens: list,
    temporal_conj_idx: int,
    speech_verb_idx: int,
) -> bool:
    """Return True if there is a finite verb between the temporal conjunction
    and the speech verb (i.e., the frame clause has its own finite verb —
    distinguishing a substantive frame from a bare particle).
    """
    for i in range(temporal_conj_idx + 1, speech_verb_idx):
        w, pos, parsing, lemma = tokens[i]
        if is_finite_verb(pos, parsing) and lemma not in SPEECH_LEMMAS:
            return True
    return False


def _has_substantive_participial_frame(
    tokens: list,
    speech_verb_idx: int,
) -> bool:
    """Return True if there is a substantive participial frame before the speech verb.

    A participial frame is substantive when the participle has ≥2 additional
    non-punctuation tokens in its cluster before the speech verb (i.e., at least
    a subject-NP or object-NP accompanying the participle, not a bare adverbial).

    Proxy test: count non-punctuation tokens before speech_verb_idx. If ≥3,
    the preamble is substantive (a bare adverb would be 1-2 tokens).
    And there is at least one participle in that preamble.
    """
    preamble = tokens[:speech_verb_idx]
    has_participle = any(_is_participle(pos, parsing) for _w, pos, parsing, _lemma in preamble)
    if not has_participle:
        return False
    # Count non-trivial (non-punctuation) tokens in preamble
    content_tokens = [
        w for w, _pos, _parsing, _lemma in preamble
        if strip_punctuation(w)  # non-empty after stripping punct
    ]
    return len(content_tokens) >= 3


def _exclusion_hoti_follows_speech(tokens: list, speech_verb_idx: int) -> bool:
    """Exclusion 1: ὅτι immediately follows the speech verb → R10 governs."""
    for i in range(speech_verb_idx + 1, min(len(tokens), speech_verb_idx + 3)):
        w, _pos, _parsing, lemma = tokens[i]
        if lemma == "ὅτι" or strip_punctuation(w) == "ὅτι":
            return True
    return False


def _exclusion_hebraism_participle(tokens: list, speech_verb_idx: int) -> bool:
    """Exclusion 2: Hebraism-marker participle anywhere before/after speech verb.

    Patterns covered:
    - ἀποκριθείς + εἶπεν (ubiquitous Synoptic double-verb; ἀποκριθείς may have
      subject NP between it and εἶπεν, so search the whole preamble)
    - λέγων + εἶπεν or εἶπεν + λέγων (bare saying-continuation)

    The participle is a redundant manner marker, not a substantive frame.
    Scan all tokens before (and up to 3 after) the speech verb.
    """
    # All tokens before speech verb
    for i in range(speech_verb_idx):
        w, pos, parsing, lemma = tokens[i]
        if _is_participle(pos, parsing) and lemma in HEBRAISM_PARTICIPLE_LEMMAS:
            return True
    # Up to 3 tokens after (λέγων trailing the speech verb)
    for i in range(speech_verb_idx + 1, min(len(tokens), speech_verb_idx + 4)):
        w, pos, parsing, lemma = tokens[i]
        if _is_participle(pos, parsing) and lemma in HEBRAISM_PARTICIPLE_LEMMAS:
            return True
    return False


def _exclusion_speech_verb_is_subordinate(tokens: list, speech_verb_idx: int) -> bool:
    """Exclusion 4 (F1-style): speech verb preceded by a relative/subordinate pronoun.

    If a relative/interrogative word precedes the speech verb on the same line,
    the speech verb is inside an embedded clause — not a main-clause speech intro.
    """
    _SUBORDINATORS: frozenset[str] = frozenset({
        "ὅ", "ὃ", "ὅν", "ὃν", "ὅς", "ὃς", "ἥ", "οὗ", "ὧν", "οἷς", "αἷς",
        "ὅπου", "ὅθεν", "καθώς", "καθὼς", "πῶς",
        "τίς", "τί", "τίνος", "τίνι", "τίνα",
        "ὅσα", "ὅσον", "ὅσοι",
    })
    for i in range(speech_verb_idx):
        lemma = tokens[i][3].lower()
        w = tokens[i][0].lower()
        if lemma in _SUBORDINATORS or w in _SUBORDINATORS:
            return True
    return False


# ─── Token binding ────────────────────────────────────────────────────────────

def _bind_line(text: str, verse_tokens: list) -> list:
    """Positionally match line words to MorphGNT verse tokens."""
    pool: dict[str, list] = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    line_tokens = []
    for raw in text.split():
        c = strip_punctuation(raw)
        if c in pool and pool[c]:
            line_tokens.append(pool[c].pop(0))
    return line_tokens


# ─── Context builder ─────────────────────────────────────────────────────────

def _build_context(verses: list[dict], ch: int, vs: int, target_line: str) -> str:
    """Return 1-2 adjacent lines for context display."""
    for verse in verses:
        if verse["ch"] == ch and verse["vs"] == vs:
            lines = verse["lines"]
            try:
                idx = lines.index(target_line)
            except ValueError:
                return ""
            start = max(0, idx - 1)
            end = min(len(lines), idx + 2)
            return " | ".join(lines[i].strip() for i in range(start, end))
    return ""


# ─── Core check ──────────────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R28-ext violations in this chapter.

    A violation is a v4-editorial line that:
      - ends with · or : (speech-intro marker)
      - contains a 3p-indicative speech verb
      - contains a substantive adverbial frame before the speech verb
        (either a temporal-conj clause with its own finite verb,
         or a participial cluster of ≥3 tokens)
      - passes all exclusion filters (X1–X4)
    """
    morph = load_morphgnt_book_with_lemma(book)
    if not morph:
        return []

    chapter_file: Optional[str] = None
    for slug, ch_num, fpath in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_file = fpath
            break
    if chapter_file is None:
        raise FileNotFoundError(
            f"v4-editorial file not found: book={book!r} chapter={chapter}"
        )

    verses = parse_chapter_file(chapter_file)
    display_book = book[0].upper() + book[1:]
    candidates: List[Candidate] = []
    line_index = 0

    for verse in verses:
        ch_num, vs_num = verse["ch"], verse["vs"]
        verse_tokens = morph.get((ch_num, vs_num), [])
        verse_ref = f"{display_book} {ch_num}:{vs_num}"

        for line in verse["lines"]:
            # Gate 1: line ends with speech-intro marker
            if not _line_ends_with_speech_marker(line):
                line_index += 1
                continue

            lt = _bind_line(line, list(verse_tokens))
            if not lt:
                line_index += 1
                continue

            # Gate 2: find 3p-indicative speech verb
            sv = _find_speech_verb(lt)
            if sv is None:
                line_index += 1
                continue
            sv_idx, sv_word, sv_lemma = sv

            # Nothing substantive can precede a speech verb at position 0
            if sv_idx == 0:
                line_index += 1
                continue

            # Exclusion 4: speech verb is inside a subordinate clause
            if _exclusion_speech_verb_is_subordinate(lt, sv_idx):
                line_index += 1
                continue

            # Exclusion 1: ὅτι follows speech verb → R10
            if _exclusion_hoti_follows_speech(lt, sv_idx):
                line_index += 1
                continue

            # Exclusion 2: λέγων/εἰπών Hebraism adjacent to speech verb
            if _exclusion_hebraism_participle(lt, sv_idx):
                line_index += 1
                continue

            # Gate 3a: substantive temporal-conj frame
            temporal_idx = _has_temporal_conj(lt)
            has_temporal_frame = (
                temporal_idx is not None
                and temporal_idx < sv_idx
                and _has_frame_finite_before_speech(lt, temporal_idx, sv_idx)
            )

            # Gate 3b: substantive participial frame
            has_participial_frame = _has_substantive_participial_frame(lt, sv_idx)

            if not (has_temporal_frame or has_participial_frame):
                line_index += 1
                continue

            # Build rationale
            if has_temporal_frame:
                conj_word = lt[temporal_idx][0]
                frame_desc = f"temporal-conj frame ({conj_word}...)"
            else:
                frame_desc = "participial-absolute frame"

            rationale = (
                f"Finite speech verb {sv_word!r} ({sv_lemma}) co-linear with "
                f"{frame_desc} — R28-ext: frame and speech-intro must split"
            )
            context = _build_context(verses, ch_num, vs_num, line)
            candidates.append(emit_candidate(
                verse_ref=verse_ref,
                line_index=line_index,
                line_text=line.strip(),
                rule=RULE_ID,
                tag="STRONG-SPLIT",
                error_class=ERROR_CLASS,
                rationale=rationale,
                context=context,
            ))
            line_index += 1

    return candidates


# ─── Markdown report ─────────────────────────────────────────────────────────

def _format_markdown(all_candidates: List[Candidate]) -> str:
    if not all_candidates:
        return "## R28-ext violations\n\nNo violations found.\n"
    lines = [
        "## R28-ext violations",
        "",
        "Rule R28-ext (§3.6): adverbial frame + finite speech verb co-linear — must split.",
        "All violations are STRONG-SPLIT.",
        f"Total: {len(all_candidates)}",
        "",
    ]
    for c in all_candidates:
        lines.append(
            f"- **{c.verse_ref}** (line {c.line_index}) [{c.tag}] {c.rationale}"
        )
        lines.append(f"  > {c.line_text}")
        if c.context:
            lines.append(f"  *context:* {c.context}")
    return "\n".join(lines) + "\n"


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="R28-ext validator: adverbial frame + speech verb must split."
    )
    parser.add_argument("--book", help="Restrict to one book (e.g. 'luke')")
    parser.add_argument(
        "--chapter", type=int, help="Restrict to one chapter (requires --book)"
    )
    parser.add_argument("--output", help="Write markdown report to this file path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    books_to_run = [args.book] if args.book else BOOKS
    all_candidates: List[Candidate] = []

    for book in books_to_run:
        chapters_to_run = (
            [args.chapter] if args.chapter else list(range(1, 200))
        )
        for ch in chapters_to_run:
            try:
                candidates = check_book_chapter(book, ch)
                all_candidates.extend(candidates)
            except FileNotFoundError:
                break
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[R28ext] WARNING: {book} ch.{ch} skipped — {exc}",
                    file=sys.stderr,
                )

    report = _format_markdown(all_candidates)

    if args.output:
        import os
        os.makedirs(
            os.path.dirname(os.path.abspath(args.output)), exist_ok=True
        )
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(
            f"[R28ext] Report written to {args.output} "
            f"({len(all_candidates)} violations)"
        )
    else:
        # Use utf-8 writer to handle Greek characters on Windows terminals.
        sys.stdout.buffer.write(report.encode("utf-8"))


if __name__ == "__main__":
    main()
