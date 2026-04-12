# GNT Reader — Colometric Reading Edition of the Greek New Testament

[![Text: CC-BY-4.0](https://img.shields.io/badge/SBLGNT-CC--BY--4.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Live](https://img.shields.io/badge/Live-gnt--reader.com-blue.svg)](https://gnt-reader.com)

A complete colometric reading edition of the SBL Greek New Testament. All 27 books (260 chapters) are formatted into sense-lines — each line represents one atomic thought, one image, one breath unit, motivated by source-language syntax. The formatting recovers compositional architecture that prose paragraphs hide.

**Live at [gnt-reader.com](https://gnt-reader.com)**

## The Gap This Fills

Colometric analysis of the Greek New Testament has a growing scholarly literature (Marschall 2024; Lee & Scott 2009; Nasselqvist 2015), yet no complete reading edition has been produced with consistent, stated criteria applied uniformly across the entire text. This project provides that edition.

## Method

Each line break is warranted by four convergent criteria:

1. **Atomic thought** — the line contains one complete propositional unit
2. **Single image** — one mental picture per line
3. **Breath unit** — a natural pause boundary for oral delivery
4. **Source-language syntax** — the break falls at a Greek grammatical joint

These criteria are grounded in ancient rhetorical theory (Pseudo-Demetrius *On Style*, Aristotle *Rhetoric*, Cicero *Orator*), modern colometric scholarship (Marschall, Lee & Scott, Nasselqvist), and cognitive linguistics (Chafe's intonation units, Miller's chunking).

The pipeline uses **Macula Greek syntax trees** (Clear Bible, CC-BY-4.0) for clause boundary detection and **MorphGNT** morphological tagging for pattern classification, followed by editorial review.

## Structural English Gloss

A toggleable English layer provides a structural gloss aligned by construction to the Greek sense-lines. This is not a published translation — each English line was written to track its corresponding Greek colon, making the compositional structure visible without requiring Greek fluency.

## Features

- Dark-theme web reader with sense-line display
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

```
[Author]. GNT Reader: A Colometric Reading Edition of the Greek New Testament.
[Year]. Available at: https://gnt-reader.com
```

## License

- **SBLGNT text:** CC-BY-4.0 (Society of Biblical Literature and Logos Bible Software)
- **Macula Greek data:** CC-BY-4.0 (Clear Bible, Inc.)
- **Scripts and web app:** MIT License

## Contributing

Issues and suggestions are welcome via GitHub Issues. Colometric corrections should reference the specific verse and proposed line-break change with grammatical rationale.
