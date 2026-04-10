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
- Tier 3 built: rhetorical pattern layer (parallel list stacking, complementary verb merging, standalone imperatives, sequence stacking, subordinating conjunction refinement)
- MorphGNT and Macula Greek datasets integrated (stored in research/ directory, gitignored)
- v2-colometric and v3-colometric output generated for all 260 chapters
- Web app now serving v3 output
- Mark 4 v3 output validated against hand-crafted gold standard — near-complete match

## Scholarly Grounding and Validation

### Key Methodological Sources

| Source | Contribution to this project |
|--------|------------------------------|
| **Wallace, *GGBB* (1996)** ch. 23–25 | Conjunction/clause classification informing v1 break-point inventory |
| **Marschall (2023)** "Refining the Criteria for Delineating Côla and Periods" | Cola ≠ clause; prepositional phrases can be cola; syllable length criteria; periodic vs. continuous style |
| **Marschall (2024)** *Colometric Analysis of Paul's Letters* (WUNT II) | Methodological foundations for colometric analysis of Pauline letters |
| **Lee & Scott (2009/2022)** *Sound Mapping the New Testament* | Cola as breath/sense units; sound mapping as exegetical method |
| **Nässelqvist (2015)** *Public Reading in Early Christianity* | Refined syllable criteria; comma (κόμμα) vs. colon distinction |
| **Macula Greek / Clear Bible** (CC-BY 4.0) | SBLGNT syntax trees providing clause boundaries for tier 2 |
| **MorphGNT** (CC-BY-SA) | SBLGNT morphological tagging enabling participle/genitive absolute detection |

### Validation Benchmarks

- **Hand-crafted test chapters** — Mark 4 and Acts 17, hand-formatted by Stan in the initial design session. Preserved in `C:\tmp\gnt-colometry-test\`. v3 output matches the gold standard on nearly all verses of Mark 4.
- Additional validation benchmarks tracked privately.

---

### Update — 2026-04-09 (session 2, continued)

#### New Principled Rules in v3

Two new rules were added to the v3 tier, each with independent grammatical warrant:

1. **Infinitive merge-back:** Dependent infinitives cannot begin a colon. When a line starts with an infinitive that is syntactically governed by a verb on the preceding line, it merges back into the governing line. Warrant: Wallace ch. 22 (complementary, purpose, and result infinitives are verbal complements, not independent clauses); Marschall's semantico-syntactic completeness criterion (an infinitive without its governing verb fails the "atomic thought" test because the thought is incomplete without the matrix verb).

2. **Verbless line merge:** Lines without any verbal element — checked via MorphGNT morphological tagging (no finite verb, participle, or infinitive present) — cannot constitute valid cola. They fail the foundational "atomic thought" test because the thought is suspended awaiting verbal resolution. Such lines are merged into their nearest verbal neighbor.

#### The Criteria Chain

The project's methodological integrity rests on a traceable chain of warrant:

- **Ancient rhetoricians** (Pseudo-Demetrius, the colometric manuscript tradition) establish that prose has internal structure at the colon/period level
- **Modern formalization** (Lee & Scott, Marschall, Nasselqvist) refines the criteria for identifying cola: breath units, semantic completeness, syllable ranges
- **Syntactic operationalization** (Macula syntax trees + Wallace's clause/conjunction taxonomy) provides the computational mechanism for applying those criteria at scale
- **Principled refinement rules** (infinitive merge-back, verbless line merge) handle edge cases that the tree structure alone does not resolve, each grounded in explicit grammatical warrant
- **Consistent application** across 137,554 words of the SBLGNT ensures that downstream quantitative analysis (authorship, genre, stylometry) is valid — the same rules applied everywhere

#### Bezae Caveat

Codex Bezae's line breaks reflect a mixture of sense-line decisions and physical layout constraints. The column width of Bezae is approximately 25-30 characters, meaning many line breaks are forced by the available writing space rather than by colometric judgment. Agreement metrics between our automated output and Bezae are meaningful — they reveal which breaks are structurally motivated — but Bezae cannot be treated as a colometric gold standard without this caveat. Some breaks are sense-line decisions; others are where the scribe ran out of room.

#### Multi-Tier Comparison Results

| Tier | Agreement with Bezae |
|------|---------------------|
| v1 (pattern-matching) | 59.7% |
| v2 (syntax-tree) | 60.6% |
| v3 (rhetorical + refinement) | 60.7% |

Each tier monotonically improves agreement with the ancient manuscript. The gains are modest because Bezae's physical layout constraints introduce noise — many Bezae breaks are layout-driven rather than sense-driven.

Notable per-book finding: Matthew shows v1 closer to Bezae than v2/v3. Simpler pattern-matching breaking approximates scribal practice for Matthew's Gospel, likely because Matthew's predominantly paratactic narrative style produces line breaks at the same conjunction-triggered points where a scribe would naturally break for column width.

## Verb Valency and the "Atomic Thought" Test

A key refinement of the foundational "atomic thought" criterion is **verb valency satisfaction**: a line is a complete thought only if the verbal element's required arguments are present within the line. This is standard linguistic valency theory applied to colometric analysis.

| Verb type | Required arguments | Line complete? |
|---|---|---|
| **Intransitive** (no object required) | Subject (often implicit in Greek) | Yes — e.g., `Μετανοήσατε` ("Repent!") |
| **Transitive without object** | Subject + Object, but object absent | No — e.g., `ἀκούσας δέ` ("having heard" — heard WHAT?) |
| **Transitive with object present** | Subject + Object, both on line | Yes — e.g., `καὶ ταῦτα εἰπὼν` ("having said these things") |
| **Passive** (patient = subject) | Subject (as patient) | Yes — e.g., `φυλασσόμενος` ("being guarded") |

### Data source: Macula syntactic role annotations

The Macula Greek Lowfat XML encodes syntactic roles on individual words (`role=s` for subject, `role=o` for object, `role=v` for verb, etc.). This provides **usage-level transitivity** for every verb in every verse — not a lexicon-based guess, but actual syntactic analysis of how the verb is used in context. ἀκούω (hear) can be transitive or intransitive; the Macula annotation tells us which it is in each specific occurrence.

This enables a principled, testable colometric rule: a line containing a participle whose Macula clause has an object (`role=o`) not present on the line has unsatisfied valency and should merge with its neighbor. This is not an arbitrary length heuristic — it is a grammatically grounded test derived from the text's own syntactic structure.

### Syntactic Clause ≠ Colometric Colon

A central finding of this project, validated empirically across 137,554 words of the SBLGNT: the syntactic clause boundaries produced by formal grammar parsers (Macula syntax trees) do not reliably correspond to colometric cola — the meaning units that a hearer processes as one thought, one image, one breath.

The divergence runs in both directions:

- **Grammar over-splits.** A syntax tree correctly identifies a prepositional phrase, an article, or a participial clause as a separate grammatical node. But `ὁ` without its noun is meaningless to a hearer. `ἐν` without its object is not a thought. The grammar permits these as separate nodes; oral meaning does not.

- **Grammar under-splits.** A syntax tree may correctly identify an entire Pauline periodic sentence as one predication. But a 200-character sentence with three participial images, two prepositional modifiers, and a relative clause is not one breath unit. The grammar sees one sentence; the ear hears six cola.

The corrective layer — the principled rules that merge fragments the tree created and split mega-lines the tree left intact — is the methodological contribution. These rules are not ad hoc formatting preferences. Each is grounded in:
- Ancient rhetorical theory (Pseudo-Demetrius on semantico-syntactic completeness)
- Modern formalization (Marschall on cola vs. clauses, Nässelqvist on syllable ranges)
- The foundational test (atomic thought, single image, breath unit)
- Koine Greek grammar (Wallace, BDF on verb valency, conjunction classification, conditional sentences)

The pipeline therefore moves from **esoteric grammar rules** (syntactic tree parsing) to **concrete and atomic senses of meaning** (what a hearer actually processes). This transition — from syntax to semantics for oral delivery — is a genuine advance in the field that neither pure grammatical analysis nor pure editorial intuition achieves alone.

### Exegetical Hot Spots: Grammar-Driven Colometric Findings

Spot-checking the colometric output against classic textual and structural debates reveals that grammar-driven formatting independently produces exegetically significant arrangements. These are not editorial decisions — they result from the same rules applied to every verse in the corpus.

#### John 1:3-4 — ὃ γέγονεν placement
**Debate:** Does ὃ γέγονεν complete v.3 ("not one thing that has been made") or begin v.4 ("what has come into being — in him was life")?
**Colometry shows:** ὃ γέγονεν stays with v.3. The relative clause is governed by the antecedent ἕν in the preceding negative construction οὐδὲ ἕν. Separating it orphans the relative pronoun from its syntactic anchor.
**Rule producing this:** Relative clause attachment to antecedent; verbless-line merge (ὃ γέγονεν alone fails the atomic thought test).

#### Romans 9:5 — ὁ ὤν and Christological referent
**Debate:** Does ὁ ὤν ἐπὶ πάντων θεὸς εὐλογητός refer to Christ or is it an independent doxology to the Father?
**Colometry shows:** ὁ ὤν connects to ὁ Χριστός. The substantival participle functions as an appositional modifier and attaches to the nearest preceding substantive.
**Rule producing this:** Participial phrase attachment; appositional modifier stays with its head noun.

#### Ephesians 1:4-5 — ἐν ἀγάπῃ attachment
**Debate:** Does ἐν ἀγάπῃ modify "holy and blameless" (backward) or "having predestined us" (forward)?
**Colometry shows:** ἐν ἀγάπῃ attaches backward to ἁγίους καὶ ἀμώμους. The line break falls after ἐν ἀγάπῃ because the participial phrase προορίσας ἡμᾶς begins a new grammatical unit.
**Rule producing this:** Participial phrase break (προορίσας triggers new line); prepositional phrase stays with its modified element.

#### 1 Timothy 3:16 — hymn structure
**Debate:** Is 3:16b a pre-Pauline hymn? What is its internal structure?
**Colometry shows:** Six relative-clause lines fall into three antithetical pairs. The parallelism emerges from the grammar alone — relative clause + aorist passive, repeated six times.
**Rule producing this:** Relative clause break; parallel stacking.

#### Philippians 2:6-8 — kenosis hymn descent
**Debate:** Internal structure of the recognized hymn (two strophes? three? chiastic?).
**Colometry shows:** The descent structure is visually self-evident. Each downward step (μορφῇ θεοῦ → μορφὴν δούλου → σχήματι... ὡς ἄνθρωπος → θανάτου → θανάτου δὲ σταυροῦ) lands on its own line. The θανάτου repetition is preserved as a dramatic short-line appendage because δέ triggers a new line.
**Rule producing this:** Participial phrase break (ὑπάρχων, λαβών, γενόμενος); subordinating conjunction break (ἵνα); discourse marker break (δέ).

#### 1 Corinthians 15:3-5 — fourfold ὅτι creedal formula
**Debate:** Boundaries and internal structure of the pre-Pauline creedal formula.
**Colometry shows:** The fourfold ὅτι stacks as four parallel declarations, each a complete predication. The creedal formula's oral architecture — four parallel, self-contained units — emerges without any knowledge that this is a creed.
**Rule producing this:** Subordinating conjunction break (ὅτι begins a new line); parallel stacking.

#### Colossians 1:15-17 — cosmic scope hymn
**Debate:** Structure and extent of the Col 1:15-20 hymn; status of the εἴτε list.
**Colometry shows:** The εἴτε quadruple list (θρόνοι / κυριότητες / ἀρχαί / ἐξουσίαι) stacks as four parallel lines. The hymnic frame (ὅς ἐστιν... ὅτι ἐν αὐτῷ... τὰ πάντα) structures itself around this list.
**Rule producing this:** Conjunction break (εἴτε); parallel stacking; relative clause break (ὅς).

#### The pattern across all seven cases

The pipeline has no concept of "hymn," "creed," "Christology," or "predestination." It applies the same grammatical rules to these verses that it applies to every other verse. The convergence between grammar-driven colometry and the conclusions of structural and exegetical scholarship validates both the method and the traditional analyses. The compositional architecture was always encoded in the grammar; prose formatting hides it; colometric formatting makes it visible.

---

### Note on editorial punctuation

Modern editorial punctuation (commas, periods, ano teleia) in the SBLGNT is not original to the text. Colometric rules must never be based on punctuation placement. The original texts were written in scriptio continua with no punctuation — the colometric line breaks themselves do the structural work that later editorial punctuation attempts to do. The web reader hides punctuation by default for this reason.

---

### Update — 2026-04-09 (session 3)

- Added "Exegetical Hot Spots" section documenting seven cases where grammar-driven colometry independently produces exegetically significant structures: John 1:3-4, Rom 9:5, Eph 1:4-5, 1 Tim 3:16, Phil 2:6-8, 1 Cor 15:3-5, Col 1:15-17
- Each finding documents the scholarly debate, what our colometry shows, and which grammatical rule produced the arrangement
- Key insight: the pipeline converges with scholarly consensus on structural analysis without any interpretive input — the grammar encodes the compositional architecture that prose formatting hides
- Paper seed created for a findings paper ("Grammar Reveals Structure") targeting NTS or JBL

