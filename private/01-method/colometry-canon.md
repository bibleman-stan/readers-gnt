# Colometry Methodology Canon — Reader's GNT

This document is the authoritative reference for the editorial methodology behind sense-line (colometric) formatting in the Reader's Greek New Testament at gnt-reader.com. It is the intellectual heart of the project: line-breaking decisions determine how the text reads, breathes, and communicates.

## Foundational premise

Humans think, compose, and deconstruct (read and hear) in sense-lines — atomic thought-units that correspond to how ideas are generated, encoded, and recovered. This is the working hypothesis that drives the project. It was not derived from any scholarly framework; it was arrived at intuitively and analogically, triggered by Royal Skousen's demonstration that the Book of Mormon could be reduced to sense-lines (*The Earliest Text*, 2009/2022) and Stan's reasoning by analogy that what is true for the Book of Mormon is likely true for the Greek New Testament and perhaps any text.

The methodology itself — four criteria, rules, hierarchy, structural justifications, merge-overrides — emerged from hands-on editorial experimentation across all 260 chapters of the GNT. It is pragmatic, not theory-derived.

## Posture

The current phase is empirical: *where are the sense-lines, actually?* The method is instrumentation for answering that question. When the method produces a line that does not reveal a genuine sense-boundary, the method is wrong and gets revised. When the method produces a line that does, the method is working.

Scholarly alignment with cognitive-science, psycholinguistic, or classical-rhetorical frameworks may or may not emerge in a later consolidation phase. Any such alignment is opportunistic, not load-bearing. No framework external to the text is currently treated as the reason a rule works.

## Architecture

The colometric methodology sits on a three-layer architecture:

**Layer 1 — Generic Koine break-legality.** Constraints any competent editor of any Koine Greek text would observe: article + noun stays together, preposition + object doesn't split, postpositives can't start a line, periphrastics stay whole. Lives as a shape-capped table at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md) — 24 rows of syntactic signature + legality verdict + BDF/Smyth/Wallace citation. Not our editorial doctrine; a pointer to generic Koine grammar facts. Migrated from canon §3.2 on 2026-04-20 (R2–R7 now live here).

**Layer 2 — Validators.** Mechanical checks that read Layer 1 and Layer 3 rules against Macula-Greek ([Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek), CC-BY 4.0) and MorphGNT ([morphgnt/sblgnt](https://github.com/morphgnt/sblgnt), CC-BY-SA) parse data. Two error classes: `MALFORMED` for Layer 1 violations (ungrammatical typography — must fix, Category A by default), `DEVIATION` for Layer 3 violations (grammatical but not our editorial convention — Category A/B/C gating per §3 Autonomy Boundary). Target directory split: `validators/syntax/` for Layer 1 checks, `validators/colometry/` for Layer 3 checks. Under active build 2026-04-20 (see session folder `private/03-sessions/2026-04-20-foundational-reframing-and-layer-1/`).

**Layer 3 — This canon.** Editorial sense-line methodology specific to the Reader's GNT. Where and why we diverge from or add to generic Koine syntax to reveal atomic thought. The three forces (§1), five structural justifications (§2), four merge-overrides (§2), rules (§3), operational tests (§4), register operationalization (§5), and Greek-specific application data (§8) all live here. The Subtractive force in §1 is the contract with Layer 1 — we never violate it.

The division matters because it separates *what Greek grammar requires of any editor* (Layer 1) from *what our project chooses to do editorially* (Layer 3). Pre-2026-04-20, the canon mixed the two — rules like R2 (never end on conjunction) were codified as editorial when they are in fact generic syntactic facts. That was a category error, resolved by the 2026-04-20 foundational-reframing + Layer 1 extraction.

---

**How to use this document:**

- **Part 1 (The Method)** is the constitutional core. Every session that touches editorial work MUST read it. It contains everything a trench Claude needs to make correct editorial decisions.
- **Part 2 (The Framework)** provides depth — register operationalization, precedent manuscripts, Greek-specific application data. Read when you need the "why" behind Part 1.
- **Part 3 (The Record)** is the historical appendix — superseded formulations, chronological update log, the reasoning trail. Read when you need to understand how a decision evolved.
- **Layer 1 and Layer 2** are separate from this canon — see the Architecture section above. Layer 1 lives at `data/syntax-reference/greek-break-legality.md`. Layer 2 validators live at `validators/syntax/` and `validators/colometry/` (under active build).

---

# Part 1: The Method

*Everything in Part 1 is authoritative and current. A trench Claude reading sections 1 through 4 has everything it needs for editorial work.*

---

## Section 1: The Framework

Sense-line breaks are governed by **three forces** operating in concert: a **generative** force that proposes where breaks should happen, a **subtractive** force that vetoes breaks that would violate Greek syntax, and a **diagnostic** force that sharpens ambiguous cases. Earlier formulations used a four-criteria strict-hierarchy framing; this framework replaces that with the three-forces architecture adopted 2026-04-20 after cross-canon alignment with the sibling project (see §10 update log).

### Mission and Method — the Discipline Framing

**Mission:** We are revealing sense-lines — atomic thoughts the reader can process as discrete units. This is what the project is trying to produce (stated in the foundational premise at the top of the canon).

**Method:** The framework below is syntax-constrained. This is **not** because syntax is primary to the mission — atomic thought is. It is because **syntactic violation is fatal while sense ambiguity is recoverable within the permitted space.** An ungrammatical line cannot be rescued by good sense. A grammatical line that isn't the ideal sense-boundary can still be read. The method therefore leads with the syntactic floor (subtractive force) so that editorial judgment (generative force) operates only within the legal-break space.

The mission is sense-driven. The method is syntax-constrained. These are two sides of the discipline, not a conflict.

### Framing Principle: Container, Not Originator

Before the three forces themselves, the relationship between *thought* and *syntax* has to be stated precisely, because it determines how the forces combine.

**The atomic thought is the primary, originating reality.** It is what the author wants to say, prior to and independent of any particular language. Greek, Hebrew, Aramaic, English, and Chinese speakers all compose in thought units. The atomic-thought target is *language-invariant*.

**Syntax is the container, not the originator.** Every atomic thought is *always already* shaped by the grammatical framework of the language it was born in — there is no unclothed "pure thought" underneath waiting to be extracted. The container constrains: Paul could not express his thought without choosing Greek syntactic patterns, and those patterns imposed fixed structural commitments (word-order possibilities, correlative pairs, conditional shapes, case government). But the container does not *originate* the thought. The thought exists first and fits itself into whatever vessel is available.

This is the classical distinction between **logos endiathetos** (the thought in the mind) and **logos prophorikos** (the thought as uttered). Colometric recovery targets the endiathetos through the prophorikos because the prophorikos is all we have.

**Consequences for the framework:**

1. **Propositions (atomic thoughts) are the generative force because they are what we are recovering.** The thought is the target.
2. **Syntax is the subtractive force — the evidence surface through which propositions become visible in this particular language, and simultaneously the floor below which no line can legally sit.** Not a separate check; not a lesser concern. Syntax both reveals where propositions end (thought-marking syntax) and constrains where breaks are legal (Layer 1 break-legality, complement integrity, formula integrity).
3. **Grammar is bigger than syntax** — it includes lexicon, morphology, pragmatics, phonology. Most of these do not affect colometric decisions. "Syntactic" is more precise than "grammatical" when we describe the evidence we use. Morphology (case, mood, person, tense) is the surface we read syntax *off of* — vocative case tells us a word is in an address relation; 2p verb inflection tells us there is an implicit "you" subject that a vocative can name. But the thing we care about is the *relationship* morphology reveals, not the morphology itself.
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

### Breath — Retired 2026-04-20

Earlier GNT formulations treated breath (oral-delivery fit) as a fourth criterion. Retired 2026-04-20 after empirical test across 260 hand-edited chapters found zero cases where breath was the sole deciding factor on any line break. The cognitive-chunking work breath was informally doing is now absorbed by structural justification #5 (substantive adjunct as own focus, §2). If a merge produces something unspeakable, reconsider — but that reconsideration will find its warrant in the three forces (propositions / syntax / image) or in justification #5, not in breath as its own criterion.

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

**Line breaks follow structure that already exists in the text. If a rule produces a line that does not match the text's inherent structure, the rule is wrong.** This is the load-bearing meta-principle for the whole project:

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

**Corollary — the "reaching-for-split" warning.** When the grammatical case for a split is borderline and you find yourself reaching for rhetorical-motif, image-analysis, cognitive-predictive-processing, or oral-rhythm arguments as tiebreakers, **that is the signal that scope creep is happening.** The scope-disciplined default in a borderline case is to keep the grammatical constituent intact — i.e., **prefer merge to split** when the grammar is ambiguous.

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

**Structural prong argument:** The accumulation pattern (adjective, adjective, prepositional phrase) is a recognized grammatical form for predicate-complement stacking. The reader reconstructs "X is [attribute]" or "X who is [attribute]" from context. Criterion 2 (single image) provides the formal justification.

**Detectable signature:** A verse or span where (a) no finite verb appears until a later verse, (b) the lines are successive characterizations of the same subject, and (c) each characterization could be extracted as a standalone description.

**Canonical cases:**
- **Acts 10:1-3** (Cornelius): `hekatontarches ek speires` / `eusebes kai phoboumenos ton theon` / `poion eleemosynas pollas to lao` — no finite verb until v.3 (eiden). Each line is one attribute of Cornelius.
- **Pauline salutations** (Rom 1:1, 2 Cor 1:1, Gal 1:1, etc.): `Paulos apostolos` / `dia thelematos theou` — each credential on its own line.
- **Heb 1:3-4**: `hos on apaugasma tes doxes` / `kai charakter tes hypostaseos autou` — each is one image of the Son.

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

**Relation to R19, R20, FEF:** These are the mechanical operationalizations of justification #5 for specific adjunct classes. Justification #5 is the generating principle; R19 / R20 / FEF treatment are how it lands for gen abs, prep catenae, and periodic frames respectively. A future adjunct pattern not covered by the existing rules inherits its warrant from justification #5 rather than requiring a new top-level rule.

**Contrast with breath:** justification #5 captures the cognitive work that breath was loosely doing (long lines need breaking) but with a principled grammatical-peripherality test rather than an un-thresholded "feels too long" judgment. Breath's continuing status is under review (§1); substantive adjunct is the proposition-side replacement for the cognitive-chunking work breath was smuggling in.

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

**Strict-application caveat — M1 rejection does not license split.** M1's "different semantic domains" tie-breaker *withdraws the gorgianic merge protection*; it does NOT by itself license a split. Before flipping to SPLIT, check whether another merge protection fires: M2 (verb-object bond), M3 (bare-governor), M4 (fragmented atomic thought), R11 (speech-intro / approach+touch), §3.7 Need/Response (Matt 25 class), §3.7 Imperative + Divine-Consequence (Luke 6:37 class), §3.7 Cause-Consequence Bonded Beat (John 6:49 class), and default-merge when grammar is ambiguous. Split only when ALL merge protections are exhausted AND both resulting fragments pass the atomic-thought test. Rationale: the canon's overall posture is merge-by-default; M1 is one of several merge levees, and its failure signals "check the others", not "proceed to split". *Codified 2026-04-21 after a round-2 adversarial pass on 318 KEEP_MERGED verdicts showed that strict-application drift (flipping on M1 failure alone) produces split-bias inconsistent with cross-corpus practice.*

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

**This is the adversarial auditor's primary over-split detection rule.** Most session 18/19 reversals (Rom 1:29, Luke 14:21, Phil 4:8, 2 Pet 2:10) triggered M4 alongside M1 or M3.

### The Complete Framework

Putting Section 2 and the merge-overrides together, the full decision procedure is:

1. **Default:** merge (predication test — members sharing one predicate and not independently atomic stay on one line).
2. **Split-trigger** (= any of justifications 1–4 firing): if BOTH the structural prong (one of justifications 1–4) AND the cognitive prong (atomic thought-unit) pass, the line splits.
3. **Merge-override:** even when a split-trigger applies, if any merge-override (M1–M4) fires, the line returns to merged state. **When split-trigger and merge-override both fire on the same line, merge-override wins** — the merge-override list is the mechanism that prevents split-triggers from producing non-atomic or bonded-pair fragments. Note: M4 is the cognitive prong restated as a merge condition — step 2 requires the cognitive prong to pass for a split to proceed; M4 blocks a split when any resulting fragment fails that same test. They are the same test viewed from opposite directions; there is no logical gap between them.
4. **Textual asymmetry override (R28):** where the author has chosen asymmetric treatment of parallel passages, preserve the author's structure regardless of editorial symmetry preferences. R28 operates at the split-trigger level — when the author's finite-verb count or structural choice differs between parallel passages, R28 blocks importing the richer passage's structure onto the sparser one, even when formal markers on the sparser side would otherwise trigger justification 1.

The framework is a default-merge with two closed lists of exceptions — five split-triggers and four merge-overrides — plus a meta-principle (R28) governing cases where authorial and editorial symmetry conflict.

---

## Section 3: The Rules

### Autonomy Boundary (Read This First)

When proposing sense-line changes, classify each change:

- **Category A — Editorial slippage:** suboptimal break, no theological or rhetorical stakes. Apply confidently.
- **Category B — Rhetorical shape:** changing the break changes how the speaker builds an argument. Flag and ask Stan before applying.
- **Category C — Theological weight:** break placement makes a doctrinal point. Flag and discuss with Stan before touching.

**Default:** When you cannot confidently assign Category A, treat it as Category B and flag for Stan. The cost of a false Category A (applying a change Stan would have wanted to discuss) is higher than the cost of a false Category B (flagging something that turns out to be straightforward).

**Mechanical-rule authority.** When a rule classified as MECHANICAL fires unambiguously on a passage — all conditions satisfied, no heuristic ambiguity — the change is **Category A by default**. The rule itself is the approval; per-item flagging is not required and wastes both sides' time. Bump to Category B only when theological, rhetorical, or textual-critical weight is independently implicated (e.g., classic exegetical hot spots like John 1:3-4, Rom 9:5, Eph 1:4-5). Editorial rules and fuzzy rules remain Category B/C as stated.

**Proposed-rule adoption protocol.** A proposed rule is adopted when its first corpus sweep produces ≥80% clean categorization (unambiguous STRONG-MERGE or STRONG-SPLIT). Apply the clean categorizations; refine the rule for the ambiguous residue and re-run. If ≥80% cannot be reached after two refinement passes, the rule is likely editorial rather than mechanical — reclassify and gate per Category B/C.

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

Rules are classified as MECHANICAL (any trained editor would apply them identically), EDITORIAL (defensible, documented, but require judgment), PRINCIPLE (governing stance, not a per-line rule), or LAYER 1 (pure Koine-Greek syntax facts, migrated 2026-04-20 to [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md); Mechanical in effect, but their warrant is generic Greek grammar rather than a project-specific editorial choice).

### 3.1 The No-Anchor Rule

Every sense-line must carry at least one thought-marking anchor: (1) a finite verb, (2) an infinitive, (3) a participle standing as predicate, or (4) a substantive head that is the independently predicated topic of its own line.

*Serves:* Criterion 1 (atomic thought) — this rule operationalizes the DEFAULT case of criterion 1 (the predication test).

**TIGHTENED participle scope (2026-04-16):** Anchor type (3) is "a participle standing as predicate" — not any participle. A participle functioning as an adverbial modifier or attributive adjective does not anchor its line; only a participle standing as the predicate of its own clause (genitive absolute, circumstantial participle carrying an independent predication via ellipsis) counts.

**Critical clarification:** A "substantive head" does NOT include bare noun phrases that continue a prior clause's predicate as list objects or appositional extensions. A line of objects from the previous line's verb fails the anchor test even though it contains nouns.

**Exemptions:**
1. Single-line verses — atomic by definition.
2. Speech-intro prefixes ending with ano teleia (kai palin:, kai eipen:) — the punctuation marks a new discourse layer.
3. Standalone sentence connectives (Hoste, Ara oun, Dia touto) — hinge markers that license a merge with the *next* line.
4. Lines that fail the anchor test but pass the two-prong exception test (Section 2) — formally-marked parallel series members, portrait-building accumulations, speech-act announcements, and classical commata may legitimately lack a traditional anchor.

**Object-continuation failure mode:** The most common way a noun-only line slips through is as a compound-list continuation: the previous line establishes a verb, and the following line names additional objects. These look anchored (they have nouns) but are not.

**Corpus status (2026-04-12):** 860 no-anchor merges applied across 26 books. Final scan: 0 unanchored lines remaining corpus-wide.

### 3.2 Syntactic Bond Rules — Migrated to Layer 1

*2026-04-20: R2–R7 (never dangle conjunction, never end on article, never split negation, never split periphrastic, fixed phrases, vocative indivisibility) are pure Koine-Greek syntax facts — they would be observed by any competent editor of any Koine text, not just this project. They have been migrated to the Layer 1 break-legality reference: [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md). Validators read them from there.*

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

*Established:* 2026-04-15 session (1 John 2:14 analysis, commits f086011, 196315a). *Refined:* 2026-04-16 session — martyreo and homologeo reclassified from cognition-class to declaration-class on the period-test argument, validated by the 1 John 4:14/4:15 parallel (martyreo and homologeo two verses apart, both public-declaration verbs with identical ὅτι-content structure).

### ὅτι Placement Convention — Leads Its Complement

When a ὅτι-clause is split from its governing verb (split applies under R10 for declaration/speech verbs: λέγω, γράφω, μαρτυρέω, ὁμολογέω, διδάσκω, κηρύσσω, ἀπαγγέλλω, etc.), the ὅτι leads the new line — it does not dangle at the end of the preceding line.

Corpus state (post-2026-04-18 flip): **834 leading : 0 trailing** — convention is universal.

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

### Need/Response Paired Beats — Stay Together

When a passage pairs a stated condition with its corresponding response in the same clause (ἐπείνασα / καὶ ἐδώκατέ μοι φαγεῖν, "I was hungry / and you gave me to eat"), the pair stays on one line as a single "need-met" beat. Each pair is one rhetorical unit: need + response is indivisible.

**Canonical cases** — Matt 25:35-36 (positive, fivefold) + Matt 25:42-43 (negative inversion):

```
ἐπείνασα γὰρ καὶ ἐδώκατέ μοι φαγεῖν,
ἐδίψησα καὶ ἐποτίσατέ με,
ξένος ἤμην καὶ συνηγάγετέ με,
γυμνὸς καὶ περιεβάλετέ με,
ἠσθένησα καὶ ἐπεσκέψασθέ με,
```

Each line is a need + response pair. Splitting the need from the response would produce dangling "I was hungry" fragments stripped of their meaning.

**Diagnostic:**
- Line contains a state/condition verb (ἐπείνασα, ἐδίψησα, ξένος ἤμην, γυμνός, ἠσθένησα, ἐν φυλακῇ ἤμην)
- Followed by καί + response verb in 2p or 3p (ἐδώκατε, ἐποτίσατε, συνηγάγετε, περιεβάλετε, ἐπεσκέψασθε, ἤλθατε)
- Pair stays merged under a shared "each need-met pair is one rhetorical beat" principle.

**Relation to R12/R13:** R12's parallel-stacking trigger fires on the OUTER series (five beats stacked), not on the INNER pairs. Each beat stays intact; the series stacks beat-by-beat.

### Imperative + Divine-Consequence — Stay Together

An imperative followed by a divine-promise response (impersonal passive or 3p active — "and it will be given," "and you will find," "and God will give") is one unified petition/promise unit. The imperative and its promised divine response stay on one line.

**Canonical cases:**
- Luke 6:37 (×3): Μὴ κρίνετε καὶ οὐ μὴ κριθῆτε / μὴ καταδικάζετε καὶ οὐ μὴ καταδικασθῆτε / ἀπολύετε καὶ ἀπολυθήσεσθε
- Luke 6:38: Δίδοτε, καὶ δοθήσεται ὑμῖν
- Luke 10:28: τοῦτο ποίει καὶ ζήσῃ
- Luke 11:9 (×3): αἰτεῖτε, καὶ δοθήσεται ὑμῖν / ζητεῖτε, καὶ εὑρήσετε / κρούετε, καὶ ἀνοιγήσεται ὑμῖν
- Jas 4:8: ἐγγίσατε τῷ θεῷ, καὶ ἐγγιεῖ ὑμῖν
- 1 John 5:16: αἰτήσει καὶ δώσει αὐτῷ ζωήν

**Diagnostic:**
- Line contains an imperative (any person/number) or a hortatory subjunctive
- Followed by καί + 2p/3p verb that expresses divine response (passive for impersonal-divine agency, or 3p active with divine subject explicit or implicit)
- Pair stays merged as one prayer/promise act.

**Why not R12:** The imperative and the promised response are not two independent propositions — they are a coordinated petition/promise unit. The divine subject of the response is typically elided; splitting the imperative from its promise severs the single rhetorical gesture.

**Related:** Compare with R11 synonymous-doublet imperatives (Mark 4:39 Σιώπα, πεφίμωσο) — another "stays merged despite καί-linkage" class. The M1 gorgianic-pair rule and these two patterns share the generating principle: **N=2 coordinate members with unified rhetorical force stay on one line**.

### Cause-Consequence Bonded Beats — Stay Together

An N=2 coordinate pair where member 2 is the direct causal consequence of member 1, AND the rhetorical/narrative *point* of mentioning member 1 IS member 2, stays merged as one bonded beat.

**Canonical cases:**
- John 6:49: `ἔφαγον... τὸ μάννα καὶ ἀπέθανον·` — "ate the manna and died." Remove "died" and the eating has no point in the manna/bread-of-life discourse.
- John 10:12: `θεωρεῖ τὸν λύκον ἐρχόμενον καὶ ἀφίησιν τὰ πρόβατα` — "sees the wolf coming and abandons the sheep." Remove "abandons" and the seeing has no point as a cowardice-indictment.

**Diagnostic — the removal test:**
- Remove member 2. Does member 1 lose its reason for being mentioned in the discourse?
- If yes, the pair is causally bonded; stay merged.
- If no (i.e., member 1 stands as its own independent beat with its own discourse value), the pair is a coordinate series; split per justification 1.

**Test contrasts (non-examples):**
- Luke 18:32 passion list (παραδοθήσεται / ἐμπαιχθήσεται / ὑβρισθήσεται / ἐμπτυσθήσεται) — each item has independent discourse value as a fate-item in the series. Not bonded; split applies.
- Jas 4:2 φονεύετε / ζηλοῦτε — parallel accusations, neither is the point of mentioning the other. Not bonded; split per M1 tie-breaker.
- John 9:15 ἐνιψάμην / βλέπω — aspect shift (aorist → present) marks two distinct events in time; even though the washing caused the seeing, the present tense on βλέπω makes it the ongoing-state beat, not the immediate-consequence of the completed washing. §3.16 fires; split.

**Why not M1:** M1 requires same semantic domain (synonymy / cognate / intensification-variant). Cause-Consequence pairs are deliberately cross-domain (action + consequence). M1's tie-breaker correctly rejects them as gorgianic, but Cause-Consequence Bonded Beat is the merge protection that fires instead.

**Family placement:** Same cluster as M1 gorgianic-pair, R11 synonymous-doublet imperative, Need/Response (Matt 25), Imperative + Divine-Consequence (Luke 6:37). All share the generating principle: **N=2 coordinate members with unified rhetorical force stay on one line**. This subsection extends the family to cover cross-domain causal bonds, which the prior subsections (all same-domain or divine-subjected) do not.

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

*27 confirmed splits applied corpus-wide (2026-04-15 sweep).*

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

*125 vocative merges landed across 21 books (2026-04-12).*

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

*15 merges applied corpus-wide (2026-04-15 sweep).*

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

The same four colometric criteria apply uniformly to all NT authors. Do not adjust thresholds, rules, or sensitivity by author or genre. Let the colometric output reveal authorial differences rather than encoding assumptions about them.

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

These are the instruments trench Claudes actually run during editorial work.

### Post-Split Function-Word Recheck (mandatory after any split pass)

**After any mass-split pass (R8, R12, R18, R19, or any rule that produces new line breaks), re-run the dangling-function-word check before committing.** A split can strand preposition-object, article-noun, or negation-verb pairs on either side of the new break. The recheck catches these.

**Why it's mandatory:** every new line break is a potential function-word orphan. The canon's "never split" list (article+noun, preposition+object, negation+verb, noun+genitive modifier, noun+possessive pronoun — see Layer 1 `data/syntax-reference/greek-break-legality.md`) is a forbidden-break set; a split pass can accidentally produce forbidden breaks if the scanner isn't perfectly tuned. The recheck is the safety net.

**Gold-standard regression-test chapters:**
1. **Mark 4** — parable density, nested subordination, gorgianic pairs
2. **Rom 2:12-13** — Paul's densely-packed νόμος argumentation; prepositional-phrase gauntlets
3. **Acts 1:1-4** — Lukan complex-participial opening; "while being assembled with them he commanded them not to depart from Jerusalem but to wait for the promise of the Father..."
4. **Heb 1:3** — triadic participle chain with aspect shifts (the §3.16 showcase)

**After any pipeline change (regen logic, scanner rewrite, validator update), manually diff these four chapters' v4 + eng-gloss before and after. If any of the four breaks, the pipeline change is suspect.**

### The No-Anchor Test (Default Case of Criterion 1)

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

### The Breath Test

**What it checks:** Can the line be delivered in one breath at natural reading pace?

**How to run it:** Read it aloud (or imagine reading aloud). If you gasp, it is too long. If you have nowhere to land, it is too short.

**Honest scope:** Currently no falsifiable threshold. Functions as a sanity check, not a mechanical gate.

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

The four-criteria hierarchy as stated (atomic thought > single image > breath > source-language syntax) is **register-flat at the base layer**. But actual practice is register-aware. Register is a **modulation layer that sits on top of the base hierarchy**, detected by local syntactic/lexical signatures rather than by coarse genre tags.

**Register is detected locally, not globally.** A chapter can shift register mid-verse. An argumentative period can contain an enumerative catena; a narrative chain can break into a sermonic indictment. We do not pre-classify whole books into registers; we read the signature of each local span and apply the appropriate modulation.

### The Six Registers

| Register | Local signature | Rule modulation |
|---|---|---|
| **Enumerative (stab-commata)** | Asyndetic or high-kai lists of parallel NPs/PPs with shared governing head; typically 3+ members; each carries independent rhetorical weight | Stack aggressively; each member is its own atomic thought. 2 Cor 6:4-7 (en-catena), 2 Cor 11:23-27 (kindynois octet), Rom 1:29-31 (vice catalog), Gal 5:19-21, Gal 5:22-23. |
| **Gorgianic (pair-bond)** | Coordinate pairs with figura etymologica, sound echoes, rhythmic balance; exactly 2 members; no independent rhetorical weight per member | Tight merging — both stay on one line. `kopo kai mochtho` (2 Cor 11:27), `hagia kai amomo` (Eph 5:27). |
| **Narrative frame-setting (FEF)** | `egeneto de` / `egeneto en to` / kai egeneto chains; temporal, spatial, circumstantial protasis with deferred main clause | Frame-expansion structure: the protasis is held together as one atomic temporal frame even when long; the main clause starts a new line. Luke 3:1-2 paradigm. |
| **Sermonic / indictment / woe-formula** | 2p imperatives stacked; vocatives at paragraph-initial; ouai formulas; rhetorical questions in anaphoric sequence | Tighter breaks; anaphoric stacking of parallel indictment clauses. Matt 23:13-29, Luke 11:42-52, Jude 11-16. |
| **Argumentative / periodic** | gar / hoti / dioti / dia touto / ara / oun causal-consecutive markers; hina and hoste result chains; participial subordinate chains in main-clause matrix | **Longer atomic-thought lines licensed; cognitive hierarchy overrides breath.** Rom 1:4-5, Heb 1:1-2 sit here — the long line is register-correct. |
| **Apostrophic** | Vocative density; 2p direct address; emotional appeal; often discourse-initial o or paragraph-initial vocative | Vocative-indivisibility + framing-attach. Each vocative gets its own line; the vocative preserves the appeal as its own discourse gesture. Gal 3:1, 4:19, 1 Cor 15:55. |

**How to read the table.** The first column is a detection rule. The second column is the modulation. No new criteria enter; the existing hierarchy governs, but the register changes which member is load-bearing in that local span.

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

The §3.7 subsections added 2026-04-21 (Cause-Consequence Bonded Beats, M1 strict-application caveat) each follow this shape implicitly. Making it explicit here means future additions can be audited against a defensibility checklist — relevant both for day-to-day consistency and for the PhD prospectus where each rule will need to carry its warrant. Retroactive audit of existing canon sections is future work; the requirement is prospective from 2026-04-22.

### v4 as methodology application (not hand typing)

A reproducibility distinction that matters for scholarly defensibility:

- **v0–v3** (earlier stages of the text pipeline) are **bit-exactly reproducible** from source. Running the scripts on the source inputs produces byte-identical output.
- **v4-editorial** is **methodologically checkable**, not bit-exactly reproducible. It is where the documented colometric methodology is *applied* through a mix of scan-and-apply tools (scripts), rule-application validators, and case-by-case editorial decisions where the rule set underdetermines. A different editor following the same canon should arrive at largely the same breaks — within the Category B/C bands of legitimate editorial variation.

**Implication:** v4 is not "hand-typed prose formatted nicely". It is the methodology *in operation*. Every line break in v4 either (a) applies a Category A rule mechanically, or (b) reflects a Category B/C editorial call that should be traceable to a canon rule plus a defensibility rationale. The corpus is auditable against the canon; it is not reproducible from the canon alone because the editorial calls require human (or Claude-with-Stan) judgment.

This framing is relevant for:
- External reviewers evaluating whether v4 is a "scholarly product" or a "personal annotation". It is the former, grounded in an articulated methodology.
- Future Claudes auditing whether a corpus edit is defensible: trace it to a canon rule + warrant. If it can't be traced, it's a methodology gap (add to canon) or a bug (fix in corpus).
- The scan-and-apply pattern: mechanical sweeps ARE methodology application, not mechanical overrides. The script encodes a Category A rule; running it applies the rule at scale.

---

## Section 7

*Retired 2026-04-20. Scholarly-grounding material (Chafe idea units, Kintsch propositions, Miller/Cowan chunking, Daneman & Carpenter reading spans, dictation hypothesis as methodological frame, Marschall comparison, cognitive-grounding test as binding constraint) archived at `private/01-method/archive/colometry-canon-scholarly-framing-2026-04-20.md`. Section number preserved to avoid breaking references in prior session notes; do not re-use.*

---

## Section 8: Greek-Specific Application

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

**Participial chain collapse (2026-04-13 finding).** When >=2 participles at different temporal planes are collapsed into one line, split them. The paradigm: Heb 1:3 (present participle sustaining, aorist participle purifying, finite indicative enthroning). Cross-gospel convergence: Eucharistic institution narratives (Matt 26:26-27 / Mark 14:22-23), feeding miracle tri-cola (Matt 14:19 / Mark 6:41), vinegar-sponge 5-action collapse (Matt 27:48 / Mark 15:36).

**Prepositional catena absorption (2026-04-13).** >=3 stacked prepositional phrases introducing distinct semantic axes earn splitting. 2 Thess 1:7 (four axes), 2 Cor 6:4-7 and 11:23-27 (the famous Pauline peristasis and kindynois catalogs).

**Suspended-subject-without-predicate.** Topicalized nominative head held in suspension while modifier material piles up before the finite verb. Luke 3:1-2's periodic dating chain; John 17:24's pendant-relative nominative; 1 John 1:1-3's 10-line hanging topic chain.

### Vocative Rules (Refined Three-Way Treatment)

See Section 3.9 for the main rules. The three-way treatment:

1. **Default own line:** Verse-initial, paragraph-initial, post-speech-intro vocatives.
2. **Merge (subject-appositive):** Vocative names the implicit subject of a 2p finite verb in the same clause.
3. **Merge (object-appositive):** Vocative restates an explicit 2p pronoun already in the clause.

Mechanical detection: `scripts/scan_vocative_apposition.py` classifies every vocative-only line. `scripts/apply_vocative_merges.py` applies the merges.

### Orphaned Adverbial Completion Rule

See Section 3.11. Greek-specific detail: the merge cases concentrate on hopou/hote/hos clauses of <=6 words that specify the preceding predicate. 15 merges applied corpus-wide (2026-04-15).

### De-Contrast Overbreak Rule

See Section 3.8. 27 confirmed splits across 16 books (2026-04-15).

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

---

## Section 10: Chronological Update Log

*The dated update blocks from the original document, preserved for the session-by-session reasoning trail.*

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

Added "Substantive Adjunct as Own Focus" as structural justification #5 in §2, matching BofM's 2026-04-19 PM addition. Justification #5 is the generative principle that R19 (gen abs always own line), R20 (prep-catena absorption), and the FEF periodic-frame treatment all derive from.

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
