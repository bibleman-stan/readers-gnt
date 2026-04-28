# Colometry Methodology Canon — Reader's GNT

This document is the authoritative reference for the editorial methodology behind sense-line (colometric) formatting in the Reader's Greek New Testament at gnt-reader.com. It is the intellectual heart of the project: line-breaking decisions determine how the text reads, breathes, and communicates.

## Foundational premise

The project's working hypothesis is that humans think, compose, and deconstruct (read and hear) in "sense-lines" — a term Skousen used for the Book of Mormon. We use it here in an expanded sense: atomic thought-units that correspond to how ideas are generated, encoded, and recovered. This hypothesis was reached intuitively and analogically, triggered by Royal Skousen's demonstration that the Book of Mormon could be rendered in sense-lines (*The Earliest Text*, 2009/2022). Skousen's stated rationale was specific to the Book of Mormon: his sense-lines aim to convey "a dictated rather than a written text," approximating how the original translation might have sounded during Joseph Smith's dictation. Stan took Skousen's term as a starting point and expanded the concept to the definition above. He then experimented with line breaks in the English Book of Mormon text, where the expanded definition appeared to expose idea-units sometimes obscured by editorial punctuation, versification, and line-break decisions. Stan applied the same method to the GNT, reasoning by analogy that what is true for the Book of Mormon is likely true for the Greek New Testament — and perhaps *any* text.

The methodology itself — three forces, structural justifications, merge-overrides, rules — emerged from hands-on editorial experimentation across all 260 chapters of the GNT. It is pragmatic, not theory-derived.

## Posture

The current phase is empirical: *where are the sense-lines, actually?* The method is instrumentation for answering that question. When the method produces a line that does not reveal a genuine sense-boundary, the method is wrong and gets revised. When the method produces a line that does, the method is working.

Scholarly alignment with cognitive-science, psycholinguistic, or classical-rhetorical frameworks may or may not emerge in a later consolidation phase. Any such alignment is opportunistic, not load-bearing. No framework external to the text is currently treated as the reason a rule works.

## Architecture

The colometric methodology sits on a three-layer architecture:

**Layer 1 — Generic Koine break-legality.** Constraints any competent editor of any Koine Greek text would observe: article + noun stays together, preposition + object doesn't split, postpositives can't start a line, periphrastics stay whole. Lives as a shape-capped table at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md) — 24 rows of syntactic signature + legality verdict + BDF/Smyth/Wallace citation. Not our editorial doctrine; a pointer to generic Koine grammar facts. R2–R7 live here.

**Layer 2 — Validators.** Mechanical checks that read Layer 1 and Layer 3 rules against Macula-Greek ([Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek), CC-BY 4.0) and MorphGNT ([morphgnt/sblgnt](https://github.com/morphgnt/sblgnt), CC-BY-SA) parse data. Two error classes: `MALFORMED` for Layer 1 violations (ungrammatical typography — must fix, Category A by default), `DEVIATION` for Layer 3 violations (grammatical but not our editorial convention — Category A/B/C gating per §3 Autonomy Boundary). Target directory split: `validators/syntax/` for Layer 1 checks, `validators/colometry/` for Layer 3 checks. Under active build.

**Layer 3 — This canon.** Editorial sense-line methodology specific to the Reader's GNT. Where and why we diverge from or add to generic Koine syntax to reveal atomic thought. The three forces (§1), five structural justifications (§2), four merge-overrides (§2), rules (§3), operational tests (§4), register operationalization (§5), and Greek-specific application data (§8) all live here. The Subtractive force in §1 is the contract with Layer 1 — we never violate it.

The division matters because it separates *what Greek grammar requires of any editor* (Layer 1) from *what our project chooses to do editorially* (Layer 3).

---

**What is this document?**

This document serves as a canon for laying out the main design philosophy (the *what / why / posture* of the project) as well as the pragmatic implementation rules and principles (the *how* — rules and tests Claude reads literally for editorial application). There are times when the line between design philosophy and operational implementation blends together. The structure aims to keep the integration honest while making the predominant character of each section legible at a glance.

- **Part 1 (The Method, §§1-4)** is the constitutional core: theoretical foundation (§§1-2) and operational rule reference (§§3-4). Each section header discloses whether the section is mainly philosophical, mainly operational, or dual-natured.
- **Part 2 (The Framework, §§5-8)** carries register operationalization, precedent and scope discipline, the change-protocol machinery (§6.5 Mandatory-audit triggers), and Greek-specific application supplements + scholarly material.
- **Part 3 (The Record, §§9-10)** is the historical appendix — superseded formulations and the chronological update log.
- **Layer 1 and Layer 2** are separate from this canon — see the Architecture section above. Layer 1 lives at `data/syntax-reference/greek-break-legality.md`. Layer 2 validators live at `validators/syntax/` and `validators/colometry/` (under active build).

**Reader's guide:**

- **Editor making editorial decisions** (typically a Claude session working on the corpus): focus on §§3-4 and §6.5. Consult §§1-2 for grounding when proposing or evaluating rules.
- **Scholar reading the method as a published artifact**: focus on §§0-1 (foundational premise + framework theory), §6 (precedent + scope), and §8 (Greek-specific application + exegetical convergence).
- **Tracking how a decision evolved**: §§9-10 carry the reasoning trail.

Some sections are dual-natured by design: §1 interleaves theoretical principles with their operational corollaries (e.g., the "reaching-for-split" vocabulary watchlist sits inside the Imposing-vs-Revealing philosophical principle); §2's five structural justifications each combine cognitive-prong (philosophical) with structural-prong (operational) arguments. **Treat bolded paragraphs as load-bearing** in those sections regardless of the surrounding prose's character. When revising philosophical prose in dual-natured sections, leave bolded paragraphs untouched unless the change is intentional and audited per §6.5.

---

# Part 1: The Method

*Everything in Part 1 is authoritative and current. Sections 1 through 4 contain everything an editor needs to make line-break decisions.*

---

## Section 1: The Framework

*Purpose: theoretical foundation for the three-forces architecture and the imposing-vs-revealing posture. **Dual-natured by design** — operational corollaries (vocabulary watchlists, fronting paradox, Showcase Acts 1:9) are embedded throughout. Treat bolded paragraphs as load-bearing for editorial application.*

Sense-line breaks are governed by **three forces** operating in concert: a **generative** force that proposes where breaks should happen, a **subtractive** force that vetoes breaks that would violate Greek syntax, and a **diagnostic** force that sharpens ambiguous cases.

### Mission and Method — the Discipline Framing

**Mission:** We are revealing sense-lines — atomic thoughts the reader can process as discrete units.

**Method:** The framework below is syntax-constrained. This is **not** because syntax is primary to the mission — atomic thought is. It is because **syntactic violation is fatal while sense ambiguity is recoverable within the permitted space.** An ungrammatical line cannot be rescued by good sense. A grammatical line that isn't the ideal sense-boundary can still be read. The method therefore leads with the syntactic floor (subtractive force) so that editorial judgment (generative force) operates only within the legal-break space.

The mission is sense-driven. The method is syntax-constrained.

### Framing Principle: Container, Not Originator

**The atomic thought is the primary, originating reality.** It is what the author wants to say, prior to and independent of any particular language. Greek, Hebrew, Aramaic, English, and Chinese speakers all compose in thought units. The atomic-thought target is *language-invariant*.

**Syntax is the container, not the originator.** Every atomic thought is *always already* shaped by the grammatical framework of the language it was born in — there is no unclothed "pure thought" underneath waiting to be extracted. The container constrains: Paul could not express his thought without choosing Greek syntactic patterns, and those patterns imposed fixed structural commitments (word-order possibilities, correlative pairs, conditional shapes, case government). But the container does not *originate* the thought. The thought exists first and fits itself into whatever vessel is available.

This is the classical distinction between **logos endiathetos** (the thought in the mind) and **logos prophorikos** (the thought as uttered). Colometric recovery targets the endiathetos through the prophorikos because the prophorikos is all we have.

**Consequences for the framework:**

1. **Propositions (atomic thoughts) are the generative force because they are what we are recovering.**
2. **Syntax is the subtractive force — the evidence surface through which propositions become visible in this particular language, and simultaneously the floor below which no line can legally sit.** Syntax both reveals where propositions end (thought-marking syntax) and constrains where breaks are legal (Layer 1 break-legality, complement integrity, formula integrity).
3. **Grammar is bigger than syntax** — it includes lexicon, morphology, pragmatics, phonology. Most of these do not affect colometric decisions. "Syntactic" is more precise than "grammatical" when we describe the evidence we use. Morphology (case, mood, person, tense) is the surface we read syntax *off of* — vocative case tells us a word is in an address relation; 2p verb inflection tells us there is an implicit "you" subject that a vocative can name.
4. **Cross-linguistic invariance is preserved.** Paul's atomic thought units in Romans are the same units whether read in Greek, English, or Chinese. Only the container changes. We are not imposing Greek syntax on English readers; we are recovering the shape Paul's thoughts actually had when he dictated them.

### The Three Forces

#### Force 1 — Generative: Propositions

**Each proposition is an atomic thought. Default SPLIT at every proposition boundary.**

A "proposition" is, at first pass, a complete predication — subject + finite verb + complement. This is the default operationalization. But predication is not the only form propositions take. The five closed-list structural justifications (Section 2) extend the generative force to cases where formal structure enables the reader to reconstruct the full thought even when overt predication is absent:

1. Formally-marked parallel series
2. Portrait-building attribute accumulation
3. Speech-act announcement convention
4. Classical comma
5. Substantive adjunct as own focus

The generative force proposes candidate breaks. Each candidate has to pass through the subtractive force before becoming an actual break.

**Atomic thought is relative to the author's resolution.** "Atomic" is not a fixed unit size; it is the smallest chunk the author intended to be processed as a single, self-contained, coherent unit of thought-meaning.

For plainer narrative (Mark's simpler scenes), atomic usually means a complete sentence-level predication. For more literary authors (Luke, Paul, John at their most crafted), "atomic" often is messier, where it can include grammatically-independent sub-units — most notably **genitive absolutes used as interjectory frames**.

A gen abs is often able to pass the atomic-thought test on its own because it carries its own subject and its own predicate. It is "absolute" in the grammatical sense of being *loosened from* (Latin *absolutus*, Greek *apoluton*) the syntactic government of the main clause — its subject is not governed by any element in the main clause (Smyth §2070). The "dependency" on the main clause is narrative, not grammatical.

Sophisticated authors build at a finer resolution because their audiences could track it — the colometric grid must track *their* sophistication, not impose a lowest-common-denominator rule.

**Thought-marking syntax vs. structural syntax** (how propositions announce themselves):

- **Thought-marking syntax** reveals where one atomic unit ends and the next begins: main-verb shifts, clause boundaries, subject changes, verb-subject binding (including vocative-as-subject), appositive coreference, camera-angle turns (proposition specification in the form of a new addressee, new speaker, new POV on a previous proposition). This is where the generative force finds its surface clues.

- **Structural syntax** is fixed Koine Greek language patterns that do *not* automatically map to thought boundaries, but rather constrain them in a particular way for a Greek-speaking audience: conditionals (ei...X, [then] Y), correlatives (kai...kai, men...de, oute...oute), comparatives (mallon...e), result clauses tightly bound to their head. These have fixed shapes GNT authors, as Greek speakers writing to Greek-speaking audiences, had to use, but the thought may be atomic across them *or* may resolve into multiple units depending on what the clauses are doing.

Defense against the obvious objection that "you're just breaking at every grammatical feature": we are breaking at the features that *mark thought boundaries*, not at every fixed Greek construction. These boundaries, however, often do intersect with each other. A men/de contrast earns a break when each limb is its own atomic claim, but it does not earn a break just because men/de is there.

#### Force 2 — Subtractive: Syntax

**Not every proposition-boundary split is legal. Greek syntax forbids some breaks.** This is the hard floor.

Three closed-list veto classes:

1. **Layer 1 break-legality** — generic Koine syntactic constraints documented in [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md). Article + noun split, preposition + object split, periphrastic split, dangling conjunction, line-final negation, crasis, line-initial postpositive, etc. These are what any competent editor of any Koine text would observe regardless of our editorial choices. Rules R2-R7 are Layer 1.

2. **Complement integrity.** A line whose atomic thought requires a syntactic complement to be grammatically complete cannot be split before that complement. Covered by R10 (cognition-verb ὅτι complement), R11 and R23 (speech-intro frames, dative-subject-of-infinitive), M2 (verb + direct-object clause-nucleus bond).

3. **Formula integrity.** Fixed multi-word units function as single constituents. Covered by Layer 1 entries for fixed phrases plus complement-adjacent rules.

When the subtractive force vetoes a proposition-boundary split, **merge wins**. Editorial judgment operates only within the space syntax permits.

The merge-override framework (M1–M4 in Section 2) encodes additional subtractive cases — gorgianic bonded pair (M1), verb-object clause-nucleus bond (M2), bare-governor indivisibility (M3), fragmented atomic thought-unit (M4) — for situations where a split-trigger fires but syntactic or cognitive integrity would be ruptured by applying it.

#### Force 3 — Diagnostic: Single Image

**When the generative + subtractive forces leave ambiguity** — a candidate break is syntactically legal and a proposition-break plausibly exists, but it is not obvious whether to split or merge — **the image test sharpens the decision.**

Each line should paint a single image or picture in the mind. Close your eyes and picture the scene. Does the line make you see ONE thing? If two distinct images, split is the right call. If one coherent image, merge is the right call.

The image test operates within syntactic permission — it never overrides a syntactic veto. It is a sharpener, not a generator and not a floor.

### The Framework in Practice

```
Generative  — Propositions  — default SPLIT at every proposition boundary
Subtractive — Syntax        — forbids some splits: Layer 1 + complement integrity + formula integrity
Diagnostic  — Image         — sharpens ambiguous cases within the permitted space
```

### Why Predication Is the Default (and When It Is Not Enough)

Predication is the most common encoding of atomic thought — a complete clause with subject + finite verb + complement. It is the natural default operationalization of the generative force. But it is not the only encoding. Stacked attributes can paint one portrait; parallel series can stack members whose shared predicate is recoverable; classical commata can carry rhetorical weight without full predication; speech-act tags announce a complete communicative event.

The two-prong exception test (Section 2) asks: (1) is there a sense-unit here? and (2) can the reader reconstruct it from the formal structure? When both answers are yes, the line is valid even without explicit predication.

### The Priority Order When Forces Leave Ambiguity

**Chunking > Oral > Rhetorical**

When the three forces leave room for multiple valid choices:

1. **Cognitive chunking** — line breaks first serve comprehension. Each line is a unit the reader can process as one cognitive bite. This is the foundational purpose of colometric formatting.
2. **Oral delivery** — line breaks support read-aloud at natural breath pace.
3. **Rhetorical structure revelation** — line breaks make the author's compositional architecture visible (parallels, escalation, climax, chiasm). This is the literary/scholarly purpose.

When these conflict, chunking wins. A break that aids cognitive chunking but flattens some rhetoric is acceptable. A break that reveals rhetoric but creates a fragment that cannot be processed is not.

### Imposing vs. Revealing — Scope Discipline

**Line breaks follow structure that already exists in the text. If a rule produces a line that does not match the text's inherent structure, the rule is wrong.**

- We do not impose visual structure that the grammar does not directly support.
- We do not construct grammatical categories to justify editorial instincts.
- If a break cannot be named in standard grammatical terms, it is an editorial decision — which is fine, but should be labeled honestly (Category B/C per §3).
- If a proposed rule consistently produces lines that don't sound like the text, the rule is imposing rather than revealing and is rejected.

**This is a presentational layer, not an analytical one.** Our job is to render the text so its grammatical and cognitive structure is visible at the line level. What scholars do on top of that — identify chiasms, mark rhetorical figures, perform discourse analysis, write commentary — is downstream work that our edition *enables* but does not perform.

**The boundary test:** if a feature requires *interpretation* of authorial intent or rhetorical strategy to detect, it is out of scope. If it can be identified by the grammar alone (case, mood, syntactic position, lexical markers), it is in scope.

**In scope (grammatical structure made visible):**
- Clause boundaries (main, subordinate, participial)
- Subordinator-introduced breaks (hina, hoti, hotan, hote, ean, hopos, hoste, etc.)
- Discourse markers as signals (kai, de, gar, oun, alla)
- Correlative pairs (men/de, me/alla, ou/alla)
- Genitive and accusative absolutes (grammatically independent constructions)
- Vocatives (refined three-way treatment — see Section 3)
- Periphrastic constructions and their elliptical extensions
- Dative subject of infinitive (chunks with the embedded proposition)
- Asyndetic lists (each enumerated nominal is its own line)
- Prepositional catenae (each prep phrase is its own constituent)
- Parallel stacking, men/de contrast, kai + finite verb chains

**Out of scope (analytical / interpretive overlay):**
- Chiasm detection (research-grade rhetorical analysis)
- Klimax / gradatio identification (rhetorical figure)
- Diatribe Q-A pair tagging (discourse-pragmatic analysis)
- Section headers / epistolary form criticism (salutation / thanksgiving / body / paraenesis)
- Anacolutha tagging (e.g., Eph 3:1 -> 3:14 pause-and-resume)
- Period anchor + clause-depth indentation (imposes a hierarchy reading; interpretive overlay)
- Authorial intent inference, theological emphasis marking, parable structure annotation

The colometric grid is **flat by design** — every line has equal visual status. We do not introduce hierarchy via indentation, font weight, color, or spatial offset, because hierarchy is interpretive.

**Corollary — punctuation must not have deterministic force.** The commas, semicolons, colons, and dashes in the SBLGNT are editorial additions — not original to the text. They may corroborate a line-break decision but CANNOT justify one by themselves. Test: remove the punctuation mentally and ask whether the break still holds on purely grammatical grounds.

**Corollary — the "reaching-for-split" warning.** When the grammatical case for a split is borderline and you find yourself reaching for rhetorical-motif, image-analysis, cognitive-predictive-processing, oral-rhythm, theological-weight, soteriological-significance, pastoral-force, narrative-climax, prosodic-emphasis, doctrinal-stakes, or any analogous non-grammatical category as a tiebreaker, **that is the signal that scope creep is happening.** The scope-disciplined default in a borderline case is to keep the grammatical constituent intact — i.e., **prefer merge to split** when the grammar is ambiguous. *See `feedback_rhetoric_bandwagon.md` catches list for examples of these terms in action.*

**The fronting paradox — marked word order argues for MERGE, not split.** When a grammatically tight unit (verb + its required-case complement, or other bound constituent) appears in a *marked* word order — e.g., object fronted before its governing verb — the natural editorial instinct is to split at the fronted element as a way of "visualizing the emphasis." **This instinct is wrong.** The rhetorical effect of fronting depends on the grammatical unity *staying intact*. The marked arrangement is felt as emphatic precisely because the hearer processes the fronted element in a non-default position *within a single breath unit*. Splitting at the fronted-element boundary mechanizes the emphasis — it imposes a pause that was not in the original oral delivery — and paradoxically *diminishes* the rhetorical force.

*Case studies:*
- **Gal 2:9 — split** (pillars characterization on own line): two distinct thoughts (the named persons vs. their ironic characterization). Subject + substantival-participial-phrase appositive, where the appositive is six words, non-trivial, and introduces the dokountes motif. Grammatical warrant for split is the substantival-participle-as-own-thought rule.
- **Gal 2:10 — merge** (fronted ton ptochon kept with mnemoneuomen on one line): mnemoeneuo requires genitive for its object. The fronted genitive + restrictive monon create a marked word order whose rhetorical force depends on the grammatical unity staying intact.

### Showcase — Acts 1:9

```
kai tauta eipon             <- aorist nominative ptc (FEF frame; subject = Jesus)
bleponton auton             <- GENITIVE ABSOLUTE (subject = disciples); interjectory
eperthee                    <- main verb resolving eipon
kai nephele hupelaben auton apo ton ophthalmon auton.
```
The gen abs interrupts the FEF suspension with a camera shift to the disciples' perspective, then the main verb drops the resolution. Merging all three into one line destroys Luke's three-beat rhythm and flattens his voice. **A gen abs embedded within an FEF should remain on its own line.**

---

## Section 2: The Unless Conditions (Closed List)

*Purpose: operational gating definitions for when exceptions to default-split apply. Five structural justifications (closed list) + four merge-overrides (closed list) + the complete decision procedure. **Dual-natured by design** — each justification interleaves cognitive-prong (philosophical) and structural-prong (operational) arguments at sub-paragraph granularity.*

When a line fails the strict predication test, it may still stand if it passes BOTH prongs of the exception test. If either prong fails, merge. The two-prong requirement prevents the exception from becoming a blank check — editorial intuition alone cannot override the predication default.

### The Two-Prong Exception Test

**Cognitive prong:** Is this a demonstrable atomic thought-unit — one new focus the reader processes as a single chunk?

**Structural prong:** Is there a formal justification for the reader to reconstruct the full thought?

Both must pass. The cognitive prong without the structural prong is just "it feels like an idea unit" — not enough. The structural prong without the cognitive prong is just "there is a grammatical pattern" — not enough either.

### The Five Structural Justifications (Closed List)

**Generating principle:** All five justifications are instances of a single underlying property: *formal structure in the text enables cognitive recovery of the full predication despite its absence from the line.* The reader can reconstruct "who did what" because the text provides machinery — parallel markers, accumulation patterns, speech-act conventions, brevity-as-emphasis, or peripherality-plus-substance — that makes the missing predicate recoverable or makes the adjunct its own focus. If no such machinery exists, the line is genuinely incomplete and must merge.

This list is extensible only by worked examples + adversarial validation. Any proposed fifth justification must (a) demonstrate that it is a genuinely distinct instance of the generating principle, not a restatement of an existing justification, and (b) survive an adversarial challenge.

#### 1. Formally-Marked Parallel Series

**Definition:** Members of a series connected by formal markers (kai-linked, correlative particles eite/oute/mete, asyndetic parallel members) where the shared predicate is cognitively recoverable from the parallel structure. This is broader than just correlative particles — any formally-marked parallel series sharing a recoverable predicate qualifies.

**Cognitive prong argument:** The reader does not experience each member as incomplete; they experience it as a beat in a series whose predicate is active in working memory. Each member reactivates the shared verb.

**Structural prong argument:** The formal markers (repeated conjunction, elided verb, parallel grammatical structure) provide the reader with the machinery to reconstruct the full predication for each member.

**PASS example — correlative with distinct predicates:**
```
oute gamousin
oute gamizontai,
```
(Matt 22:30 / Mark 12:25 / Luke 20:35 — two distinct predicates: active and passive sides of the marriage transaction. Each is a complete predication; each stands.)

**PASS example — triadic parallel series:**
```
eite oun esthiete
eite pinete
eite ti poieite,
```
(1 Cor 10:31 — three distinct predicates, three distinct activities. Each is a complete predication via the parallel structure.)

**PASS example — triadic yield list:**
```
kai epheren hen triakonta
kai hen hexekonta
kai hen hekaton.
```
(Mark 4:8, 4:20 — each member has a recoverable verb "bore" from the first member.)

**The test for stacking vs. staying:** Does each correlative/parallel member have its own DISTINCT predicate? The presence of a finite verb is necessary but not sufficient. The decisive question is whether the predicate belongs to that member alone, or whether a single predicate is shared across all members (as compound subjects, compound objects, or compound qualifiers). A shared predicate = one proposition = stay on one line.

**Stay example — compound subject sharing one verb:**
```
oute ses oute brosis aphanizei
```
(Matt 6:20 / 6:19 — two subjects, one verb aphanizei; the series is a compound-subject proposition, not two propositions.)

**The <=3 qualifier rule — triadic co-referential modifiers stay together.** Humans can hold three facets of one image as one thought unit. When a triad is three descriptors of ONE thing, they form a "three-in-one" thought and belong on one line:
- `thysian zosan hagian euareston to theo` (Rom 12:1) — three adjectives on ONE sacrifice. One line.
- `to agathon kai euareston kai teleion` (Rom 12:2) — three qualities of ONE will. One line.
- `chryson kai libanon kai smyrnan` (Matt 2:11) — three objects of ONE verb. One line.

#### 2. Portrait-Building Attribute Accumulation

**Definition:** A stack of attributes painting a single portrait where the image, not the predicate, is the structural unit.

**Cognitive prong argument:** A set of attributes building one portrait functions as one cognitive chunk even without an explicit verb, because the portrait IS the idea unit.

**Structural prong argument:** The accumulation pattern (adjective, adjective, prepositional phrase) is a recognized grammatical form for predicate-complement stacking. The reader reconstructs "X is [attribute]" or "X who is [attribute]" from context. The diagnostic force (single image) provides the formal justification.

**Detectable signature:** A verse or span where (a) no finite verb appears until a later verse, (b) the lines are successive characterizations of the same subject, and (c) each characterization could be extracted as a standalone description.

**Canonical cases:**
- **Acts 10:1-3** (Cornelius): `hekatontarches ek speires` / `eusebes kai phoboumenos ton theon` / `poion eleemosynas pollas to lao` — no finite verb until v.3 (eiden). Each line is one attribute of Cornelius.
- **Pauline salutations** (Rom 1:1, 2 Cor 1:1, Gal 1:1, etc.): `Paulos apostolos` / `dia thelematos theou` — each credential on its own line.

*(Heb 1:3-4 was previously cited here; removed 2026-04-25 because the rule's detectable signature requires "no finite verb appears until a later verse" and Heb 1:3 has ἐκάθισεν within the verse. The split of Heb 1:3 L1's two distinct-image attributes is governed by §3.16 coordinating-syntax-with-distinct-images, not by this justification.)*

#### 3. Speech-Act Announcement Convention

**Definition:** Formulas that announce a speech act — speech-intro verbs (lego, phemi) as standalone lines — where the announcement of speech is itself a complete communicative act.

**Cognitive prong argument:** The speech act IS the predication. The reader processes "he said" as a complete communicative event: someone spoke, to an audience. The content of the speech is a separate cognitive frame.

**Structural prong argument:** The speech formula is syntactically complete as a speech-act predication. The colon or ano teleia after the formula is the textual signal of a voice shift.

**PASS examples:**
```
kai elegen autois:
```
```
kai eipen auto:
```
Each is a complete speech-act predication. The speech content follows on the next line.

#### 4. Classical Comma

**Definition:** A very short emphatic unit with disproportionate semantic weight. The name preserves the classical Greek κόμμα ("cut, piece") — a short member of a larger unit.

**Cognitive prong argument:** These carry enough force to constitute a cognitive chunk despite lacking traditional predication structure. The reader processes each as a single, complete communicative beat.

**Structural prong argument:** The brevity itself is the structural justification. A one-word or two-word fragment that the author placed in isolation is doing rhetorical work that a longer elaboration would dilute.

**PASS example:** `thanatou de staurou.` (Phil 2:8) — the escalating appendage. The de triggers a new line; the dramatic compression IS the rhetorical device.

#### 5. Substantive Adjunct as Own Focus

**Definition:** A fronted or trailing adjunct (temporal PP, locative PP, causal PP, genitive absolute, participial frame, prepositional catena element) that is (a) grammatically peripheral to the matrix predication's core truth AND (b) carries substantial semantic content — enough that the reader processes it as an independent focus rather than background.

**Cognitive prong argument:** The adjunct functions as its own cognitive focus. A reader processing "[in the fifteenth year of Tiberius's reign] / the word of God came" holds the dating adjunct as one frame and the main event as another. Merging them forces the reader to process temporal-frame + event as a single thought.

**Structural prong argument:** Greek syntax treats these adjuncts as detachable — they can front, trail, or be omitted without rupturing the matrix predication. The genitive absolute construction is the sharpest case (literally "loosened from" the main clause by case disjunction — Smyth §2070). Prepositional phrases, participial frames, and catenae of semantically distinct PPs are detachable by weaker but still real grammatical warrant. When the content is substantial (not a 3-word trivial adverbial), the detachability becomes cognitively active.

**Test:** Can the adjunct be paraphrased as its own "when / where / why / how" clause that answers a question the matrix leaves open? If yes, it's a substantive adjunct and earns its own line. If the adjunct is short (≤3 words) and trivially adverbial, merge.

**Canonical cases:**
- **Genitive absolute** (R19 — always own line). `blepontōn autōn` (Acts 1:9) — camera shifts to the disciples' perspective as an interjectory frame; core event (ἐπήρθη) continues on its own line.
- **Prepositional catena** (§8). 2 Cor 6:4-7 ἐν-catena (ἐν ὑπομονῇ πολλῇ, ἐν θλίψεσιν, ἐν ἀνάγκαις, ἐν στενοχωρίαις...) — each element is a substantive adjunct on its own line.
- **FEF periodic frame** (§5, §8). Luke 3:1-2 — five genitive-phrase temporal adjuncts (ἐν ἔτει πεντεκαιδεκάτῳ τῆς ἡγεμονίας Τιβερίου Καίσαρος... ἐπὶ ἀρχιερέως Ἅννα καὶ Καϊάφα...) — the matrix ἐγένετο ῥῆμα θεοῦ lands only after the adjunct chain completes.
- **Fronted temporal existential.** John 1:1 `ἐν ἀρχῇ` — only 2 words but carries the Gospel prologue's entire temporal frame; the brevity-but-substance is the edge case flagged by the ≤3-word caveat above (substance can override length).

**Relation to R19, prep-catena (§8), FEF:** These are the mechanical operationalizations of justification #5 for specific adjunct classes. Justification #5 is the generating principle; R19 (gen abs), prep-catena treatment (§8), and FEF periodic-frame treatment (§5) are how it lands for those classes. A future adjunct pattern not covered by the existing rules inherits its warrant from justification #5 rather than requiring a new top-level rule.

**Contrast with the retired breath criterion:** justification #5 absorbs the cognitive work breath was loosely doing (long lines need breaking) — with a principled grammatical-peripherality test rather than an un-thresholded "feels too long" judgment. Breath itself is retired (§9 Superseded Formulations); substantive adjunct is the proposition-side replacement for the cognitive-chunking work breath was smuggling in.

---

### Merge-Override Conditions (Closed List)

**Symmetric counterpart to the five split-triggers above.** Where the five justifications describe cases in which the merge default is overridden to produce a split, the four merge-overrides below describe cases in which an apparent split-trigger is itself overridden, returning the members to one line. The default is still merge; these override conditions catch cases where a naive application of the split-triggers would fragment a unit that should stay whole.

**Generating principle:** Even when a line looks like it could pass the structural prong (formal markers are present), merge wins when the resulting fragments would fail on more basic grounds — the chunk is not actually two propositions (M1), the clause nucleus would be ruptured (M2), the fragment cannot stand as atomic thought (M3), or the resulting pieces would fail the atomic-thought test that the structural prong was supposed to enable (M4).

These override conditions are extensible only by worked examples + adversarial validation, same rule as the split-triggers.

#### M1. Gorgianic Bonded Pair

**Definition:** N=2 coordinate members forming a unified rhetorical image. The two members together constitute a single hendiadys rather than two distinct propositions. Even with formal καί-linkage (which would normally trigger justification 1), if the pair is bonded, merge.

**Test:** Can the two members be paraphrased as a single hendiadys or unified image? Do they carry shared rhetorical weight without independent predicative force?

**Canonical cases:**
- `kopo kai mochtho` (2 Cor 11:27) — "labor and toil" as one image of exhaustion
- `chairein meta chaironton, klaiein meta klaionton` (Rom 12:15) — two classical comma halves that together constitute one paraenetic command
- `Tolmetai, authadeis` (2 Pet 2:10) — asyndetic N=2 pair of bonded adjectives, same person

**Contrast with the ≤3 qualifier rule** (Section 2, justification 1): the ≤3 rule covers triadic co-referential modifiers of ONE thing (stay). The gorgianic-pair rule covers N=2 specifically — two members whose bonding is the rhetorical point.

**Tie-breaker when M1 and justification 1 both seem to apply (N=2 formally-marked pair):**
- If each member has a distinct finite verb AND the verbs are not synonymous, cognate, or intensification variants of each other → justification 1 wins → split. Example: `οὔτε γαμοῦσιν / οὔτε γαμίζονται` (Matt 22:30) — active and passive sides of distinct predications.
- If the two verbs are semantically synonymous, form a recognizable binomial idiom, or function as a hendiadys (single unified act expressed via two near-synonyms) → M1 wins → merge. Example: `Δαιμόνιον ἔχει καὶ μαίνεται·` (John 10:20) — one diagnostic judgment expressed via two complementary terms.
- The test is structural (verb semantic class) not intuitive. If the two verbs belong to clearly different semantic domains, they are not a gorgianic pair even if only N=2 and formally marked.

**Strict-application caveat — M1 rejection does not license split.** M1's "different semantic domains" tie-breaker *withdraws the gorgianic merge protection*; it does NOT by itself license a split. Before flipping to SPLIT, check whether another merge protection fires: M2 (verb-object bond), M3 (bare-governor), M4 (fragmented atomic thought), R11 (speech-intro / approach+touch), R8's καί-merge default for short coordinate clauses, R28 textual-asymmetry preservation when applicable, and default-merge when grammar is ambiguous. Split only when ALL merge protections are exhausted AND both resulting fragments pass the atomic-thought test. Rationale: the canon's overall posture is merge-by-default; M1 is one of several merge levees, and its failure signals "check the others", not "proceed to split".

#### M2. Verb-Object Clause-Nucleus Bond

**Definition:** A finite verb and its direct object (or obligatory complement) on short phrases stay on one line, even under split-trigger pressure. The clause nucleus is the minimal atomic predication and cannot be fragmented.

**Test:** Would splitting strand the verb without its complement, or strand the object without its governor? If yes, merge.

**Canonical cases:**
- `eipe / hina hoi lithoi houtoi artoi genontai` — reject: εἰπέ needs its ἵνα complement (Matt 4:3)
- `egertheisa / dieikonei` — reject: merging is correct because ἠγέρθη and διηκόνει form one narrative beat (Matt 8:15)
- `ton prophetas / kai sophous / kai grammateis` on 23:34 — accept split because the verb ἀποστέλλω has multiple distinct objects with formal parallel marking (justification 1 overrides)

The distinction from M1: M2 concerns verb + obligatory complement (transitive nucleus); M1 concerns coordinate members of a semantic pair.

#### M3. Bare-Governor Indivisibility

**Definition:** A head word — participial adjective (μεστούς, πλήρης, ἔνοχος), governing participle (εἰδότες, λέγοντες, εἰπών), discourse particle (ἀλλά, δέ, γάρ standalone) — cannot stand on its own line without at least one complement, object, or dependent. The bare governor fails the atomic-thought test because it is grammatical machinery awaiting content, not a complete predication.

**Test:** Can the isolated head-word be read as a complete thought? Or does the reader's attention dangle forward, expecting completion on the next line?

**Canonical cases:**
- Session 18 Rom 1:29 reversal: initially split as `mestous / phthonou / phonou / ...`; reverted to `mestous phthonou, / phonou / ...` — μεστούς alone is not a thought
- Session 19 Heb 1:1 merge: `Polymeros kai polytropos` merged back with `palai ho theos lalesas...` — the adverb pair alone dangles
- Mark 1:6 merge: `kai en ho Ioannes / endedymenos trichas kamelou` merged — bare `en` without predicate is not a thought

**Contrast with speech-intro (justification 3):** Finite speech-intro formulas (λέγει, εἶπεν + dative) ARE complete speech-act predications — the speech act itself is the content. Bare governors are not; they await content. Note: εἰπών in the M3 examples above is a participial form used as an introductory frame *without* dative or content — it dangle-awaits content. εἶπεν (finite) + dative is a complete speech act and falls under justification 3 / R11, not M3.

#### M4. Fragmented Atomic Thought-Unit

**Definition:** If splitting a line would produce fragments that individually fail the atomic-thought test, merge. This is the inverse of the cognitive prong: the cognitive prong requires each resulting chunk to be its own atomic thought for split to proceed; if any resulting fragment fails that test, the split is blocked.

**Test:** Read each proposed resulting line aloud as a standalone unit. Does it constitute one focused-attention chunk with bounded information? If any resulting line fails, the split is over-fragmenting.

**Canonical cases:**
- Trailing adverbial modifiers orphaned from their predicate: `..., hoti X / ennou pheradoteros Y` — the trailing phrase is not its own idea unit
- Dangling discourse particles: `alla` alone on a line without a complete clause
- Orphaned appositives separated from their head noun when the appositive alone has no independent image

**This is the adversarial auditor's primary over-split detection rule.** Most reversals (Rom 1:29, Luke 14:21, Phil 4:8, 2 Pet 2:10) trigger M4 alongside M1 or M3.

### The Complete Framework

Putting Section 2 and the merge-overrides together, the full decision procedure is:

1. **Default:** merge (predication test — members sharing one predicate and not independently atomic stay on one line).
2. **Split-trigger** (= any of justifications 1–4 firing): if BOTH the structural prong (one of justifications 1–4) AND the cognitive prong (atomic thought-unit) pass, the line splits.
3. **Merge-override:** even when a split-trigger applies, if any merge-override (M1–M4) fires, the line returns to merged state. **When split-trigger and merge-override both fire on the same line, merge-override wins** — the merge-override list is the mechanism that prevents split-triggers from producing non-atomic or bonded-pair fragments. Note: M4 is the cognitive prong restated as a merge condition — step 2 requires the cognitive prong to pass for a split to proceed; M4 blocks a split when any resulting fragment fails that same test. They are the same test viewed from opposite directions; there is no logical gap between them.
4. **Textual asymmetry override (R28):** where the author has chosen asymmetric treatment of parallel passages, preserve the author's structure regardless of editorial symmetry preferences. R28 operates at the split-trigger level — when the author's finite-verb count or structural choice differs between parallel passages, R28 blocks importing the richer passage's structure onto the sparser one, even when formal markers on the sparser side would otherwise trigger justification 1.

The framework is a default-merge with two closed lists of exceptions — five split-triggers and four merge-overrides — plus a meta-principle (R28) governing cases where authorial and editorial symmetry conflict.

---

## Section 3: The Rules

*Purpose: **mainly operational** — rule reference Claude reads literally for editorial application. Read for the Autonomy Boundary (Category A/B/C + scope/precedence/closed-list/carve-out diagnostic), Rule Index, and individual rule subsections (§3.1 through §3.17).*

### Autonomy Boundary (Read This First)

When proposing sense-line changes, classify each change:

- **Category A — Editorial slippage:** suboptimal break, no theological or rhetorical stakes. Apply confidently.
- **Category B — Rhetorical shape:** changing the break changes how the speaker builds an argument. Flag and ask Stan before applying.
- **Category C — Theological weight:** break placement makes a doctrinal point. Flag and discuss with Stan before touching.

**Default:** When you cannot confidently assign Category A, treat it as Category B and flag for Stan. The cost of a false Category A (applying a change Stan would have wanted to discuss) is higher than the cost of a false Category B (flagging something that turns out to be straightforward).

**Mechanical-rule authority.** When a rule classified as MECHANICAL fires unambiguously on a passage — all conditions satisfied, no heuristic ambiguity — the change is **Category A by default**. The rule itself is the approval; per-item flagging is not required and wastes both sides' time. Bump to Category B only when theological, rhetorical, or textual-critical weight is independently implicated (e.g., classic exegetical hot spots like John 1:3-4, Rom 9:5, Eph 1:4-5). Editorial rules and fuzzy rules remain Category B/C as stated.

**Proposed-rule adoption protocol.** A proposed rule is adopted when its first corpus sweep produces ≥80% clean categorization (unambiguous STRONG-MERGE or STRONG-SPLIT). Apply the clean categorizations; refine the rule for the ambiguous residue and re-run. If ≥80% cannot be reached after two refinement passes, the rule is likely editorial rather than mechanical — reclassify and gate per Category B/C.

**Scope/precedence/closed-list/carve-out diagnostic.** Canon additions that include ANY of the following are **Category B by default**, regardless of how they are framed in the commit message or §10 Update Log entry:
- A scope claim (*"rule X applies to / does not apply to Y"*)
- A precedence claim (*"rule A trumps rule B"*, *"X wins over Y when both fire"*)
- A closed-list extension (adding a verb class, adding a named category, adding a SCOPE-exclusion item)
- A named-category carve-out (introducing a new gating category, even if cross-referenced to an existing rule)

This diagnostic catches the failure mode where a canon change is self-framed as "documenting existing practice" or "scope clarification" but substantively asserts a new judgment. §6.5 "Mandatory-audit triggers for canon changes" operationalizes this diagnostic for commit-time discipline.

**Greek-specific instances:**
- **Category A:** A dangling article (ton at line end) or a verb split from its direct object — mechanical error, fix confidently.
- **Category B:** Phil 2:6-8 kenosis hymn — whether thanatou de staurou gets its own line or stays with the preceding line changes how the descent structure reads.
- **Category C:** Rom 9:5 — whether ho on epi panton theos eulogetos attaches to ho Christos (Christological reading) or begins a new doxology (theistic reading). Break placement is a doctrinal decision.

### Rule Index

| Rule | Name | Type | Section |
|------|------|------|---------|
| R1 | No-anchor rule | Mechanical | 3.1 |
| R2 | Never dangle a conjunction | Layer 1 | Layer 1 table |
| R3 | Never end on article | Layer 1 | Layer 1 table |
| R4 | Never split negation from negated | Layer 1 | Layer 1 table |
| R5 | Never split periphrastic construction | Layer 1 | Layer 1 table |
| R6 | Fixed phrases stay together | Layer 1 | Layer 1 table |
| R7 | Vocative units indivisible | Layer 1 | Layer 1 table |
| R8 | Framing devices attach | Mechanical | 3.3 |
| R9 | Subordinate clause introduction breaks | Mechanical | 3.4 |
| R10 | Complementizer hoti — cognition vs. speech | Mechanical | 3.5 |
| R11 | Direct speech introduction | Mechanical | 3.6 |
| R12 | Parallel stacking (if atomic) | Editorial | 3.7 |
| R13 | Correlative pair treatment | Editorial | 3.7 |
| R14 | Men/de contrast stacking | Editorial | 3.7 |
| R17 | De-contrast overbreak | Mechanical | 3.8 |
| R18 | Vocative rule (three-way refined) | Editorial | 3.9 |
| R19 | Genitive absolute always own line | Mechanical | 3.10 |
| R20 | Participial phrase test (refined) | Editorial | 3.10 |
| R22 | Orphaned adverbial completion | Editorial | 3.11 |
| R23 | Dative subject of infinitive | Mechanical | 3.12 |
| R24 | Qualifying phrases: escalation vs. restriction | Editorial | 3.13 |
| R27 | Authorial style principle (uniform criteria) | Principle | 3.15 |
| R28 | Textual asymmetry overrides editorial symmetry | Principle | 3.7 |

*Retired (see §9):* R15 (folded into R14), R16 (folded into R8), R21 (absorbed as operational mechanism for R12/R13/R14), R25 (folded into R11), R26 (pure restatement of M2), R29 (pointer-only; M1–M4 stand on their own in Section 2).

Rules are classified as MECHANICAL (any trained editor would apply them identically), EDITORIAL (defensible, documented, but require judgment), PRINCIPLE (governing stance, not a per-line rule), or LAYER 1 (pure Koine-Greek syntax facts at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md); Mechanical in effect, but their warrant is generic Greek grammar rather than a project-specific editorial choice).

### 3.1 The No-Anchor Rule

Every sense-line must carry at least one thought-marking anchor: (1) a finite verb, (2) an infinitive, (3) a participle standing as predicate, or (4) a substantive head that is the independently predicated topic of its own line.

*Serves:* the generative force (atomic thought / propositions) — this rule operationalizes the DEFAULT case of the generative force (the predication test).

**Participle scope.** Anchor type (3) is "a participle standing as predicate" — not any participle. A participle functioning as an adverbial modifier or attributive adjective does not anchor its line; only a participle standing as the predicate of its own clause (genitive absolute, circumstantial participle carrying an independent predication via ellipsis) counts.

**Critical clarification:** A "substantive head" does NOT include bare noun phrases that continue a prior clause's predicate as list objects or appositional extensions. A line of objects from the previous line's verb fails the anchor test even though it contains nouns.

**Exemptions:**
1. Single-line verses — atomic by definition.
2. Speech-intro prefixes ending with ano teleia (kai palin:, kai eipen:) — the punctuation marks a new discourse layer.
3. Standalone sentence connectives (Hoste, Ara oun, Dia touto) — hinge markers that license a merge with the *next* line.
4. Lines that fail the anchor test but pass the two-prong exception test (Section 2) — formally-marked parallel series members, portrait-building accumulations, speech-act announcements, and classical commata may legitimately lack a traditional anchor.

**Object-continuation failure mode:** The most common way a noun-only line slips through is as a compound-list continuation: the previous line establishes a verb, and the following line names additional objects. These look anchored (they have nouns) but are not.

**Corpus status:** 860 no-anchor merges applied across 26 books. Final scan: 0 unanchored lines remaining corpus-wide.

### 3.2 Syntactic Bond Rules — Migrated to Layer 1

*R2–R7 (never dangle conjunction, never end on article, never split negation, never split periphrastic, fixed phrases, vocative indivisibility) are pure Koine-Greek syntax facts — they would be observed by any competent editor of any Koine text, not just this project. They live at the Layer 1 break-legality reference: [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md). Validators read them from there.*

*Rule numbers R2–R7 are preserved in the Rule Index (marked as "Layer 1") to avoid breaking references in prior session notes and scanners. Their effect on editing is unchanged — they are still hard constraints that any line-break edit must respect.*

*Verb-object bond: see M2 in Section 2 — the clause-nucleus merge-override covers this domain.*

### 3.3 Framing Devices Attach

If a construction's function is to frame, introduce, or pivot to what comes next, it should not be severed from what comes next. A frame without its content is an orphan; content without its frame loses its rhetorical context.

| Marker | Function | Example |
|--------|----------|---------|
| **idou** | Deictic/mirative pointer | idou ego apostello ton angelon mou (Mark 1:2) |
| **dio** | Inferential conclusion | dio kai ho theos auton hyperupsosen (Phil 2:9) |
| **oun** | Resumptive/consequential | oun as post-positive, attaches to its clause |
| **nyn de** | Discourse pivot | nyn de choris nomou dikaiosyne theou pephanerootai (Rom 3:21) |
| **alla** | Adversative correction | Already in rules — confirmed as framing device |
| **gar** | Explanatory ground | Already in rules — confirmed as framing device |
| **plen** | Restrictive adversative | plen hoti to pneuma... diamartyretai moi (Acts 20:23) |
| **toigaroun** | Strong inference | toigaroun kai hemeis... trechomen (Heb 12:1) |

These are not merely "break triggers" — they are framing devices whose function is to introduce what follows. Never orphan them at the end of a line; they lead their content.

### 3.4 Subordinate Clause Introduction Breaks

Purpose (hina), result (hoste), causal (hoti, dioti), temporal (hotan, hote), conditional (ei, ean), comparative (kathos), "lest" (mepote) — each introduces a new line:

```
hina blepontes bleposi kai me idosin,
kai akouontes akouosi kai me syniosin,
mepote epistrepsoosin kai aphethe autois.
```

**Adjectival vs. adverbial distinction:** Adjectival subordinate clauses (hopou, hos modifying a noun) merge with their head noun — they describe the thing just mentioned and are not independent thoughts ("fell on rocky ground where it had not much earth" = one image, Mark 4:5). Adverbial subordinate clauses (hote, hina, hoste, hotan) can stand as scene-setters on their own line.

**R22 override:** Short adverbial subordinate clauses (hote/hopou/hos-clauses) that complete the preceding predicate rather than introduce a new scene merge with that predicate, not take their own line. See §3.11 Orphaned Adverbial Completion Rule. The default under R9 is split; R22 is the merge-override for the completing-predicate sub-case.

### 3.5 Complementizer hoti — Cognition vs. Speech Verbs

Not all hoti clauses are created equal. The treatment depends on what verb precedes them.

**Cognition / perception / belief verbs -> MERGE with verb line.**
When hoti follows a verb of knowing, seeing, or believing, the hoti clause is the syntactic object of the verb — the content of what is known/seen/believed. Verb + hoti + clause = one propositional unit, one atomic thought. No line break between them.

Governing verb families: oida, ginosko, horao/eidon/blepo/theoreo, pisteuo, epistamai, nomizo/dokeo, heurisko, **akouo** (hear), **syniemi** (understand).

Test: is the hoti clause the direct object — the thing that is known/believed? Then merge. Period test: `akouei.` / `syniesi.` alone are ungrammatical-feeling — they demand an object. Pass the period test as obligatory-complement verbs; merge.

```
ekeino de ginoskete hoti ei edei ho oikodespotes poia phylake ho kleptes erchetai,
egregoresen an
```
```
kai nyn oida hoti hosa an aitese ton theon
dosei soi ho theos.
```

**Declaration / speech / writing verbs -> SPLIT (verb line stands alone).**
When hoti follows lego, eipon, grapho, martyreo, homologeo, **didasko** (teach), **kerysso** (proclaim), **apangello / katangello / anangello** (announce/declare), **epangellomai** (promise), **prophēteuo** (prophesy), or similar verbs of speaking, writing, teaching, testifying, confessing, or announcing, the verb line stands alone and the hoti + content follows on the next line. The hoti may be recitative (= quotation marks introducing direct speech) or introduce indirect discourse — either way, the convention is the same as the direct speech rule: the declaration act and its content are separate structural units.

**apokrinomai (answer) — speech-intro frame class.** When hoti follows apokrinomai, the verb + hoti functions as a complex speech-intro frame pointing to the quoted answer. Merge verb + hoti onto one line (like the John 3:28 pattern). The quoted answer begins on the next line.

```
kago de soi lego
hoti sy ei Petros,
```
```
Moyses gar graphei
hoti ten dikaiosynen ten ek tou nomou
ho poiesas anthropos zesetai en aute.
```

**Why the two classes differ:** cognition verbs take the hoti clause as an inseparable syntactic object — the clause IS what is known/seen/believed and cannot be detached without losing the proposition. Declaration verbs (speak/write/testify/confess) describe a public attestation act that is grammatically complete in itself — the period test passes (`legei.` / `martyreo.` / `homologei.` are all valid sentences). The hoti content is the substance being declared, but the declaration act is a complete structural unit on its own.

**The period test is decisive for declaration verbs.** Testimony and confession verbs (martyreo, homologeo) were initially classified as cognition-adjacent on the recitative-test argument ("you can't testify quotatively"). That test fails: the right test is whether the verb forms a grammatically complete act without its complement. Declaration verbs do; cognition verbs do not. See worked examples Rom 10:2, Gal 4:15, Col 4:13, Matt 23:31, 1 John 4:14–15, Rom 8:16.

**Exception — hoti + embedded speech verb pointing to a quote.** When the hoti clause contains another speech verb (eipon, elegen) that itself points forward to a quotation rather than asserting propositional content, the whole construction functions as a complex speech-intro frame. Merge the outer verb + hoti + embedded speech verb onto one line; the quote begins the next line. John 3:28 is the canonical case: `autoi hymeis moi martyreite hoti eipon:` ("you yourselves testify for me that I said:") — the hoti clause doesn't assert content; it's middle plumbing pointing to the quotation. Same family as the Heb 1:6 hotan-speech-intro merger.

**Resolution of the verb-identity contradiction:** This rule (R10) SUPERSEDES the earlier negative result on verb-identity rules (recorded in Section 9). That negative result showed that fine-grained verb-class rules *within* each category do not generalize. But the COARSE cognition-vs-declaration distinction IS a valid verb-identity rule. The negative result holds for finer-grained verb-class subdivision; the coarse distinction holds.

### ὅτι Placement Convention — Leads Its Complement

When a ὅτι-clause is split from its governing verb (split applies under R10 for declaration/speech verbs: λέγω, γράφω, μαρτυρέω, ὁμολογέω, διδάσκω, κηρύσσω, ἀπαγγέλλω, etc.), the ὅτι leads the new line — it does not dangle at the end of the preceding line.

Corpus state: **834 leading : 0 trailing** — convention is universal.

Grammatical warrant: ὅτι is a complementizer — its function is to introduce the clause that follows. Placing it at line-end severs it from the clause it governs. Standard Koine grammar (BDF §416, Smyth §2017, Wallace p. 453-461) describes ὅτι as introducing its complement; our placement convention honors that function visually.

**Always:**
```
... λέγουσιν
ὅτι ὁ υἱὸς τοῦ ἀνθρώπου ...
```

**Never:**
```
... λέγουσιν ὅτι
ὁ υἱὸς τοῦ ἀνθρώπου ...
```

This applies only when R10 says the ὅτι-clause splits (declaration/speech verbs). For R10's merge cases (cognition/perception verbs + ὅτι), the complementizer stays on the same line as its governing verb — the leads-vs-trails question doesn't apply.

Same logic applies to the English gloss: `that` leads its complement clause on its own line when the Greek splits.

### 3.6 Direct Speech Introduction

Speech introductions (elegen, eipen, ephe + dative) get their own line. The speech content begins on the next line:

```
kai elegen autois:
Hymin to mysterion dedotai tes basileias tou theou:
```

Imperatives (Akouete, Siopa) also stand alone — they are complete predications (Mark 4:3).

**Special case: amen-prefix speech-intro formula** — ἀμήν [ἀμήν] λέγω σοι/ὑμῖν is treated as a distinct class. See the "Amen-formula speech-intro" subsection below.

**Exception: synonymous-doublet imperatives stay together.** When two imperatives are uttered as a single rebuke with one breath — where the second is not a distinct action but an intensifying restatement — they merge onto one line. Mark 4:39 `Siopa, pephimoso.` ("Be silent, be muzzled!") is the canonical example. Test: if the second imperative is a synonym or intensifier with no new content, merge. If it commands a distinct action, split.

**Speech-intro frame aggregation.** The speech-introducing apparatus is one complete speech-act predication and may include a preceding qualifying temporal or conditional clause. When the qualifier (ὅταν, ὅτε, ἐάν + finite/participial content) is the *direct qualifying condition* of the speech-intro verb (not an independent scene-setter), the entire frame merges onto one line; the quote follows on the next line. Canonical: Heb 1:6 `hotan de palin eisagagage ton prototokon eis ten oikoumenen, legei:` — one speech-intro line, symmetrical with Heb 1:5, 7, 13. Scope boundary: applies only when the temporal/conditional clause directly qualifies the speech-intro verb; if the clause introduces a new narrative scene independently, the standard R9 subordinate-clause break applies.

### OT-Attribution Tags Inside Quotation Blocks (merge, not speech-intro)

When a speech verb (λέγει, φησίν, λέγει τὸ πνεῦμα, λέγει κύριος) appears INSIDE an already-opened quotation block — attributing the quoted content to its speaker mid-quote rather than opening a new speech event — it is NOT a speech-introduction under R11. It stays merged with the surrounding quoted content.

Detection:
- A speech-intro line (ending in ano teleia `·` or colon `:`) immediately precedes the current line
- The current line contains a speech verb in a non-opening position (post-first-word, flanked by commas, or appearing after content)
- The current line's content is continuation of the already-opened quote

Canonical cases:
- **Revelation 2-3 letters** — `λέγει τὸ πνεῦμα ταῖς ἐκκλησίαις` repeated ×7 in letter-closings. Each is an OT-style attribution tag within a prophetic letter's quoted content, NOT a fresh speech-intro.
- **Pauline OT citations** — Rom 12:19 `λέγει κύριος`, Rom 14:11 `λέγει κύριος`, 1 Cor 14:21 `λέγει κύριος`, 2 Cor 6:17 `λέγει κύριος`, etc. The quoted OT passage already has its speech-intro upstream; the embedded λέγει κύριος is attribution, not intro.
- **Hebrews** — Heb 8:8-9, 8:5 `λέγει κύριος` / `φησίν` inside OT quotation blocks.
- **Acts** — Acts 7:7 `λέγει ὁ θεός`, 7:49 `λέγει κύριος` inside Stephen's quoted-OT narration.

Rationale: these are attribution markers serving the same function as "he said" parenthetically interjected in English dialogue. The canon treats them as continuation of the quoted content, not as re-introducing speech.

### Parenthetical Mid-Speech Attribution (merge, not speech-intro)

When a speech verb — typically `φησίν`, occasionally `λέγει` or `εἶπεν` — appears INSIDE a single-sentence quoted speech as a parenthetical attribution tag (flanked by commas, not opening a new speech event), it stays merged with the surrounding quoted content. This is the same merge-discipline as the OT-attribution case, applied to non-quotation-block contexts.

Detection:
- Speech verb is flanked by commas on both sides (` , φησίν, `)
- The surrounding tokens on the same line are quoted content (imperatives, finite verbs, content words)
- The verb is NOT at line-start position (it's a parenthetical interjection, not a new speech opening)

Canonical cases:
- **Matt 14:8** — `Δός μοι, φησίν, ὧδε ἐπὶ πίνακι τὴν κεφαλὴν Ἰωάννου τοῦ βαπτιστοῦ.` — "'Give me,' she says, 'the head of John the Baptist here on a platter.'" The φησίν is an attribution interjection; splitting it out would mechanize a natural mid-sentence pause and dilute the quoted speech.
- **Acts 25:22** — `Αὔριον, φησίν, ἀκούσῃ αὐτοῦ.` — "'Tomorrow,' he says, 'you will hear him.'"

Rationale: parenthetical attribution is a prose convention, not a new speech event. Treating it as a speech-intro would generate three-line micro-fragments where the original text reads as a single flowing quotation. The attribution verb is the English analogue of the comma-flanked "he said" inside a quotation.

Contrast with R11 genuine violations: a speech-intro that OPENS new speech appears at line-start, immediately followed by an ano teleia (`·`) or colon, then the quoted content on the NEXT line. If the speech verb is mid-line between quoted content, it is NOT a new speech-intro — it is parenthetical attribution.

### Amen-formula speech-intro (own line, content breaks next)

The solemnity-prefixed speech-intro formula **ἀμήν (ἀμήν) λέγω σοι / ὑμῖν** ("truly [truly] I say to you / [to thee]") is an atomic formulaic unit that gets its own line. The content of the saying breaks to the next line.

**Canonical form (single or doubled amen):**
```
ἀμὴν λέγω ὑμῖν,
<content of saying>...
```
```
ἀμὴν ἀμὴν λέγω σοι·
<content of saying>...
```

**Applied 15 times corpus-wide** (commit c51faf8, 2026-04). Matthew/Mark/Luke use single amen; John uses doubled amen. Both forms follow the same structural convention.

**Diagnostic:**
- Line starts with `ἀμήν` (or `ἀμήν ἀμήν`) + `λέγω` + pronoun (σοι / ὑμῖν / etc.)
- Ends with ano teleia, colon, or comma — then the content follows on the next line

**Why this is not a generic R11 case:** R11 says speech-intro verbs stand alone, but a bare `λέγω ὑμῖν` can merge under some contexts (speech-frame aggregation, parenthetical attribution). The amen-prefix makes this formula structurally unambiguous: the solemnity marker + speech-intro verb + addressee is a complete formulaic unit. Applying R11 without the amen-prefix recognition can leave the formula mid-line-joined with its content.

**Exception: repeated-vocative address `Κύριε κύριε`** (Matt 7:21-22, Luke 6:46) stays merged as a single speech act per §3.9 (repeated vocatives as rhetorical unit). Not governed by this rule.

**Test contrasts:**
- `ἀμὴν λέγω ὑμῖν, ...` — formula + content → two lines ✓
- `Κύριε κύριε, οὐ τῷ σῷ ὀνόματι ...` — repeated vocative → one line per §3.9 ✗ (not this rule)

### 3.7 Parallel Structures and Stacking

**Parallel stacking rule.** When the author builds parallel structures, stack them vertically to make the rhetoric visible:

```
kai hai merimnai tou aionos
kai he apate tou ploutou
kai hai peri ta loipa epithymiai
eisporeuomenai sympnigousin ton logon,
```

**But: stack only when each element is independently atomic.** If stacking a parallel produces fragment lines (subject without verb, verb without complement), merge the stack into atomic-thought-sized units even if the rhetorical mirror is lost. Atomicity overrides parallelism.

**The ellipsis principle.** An elided (gapped) verb is a real predication for colometric purposes. When a verb appears once and is implied for subsequent members of a parallel structure, each member is a complete atomic thought with a recoverable verb. This applies to triadic object lists, triadic subject lists, growth stage lists, and any parallel structure where the verb is expressed once and implied for subsequent members.

**When NOT to stack:** Multiple objects of a single verb do NOT stack — they are one thought, not separate predications. "They offered gifts: gold and frankincense and myrrh" (Matt 2:11) is one offering of three things, not three separate offerings. The test: can each member be reconstructed as an independent predication by supplying the verb? If yes, stack. If they are all objects/complements of one verb, keep together.

**Correlative pairs (eite/eite, oute/oute, mete/mete).** The stacking rule depends on whether each member is a distinct proposition or a qualifying phrase.

- **Correlative members with distinct predicates -> stack each on its own line.** Each member is a complete predication.
- **Correlative members sharing a single predicate -> one proposition -> stay.** When all members feed into one shared verb, the correlatives are distributing subjects/objects/qualifiers over a single predication.
- **Correlative phrases (prepositional, nominal, participial) modifying a head -> may stay together.** These are not independent predications; they distribute a single head across alternatives. `legomenoi theoi eite en ourano eite epi ges` (1 Cor 8:5).

**Men/de contrast stacking.** Greek's built-in contrast structure becomes spatially visible:

```
hoi men echleuazon
hoi de eipan:
```

**Me/alla and ou/alla antithesis.** Paul's signature corrective rhetoric — "not X but Y" — uses negation + alla to set up an explicit contrast. This is a standard colometric break point: alla introduces the corrective positive on its own line.

```
me hyperphronein par' ho dei phronein,
alla phronein eis to sophronein,
```
(Rom 12:3)

**Semantic grouping principle for compound lists.** Compound lists united by ONE verb or ONE preposition stay merged UNLESS a grammatical signal breaks them:
1. Elided auxiliary — each member would require its own finite verb
2. Possessive restart — re-opens a possessive domain
3. Demonstrative / article restart
4. Aspect or tense shift — different temporal planes across members

**Paradox pairs.** Antithetical pairs that form a single paradox merge onto one line: "seeing they may see and not perceive" is one thought — the paradox is the unit, not its halves (Mark 4:12, Isaiah quotation).

**Textual asymmetry overrides editorial symmetry.** When a passage has a positive/negative counterpart pair and the author uses a different structure in one than the other, preserve the author's asymmetry — do not reshape the text to force editorial parallelism.

Canonical case: Matt 25:35–36 (positive) splits each condition into its own line with its own finite verb (`epeinasa gar kai edokate moi phagein, / edipsesa kai epotisate me, / ... / esthenesa kai epeskepsasthe me, / en phylake emen kai elthate pros me.`). Matt 25:43 (negative) uses ONE verb `ouk epeskepsasthe me` to cover both `asthenes` and `en phylake`, then introduces the unmerciful action differently. The negative version's line structure reflects the Greek's single-verb treatment — splitting it to mirror the positive would require inventing predication the text does not supply.

Test: is the structural difference between parallel passages authorial (one uses N verbs, the other M≠N) or editorial (we split one and not the other for no text-grounded reason)? Authorial asymmetry is preserved. Editorial asymmetry is a parallelism-consistency drift and should be fixed. The distinction: count the finite verbs, elided verbs, and distinct predicative heads in each passage. If they differ between positive and negative, the asymmetry is the author's and the lines should reflect it. If they don't differ, editorial treatment should converge.

This is a specific instance of the broader principle that **the text is authoritative over the methodology's aesthetic preferences.** Where the author chose asymmetry, we preserve it; where the editor imposed asymmetry, we normalize it. See also "The Complete Framework" (Section 2, step 4) for how R28 operates at the split-trigger level within the full decision procedure.

*Three §3.7 subsections (Need/Response Paired Beats, Imperative + Divine-Consequence, Cause-Consequence Bonded Beats) retired 2026-04-25 — see §9 Superseded Formulations.*

### 3.8 De-Contrast Overbreak

(General discourse-marker treatment lives in R8's framing-devices table in §3.3 — γάρ, ἀλλά, πλήν, οὐδέ, μηδέ, etc. all lead their content per R8. §3.8 is reserved for the one discourse-marker pattern that needs its own diagnostic: the δέ pivot.)

**De-contrast overbreak rule.** When two distinct clauses with a de pivot appear on one line — a comma before `ho de / he de / to de / hoi de / meson de / nyni de` — split at the de. The comma marks the clause boundary; the de signals a contrast or topic shift.

**Canonical example:**
```
Hai alopekes pholeuous echousin
kai ta peteina tou ouranou kataskeenoseis,
ho de huios tou anthropou ouk echei pou ten kephalen kline.
```
(Matt 8:20)

**False positives to rule out:**
- Participial de (no new finite verb after the de)
- Intensifying `malista de` (adds emphasis, not a new clause)
- Appositional `thanatou de staurou` (emphatic specification, not a clause boundary)

Test: is there a finite verb in the clause following de? If yes -> split. If the de introduces only a nominal or participial phrase without its own finite verb -> likely false positive, leave merged.

*27 confirmed splits applied corpus-wide.*

### 3.9 Vocative Rule (Refined Three-Way Treatment)

**Default: vocatives get their own line** when they initiate or resume direct address. A vocative at the start of a verse or after a speech-introducing boundary is opening a camera-angle turn — the speaker is now turning toward an addressee — and earns its own line as a complete address act.

**Apposition exception: a vocative merges into the preceding line when it is grammatically appositive to an already-established second-person address in the same clause.** The grammatical signature: somewhere in the preceding line(s) of the same verse, *not separated from the vocative by a speech-introducing boundary* (ano teleia or colon), there is either a second-person pronoun (any form of sy / hymeis) or a second-person finite verb.

Two justifications, not one:

1. **Subject-appositive rule** — when the vocative names the implicit subject of a 2p finite verb (`Hypage, Satana`, `Agnoeite, adelphoi`, `Tharsei, teknon`, `Ouai hymin, grammateis kai Pharisaioi hypokritai`). The verb and vocative form *one atomic predication*.
2. **Object-appositive rule** — when the vocative restates an explicit 2p pronoun already in the clause (`Parakalo hymas, adelphoi`, `Gnorizo hymin, adelphoi`). The address is already established; the vocative is affective restatement.

**Verb person is irrelevant.** The triggering condition is the 2p *pronoun*, not the person of the main verb. `Akoloutheso soi, kyrie:` (Luke 9:61) — kyrie merges because it is object-appositive to soi, regardless of akoloutheso being first person. Contrast Acts 9:10 `Idou ego, / kyrie.` (correctly split: ego is 1p, kyrie is not appositive to any 2p element).

**Boundary cases that stay on their own line:**
- **Verse-initial vocative** — initiating a new address turn, no preceding grammar to lean on.
- **Verse-final vocative** — tail address, distinct act.
- **Vocative after speech-intro punctuation** — the prior 2p markers belong to the outer layer, not the inner address.
- **Stacked parallel vocatives** — treated as a parallel address structure (pateres / neaniskoi / paidia in 1 John 2:12-14).

**Discourse-frame + vocative cluster rule.** When a sentence-initial discourse marker (Loipon, To loipon, Loipon oun, Tauta de, Kago, etc.) co-occurs with a vocative, *both* are extra-clausal elements and cluster on one line; the proposition follows on the next line. Canonical example: `Loipon, adelphoi, / stekete en kyrio.` (Phil 4:1 pattern). The vocative still earns its line; it earns *that* line together with the frame particle.

**Repeated vocatives as a rhetorical unit still stay together.** `Kyrie kyrie` (Matt 7:21-22) is one speech act.

*125 vocative merges landed across 21 books.*

### 3.10 Participial Phrases and Genitive Absolutes

**Genitive absolutes are grammatically independent and ALWAYS get their own line.** A gen abs has its own subject (in genitive) and its own predicate (a genitive participle) — the literal meaning of "absolute" is "set apart" from the main clause. It functions as an interjectory frame: a camera shift, a scene-setter, an aside. Merging a gen abs into adjacent material absorbs an independent beat into something it is not. See Acts 1:9 showcase in Section 1.

**Default rule for circumstantial participles: merge with their main verb.** The default function of a Greek circumstantial participle is adverbial framing — temporal, causal, concessive, conditional, manner. All of these are DEPENDENT: they frame the main verb's action and are not complete thoughts without it.

**Exception — circumstantial participle with independent semantic weight:** A participial phrase earns its own line when it constitutes a **second predication** — that is, when the main verb can be implicitly repeated to reconstruct the participle as an independent thought. (Note: standard grammars reserve "supplementary participle" for participles completing specific verbs like τυγχάνω, λανθάνω, φθάνω, παύω per Smyth §2094-96 and Wallace §645-47. Our usage is broader — any circumstantial participle that constitutes an independent predication via ellipsis of the main verb.)

**The test:** Can you reconstruct the participle as an independent predication by supplying the main verb? If "the angel appeared" is complete thought 1, then "[the angel appeared] standing at the right of the altar" is complete thought 2 via ellipsis. Split. But if "having seen the star" requires "they rejoiced" to become a thought at all — if there's no implicit repeated verb — it's a dependent frame. Merge.

**Split examples (supplementary predication):**
- Luke 1:11: `ophthe de auto angelos kyriou / hestos ek dexion tou thysiasteriou` — "an angel appeared" / "[appeared] standing at the right." **Split.**
- Mark 4:38: `kai autos en en te prymne / epi to proskephalaion katheudon` — "he was in the stern" / "[was] sleeping on the cushion." **Split.**

**Merge examples (dependent frame):**
- Matt 2:10: `idontes de ton astera echaresan charan megalen sphodra` — "having seen the star" is causal framing for "they rejoiced." **Merge.**
- Luke 1:19: `Ego eimi Gabriel ho parestekos enopion tou theou` — attributive participle as title. **Merge.**

**Periphrastic constructions** (en + participle, mello + infinitive, archomai + infinitive) are always one verbal unit — never split.

**Periphrastic with elided auxiliary (Acts 8:28 showcase):** When a periphrastic chain extends across multiple imperfective actions sharing one auxiliary, the auxiliary can be elided for subsequent elements. Each "ellipsized periphrastic" is a complete predication via ellipsis and stacks as its own line:
```
en te hypostrephon              <- explicit periphrastic ("he was returning")
kai kathemenos epi tou harmatos autou   <- elliptical periphrastic ([en] sitting)
kai aneginosken ton propheten Esaian.   <- imperfect equivalent, stacks as parallel
```

### 3.11 Orphaned Adverbial Completion Rule

**When a short hopou / hote / hos clause completes the preceding predicate rather than introducing a new semantic layer, it merges with that predicate.** The distinguishing criterion: does the clause specify or complete the main verb's meaning? -> merge. Does it introduce a new thought layer? -> split.

- **Merge**: `akoloutheso soi hopou ean aperche.` (Matt 8:19) — hopou clause specifies the destination. `erchetai hora hote...` (John 9:4, 16:25) — hote clause specifies which hour.
- **Split**: purpose clauses (hina), result clauses (hoste), causal clauses (hoti / gar / dioti) — these introduce new semantic layers.

*15 merges applied corpus-wide.*

### 3.12 Dative Indirect Object as Semantic Subject of Infinitive

When a Greek speech or command verb (λέγω, παραγγέλλω, παρακαλέω, κελεύω, etc.) takes a dative indirect object that is ALSO the semantic subject of an infinitive complement, the dative chunks with the infinitive content, not with the speech verb frame. (Note: standard Greek grammar reserves "subject of the infinitive" for the accusative case per BDF §392, Wallace §195. The dative here is grammatically an indirect object that happens to be coreferential with the understood subject of the infinitive — but for colometric purposes, it belongs with the infinitive content it semantically controls.)

```
Lego gar dia tes charitos tes dotheises moi
panti to onti en hymin me hyperphronein par' ho dei phronein,
```
(Rom 12:3 — `panti to onti en hymin` belongs with `me hyperphronein` because it is the subject of the infinitive, not just an addressee.)

This is the colometric analogue of accusative-subject-of-infinitive constructions in indirect discourse. The dative functions as the semantic agent of the infinitive even though it is grammatically an indirect object — for line-break purposes, it belongs with the content it controls, not with the speech frame.

### 3.13 Qualifying Phrases: Escalation vs. Restriction

**Restriction (merge):** Phrases introduced by ei me, plen, ektos, monon that limit the scope of the preceding statement:
- `panta moi exestin all' ou panta sympherein` (1 Cor 6:12) — the restriction completes the thought on one line.

**Escalation (break):** Phrases that push the preceding claim to its limit, often with ei me + extreme case, or a comparative/superlative intensifier:
- Phil 2:7-8 — each step is an escalation: death, then *crucifixion-death*. The `thanatou de staurou` escalation earns its own line.
- `hyper ek perissou hon aitoumetha e nooumen` (Eph 3:20) — the escalation beyond asking or imagining.

**Test:** Does the qualifying phrase narrow the scope (restriction -> merge) or intensify the claim (escalation -> break)?

### 3.15 Authorial Style Principle

The same colometric framework applies uniformly to all NT authors. Do not adjust thresholds, rules, or sensitivity by author or genre. Let the colometric output reveal authorial differences rather than encoding assumptions about them.

Mark's paratactic short lines and Paul's periodic long lines both emerge from applying the same criteria consistently. The difference in output IS the finding — it reflects genuine compositional differences between authors, not editorial preferences about how each author "should" look.

**Corollary:** Colon-length distributions, FEF density, average words per line, and other quantitative measures derived from the colometric output are valid for stylometric analysis precisely because the criteria are uniform. If we adjusted thresholds for Paul, the Paul-specific measurements would reflect our adjustments, not Paul's style.

### 3.16 Container-Not-Originator and the Subordinating vs. Coordinating Distinction

**Container-not-originator applies to SUBORDINATING syntax only. It does NOT apply to COORDINATING or PARALLEL syntax. Parallel members are each their own atomic thought.**

| Syntax type | Example | Rule |
|---|---|---|
| **Subordinating** (modifier->head) | `eis to oros` tail on `anechoresen`; circumstantial ptc framing a main verb; single attributive gen. | Keep merged with originating head. |
| **Coordinating / parallel** | te/kai chains at different temporal planes; men/de pairs; tri-cola; asyndetic catalogs; anaphoric lists; tis/tis/tis isocola. | **Split** — each member is its own atomic thought. |

**The diagnostic test:** When in doubt, ask: does the construction describe **elaboration of one event** (-> merge) or **addition of distinct events/axes** (-> split)?

A strong signal that coordination is at work: **aspect or tense shift across members.** Heb 1:3 has a present participle (sustaining), an aorist participle (purifying), and a finite indicative (enthroning) — three actions at three temporal planes. This is coordination of events, not elaboration of one event. Split into a tri-colon.

### 3.17 Cross-Verse Continuity Merge

**When a single atomic thought crosses a Stephanus 1551 verse boundary, the sense-line stays intact.** The verse boundary is an editorial overlay (imposed 1551 on a text that already had its own rhetorical structure); it does not constrain sense-line formation. The sense-line is formed by grammatical/rhetorical continuity, and the versification is carried along by an inline superscript marker.

**Canonical example — Matt 3:1-2:**

```
3:1
Ἐν δὲ ταῖς ἡμέραις ἐκείναις παραγίνεται Ἰωάννης ὁ βαπτιστὴς
κηρύσσων ἐν τῇ ἐρήμῳ τῆς Ἰουδαίας ²καὶ λέγων·

3:2
Μετανοεῖτε,
```

The speech-intro `κηρύσσων ... καὶ λέγων·` is one atomic thought (a preaching-speech-intro bond). SBLGNT places `καὶ λέγων·` at the start of 3:2. The sense-line rule keeps `κηρύσσων ... καὶ λέγων·` as one breath unit; the `²` superscript preserves the versification reference.

**Procedure (per `handoffs/04-editorial-workflow.md`):**

1. **Identify the boundary** — grammatical continuity indicator (participle chain, suspended main verb, subject/verb straddle, speech-intro straddle, discourse-adverb leading the next clause, etc.).
2. **Merge in place** — the sense-line lives in the *earlier* verse's block (where its lead word sits), with the content that SBLGNT attributes to the later verse attached inline after a superscript digit (`²`/`³`/`⁴`/...) indicating where the later verse begins visually.
3. **Mirror in English** — the same merge, the same superscript position.
4. **Cite using the earlier verse's reference** when referring to the merged colometric line.

**Both directions apply.** The Matt 3:1-2 case has SBLGNT pushing a word *forward* into the next verse (`καὶ λέγων·` is SBLGNT-3:2 but sense-line-3:1). The John 4:35-36 case has the opposite: SBLGNT assigns `ἤδη` to the end of 4:35, but R8 makes `ἤδη` the lead of the clause in 4:36 (`ἤδη ὁ θερίζων μισθὸν λαμβάνει`). Same convention applies — keep the sense-line intact (in the earlier verse's block, where `ἤδη` sits), mark the versification boundary with a `³⁶` superscript before the post-boundary content:

```
4:35
...
ὅτι λευκαί εἰσιν πρὸς θερισμόν·
ἤδη ³⁶ὁ θερίζων μισθὸν λαμβάνει

4:36
καὶ συνάγει καρπὸν εἰς ζωὴν αἰώνιον,
ἵνα ὁ σπείρων ὁμοῦ χαίρῃ καὶ ὁ θερίζων.
```

**Precedent:** This mirrors the Nestle-Aland typographic convention for inline verse numbering, ported down to the colometric-line level. NA28 renders `καὶ λέγων·` inline in its flowing Greek with a superscript `²` marking the verse-boundary; we follow the same surface convention and add the colometric justification.

**Infrastructure:** `scripts/verify_word_order.py` recognizes these markers and splits a merged line at each superscript digit for per-verse word-order integrity comparison against SBLGNT. `scripts/build_books.py` renders superscripts as `<sup class="verse-marker">` HTML anchors so citation lookups still land at the exact inline location. A reader searching for "Matt 3:2" still finds `Μετανοεῖτε,` at the top of the 3:2 block; the superscript in 3:1's sense-line is an additional anchor for the mid-line boundary.

**Why codify this in the canon?** Versification is not original. Sense-line formation is. When they collide, the rule is clear: sense-line wins, versification becomes a secondary annotation. This principle sits alongside "editorial punctuation is not original; hide in display" (see feedback_no_editorial_overlays_as_signal) and "don't let editorial overlays drive structural decisions" — the general posture of seeing past 1550s editorial conventions to the text's own structure.

---

## Section 4: Operational Tests

*Purpose: **mainly operational** — diagnostic tests Claude runs to gate or sharpen editorial decisions (No-Anchor, Period, Image, Two-Prong, Q1/Q2, Completing-Predication, Validator Work-Queue). Each test has explicit inputs, outputs, and pass/fail criteria.*

These are the diagnostics actually run during editorial work.

### Gold-standard regression-test chapters — why these four

The chapters listed below under Post-Split Function-Word Recheck (Mark 4, Rom 2:12-13, Acts 1:1-4, Heb 1:3) were selected because together they stress every major colometric axis:

- **Mark 4** — parable density + nested subordination + gorgianic pairs (tests M1, R11, §3.7 stacking, and the gen-abs/participle discipline in §3.10)
- **Rom 2:12-13** — Paul's densely-packed νόμος argumentation with prepositional-phrase gauntlets (tests R7 PP-catena merges, R8 framing devices, and R14 coordinate-member splits)
- **Acts 1:1-4** — Lukan complex-participial opening with achri-clause and purpose-infinitive stacking (tests §3.10 participial discipline, periodic-sentence handling, and speech-intro frame aggregation)
- **Heb 1:3** — triadic participle chain with aspect shifts (the §3.16 showcase — tests coordination-vs-elaboration and the aspect-shift split trigger)

Any pipeline change that breaks one of these four is suspect. If a change breaks three or more, it's probably wrong.

### Post-Split Function-Word Recheck (mandatory after any split pass)

**After any mass-split pass (R8, R12, R18, R19, or any rule that produces new line breaks), re-run the dangling-function-word check before committing.** A split can strand preposition-object, article-noun, or negation-verb pairs on either side of the new break. The recheck catches these.

**Why it's mandatory:** every new line break is a potential function-word orphan. The canon's "never split" list (article+noun, preposition+object, negation+verb, noun+genitive modifier, noun+possessive pronoun — see Layer 1 `data/syntax-reference/greek-break-legality.md`) is a forbidden-break set; a split pass can accidentally produce forbidden breaks if the scanner isn't perfectly tuned. The recheck is the safety net.

**After any pipeline change (regen logic, scanner rewrite, validator update), manually diff the four gold-standard regression-test chapters above (Mark 4, Rom 2:12-13, Acts 1:1-4, Heb 1:3) — v4 + eng-gloss, before and after. If any of the four breaks, the pipeline change is suspect.**

### The No-Anchor Test (Default Case of the Generative Force)

**What it checks:** Does every sense-line carry at least one thought-marking anchor (finite verb, infinitive, predicate participle, or independently-predicated substantive head)?

**How to run it:** For each line, look for one of the four anchor types. If none is present, the line is a candidate for merging with its neighbor — but check the two-prong exception test (Section 2) first.

**Updated exemption list:**
1. Single-line verses (atomic by definition)
2. Speech-intro prefixes
3. Standalone sentence connectives
4. Lines passing the two-prong exception test (Section 2)

### The Period Test (Obligatory vs. Optional Complements)

**Scope:** This test applies to **non-R10 verbs only.** All cognition-, perception-, speech-, declaration-, and speech-intro-frame verbs that take ὅτι complements are R10-governed (see §3.5). Run R10 first. If the verb is R10-governed, use R10's merge/split verdict and stop. Only run the Period Test for verbs outside R10's scope (command verbs, desire verbs, causative verbs, demonstration verbs, etc.).

**What it checks:** Is a non-R10 verb's complement obligatory or optional?

**How to run it:** Can you put a period after the verb phrase and have a grammatically complete sentence? If NOT, the complement is obligatory and the break before it is forbidden.

| Greek verb | Complement type | Break before complement? |
|---|---|---|
| **keleuo / entellomai** (command) | **OBLIGATORY** | **No** |
| **thelo / epithymeo / boulomai** (desire) | **OBLIGATORY** | **No** |
| **deiknymi / deloo** (demonstrate) | **OBLIGATORY** | **No** |

R10-governed verbs (lego, eipon, phemi, martyreo, homologeo, didasko, kerysso, apangello, katangello, anangello, epangellomai, propheteuo, apokrinomai, horao, blepo, theoreo, akouo, ginosko, oida, pisteuo, epistamai, nomizo, dokeo, syniemi, heurisko) — see §3.5.

### The Image Test

**What it checks:** Does a line contain one image or two?

**How to run it:** Close your eyes and picture the scene. Does the line make you see ONE thing? If two distinct images, candidate for splitting. If no complete image, candidate for merging.

### The Two-Prong Exception Test

**What it checks:** Should a line that fails the predication test still stand?

**How to run it:** Cross-reference to Section 2. Both prongs must pass:
1. Cognitive: Is this a demonstrable idea unit?
2. Structural: Is there a formal justification (one of the five structural justifications)?

If either fails, merge.

### The Goldilocks Q1/Q2 Diagnostic (Subordinating vs. Coordinating)

**What it checks:** When evaluating a candidate merge, is the syntax subordinating (merge) or coordinating (split)?

**Q1.** Can line N be read as a standalone prosodic predication (with an implicit auxiliary if needed)?
- "having said these things" -> "he had said these things" = YES, standalone
- bare prepositional phrase -> cannot stand alone = NO

**Q2.** Does line N+1 open with a rhetorical pivot, a resumptive subject pronoun, or a parallel conjunction?
- "therefore he went forth" = YES (pivot + resumptive)
- bare finite verb directly picking up the subject = NO

**If Q1=yes AND Q2=yes -> COORDINATING, do NOT merge.**
**If Q1=no OR Q2=no -> SUBORDINATING, merge is correct.**

**Signatures of coordinate syntax (red flags for merge):**
- Resumptive subject pronoun at start of line N+1
- New grammatical subject NP opening line N+1
- "Having/being" + full predicate on line N (stands alone as "was/had")
- Aspect or tense shift between lines

**Signatures of subordinating syntax (green lights for merge):**
- Line N ends in a bare preposition waiting for its object
- Line N ends in a verb missing its direct object
- Line N ends in a speech/cognition verb awaiting content

### The Completing-Predication Test (Class P)

**What it checks:** Is a relative clause completing an identification (merge) or extending with new information (split)?

Ported from a parallel corpus colometric project and confirmed to apply identically in Greek.

**Three diagnostic tests:**

1. **Completing test (primary).** Remove the relative clause. Does the head noun stand alone as an atomic thought? If NO, the relative is completing. Merge.
2. **Paraphrase test.** Can the relative clause be replaced by an adjective? If YES, it is restrictive/identifying. Merge.
3. **New image test.** Does the relative clause paint a new scene beyond identification? If YES, it may be cataphoric and can remain split.

**It-cleft constructions always merge.** "It was X who Y" — the relative clause IS the obligatory predication.

**Greek worked examples:**

- **John 1:3-4 (ho gegonen):** The relative clause hos gegonen stays with v.3. The relative pronoun is governed by the antecedent hen in the preceding negative construction oude hen. Separating it orphans the relative pronoun from its syntactic anchor. Completing test: remove hos gegonen -> oude hen is incomplete. Merge.

- **2 Cor 1:6 (ei ... hyper tes hymon parakleseos tes energoumenes en hypomone ton auton pathematon hon kai hemeis paschomen):** The genitive relative clause hon kai hemeis paschomen identifies which sufferings. Paraphrase test: "the same sufferings" -> "the identical sufferings." Restrictive/identifying. Merge.

### The Validator Work-Queue Convention

Validator output is a **work queue**, not a review queue. Candidates tagged by a mechanical-rule validator as `STRONG-MERGE-CANDIDATE` or `STRONG-SPLIT-CANDIDATE` are application-ready per the governing rule (see Mechanical-Rule Authority in §3). Apply them without per-item flagging.

Only candidates tagged `REVIEW-REQUIRED` / `AMBIG` / `UNCLEAR` actually require per-item editorial judgment. If more than ~10% of a validator's output falls into these flagged categories, the governing rule has a gap worth codifying — refine the rule so the residue shrinks, rather than asking per item.

---

# Part 2: The Framework

*Read when you need depth. Part 2 explains the "why" behind Part 1.*

---

## Section 5: Register Operationalization

*Purpose: **mainly operational** — register-aware modulation layer that sits on top of the base framework. Six registers detected by local syntactic signatures + the FEF (Front-End Frame) treatment for Greek. Read when applying register-sensitive rules in argumentative, sermonic, narrative, or apostrophic contexts.*

The three-forces framework (§1) is **register-flat at the base layer**. But actual practice is register-aware. Register is a **modulation layer that sits on top of the base framework**, detected by local syntactic/lexical signatures rather than by coarse genre tags.

**Register is detected locally, not globally.** A chapter can shift register mid-verse. An argumentative period can contain an enumerative catena; a narrative chain can break into a sermonic indictment. We do not pre-classify whole books into registers; we read the signature of each local span and apply the appropriate modulation.

### The Six Registers

| Register | Local signature | Rule modulation |
|---|---|---|
| **Enumerative (stab-commata)** | Asyndetic or high-kai lists of parallel NPs/PPs with shared governing head; typically 3+ members; each carries independent rhetorical weight | Stack aggressively; each member is its own atomic thought. 2 Cor 6:4-7 (en-catena), 2 Cor 11:23-27 (kindynois octet), Rom 1:29-31 (vice catalog), Gal 5:19-21, Gal 5:22-23. |
| **Gorgianic (pair-bond)** | Coordinate pairs with figura etymologica, sound echoes, rhythmic balance; exactly 2 members; no independent rhetorical weight per member | Tight merging — both stay on one line. `kopo kai mochtho` (2 Cor 11:27), `hagia kai amomo` (Eph 5:27). |
| **Narrative frame-setting (FEF)** | `egeneto de` / `egeneto en to` / kai egeneto chains; temporal, spatial, circumstantial protasis with deferred main clause | Frame-expansion structure: the protasis is held together as one atomic temporal frame even when long; the main clause starts a new line. Luke 3:1-2 paradigm. |
| **Sermonic / indictment / woe-formula** | 2p imperatives stacked; vocatives at paragraph-initial; ouai formulas; rhetorical questions in anaphoric sequence | Tighter breaks; anaphoric stacking of parallel indictment clauses. Matt 23:13-29, Luke 11:42-52, Jude 11-16. |
| **Argumentative / periodic** | gar / hoti / dioti / dia touto / ara / oun causal-consecutive markers; hina and hoste result chains; participial subordinate chains in main-clause matrix | **Longer atomic-thought lines licensed by register.** Rom 1:4-5, Heb 1:1-2 sit here — the long line is register-correct. |
| **Apostrophic** | Vocative density; 2p direct address; emotional appeal; often discourse-initial o or paragraph-initial vocative | Vocative-indivisibility + framing-attach. Each vocative gets its own line; the vocative preserves the appeal as its own discourse gesture. Gal 3:1, 4:19, 1 Cor 15:55. |

**How to read the table.** The first column is a detection rule. The second column is the modulation. No new forces enter; the three forces (§1) govern, but the register changes which force is load-bearing in that local span.

### FEF Framework for Greek

**A Front-End Frame (FEF)** is a structure where a discourse marker or clause-opener suspends resolution until the main verb arrives, and everything between is part of the suspension. The frame is irreducible — no internal break produces a complete thought.

The Greek equivalent of the Hebrew wayehi protasis is the **periodic sentence with participial suspension before the main verb resolves**. Lukan prose is the densest carrier; Pauline embedded subordination produces the same irreducibility.

**Examples:**
- **Luke 3:1-2** — En etei de pentekaidekato tes hegemonias Tiberiou Kaisaros... egeneto rhema theou — a temporal FEF suspending through five genitive absolute phrases before the main verb egeneto lands.
- **Acts 1:1-4** — Ton men proton logon epoiesameen... achri hes hemeras... enteilamenos... parengeilen — periodic sentence with participial chain.
- **Ephesians 1:3-6** — Eulogetos ho theos... ho eulogesas hemas... kathos exelexato hemas... eis to einai hemas... proorisas hemas — Pauline periodic suspension.

**Connection to the egeneto question:** Lukan egeneto + infinitive/hoti constructions are FEFs — the egeneto is a discourse marker (not a semantically heavy verb), and the temporal/circumstantial material between it and the content clause is the frame. Treat as irreducible.

---

## Section 6: Precedent and Scope

*Purpose: **dual-natured** — scholarly grounding (Codex Bezae, Claromontanus, Skousen) and project scope discipline (mainly philosophical) PLUS the operational change-protocol machinery (Defensibility capture, §6.5 Mandatory-audit triggers — operational; Claude reads §6.5 literally before any canon commit).*

### Precedent for colometric layout

We are not inventing a practice; we are recovering one with ancient and modern precedent.

- **Codex Bezae (D 05), 5th c.** — Luke/Acts laid out colometrically; each line a sense unit. Empirical comparison is feasible (current corpus agrees with Bezae at 61.3% with caveat below).
- **Codex Claromontanus (Dp 06), 6th c.** — colometric Paul.
- **Jerome's Latin Vulgate *per cola et commata*, 4th c.** — Jerome's preface to Isaiah explicitly describes laying out the prophetic books "by cola and commas" for ease of reading.
- **Royal Skousen, *The Earliest Text* (2009/2022)** — modern precedent on the Book of Mormon; the trigger for this project's analogical extension to the GNT.

### Bezae as benchmark

Codex Bezae's line breaks reflect a mixture of sense-line decisions and physical layout constraints. The column width (~25-30 characters) means many breaks are forced by writing space. Agreement metrics are meaningful but Bezae is not a colometric gold standard — it is one empirical datum.

### Scope: what this project is NOT

- Not chiasm analysis (downstream rhetorical work our edition enables)
- Not discourse grammar (Runge 2010; Levinsohn 2000 — useful for pragmatics, not colometric)
- Not manuscript comparison (Swanson et al.)
- Not paragraph-level pagination (NA28, UBS5, SBLGNT — we rely on their text; everything about layout is ours)
- Not a test of any particular psycholinguistic or rhetorical-theory framework — we are producing a reading edition; theoretical alignment is a downstream question that a later phase may ask

### Empirical standard for rule adoption

A proposed rule or rule revision is adopted when it produces a more genuine sense-line in the passages it governs — not when it satisfies any theoretical framework. The test:

1. Does applying this rule produce a line that reveals an actual thought-boundary in the text?
2. Is the rule mechanically applicable, or does it require judgment?
3. Does it improve corpus consistency?

Rules that fail (1) — produce imposed or artificial breaks — are rejected regardless of theoretical elegance. Rules that pass (1) but fail (2) are documented as editorial (not mechanical) and gated per §3's Category A/B/C discipline. Rules that pass (1) and (2) but degrade (3) require a revision pass on the adjacent rules or cases that cause the degradation.

**Defensibility capture for new canon additions.** Every new canon subsection or rule revision should include three elements in its codification:
- **WHY** — what problem it solves, what case surfaced it
- **HOW WE KNOW** — the empirical warrant (corpus instances, cross-reference, grammatical test)
- **SCOPE** — where it applies and where it doesn't (test contrasts / non-examples)

Future additions are audited against this checklist — relevant for both day-to-day consistency and for the PhD prospectus where each rule needs to carry its warrant. Retroactive audit of existing canon sections is future work; the requirement is prospective from 2026-04-22.

### Mandatory-audit triggers for canon changes

The "extensible only by worked examples + adversarial validation" requirement on new structural justifications (§2 line 236) and new merge-overrides (§2 line 352) is strengthened here to an explicit mandatory-audit trigger list at commit time. A canon proposal matching any of the following triggers MUST dispatch an adversarial audit (hostile agent or equivalent external skeptical review) and reflect its findings in the commit. Skipping audit on a triggered proposal is a protocol violation.

**Mandatory-audit triggers (12 categories):**

1. **New named rules / sub-clauses / categories** — including precedence cross-references between rules (e.g., "Rule A trumps Rule B at X"). Shape-matches feel-tests, enumerated lists, and subjective carve-outs particularly.
2. **Rule status promotions** — *proposed* → settled. Removes the hedge; stakes increase.
3. **Spot-check-based proposals** — any canon claim resting on less than full-corpus-sweep evidence. Claims like "I checked 30 instances and the pattern is uniform" must be verified by a full-corpus classification before codification.
4. **Reclassification of canon-recorded Category B/C items** — once a verse, rule, or item is recorded as Category B/C in §10 Update Log or a session's pending list, subsequent sessions cannot silently reclassify it under a different rule-framing.
5. **Rule deletions or SCOPE narrowings that retire live applications** — retiring a rule is as high-stakes as adding one; audit prevents discarding legitimate work. See §9 Superseded Formulations for the retirement trail.
6. **Mechanical signature / validator changes under settled rules** — adding a verb class to a closed-list UD signature, refining a UD trigger, or changing validator conditions silently expands or contracts rule coverage.
7. **Corpus sweeps ≥5 instances under a settled rule** — a sweep asserts "the rule fires cleanly here" N times; the collective scope-claim needs audit even when individual instances are Category A.
8. **Canonical example additions to settled rules** — examples shape rule interpretation; a poorly-chosen example silently redefines the rule.
9. **Meta-rule changes to this trigger list itself** — changes to this protocol must be audited.
10. **Discipline-shifting memory file additions** — new `feedback_*.md` or `project_*.md` files that shape how Claude approaches canon work are behaviorally-governing, not just observations; they need the same scrutiny as canon.
11. **Cross-project imports** (BofM ↔ GNT ↔ Tanakh) **or recoveries from retired canon** (§9 Superseded Formulations) — provenance from a sibling project or older version is not validation; the imported claim must have GNT corpus evidence independent of its source.
12. **Corpus-fit verification — post-codification AND post-detection.**
    - **(a) Post-codification.** A new rule, sub-clause, or named pattern is **not "closed" until a corpus-wide goal-fit audit has confirmed (i) all eligible instances conform OR (ii) all residuals are explicitly enumerated** in §10. This extends trigger #3 (spot-check-based proposals) temporally: full-corpus verification is required at codification AND once after, on the live corpus.
    - **(b) Post-detection.** This trigger ALSO fires when Stan-eyeball or any audit surfaces a violation of an **existing** (settled) rule. Application drift accumulates as the corpus changes around long-codified rules. When a violation is detected, schedule a same-rule full-corpus re-sweep within the same session if practical, or as the next session's first task. (Inverse direction from #7, which gates operator-initiated sweeps.)
    - **Audit dimensions to consider:** goal-fit (does corpus implement codified rules), application-consistency on formulaic phrases (καὶ ἐγένετο FEFs, λέγων-introduced speech, ἀπεκρίθη + εἶπεν redundant-speech, μέν/δέ pairing), application-consistency on parallel-list constructions (genealogies, beatitudes, woe-series, conditional pairs — see §9 Superseded Formulations entry on §3.7 retirement + R28 textual asymmetry), self-consistency (cross-references, defensibility triplets), judgment-handoff smuggling (named in `feedback_rhetoric_bandwagon.md`).

**Audit dispatch protocol — parallel by default.** When a proposal triggers multiple audit dimensions (e.g., fake-rule test + full-corpus sweep + scope test), dispatch all in a single message with multiple Agent tool calls. Sequential only when audit A's verdict determines whether audit B should run. Parallelization substantially reduces friction and lowers the effective cost per audit.

**Audit-skippable categories (all must hold for the proposal to bypass audit):**
- Category A mechanical corpus edits per already-codified rules (sweep-scale ≥5 still triggers #7 regardless)
- Typo fixes, cross-reference updates that don't assert precedence, internal formatting cleanups
- Deletions of items already reverted in the same session (audit-trail cleanup)
- Defensibility-capture additions (WHY / HOW WE KNOW / SCOPE) to already-settled rules without changing the rule's scope

**Relationship to the self-consistency audit.** The pre-commit audit triggers above are per-change, before commit. The "≥2 canon codifications → light self-consistency audit before WRAP-UP" trigger in CLAUDE.md is session-rollup, after commits but before wrap. Both mechanisms coexist; neither replaces the other.

**Provenance and rationale.** See §10 Update Log entry 2026-04-24 for the cross-project-import context, the audit dispatched before codification, and the GNT-side risk profile that earned the trigger list its place.

### v4 as methodology application (not hand typing)

A reproducibility distinction that matters for scholarly defensibility:

- **v0–v3** (earlier stages of the text pipeline) are **bit-exactly reproducible** from source. Running the scripts on the source inputs produces byte-identical output.
- **v4-editorial** is **methodologically checkable**, not bit-exactly reproducible. It is where the documented colometric methodology is *applied* through a mix of scan-and-apply tools (scripts), rule-application validators, and case-by-case editorial decisions where the rule set underdetermines. A different editor following the same canon should arrive at largely the same breaks — within the Category B/C bands of legitimate editorial variation.

**Implication:** v4 is not "hand-typed prose formatted nicely". It is the methodology *in operation*. Every line break in v4 either (a) applies a Category A rule mechanically, or (b) reflects a Category B/C editorial call traceable to a canon rule plus a defensibility rationale. The corpus is auditable against the canon; it is not reproducible from the canon alone, because the editorial calls require human (or Claude-with-Stan) judgment.

This matters for:
- **External reviewers** evaluating whether v4 is a "scholarly product" or a "personal annotation" — it is the former, grounded in an articulated methodology.
- **Future Claudes** auditing whether a corpus edit is defensible: trace it to a canon rule + warrant. If it can't be traced, it's a methodology gap (add to canon) or a bug (fix in corpus).
- **The scan-and-apply pattern**: mechanical sweeps ARE methodology application, not overrides of it. The script encodes a Category A rule; running it applies the rule at scale.

---

## Section 7

*Retired 2026-04-20. Scholarly-grounding material (Chafe idea units, Kintsch propositions, Miller/Cowan chunking, Daneman & Carpenter reading spans, dictation hypothesis as methodological frame, Marschall comparison, cognitive-grounding test as binding constraint) archived at `private/01-method/archive/colometry-canon-scholarly-framing-2026-04-20.md`. Section number preserved to avoid breaking references in prior session notes; do not re-use.*

---

## Section 8: Greek-Specific Application

*Purpose: **dual-natured** — Greek-specific operational supplements (verb valency table, participial-rules detail, vocative/adverbial supplements, Standalone Verb Test) interleaved with scholarly material (exegetical hot-spot convergence, stylometry findings, corpus statistics, validation benchmarks) for external-reader defensibility. Operational supplements amend §3 rules; scholarly material is for the publishable artifact.*

### Verb Valency and the "Atomic Thought" Test

A key refinement: a line is a complete thought only if the verbal element's required arguments are present within the line. This is standard linguistic valency theory applied to colometric analysis.

| Verb type | Required arguments | Line complete? |
|---|---|---|
| **Intransitive** | Subject (often implicit) | Yes — e.g., `Metanoesate` ("Repent!") |
| **Transitive without object** | Subject + Object, but object absent | No — e.g., `akousas de` ("having heard" — heard WHAT?) |
| **Transitive with object present** | Subject + Object, both on line | Yes — e.g., `kai tauta eipon` |
| **Passive** (patient = subject) | Subject (as patient) | Yes — e.g., `phylassomenos` |

**Data source:** Macula Greek Lowfat XML encodes syntactic roles (role=s for subject, role=o for object, etc.), providing usage-level transitivity for every verb in every verse.

### Syntactic Clause != Colometric Colon

A central finding validated across 137,554 words of the SBLGNT: syntactic clause boundaries do not reliably correspond to colometric cola.

- **Grammar over-splits.** An article without its noun is meaningless. A preposition without its object is not a thought.
- **Grammar under-splits.** A 200-character Pauline periodic sentence with three participial images is not one breath unit.

The corrective layer — principled rules that merge fragments and split mega-lines — is the methodological contribution.

### Exegetical Hot Spots

Grammar-driven formatting independently produces exegetically significant arrangements in classic textual debates:

**John 1:3-4 (ho gegonen placement).** Colometry keeps ho gegonen with v.3. The relative clause is governed by the antecedent hen. Rule: relative clause attachment + completing-predication test.

**Romans 9:5 (ho on and Christological referent).** ho on connects to ho Christos. The substantival participle functions as an appositional modifier. Rule: participial phrase attachment.

**Ephesians 1:4-5 (en agape attachment).** en agape attaches backward to hagious kai amomous. Rule: participial phrase break at proorisas.

**1 Timothy 3:16 (hymn structure).** Six relative-clause lines in three antithetical pairs. Rule: relative clause break + parallel stacking.

**Philippians 2:6-8 (kenosis descent).** Each step lands on its own line. Rule: participial phrase break + de discourse marker.

**1 Corinthians 15:3-5 (fourfold hoti creedal formula).** Four parallel hoti declarations stack. Rule: subordinating conjunction break + parallel stacking.

**Colossians 1:15-17 (cosmic scope hymn).** The eite quadruple list stacks. Rule: conjunction break + parallel stacking.

The pipeline has no concept of "hymn," "creed," or "Christology." It applies the same rules to every verse. The convergence validates both the method and the traditional analyses.

### Participial Rules (Greek-Specific Detail)

See Section 3.10 for the main rules. Additional detail:

**Participial chain collapse.** When >=2 participles at different temporal planes are collapsed into one line, split them. The paradigm: Heb 1:3 (present participle sustaining, aorist participle purifying, finite indicative enthroning). Cross-gospel convergence: Eucharistic institution narratives (Matt 26:26-27 / Mark 14:22-23), feeding miracle tri-cola (Matt 14:19 / Mark 6:41), vinegar-sponge 5-action collapse (Matt 27:48 / Mark 15:36).

**Prepositional catena absorption.** >=3 stacked prepositional phrases introducing distinct semantic axes earn splitting. 2 Thess 1:7 (four axes), 2 Cor 6:4-7 and 11:23-27 (the famous Pauline peristasis and kindynois catalogs).

**Suspended-subject-without-predicate.** Topicalized nominative head held in suspension while modifier material piles up before the finite verb. Luke 3:1-2's periodic dating chain; John 17:24's pendant-relative nominative; 1 John 1:1-3's 10-line hanging topic chain.

### Vocative Rules (Refined Three-Way Treatment)

See Section 3.9 for the main rules. The three-way treatment:

1. **Default own line:** Verse-initial, paragraph-initial, post-speech-intro vocatives.
2. **Merge (subject-appositive):** Vocative names the implicit subject of a 2p finite verb in the same clause.
3. **Merge (object-appositive):** Vocative restates an explicit 2p pronoun already in the clause.

Mechanical detection: `scripts/scan_vocative_apposition.py` classifies every vocative-only line. `scripts/apply_vocative_merges.py` applies the merges.

### Orphaned Adverbial Completion Rule

See Section 3.11. Greek-specific detail: the merge cases concentrate on hopou/hote/hos clauses of <=6 words that specify the preceding predicate. 15 merges applied corpus-wide.

### De-Contrast Overbreak Rule

See Section 3.8. 27 confirmed splits across 16 books.

### Discourse-Frame + Vocative Cluster Rule

See Section 3.9. Canonical example: `Loipon, adelphoi, / stekete en kyrio.` (Phil 4:1).

### Stylometry Findings

**Per-author voice waveforms.** A parallel corpus colometric project proved that applying one method uniformly produces measurable voice differentiation. The GNT produces the same phenomenon: Mark's paratactic short lines vs. Paul's periodic long lines vs. Luke's frame-heavy style — all from the same criteria.

**Epistolary vs. narrative genre shift.** Acts 1:1-4 (epistolary prologue) produces long periodic lines; v5 onward produces short paratactic lines. The colometric line-length shift makes the genre boundary visible without editorial commentary.

**Hebrews finding.** The compositional-mode question — whether epistolary-register texts (Pauline core) apply differently from literary-register texts (Hebrews, Revelation, Luke-Acts, John's Gospel) — is a candidate meta-modulation above the register layer. Flagged for future empirical testing.

**Frozen divine triads.** Rev formulas (ho on kai ho en kai ho erchomenos, first/last, alpha/omega) are frozen formulas. First/last merged in Rev 1:17-18.

### Corpus Statistics

| Metric | Value |
|--------|-------|
| Total SBLGNT words | 137,554 |
| Total chapters | 260 |
| No-anchor merges (2026-04-12) | 860 |
| Vocative merges (2026-04-12) | 125 across 21 books |
| De-contrast splits (2026-04-15) | 27 across 16 books |
| Orphaned adverbial merges (2026-04-15) | 15 |
| Participial chain / catena splits (2026-04-13) | ~120 applied |
| Bezae agreement (v3) | 61.3% |

### Multi-Tier Comparison Results

| Tier | Agreement with Bezae |
|------|---------------------|
| v1 (pattern-matching) | 59.7% |
| v2 (syntax-tree) | 60.6% |
| v3 (rhetorical + refinement) | 60.7% |
| v3 + session corrections | 61.3% |

Each tier monotonically improves agreement. Notable: Matthew shows v1 closer to Bezae than v2/v3 — simpler pattern-matching approximates scribal practice for Matthew's paratactic narrative.

### Bezae Caveat

Codex Bezae's line breaks reflect a mixture of sense-line decisions and physical layout constraints. The column width (~25-30 characters) means many breaks are forced by writing space. Agreement metrics are meaningful but Bezae cannot be treated as a colometric gold standard without this caveat.

### Standalone Verb Test

Intransitive verbs of motion or state change can stand alone as a complete predication: eperthee (he was taken up), ekaumatisthe (it was scorched), anabainei (it grows up). The subject is implied, no object is required.

Transitive verbs and speech verbs CANNOT stand alone — they need their complement. eipen (he said) without its speech is a fragment. These must stay with their complement or function as a speech introduction followed by content.

### Four-Tier Pipeline

**Tier 1 — Pattern-Matching (v1-colometric).** Script: `auto_colometry.py`. Rule-based surface-text pattern matching. Known limitation: cannot detect participial phrases, genitive absolutes, or clause boundaries not marked by a surface conjunction.

**Tier 2 — Syntax-Tree-Driven (v2-colometric).** Script: `v2_colometry.py` using `macula_clauses.py`. Uses Macula Greek syntax trees (Clear Bible, CC-BY 4.0). Adds participial phrase isolation, genitive absolute identification, clause boundaries in long prose.

**Tier 3 — Rhetorical Pattern Layer (v3-colometric).** Applied on top of v2. Tricolon/bicolon stacking, men/de contrast display, climactic parallelism.

**Tier 4 — Editorial Hand (v4-editorial).** Stan's hand editing. Makes final decisions. All 260 chapters hand-edited.

**Data sources:**
- **Macula Greek** (github.com/Clear-Bible/macula-greek) — SBLGNT syntax trees, CC-BY 4.0
- **MorphGNT** (github.com/morphgnt/sblgnt) — SBLGNT morphological tagging, CC-BY-SA

### Validation Benchmarks

| Benchmark | What it tests | Limitation |
|-----------|---------------|------------|
| **Marschall** | Scholarly colometric analysis of Paul | Limited to 2 Cor 10-13 |
| **Bezae** | Ancient scribal sense-line practice | Physical layout constraints |
| **YLT alignment** | Whether breaks produce coherent English thoughts | YLT sometimes departs from Greek clause order |
| **Hand-crafted tests** | Mark 4, Acts 17 gold standard | Only 2 chapters |

### Note on Editorial Punctuation

Modern editorial punctuation (commas, periods, ano teleia) in the SBLGNT is not original to the text. Colometric rules must never be based on punctuation placement. The original texts were written in scriptio continua. The web reader hides punctuation by default for this reason.

### What We Ignore (Deliberately)

These are later additions that do not reflect authorial intent:
- **Versification** (Stephen Langton, 13th c. / Robert Estienne, 1551)
- **Modern punctuation** (editorial, not original)
- **Pericope divisions** (liturgical, not compositional)
- **Paragraph breaks** (editorial convention in NA28/UBS5)

We preserve verse references for alignment with standard editions, but they do not drive line-breaking decisions.

---

# Part 3: The Record

*These are retained for the reasoning trail. The authoritative formulations are in Part 1. Read this section when you need to understand how a decision evolved, not when you need the current rule.*

---

## Section 9: Superseded Formulations

*Purpose: **mainly historical** — retirement narratives documenting rules and formulations that no longer govern. Read to understand the reasoning trail of canon evolution. Operationally referenced by §6.5 trigger #11 (recoveries from retired canon must be audited).*

### Three §3.7 Subsections Retired (2026-04-25): Need/Response, Imperative + Divine-Consequence, Cause-Consequence Bonded Beats

First retroactive application of the §6.5 mandatory-audit trigger list (codified 2026-04-24 from BofM cross-project import). The three subsections were added 2026-04-21 without a documented full-corpus sweep. Three parallel Opus hostile audits (2026-04-25) found each subsection fails the audit-discipline standard for different reasons. All three retired; canonical cases handled by existing rules.

**Need/Response Paired Beats — OVERFIT + REDUNDANT.** Exhaustive corpus sweep on the diagnostic (state-verb + καί + 2p-response-verb) found ZERO instances outside Matt 25:35-36 / 42-43 — twelve consecutive verses by one author. The "class" was one pericope dressed up as a general principle. Subsumed by M1 + justification 1 + R8 default. Bonus defect: §3.7 Need/Response mandated merge of `ἐπείνασα γὰρ / καὶ οὐκ ἐδώκατέ μοι φαγεῖν` (Matt 25:42) while §R28 textual-asymmetry four lines earlier explicitly defended that split. Direct rule contradiction; resolves cleanly with §3.7 retirement (R28 wins).

**Imperative + Divine-Consequence — FEEL-TEST + OVERFIT + CORPUS-INCONSISTENT.** Full-corpus sweep documented 8 counterexample splits where the rule predicted merge: Matt 7:7 ×3, Acts 16:31, Luke 8:50, Jas 4:7, Jas 4:10, John 21:6, Matt 11:29, Jas 1:5. Actual merge rate ~50%, not the implied uniform behavior. Most damning: rule was codified from Luke 6 + Luke 11 + Jas 4:8 + Luke 10:28 + 1 John 5:16 set without sweeping Matt 7:7 — the exact Q-source parallel of Luke 11:9 — which SPLITS. The audit discipline lapse (failed to check the sibling gospel) is itself a precedent worth remembering. "Divine response" is a feel-test requiring theological judgment; Matt 8:9 (centurion: "Go and he goes") shows identical merge behavior with zero divine agency, demonstrating the merge phenomenon is structural not theological.

**Cause-Consequence Bonded Beats — FEEL-TEST.** The "removal test" (does member 1 lose its reason for being mentioned if member 2 is removed?) is a pericope-level rhetorical judgment that two competent editors apply differently. Applied literally, the test would require merging ~100-300 splits across the corpus (Matt 1:25, 8:15, 9:25, 12:13, Mark 14:72, Luke 24:50, Rev 8:8, Acts 7:57, etc.) — corpus change Stan does not want. The two canonical cases (John 6:49, John 10:12) merge under R8's short-line default + M1 strict-application caveat saying "check other merge protections before flipping to split"; the rule formalized two judgment calls as principle. Bonus defect: cited §3.16 for John 9:15 aspect-shift, but §3.16 is about participle chains (Container-Not-Originator), not finite-verb aspect — cross-reference mis-wired.

**M1 strict-application caveat (line 372) reference list updated**: removed three §3.7 subsection cross-references; added R8 default and R28 textual-asymmetry as the merge-protections that absorb the canonical cases.

**Audit reports archived** at `private/03-sessions/2026-04-24-bofm-discipline-imports/` (full audit text, methodology, file:line citations for every counterexample).

**Live corpus consequence:** none of the canonical merges are disturbed by retirement. Luke 6:37 ×3, Luke 11:9 ×3, Luke 6:38, Luke 10:28, Jas 4:8, 1 John 5:16, John 6:49, John 10:12, Matt 25:35-36 fivefold all stay merged under M1 strict-application caveat + R8 default + R28 (for Matt 25). The retirement is canon parsimony, not corpus revision.

**Open question forwarded (not part of retirement):** the 8 imperative+divine-consequence splits surfaced by the audit + Matt 7:7 vs Luke 11:9 Q-source asymmetry are now flagged as `application_consistency_vs_rule_coverage` candidates for direct editorial judgment — distinguishing genuine authorial asymmetry (preserve under R28; potentially publishable finding) from editorial drift (correct one to match the other).

### Canon Consolidation (2026-04-18): Six Retired Rule Numbers

Adversarial audit convergence (3 Opus agents, three angles: over-structuring, redundancy, mechanical-triggerability) identified six rule numbers as redundant, folded, or pointer-only. Retired in this pass:

- **R15 (me/alla and ou/alla antithesis)** — folded into R14 and the broader Parallel Structures and Stacking framework. Negation + alla is a formally-marked two-member contrast like men/de; the same "independently atomic → stack" logic applies. The prose remains in §3.7 as a sub-principle; it is no longer enumerated as a standalone rule.
- **R16 (explanatory gar break)** — folded into R8's framing-devices table in §3.3. gar was already listed there ("Already in rules — confirmed as framing device"); R16 was a duplicate entry. §3.8 retitled from "Discourse Markers" to "De-Contrast Overbreak" since R17 is its remaining content.
- **R21 (ellipsis principle)** — absorbed as the operational mechanism for R12/R13/R14. The elided-verb-as-real-predication principle is what makes parallel stacking work; it is not a parallel rule but the test that licenses the parallel rules.
- **R25 (temporal-clause speech-intro merger)** — folded into R11 in §3.6 as "speech-intro frame aggregation." Same principle: the complete speech-introducing apparatus is one predication, whether the frame consists of verb+dative alone (R11 original) or includes a preceding qualifying subordinate clause (the Heb 1:6 case formerly called R25).
- **R26 (never split verb from direct object, short)** — deleted. Pure restatement of M2 (verb-object clause-nucleus bond). R26's own text said "M2 is the operational test." Only a cross-reference to M2 remains in §3.2.
- **R29 (merge-override conditions pointer)** — deleted from the Rule Index. It was a table-of-contents entry, not a rule. M1–M4 stand on their own in Section 2.

**Rule count:** 29 → 23 (R1–R29 with R15/R16/R21/R25/R26/R29 gapped). M1–M4 unchanged.

**What this does not change:** no colometric output changes. Every editorial call these retired rules governed is still governed — by the rules that absorbed them. This is canon parsimony, not methodology revision.

**Rule-number gaps preserved** rather than renumbered, to avoid breaking references in session notes, scanners, and prior commits.

### The Negative Result on Verb-Identity Rules

**Date:** 2026-04-13 (from parallel corpus testing).

**Finding:** An exhaustive audit of 131 verb + "that"-complement constructions tested whether verb type alone could predict break-vs-merge behavior. The audit failed decisively: no classification by verb class produces consistent results. What actually governs: (a) formula status (speech introductions break consistently) and (b) length/breath.

**Partial supersession (2026-04-16):** Section 3.5 (R10, hoti complementizer rule) establishes that the COARSE cognition-vs-speech distinction IS a valid verb-identity rule. The negative result holds for finer-grained verb-class subdivision within each category, but the coarse binary is codified. The negative result is retained as a warning against building elaborate verb-class taxonomies.

### The Universal Vocative Rule (Superseded)

**Date:** 2026-04-11.

**Formulation:** "All vocatives get their own line — universal rule."

**Why it changed (2026-04-12):** The apposition exception was discovered: vocatives bound to 2p verbs or pronouns in the same clause are *inside* one atomic thought, not beside it. See Section 3.9 for the current three-way treatment.

### The Earlier Vocative Explorations

The "Vocative Attachment" and "Epistolary vs. Narrative Vocative Distinction" explorations from the Mark 4 and Acts 1 editorial passes were dissolved into the simpler universal + apposition rule during the Luke 1:3 discussion. The Luke 1:3 kratiste Theophile case confirmed that the correct distinction is grammatical (2p binding), not contextual (epistolary vs. narrative).

### The Duplicate Section 6b

**Original document issue:** Two different sections were both labeled section 6b: (a) me/alla and ou/alla antithesis, and (b) dative subject of infinitive. In the restructured document, these are Rule R15 (Section 3.7) and Rule R23 (Section 3.12) respectively.

### Prior Hierarchy Versions

**2026-04-09 (original):** Four criteria listed without hierarchy.

**2026-04-11 (syntax-as-floor):** Syntax (floor) > atomic idea (primary) > new image (strong) > breath (secondary). Same day harmonized to move syntax to position 4.

**2026-04-12 (absolutist):** "Atomic thought wins every collision" — applied without the "unless" mechanism.

**2026-04-16 (current):** "Default + unless." Criterion 1 governs by default; the two-prong exception test provides principled exceptions.

### Idou Three-Type Distinction (Unsettled)

**Adapted from parallel corpus work:** Deictic (pointing), mirative (surprise), logical-connective (discourse pivot). Not yet tested on GNT material. Open questions: does type 3 merge? How does kai idou interact? Does LXX-influenced idou in Luke-Acts differ from Matthean usage?

*Action item:* Test on Matt 1-2, Luke 1-2, Rev 1-3.

### The Goldilocks Three-Phase History

1. **Phase 1 (early v4):** Over-enthusiastic splitting — particles and bare PPs got their own lines.
2. **Phase 2 (session 9):** Over-correction via container-not-originator + no-anchor pass — 900+ merges, some collapsing coordinated parallel members into mega-lines.
3. **Phase 3 (session 10):** The subordinating-vs-coordinating refinement restored the right answer.

### Marschall Posture *(retired 2026-04-20 — archived with other scholarly-framing material)*

### Breath as a Fourth Criterion *(retired 2026-04-20)*

Earlier GNT formulations treated breath (oral-delivery fit) as a fourth criterion alongside atomic thought, single image, and source-language syntax. Retired 2026-04-20 after empirical test across 260 hand-edited chapters found zero cases where breath was the sole deciding factor on any line break. The cognitive-chunking work breath was informally doing is absorbed by structural justification #5 (substantive adjunct as own focus, §2). If a merge produces something unspeakable, the reconsideration finds its warrant in the three forces (propositions / syntax / image) or in justification #5. Full retirement reasoning at §10 Update Log entry "2026-04-20 (later³) — H3: Breath Criterion Retired."

---

## Section 10: Chronological Update Log

*Purpose: **dual-natured** — chronological reasoning trail. Recent entries documenting active-rule provenance are operationally referenced (cross-project import status, audit findings, retirement dates); older entries are historical narrative. When an entry documents an active rule, it is the canonical source for that rule's WHY/HOW WE KNOW/SCOPE.*

*The dated update blocks from the original document, preserved for the session-by-session reasoning trail.*

---

### 2026-04-28 — Cross-project port-back from Tanakh (pure wins)

After completing the architecture-transition sweep (later⁷), Stan asked for a deep-dive comparison vs. the sibling Tanakh-Reader project — looking for opportunities to adopt patterns Tanakh has solved better. Three parallel Sonnet research agents scanned both projects' methodology canons, process discipline, and session-log parallelism profiles. The audit surfaced a small set of pure wins to port back this commit; substantive canon additions (Step 0 Input Filter, N=2 Adjudication Principle naming) and the larger architectural change (hook-automated cascade) are deferred to follow-up audits/sessions.

**Ported this commit:**

- **§6.5 trigger count consistency fix.** Header said "11 categories" but body enumerated 12 (artifact from when trigger #12 was ported from Tanakh on 2026-04-26 / later — see later entry). Header now says "12 categories." Same fix applied to `CLAUDE.md` line 153. Tanakh §7 already says 12; we now match.
- **`CLAUDE.md`: "Parallelize audits by default" promoted from memory to surface text.** Tanakh `CLAUDE.md:232` states this discipline explicitly; ours had it only in `memory/feedback_adversarial.md` and `memory/feedback_parallelize.md`. Memory is invisible to fresh sessions on cold-start; CLAUDE.md is mandatory. Added a paragraph to the pre-commit adversarial-audit discipline section in `CLAUDE.md`.
- **`validators/_shared/` convention adopted.** Tanakh has `validators/_shared/poetic_register.py` as a tested helper module. We had `morphgnt_lookup.py` and `macula_clauses.py` ad-hoc at `scripts/`. Both moved to `validators/_shared/` (with empty `__init__.py`). `validators/common.py` updated to use `from _shared import macula_clauses, morphgnt_lookup` after `sys.path.insert(0, _VALIDATORS_DIR)`. `_REPO_ROOT` resolution in both moved files updated to walk up two levels (was one level when in `scripts/`). Validator baseline-check passes (no regressions); helper imports verified.

**Audit-status for this commit per §6.5:** typo fix (trigger count) + cross-reference update (CLAUDE.md surfacing of memory discipline) + architectural relocation (no canon claim). No new precedence claims, scope claims, closed-list extensions, or carve-outs. **Audit-skippable.**

**Carry-forward (separate commits):**

- **Step 0 — Input Filter** in canon §1 (closed-list addition; needs §6.5 trigger #3 audit before landing).
- **Hook-automated cascade.** Tanakh's pre-commit hook auto-rebuilds derived layers via `refresh_book.py` and stages them atomically. Worth investigating but the architectural decision (auto-stage derived files vs. fail-with-message vs. status-quo manual cascade) needs Stan judgment — unilateral port could surprise the editor.
- **N=2 Adjudication Principle** as a named, generalized principle in §1. We have the substance in M1 tie-breaker language; promoting it to a named principle is methodology work that deserves a dedicated session, not a casual port.

---

### 2026-04-26 (later⁷) — Architecture transition: tier-producer scripts archived

After the later⁶ residue-purge commit, Stan asked whether the three vestigial scripts flagged as carry-forward (`diagnostic_scanner.py`, `v3_colometry.py`, `v4_pauline_review.py`) should be retired. I recommended **wide scope, framed as freeze-and-document rather than delete**: the project transitioned from a machine pipeline (v0→v1→v2→v3) to a hand-edited corpus (`v4-editorial/` as single source of truth) when v4 reached 260/260 coverage. The producer scripts have been operationally vestigial since then; the documentation hadn't caught up. Stan greenlit ("be very careful, redundant, and smart about paralleling/double-checking, but proceed").

**Pre-flight audit (5 parallel Sonnet agents):**

1. **Live-readers audit:** Verified the scope claim "v4-editorial is single source of truth, v1/v2/v3 have no live readers." Outcome: scope claim holds — *with one caveat.* `scripts/build_books.py` had a silent runtime fallback to `v3-colometric/` (`GK_FALLBACK_DIR`, `resolve_greek_path()` lines 226–245) that returned a v3 path if a v4 file was missing. Practically dead given v4 completeness, but the code path was active.
2. **Retirement-readiness for the 3 named scripts:** All three confirmed retire-ready — zero inbound module imports, all command-line references are doc-examples. Input paths point at `v3-colometric/` / `v2-colometric/`.
3. **morphgnt_lookup.py + sibling-script status:** `morphgnt_lookup.py` is **ACTIVE** (used by `validators/common.py` as the morphological backend for the production validator suite — must NOT archive). `v4_auto_fix.py` is **ACTIVE**. Five additional scripts surfaced as same-class vestigial: `v2_colometry.py`, `auto_colometry.py`, `build_v0_prose.py`, `generate_english_glosses.py` (SEED-ONLY, predates `regenerate_english.py`), `generate_pauline_english.py` (zero inbound refs).
4. **v4-editorial completeness:** 260/260 confirmed (27 books, all expected chapter counts present). The `build_books.py` fallback is unreachable on every normal build.
5. **English-gloss generator status:** `generate_english_glosses.py` is SEED-ONLY (predates incremental-regen tool); `generate_pauline_english.py` is fully vestigial (no inbound refs, V1_DIR fallback).

**Archived this commit (8 scripts → `scripts/archive/`):**

- `build_v0_prose.py` (v0 producer)
- `auto_colometry.py` (v1 producer)
- `v2_colometry.py` (v2 producer)
- `v3_colometry.py` (v3 producer; "last machine tier")
- `diagnostic_scanner.py` (line-auditing tool, superseded by Layer 2 validators)
- `v4_pauline_review.py` (one-time editorial review pass)
- `generate_english_glosses.py` (eng-gloss seeder, superseded by `regenerate_english.py`)
- `generate_pauline_english.py` (Pauline-subset seeder)

**Defensive code change:** Removed the `GK_FALLBACK_DIR` v3-colometric fallback from `scripts/build_books.py`. `resolve_greek_path()` now raises `FileNotFoundError` with a clear message if a v4-editorial file is missing. Smoke-tested with `--book mark` and full-corpus build; both pass.

**Documentation aligned:**

- `scripts/archive/README.md` (new) — architecture-transition explanation + per-script provenance.
- `CLAUDE.md` Key Files table — replaced archived-script entries with currently-active scripts; updated NEVER list (auto_colometry warning replaced with `scripts/archive/` warning).
- `data/text-files/README.md` + four per-tier READMEs (`v0-prose/`, `v1-colometric/`, `v2-colometric/`, `v3-colometric/`) — producer paths now point under `archive/`; v3 README "Historical note on the build pipeline" updated to record the fallback removal.
- `handoffs/03-architecture.md` — banner at top noting the archive sweep; line 539 diagnostic_scanner description updated to record the archive move; dated update blocks below preserved unchanged (snapshots are append-only).
- `handoffs/04-editorial-workflow.md` — banner at top; "Protection of Hand-Edited Chapters" section updated to record resolution; Phase 1 example (line 177) updated from `v3_colometry.py` to currently-active scripts (`apply_m1_merges.py`, etc.).
- `scripts/morphgnt_lookup.py` docstring — clarified that the production user is now `validators/common.py`; v3_colometry.py noted as the original (now-archived) reason for its existence.

**Carry-forward (separate from this commit):**

- `bezae_compare.py` reads multiple tiers analytically and may benefit from a similar fallback review, but it is a live web-app feature (not in the editorial loop) and its multi-tier reads are appropriate for its purpose. No action recommended at this time.
- The frozen tier corpus directories (`v0-prose/`, `v1-colometric/`, `v2-colometric/`, `v3-colometric/`) remain in `data/text-files/`. They are inert but harmless; preserved for provenance and re-derivability per the data/text-files/README.md "two reproducibility regimes" framing.

**Audit-status for this commit per §6.5:** This is a SCOPE claim about the project's architecture ("v4-editorial is single source of truth, v0–v3 are frozen scaffolding"). Per §6.5 trigger #2 (scope claim), an audit was warranted and was satisfied by the 5-agent pre-flight verification documented above. The audit-evidence is the agent verdicts + the §10 entry capturing them; the scope claim has the empirical basis Stan asked for.

---

### 2026-04-26 (later⁶) — Final residue purge: README.md + 3 scripts + secondary doc/CLAUDE.md sweep

After the later⁵ commit, a wider sweep surfaced more retired-framework residue across public-facing surfaces and helper scripts. Same carry-forward-inertia class as later² through later⁵; same audit-skippable rationale.

Purged:

- **`README.md`** — line 7 (project tagline) replaced four-criteria language ("one atomic thought, one image, one breath unit, motivated by source-language syntax") with "an atomic thought-unit reflecting Greek grammatical structure." Method section (lines 17-22) replaced the four-criteria enumeration ("1. Atomic thought / 2. Single image / 3. Breath unit / 4. Source-language syntax") with the canonical three-forces summary (generative / subtractive / diagnostic) plus precedent grounding.
- **`CLAUDE.md`** — `## Colometric Principles (Orientation Only)` section: replaced `### Four Criteria (hierarchy)` block (with "Breath Unit" as criterion 3 and the "default + unless" 2026-04-16 reframe wording) with `### Three forces (canon §1)` summary matching current canon §1. Updated R-rule pointer line to drop the "default + unless" framing.
- **`scripts/scan_english_drift.py:21`** — heuristic comment "almost never ends a breath unit" → "is almost never line-final in well-formed English."
- **`scripts/v3_colometry.py`** — three methodological references (line 995 "loses the breath-unit structure" → "loses the per-image atomic-thought structure"; line 3275-3276 "exceed the breath-unit threshold (~30 syllables ≈ 80 chars of Greek)" → "exceed a display-length threshold (~80 chars of Greek)"; line 3505 "too long for a single breath unit" → "display-overlong lines").
- **`scripts/v4_pauline_review.py:4`** — docstring "Applies the four criteria + sub-principles from 02-colometry-method.md" → "Applies the colometric framework codified in private/01-method/colometry-canon.md" (the referenced doc path was also stale).
- **`handoffs/01-project-overview.md:118`** — descriptive use ("the author's own breath units are best preserved") → "the author's own atomic thought-units are best preserved." Stan's standing instruction (later⁴) explicitly extended the purge to descriptive uses, not just methodological ones.
- **`handoffs/03-architecture.md:539`** — diagnostic_scanner.py description: the parenthetical claiming a "residual breath-unit test in the script's source" no longer matches the file (test was purged at later⁵). Updated to record the purge date and flag stale path discovery as a separate issue.

Verified post-purge: `breath unit` / `breath-unit` only remain in two explicit historical retirement notes (canon §10 entries themselves and the audit-trail note in `scripts/diagnostic_scanner.py:11`); these are intentional. `four criteria` and `Breath Test` return zero matches across the repo.

**Separate observations carried forward (not addressed this commit):** the input paths for `scripts/v3_colometry.py` (`data/text-files/v2-colometric/` → `v3-colometric/`) and `scripts/v4_pauline_review.py` (V3_DIR → V4_DIR) likely point at corpus stages that no longer exist as live working surfaces. Same vestigialness flag as `scripts/diagnostic_scanner.py` (later⁵). Stan to decide retire-vs-update for all three.

**Audit-skippable per §6.5** — pure residue cleanup of public-facing and helper-script surfaces that operationalized retired framing. Substantive retirements (Breath as a force / four-criteria → three-forces) were made 2026-04-20 with empirical 0-impact validation and audit. No new precedence claims, scope claims, closed-list extensions, or category carve-outs.

---

### 2026-04-26 (later⁵) — scripts/diagnostic_scanner.py breath-unit test purged

Stan corrected my hedging: "if we're purging, we're purging, right" — the script's residual `Test 3: Syllable count (breath unit)` was the same residue class as the §4 Breath Test removed at later². No reason to hold for separate decision; carry-forward-inertia firing again.

Removed from `scripts/diagnostic_scanner.py`:
- `Test 3: Syllable count (breath unit)` block (the per-line check + flag-append logic)
- `FLAG_TOO_SHORT` and `FLAG_TOO_LONG` flag definitions
- `count_greek_syllables` function (~25 lines; only used by Test 3)
- Now-orphaned helpers: `_VOWEL_BASES`, `_DIPHTHONGS`, `_strip_accents`
- Two `FLAG_TOO_*` references in violation-breakdown reporting lists
- Unused `unicodedata` import
- Docstring updated to reflect current two forces (atomic thought, single image) with a brief note explaining the retirement

Verified: script parses cleanly; no remaining `breath`/`FLAG_TOO`/syllable references except the docstring retirement note. handoffs/03-architecture.md:539 description (updated at later⁴) now matches the script.

**Separate observation (not addressed this commit):** the script's input-discovery logic expects `data/text-files/v3-colometric/` paths that no longer exist (corpus structure migrated to `data/text-files/v4-editorial/`). Smoke test on `mark-04` chapter failed at file-discovery. Suggests the script may be vestigial overall, not just the breath-unit test. Logged as carry-forward — Stan to decide whether to retire the script entirely or update its path-resolution.

**Audit-skippable per §6.5** — internal cleanup of code that operationalized a retired criterion. Substantive Breath retirement was made and audited 2026-04-20.

---

### 2026-04-26 (later⁴) — Adjacent-surface residue purged: CLAUDE.md + handoffs/

After the canon residue audit (later³), Stan asked whether the cleanup implies anything mechanical needs checking, or just documentation drift. Honest answer: corpus is fine (substantive retirements were applied 2026-04-20 with empirical 0-impact validation), but ADJACENT documentation surfaces still carried retired-framework references. Sweep across validators/ (clean), scripts/ (one remaining residue at `scripts/diagnostic_scanner.py:249` — held per Stan's direction), CLAUDE.md, handoffs/, and memory active files (clean; archive/ entries are properly archived).

**Purged this commit:**

- **CLAUDE.md line 9** — "natural breath unit based on Greek grammatical structure" → "atomic thought-unit reflecting Greek grammatical structure". Stan called the descriptive use of "breath unit" muddying even when not invoked as methodological criterion; purged.
- **handoffs/01-project-overview.md line 5** — same descriptive purge as CLAUDE.md line 9.
- **handoffs/01-project-overview.md line 223** — "three core criteria (atomic thought, single image, breath unit)" → "framework's primary forces (atomic thought, single image), with syntax operating as a subtractive constraint rather than a primary driver". Reframes the historical v1-vs-v3 finding to current three-forces vocabulary.
- **handoffs/01-project-overview.md line 239** — Universal Vocative Rule explanation: "an atomic thought (a complete address act) and a natural breath unit (pause before and after)" → "an atomic thought (a complete address act, with natural pause before and after)". Folds the breath-unit framing into the atomic-thought clause as a parenthetical phenomenological claim, not a methodological criterion.
- **handoffs/01-project-overview.md line 257** — "The four core criteria (atomic thought, single image, breath unit, source-language syntax)" → "The framework's three forces (atomic thought, single image, syntax-as-constraint)". Internal consistency restored (the file had been using both "three core criteria" and "four core criteria" inconsistently).
- **handoffs/03-architecture.md line 539** — diagnostic_scanner.py description: "Applies the three core colometric criteria to flag lines that fail atomic thought, single image, or breath unit tests" → "Applies the framework's forces to flag lines that fail atomic-thought or single-image tests. (Note: a residual breath-unit test in the script's source is residue from the retired Breath criterion; see canon §10 2026-04-20 retirement entry.)". Doc now states what the script SHOULD do; the script's stale test logic flagged for separate fix.
- **handoffs/04-editorial-workflow.md lines 365, 440, 448** — same purges as 01-project-overview lines 223, 239, 257 (the two files carried near-duplicate content).

**Held for separate fix:**
- **scripts/diagnostic_scanner.py line 249** — "Test 3: Syllable count (breath unit)". Active script's stale test logic. Stan held: needs separate decision on whether to retire the test entirely, replace with a different metric, or leave the test logic but rename. Logged as carry-forward.

**Audit-skippable per §6.5** — internal documentation cleanup + cross-reference updates that don't assert precedence. The substantive retirements (Breath, four-criteria framework) were made and audited 2026-04-20.

**Going-forward discipline (continuation of carry-forward-inertia from later² + same-session sweep from later³):** every retirement triggers a same-session sweep across active sections AND adjacent documentation surfaces (CLAUDE.md, handoffs/, validators/, scripts/, memory). Per the carry-forward-inertia diagnostic: the deciding move was already made at the substantive retirement; downstream documentation residue is mechanical to fix at the same time, not a deliberation point.

---

### 2026-04-26 (later³) — Residue audit pass: 5 more retired-framework references purged

After the Breath Test removal (later²), Stan asked for another residue audit per the carry-forward-inertia discipline lesson — sweep for OTHER places where §X retired a thing but §Y still has dead text. Five active residues found and purged:

- **§0 Foundational premise (line 9)** — "four criteria, rules, hierarchy, structural justifications, merge-overrides" → "three forces, structural justifications, merge-overrides, rules". The four-criteria framework was retired 2026-04-20 in favor of three forces; "hierarchy" referenced the retired strict-hierarchy framing.
- **§2 justification #5 substantive-adjunct (line 351)** — "Breath's continuing status is under review (§1)" was true 2026-04-19/20 when retirement was being decided. Breath was retired 2026-04-20. Updated to "Breath itself is retired (§9 Superseded Formulations)" with the surrounding contrast paragraph adjusted to current-state framing.
- **§5 Register Operationalization intro (line 1065)** — "The four-criteria hierarchy as stated (atomic thought > single image > breath > source-language syntax) is register-flat at the base layer" → "The three-forces framework (§1) is register-flat at the base layer". The retired-framework anchor was load-bearing for the "register is a modulation layer" claim that follows; updated to the three-forces anchor without changing the substance.
- **§5 "How to read the table" note (line 1080)** — "the existing hierarchy governs" → "the three forces (§1) govern"; "No new criteria enter" → "No new forces enter". Same framework-anchor swap.
- **§5 Six Registers table, Argumentative row (line 1077)** — "cognitive hierarchy overrides breath" → "licensed by register". Breath is retired; nothing for the hierarchy to override.
- **§3.15 Authorial Style Principle (line 868)** — "The same four colometric criteria apply uniformly" → "The same colometric framework applies uniformly". Substance unchanged (uniform application across authors); framework anchor updated.

Sections checked and confirmed clean (no retired-framework residue): §0 Posture, §0 Architecture, §1 The Framework (cleaned in pass 1+2), §2 Five Justifications + M1-M4, §3 The Rules (R1-R28; retired R15/R16/R21/R25/R26/R29 properly listed in Rule Index with `*Retired (see §9):*` marker), §4 Operational Tests (Breath Test now removed), §6 Precedent and Scope (cleaned in pass 1), §7 (retired marker present), §8 Greek-Specific Application.

The carry-forward-inertia pattern was the diagnostic: each of these residues had been visible in the canon for sessions but treated as out-of-scope for non-residue work. The discipline added at "later²" — *if §X retired a thing, sweep §Y for residual references at the same time* — would have caught all five at the time of the original retirements. Going forward, this discipline applies to every retirement: same-session sweep across active sections.

**Audit-skippable per §6.5** — internal formatting cleanup + cross-reference updates that don't assert precedence (no rule semantics changed, no new scope/precedence/closed-list claims). The substantive retirements (Breath, four-criteria framework) were made and audited 2026-04-20.

---

### 2026-04-26 (later²) — §4 Breath Test removed (residue from §1 retirement)

§1 retired Breath as a force on 2026-04-20. The §4 Operational Tests subsection on the Breath Test was not removed at that time and survived four subsequent canon-cleanup passes. It self-confessed "no falsifiable threshold... not a mechanical gate" — dispositive on its own that the section was residue, not a reasoned exception. §1 had already made the call.

The contradiction was flagged as Tier 3 carry-forward in the 2026-04-25 canon audit, then carried forward across three subsequent session continuations without action. Stan caught it directly today and named the pattern: when §X retires a thing, sweep §Y for residual references at the same time; don't carry the contradiction as a "deferred" decision point. **A contradiction where one side has already retired the thing is residue, not deliberation.**

This commit removes §4 The Breath Test entirely. The cognitive-chunking work breath was informally doing (long-line flag) is fully absorbed by §2 structural justification #5 (substantive adjunct as own focus). §9 retains the retirement narrative; §10 retains the 2026-04-20 reasoning trail.

**Audit-skippable per §6.5** — internal formatting cleanup + cross-reference update without precedence claim. The substantive call (retire Breath) was made and audited 2026-04-20.

**Discipline lesson logged:** "carry-forward inertia" — when an item appears on a carry-forward list, the test for whether it earns continued deferral vs. immediate action is whether the deciding move has already been made elsewhere. If yes, fix on first contact instead of re-deferring.

---

### 2026-04-26 (later) — Mechanical hook port from Tanakh + §6.5 trigger #12 added

Three port-backs from sibling Tanakh-reader project, where they had been built and validated. Cross-project audit (three parallel hostile audits — discipline machinery, three-layer architecture, voice quality) surfaced these as items GNT was missing. Stan greenlit the engineering investment.

**1. Regression-baseline pre-commit hook.** Extended `validators/run_all.py` with three new modes — `--summary` (per-rule dashboard), `--baseline-check` (compare to `validators/.baseline.json`; exit 1 on regression), `--update-baseline` (capture current counts). Created `validators/.baseline.json` with all 9 GNT validators at 0 candidates each. Wrote `validators/hooks/pre-commit` shell script gating commits that touch the canon, syntax-reference, v4-editorial corpus, or validators/ — runs `--baseline-check` and blocks if any rule's candidate count increased. Installed to `.git/hooks/pre-commit`.

**2. Content-aware commit-msg hook.** Wrote `validators/check_canon_extensions.py` adapted from Tanakh's `validators/check_canon_extensions.py` with GNT-specific changes: watches both `private/01-method/colometry-canon.md` AND `data/syntax-reference/greek-break-legality.md`; regex patterns updated for GNT §3.X rule numbering; audit-evidence keywords updated to GNT §-numbers (§6.5, §10); `NEW_DATED_PRINCIPLE_RE` loosened per cross-project audit-B finding (now detects any new `### ` heading whose text doesn't look like a §10 dated update-log entry, broadening recall at the cost of more false-positives that the skip-safe claim can clear). Wrote `validators/hooks/commit-msg` shell script. Installed to `.git/hooks/commit-msg`.

**3. §6.5 trigger #12 — Corpus-fit verification (post-codification AND post-detection).** Added as the 12th mandatory-audit trigger. Pre-commit audit dispatched per §6.5 trigger #9 (meta-rule changes to the trigger list itself); audit verdict was ADOPT-WITH-REVISION with four substantive changes from Tanakh's original wording: (i) explicit relationship statement to triggers #3 and #7 to disambiguate scope; (ii) dropped ὅτι-complement-after-cognition example (overlaps with §4 Period Test, smuggles scope); (iii) replaced with μέν/δέ pairing example (load-bearing GNT pattern); (iv) updated §3.7 reference to §9 Superseded Formulations entry on §3.7 retirement (since §3.7 itself was retired 2026-04-25). Cut redundant prose ("HOW WE KNOW" recap, "parallel by default" duplication).

**Net impact.** GNT now has cross-project parity with Tanakh (and BofM, who had built similar mechanisms first). The audit-discipline gap that was discretionary-only at commit time is now mechanically gated:

- Pre-commit hook catches **regressions** (any rule's candidate count increased).
- Commit-msg hook catches **closed-list extensions** (new rules / merge-overrides / Layer 1 table rows / audit triggers / SCOPE bullets) that don't increase any rule's count and would otherwise slip through.
- Both hooks bypass-able via `git commit --no-verify` for Stan-only explicit decisions.

**This commit's audit status.** §6.5 trigger #9 (meta-rule change to the trigger list itself) audit dispatched and applied per the revised wording above. §6.5 trigger #11 (cross-project import) audit consists of the original three parallel audits dispatched 2026-04-26 (discipline / three-layer / voice). §6.5 trigger #1 (new closed-list category in §6.5) audit also satisfied via trigger #9's meta-rule audit. All three triggers fire on this single addition; all three are documented above.

---

### 2026-04-26 — CLAUDE.md tightening: required audit-status declaration in canon-touching commit messages

Cross-project signal: BofM landed a content-aware commit-msg hook that blocks commits touching the BofM canon if the diff matches §7.3 trigger patterns (new closed-list rows, new rule sections, new merge-overrides, new dated principles, new triggers, new SCOPE-exclusion bullets) without audit-evidence in the commit message. Their precedent failure (an emotion-class extension smuggled into an audio-asset commit) would now block.

Same gap exists for GNT in same shape: §6.5 trigger #1 audit dispatch is discretionary at commit time; if Claude skips, nothing catches. This session demonstrated the failure mode (the "judgment-handoff smuggling" catch earlier this week — caught by Stan, not by automation).

GNT response, smaller than BofM's mechanical gate. Two reasons for the smaller response:

1. **The pre-commit regression-baseline hook isn't buildable for GNT yet.** That hook depends on validators producing rule-violation counts. GNT validators are "under active build" per §0; until they produce baselines, that half of BofM's gating isn't available.

2. **Recent commit-message practice is already mostly disciplined.** Spot-check of the last 11 canon-touching commits showed 10 of 11 explicitly declared audit-status (skippable + reason, or dispatched + evidence-location). One inconsistency, no failure. Marginal benefit of a full mechanical hook is real but smaller than BofM's situation.

**Documentation tightening applied (this commit):** CLAUDE.md "Pre-commit adversarial-audit discipline" section extended with one paragraph requiring every canon-touching commit message to declare audit-status explicitly — either `Audit-skippable per §6.5 ([reason])` or `Audit dispatched: [evidence]`. Omission becomes a visible discipline failure in `git log`. Closes most of the gap without engineering investment. The mechanical hook (BofM-style content-aware commit-msg gate) remains a deferred option if drift recurs.

**Audit-skippable per §6.5** (defensibility-capture addition to an already-settled rule — the existing pre-commit discipline — without scope change). No rule semantics modified.

---

### 2026-04-25 (later⁷) — Voice cleanup pass 3: Foundational premise rewrite + §4 redundancy removal

Stan rewrote the Foundational premise paragraph to give a more accurate "how did we get here" narrative (the actual sequence: Skousen's term → Stan expanded the concept → tested on BofM English → applied to GNT → universalist generalization). Web search confirmed Skousen's stated rationale in *The Earliest Text* is BofM-dictation-specific, not part of a "previous pioneers in colometry" tradition; bracketed claim removed accordingly. Per Stan's direction, then applied the slop-cleanup discipline to the rewritten paragraph + reviewed the rest of the document.

Foundational premise paragraph cleanups (7 internal edits within one paragraph):

  - Bureaucratic stack: "The operating key assumption and theoretical framework for this project is that..." → "The project's working hypothesis is that..."
  - "real-world demonstration" → "demonstration" (filler removed)
  - Verbose Skousen sentence "Stan took inspiration from Skousen's coining of the term 'sense-line' as a conceptual starting point and expanded upon the concept until arriving at the definition mentioned above" → "Stan took Skousen's term as a starting point and expanded the concept to the definition above"
  - Passive "This expanded 'atomic thought' unit was then used to experiment in creating line breaks..." → active "He then experimented with line breaks..."
  - Hedge pile "where it seemed to genuinely be exposing idea units" → "where the expanded definition appeared to expose idea-units"
  - "his same method" → "the same method"
  - "sense-lines" / "sense lines" → standardized to "sense-lines"
  - All-caps "ANY text" → italicized "*any* text" (scholarly emphasis convention)
  - Air-quotes around our internal definition removed; quotes preserved on first introduction of "sense-lines" and on Skousen's quoted phrase

§4 Operational Tests redundancy removed:

  - "Post-Split Function-Word Recheck" subsection had a duplicate gold-standard chapter list (already stated in the preceding "Gold-standard regression-test chapters — why these four" subsection). Replaced the duplicate list with an inline reference to the first list, preserving the operational instruction ("manually diff these four chapters' v4 + eng-gloss before and after").

Sections reviewed and found tight after prior cleanups (no edits this pass): §0 Posture, §0 Architecture, §0 What is this document (the "structure aims to keep the integration honest" sentence flagged 4× and kept by Stan stays), §1 Three Forces, §1 Priority Order, §1 Imposing-vs-Revealing, §2 Five Structural Justifications, §4 Two-Prong Exception Test, §6 Defensibility-capture (cleaned in pass 1 + pass 2).

Net: ~12 lines changed across 2 paragraphs/sections. No rule content modified. Audit-skippable per §6.5.

Going-forward discipline (codified across passes 1-3 in §10 entries `2026-04-25 (later⁵)` through `(later⁷)`): write for human readability throughout; cost asymmetry runs one direction (extra context for humans is free for AI); domain Greek/colometric terms stay; project-internal jargon gets defined or rewritten as description; section-internal historical residue goes to §10; bureaucratic nominalizations / passive voice / "serves to" constructions / triadic-rhythm parallels / self-restating clauses / meta-pointing cross-references all get pruned opportunistically.

---

### 2026-04-25 (later⁶) — Voice cleanup pass 2: jargon expansion + AI-slop removal in §0-§1 + §3.7 residue

Stan committed to the framing: "if this is my proto-scholarly document, write it for the human reader by default. Extra context costs Claude nothing; missing context costs the human reader real effort." Discriminator: write for humans throughout; AI-jargon (project-internal shorthand) goes; domain Greek/colometric terms stay because they're content.

This pass:

- §0 preface (line 33): Stan's air-quote removal landed. Direct content-led prose, no scare-quotes around content.
- §0 Part 1 bullet (line 35): replaced "any work session performed by Claude under Stan's direction involving editorial work reads it" (Stan's prior bureaucratic phrasing) with content-led "is the constitutional core: theoretical foundation (§§1-2) and operational rule reference (§§3-4)." Reader-routing handled separately by the Reader's guide; the Part bullets describe what each Part *is*.
- §1 Part 1 epigraph (line 52): "A trench Claude reading sections 1 through 4 has everything it needs for editorial work." → "Sections 1 through 4 contain everything an editor needs to make line-break decisions." Drops "trench Claude" project jargon; states the content directly.
- §2 M4 over-split rule (line 420): "Most session 18/19 reversals" → "Most reversals." Strips the project-internal session-numbering reference; the verse list communicates the data point.
- §4 Operational Tests intro (line 936): "These are the instruments trench Claudes actually run" → "These are the diagnostics actually run." Drops "trench Claudes."

Net: 5 small edits, 5 lines changed. No rule content modified.

**Going-forward discipline:**
- Domain Greek/colometric terms (genitive absolute, M1, R8, hoti-complement, καί-merge) stay — they are content.
- Project-internal jargon (trench Claude, session-numbering, sweep, validator, scanner, cascade) needs to be either defined upstream once OR rewritten as description. "Session" used operationally (e.g., "in the same session" within §6.5 trigger #4) earns its place because it has a concrete operational meaning at commit-time; "session 18/19 reversals" was just project-internal index residue.
- Reader-routing belongs in the Reader's guide, not in every Part description.
- Bureaucratic agent-naming ("performed by Claude under Stan's direction") is AI-precision over human-readability. The cost asymmetry runs the other way: extra context for humans is free for AI; AI-precision-via-jargon is costly for humans.

Audit-skippable per §6.5 (internal formatting cleanup; no rule content changed; no scope/precedence/closed-list claims).

---

### 2026-04-25 (later⁵) — Voice cleanup: stripped AI-slop patterns from §0-§1 and §6

Stan demonstrated a cleanup pattern by editing the §0 "How to use this document" preface in place: cut bureaucratic abstraction ("the canon serves two audiences with different reading patterns"), strip restated content ("As such, this document does allow those to blend together"), name the things instead of categorizing them. Direction: "your document reads too much like AI slop in places and not QUITE coherent for the human audience." Stan invited Claude to riff off the pattern and clean more.

Patterns hunted:
- Bureaucratic noun phrases ("audiences with different reading patterns")
- Triadic parallel "X, Y, and Z" structures filled out for rhythm
- Conceptual-filler sentences telling you what's coming rather than just being it
- Self-restating clauses ("X. As such, X-restated.")
- Meta-pointing to other parts of the canon when the cross-reference adds nothing
- "Serves to" / "serves as" instead of "is" or "does"

Changes this commit (Stan's + Claude's, intermingled in the same paragraphs):

- §0 preface heading: "How to use this document" → "What is this document?" (Stan)
- §0 preface body: rewritten content-led instead of audience-led (Stan)
- §0 preface: double-space fix
- §1 Mission: cut "(stated in the foundational premise at the top of the canon)" meta-pointer
- §1 Method tail: cut "These are two sides of the discipline, not a conflict" defensive restatement
- §1 Framing Principle intro: cut "Before the three forces themselves, the relationship between thought and syntax has to be stated precisely..." meta-framing-of-the-section opener
- §1 Consequences item 1: cut "The thought is the target" restatement
- §1 Consequences item 2: cut "Not a separate check; not a lesser concern" defensive add
- §1 Consequences item 3: cut "But the thing we care about is the relationship..." restatement of prior sentence
- §1 Imposing-vs-Revealing: cut "This is the load-bearing meta-principle for the whole project:" meta-claim before the bullet list
- §6 Defensibility-capture middle paragraph: cut "The §3.17 ... and the §6.5 ... each include explicit WHY/HOW/SCOPE elements. Making the requirement explicit here means..." meta-pointing-and-restating sentences
- §6 v4 framing list: tighter intro ("This matters for:" vs. "This framing is relevant for:"); bolded list-item leads for parallelism

Net: ~30 lines changed, 14 insertions / 16 deletions across ~9 paragraphs. No rule content modified; voice tightened.

Audit-skippable per §6.5 (internal formatting cleanup; no scope/precedence/closed-list claims; no rule semantics changed). The discipline going forward: when in or near a section for other reasons, prune the slop opportunistically. No standing cleanup-pass directive — clean-as-you-go.

---

### 2026-04-25 (later⁴) — Residue cleanup: stripped historical-narrative residue from active sections per the rationale-vs-reasoning-trail discipline

Stan's question on line 27 ("Pre-2026-04-20, the canon mixed the two...") and line 31 ("How to use this document — used by whom?") surfaced a class of issues: the canon had accumulated historical-narrative residue inside current-state operational sections. Each residue was load-bearing at the moment of its codification (it justified a recent change) but stale once the change was settled. The pattern: "(added 2026-04-X)," "TIGHTENED 2026-04-X," "Pre-2026-04-X we used to do Y, now we do Z," "Earlier formulations used a four-criteria framing..."

**Stated discipline going forward (now codified by the cleanup itself):**

- **Rationale-for-current-state lives in the rule body.** Why the rule is what it is.
- **Reasoning-trail-for-the-change lives in §10.** The journey of how we got there. §10 is the canonical record.
- **Fresh-change pointer ("see §10 entry 2026-04-X") allowed inline temporarily** — in the rule body, near the change. After a few sessions or once the change is settled, even the pointer goes; §10 is enough.
- **Status markers for retired material stay** ("(retired 2026-04-X — see §9)"); they communicate current state.
- **Corpus chronicle dates stay** in the §8 Corpus Statistics table where the dates are intrinsic to the chronicle.
- **Operational cutoff dates stay** (e.g., "prospective from 2026-04-22" on the defensibility-capture meta-rule — that's the cutoff, not residue).

**Cleanup applied this commit:**

- §0 Architecture: stripped "Pre-2026-04-20, the canon mixed the two..." (line 27 residue); stripped migration-date and "under active build 2026-04-20" markers from Layer 1/Layer 2 descriptions (current-state framing).
- §1 The Framework intro: stripped "Earlier formulations used a four-criteria strict-hierarchy framing..." sentence.
- §1 Breath subsection: removed entirely from §1; moved to §9 Superseded Formulations as "Breath as a Fourth Criterion *(retired 2026-04-20)*". The §10 retirement entry stays as the canonical reasoning trail.
- §1 Reader's guide heading: dropped "(added 2026-04-25)" date marker.
- §1 Imposing-vs-Revealing watchlist annotation: trimmed "Vocabulary list extended 2026-04-25 after the 'soteriological climax' catch" reasoning trail to a clean operational pointer ("See `feedback_rhetoric_bandwagon.md` catches list for examples").
- §2 M1 strict-application caveat: stripped italic reasoning trail ("*Codified 2026-04-21 after a round-2 adversarial pass on 318 KEEP_MERGED verdicts...*"). Rule body retains the rationale ("the canon's overall posture is merge-by-default"); §10 entry 2026-04-21 (later²) carries the trail.
- §3 scope/precedence/closed-list/carve-out diagnostic heading: dropped "(added 2026-04-24 from BofM cross-project directive)" date marker.
- §3.1 No-Anchor Rule: "TIGHTENED participle scope (2026-04-16)" → "Participle scope" (current-state heading); stripped corpus-status date.
- §3.2 Layer 1 migration: "*2026-04-20: R2–R7 ... have been migrated to ...*" → "*R2–R7 ... live at ...*" (current-state framing).
- §3.5 R10 Cognition vs. Speech: stripped "*Established:* 2026-04-15 session ... *Refined:* 2026-04-16 session ..." reasoning trail. Rule body retains the substance; §10 has the journey.
- §3.5 ὅτι Placement: "Corpus state (post-2026-04-18 flip): 834 leading : 0 trailing" → "Corpus state: 834 leading : 0 trailing" (the flip date is in §10).
- §3.7 R28 / inline corpus-stat callouts: stripped sweep-dates from "(2026-04-15 sweep)" and similar parentheticals where the date was ornamental, not load-bearing.
- §6 Defensibility-capture paragraph: stripped per-codification dates where they were illustrative-not-cutoff.
- §6.5 Provenance + Why-it-earns paragraphs: replaced two paragraphs of reasoning-trail prose with a one-line pointer to §10 entry 2026-04-24. The §10 entry has the full audit trail and import context.
- §8 Greek-Specific subsections: stripped dates from "Participial chain collapse (2026-04-13 finding)" and "Prepositional catena absorption (2026-04-13)"; stripped sweep dates from inline cross-references to §3.11 and §3.8.

**What was NOT stripped (intentional residues that earn their place):**

- §3.17 retirement footnote at line 759: fresh change (2026-04-25), pointer to §9 — kept per the "fresh-change pointer allowed inline temporarily" clause.
- Heb 1:3-4 removal annotation at §1 line 306: fresh change (2026-04-25), explanatory note. Kept.
- §6 "prospective from 2026-04-22": cutoff date for the defensibility-capture meta-rule. Operational, not residue.
- §6.5 pointer to §10 entry 2026-04-24 (line 1183 after this commit): the §6.5 trigger list was just imported; pointer stays for the few-sessions transition window.
- §7 retirement note ("Retired 2026-04-20. Scholarly-grounding material..."): retired-section status marker.
- §8 Corpus Statistics table: chronicle dates intrinsic to the data.
- §9 Superseded Formulations entries: §9 is the proper home for retirement narratives.
- §10 entries: §10 is the proper home for the reasoning trail.

**Net effect.** Active rule sections now state current-state cleanly without embedded "we used to do X" narrative. §10 stays as the single source of truth for change history. ~58 lines edited / 31 lines net removed across ~14 paragraphs. Audit-skippable per §6.5 (internal formatting cleanups + cross-reference updates that don't assert precedence). No rule content lost; no cross-reference broken.

**Defensibility capture (for this commit's discipline):**
- WHY: stale historical residue in current-state sections muddies what each section is *for*; doubles the canonical record between rule body and §10; creates editorial friction (Stan can't tell what a date is doing in a rule body).
- HOW WE KNOW: Stan's questions on line 27 + line 31 surfaced the pattern; comprehensive scan identified ~14 instances of pure residue; rationale-vs-reasoning-trail discipline distinguishes load-bearing dates from residue cleanly.
- SCOPE: applies to active rule sections (Parts 1-2). §9 retirement narratives and §10 update log are the proper homes for historical content; they retain their dates.

---

### 2026-04-25 (later³) — Section-purpose disclosure: preface rewrite + Reader's guide + PURPOSE headers at each section

After Stan's editorial-anxiety inquiry (he wanted to revise theory paragraphs without breaking Claude's literal-read targets), evaluated three architectural options: full split into two docs (rejected — drift risk + cross-reference rework + BofM divergence), inline blockquote convention for OP paragraphs in MIXED sections (rejected after three parallel hostile audits — theater not protection, fast decay, BofM precedent is "extract don't annotate"), section-level disclosure (adopted).

**This commit applies the section-level disclosure path:**

1. **Preface rewrite (lines 31-36 → expanded).** Replaced the misleading "Part 1 = constitutional core for humans" framing with an honest description: Part 1 contains BOTH theoretical foundation (§§1-2) AND the heaviest operational rule reference (§§3-4). Stan's framing ("mainly human / mainly robot / some bleed is fine — that's how it goes") preserved as the organizing posture.

2. **Reader's guide subsection added** after the preface. Routes readers by purpose: editor making editorial decisions → §§3-4 + §6.5; scholar reading method as artifact → §§0-1, 6, 8; tracking decision evolution → §§9-10. States explicitly that §§1 and 2 are dual-natured by design and that bolded paragraphs in those sections are load-bearing regardless of surrounding prose.

3. **PURPOSE headers added at each of 9 section openers** (§§1, 2, 3, 4, 5, 6, 8, 9, 10). Each header discloses the section's predominant character: "mainly philosophical," "mainly operational," "dual-natured by design," or "mainly historical." Cross-references operational sub-blocks where they sit inside otherwise-philosophical sections.

**What was NOT done:**
- No paragraph-level inline markers (rejected per audit consensus — fast decay, classification ambiguity, distorts meaning at sub-paragraph mixing points).
- No section reshuffling (preserves cross-references; preserves BofM-parity).
- No two-doc split.
- No publishable-artifact extraction (separable; deferred).

**Audit discipline.** Three parallel Opus hostile audits (efficacy / edge cases / conversion + drift) ran before adopting the path. Audit consensus: preface rewrite unanimously approved; blockquote convention unanimously rejected; section-level disclosure (this commit's path) was the convergent positive recommendation. Per §6.5: this is internal formatting cleanup + cross-reference clarification (audit-skippable), but the audit was run anyway because the change touches the canon's organizing structure.

**Defensibility capture:**
- WHY: solve Stan's editorial-anxiety problem (revise theory without breaking operational reads) at the section level rather than the paragraph level.
- HOW WE KNOW: three parallel hostile audits documented in this session's folder; convergent rejection of paragraph-level marking; convergent approval of section-level disclosure.
- SCOPE: applies to canon top-of-document and section openers only; no rule content changed; no rule semantics affected.

---

### 2026-04-25 (later²) — Canon audit Tier 2: 4 corpus/canon mechanical fixes from rule-traceability findings

Following the 4 parallel canon audits (order/precedence, ambiguity, verbosity, goal-fit) earlier this session, Audit 4 (goal-fit) surfaced concrete canon-corpus mismatches. After Stan's pushback ("either fix the effing rules or quit effing hedging"), reclassified the findings: 4 are mechanical applications of existing rules, 1 (§3.16 inconsistency) was a misread of the rule's actual scope.

**Mechanical applications (Category A under existing rules):**

- **Rev 1:3** — restructured from 4-line layout violating M2 (`καὶ τηροῦντες / τὰ ἐν αὐτῇ γεγραμμένα` split verb from object) to 4 lines correctly applying justification 1 (N=3 substantival participles parallel) + M2 (each participle merged with its complement): `μακάριος ὁ ἀναγινώσκων / καὶ οἱ ἀκούοντες τοὺς λόγους τῆς προφητείας / καὶ τηροῦντες τὰ ἐν αὐτῇ γεγραμμένα, / ὁ γὰρ καιρὸς ἐγγύς.`

- **John 17:24** — `θέλω` had been on its own line, violating §4 Period Test which lists *thelo / epithymeo / boulomai* (desire) as OBLIGATORY-complement (no break permitted). Merged θέλω with its ἵνα-clause: `θέλω ἵνα ὅπου εἰμὶ ἐγὼ κἀκεῖνοι ὦσιν μετʼ ἐμοῦ`. Fronted topic `ὃ δέδωκάς μοι` retained as own line. Verse went from 7 lines to 6.

- **Rom 9:5** — `ὁ ὢν` had been orphaned at line-end; canon §8 line 1222 prescribes Christological reading (`ὁ ὢν` connects to `ὁ Χριστός` as substantival participle / appositional modifier). Restructured to: `ὧν οἱ πατέρες, / καὶ ἐξ ὧν ὁ χριστὸς τὸ κατὰ σάρκα, / ὁ ὢν ἐπὶ πάντων, θεὸς εὐλογητὸς εἰς τοὺς αἰῶνας· ἀμήν.` — 3 lines, with ὁ ὢν leading the appositive predicate. Category A within the canon's documented Category-C disposition (canon §8 already chose Christological).

- **Heb 1:3 L1 split + canon §1 line 295 citation correction** — L1 had merged `ὃς ὢν ἀπαύγασμα τῆς δόξης` with `καὶ χαρακτὴρ τῆς ὑποστάσεως αὐτοῦ`. The two attributes are distinct semantic domains (light/radiance vs. seal/imprint metaphors) — M1 strict-application caveat rejects gorgianic merge for cross-domain pairs; no other merge protection fires; §3.16 prescribes split for coordinating syntax with distinct images. Split applied. Verse went from 4 to 5 lines. Canon §1 line 295 had cited Heb 1:3-4 as a portrait-attribute (justification 2) example, but the rule's detectable signature (line 290) requires "no finite verb appears until a later verse" — Heb 1:3 has `ἐκάθισεν` within the verse. Removed Heb 1:3-4 from the example list with explanatory note pointing to §3.16 as the actual governing rule.

**Non-action (audit-misread)**: Audit 4 also flagged §3.16 aspect-shift as "fires inconsistently corpus-wide" citing Heb 1:3, Heb 1:9, and Phil 2:7. Re-reading §3.16 confirms: the rule covers any subordinating-vs-coordinating distinction, not just participle-chain aspect-shift. Heb 1:9 splits aorist+aorist parallel finite verbs (justification 1, parallel members with distinct predicates) — different rule. Phil 2:7 merges γενόμενος + εὑρεθεὶς (same-aspect participles describing the same incarnation event) — §3.16 elaboration-vs-distinct-events test fires merge correctly. The audit conflated §3.16 with finite-verb parallelism rules and assumed aspect-shift was §3.16's only diagnostic. No corpus action; no canon revision.

**Cascade outcomes**: regen for john + rom + rev + heb. Two regen successes (john 17:24, heb 1:3 — line counts changed). Two no-ops where line counts didn't change (rom 9:5, rev 1:3) but break positions shifted — required manual English re-pairing for rev 1:3 and heb 1:3 (per `feedback_verify_cascade_output` discipline). HTML rebuilt for all four books. `verify_word_order.py`: 0 discrepancies. `check_cascade_alignment.py`: 3 warnings (the known stable construction FPs).

**Pre-commit audit discipline**: §6.5 trigger #1 (canonical example correction), trigger #5 (canon revision retiring a citation), trigger #8 (canonical example modification) satisfied via the 4 parallel canon audits earlier this session. The corpus changes themselves are Category A applications under existing rules (M2 / §4 Period Test / canon §8 Christological reading / §3.16 + M1 strict-application).

**Reframing lesson logged**: Stan's pushback ("either fix the effing rules or quit effing hedging") reinforced that "edge cases" and "decision points" are usually mechanical applications I'm hedging on. If the canon prescribes X and v4 has Y, the default is to apply the canon. Stan's judgment is needed only when the canon's stated scope doesn't actually cover the case (canon defect → fix canon), or when a rule's scope is genuinely unclear (rule-clarity gap → fix rule). Most "Tier 2 needs your judgment" items are actually Tier 1 mechanical fixes I was hesitant to apply.

---

### 2026-04-25 (later) — Meta-correction: judgment-handoff smuggling caught + tightening applied + Matt 25:42a / Acts 16:31 / Luke 8:50 / Jas 4:7 merges

Within minutes of committing the §3.7 retirement (`6b741fe`), Phase B reasoning produced the exact failure mode the retirement targeted: invoking "soteriological weight," "pastoral comfort," "narrative climax," and "prosodic emphasis" as adjudication categories for splits at Acts 16:31, Luke 8:50, and Jas 4:7. Stan caught it directly: *"soteriological climax... gibberish that contradicts the colometry document."*

**Three parallel hostile meta-audits** dispatched on the failure:
- AUDIT A (cognitive/process): root cause = pre-commit self-test scoped to canon-file edits, not session-folder analysis docs; Phase B framing as "decision points for Stan's judgment" let weight-based reasoning reach the page without the discipline ever firing. Pattern named: **"judgment-handoff smuggling"** — sub-shape of named-category carve-out, distinguished by the handoff verb ("Stan's call," "warrant," "open question") doing the work that "named category" does in the parent pattern. R28 framework drift mid-document — silently slid from "is asymmetry textual?" to "is asymmetry weight-justified?" — re-instantiating retired §3.7 logic under new labels (reclassification by stealth).
- AUDIT B (tightening proposals): rejected 4 of 8 candidates as rule-multiplication; accepted 3 — extend canon §1 line 200 vocabulary watchlist (T5); add judgment-handoff smuggling sub-pattern to `feedback_rhetoric_bandwagon.md` (T3); add first GNT-native catch entry (T4).
- AUDIT C (session sweep): contamination confined to Phase B findings document's bridging/forwarding paragraphs (Tier 2/4 + line 118 + line 120-122). Canon §9, canon §10, Tier 1 commit body (`358657b`), yesterday's import commit (`2501e48`), and the §3.7 retirement reasoning itself are clean. Note: the §3.7 retirement audit chain itself contained a small conflation — Audit 1 treated R28 as protecting the Matt 25:42a split (it does not; R28 protects only the genuine compression at 25:43c "ἀσθενὴς καὶ ἐν φυλακῇ καὶ οὐκ ἐπεσκέψασθέ με" where two state-conditions are covered by one response verb).

**Codified (this commit):**

1. **§1 line 200 vocabulary watchlist extended.** Added theological-weight, soteriological-significance, pastoral-force, narrative-climax, prosodic-emphasis, doctrinal-stakes, and "any analogous non-grammatical category" to the disallowed-tiebreaker list. Closes the actual vocabulary gap that let yesterday's reasoning through.

2. **Memory `feedback_rhetoric_bandwagon.md`**: new "judgment-handoff smuggling sub-pattern" section + first GNT-native entry in catches training set documenting the 2026-04-25 "soteriological climax" catch with specific traps that produced it.

3. **Phase B findings document annotated** at top with contamination notice. Document preserved for the reasoning trail; contaminated sections marked as record-of-failure-mode rather than load-bearing analysis.

**Corpus merges applied as Tier 1 mechanical-default corrections (not "decisions"):**

- **Matt 25:42a**: `ἐπείνασα γὰρ / καὶ οὐκ ἐδώκατέ μοι φαγεῖν` merged to one line. R28 mechanical test — counts identical to Matt 25:35a (1 state verb + 1 negated response verb = 2 finite verbs). No authorial asymmetry. R28 protects only 25:43c (the genuine sick+prison-under-one-verb compression), not 25:42a.
- **Acts 16:31**: `Πίστευσον ἐπὶ τὸν κύριον Ἰησοῦν, καὶ σωθήσῃ σὺ καὶ ὁ οἶκός σου.` merged. Same author (Luke) merges similar imperative+καί+response constructions consistently in Luke 6:37 ×3, 11:9 ×3, 6:38, 10:28. Same-author consistency under M1 strict-application caveat + R8 short-line default.
- **Luke 8:50**: `Μὴ φοβοῦ, μόνον πίστευσον, καὶ σωθήσεται.` merged. Same Luke-author consistency.
- **Jas 4:7 second split**: `ἀντίστητε δὲ τῷ διαβόλῳ, καὶ φεύξεται ἀφʼ ὑμῶν·` merged. First split at the contrastive δέ pivot (`ὑποτάγητε / ἀντίστητε δέ`) stays — that is grammatical. Same-chapter same-author consistency with Jas 4:8 + Jas 4:10 (both merged 1-line imperative+καί+response constructions).

**Cascade outcomes:** regen Matt + Luke + Acts + Jas (4 verses redistributed). Three manual fixes required after regen due to proportional-heuristic redistribution failures: Matt 25:42 English content scrambled (rewrote 2 lines clean); Luke 8:50 English orphaned "Do" at line-end (rewrote to mirror 2-line Greek); Luke 6:25 collateral damage (regen deleted "Woe" from line 127 — restored). HTML rebuilt for all 4 books. `verify_word_order.py`: 0 discrepancies across 27 books. `check_cascade_alignment.py`: 3 warnings (the known stable construction FPs).

**Defensibility capture:**
- WHY: a discipline that fires only on canon-file commits cannot catch failure modes embedded in session-folder analysis documents that recommend corpus actions. The vocabulary-watchlist extension closes the gap by making the prohibited reasoning recognizable wherever it appears (canon, analysis, recommendation, post-hoc rationale).
- HOW WE KNOW: 3 parallel Opus hostile meta-audits with full text-citation evidence; corpus merges grounded in R28-mechanical or M1-caveat + R8-default reasoning explicitly free of weight-based vocabulary.
- SCOPE: tightening targets a behavioral failure-shape (judgment-handoff smuggling) and a vocabulary gap; does NOT promote audit machinery to all corpus decisions or to all editorial outputs (audit B explicitly rejected that as scope creep).

---

### 2026-04-25 — Three §3.7 subsections retired after first retroactive audit application

First exercise of the §6.5 mandatory-audit trigger list (codified yesterday from BofM cross-project import). Stan asked whether anything in the existing canon warranted retroactive review under the new discipline; the §3.7 subsection burst from 2026-04-21 (Need/Response Paired Beats, Imperative + Divine-Consequence, Cause-Consequence Bonded Beats) was identified as the strongest shape-match for triggers #1 (new sub-clauses) + #7 (corpus-sweep evidence missing) + #8 (canonical example additions).

**Three parallel Opus hostile audits dispatched** — one per subsection, each running a full-corpus sweep against the rule's diagnostic. All three failed:

- Need/Response: ZERO non-Matt-25 instances; rule was a single pericope masquerading as general principle. Plus direct contradiction with §R28 on Matt 25:42.
- Imperative + Divine-Consequence: 8 documented counterexample splits; ~50% actual merge rate. Rule was codified from a Luke-only set without sweeping Matt 7:7 — the Q-source parallel that splits.
- Cause-Consequence: removal test is a feel-test; literal application would force ~100-300 corpus merges Stan does not want.

**Decision: retire all three (Option 1, full retirement)** rather than demote-to-worked-examples (Option 2). Stan's reasoning: rules that don't earn their place go; canon parsimony > per-verse documentation; §10 Update Log + git history + §9 Superseded Formulations preserve the reasoning trail. Retiring cleanly establishes that the audit discipline applies to its own outputs without exception — the first retroactive application is the precedent for all future ones.

**Edits this commit:**

- **§3.7**: deleted three subsection blocks (lines 748-812 in pre-edit state). Replaced with a note pointing to §9 retirement entry.
- **§2 M1 strict-application caveat**: removed the three §3.7 cross-references from the merge-protections checklist; added R8 default + R28 in their place.
- **§9 Superseded Formulations**: new entry "Three §3.7 Subsections Retired (2026-04-25)" with full audit findings + corpus-consequence note + open-question forwarding.
- **§10 Update Log**: this entry.

**Live corpus consequence**: none. Every canonical merge that the retired rules protected (Luke 6:37 ×3, Luke 11:9 ×3, Luke 6:38, Luke 10:28, Jas 4:8, 1 John 5:16, John 6:49, John 10:12, Matt 25:35-36 fivefold) stays merged under M1 + R8 + R28. The retirement is documentary, not prescriptive.

**Open question forwarded (Phase B of this session)**: 8 imperative+divine-consequence splits + the Matt 7:7 vs Luke 11:9 Q-source asymmetry are flagged as `application_consistency_vs_rule_coverage` candidates. Each needs R28 mechanical analysis (count finite verbs / elided verbs / predicative heads in each parallel passage) to determine whether the asymmetry is authorial (preserve — potentially publishable as colometric evidence of authorial choice) or editorial (correct one to match the other). Phase B work in this session.

**Defensibility capture:**
- WHY: rules that fail the discipline standard go to §9; the alternative (keeping them around as worked examples) is the zombie-rule failure mode the new audit discipline targets.
- HOW WE KNOW: 3 parallel Opus hostile audits with full-corpus sweeps + file:line citations; audit reports archived in session folder.
- SCOPE: §3.7 only; other rules retain their current status.

---

### 2026-04-24 — Pre-commit adversarial-audit discipline imported from BofM (§3 diagnostic + §6.5 trigger list + CLAUDE.md self-test + memory consolidation)

Cross-project import from BofM's 2026-04-23 canon tightening (BofM commits `cc555b8`, `1357a62`). BofM codified a systematic adversarial-audit discipline after 5 fake-rule catches in one session (Stab-commata register, doctrinal-weight Category-B bump, EP-6 Exception/Save, 1 Ne 19:5 reclass attempt, R28 reverse). Per BofM canon §7.3 item 11, cross-project imports require adversarial audit independent of source.

**Audit discipline applied to this import.** Three parallel Opus hostile audits dispatched 2026-04-24 AM:
- **Necessity audit**: does GNT have the failure modes the imports catch? Verdict: GNT's recent codifications do not cleanly shape-match BofM's 5 catches; but GNT's §3.7 subsection burst (Need/Response + Imperative + Divine-Consequence + Cause-Consequence, 2026-04-21) and gold-standard 4-chapter list (2026-04-22) lack full-corpus sweep provenance by BofM §7.3 trigger-#7 standards. Import is prospective discipline, not retroactive catch. CONFIDENCE: MEDIUM.
- **Redundancy audit**: for each of 4 candidates (§7.3 trigger list, §2 diagnostic, CLAUDE.md self-test, `feedback_rhetoric_bandwagon` extensions), is there GNT discipline that duplicates? Verdict: #1 and #2 COMPLEMENTARY (clean imports); #3 and #4 PARTIAL-OVERLAP (consolidate into existing GNT infrastructure rather than add standalone).
- **Framework-mismatch audit**: do BofM's §§2/7/8 references port? Verdict: NO — GNT §2 is "Unless Conditions" (not Autonomy Boundary), GNT §7 is RETIRED, GNT §8 is "Greek-Specific Application" (update log is §10). All §2/§7/§8 refs in imports must retarget. Recommended §6.5 placement for trigger list (between Defensibility capture and v4 methodology subsections). CLAUDE.md section between "Rule-Derivative vs. Ad-Hoc" and "Build Pipeline". Strip BofM-specific named examples (1 Ne 19:5, Gap 1-A, EP-6, Stab-commata, Mosiah 18:7, etc.).

**Codified (this commit):**

1. **§3 Autonomy Boundary — scope/precedence/closed-list/carve-out diagnostic.** Canon additions that include a scope claim, precedence claim, closed-list extension, or named-category carve-out default to Category B regardless of commit-message framing. Catches the "self-framed as documenting practice" failure mode. Cross-references §6.5 for the audit mechanism.

2. **§6 Precedent and Scope — new §6.5 "Mandatory-audit triggers for canon changes".** Enumerates 11 mandatory-audit triggers (new rules/sub-clauses, status promotions, spot-check proposals, B/C reclassifications, rule deletions, validator changes, sweeps ≥5, canonical example additions, meta-rule changes, discipline-shifting memory additions, cross-project imports). Audit-skippable catalog named explicitly. Parallelization default (independent audits dispatched in one message). Relationship to CLAUDE.md self-consistency audit trigger stated (pre-commit vs session-rollup, distinct mechanisms).

3. **CLAUDE.md — new "Pre-commit adversarial-audit discipline" section.** 3-question self-test (scope/precedence/closed-list/carve-out | spot-check evidence | reclassification/deletion of settled canon). Placed between "Rule-Derivative vs. Ad-Hoc Changes" and "Build Pipeline". Explicit cross-refs to §3 diagnostic and §6.5 trigger list. Explicit distinction from the existing Session-bookend self-consistency trigger (both coexist).

4. **Memory `feedback_rhetoric_bandwagon.md` extended.** Two new sub-patterns merged with existing external-rhetoric content: (a) named-category carve-out — the rhetoric-bandwagon failure mode applied to internally-invented categories (not just externally imported ones); (b) biased-spot-check — full-corpus sweep required before codification, spot-check confirmation alone is insufficient. BofM's 5-catches training set cited as sibling reference; GNT builds its own catches list as failures occur. Operational 3-question discipline mirrors CLAUDE.md.

**What was NOT imported and why:**
- **BofM §1 Application Order step-by-step (Step 0-4).** BofM generated this from 4 parallel structural audits on its own rule set. GNT would need its own structural audit before porting. Deferred as a future investigation; not necessary for the audit-discipline tightening.
- **BofM N=2 Adjudication Principle (cross-cutting).** Precipitating case was BofM Alma 24:10 compound-verb under shared auxiliary; GNT's M1 strict-application caveat (2026-04-21) already covers the corresponding GNT ground. Principle likely redundant for GNT; skip until a GNT corpus case surfaces the gap.
- **BofM-specific named examples in the trigger list and §8 entries.** Stripped per framework-mismatch audit.
- **BofM `feedback_agent_sweep_filter.md` (level/provenance/redundancy filter).** GNT has `feedback_adversarial_agent_drift.md` covering a related but distinct failure mode (hostile-audit genre-group drift). Not duplicated.

**Reference breakage checked:** all "§2" references in imported material retargeted to "§3" (GNT Autonomy Boundary); all "§7 Change Protocol" self-references retargeted to "§6.5"; all "§8" references retargeted to "§10 Update Log"; "pending.md" references retargeted to session-folder pending lists.

**Files touched:** `private/01-method/colometry-canon.md` (§3 + §6 + §10), `CLAUDE.md` (new section), `C:/Users/bibleman/.claude/projects/c--Users-bibleman-repos-readers-gnt/memory/feedback_rhetoric_bandwagon.md` (extended).

**Defensibility capture:**
- **WHY**: prospective prevention of under-sweep-before-codification and self-framed-as-documentation-but-actually-precedence-claim failure modes; GNT's §3.7 burst and gold-standard list are the relevant exposure.
- **HOW WE KNOW**: 3 parallel hostile audits (necessity/redundancy/framework) dispatched 2026-04-24 before codification; audit findings recorded above.
- **SCOPE**: applies to all future canon commits; pre-commit per-change (§6.5 / CLAUDE.md self-test) and session-rollup (existing ≥2-codifications self-consistency trigger) are distinct mechanisms that coexist.

---

### 2026-04-22 (later²) — Tier 2/4/5 sweep codifications (2 canon + 4 memory + 1 CLAUDE.md)

Continuation of 2026-04-22's hidden-decision-point sweep. After Tier 1
(prevent-misapplication) codifications landed, Tiers 2-5 triaged:

**Canon additions (§6 Precedent and Scope):**
- **Defensibility capture for new canon additions** — WHY / HOW WE KNOW /
  SCOPE triplet required for new subsections/rule revisions. Prospective
  from 2026-04-22; retroactive audit deferred.
- **v4 as methodology application** — reproducibility-regimes
  distinction (v0-v3 bit-exact; v4 methodologically auditable). Matters
  for external review and PhD prospectus framing.

**Memory installs** (not committed — outside git):
- `feedback_scripts_before_agents.md` — script-first for mechanical sweeps.
- `feedback_commit_format_mechanical.md` — mass-edit commit body format.
- `feedback_check_existing_tooling.md` — MorphGNT/validator/Layer 1 check
  before building new scanners.
- `project_substrate_stable_api.md` — v4-editorial as read-only API for
  analytical tools (fork-don't-enrich).

**CLAUDE.md** (session bookend):
- Canon self-consistency audit trigger — after ≥2 canon codifications,
  light-touch audit before WRAP-UP.

**Skipped as obsolete or over-structure:**
- Mechanical-merge 5-step pattern (covered by existing parallelize memory)
- Three-quality signature + verdict-render (overseer-era artifact)
- 17-agent cross-lens wave architecture (overseer-era)

**Tier 3 items (forgotten carry-forwards) resolved by corpus inspection:**
- 4 atomic-attribute candidates (Luke 2:36, Acts 9:36, 16:1, 16:14) — all
  currently show clean attribute-per-line structure. Implicitly resolved.
- John 6:22 (εἶδον + two ὅτι) — current state follows R10 properly.
  Implicitly resolved.

**Tier 3 items flagged for Stan** (deferred; require authorization):
- 21 REVIEW correlatives from 04-15 `scan_correlative_stacking.py`
- Track B AMBIGUOUS re-audit from 04-16
- Stylometry re-run (trigger condition may now be met)

---

### 2026-04-22 (later) — Tier 1 sweep codifications (2 canon + 4 memory)

Triggered by Stan's concern that other established conventions may be hiding
undocumented. Four parallel sweeps (handoffs / session-notes / git-log /
retired-docs) identified ~25 items across 5 tiers. Tier 1 items (prevent
future misapplication) applied:

- **Canon §3.6 Amen-formula subsection** — ἀμήν [ἀμήν] λέγω σοι/ὑμῖν
  gets its own line; content breaks to next line. Applied to 15 corpus
  instances in commit c51faf8 (2026-04) but never codified. A future
  adversarial sweep could have re-jammed.
- **Canon §4 Post-Split Function-Word Recheck** — mandatory after any
  mass-split pass; Mark 4 / Rom 2:12-13 / Acts 1:1-4 / Heb 1:3 as gold-
  standard regression-test chapters for pipeline changes.
- Memory installs (not committed — outside git):
  `feedback_regen_force_destructive.md`, `feedback_two_phase_pipeline.md`,
  `feedback_two_check_cascade.md`, `project_known_gloss_drift.md`.

Tiers 2-5 pending Stan triage.

---

### 2026-04-22 — Canon §3.17: Cross-Verse Continuity Merge codified

The convention was already in practice (18 Greek + 18 English instances in
the corpus) and documented in `handoffs/04-editorial-workflow.md` §"Cross-
verse continuity" and `handoffs/03-architecture.md` §"Source format
convention". Promoted to canon on 2026-04-22 after Stan flagged the gap
(John 4:35 `ἤδη` decision was stuck on "do we move words across verse
boundaries?" with no canon answer to point at).

The rule: sense-lines follow grammatical/rhetorical structure; when they
cross a Stephanus 1551 verse boundary, the sense-line stays intact in the
earlier verse's block and an inline superscript (`²`/`³⁶`/`⁴`/...) carries
the versification reference. Mirrors the Nestle-Aland typographic
convention ported down to the colometric-line level.

Applied same day: John 4:35/4:36 (`ἤδη` pattern — SBLGNT-back / R8-forward)
and 1 Cor 14:5 (`μείζων` — within-verse R8 restructure, not cross-verse).

---

### 2026-04-21 (later²) — M1 tie-breaker strict-application caveat

Added as a paragraph appended to the M1 tie-breaker block in Section 2.
"M1 rejection does not license split": when the different-domain tie-breaker
fires and withdraws gorgianic protection, check the other merge levees (M2,
M3, M4, R11, the three §3.7 bonded-beat patterns, default-merge) before
flipping to split.

Motivation: today's reverse-drift round-2 pass showed the John agent flipped
6 items under strict M1 rejection, while the Synoptic agents saw structurally
similar pairs and affirmed them. Cross-genre inconsistency traced to
treating M1 failure as sufficient for split rather than as a signal to check
other protections. Codifying this caveat prevents future adversarial passes
from repeating the drift.

No corpus edits.

---

### 2026-04-21 (later) — Canon codification: Cause-Consequence Bonded Beats

Surfaced by today's reverse-drift round-2 adversarial pass on 318 KEEP_MERGED
verdicts. Two Johannine N=2 cross-domain pairs resisted splitting despite
failing M1's same-domain tie-breaker:

- John 6:49 `ἔφαγον... τὸ μάννα καὶ ἀπέθανον` (eating + mortal consequence)
- John 10:12 `θεωρεῖ τὸν λύκον ἐρχόμενον καὶ ἀφίησιν τὰ πρόβατα` (perception +
  cowardly response)

Both are causally bonded — member 2 is the direct consequence of member 1 AND
the rhetorical point of mentioning member 1. The removal test diagnoses the
bond: remove member 2, member 1 loses its reason for being mentioned.

Added as §3.7 subsection. Canon family: M1 gorgianic-pair, R11 synonymous-
doublet imperative, Need/Response (Matt 25), Divine-Consequence (Luke 6:37),
and now Cause-Consequence Bonded Beats (John 6:49, 10:12). All share the
generating principle: **N=2 coordinate members with unified rhetorical force
stay on one line** — extended to cover cross-domain causal bonds.

No corpus edits (these two verses were already correctly merged in
v4-editorial; adding the canon protection prevents future adversarial flips
from over-applying the M1 tie-breaker).

---

### 2026-04-21 — Canon codification: need/response + divine-consequence patterns

Surfaced by today's triage of the 51 deferred reverse-drift candidates from
2026-04-18. The triage found that 17 of 51 "split candidates" were actually
instances of two recurring rhetorical patterns that the canon didn't name:

1. **Need/Response class** (Matt 25 fivefold positive + inversion, 7 instances)
2. **Divine-Consequence class** (Luke 6:37, 11:9, Jas 4:8, 1 John 5:16, etc., 10 instances)

Both are "N=2 coordinate members with unified rhetorical force stay merged"
patterns — same generating principle as M1 gorgianic-pair and R11 synonymous-
doublet imperative. Added as §3.7 subsections with canonical cases, diagnostics,
and relation to R12.

No corpus edits (the 17 candidates were already correctly merged in v4-editorial;
the scanner was over-flagging). This closes a canon gap revealed by the FP
analysis.

---

### 2026-04-20 (later⁷) — ὅτι-leads convention codified

Corpus has been 834:0 ὅτι-leading post the 2026-04-18 corrective flip
(176 Greek + 19 English). Codified in §3.5 as "ὅτι Placement
Convention — Leads Its Complement" so a future sweep without corpus
inspection can't reintroduce the trailing pattern.

Grammatical warrant: ὅτι is a complementizer; it introduces its clause.
Line-end ὅτι severs the complementizer from the clause it governs.
Standard Koine grammar (BDF §416, Smyth §2017, Wallace) describes ὅτι
as introducing its complement.

No corpus edits — convention was already universal; this closes a canon
gap flagged in the 2026-04-18 carry-forwards.

---

### 2026-04-20 (later⁶) — R11 round 4: parenthetical mid-speech attribution codified

Triggered by the 2 remaining R11 REVIEW-REQUIRED items (John 18:4, Acts 25:22)
after round 3 (commit 16ea854). Per Stan's decision, this pattern gets
canon-codified rather than per-item reviewed, matching the OT-attribution
treatment.

Canon addition:
- §3.6 new subsection "Parenthetical Mid-Speech Attribution" codifying that
  speech verbs (typically φησίν) interjected mid-quote as attribution tags
  stay merged with surrounding quoted content. Canonical cases: Matt 14:8,
  Acts 25:22.

Validator update (R11 round 4):
- F5 filter upgraded from REVIEW-REQUIRED downgrade to full filter.

Post-refinement R11 count: 0. Both former F5 REVIEW items filtered cleanly:
Acts 25:22 via F5 (φησίν flanked by commas confirmed). John 18:4 also
filtered by F5 — the _is_parenthetical_attribution function covered it.

No v4-editorial text changes.

---

### 2026-04-20 (later⁵) — R11 round 3 + OT-attribution canon codification

Triggered by today's R11 mass-apply triage finding 7 held FPs + 20 REVIEW-REQUIRED
OT-attribution items. Stan's decision: OT-attribution is canon-level, not per-item
review.

Canon additions:
- §3.6 new subsection "OT-Attribution Tags Inside Quotation Blocks" codifying that
  speech verbs inside already-opened quotation blocks (λέγει κύριος, λέγει τὸ
  πνεῦμα, post-positioned φησίν) stay merged as attribution tags, not fresh
  speech-intros. Canonical cases: Rev 2-3 seven letters, Pauline OT citations,
  Hebrews 8, Acts 7.

Validator updates (R11 round 3):
- Class B (OT attribution) upgraded from REVIEW-REQUIRED downgrade to full filter.
- F4 (speech verb inside already-opened quote) upgraded to full filter.
- F6: added ὅσα/ὅσοι/ὅσον and variants to _SUBORDINATORS (fixes John 10:41, Acts 4:23).
- F7: post-positioned attribution tag filter (fixes Luke 7:40, Acts 23:35, Heb 8:5).
- F8: narrative explanatory comment filter (fixes John 21:19 line 84).
- F9: descriptive speech-as-behavior comment filter (fixes Matt 23:3).

Post-refinement R11 count: 2 total candidates (down from 27 post-round-2). Both
remaining are REVIEW-REQUIRED via F5 (parenthetical mid-speech attribution):
John 18:4 and Acts 25:22. These are the final residue for Stan's review.

No v4-editorial text changes. No corpus sweep needed — the 20+ OT-attribution
lines were already correctly merged in the corpus; the validator was over-flagging.

F5 (parenthetical mid-speech attribution, Matt 14:8 class) retained as
REVIEW-REQUIRED since canon hasn't resolved that specific pattern.

### 2026-04-20 (later⁴) — H4: Three-Layer Architectural Statement in Canon Opening

Added `## Architecture` section between `## Posture` and the `How to use this document` block, making the Layer 1 / Layer 2 / Layer 3 architecture explicit up-front. Matches the BofM sibling canon's v2.0 opening and closes H4 from today's cross-canon alignment audit.

Layer 1 (generic Koine break-legality) points to `data/syntax-reference/greek-break-legality.md` — the R2–R7 migration landed 2026-04-20 in the foundational-reframing commit but wasn't yet announced in the canon's opening. Now explicit.

Layer 2 (validators) honestly marked as "under active build 2026-04-20" — directory split `validators/syntax/` + `validators/colometry/` is the target shape; MVP is being built in parallel this session (see session folder).

Layer 3 (this canon) positioned as the editorial-delta surface where we diverge from or add to generic Koine syntax to reveal atomic thought.

Also: "How to use this document" block gains a pointer to Layer 1 + Layer 2 locations so a Claude reading the canon cold learns where the layers live.

No colometric output changes. Pure documentation — architecture made visible at the top of the canon rather than implicit through §3.2's Layer 1 pointer.

---

### 2026-04-20 (later³) — H3: Breath Criterion Retired

Empirical justification: 4 parallel agents tested whether breath was ever the sole deciding factor on any line break across (a) today's 2.2MB full-transcript, (b) sessions 2026-04-12 to 2026-04-13, (c) sessions 2026-04-14 to 2026-04-18, (d) canon update log + retired overseer + archives. Total: 0 STRONG hits, 18 MEDIUM hits (all with breath alongside other forces where removing breath would not flip the decision), ~98 WEAK hits, 2 NULL hits.

Canon log history shows a 12-day empirical retreat: entered 2026-04-09 as full criterion with no threshold, flagged leaky in session 9 (2026-04-12), had its problems solved by syntax rules in session 10 (2026-04-13) rather than by any breath-based mechanism, progressively demoted across sessions 10–18, landed 2026-04-20 as "sanity check only / status under review" — and now retired entirely.

Pauline-specific check (the amanuensis-dictation hesitation): only two MEDIUM hits in Pauline material (Phil 4:1 and 2 Cor 10); in 2 Cor 10 the canon explicitly states cognitive hierarchy overrides breath. The amanuensis argument gave breath its best chance at being load-bearing, and the empirical record is that even in Paul, breath never decided a break.

Cognitive-chunking work breath was informally doing is now absorbed by structural justification #5 (substantive adjunct as own focus, added 2026-04-20 via H2). With that in place, breath has no remaining independent work.

Changes:
- §1 "Breath — Status Under Review" subsection replaced with short "Breath — Retired 2026-04-20" note.
- Framework in Practice ASCII box simplified from 4 lines (3 forces + breath sanity) to 3 (three forces cleanly).
- Priority Order subsection opening updated to remove "breath sanity check" reference.

Test evidence lives at `private/03-sessions/2026-04-20-foundational-reframing-and-layer-1/breath-empirical-test-{A,B,C,D}.md`.

Sibling project (BofM) retired breath 2026-04-19 on parallel reasoning. GNT now aligned.

No editorial output changes. No v4-editorial text touched.

### 2026-04-09 — Initial Methodology Document

- Foundation created with core premise, dictation hypothesis, scope boundary, four criteria, container-not-originator principle
- Greek-specific break points drafted (main clauses, subordinate clauses, participial phrases, direct speech, parallel stacking, men/de, gar)
- Two test chapters hand-formatted (Mark 4, Acts 17)
- Auto-formatter built and run on all 260 chapters
- Known limitations documented
- Hand-crafted test chapters overwritten by auto-formatter (preserved in git history)

### 2026-04-09 (session 2) — Four-Tier Pipeline

- Pipeline designed: Tier 1 (pattern-matching), Tier 2 (Macula syntax trees), Tier 3 (rhetorical patterns), Tier 4 (editorial hand)
- Macula Greek and MorphGNT integrated
- v2/v3 output generated for all 260 chapters
- Mark 4 v3 validated against gold standard
- Scholarly grounding section added (Wallace, Marschall, Lee & Scott, Nasselqvist)
- Bezae comparison: 59.7% -> 60.6% -> 60.7% across tiers

### 2026-04-09 (session 2, continued) — Principled Rules in v3

- Infinitive merge-back rule added
- Verbless line merge rule added
- The criteria chain documented
- Bezae caveat recorded (physical layout constraints)

### 2026-04-09 (session 3) — Exegetical Hot Spots

- Seven hot spots documented: John 1:3-4, Rom 9:5, Eph 1:4-5, 1 Tim 3:16, Phil 2:6-8, 1 Cor 15:3-5, Col 1:15-17
- YLT English validation layer integrated
- Unified predication test using Macula tree walk
- Verb valency majority threshold (50%)
- Sentence boundary detection as hard constraint (1,298 splits)
- Sub-clause splitting at Macula word-group boundaries (~1,100 splits)
- Post-split safety guards (genitive articles, negations, possessives, postpositives)
- Corpus health: 0 lines >120 chars; Bezae agreement 61.3%

### 2026-04-11 — Cross-Pollination from Parallel Corpus Project

- FEF framework adapted for Greek (periodic sentences with participial suspension)
- Three-category framework (A/B/C) formalized
- Framing devices unified as a principle
- Idou three-type distinction ported (status: unsettled)
- Syntactic bond rules expanded (periphrastic construction, negation)
- Qualifying phrases: escalation vs. restriction adapted
- Hoti cataphoric/anaphoric distinction ported
- Authorial style principle codified
- Scanner backlog item: parallel diagnostic scanner

### 2026-04-11 — Acts 1 Editorial Pass

- Lukan periodic style confirmed as FEF
- Epistolary/narrative genre shift visible in colometry
- Standalone verb test refined
- Elaborative apposition merges
- Geographic expansion stacking (Acts 1:8)
- Short genitive absolute merging confirmed

### 2026-04-12 (session 9) — Container-Not-Originator, Vocative, No-Anchor

- Container-not-originator established as unifying principle
- Thought-marking vs. structural syntax distinction codified
- Vocative rule refined from universal to apposition-aware (125 merges)
- No-anchor rule established and applied (860 merges)
- Rom 7:14-8:8 nomos-stack harmonization
- Leaky areas identified: breath unit, cross-verse dependencies, structural-syntax enforcement

### 2026-04-13 (session 10) — The Goldilocks Refinement

- Container-not-originator restricted to subordinating syntax only
- Three new corpus-wide classes: PARTICIPIAL-CHAIN-COLLAPSE, PREP-CATENA-ABSORPTION, SUSPENDED-SUBJECT-WITHOUT-PREDICATE
- Eight parallel scanning agents across genre groups
- ~120 high-confidence splits applied
- Cross-agent convergences validated (Heb 1:3 from both directions, Eucharistic institution across synoptics)

### 2026-04-13 (second entry) — Criterion Priority and Compound Lists

- Chunking > oral > rhetorical priority explicitly codified
- Semantic grouping principle for compound lists
- Period test as concrete diagnostic for obligatory-vs-optional complements
- Negative result on verb-identity rules recorded

### 2026-04-13 (session 12) — Marschall Posture and Cognitive-Grounding Test

- Marschall 2024 monograph received and analyzed
- 2 Cor 11:25-27 convergence confirmed
- Cognitive-grounding test established as binding constraint on future rule adoption
- Selective adoption framework: what to adopt, what not to adopt
- Marschall positioned as validation benchmark, not theoretical authority
- Prospectus framing: dictation-hypothesis advantage over periodic-style framework

### 2026-04-14 (session 13) — Register Operationalization

- Six registers named with local signatures and rule modulations
- Camera angle change confirmed as editor-facing teaching language
- Register is modulation layer, not rule-multiplication
- Compositional-mode-conditional hierarchy flagged for future empirical testing

### 2026-04-15 — Atomic-Attribute Pattern, Speech-Intro Merger, hoti Rule, Corpus Sweeps

- Atomic-attribute portrait pattern codified (Acts 10:1-3, Pauline salutations, Heb 1:3-4)
- Temporal-clause speech-intro merger (Heb 1:6 canonical case)
- Section 2a hoti rule established: cognition verbs merge, speech verbs split
- De-contrast overbreak: 27 splits
- Orphaned adverbial completion: 15 merges
- Vocative sweep continuation
- Correlative pair treatment codified with distinct-predicate test

### 2026-04-16 — Hierarchy Reframe: Default + Unless

- Criterion 1 reframed from predication-only to "default + two-prong exception test"
- Four structural justifications established as closed list
- No-anchor rule connected to the two-prong exception test
- Atomic-attribute pattern reframed from exception to codified "unless" case
- Duplicate section 6b flagged
- Section 2a vs. verb-identity negative result resolved
- Parallel update made to sibling project canon
- No-anchor rule participle scope tightened: "standing as predicate"
- Class P completing-predication test ported with Greek examples
- "Imposing vs. revealing" stated as standalone doctrine

### 2026-04-18 — Canon Consolidation: Six Rules Retired

Adversarial audit by three Opus agents (over-structuring / redundancy / mechanical-triggerability) converged on six rule numbers as redundant, folded, or pointer-only. Retired: R15 (folded into R14 parallel-structures framework), R16 (folded into R8's framing-devices table), R21 (absorbed as operational mechanism for R12/R13/R14), R25 (folded into R11 as speech-intro frame aggregation), R26 (pure M2 restatement — deleted), R29 (pointer-only — deleted). Rule count: 29 → 23 (R1–R29 with gaps). M1–M4 unchanged. Section 9 carries the retirement documentation. No colometric output changes; canon parsimony, not methodology revision. Also: first rule-application validator `scripts/validate_r18_vocative.py` added — tests R18 compliance by morphology + position, not shape-pattern match. 11 candidates corpus-wide vs. 209 from the superseded shape detector.

### 2026-04-20 (later²) — H2: Fifth Structural Justification — Substantive Adjunct as Own Focus

Added "Substantive Adjunct as Own Focus" as structural justification #5 in §2, matching BofM's 2026-04-19 PM addition. Justification #5 is the generative principle that R19 (gen abs always own line), prep-catena absorption (§8), and the FEF periodic-frame treatment all derive from.

This is a unification move, not an addition of editorial behavior. Three existing rules that previously presented as independent syntactic rules are now surfaced as mechanical operationalizations of one generating principle: a fronted or trailing adjunct that is (a) grammatically peripheral to the matrix + (b) carries substantial semantic content earns its own line.

Worked examples differ from BofM (gen abs, prep catena, FEF periodic frame for Greek; Alma 52:18 year-formula for BofM), but the principle is the same. Canonical Greek cases: Acts 1:9 genitive-absolute camera shift; 2 Cor 6:4-7 ἐν-catena; Luke 3:1-2 periodic temporal chain; John 1:1 ἐν ἀρχῇ as edge-case short-but-substantive adjunct.

Also: justification #5 absorbs the cognitive-chunking work that breath was informally doing (long lines need breaking) but with a principled grammatical-peripherality test rather than an un-thresholded "feels too long" judgment. This prefigures the H3 decision on whether breath itself can now be retired.

Affected sections: §1 list of five justifications under Force 1 (Generative); §2 new #5 subsection; §2 Merge-Override intro ("five split-triggers"); §2 Complete Framework ("five split-triggers and four merge-overrides"); §4 Two-Prong Exception Test ("one of the five structural justifications"); section heading "The Four Structural Justifications" → "The Five Structural Justifications" with regenerating-principle text rewritten.

No editorial output changes.

### 2026-04-20 (later) — H1: Three-Forces Reframe of §1

Triggered by cross-canon alignment audit (see `private/03-sessions/2026-04-20-foundational-reframing-and-layer-1/cross-canon-audit.md`). §1 rewritten from "Four Criteria hierarchy with syntax as servant" to "Three Forces: propositions (generative) / syntax (subtractive) / image (diagnostic)." This aligns GNT with BofM's 2026-04-19 framework reframing.

Key changes:
- Section retitled "The Framework" (was "The Hierarchy").
- Explicit "Mission and Method — Discipline Framing" subsection added: mission is sense-driven, method is syntax-constrained, with the BofM hedge verbatim ("syntactic violation is fatal while sense ambiguity is recoverable within the permitted space"). Mission-primacy is preserved; method leads with the subtractive force.
- Four Criteria replaced with Three Forces. Atomic thought → Generative (propositions). Image → Diagnostic. Syntax → Subtractive (explicit three closed-list veto classes: Layer 1 break-legality, complement integrity, formula integrity). Merge-override framework M1-M4 explicitly named as additional subtractive cases.
- Container-not-originator principle retained (GNT-unique value). "Consequences for the framework" list rewritten to describe the three-forces architecture.
- "Thought-marking syntax vs. structural syntax" distinction retained, re-anchored as how propositions announce themselves to the generative force.
- "Hierarchy in Practice" ASCII box replaced with "Framework in Practice" three-force summary.

H3 (breath retirement) not yet decided. Breath demoted to "status under review — sanity check only, not a force in the framework." Empirical test pending: has breath ever been the deciding factor on any line break across 260 hand-edited chapters?

No editorial output changes. No v4-editorial text touched. Pure methodology-framing refactor. Rules, merge-overrides, and structural justifications operationally unchanged.

### 2026-04-20 — Foundational Reframing and Scholarly-Framing Retirement

Triggered by Stan's clarification that the project's intellectual foundation is (a) Stan's own premise — *humans think, compose, and deconstruct (read/hear) in sense-lines* — and (b) Skousen's precedent that sense-line reduction is possible, demonstrated on the Book of Mormon, extended to the GNT by analogy. Chafe / Kintsch / Daneman & Carpenter / Miller-Cowan / Marschall / dictation-hypothesis-as-methodological-frame were treated as *load-bearing cognitive grounding* by the pre-2026-04-20 canon. They are not. They are at most opportunistic convergences, noted where they happen, never load-bearing.

Changes:
- **Added foundational-premise block + posture block** at the top of the canon, stating Stan's premise explicitly and crediting Skousen as precedent.
- **Replaced §§6-7** with a new short §6 (Precedent and Scope — ancient comparanda, Bezae caveat, scope boundaries, empirical standard for rule adoption). §7 retired, number preserved.
- **Archived** excised material to `private/01-method/archive/colometry-canon-scholarly-framing-2026-04-20.md` for the reasoning trail. Not canonical; do not cite.
- **Moved** "Imposing vs. Revealing" principle into §1 as the load-bearing scope-discipline doctrine, with punctuation-not-deterministic corollary alongside.
- **Reframed** §1 "Cognitive Cycle" subsection as "Why Predication Is the Default (and When It Is Not Enough)" — drops theoretical framing, keeps operational logic.
- **Retitled** M4 "Fragmented Chafe Idea Unit" → "Fragmented Atomic Thought-Unit." Same principle, neutral label.
- **Removed** Marschall-Posture retrospect from §9 (archived with other scholarly-framing material).
- **Reframed** §8 Hebrews finding: "dictation-grounded texts" → "epistolary-register texts."

Pragmatic stance established: current phase is empirical — *where are the sense-lines, actually?* Method is instrumentation. Rules are revised when they fail to produce genuine sense-lines, not when they lack theoretical warrant. Scholarly alignment is a later, opportunistic question. No colometric output changes from this reframing; this is framing discipline only.

---

*Document created: 2026-04-09. Restructured: 2026-04-16. Canon consolidated: 2026-04-18. Foundational reframing: 2026-04-20.*
