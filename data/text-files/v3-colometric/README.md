# v3-colometric — Rhetorical-pattern refined sense-lines

**Tier 3 of the GNT Reader text pipeline.** The last mechanical tier. Takes v2's syntax-tree-driven segmentation and applies rhetorical-pattern detection to refine it further.

## What's here

260 `.txt` files, one chapter per file, organized in the same 27 book subfolders as every other tier:

```
v3-colometric/
  01-matt/matt-01.txt … matt-28.txt
  …
  27-rev/rev-01.txt … rev-22.txt
```

Same output format as v1 and v2: verse numbers followed by line-broken Greek text, apparatus markers stripped.

## What v3 adds over v2

v2 gives us reliable clause and phrase boundaries from the Macula syntax trees. v3 is where we layer project-specific rhetorical-pattern awareness on top of that structure:

- Parallelism detection (stacked `μέν…δέ` contrasts, antithesis, parisosis)
- Discourse-marker framing (γάρ, οὖν, ἄρα, διό anchoring in argumentative chains)
- Speech-introduction formatting (keeps `ἔλεγεν αὐτοῖς·` on its own line)
- Vocative isolation (each vocative on its own line per the universal vocative rule)
- A handful of other rhetorical-pattern refinements that accumulated during v3's development

The practical effect: v3 reads more naturally than v2 in dialogue passages, argumentative periods, and stacked-parallelism registers. It is the last mechanical tier — every subsequent change is editorial.

**v3 is still mechanical.** It does not apply the atomic-thought / cognitive-hierarchy / register-sensitive rule set that governs v4. Those rules — and the case-by-case judgments they license — are the province of the methodology-application layer.

## How v3 relates to the other tiers

- **Upstream:** `v2-colometric/`. v3 reads v2 chapter files directly and rewrites them with rhetorical-pattern refinements.
- **Downstream:** `v4-editorial/`. v4 is what you get when the project's documented colometric methodology is applied to v3 — via a mix of systematic scan-and-apply tools (the vocative pass, the no-anchor pass, the Goldilocks refinement, Class F audits) and case-by-case editorial decisions where the rule set underdetermines. v4 is the single source of truth for the web app; v3 is v4's starting point.

The pipeline graph:

```
sblgnt-source/ ─┬─> v1-colometric/  (auto_colometry.py, pattern-matched)
                └─> v2-colometric/  (v2_colometry.py, Macula-tree-driven)
                                   │
                                   ▼
                                v3-colometric/  (v3_colometry.py, rhetorical refinement)
                                   │
                                   ▼
                                v4-editorial/   (project's documented colometric methodology applied to the text)
```

v3 is the machine / human boundary. Everything upstream of v3 is deterministic; everything downstream (v4) is editorial.

## Reproducing this tier

```bash
PYTHONIOENCODING=utf-8 py -3 scripts/v3_colometry.py
```

The script reads `data/text-files/v2-colometric/{NN-book}/*.txt` and writes to `data/text-files/v3-colometric/{NN-book}/{abbrev}-{NN}.txt`. Running it against the same v2 content produces a bit-exact copy of this directory.

## Historical note on the build pipeline

Before `v4-editorial/` existed (sessions 1-5 of the project), `v3-colometric/` was the source that `scripts/build_books.py` read to generate the public HTML. The build script still contains a v3 fallback path — if a chapter file is missing from v4-editorial for some reason, build_books.py falls back to the v3 version. In practice, this fallback is dead code: every chapter has been editorially reviewed and lives in v4. The fallback is preserved as a safety net and as documentation of the v3 → v4 transition.

## Status

**Frozen.** v3 is the final machine tier. It has been superseded for editorial purposes by v4. It is retained as the reproducibility record, the "complete mechanical baseline" for diffing against the editorial hand, and the build pipeline's historical fallback. The script that produces it is preserved but not actively developed.

## License

Text content derived from the SBL Greek New Testament, © Society of Biblical Literature, CC-BY-4.0. Segmentation ultimately derived from Macula Greek (via v2) and project rhetorical-pattern refinements (via v3).
