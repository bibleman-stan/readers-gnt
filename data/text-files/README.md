# GNT Reader — Text Pipeline

This directory holds the GNT Reader's colometric text and the pipeline that produces it, from the canonical SBLGNT source to the reading edition served at gnt-reader.com.

## Canonical pipeline (mechanical-first)

Per `~/repos/atu-method/docs/framework.md` (the canonical cross-corpus methodology), the pipeline is **mechanical-first**:

```
v0    Source text (SBLGNT prose, verse markers)
  ↓
v1    Parse-derived clause units (SBLGNT-lowfat clause-atoms + MorphGNT)
  ↓
v1.5  Binding rules applied — ATU candidate groups (the SBLGNT-native fabric)
  ↓
v2    (Optional) narrow-task LLM adjudication on residual cases   ← NOT YET BUILT for GNT
  ↓
v3    Editorial review → final reading edition                    ← NOT YET DONE for GNT
```

> **Status (2026-05-22): GNT is live at v1.5.** What gnt-reader.com serves is the
> mechanical-first **v1.5** baseline (clause-atoms + the ported Layer-1 binding rules),
> a "deploy-then-refine" edition — NOT a methodology-complete one. A genre-spread
> idea-unit measurement put it at ~72% (pervasive over-splitting: dependent clauses
> severed from their heads). **v2-adjudication and v3-editorial are the unbuilt path to
> a refined edition.** The deployed directory is named `v1.5` (not `v4`) so the label
> never overstates the stage.

## Directory layout

| Directory | What it is |
|---|---|
| `v0-prose/` | **v0** — Canonical SBLGNT prose, one chapter per file (apparatus markers `⸀ ⸁ ⸂ ⸃ ⸄ ⸅` retained). The starting point. |
| `v1.5/grk/` (+ `v1.5/eng-kjv/`) | **v1 + v1.5 — the currently deployed edition.** Clause-atoms off SBLGNT-lowfat + MorphGNT with the ported Layer-1 binding rules applied (R3/R4/R7/R8/R9/R10), surface-order emit. **The single source of truth the web app builds from** (`scripts/build_books.py` → `books/*.html`). A mechanical-first v1.5 baseline — not yet methodology-complete. (Renamed from `v4/grk` on 2026-05-22, since "v4" overstated the stage.) |
| `sblgnt-source/`, `tagnt-source/` | Upstream Greek text + apparatus. Never modified. |
| `_retired-2026-04-mechanical-tiers/` | The prior `v1-/v2-/v3-colometric` machine tiers (surface-pattern → Macula-syntax → rhetorical, frozen 2026-04-09). Their v1/v2/v3 numbering was a **different, retired** scheme that collides with the canonical v1/v1.5/v2/v3 stages above — archived here to prevent confusion. Producers at `scripts/archive/`. |

**v2 and v3 do not exist yet.** v2 (optional narrow-task LLM adjudication on the v1.5 residuals — cf. the BoFM `data/text-files/v2-adjudicated/` override layer) and v3 (editorial review) are the unbuilt path from the current v1.5 baseline to a refined edition.

Plus one non-Greek directory:

- `v1.5/eng-kjv/` — English structural glosses aligned line-for-line with `v1.5/grk/`. The active English-regen tool is `scripts/regenerate_english.py` (incremental, with skip-guard). The original from-scratch seeder (`generate_english_glosses.py`) and a Pauline-only seeder variant (`generate_pauline_english.py`) were archived 2026-04-26 and live under `scripts/archive/`.

And one untouched reference:

- `sblgnt-source/` — 27 canonical SBLGNT book files, one file per book, whole-book prose. Never modified. This is the upstream text `v0-prose/` is derived from. CC-BY-4.0 per the SBLGNT license.

## The retired machine tiers (`_retired-2026-04-mechanical-tiers/`)

Before the SBLGNT-native mechanical-first fabric existed, the GNT Reader bootstrapped its own colometric starting point through three machine passes — `v1-colometric` (surface-pattern), `v2-colometric` (Macula-syntax), `v3-colometric` (rhetorical) — culminating in a hand-edited `v4` editorial layer. **That entire v1→v4 scheme is retired.** Its numbering collided with the canonical v1/v1.5/v2/v3 stages (a `v4` that the framework has no place for), which is precisely why it was archived under `_retired-2026-04-mechanical-tiers/` and the deployed dir was relabeled to `v1.5` on 2026-05-22.

The retired tiers are preserved for **transparency and reproducibility of the bootstrap**: given `sblgnt-source/` (+ Macula Greek trees), re-running the frozen producers reproduces them bit-for-bit — `scripts/archive/auto_colometry.py` (→ v1), `scripts/archive/v2_colometry.py` (→ v2), `scripts/archive/v3_colometry.py` (→ v3). They are NOT part of the live pipeline and must not be confused with the canonical stages. Running the producers today overwrites the frozen tier corpora.

## Navigation

Every tier uses the same book-subfolder layout:

```
vN/
  01-matt/matt-01.txt … matt-28.txt     (28 chapters)
  02-mark/mark-01.txt … mark-16.txt     (16)
  03-luke/luke-01.txt … luke-24.txt     (24)
  04-john/john-01.txt … john-21.txt     (21)
  05-acts/acts-01.txt … acts-28.txt     (28)
  06-rom/rom-01.txt … rom-16.txt        (16)
  07-1cor/1cor-01.txt … 1cor-16.txt     (16)
  08-2cor/2cor-01.txt … 2cor-13.txt     (13)
  09-gal/gal-01.txt … gal-06.txt        (6)
  10-eph/eph-01.txt … eph-06.txt        (6)
  11-phil/phil-01.txt … phil-04.txt     (4)
  12-col/col-01.txt … col-04.txt        (4)
  13-1thess/1thess-01.txt … 1thess-05.txt (5)
  14-2thess/2thess-01.txt … 2thess-03.txt (3)
  15-1tim/1tim-01.txt … 1tim-06.txt     (6)
  16-2tim/2tim-01.txt … 2tim-04.txt     (4)
  17-titus/titus-01.txt … titus-03.txt  (3)
  18-phlm/phlm-01.txt                    (1)
  19-heb/heb-01.txt … heb-13.txt        (13)
  20-jas/jas-01.txt … jas-05.txt        (5)
  21-1pet/1pet-01.txt … 1pet-05.txt     (5)
  22-2pet/2pet-01.txt … 2pet-03.txt     (3)
  23-1john/1john-01.txt … 1john-05.txt  (5)
  24-2john/2john-01.txt                  (1)
  25-3john/3john-01.txt                  (1)
  26-jude/jude-01.txt                    (1)
  27-rev/rev-01.txt … rev-22.txt        (22)
```

Total: 260 chapters, consistent shape in every tier.

## How to reproduce the live edition (mechanical-first)

The deployed `v1.5/grk` is produced deterministically by the SBLGNT-native fabric:

```bash
# v1 + v1.5 — clause-atoms off SBLGNT-lowfat + MorphGNT, with the ported
# Layer-1 binding rules applied (surface-order emit). Per chapter:
#   py -3 scripts/sblgnt_generate.py <Book> <chap> --write   → writes v1.5/grk/<book>/<slug>-NN.txt
# (omit --write to print the chapter for inspection). Fabric + binding-rule
# implementations live in scripts/sblgnt_v1_fabric.py.
PYTHONIOENCODING=utf-8 py -3 scripts/sblgnt_generate.py Matt 2 --write

# build — assemble the reading edition the web app serves
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py   # v1.5/grk + v1.5/eng-kjv → books/*.html
```

The retired bootstrap tiers in `_retired-2026-04-mechanical-tiers/` are reproducible via their frozen `scripts/archive/` producers — see "The retired machine tiers" above; they are not part of this pipeline.

## For the curious

- Project overview: `handoffs/01-project-overview.md`
- Architecture: `handoffs/03-architecture.md`
- Editorial workflow: `handoffs/04-editorial-workflow.md`
- Live site: gnt-reader.com
- Source repository: github.com/bibleman-stan/readers-gnt
