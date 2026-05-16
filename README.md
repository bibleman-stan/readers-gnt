# GNT Reader — Colometric Reading Edition of the Greek New Testament

[![Text: CC-BY-4.0](https://img.shields.io/badge/SBLGNT-CC--BY--4.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Live](https://img.shields.io/badge/Live-gnt--reader.com-blue.svg)](https://gnt-reader.com)

A complete colometric reading edition of the SBL Greek New Testament. All 27 books (260 chapters) are formatted into **atomic thought units (ATUs)** — each line carries one ATU, a unit of thought defined by what a reader can process as a single complete thought. The formatting recovers compositional architecture that prose paragraphs hide.

**Live at [gnt-reader.com](https://gnt-reader.com)**

## The Gap This Fills

Colometric analysis of the Greek New Testament has a growing scholarly literature (Marschall 2024; Lee & Scott 2009; Nasselqvist 2015), yet no complete reading edition has been produced with consistent, stated criteria applied uniformly across the entire text. This project provides that edition.

## Method

This edition implements the **ATU Method** — a cross-corpus methodology framework maintained at [atu-method](https://github.com/bibleman-stan/atu-method) and shared with the sibling readers ([readers-tanakh](https://github.com/bibleman-stan/readers-tanakh), [readers-bofm](https://github.com/bibleman-stan/readers-bofm)).

Every editorial break is positively justified. Three forces operate at every candidate boundary:

- **Generative.** Each proposition splits by default (`framework.md §1.1`). Five structural justifications (J1–J5: parallel series, portrait accumulation, speech-act announcement, classical commata, substantive adjunct) extend the rule to non-predicated atomic thoughts.
- **Subtractive.** Four merge-overrides (M1–M4: Gorgianic bonded pair, verb-object clause-nucleus bond, bare-governor indivisibility, fragmented atomic thought) catch cases where naïve application of split-triggers would fragment a unit that should stay whole.
- **Diagnostic.** When the generative and subtractive forces leave a candidate boundary genuinely ambiguous, a single-image / camera-angle check is the tiebreaker.

The methodology is operated as what it is: a consistently-applied editorial practice grounded in target-language syntax, tested against the corpus, and refined by validator sweeps. It is not derived from a cognitive theory; no such claim is asserted (`framework.md §0.3`). External editorial overlays — NA28 paragraph structure, ancient codex colometric arrangements (Bezae, Claromontanus), Jerome's Vulgate cola — are preserved as textual evidence and consulted as historical pedigree (the per-cola format is not a new idea), but carry no authority in editorial decisions (`framework.md §0.4`). Modern colometric scholarship (Marschall 2024; Lee & Scott 2009; Nasselqvist 2015) is engaged as scholarly contemporary, not as method-derivation.

The pipeline uses **Macula Greek syntax trees** (Clear Bible, CC-BY-4.0) as the constituent-tree primitive and **MorphGNT** morphological tagging for pattern classification, with a UD-query validator suite implementing each canon rule and a pre-commit baseline check.

## Structural English Gloss

A toggleable English layer provides a structural gloss aligned by construction to the Greek ATUs. This is not a published translation — each English line was written to track its corresponding Greek colon, making the compositional structure visible without requiring Greek fluency.

## Features

- Dark-theme web reader with ATU-formatted display
- Structural English gloss (toggle between Greek / English / Both)
- Diacritic-free Greek search with lemma expansion
- Boolean search operators (AND, OR, NOT, NEAR, `"phrases"`)
- Scholarly corpus filters (Synoptics, Pauline, Johannine, General Epistles, etc.)
- Verse-level navigation and verse number toggle
- Codex Bezae colometric comparison tool

## What the Method Reveals

Colometric formatting exposes compositional structure that standard formatting obscures:

- Parallel cola, tricolon sequences, and chiastic structures become physically visible
- Authorial rhetoric (Paul's argumentation architecture, Mark's oral patterning, Luke's periodic restructuring) is laid bare in colon structure
- Synoptic comparison at the thought-unit level — how redactors transformed compositional units, not just vocabulary
- Colon-length distributions and break-point classifications become quantifiable stylometric data

## Data Sources

| Source | License | URL |
|--------|---------|-----|
| SBLGNT | CC-BY-4.0 | [github.com/morphgnt/sblgnt](https://github.com/morphgnt/sblgnt) |
| Macula Greek | CC-BY-4.0 | [github.com/Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek) |
| MorphGNT | CC-BY-SA | [github.com/morphgnt/sblgnt](https://github.com/morphgnt/sblgnt) |

## How to Cite

If you use this edition or build on it, please credit both the edition and the underlying methodology:

```
Stan the Bible Man. GNT Reader: A Colometric Reading Edition of the
Greek New Testament. 2026.
https://github.com/bibleman-stan/readers-gnt
https://gnt-reader.com

Stan the Bible Man. ATU Method: Computational Colometry for Canonical
Texts. 2026. https://github.com/bibleman-stan/atu-method
```

For machine-readable citation, see [CITATION.cff](CITATION.cff) (auto-rendered by GitHub's "Cite this repository" widget).

The methodology and Python apparatus that produced this edition live in [atu-method](https://github.com/bibleman-stan/atu-method) — the shared mechanical-layer repository consumed by this and sibling reader editions.

## License

- **SBLGNT text:** CC-BY-4.0 (Society of Biblical Literature and Logos Bible Software)
- **Macula Greek data:** CC-BY-4.0 (Clear Bible, Inc.)
- **Scripts and web app:** MIT License

## Contributing

Issues and suggestions are welcome via GitHub Issues. Colometric corrections should reference the specific verse and proposed line-break change with grammatical rationale.
