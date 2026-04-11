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

## The Four Criteria

### 1. Atomic Thought
Each line must contain one complete thought — a predication that can stand on its own as a unit of meaning. A line that requires the next line to resolve its subject, verb, or complement is incomplete.

### 2. Single Image
Each line should paint a single image or picture in the mind. If a line contains two distinct images, it's a candidate for splitting. If a line contains no complete image, it may need merging.

### 3. Breath Unit
Each line can be delivered in one breath at natural reading pace. This is the oral-delivery criterion: ancient authors composed for the ear. Very short fragments (1-2 words) are rarely valid unless they are complete predications (imperatives, vocatives-as-commands). Very long lines likely contain multiple thoughts.

### 4. Source-Language Syntax
Line breaks are informed by the clause and syntax structure of the source language. For Greek: conditional constructions (εἰ/ἐάν protasis/apodosis), correlative pairs (μέν/δέ, μᾶλλον...ἤ, οὔτε...οὔτε), subordinating conjunctions (ἵνα, ὥστε, ὅταν, ὅτε), participial phrases, genitive absolutes, and discourse markers (γάρ, ἀλλά, οὖν) all signal natural break points. For the BOM Reader, the equivalent is English clause structure. For Hebrew (if extended to the OT), the same principle applies to Hebrew syntax.

**This criterion serves the first three — it does not override them.** Grammar helps us *find* where atomic thoughts, images, and breath units naturally break. If a grammatical rule produces a line that isn't an atomic thought, the rule is wrong, not the criteria. Grammar reveals structure that already exists in the text; it doesn't create structure.

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

## Principles Established by v4 Editorial Pass (Mark 4)

These principles were identified during the first hand-editing pass on Mark 4 (session 4, 2026-04-10). They refine the three core tests with specific grammatical guidance.

### Ellipsis Principle
An elided (gapped) verb is a real predication for colometric purposes. When a verb appears once and is implied for subsequent members of a parallel structure, each member is a complete atomic thought with a recoverable verb. This applies to:
- **Triadic object lists:** "bore thirty / [bore] sixty / [bore] a hundred" (Mark 4:8, 4:20)
- **Triadic subject lists:** "worries [choke] / deceit [chokes] / desires choke" (Mark 4:19)
- **Growth stage lists:** "first blade / [then] ear / [then] full grain" (Mark 4:28)
- **Any parallel structure** where the verb is expressed once and implied for subsequent members

The scholarly warrant: this is standard Greek gapping (ellipsis). Each elided clause is semantically complete because the verb is recoverable from context.

### Subordinate Clause Attachment
- **Adjectival subordinate clauses** (ὅπου, ὅς modifying a noun) merge with their head noun — they describe the thing just mentioned and are not independent thoughts. "Fell on rocky ground where it had not much earth" = one image (Mark 4:5).
- **Adverbial subordinate clauses** (ὅτε, ἵνα, ὥστε, ὅταν) can stand as scene-setters on their own line — they frame a new temporal, purpose, or result context (Mark 4:6 "καὶ ὅτε ἀνέτειλεν ὁ ἥλιος").

### Vocative Rule
All vocatives get their own line. A vocative is both an atomic thought (a complete address act — "I am speaking to you") and a breath unit (oral delivery naturally pauses after an address before the speech content follows). This applies universally regardless of word count, formality, or syntactic position: Κύριε, Διδάσκαλε, κράτιστε Θεόφιλε, Ἄνδρες Γαλιλαῖοι — all standalone.

**One exception: repeated vocatives as a rhetorical unit.** "Κύριε κύριε" (Lord, Lord — Matt 7:21-22) stays together because the doubling is itself the rhetorical device — one speech act, not two. This exception actually confirms the rule: the repetition proves that a single vocative is a complete unit, because doubling it creates emphasis rather than redundancy.

Note: imperatives (Ἀκούετε, Σιώπα) also stand alone — they are complete predications (Mark 4:3, 4:39). Vocatives and imperatives are different grammatically but behave the same colometrically: each is a complete speech act that earns its own line.

**Supersedes** the earlier "Vocative Attachment" and "Epistolary vs. Narrative Vocative Distinction" sections. Those distinctions were explored during the Mark 4 and Acts 1 editorial passes and resolved into this simpler universal rule during the Luke 1:3 discussion.

### Participial Phrase Test (Refined Camera Angle + Ellipsis)

**Default rule:** Circumstantial participles merge with their main verb. The default function of a Greek circumstantial participle is adverbial framing — temporal (when/after), causal (because), concessive (although), conditional (if), manner (by/while). All of these are DEPENDENT: they frame the main verb's action and are not complete thoughts without it.

**Exception — supplementary predication via ellipsis:** A participial phrase earns its own line when it constitutes a **second predication** — that is, when the main verb can be implicitly repeated to reconstruct the participle as an independent thought. This is the ellipsis principle applied to participial supplements.

**The test:** Can you reconstruct the participle as an independent predication by supplying the main verb? If "the angel appeared" is complete thought 1, then "[the angel appeared] standing at the right of the altar" is complete thought 2 via ellipsis. Split. But if "having seen the star" requires "they rejoiced" to become a thought at all — if there's no implicit repeated verb — it's a dependent frame. Merge.

**Split examples (supplementary predication — main verb implicitly repeatable):**
- Luke 1:11: "ὤφθη δὲ αὐτῷ ἄγγελος κυρίου / ἑστὼς ἐκ δεξιῶν τοῦ θυσιαστηρίου" — "an angel appeared" (thought 1) / "[appeared] standing at the right of the altar" (thought 2 via ellipsis). **Split.**
- Mark 4:38: "καὶ αὐτὸς ἦν ἐν τῇ πρύμνῃ / ἐπὶ τὸ προσκεφάλαιον καθεύδων" — "he was in the stern" (thought 1) / "[was] sleeping on the cushion" (thought 2 via ellipsis). **Split.**

**Merge examples (dependent frame — no implicit repetition):**
- Matt 2:10: "ἰδόντες δὲ τὸν ἀστέρα ἐχάρησαν χαρὰν μεγάλην σφόδρα" — "having seen the star" is causal framing for "they rejoiced." You cannot say "[they rejoiced] having seen" as an independent thought. **Merge.**
- Luke 1:19: "Ἐγώ εἰμι Γαβριὴλ ὁ παρεστηκὼς ἐνώπιον τοῦ θεοῦ" — attributive participle as title/identity. **Merge.**

**Periphrastic constructions** (ἦν + participle, μέλλω + infinitive, ἄρχομαι + infinitive) are always one verbal unit — never split.

### Paradox Pairs
Antithetical pairs that form a single paradox merge onto one line: "seeing they may see and not perceive" is one thought — the paradox is the unit, not its halves (Mark 4:12, Isaiah quotation). The same applies to any construction where the second element completes (not extends) the first.

### καί + Finite Verb
Each καί + new finite verb is a candidate for a new line — a new finite verb introduces a new predication, which is by definition a new thought. This is the primary break signal in Markan paratactic narrative.

### Standalone Verb Test
Intransitive verbs of motion or state change can stand alone as a complete predication: ἐπήρθη (he was taken up), ἐκαυματίσθη (it was scorched), ἀναβαίνει (it grows up). The subject is implied, no object is required — the predication is complete.

Transitive verbs and speech verbs CANNOT stand alone — they need their complement to be a complete thought. εἶπεν (he said) without its speech is a fragment. ἐδίδασκεν (he was teaching) without its object or manner phrase is incomplete. These must stay with their complement on the same line or function as a speech introduction line followed by the speech content.

---

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
| **Priscille Marschall (2023)** "Refining the Criteria for Delineating Côla and Periods" | Cola ≠ clause; prepositional phrases can be cola; syllable length criteria; periodic vs. continuous style |
| **Priscille Marschall (2024)** *Colometric Analysis of Paul's Letters* (WUNT II) | Methodological foundations for colometric analysis of Pauline letters |
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

---

### Update — 2026-04-09 (YLT integration)

#### English Validation via YLT Alignment

The YLT English layer provides a pragmatic validation benchmark for colometric breaks, alongside the existing Marschall and Bezae benchmarks:

- **If a Greek colometric break produces an incoherent English line** (a fragment that is not a complete thought in YLT), that is a signal the break may be wrong — or that YLT departs from Greek clause order at that point.
- **If a Greek colometric break produces a clean, readable English thought**, that confirms the break reflects a genuine sense-unit boundary.

This is **pragmatic validation, not a principled criterion**. The English rendering cannot drive colometric decisions — the breaks are determined by Greek grammar (tiers 1-3) and editorial judgment (tier 4). But the YLT alignment serves as a useful cross-check: a break that works in both Greek and English is more likely to be structurally motivated than one that only works in Greek. A break that fails in English warrants a second look, even if it may ultimately be correct (since YLT does rearrange some clauses).

This adds a third validation dimension to the existing framework:

| Benchmark | What it tests | Limitation |
|-----------|---------------|------------|
| **Marschall** | Scholarly colometric analysis of Paul | Limited to 2 Cor 10-13 |
| **Bezae** | Ancient scribal sense-line practice | Physical layout constraints introduce noise |
| **YLT alignment** | Whether breaks produce coherent English thoughts | YLT sometimes departs from Greek clause order |

---

### Update — 2026-04-09 (session 3, pipeline refinements)

#### Unified Predication Test

Replaced the patchwork of participle-handling heuristics with a single principled test using Macula tree walk. For any participle on a line, the test walks up the Macula syntax tree to determine whether the participle governs its own predication (adverbial/circumstantial — earns its own line) or is governed by a matrix verb (complementary/periphrastic — merges into the governing line). This replaces separate rules for complement participles, periphrastic constructions, and participial phrases with one unified decision procedure.

#### Verb Valency Majority Threshold

Refined the verb valency satisfaction rule: a verb's valency is considered satisfied if 50% or more of its Macula-annotated object references (`role=o` and now `role=vc`) appear on the same line. This prevents false positives where a single distant object reference causes a merge. The 50% threshold was validated on Acts 9:2 (εὕρῃ keeps its complement) and other adversarial test cases.

#### Sentence Boundary Detection as Hard Constraint

Macula `<sentence>` elements now provide hard-constraint sentence boundaries. No colometric colon may span a sentence boundary — this is enforced as a post-processing pass that splits any line crossing a sentence break. Produced 1,298 splits corpus-wide. This rule has no exceptions: sentence boundaries are structural facts of the text, not editorial preferences.

#### Sub-Clause Splitting Using Macula Word Groups

For lines exceeding 80 characters that contain multiple Macula `<wg>` (word group) boundaries, the pipeline now splits at the highest-level word-group boundary. This addresses the "grammar under-splits" problem where long Pauline periodic sentences remain as single lines after clause-boundary extraction. Produced ~1,100 splits and reduced lines >120 characters to zero across the entire corpus.

#### Post-Split Safety Guards

Every splitting operation is followed by safety guards that prevent splitting inside tight grammatical units:
- **Genitive articles:** Never split between an article and its following genitive noun
- **Negations:** Never split between οὐ/μή and the word they negate
- **Possessives:** Never split between a noun and its possessive pronoun
- **Postpositives:** Never strand a postpositive particle (γάρ, δέ, οὖν, μέν, τε) at the start of a new line without its host word

#### YLT Alignment as Pragmatic Validation

The YLT English layer (99.8% gloss-matched to the Greek) provides a third validation dimension. Incoherent English lines signal potentially bad Greek breaks. This is pragmatic validation, not a principled criterion — Greek grammar drives the breaks, English coherence cross-checks them.

**Known limitation:** Ambiguous common words (it, the, and) in the YLT are sometimes misassigned when they appear multiple times in a verse. This needs POS-based disambiguation using Macula role annotations — a future refinement.

#### Corpus Health After Session 3

| Metric | Before session 3 | After session 3 |
|--------|-------------------|------------------|
| Lines >120 chars | present | **0** |
| Lines >80 chars | many | **~16** |
| Dangling function words | many | **~14** |
| Bezae agreement | 60.7% | **61.3%** |

---

### Update — 2026-04-11 (cross-pollination from BOM Reader project)

The following principles were developed and tested in the BOM Reader colometry work (documented in `readers-bofm/handoffs/10-colometry.md`) and are here adapted for Greek New Testament colometry. Each has been translated from its English/BOM context into Greek-specific terms with GNT examples.

#### 1. Front-End Frames (FEFs)

**Principle:** A Front-End Frame is a line that (1) opens a verse or verse-block, (2) begins with a discourse marker, (3) binds syntactically to dependent elements such that no internal break exists without orphaning either frame or content, and (4) is followed by expansion lines that unpack the frame's content. The frame *suspends resolution* until the main verb arrives; everything between the discourse marker and the main verb is part of the suspension.

**Greek adaptation:** The Greek equivalent of the BOM's wayyehi protasis is the **periodic sentence with participial suspension before the main verb resolves**. Lukan prose is the densest carrier: extended genitive absolutes, participial chains, and temporal clauses stack between an opening marker and the finite verb that resolves them. Pauline embedded subordination (relative clauses within purpose clauses within participial frames) produces the same irreducibility at clause level.

**Examples:**
- **Luke 3:1-2** — Ἐν ἔτει δὲ πεντεκαιδεκάτῳ τῆς ἡγεμονίας Τιβερίου Καίσαρος... ἐγένετο ῥῆμα θεοῦ — a temporal FEF that suspends through five genitive absolute participial phrases before the main verb ἐγένετο lands. The entire frame is irreducible.
- **Acts 1:1-4** — Τὸν μὲν πρῶτον λόγον ἐποιησάμην... ἄχρι ἧς ἡμέρας... ἐντειλάμενος... παρήγγειλεν — periodic sentence with participial chain suspending resolution across multiple clauses. No internal break produces a complete thought.
- **Ephesians 1:3-6** — Εὐλογητὸς ὁ θεὸς... ὁ εὐλογήσας ἡμᾶς... καθὼς ἐξελέξατο ἡμᾶς... εἰς τὸ εἶναι ἡμᾶς... προορίσας ἡμᾶς — Pauline periodic suspension with embedded purpose and result clauses; the FEF frame does not resolve until the main predication completes.

**Connection to open question:** The "ἐγένετο patterns" item in "Decisions Still Open" is now subsumed by the FEF framework. Lukan ἐγένετο + infinitive/ὅτι constructions are FEFs — the ἐγένετο is a discourse marker (not a semantically heavy verb), and the temporal/circumstantial material between it and the content clause is the frame. Treat as irreducible.

#### 2. Three-Category Framework (A/B/C)

**Principle:** When reviewing sense-lines, proposed changes fall into three categories:
- **Category A — Editorial slippage:** Break placement is suboptimal by our own principles. No theological or rhetorical stakes. Safe to revise with review.
- **Category B — Rhetorical shape:** The arrangement reflects how a speaker builds argument or emphasis. Changing the break changes the rhetoric. Requires judgment about what the speaker is doing.
- **Category C — Theological weight:** Break placement makes a doctrinal point, or a proposed change would flatten something intentional. Flag and discuss before touching.

**Greek adaptation:** Already referenced in `04-editorial-workflow.md` but not formalized in the methodology. Greek-specific instances:

- **Category A example:** A dangling article (τόν at line end) or a verb split from its direct object — mechanical error, fix confidently.
- **Category B example:** Phil 2:6-8 kenosis hymn — whether θανάτου δὲ σταυροῦ gets its own line or stays with the preceding line changes how the descent structure reads. The δέ break is rhetorically motivated.
- **Category C example:** Rom 9:5 — whether ὁ ὤν ἐπὶ πάντων θεὸς εὐλογητός attaches to ὁ Χριστός (Christological reading) or begins a new doxology (theistic reading). Break placement is a doctrinal decision.

Category A gets a confident proposal. B and C get a question first.

#### 3. Framing Devices — Unifying Principle

**Principle:** If a construction's function is to frame, introduce, or pivot to what comes next, it should not be severed from what comes next. A frame without its content is an orphan; content without its frame loses its rhetorical context.

**Greek adaptation:** Several Greek discourse markers already appear individually in our break-point rules (γάρ, ἀλλά, δέ as contrast). The unifying principle behind them all is the framing-device principle. The following are framing devices that attach forward to their content:

| Marker | Function | Example |
|--------|----------|---------|
| **ἰδού** | Deictic/mirative pointer | ἰδοὺ ἐγὼ ἀποστέλλω τὸν ἄγγελόν μου (Mark 1:2) |
| **διό** | Inferential conclusion | διὸ καὶ ὁ θεὸς αὐτὸν ὑπερύψωσεν (Phil 2:9) |
| **οὖν** | Resumptive/consequential | οὖν as post-positive, attaches to its clause |
| **νῦν δέ** | Discourse pivot ("but as it is") | νῦν δὲ χωρὶς νόμου δικαιοσύνη θεοῦ πεφανέρωται (Rom 3:21) |
| **ἀλλά** | Adversative correction | Already in our rules — confirmed as framing device |
| **γάρ** | Explanatory ground | Already in our rules — confirmed as framing device |
| **πλήν** | Restrictive adversative | πλὴν ὅτι τὸ πνεῦμα... διαμαρτύρεταί μοι (Acts 20:23) |
| **τοιγαροῦν** | Strong inference | τοιγαροῦν καὶ ἡμεῖς... τρέχωμεν (Heb 12:1) |

These are not merely "break triggers" — they are framing devices whose function is to introduce what follows. Never orphan them at the end of a line; they lead their content.

#### 4. ἰδού Three-Type Distinction

**Principle (adapted from the BOM "behold" distinction):** ἰδού in the GNT functions in at least three distinct ways, each with potentially different colometric treatment:

1. **Deictic (pointing):** Directs attention to a specific person, object, or scene. Common in narrative: ἰδοὺ ἀστὴρ προῆγεν αὐτούς (Matt 2:9 — "behold, a star went before them"). The ἰδού attaches forward to the thing pointed at.

2. **Mirative (surprise/discovery):** Marks unexpected information. Common in miracle narratives and apocalyptic: καὶ ἰδοὺ σεισμὸς μέγας ἐγένετο (Matt 28:2 — "and behold, a great earthquake occurred"). Often paired with καί. The surprise is the frame for the event.

3. **Logical-connective (discourse pivot):** Introduces an argument, prophecy, or announcement. Especially in prophetic speech: ἰδοὺ ἐγὼ ἀποστέλλω ὑμᾶς ὡς πρόβατα (Matt 10:16 — "behold, I send you out as sheep"). Functions as a discourse marker more than a deictic pointer.

**Status: UNSETTLED.** The three-type distinction is ported from BOM work but not yet tested on GNT material. Open questions:
- Does type 3 (logical-connective) benefit from merging with its clause rather than standing alone?
- How does ἰδού interact with καί ἰδού (which may always be mirative)?
- Does the LXX-influenced ἰδού in Luke-Acts behave differently from the Matthean usage?
- Should ἰδού be added to the FEF marker inventory?

**Action item:** Test on Matt 1-2 (heavy ἰδού usage), Luke 1-2 (Septuagintal style), and Rev 1-3 (prophetic/apocalyptic).

#### 5. Syntactic Bond Rules — Expanded

Several syntactic bond rules already appear in our Carry-Over Rules section. The following additions ensure completeness, adapted from the BOM audit:

**New rule — Never split periphrastic constructions:** Greek periphrastic constructions (εἰμί + participle, e.g., ἦν διδάσκων "was teaching," ἔσονται... ὑποτασσόμενοι "will be subject") function as single verbal units. The auxiliary and participle must stay on the same line. This is the Greek equivalent of the BOM's "never split auxiliary from main verb" rule.
- Example: ἦν γὰρ διδάσκων αὐτούς (Mark 1:22) — never split ἦν from διδάσκων.
- Also applies to μέλλω + infinitive (μέλλει... ἔρχεσθαι), ἄρχομαι + infinitive (ἤρξατο διδάσκειν).

**New rule — Never split negation from negated element:** οὐ/μή and their compounds (οὐδέ, μηδέ, οὐκέτι, μήποτε) must stay with the word they negate. Already implicit in our practice but now explicit.
- Example: οὐκ ἔστιν ὧδε (Mark 16:6) — never strand οὐκ at line end.

**Confirmed existing rules (now cross-referenced with BOM equivalents):**
- Never dangle conjunction at line end (Carry-Over Rule 1) — confirmed
- Never split verb from direct object (Carry-Over Rule 2) — confirmed
- Never end on article (Carry-Over Rule 6) — confirmed
- Vocative units indivisible (Carry-Over Rule 7) — confirmed
- Fixed phrases stay together (Carry-Over Rule 8) — confirmed

#### 6. Qualifying Phrases — Escalation vs. Restriction

**Principle:** A qualifying phrase that **restricts** the preceding claim belongs with it on the same line. A qualifying phrase that **escalates** — pushing the claim to a further extreme — earns its own line, because the escalation is itself a thought that benefits from its own arrest.

**Greek adaptation:**

**Restriction (merge):** Phrases introduced by εἰ μή, πλήν, ἐκτός, μόνον that limit the scope of the preceding statement:
- πάντα μοι ἔξεστιν ἀλλ᾽ οὐ πάντα συμφέρει (1 Cor 6:12) — the restriction completes the thought on one line.

**Escalation (break):** Phrases that push the preceding claim to its limit, often with εἰ μή + extreme case, or a comparative/superlative intensifier:
- ἐκενώσεν ἑαυτὸν μορφὴν δούλου λαβών... / γενόμενος ὑπήκοος μέχρι θανάτου, / θανάτου δὲ σταυροῦ. (Phil 2:7-8) — each step is an escalation: death, then *crucifixion-death*. The θανάτου δὲ σταυροῦ escalation earns its own line.
- ὑπὲρ ἐκ περισσοῦ ὧν αἰτούμεθα ἢ νοοῦμεν (Eph 3:20) — the escalation beyond asking or imagining.

**Test:** Does the qualifying phrase narrow the scope (restriction → merge) or intensify the claim (escalation → break)?

#### 7. Vocative Rule (Simplified — supersedes earlier distinctions)

**SUPERSEDED.** The three-category vocative distinction (epistolary / narrative / compound) explored during the Mark 4 and Acts 1 editorial passes has been resolved into a single universal rule. See the "Vocative Rule" section in "Principles Established by v4 Editorial Pass" above. All vocatives get their own line — no categories needed. The earlier distinction between epistolary and narrative vocatives was dissolved by recognizing that ALL vocatives are both atomic thoughts (complete address acts) and breath units (natural oral-delivery pauses). Confirmed by Luke 1:3 κράτιστε Θεόφιλε discussion.

#### 8. ὅτι Cataphoric/Anaphoric Distinction

**Principle (adapted from BOM Rule 19):** ὅτι clauses function differently depending on whether they point forward (introducing new content) or backward (restating/grounding what was just said).

**Cataphoric ὅτι (new content — break):** The ὅτι introduces information the reader hasn't heard yet. It earns its own line:
- λέγω ὑμῖν ὅτι... (I say to you that...) — the ὅτι clause is the new content.
- Content-ὅτι after verbs of perceiving, knowing, saying: breaks at ὅτι.

**Anaphoric ὅτι (restating — merge candidate):** The ὅτι clause restates or grounds what was just said. Common in Johannine style:
- ἐν τούτῳ γινώσκομεν ὅτι... (by this we know that...) — the ὅτι clause merely unpacks "this." Merge candidate.

**ὅτι recitativum (speech marker — own line):** Functions as a quotation marker introducing direct speech. Treat as speech attribution: the ὅτι-introduction gets its own line, the speech begins on the next.

**Status: UNSETTLED.** The three-way distinction is clear in theory but needs testing against actual GNT material to establish consistent practice.

#### 9. Authorial Style Principle

**Principle:** The same four colometric criteria apply uniformly to all NT authors. Do not adjust thresholds, rules, or sensitivity by author or genre. Let the colometric output reveal authorial differences rather than encoding assumptions about them.

This means: Mark's paratactic short lines and Paul's periodic long lines both emerge from applying the same criteria consistently. The difference in output IS the finding — it reflects genuine compositional differences between authors, not editorial preferences about how each author "should" look.

**Corollary:** Colon-length distributions, FEF density, average words per line, and other quantitative measures derived from the colometric output are valid for stylometric analysis precisely because the criteria are uniform. If we adjusted thresholds for Paul, the Paul-specific measurements would reflect our adjustments, not Paul's style.

**Established by:** The BOM Reader project proved this works — applying one method uniformly across the Book of Mormon produced measurable voice differentiation (oratorical voices averaged 7.7 words/line; narrative voices 9.1) without any author-specific tuning.

#### 10. Future Work — Parallel Diagnostic Scanner

Build a Runge-informed diagnostic script (analogous to the BOM project's `parry_split_candidates.py`) that scans all v3/v4 output for repeated syntactic frames and flags lines where internal parallel boundaries suggest splits. Target patterns:
- Repeated ὅτι clauses (creedal formulas, Johannine "I am" statements)
- εἴτε...εἴτε lists (Paul's hypothetical catalogs)
- οὔτε...οὔτε chains (negation lists)
- Repeated participial constructions (hymnic passages)
- μακάριοι chains (Beatitudes, Revelation's seven beatitudes)
- οὐαί chains (Woe oracles)

This would accelerate the identification of passages where the automated pipeline fails to stack parallel structures consistently — the #3 failure mode identified in the session 4 scope audit.

---

### Update — 2026-04-11 (Acts 1 editorial pass)

Insights confirmed or discovered during the Acts 1 v4 editorial work:

- **Lukan periodic style as FEF:** Acts 1:1-4 confirmed as a Forced Extended Format. The periodic sentence suspends resolution across participial chains; the "least bad" break strategy is Option B — temporal/circumstantial frame → participial elaboration → main verb resolution. FEF-aware formatting in Luke-Acts means accepting longer lines for periodic sentences and using this three-layer structure rather than forcing short lines that break mid-thought.

- **Epistolary vs. narrative genre shift visible in colometry:** Acts 1:1-4 (epistolary prologue) produces long periodic lines; v5 onward produces short paratactic lines. The colometric line-length shift makes the genre boundary visible without editorial commentary. This may also reveal Semitic source material — vv5-11 have been identified by scholars (Torrey, Black) as showing Semitic interference, and the short paratactic lines corroborate this.

- **Standalone verb test refined:** Intransitive verbs of motion/state change (ἐπήρθη, ἐκαυματίσθη) can stand alone as a complete line. Transitive/speech verbs (εἶπεν, ἐδίδασκεν) cannot — they need their complement on the same line. Confirmed by Acts 1:15 editorial decision.

- **Elaborative apposition merges:** When a verb + action is followed by elaboration identifying WHO or WHAT (Acts 1:23 "they put forward two, Joseph... and Matthias"), the elaboration is not a new image — it identifies the same action. Merge as one line.

- **Geographic expansion stacking:** Acts 1:8 stacks "Jerusalem / all Judea / Samaria / the ends of the earth" as expanding concentric circles — each an implied "[you will be my witnesses] in X." This is the ellipsis principle applied to geographic lists.

- **Short genitive absolute merging confirmed:** Acts 1:4 "συναλιζόμενος" (while eating together) merges with its main verb as adverbial framing, consistent with Mark 4:35 "ὀψίας γενομένης" merge. Short circumstantial participles functioning as scene-setting frame merge with the clause they modify.

