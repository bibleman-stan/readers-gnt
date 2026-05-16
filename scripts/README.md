# scripts/

Active scripts for the GNT-Reader editorial loop. Everything here operates against `data/text-files/v4/grk/` (Greek source of truth) or its derivatives (`v4/eng-kjv/`, `books/*.html`). Historical / one-off / superseded scripts live in [`archive/`](archive/README.md).

## Core cascade (6)

These run as part of the standard editorial cascade per `CLAUDE.md`:

| Script | Role |
|---|---|
| **`regenerate_english.py`** | Greek edit → English regen (KJV-verbatim per ATU line via `atu_method.kjv_alignment.align_verse`) |
| **`build_books.py`** | English regen → HTML build (`books/*.html`) |
| **`verify_word_order.py`** | Three-check #1: every Greek word present in expected verse per SBLGNT |
| **`scan_english_drift.py`** | Three-check #2: English-quality drift detector (`--min-confidence high`) |
| **`scan_eng_kjv_coverage.py`** | Three-check #3: eng-kjv coverage parity (wired into pre-commit Phase 2 + `--baseline-check`) |
| **`v4_auto_fix.py`** | Mechanical-class fixes against `v4/grk/` (Layer 1 auto-corrections) |

## Macula syntax-tree helpers (4)

Read-only accessors over Macula Greek constituent data. Used by detectors under `validators/` and by ad-hoc analysis.

- **`macula_sentences.py`** — sentence-level constituent boundaries.
- **`macula_predication.py`** — predicate / clause-role labelling.
- **`macula_valency.py`** — verb-valency queries (argument structure).
- **`macula_wordgroups.py`** — word-group / phrase-cluster access.

The dedicated shared modules `validators/_shared/macula_clauses.py` and `validators/_shared/morphgnt_lookup.py` are the preferred entry points for detector code; the helpers here are for one-off Macula exploration.

## Layer-2 / Layer-3 detector scanners (~30)

Validator-style scanners that emit candidates for editorial review. Each targets a named pattern; some have already swept the corpus once and now serve as drift detectors.

### Scan-style (read-only candidate emitters)

`scan_acc_absolutes.py`, `scan_adverbial_speech_intro_split.py`, `scan_alla_antitheses.py`, `scan_asyndetic_lists.py`, `scan_bare_subject.py`, `scan_bridge_finite_verbs.py`, `scan_class_F_greek.py`, `scan_correlative_stacking.py`, `scan_crossverse_continuity.py`, `scan_dangling_relative.py`, `scan_dative_infinitive.py`, `scan_elided_parallels.py`, `scan_english_straddles.py`, `scan_genabs_absorbed.py`, `scan_gorgianic_pairs.py`, `scan_hoti_jammed_speech_intro.py`, `scan_ideou_subject_anticipation.py`, `scan_jammed_members.py`, `scan_line_ending_participles.py`, `scan_m1_reverse_drift.py`, `scan_main_clause_fefs.py`, `scan_multi_finite_line.py`, `scan_no_anchor_lines.py`, `scan_overstacked_qualifiers.py`, `scan_parallelism_consistency.py`, `scan_prep_catenae.py`, `scan_r18_class3_orphan_vocatives.py`, `scan_r23_dative_infinitive.py`, `scan_vocative_apposition.py`.

### Apply-style (write-back appliers, used during active sweeps)

- **`apply_no_anchor_merges.py`** — no-anchor-line merge applier (canon §3 anchor principle).
- **`apply_vocative_merges.py`** — vocative-line merge applier (companion to R18 own-line rule).
- **`sweep_r19_genabs.py`** — R19 genitive-absolute own-line sweep applier.
- **`participle_merge.py`** — participial-clause merge applier (selective; runs against flagged candidates only).
- **`detect_attributive_splits.py`** — attributive-construction split detector / applier hybrid.

Completed-sweep appliers move to `archive/` once the corpus is clean. The detector home for newly-codified canon rules is `validators/syntax/*` (Layer-1 break-legality, mechanical) and `validators/colometry/*` (higher-layer signature checks).

## Active tools (general utilities, 6)

Cross-cutting analytical / data-prep utilities used outside the editorial cascade itself.

- **`bezae_compare.py`** — Codex Bezae diff tool for textual-critical hot spots.
- **`build_lemma_index.py`** — lemma → occurrences index builder (search-page support).
- **`colometric_stylometry.py`** — colometric stylometry across the NT.
- **`english_quality_check.py`** — English-side spot-check harness (heavier than `scan_english_drift.py`).
- **`import_aland_pericopes.py`** — Aland pericope-boundary importer (cross-Synoptic alignment).
- **`ingest_tagnt_gaps.py`** — TAGNT Strong's-coverage gap audit / loader patcher.

## Diagnostic / audit one-offs (4)

Non-routine investigations kept in `scripts/` because they remain referenced by ongoing canon work.

- **`check_cascade_alignment.py`** — cascade-staleness diagnostic (pre-commit Phase 1 standalone runner).
- **`enumerate_m1_candidates.py`** — M1 bonded-pair candidate enumerator.
- **`audit_anaphoric_gen_abs_macula.py`** — anaphoric-genitive-absolute audit via Macula (`framework.md §1.1` bidirectional test).
- **`audit_hendiadys_merism_gnt.py`** — hendiadys / merism scope audit (canon §1 M1 paraphrase-test).

## Conventions

- Run from repo root with `PYTHONIOENCODING=utf-8` on Windows.
- Scripts that touch `v4/grk/` follow the cascade rule: Greek edit → English regen → HTML rebuild → three-check → commit → push.
- Scripts that wrap canon-named detectors emit `validators/_shared/` `Candidate` objects via `emit_candidate` (post verdict-layer migration, 2026-05-16).
- Validator-style scanners that complete their sweep move to `archive/`; the long-tail detectors remain here as drift detectors.
