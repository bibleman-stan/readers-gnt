# 01 — Project Overview

## What This Is

A colometric reading edition of the Greek New Testament. The SBLGNT text is reformatted into **sense-lines (cola)** — each line is a natural breath unit based on Greek grammatical structure, designed for oral delivery and comprehension.

The website is served from GitHub Pages. No custom domain yet — currently at `bibleman-stan.github.io/readers-gnt/`. Domain registration is through Cloudflare (same account as bomreader.com). Domain candidates under consideration: `gntreader.com`, `gnt-reader.com`.

## Origin (2026-04-09)

Stan identified a gap in the scholarly landscape: while colometric *analysis* of the GNT exists, no one has produced a complete, publicly accessible *reading edition* formatted into sense-lines. The project was conceived, researched, prototyped, scaffolded, and built to a working v1 state in a single session.

## The Scholarly Landscape

### What exists (analysis, not reading editions):

1. **Lee & Scott, *Sound Mapping the New Testament* (2009, 2nd ed.)** — Developed a method for analyzing cola as sound units. The colon is established as the basic form of NT literature. Produced sample analyses of select passages, not a formatted reading text. A follow-up volume, *Sound Matters* (2018), collects a decade of sound mapping scholarship.

2. **Priscille Marschall, *Colometric Analysis of Paul's Letters* (2024, WUNT II)** — Most recent and methodologically rigorous work. Builds criteria for delineating κῶλα and periods from ancient Greek and Latin rhetorical treatises. Applied to 2 Cor 10–13. Shows how colometric analysis can inform repunctuation and exegetical debates. Published by Mohr Siebeck.

3. **Steven Runge, *Discourse Grammar of the Greek New Testament* (2010) / Lexham Discourse GNT (2007)** — Spent three years annotating the entire GNT with discourse features. Produces propositional displays (indented clause diagrams), not a reading format. Labels clause relationships.

4. **Stephen Levinsohn, *Discourse Features of New Testament Greek* (2000, 2nd ed.)** — Functional approach to information structure. Covers constituent order, sentence conjunctions, reference patterns, highlighting.

5. **OpenGNT (github.com/eliranwong/OpenGNT)** — Open-source Greek text tagged with Levinsohn discourse features, clause divisions marked with `°`. A dataset, not a reading app. Could be a useful data source.

6. **Ancient manuscript practice** — Codex Bezae and Codex Claromontanus were written in sense-lines (colometric layout). The idea of formatting the GNT this way has ancient precedent.

### What exists (reader's editions, not colometric):

- **Bibliotheca** — Strips chapters/verses for aesthetic book feel, keeps conventional paragraph breaks.
- **ESV Reader's Bible** — Similar approach, slightly more structured.
- **NIV *Books of the Bible*** — Uses line breaks to indicate "breaks in thought flow," closest in spirit but based on English translation, not Greek grammar.
- **Logos community** — A 2013 feature request for sense-line breaks for oral reading. Still not implemented 13 years later.

### The gap this project fills:

**Nobody has taken the Greek text, applied grammatically-motivated colometric line-breaking across the whole GNT, and produced a readable digital edition.** The theory is mature, the methodology has recent serious work, but the applied reading edition does not exist.

## Research Value

Colometric formatting reveals compositional structure that standard prose formatting obscures:

1. **Revealing authorial intent** — When you break Mark's parables into parallel cola, you see that Mark constructed carefully patterned oral compositions, not rambling narratives. The sense-lines make the composer visible behind the text.

2. **Revealing structure/consistency** — Once the text is in cola, you can count patterns: How does Mark's parable speech differ structurally from his narrative? The colometry becomes quantifiable data.

At a high level, consistent colometric formatting across the entire GNT enables several categories of inquiry:

- **Structural revelation** — compositional structures (tricolon, chiasm, parallel cola) become physically visible in the line layout without interpretive overlay. Structures hiding in prose formatting are exposed by the sense-lines.
- **Exegetical architecture** — authors' rhetorical strategies (Paul's argumentation structure, Mark's oral patterning, Luke's periodic restructuring) are laid bare in the colon structure. The line breaks show where an author shifts from assertion to evidence, from narrative to speech, from parallel to climactic.
- **Synoptic analysis** — when the same material appears in different Gospels, the colometric structure reveals how redactors transformed the compositional units. Mark's short paratactic cola vs. Luke's longer periodic reworking of the same content is measurable at the thought-unit level, not just the word level.
- **Quantitative stylometry** — colon-length distributions, break-point classifications, and rhetorical pattern frequencies become author-discriminating data points. This operates at the oral-compositional level rather than the vocabulary level where traditional stylometry works.
- **Discourse structure / pericope boundaries** — colometric shifts (short→long cola, paratactic→periodic) signal genre transitions within a text; may challenge traditional lectionary/pericope divisions
- **Translation methodology** — colometric edition maps original thought architecture for translators; reveals how many sense-lines in modern translations correspond to the author's actual cola
- **Oral performance reconstruction** — line length alternation is a performance score: short lines = emphasis/pause, long lines = momentum. Complete colometric data enables performance dynamics mapping across entire books.
- **Intertextuality / quotation detection** — when OT is quoted in NT, does the quotation maintain its original colometric structure or get restructured? The structural contrast or assimilation is visible.
- **Pedagogy** — Greek students get text formatted for comprehension (one thought per line) rather than for verse-lookup
- **Computational rhetorical figure detection** — chiasm, inclusio, ring composition involve patterned repetition at the colon level. With cola identified and numbered, automated detection becomes possible.
- **Diachronic comparison** — track how an author's style changes across their corpus (does Paul's colon length increase over his career? does Luke differ between Gospel and Acts?)

Additional research directions tracked privately.

## Project Siloing

Stan explicitly decided that this project should be **publicly siloed** from the BOM Reader project. No cross-references in README, CLAUDE.md, or any public-facing files. The connection exists in Stan's private memory files and internal knowledge, but the two projects present as independent efforts to the public.

**Why:** Multiple reasons Stan chose not to elaborate — respect this decision and never add cross-references.

---

## YLT English Layer

### What It Is

A toggleable public-domain English rendering aligned to the colometric line breaks. The translation is Young's Literal Translation (1898), chosen for its unmatched Greek word-order fidelity among English translations. The web app offers three display modes: **Greek** (default), **English** (YLT only), and **Both** (interleaved Greek and English lines).

### Why YLT

Young's Literal Translation preserves Greek clause structure, tense distinctions, and word order to a degree no other English translation approaches. This means:

- Colometric line breaks in the Greek correspond closely to natural break points in the YLT text
- The participial and subordinate clause structure that motivates the line breaks is preserved in the English rendering
- YLT's "woodenness" is a feature, not a bug: "having gone to the chief priest" preserves the participial structure that motivated the line break, where a smooth modern translation would obscure it

YLT is fully public domain (1898), available in machine-readable formats from eBible.org.

### Why This Matters

This decision transforms the project from a Greek specialist tool into a platform accessible to anyone. The potential audience expands from Greek readers (hundreds) to a much broader community (thousands):

- **Seminary students** preparing sermons or studying discourse structure
- **Pastors** without active Greek who want to see the text's compositional architecture
- **Digital humanities researchers** analyzing oral performance, rhetorical structure, or translation methodology without requiring Greek fluency
- **Literary scholars** interested in ancient compositional technique
- **Translation theorists** evaluating how sense-line structure maps across languages

The scholarly argument becomes **self-demonstrating**: a reader can toggle to English and immediately see that each line IS one thought. Instead of writing a paper that describes colometric principles, the site shows them.

### What This Is NOT

This is not a translation project. The colometric structure is the contribution; the language is just the rendering. The same line breaks drive both the Greek and English views. YLT is a lens through which non-Greek-readers can evaluate the colometric claims — nothing more.

### Two Claims, Not One

With the YLT layer, the project now makes two independent claims:

1. **These line breaks reflect Greek discourse structure** (the original colometric claim)
2. **The YLT splitting accurately represents those breaks in English** (the alignment claim)

Claim 2 is editorial work that can be wrong independently of claim 1. A bad YLT split could undermine confidence in the Greek colometry. Both claims must be reviewed and validated independently.

---

### Established — 2026-04-09
- Project conceived, researched, built to working v1
- Scholarly landscape mapped
- Four research advantages identified
- Siloing decision made

---

### Update — 2026-04-09
- YLT English layer integration decided
- Three display modes designed: Greek (default) / English (YLT) / Both (interleaved)
- Strategic rationale documented: broadens audience, makes colometric argument self-demonstrating
- YLT chosen for highest Greek word-order fidelity of any public domain English translation
- Two-claim framework established: colometric structure (claim 1) and YLT alignment accuracy (claim 2) are independently reviewable
