# v0-prose — Canonical SBLGNT prose, one chapter per file

**Tier 0 of the GNT Reader text pipeline.** This directory is our starting point: the SBLGNT text exactly as published, chapter-split into 260 files across 27 book subfolders.

## What's here

260 `.txt` files. Each file is one chapter of one New Testament book. Layout:

```
v0-prose/
  01-matt/matt-01.txt … matt-28.txt
  02-mark/mark-01.txt … mark-16.txt
  …
  27-rev/rev-01.txt … rev-22.txt
```

Each chapter file is flowing prose, one verse per line, verse markers preserved in the `{BookAbbrev} {chapter}:{verse}` format the SBLGNT uses:

```
Matt 1:1	Βίβλος γενέσεως Ἰησοῦ χριστοῦ υἱοῦ Δαυὶδ υἱοῦ Ἀβραάμ.
Matt 1:2	Ἀβραὰμ ἐγέννησεν τὸν Ἰσαάκ, Ἰσαὰκ δὲ ἐγέννησεν τὸν Ἰακώβ, …
```

**Apparatus markers retained.** The SBLGNT's manuscript-variant markers (`⸀ ⸁ ⸂ ⸃ ⸄ ⸅`) are preserved as-is. v0 is a faithful slice of the published scholarly text; the first stripping happens at the v1 step, deterministically, as part of `scripts/archive/auto_colometry.py`.

## How v0 relates to the other tiers

- **Upstream of v0:** `data/text-files/sblgnt-source/` — 27 whole-book files, the canonical SBLGNT distribution. v0 is a mechanical per-chapter split of those files with no content changes.
- **Downstream of v0:** `v1-colometric/` is produced from `sblgnt-source/` (not from v0 directly, though the content is equivalent) via `scripts/archive/auto_colometry.py`. v0 exists so that readers/reproducers have a per-chapter view of the starting text that visually matches every downstream tier's layout.

## Why we preserve this tier

Without v0, the pipeline story is asymmetric: `sblgnt-source/` has whole-book files, while v1/v2/v3/v4 have per-chapter files in book subfolders. A reader trying to diff "where we started" against "where we ended up" on a given chapter would have to chapter-split the source file themselves. v0 does that split once so the five-tier comparison has consistent shape all the way down.

## Reproducing this tier

```bash
PYTHONIOENCODING=utf-8 py -3 scripts/archive/build_v0_prose.py
```

This script reads `sblgnt-source/*.txt`, splits each book file into chapter files using the `{BookAbbrev} {chapter}:{verse}` line prefix, and writes the chapter files into the book-subfolder layout shown above. Running it against the same `sblgnt-source/` content produces a bit-exact copy of this directory.

## License

Content is from the SBL Greek New Testament, © Society of Biblical Literature, released under CC-BY-4.0. See the SBLGNT license at sblgnt.com for full terms.
