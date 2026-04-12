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

## Computational Opportunity Space: The Pre-Parsed Analytical Substrate

The colometric edition creates something that has not previously existed for the Greek New Testament: a **pre-parsed analytical substrate** — every verse broken into syntactically-motivated sense-lines using consistent, documented criteria. This transforms problems that were previously trapped in close-reading methodology into computationally tractable tasks.

### The Core Insight

In a standard paragraph-formatted GNT, any analytical task requires simultaneously solving two problems: (1) where are the clause boundaries? and (2) what is the phenomenon I'm looking for? The colometric edition pre-solves problem (1). Each line is one colon. Every analytical question reduces to: "does this line exhibit property X?" That reduction is what makes agent-based detection feasible at corpus scale.

### Pauline Studies: Ellipsis, Anacoluthon, and Structural Compression

Paul's letters are the richest test case. His frequent use of ellipsis (gapping) — where a verb or predicate is syntactically required but omitted because it is recoverable from context — becomes detectable when the text is in sense-lines. A line that lacks a verbal element in a context where one is required is a candidate for ellipsis. The question reduces to: "is this line syntactically complete?"

Example: Galatians 2:7 — the καθώς clause presupposes the entire verbal idea (πεπίστευμαι τὸ εὐαγγέλιον) from the previous line. In sense-line format, the gapped line is immediately visible as incomplete; in paragraph format, it's buried in a subordinate clause.

Beyond ellipsis, the same substrate enables systematic detection of:
- **Anacoluthon** — lines where Paul starts a construction and never finishes it (the colon just stops, and the next one picks up differently)
- **Parenthesis mapping** — where Paul interrupts his own argument with a digression, visible as cola that break the syntactic flow of surrounding lines
- **Asyndeton patterns** — cola lacking connective particles, which in Paul often signal emotional intensity or rhetorical climax
- **Colon-length compression** — places where Paul's cola get dramatically shorter, often marking argumentative peaks

### Structural Glosses as a Force Multiplier

The structural English glosses (aligned by construction to Greek sense-lines) double the analytical surface. An agent can reason about both the Greek syntax and the English rendering simultaneously. For ellipsis detection specifically: a Greek line missing a verb paired with an English line that also lacks a verb is a high-confidence ellipsis candidate. A Greek line missing a verb but whose English line contains one reveals where the translator silently supplied the gapped element.

### Reframing Pauline Difficulty: Compression as Lucidity

The entire scholarly tradition has a bias toward "Paul-as-difficult." But ellipsis is only possible when the logic is so clear that the speaker can omit the verb and trust the audience to supply it. Gapping is a marker of compositional confidence, not confusion.

When the gapped elements are systematically reconstructed and found to be always recoverable from the immediate context — when Paul never actually leaves his audience without the information they need — then the "difficult Paul" reputation starts looking like a problem of prose formatting rather than a problem of Pauline thought. The colometric edition may show that Paul is one of the most disciplined composers in the NT — that his density is architectural precision, not muddled thinking.

The practical implication: systematically distinguishing genuinely difficult passages (where the syntax is truly broken or ambiguous) from merely compressed passages (where the structure is tight enough to support ellipsis) would produce a much smaller, more precisely defined set of Pauline cruces than the tradition currently recognizes. That distinction has never been drawn systematically because the prerequisite work — consistent sense-line formatting across the entire corpus — didn't exist until now.

### Beyond Paul

The same analytical substrate serves every NT author, though the phenomena differ:
- **Mark:** Paratactic chain analysis — where does Mark's καί-chain create genuine narrative segmentation vs. mere conjunction?
- **Luke-Acts:** Genre-shift detection — quantifiable line-length differences between epistolary prologues, narrative, and embedded speeches
- **John:** Repetition-with-variation patterns — John's spiral rhetoric (restating with slight modification) becomes visible as near-identical cola with targeted substitutions
- **Revelation:** Vision formula mapping — the repeated "καὶ εἶδον" structures become countable, classifiable, and comparable
- **Hebrews:** A fortiori chain detection — πόσῳ μᾶλλον escalation patterns across the argument

None of these analyses require new theory. They require the formatted dataset that this project provides.

### Colometric Structure as a Translation-Critical Concern

A further scholarly implication reaches beyond text-internal analysis and into translation theory itself: **if translators have misunderstood which units belong together, they have quite possibly mistranslated important passages.** A line break is not a neutral presentation choice — it encodes an implicit claim about where one thought ends and the next begins. When a translator reads a paragraph-formatted Greek text and renders it in English, the translator's (often unconscious) segmentation of that text becomes the load-bearing assumption underneath every choice of verb, preposition, subject binding, and clause nesting.

Concrete consequences when the segmentation is wrong:
- **Subject-verb mis-attribution:** when a participle is absorbed into the wrong frame, its implied subject can be assigned to the wrong referent (the Acts 1:9 class: merging `βλεπόντων αὐτῶν` into the main clause makes "they" look like the subject of ἐπήρθη rather than Jesus). Translators who inherit the wrong break make downstream binding errors.
- **Antithesis flattening:** μή/ἀλλά pairs compressed into one colon lose their corrective force and get smoothed into single assertions. Rom 12:3 is the case in point — "not to think too highly but to think soberly" becomes "to think soberly" because the antithesis is invisible in the source segmentation.
- **Dative-subject-of-infinitive mis-binding:** when a dative IO is floated as a vocative-style apostrophe, translators treat it as "addressees" rather than "semantic subject of the infinitive." This changes what the command is *about*.
- **Qualifier chain misgrouping:** three adjectives on one noun vs. three separate predications — getting this wrong changes whether a passage reads as one composite image or a sequence of escalating claims.
- **Attributive participle splits:** splitting ὁ τεχθεὶς from βασιλεύς (Matt 2:2) can lead translators to render "the born one" as a substantival phrase ("the one born") rather than an attributive ("the born king"). Same words, different English syntax, different theological emphasis.

The testable claim: **every class of colometric error we have identified in v4 had an empirically verifiable impact on downstream translation choices in one or more major English versions.** A comparative pass across NA28, NIV, NRSV, ESV, NASB, and YLT against corrected colometric structure would yield a map of places where segmentation disagreements correspond to translation disagreements. Where they correlate, the colometric analysis provides a *grammatical warrant* for preferring one translation over another — not on theological grounds, but on the grounds that the author's own breath units are best preserved by the translation that matches the segmentation.

This moves colometric methodology from being a *reading aid* to being a *translation-critical discipline*. It provides translators, exegetes, and commentary writers with a structured substrate for discovering where their paragraph-inherited assumptions may be flattening the source. It also offers a mechanism for adjudicating certain translation disputes — not all, but the subset where the dispute traces back to unclear clause-unit boundaries in the editor's (or translator's) mental segmentation of the Greek.

**For the PhD prospectus:** this is one of the strongest "why does this matter" arguments for the project's scholarly contribution. The edition is not merely a pedagogical tool; it is a text-critical and translation-critical resource that makes a specific kind of error newly detectable and correctable.

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

---

### Update — 2026-04-10 (session 4)

#### YLT Replaced by WEB (World English Bible)

YLT (Young's Literal Translation, 1898) was replaced by the **World English Bible** (WEB, public domain, modern English) as the English rendering layer.

**Why the switch:** The YLT's archaisms ("doth", "hath", "art thou", "fowls of the heaven") create readability barriers for the English-only demographic the project aims to serve. WEB is still very literal (formal equivalence) but uses modern English, making the colometric structure immediately comprehensible without requiring the reader to parse 19th-century idiom.

**Alignment approach changed:** YLT alignment used a sequential forward-scan matching Macula glosses to YLT text. WEB alignment uses a "double-wire" approach: Greek to Macula English (perfect by construction) to WEB (LCS alignment), with spaCy dependency parsing as a cut-point validator to prevent splitting inside English phrases.

**Known limitation:** WEB sometimes restructures sentences differently from Greek word order, causing unavoidable alignment mismatches on approximately 10% of verses. This is inherent to any modern-English translation and cannot be fully solved algorithmically.

The YLT section above is retained for historical context but YLT is no longer the active English layer.

#### Domain Purchased and Configured

- **gnt-reader.com** purchased via Cloudflare
- DNS configured: Cloudflare DNS pointing to GitHub Pages
- CNAME file added to repo root
- HTTPS enforced
- Landing page updated with verse popover matching in-app navigation
- Domain status: live and serving

#### Colometric Methodology Reset

YLT/WEB alignment work in session 4 revealed that the v3 colometric pipeline has an approximately **10-12% error rate** in the Greek breaks themselves (not just English alignment problems).

Examples discovered:
- Mark 4:1 — subject split from verb
- Matt 16:25 — inconsistent conditional treatment

Comparison showed that v1 (simple conjunction rules) got some verses RIGHT that v3 (sophisticated Macula-driven pipeline) BROKE. Root cause: v3 optimizes for grammar rules rather than the three core criteria (atomic thought, single image, breath unit). The v2/v3 layers were actively making some things worse — "polluting" v1's criteria-driven breaks.

This does not invalidate the v3 pipeline but establishes that automated sophistication is not automatically better. The v4 editorial pass is now understood as essential, not optional.

---

### Update — 2026-04-11 (post v4 editorial review)

#### English Layer: Structural Glosses Replace WEB/YLT Entirely

The English rendering is no longer an aligned translation (WEB or YLT). It is now a **purpose-built structural gloss** that tracks Greek clause order by construction. Each English line was written to match its corresponding Greek line — there is no alignment algorithm because alignment is guaranteed by design. 260 chapters complete.

This eliminates the two-claim problem documented above. The English is not a translation being force-fit to Greek breaks; it is a rendering constructed from the breaks. The single claim is: these line breaks reflect Greek discourse structure, and the English lets you see that structure without knowing Greek.

#### Universal Vocative Rule

All vocatives now get their own line — each is an atomic thought (a complete address act) and a natural breath unit (pause before and after). One exception: repeated vocatives (e.g., Κύριε κύριε) stay on one line. This supersedes the earlier three-category distinction (vocative attachment principle from session 4).

#### Cross-Pollination from BOM Reader

Ten principles were ported and adapted for Greek colometry:
1. Framing-element fragments (FEFs) — merge into adjacent cola
2. Three-category editorial framework (mechanical / rhetorical / theological)
3. Framing device isolation (temporal, spatial, circumstantial)
4. ἰδού distinction (presentative vs. interjection behavior)
5. Syntactic bond hierarchy (what must never be split)
6. Escalation/restriction pattern recognition
7. Vocative rule (adapted to Greek address conventions)
8. ὅτι distinction (content clause vs. causal clause treatment)
9. Authorial style principle (Mark's parataxis vs. Luke's periodicity)
10. Parallel diagnostic scanner (automated detection of stackable structures)

#### Methodology Maturation

The four core criteria (atomic thought, single image, breath unit, source-language syntax) are now supported by approximately 15 sub-principles, all tested against editorial practice in the Mark 4 and Acts 1 gold standard chapters. The methodology has moved from ad hoc rule accumulation to a principled framework with documented precedent for each sub-rule.
