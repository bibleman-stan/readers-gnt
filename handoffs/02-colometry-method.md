# 02 — Greek Colometric Methodology

## Foundation

This project applies sense-line (colometric) formatting to the Greek New Testament. The method is grounded in the scholarly tradition of Lee & Scott (sound mapping), Marschall (colometric analysis), and ancient manuscript practice (Codex Bezae, Codex Claromontanus).

## Core Premise

Ancient authors composed for oral delivery. The text was heard, not silently read. Modern verse-and-paragraph formatting obscures the original compositional structure. By breaking the text at its natural grammatical joints, we recover the author's own phrasing — the cola (κῶλα) and periods (περίοδοι) that structured the original composition.

## What We Ignore (Deliberately)

These are later additions that do not reflect authorial intent:

- **Versification** (Stephen Langton, 13th c. / Robert Estienne, 1551)
- **Modern punctuation** (editorial, not original)
- **Pericope divisions** (liturgical, not compositional)
- **Paragraph breaks** (editorial convention in NA28/UBS5)

We preserve verse references for alignment with standard editions, but they do not drive line-breaking decisions.

## What We Follow

- **Greek clause structure** — main clauses, subordinate clauses, participial phrases
- **Discourse markers** — καί, δέ, γάρ, οὖν, ἀλλά as structural signals
- **Rhetorical patterns** — parallelism, tricolon, chiasm, μέν/δέ contrast
- **Breath and thought units** — each line processable as a single cognitive chunk

## The Three Tests

### 1. The Foundational Test
**Each line must be an atomic thought, an atomic breath unit, or ideally both.**

This overrides all other rules. A line that passes this test is valid. A line that fails it needs revision.

- **Atomic thought:** the reader can process this line as a single unit of meaning without needing the next line to resolve it
- **Atomic breath unit:** the line can be delivered in one breath at natural reading pace

### 2. The Image Test
Each line should paint a single image or picture in the mind. If a line contains two distinct images, it's a candidate for splitting. If a line contains no complete image, it may need merging.

### 3. Grammar Reveals Structure — It Doesn't Create It
Line breaks follow grammatical structure that already exists in the text. The breaks are descriptive, not interpretive. We make visible what is already encoded.

## Greek-Specific Break Points

### 1. Main Clause Boundaries
Each new finite verb introducing a new action or state is a candidate for a new line. In Markan narrative, the paratactic καί chain becomes visible as a sequence of images:

```
καὶ γίνεται λαῖλαψ μεγάλη ἀνέμου,
καὶ τὰ κύματα ἐπέβαλλεν εἰς τὸ πλοῖον,
ὥστε ἤδη γεμίζεσθαι τὸ πλοῖον.
```

### 2. Subordinate Clause Introductions
Purpose (ἵνα), result (ὥστε), causal (ὅτι, διότι), temporal (ὅταν, ὅτε), conditional (εἰ, ἐάν), comparative (καθώς), "lest" (μήποτε) — each introduces a new line:

```
ἵνα βλέποντες βλέπωσι καὶ μὴ ἴδωσιν,
καὶ ἀκούοντες ἀκούωσι καὶ μὴ συνιῶσιν,
μήποτε ἐπιστρέψωσιν καὶ ἀφεθῇ αὐτοῖς.
```

### 3. Participial Phrases
Major participial phrases (especially genitive absolutes) function as temporal or circumstantial framing and earn their own line:

```
Σταθεὶς δὲ Παῦλος ἐν μέσῳ τοῦ Ἀρείου Πάγου ἔφη·
```

When participial chains describe the same action, they may stay together:

```
διερχόμενος γὰρ καὶ ἀναθεωρῶν τὰ σεβάσματα ὑμῶν
```

### 4. Direct Speech
Speech introductions (ἔλεγεν, εἶπεν, ἔφη + dative) get their own line. The speech content begins on the next line:

```
καὶ ἔλεγεν αὐτοῖς·
Ὑμῖν τὸ μυστήριον δέδοται τῆς βασιλείας τοῦ θεοῦ·
```

### 5. Parallel Stacking
When the author builds parallel structures, stack them vertically to make the rhetoric visible:

```
καὶ αἱ μέριμναι τοῦ αἰῶνος
καὶ ἡ ἀπάτη τοῦ πλούτου
καὶ αἱ περὶ τὰ λοιπὰ ἐπιθυμίαι
εἰσπορευόμεναι συμπνίγουσιν τὸν λόγον,
```

This is especially powerful for triadic yield patterns:

```
καὶ ἔφερεν ἓν τριάκοντα
καὶ ἓν ἑξήκοντα
καὶ ἓν ἑκατόν.
```

### 6. μέν/δέ Contrast
Greek's built-in contrast structure becomes spatially visible:

```
οἱ μὲν ἐχλεύαζον
οἱ δὲ εἶπαν·
```

Also:
```
Ὑμῖν τὸ μυστήριον δέδοται τῆς βασιλείας τοῦ θεοῦ·
ἐκείνοις δὲ τοῖς ἔξω ἐν παραβολαῖς τὰ πάντα γίνεται,
```

### 7. Explanatory γάρ
Often introduces a new line, since it signals a shift to explanation:

```
ἐν αὐτῷ γὰρ ζῶμεν
καὶ κινούμεθα
καὶ ἐσμέν,
```

### 8. Discourse Markers (ἀλλά, πλήν, οὐδέ, μηδέ)
These introduce contrasts or corrections and earn a new line:

```
ἀλλὰ περιμένειν τὴν ἐπαγγελίαν τοῦ πατρός
```

## Carry-Over Rules

These rules apply universally, adapted from established editorial practice:

1. **Never dangle a conjunction** at line end — καί, δέ, ἀλλά lead their line
2. **Never split verb from direct object** on short phrases
3. **Framing devices attach** — discourse markers lead their content, don't orphan them
4. **Parallel structures stack vertically** to show rhetorical pattern
5. **Line length is a signal, not a rule** — short lines create emphasis and slow the reader; long lines create flow and momentum
6. **Never end a line on an article** (τόν, τήν, τό, etc.)
7. **Vocative units are indivisible** — Ἄνδρες Ἀθηναῖοι stays whole
8. **Fixed phrases stay together** — ἐν αὐτῷ, εἰς τὸν αἰῶνα, etc.

## Hand-Crafted vs. Auto-Formatted

Two levels of quality exist in the v1-colometric files:

**Hand-crafted test chapters** (Mark 4, Acts 17) were originally formatted manually with full editorial judgment. These demonstrated the vision: tricolon stacking, careful speech-intro breaks, parallel μέν/δέ, dramatic short lines. However, they were **overwritten** by the auto-formatter during the full-corpus run on 2026-04-09. The hand-crafted versions are preserved in the git history (commit `4721433`) and in `C:\tmp\gnt-colometry-test\`.

**Auto-formatted chapters** (all 260) were produced by `scripts/auto_colometry.py`. The auto-formatter applies rule-based breaking (subordinate clauses, speech introductions, discourse markers, comma+καί patterns) but is significantly less granular than hand editing. Known limitations:
- Does not stack tricolon/parallel lists (the "τριάκοντα/ἑξήκοντα/ἑκατόν" pattern stays on one line)
- Misses some speech introductions (only catches common patterns)
- Does not break at genitive absolutes (would require morphological tagging)
- Over-splits some lines at comma+καί where the join is tighter than a clause boundary
- Under-splits long lines that lack comma triggers

**The auto-formatter is a starting point, not the final word.** Stan hand-edits the v1 output. Same workflow as the BOM Reader's v1→v2 process.

## Moments Where Colometry Does Real Work

These examples from the hand-crafted test chapters show what the project reveals:

- **Mark 4:8, 20** — triadic yield stacks vertically, making climactic parallelism visible
- **Mark 4:12** — Isaiah quotation already is cola; three lines of paradox stack perfectly
- **Mark 4:19** — triple choking list stacks, then verb lands as payoff
- **Mark 4:39** — Σιώπα, πεφίμωσο as a standalone dramatic line
- **Acts 17:28** — Paul's Epimenides tricolon becomes three punching lines; Aratus quotation gets its own line
- **Acts 17:32** — μέν/δέ split audience becomes spatially visible

## Decisions Still Open

- **How short is too short?** Single-word lines (e.g., ἐκαυματίσθη) — dramatic emphasis or fragmentation?
- **Genitive absolute attachment:** always its own line, or sometimes attached to main clause?
- **ὅτι recitativum:** stays with speech intro, or breaks?
- **Cross-verse continuity:** when a sentence spans verses, should we visually indicate the continuation?
- **Indentation:** should subordinate clauses be indented? Currently flat.
- **"And it came to pass" (ἐγένετο) patterns:** does the Wayyehi rule from BOM Reader apply to Lukan ἐγένετο + infinitive constructions?
- **Καί as conjunction vs. clause-introducer:** the auto-formatter uses comma+καί as a heuristic, but this misses many clause boundaries and falsely triggers on some noun joins

---

## Four-Tier Pipeline

The colometric formatting pipeline has four tiers, each building on the previous:

### Tier 1 — Pattern-Matching (v1-colometric)

Script: `auto_colometry.py`. Rule-based surface-text pattern matching. Breaks at known subordinating conjunctions (ἵνα, ὥστε, ὅτι, ὅταν, ὅτε, ἐάν, μήποτε, etc.), discourse markers (ἀλλά, πλήν, ἄρα), postpositive conjunctions (γάρ, οὖν), μέν/δέ correlative pairs, speech introductions, vocative phrases, and comma+καί heuristic. Conjunction inventory informed by Wallace, *Greek Grammar Beyond the Basics* (1996), chapters 24–25. Known limitation: cannot detect participial phrases, genitive absolutes, or clause boundaries not marked by a surface-level conjunction.

### Tier 2 — Syntax-Tree-Driven (v2-colometric)

Script: `v2_colometry.py` using `macula_clauses.py`. Uses clause boundaries extracted from the **Macula Greek** Lowfat XML syntax trees (Clear Bible, CC-BY 4.0), which provide hierarchical phrase-structure annotation of the SBLGNT text. Clause boundaries are determined by scholars, not heuristics. The Macula trees are derived from the Global Bible Initiative syntax markup, auto-generated then hand-corrected.

**What this tier adds:**
- Participial phrases isolated as their own lines (detected by `mood="participle"` in the tree)
- Genitive absolutes identified (genitive participle + genitive noun/pronoun within the same clause node)
- Clause boundaries in long prose passages that have no surface conjunction trigger
- Infinitival clauses, relative clauses, and complement clauses properly segmented

**Data sources:**
- **Macula Greek** (github.com/Clear-Bible/macula-greek) — SBLGNT syntax trees, CC-BY 4.0
- **MorphGNT** (github.com/morphgnt/sblgnt) — SBLGNT morphological tagging, CC-BY-SA

The SBLGNT source text remains canonical for all output — the Macula data determines WHERE to break, but WHAT text appears comes from the SBLGNT.

### Tier 3 — Rhetorical Pattern Layer (future)

Applied on top of v2 clause boundaries. Detects and formats rhetorical structures:
- Tricolon/bicolon stacking (parallel lists displayed vertically)
- μέν/δέ contrast display
- Climactic parallelism
- Chiastic structure display
- Geographic/catalog list stacking

This tier answers *how should the clauses display* rather than *where do clauses break*.

### Tier 4 — Editorial Hand (future)

Stan's hand editing. Makes final decisions on:
- Cases where automated breaking is suboptimal
- Dramatic emphasis (standalone short lines for rhetorical effect)
- Theological sensitivity (break placement that affects doctrinal reading)
- Resolving open questions (genitive absolute attachment, ὅτι recitativum, etc.)

---

### Established — 2026-04-09
- Initial methodology document created
- Two test chapters hand-formatted (Mark 4, Acts 17)
- Greek-specific break-point rules drafted
- Auto-formatter built and run on all 27 books (260 chapters)
- Known limitations of auto-formatter documented
- Hand-crafted test chapters overwritten by auto-formatter (preserved in git history and /tmp)

---

### Update — 2026-04-09 (session 2)
- Four-tier pipeline designed and documented
- Tier 1 expanded with Wallace-informed conjunction inventory (γάρ, οὖν, δέ, εἰ, ἐπεί, ὅπως, ἄχρι, etc.)
- Tier 2 built using Macula Greek syntax trees for clause-boundary extraction
- MorphGNT and Macula Greek datasets integrated (stored in research/ directory, gitignored)
- v2-colometric output generated for all 260 chapters
- Web app now serving v2 output
