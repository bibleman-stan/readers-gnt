# 01 — Project Overview

## What This Is

A colometric reading edition of the Greek New Testament. The SBLGNT text is reformatted into **sense-lines (cola)** — each line is a natural breath unit based on Greek grammatical structure, designed for oral delivery and comprehension.

The website is served from GitHub Pages. No custom domain yet — currently at `bibleman-stan.github.io/readers-nt/`. Domain registration is through Cloudflare (same account as bomreader.com). Domain candidates under consideration: `ntreader.com`, `gntreader.com`, `nt-reader.com`.

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

## Four Research Advantages

Stan identified these during the initial design conversation:

1. **Revealing authorial intent** — When you break Mark's parables into parallel cola, you see that Mark constructed carefully patterned oral compositions, not rambling narratives. The sense-lines make the composer visible behind the text.

2. **Revealing structure/consistency** — Once the text is in cola, you can count patterns: How does Mark's parable speech differ structurally from his narrative? Does Luke's Areopagus speech use different clause lengths than his travel narrative? The colometry becomes quantifiable data.

3. **Text-critical implications** — If a variant reading breaks or preserves a colometric pattern, that's evidence for or against it. If the "harder reading" also happens to be the reading that maintains a tricolon, that's a new kind of argument. Marschall touched on this with repunctuation, but nobody has systematized it.

4. **Stylometry-plus** — Average colon length per author, participial chain frequency, μέν/δέ density, ἵνα-clause frequency, tricolon vs. bicolon ratios. Mark vs. Luke vs. Paul vs. Hebrews become quantitatively distinguishable at the colometric level, not just the word level.

## Project Siloing

Stan explicitly decided that this project should be **publicly siloed** from the BOM Reader project. No cross-references in README, CLAUDE.md, or any public-facing files. The connection exists in Stan's private memory files and internal knowledge, but the two projects present as independent efforts to the public.

**Why:** Multiple reasons Stan chose not to elaborate — respect this decision and never add cross-references.

---

### Established — 2026-04-09
- Project conceived, researched, built to working v1
- Scholarly landscape mapped
- Four research advantages identified
- Siloing decision made
