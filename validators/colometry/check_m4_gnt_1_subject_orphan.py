"""
check_m4_gnt_1_subject_orphan.py — Layer 3 validator for M4-GNT-1 (canon §3.18).

M4-GNT-1: Subject-Orphan Predicate Completion (Greek Instantiation)

When a v4/grc line whose content is a subject NP (closed-list-eligible
shape) terminates in `,' or `·`, AND the immediately-next line is a bare finite
predicate (finite verb lead, no leading connective, no independent subject),
the predicate-line MUST be merged onto the subject-line as a single ATU.

Codified 2026-05-11 as GNT corpus instantiation of framework M4 (fragmented
atomic thought-unit; canon §3.18 / §1 M4). Sibling of M4-BoFM-1.

Five Greek-specific exclusions (G1–G5):
  G1: Attributive participle on line B (modifier of NP on line A) → STAY-SPLIT
  G2: Verbless nominal-sentence line A (predicate NP/ADJ; complete by ellipsis)
      → STAY-SPLIT
  G3: Periphrastic-construction line B (R5 governs) → STAY-SPLIT
  G4: Doxological vocative-NP + infinitival-complement → STAY-SPLIT
  G5: Line A has only participial verbs → eligible despite a_verb heuristic

Stage 1 (surface-pattern) + Stage 2 (MorphGNT-aware filter).

Output kinds:
  subject-orphan-STRONG      Stage 1 + Stage 2 pass  → STRONG-MERGE-CANDIDATE
  subject-orphan-REVIEW      Stage 1 pass, Stage 2 unavailable or inconclusive
  subject-orphan-LONG-REVIEW merged > LENGTH_BACKSTOP chars → needs editorial

Usage:
  PYTHONIOENCODING=utf-8 py -3 -m validators.colometry.check_m4_gnt_1_subject_orphan
      [--book SLUG] [--chapter N] [--output PATH]
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
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

RULE_ID = "M4-GNT-1"
ERROR_CLASS = "DEVIATION"  # Layer 3 editorial rule

LENGTH_BACKSTOP = 130  # chars in merged line; backstop → LONG-REVIEW

# ─── Book slug list ────────────────────────────────────────────────────────────

_BOOKS: list[str] = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph",
    "phil", "col", "1thess", "2thess",
    "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet",
    "1john", "2john", "3john", "jude", "rev",
]

# ─── Already-applied skip-set ──────────────────────────────────────────────────
# Loci merged on 2026-05-11 sweep. (book, chapter, verse) tuples.
_APPLIED: frozenset[tuple] = frozenset({
    ("col", 3, 18),
    ("col", 3, 19),
    ("col", 3, 20),
    ("col", 3, 22),
    ("eph", 5, 25),
    ("eph", 6, 1),
    ("eph", 6, 5),
    ("1pet", 5, 5),
    ("acts", 16, 14),
    ("matt", 1, 19),
    ("1thess", 4, 16),
})

# ─── Surface-level patterns ────────────────────────────────────────────────────

# Greek leading connectives that BLOCK firing (line B is a coordinate or
# subordinate clause, not a bare-predicate orphan).
_LEADING_CONNECTIVES: frozenset[str] = frozenset({
    "καί", "καὶ", "δέ", "δὲ", "γάρ", "γὰρ", "οὖν", "ἀλλά", "ἀλλὰ",
    "ἤ", "εἰ", "ὅτι", "ἵνα", "ὅταν", "ὅτε", "ὡς", "ὥστε", "ὅπου",
    "ὅπως", "ἐάν", "εἰ", "ἄν", "μή", "οὐ", "οὐκ", "οὐχ",
    # Articles on line-B start: the NP would be a new phrase, not a bare predicate
    "ὁ", "ἡ", "τό", "οἱ", "αἱ", "τά", "τοῦ", "τῆς", "τῷ", "τήν",
    "τόν", "τῶν", "τοῖς", "ταῖς", "τούς", "τάς",
})

# Greek relative-pronoun forms that BLOCK firing on line B.
# Line B beginning with a relative pronoun is a relative clause modifying
# the NP on line A — it is NOT a bare orphan predicate.
# (Stage 1 surface guard; Stage 2 RR-pos check catches remaining cases.)
_RELATIVE_LEADS: frozenset[str] = frozenset({
    # ὅς declension (including accent variants)
    "ὅς", "ὃς", "ἥ", "ἣ", "ὅ", "ὃ",
    "οὗ", "ἧς", "ᾧ", "ᾗ", "ὅν", "ὃν", "ἥν", "ἣν",
    "οἵ", "οἳ", "αἵ", "αἳ", "ἅ", "ἃ",
    "ὧν", "οἷς", "αἷς", "οὕς", "οὓς", "ἅς", "ἃς",
    # ὅστις declension
    "ὅστις", "ἥτις", "ὅτι", "οἵτινες", "αἵτινες", "ἅτινα", "ἃτινα",
    "ὧντινων", "οἵστισιν", "ὅτου", "ὅτῳ",
})

# J3 speech-act verb lemmas: when line A contains one of these, it is a
# speech-intro tag (λέγων αὐτοῖς·), not a subject NP.
_SPEECH_LEMMAS: frozenset[str] = frozenset({
    "λέγω", "λαλέω", "εἶπον", "ἀποκρίνομαι", "ἐρωτάω", "φημί",
})

# MorphGNT POS codes for participial forms (verb with VerbForm=Part)
# MorphGNT parsing: pos starts "V", parsing[3] == 'P' → participle
def _is_participle(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "P"


def _is_infinitive(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "N"


def _is_finite(pos: str, parsing: str) -> bool:
    """Finite verb: indicative/subjunctive/imperative/optative."""
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in "ISDO"


# Periphrastic copulas (G3 exclusion)
_PERIPHRASTIC_LEMMAS: frozenset[str] = frozenset({"εἰμί"})

# Doxological line-B infinitive markers (G4 exclusion)
_AXIOS_RE = re.compile(r"Ἄξιος\s+εἶ\b", re.UNICODE)

# ─── MorphGNT per-verse token cache ──────────────────────────────────────────

_morph_cache: dict[str, dict] = {}


def _get_morph(slug: str) -> dict:
    """Return MorphGNT 4-tuple dict for a book slug; cache."""
    if slug not in _morph_cache:
        _morph_cache[slug] = load_morphgnt_book_with_lemma(slug)
    return _morph_cache[slug]


def _morph_tokens_for_verse(slug: str, ch: int, vs: int) -> list[tuple]:
    """Return list of (word, pos, parsing, lemma) for one verse."""
    data = _get_morph(slug)
    return data.get((ch, vs), [])


# ─── Stage-1 surface helpers ──────────────────────────────────────────────────

def _ends_in_comma_or_ano_teleia(line: str) -> bool:
    """Line A must end in `,` or `·` (ano teleia)."""
    s = line.rstrip()
    return s.endswith(",") or s.endswith("·") or s.endswith("·") or s.endswith("·")


def _leading_token(line: str) -> str:
    """Return the first whitespace-separated token of a line (NFC-stripped)."""
    parts = line.lstrip().split()
    return unicodedata.normalize("NFC", parts[0]) if parts else ""


def _is_connective_lead(line: str) -> bool:
    """True if line B begins with a Greek connective or article."""
    tok = _leading_token(line)
    # Strip punctuation from token for comparison
    tok_clean = strip_punctuation(tok)
    # Check both NFC and NFD-like variants by checking the cache set with
    # NFC-normalized tok
    return tok_clean in _LEADING_CONNECTIVES or tok in _LEADING_CONNECTIVES


def _is_bare_vocative_line(line: str) -> bool:
    """Rough check: line is a single-word vocative address (like `ἀδελφοί,`).
    These are R7 territory; M4-GNT-1 does NOT fire on purely-vocative line A.
    We use length heuristic: ≤2 tokens and no other content marker.
    The Stage 2 morphological check confirms.
    """
    tokens = [t for t in line.split() if strip_punctuation(t)]
    # Allow "ὁμοίως, νεώτεροι," style (2 content tokens) as eligible NP
    return len(tokens) <= 1


# ─── Stage 2 MorphGNT helpers ─────────────────────────────────────────────────

def _line_tokens_in_verse(
    line: str,
    verse_tokens: list[tuple],  # (word, pos, parsing, lemma) for the whole verse
) -> list[tuple]:
    """Return the subset of verse_tokens that appear in `line`.

    Uses a greedy forward-match against strip_punctuation(word). Returns
    empty list when MorphGNT data is unavailable.
    """
    line_words = [strip_punctuation(w) for w in line.split() if strip_punctuation(w)]
    if not line_words or not verse_tokens:
        return []
    result = []
    vt_idx = 0
    for lw in line_words:
        # Scan forward through verse_tokens for a match
        for scan in range(vt_idx, min(vt_idx + 10, len(verse_tokens))):
            vt_word = strip_punctuation(verse_tokens[scan][0])
            if unicodedata.normalize("NFC", vt_word) == unicodedata.normalize("NFC", lw):
                result.append(verse_tokens[scan])
                vt_idx = scan + 1
                break
    return result


def _has_any_finite_verb(morph_tokens: list[tuple]) -> bool:
    """True if any token in morph_tokens is a finite verb (Ind/Sub/Imp/Opt)."""
    return any(_is_finite(t[1], t[2]) for t in morph_tokens)


def _all_verbs_are_participial(morph_tokens: list[tuple]) -> bool:
    """True if every verbal token on the line is participial (no finite verb).
    An empty verbal list returns True (no finite verb = G5 eligible).
    """
    verbs = [t for t in morph_tokens if t[1].startswith("V")]
    return all(_is_participle(t[1], t[2]) or _is_infinitive(t[1], t[2]) for t in verbs)


def _line_b_has_finite_verb_lead(morph_tokens: list[tuple]) -> bool:
    """True if the first verbal token on line B is a finite verb (not participle)."""
    for t in morph_tokens:
        if t[1].startswith("V"):
            return _is_finite(t[1], t[2])
    return False


def _line_b_starts_with_participle(morph_tokens: list[tuple]) -> bool:
    """G1: True if line B's first verbal token is a participle (attributive modifier)."""
    for t in morph_tokens:
        if t[1].startswith("V"):
            return _is_participle(t[1], t[2])
    return False


def _line_b_periphrastic(morph_tokens_b: list[tuple], morph_tokens_a: list[tuple]) -> bool:
    """G3: True if line B looks like the copula of a periphrastic construction.

    Heuristic: line B contains a copula lemma (εἰμί) AND line A ends with a
    participle form → periphrastic. R5 governs; M4-GNT-1 does not fire.
    """
    b_has_copula = any(t[3] in _PERIPHRASTIC_LEMMAS for t in morph_tokens_b)
    a_ends_with_participle = bool(morph_tokens_a) and _is_participle(
        morph_tokens_a[-1][1], morph_tokens_a[-1][2]
    )
    return b_has_copula and a_ends_with_participle


def _line_a_verbless_complete(morph_tokens_a: list[tuple]) -> bool:
    """G2: True if line A appears to be a complete verbless nominal sentence.

    Heuristic: line A has no verbal tokens at all. Greek allows complete
    clauses by ellipsis of ἐστίν; these are not subject-NPs awaiting a
    predicate — they are predicate-NPs standing alone.
    A line with deictic ἰδού + NP is the canonical G2 case (Luke 1:38).
    """
    return not any(t[1].startswith("V") for t in morph_tokens_a)


# ─── Stage 2 — additional GC-exclusion helpers ───────────────────────────────

def _has_any_speech_verb(morph_tokens: list[tuple]) -> bool:
    """J3: True if line A contains a speech-act verb lemma.

    Lines like `λέγων αὐτοῖς·` or `προσευχόμενος καὶ λέγων·` are
    speech-intro tags, not subject NPs. The presence of λέγω / φημί /
    εἶπον on line A disqualifies M4-GNT-1 firing.
    """
    return any(t[3] in _SPEECH_LEMMAS for t in morph_tokens if t[1].startswith("V"))


def _has_unanchored_nom_participle(morph_tokens: list[tuple]) -> bool:
    """GC-ext: True if line A has a nominative participle NOT preceded by an article.

    A nominative participle that follows an article (RA) is a substantival
    participle — a genuine subject NP (e.g., `Ὁ καταλύων τὸν ναόν`).
    A nominative participle WITHOUT a preceding article is a circumstantial
    participle — a full adverbial clause (e.g., `λαβὼν τοὺς ἄρτους,`).
    Circumstantial participles on line A = complete clauses; M4-GNT-1 cannot fire.

    parsing[3] == 'P' (participle), parsing[4] == 'N' (nominative case).
    """
    prev_was_article = False
    for t in morph_tokens:
        if t[1] == "RA":
            prev_was_article = True
            continue
        if (t[1].startswith("V") and len(t[2]) >= 5
                and t[2][3] == "P" and t[2][4] == "N"):
            if not prev_was_article:
                return True
        prev_was_article = False
    return False


def _has_infinitive_only_verbs(morph_tokens: list[tuple]) -> bool:
    """G5-refined: True if all verbal tokens on line A are infinitives (no participles).

    The original G5 eligibility check used _all_verbs_are_participial, which
    inadvertently treated infinitives as participials (both are non-finite).
    Infinitive-only lines like `ἢ εἰπεῖν·` are verb-phrase complements, not
    subject NPs. This check blocks them from STRONG promotion.

    Returns True (block) if at least one infinitive exists AND no participle exists.
    Returns False (allow) if the only verbals are true participles.
    """
    verbs = [t for t in morph_tokens if t[1].startswith("V")]
    if not verbs:
        return False
    has_inf = any(len(t[2]) >= 4 and t[2][3] == "N" for t in verbs)
    has_ptc = any(len(t[2]) >= 4 and t[2][3] == "P" for t in verbs)
    return has_inf and not has_ptc


def _has_genitive_participle(morph_tokens: list[tuple]) -> bool:
    """Genitive-absolute guard: True if line A contains a genitive participle.

    A genitive participle (parsing[3]=='P', parsing[4]=='G') on line A signals
    a genitive absolute construction — a complete adverbial clause in its own
    right. M4-GNT-1 does NOT fire on genitive absolute line A.
    (Complements G3's periphrastic check with a dedicated gen-abs check.)
    """
    return any(
        t[1].startswith("V") and len(t[2]) >= 5 and t[2][3] == "P" and t[2][4] == "G"
        for t in morph_tokens
    )


def _line_b_starts_with_relative(morph_tokens: list[tuple]) -> bool:
    """True if line B's first token is a relative pronoun (MorphGNT pos == 'RR').

    A line B beginning with a relative pronoun is a relative clause that
    modifies the NP on line A — not a bare orphan predicate awaiting a subject.
    """
    for t in morph_tokens:
        return t[1] == "RR"
    return False


# ─── Chapter-level checker ────────────────────────────────────────────────────

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return M4-GNT-1 candidates for one chapter.

    Implements the check_book_chapter(book, chapter) -> List[Candidate] contract
    shared across colometry validators.
    """
    # Locate chapter file
    chapter_path: Optional[str] = None
    for slug, ch_num, fp in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_path = fp
            break
    if chapter_path is None:
        raise FileNotFoundError(
            f"v4/grc chapter not found: book={book!r} chapter={chapter}"
        )

    verses = parse_chapter_file(chapter_path)
    candidates: List[Candidate] = []

    for verse in verses:
        vs_ch = verse["ch"]
        vs_num = verse["vs"]
        lines: list[str] = verse["lines"]

        # Skip already-applied loci
        if (book, vs_ch, vs_num) in _APPLIED:
            continue

        # Load MorphGNT tokens for this verse (Stage 2 filter)
        verse_morph = _morph_tokens_for_verse(book, vs_ch, vs_num)

        for idx in range(len(lines) - 1):
            line_a = lines[idx]
            line_b = lines[idx + 1]

            # ── Stage 1 surface filter ────────────────────────────────────────

            # Line A must end in comma or ano teleia
            if not _ends_in_comma_or_ano_teleia(line_a):
                continue

            # Line B must NOT start with a leading connective
            if _is_connective_lead(line_b):
                continue

            # Bare-single-token vocative on line A: R7 governs
            if _is_bare_vocative_line(line_a):
                continue

            # G4: doxological Ἄξιος εἶ + line B infinitive — STAY-SPLIT
            if _AXIOS_RE.search(line_a):
                continue

            # Stage 1: line B starts with a relative pronoun → relative clause,
            # not a bare orphan predicate (surface guard; Stage 2 catches via RR pos)
            b_lead = strip_punctuation(_leading_token(line_b))
            if b_lead in _RELATIVE_LEADS:
                continue

            # Line B must have at least one token that looks like a verb
            b_tokens_raw = [t for t in line_b.split() if strip_punctuation(t)]
            if not b_tokens_raw:
                continue

            # ── Stage 2 MorphGNT-aware filter ────────────────────────────────

            morph_a = _line_tokens_in_verse(line_a, verse_morph)
            morph_b = _line_tokens_in_verse(line_b, verse_morph)

            stage2_available = bool(morph_a or morph_b)
            stage2_pass = False
            stage2_reason = "no-morph-data"

            if stage2_available:
                # G1: line B starts with attributive participle → STAY-SPLIT
                if morph_b and _line_b_starts_with_participle(morph_b):
                    stage2_reason = "G1-attributive-participle-lead-B"
                    # Not a candidate — skip
                    continue

                # G2: line A is a complete verbless nominal sentence → STAY-SPLIT
                if morph_a and _line_a_verbless_complete(morph_a):
                    stage2_reason = "G2-verbless-nominal-line-A"
                    continue

                # G3: periphrastic construction (R5 governs) → STAY-SPLIT
                if morph_a and morph_b and _line_b_periphrastic(morph_b, morph_a):
                    stage2_reason = "G3-periphrastic"
                    continue

                # G5 check: line A has only participial verbs → still eligible
                a_only_participial = _all_verbs_are_participial(morph_a)

                # Line A must NOT have a finite verb (would be a complete clause)
                if not a_only_participial and _has_any_finite_verb(morph_a):
                    stage2_reason = "A-has-finite-verb-already"
                    continue

                # Line B must have a finite verb as lead (not a bare noun chain)
                if morph_b and not _line_b_has_finite_verb_lead(morph_b):
                    stage2_reason = "B-no-finite-verb-lead"
                    continue

                # ── Additional GC-exclusion checks ────────────────────────────
                # Require morph_a non-empty for STRONG (cannot confirm line A
                # structure without morphological data for line A itself).
                if not morph_a:
                    stage2_reason = "no-morph-data-line-A"
                    stage2_pass = False
                    # Fall through to REVIEW-REQUIRED below — do NOT skip
                else:
                    # J3: line A has a speech-act verb (speech-intro tag)
                    if _has_any_speech_verb(morph_a):
                        stage2_reason = "J3-speech-verb-on-line-A"
                        continue

                    # GC-ext: line A has nominative participle without article
                    # (circumstantial participle = full adverbial clause)
                    if _has_unanchored_nom_participle(morph_a):
                        stage2_reason = "GC-nom-participle-no-article-line-A"
                        continue

                    # G5-refined: line A has only infinitives, no participles
                    # (infinitive complements ≠ subject NPs)
                    if _has_infinitive_only_verbs(morph_a):
                        stage2_reason = "G5-infinitive-only-line-A"
                        continue

                    # Genitive-absolute: line A has a genitive participle
                    if _has_genitive_participle(morph_a):
                        stage2_reason = "GC-genitive-absolute-line-A"
                        continue

                    # Relative-pronoun lead on B (stage 2 RR-pos check for
                    # cases the stage-1 surface guard may have missed)
                    if morph_b and _line_b_starts_with_relative(morph_b):
                        stage2_reason = "GC-relative-clause-lead-B"
                        continue

                    stage2_pass = True
                    stage2_reason = ""

            # ── Length backstop ───────────────────────────────────────────────
            merged = line_a.rstrip() + " " + line_b.lstrip()
            tag: str
            rationale: str

            if len(merged) > LENGTH_BACKSTOP:
                tag = "REVIEW-REQUIRED"
                rationale = (
                    f"M4-GNT-1 surface match but merged length {len(merged)} "
                    f"> {LENGTH_BACKSTOP}: editorial review required."
                )
            elif stage2_available and stage2_pass:
                tag = "STRONG-MERGE-CANDIDATE"
                rationale = (
                    "M4-GNT-1: subject NP on line A (ends `,`/`·`) + "
                    "bare finite predicate on line B. Stage 1+2 pass."
                )
            elif stage2_available:
                # Stage 2 demoted but already filtered exclusions above;
                # this path means morph data present but partial match
                tag = "REVIEW-REQUIRED"
                rationale = (
                    f"M4-GNT-1: Stage 1 pass, Stage 2 inconclusive "
                    f"[{stage2_reason}]. Manual review."
                )
            else:
                # No morph data: surface-only result
                tag = "REVIEW-REQUIRED"
                rationale = (
                    "M4-GNT-1: Stage 1 surface match, no MorphGNT data "
                    "for Stage 2 confirmation. Manual review."
                )

            verse_ref = f"{book.capitalize()} {vs_ch}:{vs_num}"
            # line_index within chapter: count lines before this verse + idx
            verse_line_offset = sum(len(v["lines"]) for v in verses if
                                    (v["ch"], v["vs"]) < (vs_ch, vs_num))
            line_global_idx = verse_line_offset + idx

            context = (
                f"  A: {line_a.strip()[:90]}\n"
                f"  B: {line_b.strip()[:90]}\n"
                f"  merged ({len(merged)} chars): {merged[:110]}"
            )

            candidates.append(
                emit_candidate(
                    verse_ref=verse_ref,
                    line_index=line_global_idx,
                    line_text=line_a.strip(),
                    rule=RULE_ID,
                    tag=tag,
                    error_class=ERROR_CLASS,
                    rationale=rationale,
                    context=context,
                )
            )

    return candidates


# ─── CLI entry point ──────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", help="Run on a single book slug (e.g. 'col')")
    ap.add_argument("--chapter", type=int, help="Run on a single chapter (requires --book)")
    ap.add_argument("--output", help="Write results to this file path (default: stdout)")
    args = ap.parse_args()

    all_candidates: list[Candidate] = []

    if args.book and args.chapter:
        all_candidates = check_book_chapter(args.book, args.chapter)
    elif args.book:
        book = args.book
        for slug, ch_num, _fp in iter_v4_chapters():
            if slug == book:
                all_candidates.extend(check_book_chapter(book, ch_num))
    else:
        for book in _BOOKS:
            for slug, ch_num, _fp in iter_v4_chapters():
                if slug == book:
                    all_candidates.extend(check_book_chapter(book, ch_num))

    strong = [c for c in all_candidates if c.tag == "STRONG-MERGE-CANDIDATE"]
    review = [c for c in all_candidates if c.tag == "REVIEW-REQUIRED"]

    out_lines = [
        "=" * 72,
        f"M4-GNT-1 (Subject-Orphan Predicate Completion) — {RULE_ID}",
        "=" * 72,
        f"Total candidates: {len(all_candidates)}",
        f"  STRONG-MERGE-CANDIDATE : {len(strong)}",
        f"  REVIEW-REQUIRED        : {len(review)}",
        "",
    ]

    for c in all_candidates:
        out_lines.append(f"[{c.tag}]  {c.verse_ref}  line_idx={c.line_index}")
        out_lines.append(f"  {c.rationale}")
        if c.context:
            out_lines.append(c.context)
        out_lines.append("")

    result = "\n".join(out_lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(result)
        print(f"Results written to {args.output}")
    else:
        print(result)

    sys.exit(1 if all_candidates else 0)


if __name__ == "__main__":
    main()
