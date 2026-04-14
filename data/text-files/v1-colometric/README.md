# v1-colometric — Rule-based pattern-matched sense-lines

**Tier 1 of the GNT Reader text pipeline.** First-pass mechanical colometric formatting, produced by surface pattern matching on the SBLGNT prose.

## What's here

260 `.txt` files. Each file is one chapter of one New Testament book, broken into sense-lines by `scripts/auto_colometry.py`. Layout mirrors every other tier:

```
v1-colometric/
  01-matt/matt-01.txt … matt-28.txt
  …
  27-rev/rev-01.txt … rev-22.txt
```

Each chapter file has verse numbers followed by line-broken Greek text:

```
1:1
Βίβλος γενέσεως Ἰησοῦ χριστοῦ
υἱοῦ Δαυὶδ
υἱοῦ Ἀβραάμ.

1:2
Ἀβραὰμ ἐγέννησεν τὸν Ἰσαάκ,
…
```

Apparatus markers (`⸀ ⸁ ⸂ ⸃ ⸄ ⸅`) are stripped. Line breaks are introduced by surface pattern matching — punctuation, known subordinators (ἵνα, ὥστε, ὅτι, ὅταν, ἐάν, μήποτε, …), discourse particles (ἀλλά, δέ, γάρ in context), speech introductions (ἔλεγεν αὐτοῖς·), and a handful of other lexical cues.

## What v1 is good at (and what it isn't)

**v1 is a first draft.** It catches the low-hanging colometric structure: obvious subordinate clauses, discourse particles, speech introductions, basic punctuation-aligned breaks. It produces a reasonable starting point for further refinement.

**v1 is not scholar-annotated.** It has no knowledge of Greek syntax trees beyond what surface patterns reveal. It misses many participial phrases, mis-handles genitive absolutes, does not reliably isolate embedded prose from matrix clauses, and cannot distinguish subordinating from coordinating uses of the same particle. These shortcomings are what `v2_colometry.py` exists to fix.

**v1 is deterministic.** Running `auto_colometry.py` against the same `sblgnt-source/` content produces a bit-exact copy of this directory. This is important for reproducibility: someone verifying our work can reproduce v1 exactly.

## How v1 relates to the other tiers

- **Upstream:** `sblgnt-source/` (27 canonical SBLGNT book files). v1 reads source directly, not from `v0-prose/`. (v0 and v1 use the same content; v0 exists for navigation symmetry, not as v1's data source.)
- **Downstream:** v2 is not produced from v1. v2 re-segments from the source using Macula syntax trees. v1 and v2 are independent mechanical passes over the same source text; they are NOT in a chain. v3 is produced from v2 (not v1). v4 (hand editorial) is produced from v3.

The pipeline graph:

```
sblgnt-source/ ─┬─> v1-colometric/  (auto_colometry.py, pattern-matched)
                └─> v2-colometric/  (v2_colometry.py, Macula-tree-driven)
                                   │
                                   ▼
                                v3-colometric/  (v3_colometry.py, rhetorical refinement of v2)
                                   │
                                   ▼
                                v4-editorial/   (hand editing by the project editor)
```

v1 is a parallel branch, not a predecessor of v2. It exists as the "pattern-matching-only baseline" — a point of comparison for seeing what the syntax-tree pass adds.

## Reproducing this tier

```bash
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py
```

Or to regenerate a single book:

```bash
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py --book Mark
```

The script reads `data/text-files/sblgnt-source/*.txt` and writes to `data/text-files/v1-colometric/{NN-book}/{abbrev}-{NN}.txt`.

**Warning:** running `auto_colometry.py` will overwrite every file in this directory.

## Status

**Frozen.** v1 was the first machine tier. It has been superseded for editorial purposes by v2 (syntax-tree-driven) and subsequently by v3 and v4. v1 is retained as the reproducibility and methodology-comparison record, not as a working tier. The script that produces it is preserved but not actively developed.

## License

Derived from the SBL Greek New Testament, © Society of Biblical Literature, CC-BY-4.0.
