# Unanchored English-alignment scan — bound the supplement-attachment problem

## Context

The Mark 4:6 alignment issue surfaced in the GNT-Reader-2 session:

- Greek line 1: `καὶ ὅτε ἀνέτειλεν ὁ ἥλιος` ("when the sun rose")
- Greek line 2: `ἐκαυματίσθη` (aorist passive 3sg — "it was scorched"; subject implicit in morphology)
- Greek line 3: `καὶ διὰ τὸ μὴ ἔχειν ῥίζαν ἐξηράνθη`

- KJV line 1: `But when the sun was up, it` ← "it" stranded
- KJV line 2: `was scorched;`
- KJV line 3: `and because it had no root, it withered away.`

**Diagnosis:** `atu_method.kjv_alignment.align_verse` anchors Strong's-tagged English words to their Greek targets. Words without Strong's tags (translation supplements: "it" / "he" / "they" / "and" / auxiliaries / particles) fall back to surface-proximity attachment with neighboring aligned content. When an unanchored pronoun's grammatical subject-of-verb is on the next Greek line, surface proximity attaches it to the previous line — the wrong line.

This is almost certainly NOT unique to Mark 4:6. The same failure mode applies anywhere KJV supplies a pronoun / auxiliary / particle that grammatically belongs to a subsequent line. A parallel directive runs in Tanakh; we expect more cases there due to stronger Hebrew pro-drop.

**This directive bounds the problem before solution design.** Diagnostic scan only; no fixes.

## Items

1. **Identify unanchored English tokens across the GNT corpus.** For each verse in `v4/eng-kjv/`, walk the KJV tokens and flag any token whose alignment to Greek (via Strong's number, per `atu_method.kjv_alignment`) is null/missing. Output: per-verse list of unanchored tokens with their current line position in v4.

2. **Classify by POS / function:**
   - **Pronouns**: it, he, she, they, we, you, I, him, her, them, us, me — highest-impact category for the Mk 4:6 failure shape
   - **Auxiliaries**: was, were, is, are, am, be, been, being, has, have, had, shall, will, would, should, may, might
   - **Articles**: the, a, an
   - **Conjunctions**: and, but, or, for, nor, so, yet
   - **Particles**: behold, lo, verily
   - **Other**: anything else surfaced; document the category as it emerges

3. **For each unanchored token, classify its line-attachment correctness:**
   - **OK**: token is on the line where its grammatical attachment target lives (e.g., "it" is on the same line as the verb it's the subject of)
   - **MIS-ATTACHED**: token is on the line BEFORE or AFTER its grammatical target's line
   - **AMBIGUOUS**: can't determine without judgment; surface for review

   Use Stanza English UD parsing to determine each unanchored token's grammatical attachment target. Match the target token's line position in v4/eng-kjv.

4. **Report per category:**
   - Total count of unanchored tokens
   - OK count
   - MIS-ATTACHED count + 5-10 representative examples (verse reference + current line + correct line + the unanchored token)
   - AMBIGUOUS count + sample

5. **Identify the top mis-attachment shapes:**
   - "Subject pronoun stranded at end of prior line before its verb" (Mk 4:6 shape) — count
   - "Auxiliary stranded after subject when verb is on next line" — count
   - "Conjunction stranded at end of prior clause" — count
   - Other shapes surfaced — count + describe

6. **Intervention-scope estimate for Stan:**
   - Whether the MIS-ATTACHED volume justifies an LLM-resolver pattern (sibling to `resolve_review_required.py`)
   - Whether a mechanical heuristic alone would cover the majority (e.g., "unanchored pronoun whose UD target is on next line → attach to next line" — pure rule, no LLM)
   - Hybrid: mechanical for high-confidence shapes; LLM-resolver for the residue
   - Cost estimate (if LLM-resolver path): expected Sonnet calls per pass corpus-wide

7. **Don't fix anything.** Diagnostic only. No alignment changes; no v4 modifications.

## Reporting

Reply at `directives/replies/2026-05-16-2300-unanchored-alignment-scan.md`:

- Per-category counts table (OK / MIS-ATTACHED / AMBIGUOUS)
- Top 5 mis-attachment shapes with counts
- Representative MIS-ATTACHED examples per category (5-10 each — verse reference + current line N + proposed line M + token + reasoning)
- Intervention-scope recommendation: LLM-resolver / mechanical-heuristic / hybrid / hand-fix-only
- Cost estimate (if LLM-resolver): expected Sonnet call volume + tier

## Audit triggers

Diagnostic scan. No alignment changes. No validator changes. No rule changes. **Audit-skippable per §7.4.**

If/when an intervention is selected, that's a separate directive with its own audit trigger assessment.

## Parallelism note

Runs independently of other queued directives. A parallel directive in `readers-tanakh/directives/pending/2026-05-16-2300-unanchored-alignment-scan.md` runs the same scan against Tanakh-Reader's Hebrew→KJV alignment. Cross-repo result comparison after both replies land will inform whether the resolver pattern should be cross-corpus-shared (`atu_method.alignment_resolution`) or per-repo.
