# Greek Constraint Catalog v1 — Design Proposal (PRE-BUILD)

**Status:** DRAFT — pre-build §7.3 adversarial audit dispatched; implementation gated on CLEAR / REVISE-applied verdict.

**Authored by:** vault-Claude (Opus 4.7).
**Trigger context:** Tanakh just shipped its Hebrew Constraint Catalog v1 + 26/26 Macula wiring (`readers-tanakh@7c919980c`). GNT needs the parallel — reindex the existing R-rules into the new three-stage architecture (cognitive identification → catalog audit → editorial review) per the 2026-05-17 framework supersession (`atu-method` commit `f6e834a`).

**§7.3 audit triggers fired:**
- Trigger #1 (new mechanism — Stage 2 catalog runner)
- Trigger #2 (new closed-list — Greek Constraint Catalog v1)
- Trigger #3 (new sub-category — verdict-family / tier system parallel to Hebrew catalog)
- Trigger #4 (new rules implicit in restructuring R-rule taxonomy into BIND/SPLIT/JUDGMENT-REQUIRED/INFORM)

PRE-BUILD audit MUST clear before any code lands.

---

## 1. Goal

Produce a Greek Constraint Catalog v1 (`canon/constraint_catalog_v1.md` — to be created) and Stage 2 audit runner (`scripts/atu_pipeline/audit_constraints.py` — to be created) that:

1. **Reindex existing R-rules** (R1, R2–R7 Layer 1, R8–R28, M4-GNT-1) into the three-stage architecture's Stage 2 format. Each entry: `id` / `name` / `verdict_family` / `tier` / `precedence` / `scope` / `exclusions` / `closed_lists` / `operationalization` / `examples`.
2. **Reuse existing detectors** at `validators/syntax/check_r{2-9}_*.py` and `validators/colometry/check_r{10,11,17,18,18a,19,25,28}_*.py` and `check_m4_gnt_1_subject_orphan.py` as the catalog's underlying check functions — wrap them with the new audit-output schema, do NOT re-implement.
3. **Match Tanakh's audit-output JSONL format** so the cross-corpus Stage 3 editorial-review tooling can consume both unchanged.

**Out of scope for this design:** Stage 1 (LLM ATU rendering) — GNT v4/grk is already rendered. Stage 3 (editorial-review surface) — separate work item.

---

## 2. Architectural alignment with Tanakh

| Concern | Tanakh | GNT (this design) |
|---|---|---|
| Catalog spec doc | `canon/constraint_catalog_v1.md` | `canon/constraint_catalog_v1.md` (NEW) |
| Stage 2 runner | `scripts/atu_pipeline/audit_constraints.py` | `scripts/atu_pipeline/audit_constraints.py` (NEW) |
| Check cluster modules | `scripts/atu_pipeline/checks_*.py` (5 clusters) | reuse `validators/{syntax,colometry}/check_r*.py` — register-and-adapt |
| Shared structural IR | `validators/_shared/macula_constituents.py` (token + constituent) | `validators/_shared/macula_clauses.py` (clause-level) + `validators/_shared/morphgnt_lookup.py` (word-level morph) — already present |
| Closed-list module | `validators/_shared/bonded_noun_pairs.py` | `validators/_shared/closed_lists_gnt.py` (NEW) — consolidates R8 framing devices, R9 subordinators, R10 cognition/speech verbs, R11/R28-ext speech frames, R18a-GNT patriarch variants, M4-GNT-1 SUBJECT_SHAPES, etc. |
| Coverage pre-flight | `audit_constraints.py --coverage-only` reports active/NYI | Same |
| Stage-1 input | `data/reports/atu_pipeline/<book>/chapter-NN.jsonl` (verse/source/draft/agreement) | Same shape; for GNT we synthesize from existing v4/grk as `draft = v4/grk content` (Stage 1 already applied historically) |
| Audit output | `chapter-NN-audit.jsonl` with per-verse firings | Same |

**Key divergence from Tanakh:** GNT has clause-level Macula IR + word-level morph rather than token-level constituent trees. Check operationalization for some Hebrew constraints uses `frame_args` / `antecedents` / `is_construct` etc.; the Greek equivalents are `ClauseInfo.has_participle` / `ClauseInfo.is_genitive_absolute` / `morphgnt_lookup.word_is_X` / `line_has_finite_verb`. The catalog must specify which API each check consumes.

---

## 3. Verdict-family / tier system

Parallel to Hebrew catalog. Four verdict families × two tiers:

- **BIND** — line N+1 must merge into line N (or vice versa); the boundary violates a structural constraint.
- **SPLIT** — line N must split; the line contains two propositions that fail the bidirectional test independently.
- **JUDGMENT-REQUIRED** — boundary requires editorial review; cannot be auto-applied.
- **INFORM** — diagnostic flag for editorial visibility; does not require action.

Tiers:

- **HARD** — auto-applied when LLM agreement is unanimous; surfaces for review only when Stage 1 disagrees.
- **ADVISORY** — always surfaces for review; never auto-applied.

GNT current R-rules already classify rules as Mechanical (Category A) / Editorial (Category B) / Layer 1 / Principle. Mapping:

| Current GNT class | Catalog v1 tier | Catalog v1 verdict family |
|---|---|---|
| Layer 1 R2–R7 (syntactic vetoes) | HARD | BIND (never-split) |
| Mechanical (Cat A) with MERGE_FORWARD/BACKWARD action | HARD | BIND |
| Mechanical (Cat A) with SPLIT action | HARD | SPLIT |
| Editorial (Cat B) — judgment-required | ADVISORY | JUDGMENT-REQUIRED |
| Principle (R27, R28) | — | (NOT a per-line check; cited by other entries' precedence/exclusions) |

---

## 4. Catalog entries — proposed inventory

**Total proposed: 18 active entries** (R12, R13, R14 retire from catalog as pure-editorial-judgment with no detector; R27, R28 are principles not entries).

### Layer 1 syntactic vetoes (HARD / BIND)

| ID | Name | Detector (existing) | Macula/MorphGNT op |
|---|---|---|---|
| R2 | Never dangle conjunction | `validators/syntax/check_r2_no_dangle_conjunction.py` | morphgnt POS check for CONJ at line-final |
| R3 | Never end on article | `validators/syntax/check_r3_no_line_end_article.py` | morphgnt POS check for DEF-art at line-final |
| R4 | Never split negation from negated | `validators/syntax/check_r4_no_split_negation.py` | morphgnt closed-list `οὐ/μή` + adjacent-verb check |
| R5 | Never split periphrastic | `validators/syntax/check_r5_periphrastic.py` | morphgnt `εἰμί` + participle on line break |
| R6 | Fixed phrases stay together | `validators/syntax/check_r6_fixed_phrases.py` | closed-list of canonical fixed phrases |
| R7 | Vocative units indivisible | `validators/syntax/check_r7_vocative_units.py` | morphgnt `word_is_vocative()` + adjacency |

### Layer 3 mechanical (HARD / BIND or SPLIT)

| ID | Name | Detector | Verdict | Op |
|---|---|---|---|---|
| R1 | No-anchor rule | `scripts/scan_no_anchor_lines.py` | BIND | morphgnt anchor-type check (finite/inf/pred-ptc/topic-NP) |
| R8 | Framing devices attach | `validators/syntax/check_r8_framing_devices.py` | BIND | closed-list FRAMING_DEVICES + line-final position |
| R9 | Subordinate clause openers | `validators/syntax/check_r9_subordinate_clause.py` | SPLIT | closed-list of subordinators + clause-initial position |
| R10 | ὅτι complementizer routing | `validators/colometry/check_r10_hoti_complementizer.py` | BIND (cognition class) or SPLIT (speech class) | closed-list cognition/speech verbs + ὅτι attachment |
| R11 | Speech-intro frame | `validators/colometry/check_r11_speech_intro.py` | BIND | closed-list speech verbs + dative addressee |
| R28-ext | Speech-act announcement after adverbial frame | `validators/colometry/check_r28_speech_act_frame.py` | SPLIT | speech-verb + adverbial-frame pattern |
| R17 | De-contrast overbreak | `validators/colometry/check_r17_de_contrast_overbreak.py` | BIND | δέ-contrast across line boundary without independent predication |
| R18a-GNT | Patriarch-deity-triad indivisibility | `validators/colometry/check_r18a_patriarch_triad.py` | BIND | closed-list patriarch-triad variants |
| R19 | Genitive absolute own-line | `validators/colometry/check_r19_genabs.py` | SPLIT | `macula_clauses.ClauseInfo.is_genitive_absolute` + co-linear-with-matrix detection |
| R25 | ὥστε short-consecutive-result binding | `validators/colometry/check_r25_hoste_consecutive_result.py` | BIND | ὥστε + word-count threshold |
| M4-GNT-1 | Subject-orphan predicate completion | `validators/colometry/check_m4_gnt_1_subject_orphan.py` | BIND | SUBJECT_SHAPES closed list + LEADING_CONNECTIVES guard |

### Layer 3 editorial (ADVISORY / JUDGMENT-REQUIRED)

| ID | Name | Detector | Op |
|---|---|---|---|
| R18 | Vocative rule (three-way refined) | `validators/colometry/check_r18_vocative.py` | morphgnt vocatives + categorical refinement |
| R20 | Participial phrase test | `scripts/scan_line_ending_participles.py` (scanner) | morphgnt participles + dependency |
| R23 | Dative subject of infinitive | `scripts/scan_r23_dative_infinitive.py` (scanner) | dat-NP + inf adjacency |

### Cross-verse / cross-clause (HARD / BIND)

| ID | Name | Detector | Op |
|---|---|---|---|
| GNT-cross-verse-continuity | Cross-verse grammatical continuity | NEW or borrow from Tanakh JM-cross-verse-continuity pattern | clause-final subordinator/article/conj/etc → BIND to next verse |

### Retired from catalog v1

- **R12, R13, R14** — editorial judgment, no detector, no closed list. Surface as Stage 3 editorial-review notes, not Stage 2 catalog entries.
- **R22, R24** — same.
- **R27, R28** — principles, cited in precedence/exclusions of other entries.

---

## 5. Catalog entry schema (per entry)

```yaml
constraint_id: R19
title: "Genitive absolute own-line"
verdict_family: SPLIT
tier: HARD
precedence: 3
status: DRAFT-promoting-from-canon-§3.10
scope: |
  Line containing an anarthrous genitive participle + agreeing genitive
  subject AND a finite verb (gen abs co-linear with main clause).
closed_lists: []
exclusions:
  - "Adnominal: gen article immediately before participle"
  - "PP-governed: preposition within 3 tokens before ptc or subject"
  - "R7 vocative-only line"
  - "R6 fixed-phrase span"
precedence_yields_to:
  - "R2-R7 (Layer 1 vetoes)"
  - "R6 (fixed phrases — known FP allowlist gap, see §3.10 detector notes)"
  - "R7 (vocative-only line — known detector gap)"
precedence_wins_over:
  - "M4-GNT-1 (per §3.18 universal exclusion #11)"
  - "R28-ext (per §3.6 R28-ext relation)"
operationalization: |
  Input: ClauseInfo per verse via macula_clauses.get_verse_clauses_detailed().
  For each clause where is_genitive_absolute=True, check if the clause's
  word span is co-linear with a finite verb on the same v4/grk line
  (via morphgnt_lookup.line_has_finite_verb()). If yes → fire SPLIT.
detector: validators/colometry/check_r19_genabs.py
detector_function: scan_chapter (existing)
adapter: scripts/atu_pipeline/checks_layer3_mechanical.py::check_r19_genabs
examples:
  positive:
    - "matt 1:18: τοῦ δὲ Ἰησοῦ Χριστοῦ ἡ γένεσις οὕτως ἦν. — gen abs split applies"
  negative:
    - "matt 9:10: ἐγένετο + gen abs Septuagintalism — KNOWN FP via _KNOWN_FP_ALLOWLIST"
```

---

## 6. Runner architecture

`scripts/atu_pipeline/audit_constraints.py` — parallel to Tanakh.

```
Inputs:
  --book <slug>            # e.g., matt
  --chapter <int>          # e.g., 1
  --coverage-only          # report active/NYI; do not audit

Loads:
  canon/constraint_catalog_v1.md → parse entries
  scripts/atu_pipeline/checks_*.py → cluster modules with @register_check
                                     decorators OR _CLUSTER_DIRECT_REGISTRATIONS
                                     adapter table (Tanakh pattern)
  Stage-1 JSONL at data/reports/atu_pipeline/<book>/chapter-NN.jsonl

Outputs:
  data/reports/atu_pipeline/<book>/chapter-NN-audit.jsonl
  Per-verse: {"verse": "1:1", "agreement": "...", "firings": [{constraint_id, ...}]}
```

**Cluster module organization (proposed):**

| Cluster file | Constraints |
|---|---|
| `scripts/atu_pipeline/checks_layer1_syntactic_vetoes.py` | R2, R3, R4, R5, R6, R7 |
| `scripts/atu_pipeline/checks_layer3_mechanical.py` | R1, R8, R9, R10, R11, R17, R18a-GNT, R19, R25, R28-ext, M4-GNT-1 |
| `scripts/atu_pipeline/checks_layer3_editorial.py` | R18, R20, R23 |
| `scripts/atu_pipeline/checks_cross_verse.py` | GNT-cross-verse-continuity |

Each adapter function has the same 5-arg signature as Tanakh (`verse_text`, `source_text`, `book_slug`, `chapter`, `verse_num`) and returns the same dict shape (`fires`, `verdict`, `reason`, `details`).

**Adapter pattern (per entry):**

```python
def check_r19_genabs(verse_text, source_text, book_slug, chapter, verse_num):
    from validators.colometry.check_r19_genabs import scan_chapter
    # Existing detector returns Candidate objects; wrap into catalog firing.
    candidates = scan_chapter(book_slug, chapter)
    fires = any(c.verse == verse_num for c in candidates)
    return {
        "fires": fires,
        "verdict": "SPLIT" if fires else "NO-EFFECT",
        "reason": "...",
        "details": {...},
    }
```

Existing validators run per-chapter; the adapter filters their output to the per-verse cell the catalog runner expects.

---

## 7. Closed-list module

`validators/_shared/closed_lists_gnt.py` (NEW) consolidates:

- `FRAMING_DEVICES` (R8: ἰδού, διό, οὖν, ἀλλά, γάρ, πλήν, τοιγαροῦν + νῦν δέ pair)
- `SUBORDINATORS` (R9: ἵνα, ὥστε, ὅτι, διότι, ὅταν, ὅτε, εἰ, ἐάν, καθώς, μήποτε)
- `R10_COGNITION_VERBS` (οἶδα, γινώσκω, ὁράω/εἶδον/βλέπω/θεωρέω, πιστεύω, ἐπίσταμαι, νομίζω/δοκέω, εὑρίσκω, ἀκούω, συνίημι)
- `R10_SPEECH_VERBS` (λέγω, εἶπον, γράφω, μαρτυρέω, ὁμολογέω, διδάσκω, κηρύσσω, ἀπαγγέλλω, καταγγέλλω, ἀναγγέλλω, ἐπαγγέλλομαι, προφητεύω)
- `R11_SPEECH_INTRO_VERBS` (λέγω, εἶπον, ἀποκρίνομαι, ἔφη)
- `R18a_PATRIARCH_TRIAD_VARIANTS` (4 surface-form variants)
- `M1_GNT_BONDED_PAIRS` (κόπος+μόχθος, χαίρειν+κλαίειν dual, Τολμηταί+αὐθάδεις)
- `M4_GNT_1_SUBJECT_SHAPES` (C1 vocative_address_NP, C2 np_with_appositive, C3 np_with_participial, C5 biographical_intro)
- `M4_GNT_1_LEADING_CONNECTIVES_BLOCK_FIRE` (καί, δέ, γάρ, οὖν, ἀλλά, ἤ, εἰ, ὅτι, ἵνα, ὅταν, ὅτε, ὡς, ὥστε, ὅπου, ὁ, ἡ, τό)

Currently these closed lists live INLINE in their respective `validators/{syntax,colometry}/check_r*.py` detector files. Consolidating into `closed_lists_gnt.py` lets the catalog spec reference them by canonical name and the detectors import them from one place (no drift between catalog and detector).

**Migration**: detectors should import from `closed_lists_gnt.py` rather than maintaining inline copies. This is the same anti-drift discipline the Tanakh `bonded_noun_pairs.py` consolidation enforced.

---

## 8. Open questions for the audit panel

1. **R12/R13/R14 retirement** — pure-editorial-judgment R-rules with no detector. Catalog v1 retires them from Stage 2 entirely and surfaces them at Stage 3 (editorial review). Is that the right call, or should the catalog carry an "ADVISORY-no-detector" slot so they appear in the coverage manifest?

2. **GNT-cross-verse-continuity** — does GNT need this as a NEW entry? Tanakh has JM-cross-verse-continuity (subordinator at verse-end, construct-state rectum, bare conjunction prefix, speech-frame). Greek equivalents: verse-final ὅτι / ἵνα / ὅταν (R9 subordinator); verse-final article (R3); verse-final καί (R8 framing). Are these already covered by R3/R8/R9 within-verse and a separate cross-verse rule would double-fire?

3. **Closed-list extraction** — moving FRAMING_DEVICES / SUBORDINATORS / etc. out of detector files and into `closed_lists_gnt.py` is a refactor with risk of breaking existing baseline counts (`validators/.baseline.json`). Should this be a separate PR with its own baseline-update commit, or bundled with the catalog v1 ship?

4. **Adapter overhead** — each adapter calls `scan_chapter(book_slug, chapter)` once per verse audited. For a 16-verse chapter that's 16 calls; each does a full chapter scan; total = 16×N detectors. Should adapters cache the chapter-level scan result so each detector runs once per chapter (not per verse)?

5. **Macula coverage limit** — Macula Greek covers SBLGNT books only (27 books). All R-rules are GNT-specific so this is moot for now, but if cross-corpus shared infrastructure is intended, it's a boundary worth surfacing.

6. **Stage-1 JSONL format for GNT** — Tanakh's `chapter-NN.jsonl` has `{verse, source, draft, agreement}`. GNT v4/grk is already rendered; we synthesize the JSONL with `draft = v4/grk content` and `agreement = "EXISTING-HAND-EDIT"`. Is this an acceptable synthetic Stage-1 state, or do we need a different sentinel?

7. **Existing baseline preservation** — `validators/.baseline.json` records current counts per rule. The Stage 2 catalog runner is independent of `run_all.py`. If both run on the same corpus they'd report twice. Resolution: catalog runner is the canonical Stage 2 source; `run_all.py` continues to gate commits via `--baseline-check`. Both can coexist. Is that the right boundary?

---

## 9. Implementation phases (gated on audit verdict)

**Phase 0 (this turn):** Design proposal + ≥2 parallel adversarial audits. STOP if any MUST-FIX.

**Phase 1 (next turn after audit clears):** Write `canon/constraint_catalog_v1.md`. Spec only; no runner code yet. ≥2 catalog-conformance audits on the spec.

**Phase 2:** Write `closed_lists_gnt.py` + migrate detectors to import. Update baseline. Two audits: structural correctness + import-graph integrity.

**Phase 3:** Write `scripts/atu_pipeline/audit_constraints.py` + cluster adapter modules. Smoke test on Matt 1. Coverage pre-flight should show ~18 active.

**Phase 4:** End-to-end integration test: synthesize chapter-01.jsonl for Matt 1 from v4/grk → run audit → inspect. Compare against `validators/run_all.py --baseline-check` on the same chapter; firings should align.

**Phase 5:** Commit + push with §7.5 audit-evidence in message.

---

## 10. Cross-corpus normalization (added per Stan 2026-05-17-1900)

**Strategic outcome:** This GNT work is also the opportunity to factor reusable Stage 2 infrastructure into `atu-method/` so that LXX and Vulgate readers (future corpora) can adopt the catalog architecture without re-inventing the runner/spec/IR.

### Candidate shared infrastructure (lives in `atu-method/`)

| Component | Proposed location in `atu-method/` | Corpus-agnostic? | Notes |
|---|---|---|---|
| Catalog spec format (entry schema, verdict-family taxonomy, tier system, header `implementation_conventions`) | `atu-method/docs/constraint-catalog-spec.md` | YES | One canonical spec; each corpus's catalog conforms |
| Catalog parser (`parse_catalog_master`) | `atu-method/atu_method/catalog_parser.py` | YES | Reads any conforming catalog markdown into `ConstraintEntry` dataclasses |
| Stage-2 runner skeleton (CHECK_REGISTRY, `audit_verse`, `audit_chapter`, `coverage_preflight`, arity-based dispatch, `_register_cluster_checks` pattern) | `atu-method/atu_method/stage2_runner.py` | YES | Per-corpus runner = thin shim that imports skeleton + binds cluster registrations |
| Stage-1 JSONL schema | `atu-method/docs/stage1-jsonl-schema.md` | YES | `{verse, source, draft, agreement, pass1, pass2, pass3, pass_errors}` already canonical |
| Stage-2 audit output JSONL schema | `atu-method/docs/stage2-jsonl-schema.md` | YES | `{verse, agreement, firings: [...]}` |
| Check function signature contract | `atu-method/docs/check-signature.md` | YES | 5-arg `(verse_text, source_text, book_slug, chapter, verse_num) → dict` |
| Production-tier render protocol (Opus 3-pass + agreement scoring) | `atu-method/atu_method/stage1_pipeline.py` (refactor of Tanakh's `render_atus.py`) | YES | Per-corpus = prompt + book-slug + Macula adapter |
| Pipeline orchestrator (Stage 1 → Stage 2 → Stage 3) | `atu-method/atu_method/pipeline.py` (refactor of Tanakh's `run_pipeline.py`) | YES | Per-corpus = thin Aramaic/Hebrew/Greek/Latin BAIL pre-flight |

### Stays per-corpus

| Component | Location | Why |
|---|---|---|
| Constraint catalog content | `<corpus>/canon/constraint_catalog_v1.md` | Each language has different syntactic rules |
| Macula IR adapter | `<corpus>/validators/_shared/<macula adapter>.py` | Token vs clause vs phrase IR differs by language |
| Closed-list module | `<corpus>/validators/_shared/closed_lists_<corpus>.py` | Lemmas are language-specific |
| Cluster check modules | `<corpus>/scripts/atu_pipeline/checks_*.py` | Operationalization-specific |
| Minimal-rubric prompt | `<corpus>/scripts/atu_pipeline/prompts/minimal_rubric_<lang>.md` | Language-specific syntactic constraints in the rubric |
| Detector logic | `<corpus>/validators/{syntax,colometry}/check_<rule>.py` (GNT) or cluster modules (Tanakh) | Corpus-specific |

### Migration order

1. **Phase 0 (next, before catalog v1):** Refactor Tanakh's `audit_constraints.py` and `render_atus.py` into `atu-method/atu_method/{stage2_runner,stage1_pipeline}.py` as importable skeletons. Tanakh's existing scripts become thin shims. **§7.3 audit-gated.**

2. **Phase 1:** Write `atu-method/docs/constraint-catalog-spec.md` codifying the spec format Tanakh `constraint_catalog_v1.md` already conforms to. **§7.3 audit-gated.**

3. **Phase 2:** Author `<GNT>/canon/constraint_catalog_v1.md` conforming to the spec; reuse the now-shared skeleton in `<GNT>/scripts/atu_pipeline/audit_constraints.py` (thin shim).

4. **Phase 3:** LXX + Vulgate adoption — corpus-specific catalog + Macula adapter + closed-lists; shared skeleton handles everything else.

### Risks of this normalization step

- **Coupling risk:** moving shared skeleton to `atu-method/` creates a cross-repo dependency (`readers-gnt` depends on `atu-method` at runtime). Current Tanakh already has this dependency for `atu-method/docs/*.md` references; runtime import dependency is a step further.
- **Versioning risk:** if `atu-method/atu_method/stage2_runner.py` changes, all corpora using it must agree. Solution: SemVer the API surface; corpora pin version in their CLAUDE.md.
- **Audit-load risk:** every shared-infrastructure change touches multiple corpora; §7.3 triggers fire often. Solution: explicit audit-skippable category for cosmetic / non-semantic refactors per `change-protocol.md §7.4`.

This Phase 0 (Tanakh refactor → shared skeleton) is what should ship BEFORE GNT catalog v1, because Tanakh is the working reference implementation; GNT becomes its first consumer.

---

## 11. Audit panel — dispatch parameters

≥2 parallel adversarial Sonnet agents on this design. Audit dimensions:

- **Audit A (architecture correctness + cross-corpus factoring):** Does the catalog format faithfully represent the existing R-rules without scope/precedence drift? Are the verdict-family/tier mappings defensible? Are there R-rules I'm proposing to retire (R12/13/14) that ACTUALLY have detector capability or shouldn't be retired? Are there NEW rules implicit in the restructuring that aren't being surfaced as such? **Cross-corpus angle:** is the §10 normalization (shared skeleton in `atu-method/`, per-corpus catalog/IR/closed-lists/clusters) the right cut, or are there cross-corpus concerns I'm leaving on the per-corpus side that should also normalize?

- **Audit B (operationalization correctness + migration risk):** Does each entry's claimed Macula/MorphGNT operationalization actually work given the existing `_shared/` API surface? Are there gaps where the existing detector relies on logic NOT yet exposed via `_shared/`? Are the closed-list extractions safe (no drift between catalog and detector after refactor)? Does the adapter pattern correctly preserve existing detector semantics? **Cross-corpus angle:** is the proposed migration order (Phase 0 Tanakh refactor → Phase 1 spec → Phase 2 GNT adoption) safe, or does it risk breaking Tanakh's working pipeline mid-refactor? Should the refactor happen on a branch with full validation before main lands?

Both audits return CLEAR / REVISE-applied / STOP-AND-SURFACE.

---

## 11. Recovery if audit returns STOP-AND-SURFACE

Per `feedback_never_skip_audit_gate`: hold all design state pending audit verdict. If MUST-FIX findings: revise this proposal, re-dispatch audits on the revision, repeat until CLEAR. No code lands until both audits clear.

If audit returns REVISE-applied with embedded specifics: apply the specifics inline, re-audit OR proceed to Phase 1 per audit-α/audit-β's joint sign-off.

---

End of design proposal.
