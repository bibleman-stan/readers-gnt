# v2-colometric — Syntax-tree-driven sense-lines

**Tier 2 of the GNT Reader text pipeline.** Mechanical colometric formatting produced using scholar-annotated clause boundaries from the Macula Greek syntax trees. This is the tier where external linguistic data enters the pipeline.

## What's here

260 `.txt` files, one chapter per file, organized in the same 27 book subfolders as every other tier:

```
v2-colometric/
  01-matt/matt-01.txt … matt-28.txt
  …
  27-rev/rev-01.txt … rev-22.txt
```

Each chapter file has verse numbers followed by line-broken Greek text, same output format as v1. Apparatus markers are stripped.

## What makes v2 different from v1

v1 is pattern matching on the surface of the text. v2 is pattern matching on the **parse tree** — specifically, the scholar-annotated clause and phrase boundaries published in the [Macula Greek](https://github.com/Clear-Bible/macula-greek) project by Clear Bible / Global Bible Initiative. Those trees give us:

- Verb-headed clause boundaries that are reliable even when surface punctuation is missing or misleading
- Participial phrase brackets (including genitive absolutes, which v1 frequently missed)
- Subordinate vs. coordinate disambiguation on ambiguous particles
- Reliable matrix-clause isolation when prose is embedded

The practical effect: v2 handles participial chains, genitive absolutes, and embedded prose segments significantly better than v1. It is the first tier whose output a careful reader can use without frequent obvious errors.

**v2 is still mechanical.** It does not apply any editorial judgment about rhetorical structure or cognitive-atomicity — those considerations enter at v3 and v4 respectively. It is a syntactic-surface improvement over v1, not a semantic one.

## How v2 relates to the other tiers

- **Upstream:** `sblgnt-source/` (for the text) plus the Macula Greek syntax trees (for the parse structure). v2 is NOT produced from v1.
- **Downstream:** `v3-colometric/` is produced from v2 by `scripts/v3_colometry.py`, which adds rhetorical-pattern awareness. v2 is v3's direct predecessor in the chain.

The pipeline graph:

```
sblgnt-source/ ─┬─> v1-colometric/  (auto_colometry.py, pattern-matched)
                └─> v2-colometric/  (v2_colometry.py, Macula-tree-driven)
                                   │
                                   ▼
                                v3-colometric/  (v3_colometry.py, rhetorical refinement of v2)
                                   │
                                   ▼
                                v4-editorial/   (project's documented colometric methodology applied to the text)
```

## Reproducing this tier

v2 depends on external Macula Greek syntax-tree data that is not bundled with this repository. To reproduce:

1. Obtain the Macula Greek syntax trees from [github.com/Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek).
2. Place or symlink them where `scripts/v2_colometry.py` expects to find them (see the script's top-of-file docstring for the exact path conventions).
3. Run:
   ```bash
   PYTHONIOENCODING=utf-8 py -3 scripts/v2_colometry.py
   ```

The script reads `sblgnt-source/` + the Macula trees and writes to `v2-colometric/{NN-book}/{abbrev}-{NN}.txt`.

## Status

**Frozen.** v2 has been superseded for editorial purposes by v3 and v4. It is retained as the reproducibility record, the "syntax-tree-driven baseline" for comparison, and the direct input to v3. The script that produces it is preserved but not actively developed.

## Attribution

The Macula Greek syntax trees are published by Clear Bible / Global Bible Initiative under a permissive license (see the macula-greek repository for current terms). Our use of those trees in this pipeline is gratefully acknowledged.

## License

Text content derived from the SBL Greek New Testament, © Society of Biblical Literature, CC-BY-4.0. Segmentation derived from the Macula Greek syntax trees (see above).
