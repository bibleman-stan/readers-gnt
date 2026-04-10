# GNT Reader — Colometric Reading Edition of the Greek New Testament

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Text: CC-BY-4.0](https://img.shields.io/badge/SBLGNT-CC--BY--4.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Live Site](https://img.shields.io/badge/Live-GitHub%20Pages-orange.svg)](https://bibleman-stan.github.io/readers-gnt/)

A complete colometric reading edition of the SBL Greek New Testament. All 27 books (260 chapters, 7,957 verses) are formatted into sense-lines based on Greek grammatical structure. Each line represents one thought, one breath, one image — recovering the oral-compositional structure the original authors intended.

## The Gap This Fills

Colometric analysis of the Greek New Testament has a growing scholarly literature (Lee & Scott 2009; Marschall 2024; Nässelqvist 2015), yet no complete reading edition of the GNT has been produced with consistent, stated criteria applied uniformly across the entire text. This project provides that edition, together with the tooling and validation data to reproduce and critique it.

## Method

A four-tier pipeline produces the colometric text:

1. **Pattern-matching** — subordinating conjunctions, discourse markers, and clause-level break points informed by Wallace (1996)
2. **Syntax-tree-driven clause boundaries** — leveraging Macula Greek / Clear Bible (CC-BY 4.0) treebank data
3. **Rhetorical pattern refinement** — parallel stacking, staccato commata, complement merging, verb valency validation
4. **Editorial hand** — manual review and correction (in progress)

**Key principles:**
- No arbitrary length constraints (line length is authorial, not editorial)
- No punctuation-based rules (punctuation is editorial, not original)
- Every break rule is grammatically warranted and author-agnostic
- Syntactic clause ≠ colometric colon (a central finding of this work)

## Validation

| Benchmark | Agreement |
|-----------|-----------|
| Marschall (2023) hand analysis | 3/5 example passages match |
| Codex Bezae colometric agreement (best automated tier) | 61.3% |
| Hand-crafted gold standard, Mark 4 | 39% exact match (v3 more granular) |

## Data Sources

| Source | License | URL |
|--------|---------|-----|
| SBLGNT | CC-BY-4.0 | [github.com/morphgnt/sblgnt](https://github.com/morphgnt/sblgnt) |
| Macula Greek | CC-BY 4.0 | [github.com/Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek) |
| MorphGNT | CC-BY-SA | [github.com/morphgnt/sblgnt](https://github.com/morphgnt/sblgnt) |
| Codex Bezae XML | Public | [github.com/itsee-birmingham/codex-bezae](https://github.com/itsee-birmingham/codex-bezae) |

## Features

- Dark-theme web reader with sense-line display
- Verse-level navigation (`#book-chapter-verse`)
- Diacritic-free Greek search with lemma expansion (type `ακουω` to find all 52 inflected forms)
- Boolean search operators (AND, OR, NOT, NEAR, `"phrases"`)
- Punctuation and verse number toggle
- Codex Bezae comparison tool

## Build Pipeline

```bash
PYTHONIOENCODING=utf-8 py -3 scripts/v2_colometry.py    # Macula clause boundaries
PYTHONIOENCODING=utf-8 py -3 scripts/v3_colometry.py    # Rhetorical refinement
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py     # Text → HTML
```

## How to Cite

```
[Author]. GNT Reader: A Colometric Reading Edition of the Greek New Testament.
[Year]. Available at: https://bibleman-stan.github.io/readers-gnt/
```

## License

- **SBLGNT text:** CC-BY-4.0 (Society of Biblical Literature and Logos Bible Software)
- **Macula Greek data:** CC-BY 4.0 (Clear Bible, Inc.)
- **Scripts and web app:** MIT License

## Contributing

Issues and suggestions are welcome via GitHub Issues. Colometric corrections should reference the specific verse and proposed line-break change with grammatical rationale.
