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

- `v4/eng-kjv/` — English structural glosses aligned line-for-line with `v4/grk/`. The active English-regen tool is `scripts/regenerate_english.py` (incremental, with skip-guard). The original from-scratch seeder (`generate_english_glosses.py`) and a Pauline-only seeder variant (`generate_pauline_english.py`) were archived 2026-04-26 and live under `scripts/archive/`.

And one untouched reference:

- `sblgnt-source/` — 27 canonical SBLGNT book files, one file per book, whole-book prose. Never modified. This is the upstream text `v0-prose/` is derived from. CC-BY-4.0 per the SBLGNT license.

## Why all five tiers are preserved

**Transparency.** Anyone checking our work can see exactly what the text looked like at every stage. "Where did we start, where did we go, how did it look along the way" is fully inspectable.

**Reproducibility.** v0 → v1 → v2 → v3 is a deterministic pipeline. Given our source data (`sblgnt-source/` for v0, plus the Macula Greek syntax trees for v2), anyone can re-run `scripts/archive/auto_colometry.py`, `scripts/archive/v2_colometry.py`, and `scripts/archive/v3_colometry.py` against these inputs and produce bit-exact copies of the v1/v2/v3 tiers. The v3 → v4 transition is NOT deterministic; it's editorial hand work, and the rules governing it are documented in `handoffs/` (see the colometric methodology references).

**Honesty.** Unlike the Book of Mormon Reader (a sibling project which starts from Royal Skousen's published sense-lines), the GNT Reader had no pre-existing scholar-annotated colometric edition to lean on. The three mechanical tiers are the record of how we bootstrapped our own starting point from raw SBLGNT prose plus external syntax-tree data. Preserving them is the honest way to show the mechanical baseline we built before any editorial decisions entered.

**Comparability.** A researcher interested in machine-only colometric segmentation can cite v1, v2, or v3 as-is without needing to consult the methodology-applied layer. A researcher interested in the methodology's contribution can diff v3 against v4 to measure the value-add of the rule-application layer.

## Two kinds of reproducibility

The five tiers divide into two reproducibility regimes, and the distinction matters:

- **v0, v1, v2, v3 are bit-exactly reproducible.** Given the same inputs (`sblgnt-source/` for v0/v1; `sblgnt-source/` + Macula Greek trees for v2; v2 output for v3), running the corresponding script produces a byte-for-byte copy of the tier. Anyone can confirm our mechanical output.
- **v4 is methodologically checkable, not bit-exactly reproducible.** The rule set is documented, but case-by-case judgment enters where rules conflict or underdetermine, and two careful readers applying the same methodology will occasionally reach different break decisions on hard passages. What v4 IS reproducible as: any chapter can be audited against the documented rule set in `handoffs/02-colometry-method.md` (the private methodology canon) or its public summaries to confirm whether breaks conform to the rules. Disagreement at an individual line is resolvable by consulting the methodology, not by dispute over "what Stan happened to type." The contribution lives in the rule set; v4 is its application, not its stenography.

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

## How to reproduce the pipeline

```bash
# v0 — chapter-split the SBLGNT source prose
PYTHONIOENCODING=utf-8 py -3 scripts/archive/build_v0_prose.py

# v1 — mechanical pattern-matched pass (reads sblgnt-source/, writes v1-colometric/)
PYTHONIOENCODING=utf-8 py -3 scripts/archive/auto_colometry.py

# v2 — Macula syntax-tree pass (requires Macula Greek trees; reads sblgnt-source/ + Macula, writes v2-colometric/)
PYTHONIOENCODING=utf-8 py -3 scripts/archive/v2_colometry.py

# v3 — rhetorical-pattern refinement (reads v2-colometric/, writes v3-colometric/)
PYTHONIOENCODING=utf-8 py -3 scripts/archive/v3_colometry.py
```

The producer scripts were moved to `scripts/archive/` on 2026-04-26 once `v4/grk/` reached 260/260 coverage and the v0–v3 tiers were no longer in the active editorial loop. They are preserved unchanged for re-derivation; running them today will overwrite the frozen tier corpora.

v4 is not produced by a single reproducible script because rule application involves judgment calls at the margin. It is, however, methodologically checkable — see the two-reproducibility-regimes note above and `handoffs/04-editorial-workflow.md` for the editorial workflow and the rule set the editor applies.

## For the curious

- Project overview: `handoffs/01-project-overview.md`
- Architecture: `handoffs/03-architecture.md`
- Editorial workflow: `handoffs/04-editorial-workflow.md`
- Live site: gnt-reader.com
- Source repository: github.com/bibleman-stan/readers-gnt
