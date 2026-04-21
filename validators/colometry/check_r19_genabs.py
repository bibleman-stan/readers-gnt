"""
check_r19_genabs.py — Layer 2 colometry validator for Rule R19.

R19: Gen abs always gets its own line (no unless-cases, canon §3.10 / SJ #5).
Violation: line containing an anarthrous gen ptc + agreeing gen subject AND a
finite verb — gen abs co-linear with main clause.
Adnominal exclusion: gen article immediately before ptc.
PP-governed exclusion: preposition within 3 tokens before ptc or subject.
All violations are STRONG-SPLIT.
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
    is_genitive_participle,
    is_genitive_noun_or_pronoun,
    is_finite_verb,
)

RULE_ID = "R19"
ERROR_CLASS = "DEVIATION"   # Layer 3 editorial

# Known false positives — attributive NP structures that the adjacency heuristic
# can't resolve. Added 2026-04-20 after manual triage. If this list grows past
# ~5 entries, consider refining the Class B filter (inter-line NP awareness,
# wider adjacency window) rather than listing exceptions.
_KNOWN_FP_ALLOWLIST: frozenset[tuple[str, int, int]] = frozenset({
    ("john",  7, 38),   # ὕδατος ζῶντος — attributive, head ποταμοί scattered on same line
    ("2cor",  6, 16),   # θεοῦ ἐσμεν ζῶντος — head ναός on prior line (inter-line NP)
    ("heb",  11,  1),   # ἐλπιζομένων ὑπόστασις πραγμάτων — ptc-noun gap > 1
    ("matt",  9, 10),   # ἐγένετο + gen abs Septuagintalism — formulaic temporal frame, not independent
    ("phil",  2, 15),   # γενεᾶς σκολιᾶς καὶ διεστραμμένης — attributive adjective-modified NP, not gen abs
})

# Class A filter: finite verbs inside these subordinating words are NOT main-clause finites.
_SUBORDINATORS: frozenset[str] = frozenset({
    # temporal / causal conjunctions
    "ὅτε", "ὅταν", "ὡς", "ἐπεί", "ἐπειδή", "ὅπως",
    # relative pronouns (all common forms)
    "ὅς", "ἥ", "ὅ", "ὅν", "ἥν", "οἷς", "αἷς", "ὧν",
    "ὅσος", "ὅσοι", "ὅση", "ὅσα",
    "ὅστις", "ἥτις", "ὅτι",
    # interrogative-relative
    "ὅπου", "ὅθεν",
    # purpose/result subordinator
    "ἵνα",
    # interrogative / indirect-question markers
    "τί", "τίς", "τίνος", "τίνι", "τίνα", "τίνες", "τίνων", "τίσιν", "τίνας",
    "πῶς", "πότε", "διατί",
})

# Perception verbs whose genitive complements are NOT genitive absolutes:
# ἀκούω/ὁράω/βλέπω/θεωρέω/θεάομαι take a gen object + participial complement.
_PERCEPTION_LEMMAS: frozenset[str] = frozenset({
    "ἀκούω", "ὁράω", "βλέπω", "θεωρέω", "θεάομαι", "ὁρῶ", "εἴδω", "εἶδον",
})


def _is_perception_verb_complement(gen_ptc_idx: int, gen_subj_idx: int, tokens: list) -> bool:
    """Return True if a perception verb on the same line (within 5 tokens before the
    gen-noun/ptc pair) governs the gen noun + gen ptc as its complement.
    In that construction the genitive is an object-complement, not a gen abs.
    """
    min_idx = min(gen_ptc_idx, gen_subj_idx)
    for k in range(max(0, min_idx - 5), min_idx):
        _, _, _, lemma = tokens[k]
        if lemma in _PERCEPTION_LEMMAS:
            return True
    return False

BOOKS: list[str] = [
    "matt","mark","luke","john","acts","rom","1cor","2cor","gal","eph",
    "phil","col","1thess","2thess","1tim","2tim","titus","phlm",
    "heb","jas","1pet","2pet","1john","2john","3john","jude","rev",
]


def _finite_is_subordinate(finite_idx: int, line_tokens: list) -> bool:
    """Class A filter: return True if the finite verb at finite_idx is inside a
    subordinate clause (temporal/relative) on the same line as the gen abs.

    Detection: scan leftward from finite_idx; if we hit a subordinator lemma
    before the start of the line (or before a clause-boundary marker like δέ/καί
    that would open a new independent clause), the finite is subordinate.
    """
    for k in range(finite_idx - 1, -1, -1):
        lemma_k = line_tokens[k][3].lower().rstrip("·,.")
        # Strip accents by normalising? We match on the lemma field from MorphGNT
        # which is already citation form. Check membership directly.
        if lemma_k in _SUBORDINATORS:
            return True
        # A coordinating particle opening a new independent clause resets scope.
        # δέ / καί / γάρ / οὖν / ἀλλά at position > 0 mean we've crossed back
        # into independent territory — stop scanning.
        if lemma_k in {"δέ", "καί", "γάρ", "οὖν", "ἀλλά", "δέ"} and k > 0:
            break
    return False


def _is_attributive_gen_ptc(ptc_idx: int, subj_idx: int, line_tokens: list) -> bool:
    """Class B filter: return True if the putative gen abs is really an attributive
    genitival participle within a noun phrase.

    Signatures detected:
    1. Genitive article (τοῦ/τῆς/τῶν) immediately precedes the gen noun, AND the
       gen participle is immediately adjacent — e.g. τοῦ θεοῦ ζῶντος.
    2. Genitive article anywhere within 2 positions before the noun (article–noun
       split by an adverb, e.g. τοῦ ἤδη ζῶντος θεοῦ).
    3. No article but ptc is immediately adjacent to noun (within 1 position) AND
       the noun looks adnominal — i.e. there is a preceding nominative or
       accusative head noun within the line that the gen NP modifies.
       e.g. ὑγιαινόντων λόγων, υἱοὶ θεοῦ ζῶντος.
    """
    noun_idx = subj_idx

    # ── check 1 & 2: genitive article within 2 positions before the noun ──
    if noun_idx > 0:
        for k in range(max(0, noun_idx - 2), noun_idx):
            _, apos, apr, _ = line_tokens[k]
            if _is_article_gen(apos, apr):
                if abs(ptc_idx - noun_idx) <= 2:
                    return True

    # ── check 3: anarthrous but ptc immediately adjacent to noun AND the noun is
    #    governed by an immediately adjacent non-genitive head noun (within 2 pos).
    #    This catches e.g. υἱοὶ θεοῦ ζῶντος (υἱοί nom, immediately before θεοῦ)
    #    and ὑποτύπωσιν ἔχε ὑγιαινόντων λόγων (ὑποτύπωσιν acc, adjacent to the gen NP).
    #    It does NOT fire for δείπνου γινομένου or μὴ ὄντος νόμου because those gen
    #    nouns have no adjacent nom/acc/dat head noun within 2 positions.
    if abs(ptc_idx - noun_idx) <= 1:
        outer = min(ptc_idx, noun_idx)  # leftmost of the gen-ptc pair
        inner = max(ptc_idx, noun_idx)  # rightmost
        # Check immediately before the pair (up to 2 positions left of outer)
        for k in range(max(0, outer - 2), outer):
            _, pos_k, p_k, _ = line_tokens[k]
            if pos_k.startswith("N-") and len(p_k) >= 5 and p_k[4] in ("N", "A", "D"):
                return True
        # Check immediately after the pair (up to 2 positions right of inner)
        for k in range(inner + 1, min(len(line_tokens), inner + 3)):
            _, pos_k, p_k, _ = line_tokens[k]
            if pos_k.startswith("N-") and len(p_k) >= 5 and p_k[4] in ("N", "A", "D"):
                return True

    return False


def _is_article_gen(pos: str, parsing: str) -> bool:
    return pos == "RA" and len(parsing) >= 5 and parsing[4] == "G"


def _preceded_by_prep(tokens: list, idx: int, window: int = 3) -> bool:
    for k in range(max(0, idx - window), idx):
        if tokens[k][1] == "P-":
            return True
    return False

def _gen_abs_candidates(tokens: list) -> list[tuple]:
    """Return [(ptc_word, ptc_lemma, subj_word, subj_lemma, ptc_idx, subj_idx)]
    for likely gen abs on this line.

    MorphGNT detection path:
      - Gen ptc: pos starts "V", parsing[3]=="P", parsing[4]=="G"
      - Agreeing subject: pos in N-/RP/RD/A-, parsing[4]=="G",
        parsing[5] (number) + parsing[6] (gender) match ptc

    Edge cases: embedded gen abs inside FEF fires correctly (canon §1 Acts 1:9).
    Gen abs chain: each ptc tested independently; fires once per unique ptc.

    Class B filter applied here: attributive genitival participles (e.g.
    θεοῦ ζῶντος, ὑγιαινόντων λόγων) are excluded before any finite-verb check.
    """
    out = []
    for i, (w, pos, p, lemma) in enumerate(tokens):
        if not is_genitive_participle(pos, p):
            continue
        # Adnominal exclusion: gen article directly before this participle
        if i > 0:
            _, ppos, pp, _ = tokens[i - 1]
            if _is_article_gen(ppos, pp):
                continue
        # PP-governed exclusion: preposition within 3 positions before participle
        if _preceded_by_prep(tokens, i, window=3):
            continue

        ptc_num = p[5] if len(p) >= 6 else ""
        ptc_gnd = p[6] if len(p) >= 7 else ""

        # Search for agreeing genitive subject within 3 positions either side
        for j in range(max(0, i - 2), min(len(tokens), i + 3)):
            if j == i:
                continue
            w2, pos2, p2, lemma2 = tokens[j]
            if not is_genitive_noun_or_pronoun(pos2, p2):
                continue
            if _preceded_by_prep(tokens, j, window=3):
                continue
            num2 = p2[5] if len(p2) >= 6 else ""
            gnd2 = p2[6] if len(p2) >= 7 else ""
            if num2 == ptc_num and gnd2 == ptc_gnd:
                # Class B: skip attributive genitival participles (NP-internal)
                if _is_attributive_gen_ptc(i, j, tokens):
                    break
                # Perception-verb complement filter: gen noun + gen ptc as object
                if _is_perception_verb_complement(i, j, tokens):
                    break
                out.append((w, lemma, w2, lemma2, i, j))
                break
    return out


def _bind_line(text: str, verse_tokens: list) -> list:
    """Positionally match line words to verse morphology tokens."""
    pool: dict[str, list] = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    line_tokens = []
    for raw in text.split():
        c = strip_punctuation(raw)
        if c in pool and pool[c]:
            line_tokens.append(pool[c].pop(0))
    return line_tokens

def check_book_chapter(book: str, chapter: int) -> List[Candidate]:
    """Return Candidate objects flagging R19 violations in this chapter.

    Uses MorphGNT (not Macula ClauseInfo) because gen-abs detection requires
    per-word pos + parsing strings that ClauseInfo does not expose.
    """
    morph = load_morphgnt_book_with_lemma(book)
    if not morph:
        return []

    # Locate v4-editorial chapter file via iter_v4_chapters
    chapter_file: Optional[str] = None
    for slug, ch_num, fpath in iter_v4_chapters():
        if slug == book and ch_num == chapter:
            chapter_file = fpath
            break
    if chapter_file is None:
        raise FileNotFoundError(f"v4-editorial file not found: book={book!r} chapter={chapter}")

    verses = parse_chapter_file(chapter_file)
    display_book = book[0].upper() + book[1:]
    candidates: List[Candidate] = []
    line_index = 0   # 0-based across whole chapter

    for verse in verses:
        ch_num, vs_num = verse["ch"], verse["vs"]
        verse_tokens = morph.get((ch_num, vs_num), [])
        verse_ref = f"{display_book} {ch_num}:{vs_num}"

        for line in verse["lines"]:
            lt = _bind_line(line, list(verse_tokens))  # copy so pop doesn't exhaust
            gen_abs = _gen_abs_candidates(lt)
            if gen_abs:
                # Enumerate all finite verbs on the line; apply Class A filter
                # to each.  Only flag when at least one NON-subordinate finite
                # verb is co-linear with the gen abs.
                fins_with_idx = [
                    (idx, w, lm)
                    for idx, (w, pos, p, lm) in enumerate(lt)
                    if is_finite_verb(pos, p)
                ]
                # Filter out subordinate-clause finites (Class A)
                main_fins = [
                    (w, lm)
                    for idx, w, lm in fins_with_idx
                    if not _finite_is_subordinate(idx, lt)
                ]
                if main_fins:
                    if (book, ch_num, vs_num) in _KNOWN_FP_ALLOWLIST:
                        continue
                    ptc, ptc_l, subj, subj_l, _pi, _si = gen_abs[0]
                    fin, fin_l = main_fins[0]
                    context = _build_context(verses, ch_num, vs_num, line)
                    rationale = (
                        f"Gen abs ({ptc}/{ptc_l} + {subj}/{subj_l}) co-linear "
                        f"with finite verb {fin}/{fin_l} — R19: gen abs always own line"
                    )
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


def _build_context(verses: list[dict], ch: int, vs: int, target_line: str) -> str:
    """Return 1-2 adjacent lines from the same verse as context."""
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


def _format_markdown(all_candidates: List[Candidate]) -> str:
    if not all_candidates:
        return "## R19 violations\n\nNo violations found.\n"
    lines = [
        "## R19 violations",
        "",
        "Rule R19: genitive absolute always gets its own line (no unless-cases).",
        "All violations are STRONG-SPLIT.",
        f"Total: {len(all_candidates)}",
        "",
    ]
    for c in all_candidates:
        lines.append(f"- **{c.verse_ref}** (line {c.line_index}) [{c.tag}] {c.rationale}")
        lines.append(f"  > {c.line_text}")
        if c.context:
            lines.append(f"  *context:* {c.context}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R19 validator: genitive absolute must be on its own line."
    )
    parser.add_argument("--book", help="Restrict to one book (e.g. 'acts')")
    parser.add_argument("--chapter", type=int, help="Restrict to one chapter (requires --book)")
    parser.add_argument("--output", help="Write markdown report to this file path")
    args = parser.parse_args()

    if args.chapter and not args.book:
        parser.error("--chapter requires --book")

    books_to_run = [args.book] if args.book else BOOKS
    all_candidates: List[Candidate] = []

    for book in books_to_run:
        chapters_to_run = [args.chapter] if args.chapter else list(range(1, 200))
        for ch in chapters_to_run:
            try:
                candidates = check_book_chapter(book, ch)
                all_candidates.extend(candidates)
            except FileNotFoundError:
                break   # no more chapters for this book
            except Exception as exc:  # noqa: BLE001
                print(f"[R19] WARNING: {book} ch.{ch} skipped — {exc}", file=sys.stderr)

    report = _format_markdown(all_candidates)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"[R19] Report written to {args.output} ({len(all_candidates)} violations)")
    else:
        print(report)


if __name__ == "__main__":
    main()
