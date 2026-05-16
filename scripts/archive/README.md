# scripts/archive/

This directory holds scripts that produced the v0–v3 colometric corpus tiers (and adjacent one-time tools) during the project's bootstrap phase. They are no longer part of the active editorial loop.

## Architecture transition

Until 2026-04 the project ran a machine pipeline:

```
sblgnt-source/  →  v0-prose/  →  v1-colometric/  →  v2-colometric/  →  v3-colometric/
```

Each tier was produced by a Python script reading the previous tier and applying one layer of refinement (chapter-splitting → sentence breaks → clause breaks via Macula syntax trees → rhetorical-pattern refinement). The output of the last machine tier (`v3-colometric/`) was then **hand-edited across all 260 chapters** into `v4-editorial/`.

After `v4-editorial/` reached 260/260 coverage and was confirmed as the single source of truth for Greek text (per `CLAUDE.md`), the producer scripts stopped being part of the active loop. They are preserved here for provenance — the v0–v3 corpus directories remain in `data/text-files/` as frozen scaffolding documenting the bootstrap path, and any future re-derivation would need these scripts.

The active editorial loop is now:

```
v4-editorial/  →  regenerate_english.py  →  eng-gloss/  →  build_books.py  →  books/*.html
```

See `private/01-method/colometry-canon.md` §10 (2026-04-26 later⁷ entry) for the audit trail behind this transition.

## Archived scripts

### Tier producers

- **`build_v0_prose.py`** — produced `v0-prose/` (sblgnt-source split into chapter files). Last v0 update: 2026-04-14.
- **`auto_colometry.py`** — produced `v1-colometric/` (sblgnt-source → v1, sentence-level breaks). Last v1 update: 2026-04-09.
- **`v2_colometry.py`** — produced `v2-colometric/` (v1 → v2, Macula-driven clause-level breaks). Last v2 update: 2026-04-09.
- **`v3_colometry.py`** — produced `v3-colometric/` (v2 → v3, rhetorical-pattern refinement; the "last machine tier"). Last v3 update: 2026-04-09.

### Editorial / analytical tools

- **`v4_pauline_review.py`** — one-time editorial review pass that wrote initial `v4-editorial/` files for 87 Pauline chapters by applying the colometric framework to v3 input. Output has since been hand-edited; the script is historical.
- **`diagnostic_scanner.py`** — line-auditing tool. Input paths resolve to `v3-colometric/`. The `validators/` Layer 2 checks (operating on `v4-editorial/`) supersede it.

### English-gloss seeders

- **`generate_english_glosses.py`** — original from-scratch seeder for `eng-gloss/` (read v4 with v3 fallback, wrote new English glosses). Superseded by `regenerate_english.py`, the incremental-regen tool with a skip-guard for the active loop.
- **`generate_pauline_english.py`** — Pauline-subset variant of the seeder with v1/v3/v4 three-tier fallback. Predates full v4 coverage. Zero inbound references at archive time.

### 2026-05-16 archival wave (validators/colometry/ takeover + completed sweeps)

When the verdict-layer migration and R8/R9/R10/R17 implementations shipped (commits `c1886b60` → `0a7cfb36`), the canonical detector home became `validators/syntax/` and `validators/colometry/`. The following 12 `scripts/` entries — appliers that finished sweeping, validators superseded by canon-named successors, and a self-retired investigation — moved here.

#### Validators superseded by `validators/colometry/*`
- **`validate_r11_speech_intro.py`** — superseded by `validators/colometry/check_r11_speech_intro.py`.
- **`validate_r18_vocative.py`** — superseded by `validators/colometry/check_r18_vocative.py`.
- **`validate_r19_genabs.py`** — superseded by `validators/colometry/check_r19_genabs.py`. (Note: `scripts/sweep_r19_genabs.py` remains active as the sweep applier.)

#### Investigation superseded by canon-named successor
- **`scan_hoti_complement.py`** — superseded by `validators/colometry/check_r10_hoti_complementizer.py` (commit `c1886b60`, R10 canon §3.5). The script was a pre-canon exploratory survey; canon §3.5 + R10 validator now own the detector logic.

#### Appliers — sweep complete
- **`apply_line_splits.py`** — generic line-split applier from the early hand-edit phase; one-off completed.
- **`apply_m1_merges.py`** — M1 bonded-pair merge applier; sweep complete corpus-wide.
- **`apply_vocative_rule.py`** — vocative own-line applier; sweep complete and now enforced by `validators/colometry/check_r18_vocative.py`.

#### ὅτι-lead flip sweeps (canon §3.5 R10)
- **`flip_hoti_to_lead.py`** — Greek-side ὅτι-lead flip sweep; complete.
- **`flip_that_to_lead.py`** — English-side companion sweep (KJV "that" alignment); complete.

#### Other one-offs
- **`filter_reverse_splits.py`** — auxiliary filter for completed split-sweep; no longer referenced.
- **`scan_emdash_midline.py`** — self-retired per inline rationale (corpus convention settled; no remaining inbound calls).
- **`sweep_r19_correct_acc.py`** — one-off accusative-correction bug-fix sweep on R19 output; complete.

## What stays in `scripts/`

The active editorial loop and any scripts referenced by it remain in `scripts/`:

- `regenerate_english.py` (active English-regen tool — replaces `generate_english_glosses.py`)
- `build_books.py` (HTML generator; reads `v4-editorial/` only as of this commit)
- `validators/_shared/morphgnt_lookup.py` (used by `validators/common.py`; relocated 2026-04-28 from `scripts/`)
- `validators/_shared/macula_clauses.py` (used by `validators/common.py`; relocated 2026-04-28 from `scripts/`)
- `v4_auto_fix.py` (mechanical fixes against `v4-editorial/`)
- All `scan_*.py` / `apply_*.py` / `validate_*.py` / `sweep_*.py` scripts (validator-driven sweeps against `v4-editorial/`)
- All `macula_*.py` scripts (Macula syntax-tree access)
- `bezae_compare.py`, `verify_word_order.py`, `colometric_stylometry.py`, `english_quality_check.py`, etc.

## Re-running an archived script

The scripts are preserved as-is. To re-run one (rare; almost always the wrong move), set `PYTHONIOENCODING=utf-8` and run from the repo root:

```
PYTHONIOENCODING=utf-8 py -3 scripts/archive/v3_colometry.py
```

Be aware that input/output paths still point at the historical tier directories (`v2-colometric/`, etc.). Re-running would overwrite frozen scaffolding — almost never the desired outcome.
