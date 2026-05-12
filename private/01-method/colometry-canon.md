# Colometry Methodology Canon — Reader's GNT

**Version:** 3.0 (2026-05-12 — framework extracted to atu-method/docs/framework.md)
**Predecessors:**
- v2.0 (2026-04-20) — superseded; framework material lived in §0/§1/§2/§6 prose. Now pointered to atu-method.
- v1.0 (document created 2026-04-09; restructured 2026-04-16; consolidated 2026-04-18) — retained for reference via §10 Update Log; no longer authoritative as a version.

---

## How to use this document

This canon is the GNT-corpus instantiation of the ATU methodology framework. Universal framework material (mission, generative principle, structural justifications, merge-overrides, decision procedure, change protocol) lives in [`atu-method/docs/framework.md`](../../atu-method/docs/framework.md); this document holds GNT-specific rule detail and operational artefacts.

**For humans** reviewing the method or wanting WHY-content: see [`atu-method/docs/framework.md`](../../atu-method/docs/framework.md) (universal framework) + [`atu-method/scholarship/gnt/`](../../atu-method/scholarship/gnt/) (per-rule rationale, grammatical grounding, empirical evidence, intellectual lineage, adversarial history).

**For robots** applying the method to v4/grk sources: read **Part II — Operating Rules** below (§3 Rule Index, §3.1–§3.18, §4 Operational Tests). The Rule Index lists each rule's type and autonomy category. Validator output is a **work queue**, not a review queue. Category A rules fire on unambiguous UD signatures and do not require per-item Stan approval; Category B/C items are the only flags requiring editorial judgment.

**For updating this document:** see [`atu-method/docs/framework.md §7 Change Protocol`](../../atu-method/docs/framework.md) for the universal change protocol (12 mandatory-audit triggers, audit-skippable categories, commit-msg discipline). The GNT-specific mechanical gate for audit compliance is the `validators/hooks/commit-msg` pre-commit hook.

---

# Part I — Method (pointer-only; framework material in atu-method)

## 0. Purpose, Posture, and Architecture

**Pointer to framework.** Universal mission, method (sense-driven mission + syntax-constrained method), pragmatic stance, and scope statements are codified at [`atu-method/docs/framework.md §0`](../../atu-method/docs/framework.md). This canon does not duplicate that prose.

**GNT-specific intellectual lineage** (not in the universal framework): The project's working hypothesis was reached intuitively and analogically, triggered by Royal Skousen's demonstration that the Book of Mormon could be rendered in "sense-lines" (*The Earliest Text*, 2009/2022). Skousen's stated rationale was specific to the Book of Mormon: his sense-lines aim to convey "a dictated rather than a written text." Stan took Skousen's sense-line as the kernel and arrived at the present ATU model — a unit defined not by its scribal-tradition genre but by what a reader can process as a single complete thought. Stan applied the same method to the GNT, reasoning by analogy that what is true for the Book of Mormon is likely true for the Greek New Testament — and perhaps *any* text. The methodology itself — three forces, structural justifications, merge-overrides, rules — emerged from hands-on editorial experimentation across all 260 chapters of the GNT. It is pragmatic, not theory-derived.

**GNT-specific architecture.** The four-plane model (Data / Specification / Tooling / Delivery) for the broader reader-family is documented universally at [`atu-method/docs/architecture.md`](../../atu-method/docs/architecture.md). Within the GNT repo, the per-corpus layer structure is:

- **Layer 1 — Generic Koine break-legality.** Constraints any competent editor of any Koine Greek text would observe. Lives as a shape-capped table at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md) — 24 rows of syntactic signature + legality verdict + BDF/Smyth/Wallace citation. Parse data: Macula-Greek ([Clear-Bible/macula-greek](https://github.com/Clear-Bible/macula-greek), CC-BY 4.0) and MorphGNT ([morphgnt/sblgnt](https://github.com/morphgnt/sblgnt), CC-BY-SA). R2–R7 live here.
- **Layer 2 — Validators.** Mechanical checks reading Layer 1 and Layer 3 rules against Macula + MorphGNT parse data. Two error classes: `MALFORMED` (Layer 1 — must fix, Category A), `DEVIATION` (Layer 3 — Category A/B/C per §3 Autonomy Boundary). `validators/syntax/` for Layer 1; `validators/colometry/` for Layer 3.
- **Layer 3 — This canon.** GNT-specific ATU methodology. The Subtractive force in §1 is the contract with Layer 1 — we never violate it.

**Reader's guide:**
- **Editor making editorial decisions**: focus on §§3-4 and §6.5. Consult §§1-2 for grounding when proposing or evaluating rules.
- **Scholar reading the method as a published artifact**: focus on the GNT-specific framing below (§0 intellectual lineage + §8 Greek-specific application + exegetical convergence).
- **Tracking how a decision evolved**: §§9-10 carry the reasoning trail.

---

## 1. The Framework — Proposition-First, Syntax-Constrained

**Pointer to framework.** The framework specification — generative principle (each proposition splits by default); three closed-list ways syntax forbids splits (Layer 1 mid-phrase prohibitions, complement integrity, formula integrity); image diagnostic (camera-angle test); five structural justifications J1–J5 (formally-marked parallel series, portrait accumulation, speech-act announcement, classical commata, substantive adjunct); four merge-overrides M1–M4 (Gorgianic bonded pair, verb-object clause-nucleus bond, bare-governor indivisibility, fragmented atomic thought-unit); the four forces summary; the five-step decision procedure; the application-order step-by-step (Step 0 input filter through Step 4 diagnostic); the N=2 Adjudication Principle and N=3+ cliff; the punctuation-not-a-signal and versification-not-a-signal stances; the Parallel-List Uniformity Principle; and the Authorial Asymmetry Principle — is codified at [`atu-method/docs/framework.md §1`](../../atu-method/docs/framework.md). This canon does not duplicate that prose.

**GNT-corpus instantiations of the framework:**

- **Step 0 input filter — GNT-specific exclusions.** In addition to the universal filters (punctuation, versification, verse position), GNT editing also excludes from the evidence base: manuscript line divisions in scholarly comparanda (Codex Bezae, Claromontanus — consulted as empirical comparanda, not authoritative warrants; see §6 below); editorial paragraph divisions in printed GNT editions (NA28/UBS5/SBLGNT ¶ marks — never a break signal); and lectionary/pericope divisions.

- **Force 1 (Generative) — GNT resolution principle.** Atomic thought is relative to the author's resolution. For plainer narrative (Mark's simpler scenes), atomic usually means a complete sentence-level predication. For more literary authors (Luke, Paul, John at their most crafted), "atomic" often includes grammatically-independent sub-units — most notably genitive absolutes used as interjectory frames. See §8 for participial and FEF treatment.

- **Force 2 (Subtractive) — GNT Layer 1 reference.** GNT Layer 1 break-legality lives at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md) (24-row table; R2–R7). Parse data: Macula-Greek + MorphGNT.

- **Force 3 (Diagnostic) — GNT image test.** In GNT application: close your eyes and picture the scene. Does the line make you see ONE thing? Canonical cases: Gal 2:9 (split — two distinct thoughts: the named persons vs. their ironic characterization); Gal 2:10 (merge — fronted genitive + restrictive *μόνον* form a marked word order whose rhetorical force depends on grammatical unity staying intact). The full principle and case-study pair live at §8 **Marked Word Order (Fronting Paradox)** — relocated there in the 2026-05-12 restructure because it is GNT-specific operational content (Greek's case-marked freedom of word order), not universal framework.

- **N=2 Adjudication Principle — GNT canonical cases.**
  - MERGE: `Δαιμόνιον ἔχει καὶ μαίνεται·` (John 10:20) — one diagnostic judgment expressed via two complementary terms.
  - MERGE: `κόπῳ καὶ μόχθῳ` (2 Cor 11:27) — "labor and toil" as one image of exhaustion.
  - SPLIT: `οὔτε γαμοῦσιν / οὔτε γαμίζονται` (Matt 22:30) — active and passive sides of the marriage transaction; distinct predicates.

- **M1 bonded-pair list (GNT corpus-attested):** `{κόπῳ, μόχθῳ}` (2 Cor 11:27 — labor+toil); `{χαίρειν μετὰ χαιρόντων, κλαίειν μετὰ κλαιόντων}` (Rom 12:15 — two classical-comma halves constituting one paraenetic command); `{Τολμηταί, αὐθάδεις}` (2 Pet 2:10 — asyndetic N=2 bonded adjective pair).

- **J3 named patterns (speech-act announcement) — GNT instantiations.** Direct speech introduction: `καὶ ἔλεγεν αὐτοῖς:` / `καὶ εἶπεν αὐτῷ:` — each is a complete speech-act predication. See §3.6 (R11) for the full treatment.

- **J5 substantive adjunct — GNT canonical cases.**
  - Genitive absolute (R19 — always own line): `βλεπόντων αὐτῶν` (Acts 1:9) — camera shifts to disciples' perspective as interjectory frame.
  - Prepositional catena: 2 Cor 6:4-7 ἐν-catena — each element on its own line.
  - FEF periodic frame: Luke 3:1-2 — five genitive-phrase temporal adjuncts before the matrix ἐγένετο ῥῆμα θεοῦ.
  - Fronted temporal existential: John 1:1 `ἐν ἀρχῇ` — only 2 words but carries the Gospel prologue's entire temporal frame (brevity-but-substance edge case).

- **Showcase — Acts 1:9 (genitive absolute embedded within FEF).**
  ```
  καὶ ταῦτα εἰπών             <- aorist nominative ptc (FEF frame; subject = Jesus)
  βλεπόντων αὐτῶν             <- GENITIVE ABSOLUTE (subject = disciples); interjectory
  ἐπήρθη                      <- main verb resolving εἰπών
  καὶ νεφέλη ὑπέλαβεν αὐτὸν ἀπὸ τῶν ὀφθαλμῶν αὐτῶν.
  ```
  The gen abs interrupts the FEF suspension with a camera shift to the disciples' perspective, then the main verb drops the resolution. **A gen abs embedded within an FEF should remain on its own line.**

- **Container-not-originator (GNT-specific articulation).** The atomic thought is the primary, originating reality — language-invariant. Syntax is the container, not the originator. This is the classical distinction between *logos endiathetos* (the thought in the mind) and *logos prophorikos* (the thought as uttered). Colometric recovery targets the *endiathetos* through the *prophorikos* because the *prophorikos* is all we have. Paul's atomic thought units in Romans are the same units whether read in Greek, English, or Chinese. Only the container changes.

- **Thought-marking syntax vs. structural syntax (GNT distinction).** *Thought-marking syntax* reveals where one atomic unit ends and the next begins: main-verb shifts, clause boundaries, subject changes. *Structural syntax* is fixed Koine Greek patterns that do not automatically map to thought boundaries but constrain them: conditionals, correlatives, result clauses. A μέν/δέ contrast earns a break when each limb is its own atomic claim, not just because μέν/δέ is present.

- **Priority order when forces leave ambiguity:** Chunking > Oral > Rhetorical. When the three forces leave room for multiple valid choices, cognitive chunking wins over oral delivery wins over rhetorical-structure revelation.

- **Imposing vs. Revealing — GNT scope discipline.** The boundary test: if a feature requires *interpretation* of authorial intent to detect, it is out of scope. If it can be identified by the grammar alone (case, mood, syntactic position, lexical markers), it is in scope. Out of scope for the GNT colometric grid: chiasm detection, klimax/gradatio identification, diatribe Q-A pair tagging, section headers / epistolary form criticism, anacolutha tagging, period-anchor + clause-depth indentation, authorial-intent inference. The grid is flat by design — every line has equal visual status. "Reaching-for-split" warning: when the grammatical case is borderline and you find yourself reaching for rhetorical-motif, oral-rhythm, theological-weight, or any non-grammatical category as tiebreaker, that is scope creep; prefer merge.

---

## 2. Autonomy Boundary — Categories A / B / C

**Pointer to framework.** Categories A (Mechanical, mandatory), B (Editorial, judgment-required), C (Theological / textual-critical), the Mechanical-Rule Authority principle, the default-handling under uncertainty, and the Scope/Precedence/Closed-List Diagnostic are codified at [`atu-method/docs/framework.md §2`](../../atu-method/docs/framework.md). This canon does not duplicate that prose.

Per-rule Category assignments are in each §3 rule entry's classification.

**GNT-specific instances:**
- **Category A:** A dangling article (τόν at line end) or a verb split from its direct object — mechanical error, fix confidently. 860 no-anchor merges applied across 26 books (corpus-wide scan result).
- **Category B:** Phil 2:6-8 kenosis hymn — whether `θανάτου δὲ σταυροῦ` gets its own line changes how the descent structure reads.
- **Category C:** Rom 9:5 — whether `ὁ ὢν ἐπὶ πάντων θεὸς εὐλογητός` attaches to `ὁ Χριστός` (Christological reading) or begins a new doxology (theistic reading). Break placement is a doctrinal decision. John 1:3-4 (ho gegonen placement) — colometry keeps `ὃ γέγονεν` with v.3; the relative clause governed by antecedent `ἕν` per complement-attachment rule.

---

# Part II — Operating Rules (for robots applying the method)

*Everything in Part II is authoritative and current. Sections 3 through 5 contain everything an editor needs to make line-break decisions.*

---

## Section 1: The Framework

*Framework material is in Part I above. See §0 (Purpose, Posture, Architecture), §1 (Framework pointer + GNT-corpus instantiations), and §2 (Autonomy Boundary pointer + GNT instances). The universal framework specification lives at [`atu-method/docs/framework.md §1`](../../atu-method/docs/framework.md).*

---

## Section 2: The Unless Conditions (Closed List)

**Pointer to framework.** The five structural justifications (J1–J5) and four merge-override conditions (M1–M4), their generating principles, two-prong exception test, complete decision procedure, and the N=2 Adjudication Principle are codified at [`atu-method/docs/framework.md §1.4–§1.9`](../../atu-method/docs/framework.md). This canon does not duplicate that prose.

**GNT-corpus instantiations (§2):**

### J1 — Formally-Marked Parallel Series: GNT Cases

- **PASS — correlative with distinct predicates:** `οὔτε γαμοῦσιν / οὔτε γαμίζονται` (Matt 22:30 / Mark 12:25 / Luke 20:35) — two distinct predicates: active and passive sides of the marriage transaction. Each is a complete predication; each stands.
- **PASS — triadic parallel series:** `εἴτε οὖν ἐσθίετε / εἴτε πίνετε / εἴτε τι ποιεῖτε` (1 Cor 10:31) — three distinct predicates, three distinct activities.
- **PASS — triadic yield list:** `καὶ ἔφερεν ἓν τριάκοντα / καὶ ἓν ἑξήκοντα / καὶ ἓν ἑκατόν` (Mark 4:8, 4:20) — recoverable verb "bore" from first member.
- **STAY — compound subject sharing one verb:** `οὔτε σὴς οὔτε βρῶσις ἀφανίζει` (Matt 6:19/20) — two subjects, one verb; compound-subject proposition, not two propositions.
- **The ≤3 qualifier rule — triadic co-referential modifiers stay on one line:**
  - `θυσίαν ζῶσαν ἁγίαν εὐάρεστον τῷ θεῷ` (Rom 12:1) — three adjectives on ONE sacrifice.
  - `τὸ ἀγαθὸν καὶ εὐάρεστον καὶ τέλειον` (Rom 12:2) — three qualities of ONE will.
  - `χρυσὸν καὶ λίβανον καὶ σμύρναν` (Matt 2:11) — three objects of ONE verb.

### J2 — Portrait-Building Attribute Accumulation: GNT Cases

**Detectable signature:** No finite verb appears until a later verse; lines are successive characterizations of the same subject; each characterization could be extracted as a standalone description.

- **Acts 10:1-3** (Cornelius): `ἑκατοντάρχης ἐκ σπείρης` / `εὐσεβὴς καὶ φοβούμενος τὸν θεόν` / `ποιῶν ἐλεημοσύνας πολλὰς τῷ λαῷ` — no finite verb until v.3 (εἶδεν). Each line is one attribute of Cornelius.
- **Pauline salutations** (Rom 1:1, 2 Cor 1:1, Gal 1:1, etc.): `Παῦλος ἀπόστολος` / `διὰ θελήματος θεοῦ` — each credential on its own line.

*(Heb 1:3-4 was previously cited here; removed 2026-04-25 because the rule's detectable signature requires "no finite verb appears until a later verse" and Heb 1:3 has ἐκάθισεν within the verse. The split of Heb 1:3 L1's two distinct-image attributes is governed by §3.16 coordinating-syntax-with-distinct-images, not by this justification.)*

### J3 — Speech-Act Announcement: GNT Cases

- `καὶ ἔλεγεν αὐτοῖς:` — complete speech-act predication; speech content follows on next line.
- `καὶ εἶπεν αὐτῷ:` — same pattern.

See §3.6 (R11) for the full GNT speech-intro treatment.

### J4 — Classical Comma: GNT Case

- `θανάτου δὲ σταυροῦ.` (Phil 2:8) — the escalating appendage. The δέ triggers a new line; the dramatic compression IS the rhetorical device.

### J5 — Substantive Adjunct as Own Focus: GNT Cases

- **Genitive absolute** (R19 — always own line): `βλεπόντων αὐτῶν` (Acts 1:9) — camera shifts to disciples' perspective as interjectory frame.
- **Prepositional catena** (§8): 2 Cor 6:4-7 ἐν-catena (ἐν ὑπομονῇ πολλῇ, ἐν θλίψεσιν, ἐν ἀνάγκαις, ἐν στενοχωρίαις...) — each element on its own line.
- **FEF periodic frame** (§5, §8): Luke 3:1-2 — five genitive-phrase temporal adjuncts (ἐν ἔτει πεντεκαιδεκάτῳ τῆς ἡγεμονίας Τιβερίου Καίσαρος... ἐπὶ ἀρχιερέως Ἅννα καὶ Καϊάφα...) — the matrix ἐγένετο ῥῆμα θεοῦ lands only after the adjunct chain completes.
- **Fronted temporal existential edge case:** John 1:1 `ἐν ἀρχῇ` — only 2 words but carries the Gospel prologue's entire temporal frame; substance overrides the ≤3-word default-merge caveat.

*Relation to R19, prep-catena (§8), FEF:* These are the mechanical operationalizations of J5 for specific GNT adjunct classes. J5 is the generating principle; R19 (gen abs), prep-catena treatment (§8), and FEF periodic-frame treatment (§5) are how it lands for those classes. A future adjunct pattern not covered by existing rules inherits its warrant from J5 rather than requiring a new top-level rule.

### M1 — Gorgianic Bonded Pair: GNT Cases

- `κόπῳ καὶ μόχθῳ` (2 Cor 11:27) — "labor and toil" as one image of exhaustion → MERGE.
- `χαίρειν μετὰ χαιρόντων, κλαίειν μετὰ κλαιόντων` (Rom 12:15) — two classical-comma halves constituting one paraenetic command → MERGE.
- `Τολμηταί, αὐθάδεις` (2 Pet 2:10) — asyndetic N=2 bonded adjective pair, same person → MERGE.

**Tie-breaker (N=2 formally-marked pair):**
- SPLIT: `οὔτε γαμοῦσιν / οὔτε γαμίζονται` (Matt 22:30) — active and passive sides; distinct predicates; J1 wins.
- MERGE: `Δαιμόνιον ἔχει καὶ μαίνεται·` (John 10:20) — one diagnostic judgment; M1 wins.

**M1 strict-application caveat:** When M1's bonded-pair grounds are withdrawn ("different semantic domains"), that does NOT by itself license a split. Before flipping to SPLIT, check: M2 (verb-object bond), M3 (bare-governor), M4 (fragmented atomic thought), R11 (speech-intro), R8's καί-merge default, R28 textual-asymmetry, and default-merge when grammar is ambiguous. Split only when ALL merge protections are exhausted AND both fragments pass the atomic-thought test.

### M2 — Verb-Object Clause-Nucleus Bond: GNT Cases

- `εἰπέ` / `ἵνα οἱ λίθοι οὗτοι ἄρτοι γένωνται` — reject split: εἰπέ needs its ἵνα complement (Matt 4:3).
- `ἐγερθεῖσα / διηκόνει` — reject split: ἠγέρθη and διηκόνει form one narrative beat (Matt 8:15).
- `τοὺς προφήτας / καὶ σοφοὺς / καὶ γραμματεῖς` at Matt 23:34 — accept split: ἀποστέλλω has multiple distinct objects with formal parallel marking (J1 overrides).

### M3 — Bare-Governor Indivisibility: GNT Cases

- Rom 1:29 reversal: initially split as `μεστούς / φθόνου / φόνου / ...`; reverted to `μεστοὺς φθόνου, / φόνου / ...` — μεστούς alone is not a thought.
- Heb 1:1 merge: `Πολυμερῶς καὶ πολυτρόπως` merged back with `πάλαι ὁ θεὸς λαλήσας...` — the adverb pair alone dangles.
- Mark 1:6 merge: `καὶ ἦν ὁ Ἰωάννης / ἐνδεδυμένος τρίχας καμήλου` merged — bare `ἦν` without predicate is not a thought.

### M4 — Fragmented Atomic Thought-Unit: GNT Cases

- Trailing adverbial modifiers orphaned from their predicate: `..., ὅτι X / ...` trailing phrase is not its own idea unit.
- Dangling discourse particles: `ἀλλά` alone on a line without a complete clause.
- Orphaned appositives separated from head noun when the appositive alone has no independent image.

**Primary over-split detection rule.** Most GNT reversals (Rom 1:29, Luke 14:21, Phil 4:8, 2 Pet 2:10) trigger M4 alongside M1 or M3.

---

## Section 3: The Rules

*Purpose: **mainly operational** — rule reference Claude reads literally for editorial application. Read for the Autonomy Boundary (Category A/B/C + scope/precedence/closed-list/carve-out diagnostic), Rule Index, and individual rule subsections (§3.1 through §3.17).*

### Autonomy Boundary (Read This First)

When proposing ATU-level changes, classify each change:

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
| R11-ext / R28-ext | Speech-act announcement after adverbial frame (split) | Mechanical | 3.6 |
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
| R25 | ὥστε short-consecutive-result binding | Mechanical | 3.14a |
| R27 | Authorial style principle (uniform criteria) | Principle | 3.15 |
| R28 | Textual asymmetry overrides editorial symmetry | Principle | 3.7 |
| M4-GNT-1 | Subject-orphan predicate completion (Greek instantiation) | Mechanical | 3.18 |

*Retired (see §9):* R15 (folded into R14), R16 (folded into R8), R21 (absorbed as operational mechanism for R12/R13/R14), R25-old (folded into R11 — superseded 2026-05-11 by R25 ὥστε-binding; see §9), R26 (pure restatement of M2), R29 (pointer-only; M1–M4 stand on their own in Section 2).

Rules are classified as MECHANICAL (any trained editor would apply them identically), EDITORIAL (defensible, documented, but require judgment), PRINCIPLE (governing stance, not a per-line rule), or LAYER 1 (pure Koine-Greek syntax facts at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md); Mechanical in effect, but their warrant is generic Greek grammar rather than a project-specific editorial choice).

### 3.1 The No-Anchor Rule

Every ATU must carry at least one thought-marking anchor: (1) a finite verb, (2) an infinitive, (3) a participle standing as predicate, or (4) a substantive head that is the independently predicated topic of its own line.

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

**Speech-intro frame aggregation (short qualifier only).** The speech-introducing apparatus may merge with a preceding qualifying clause *only when the qualifier is structurally minimal* — a bare ἐάν/ὅταν + subjunctive with no substantial finite-clause content of its own (e.g., `ἐὰν μὴ λέγω·`). When the qualifier is substantive — it contains a finite verb, object NPs, and scene-setting content independent of the speech verb — it is NOT a mere qualifier; it is a full adverbial clause, and R28-ext below mandates the split. Scope boundary: applies only to structurally trivial qualifiers; anything with a full finite-clause body (subject, verb, object) falls under R28-ext and splits.

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

### R28-ext: Speech-Act Announcement After Frame (split)

**Status:** Active (2026-05-11)
**Category:** A (Mechanical, mandatory)
**Layer:** 3 — sub-rule of §3.6 (R11 speech-intro discipline)
**Port:** GNT adaptation of BofM R28 (Speech-Act Announcement After Frame, canon §5 R28)

**Statement.** When a finite speech verb (λέγω, εἶπον/λέγω, φημί) that introduces direct speech co-occurs on the same v4/grk line with a substantive preceding adverbial frame — temporal clause (ὅταν/ὅτε/ὡς + finite verb), causal clause, or participial absolute frame with its own subject/object content — the line MUST be split. The frame occupies line 1; the finite speech verb and its dative-object address (if any) occupy line 2. The speech verb's line 2 closes with the ano teleia (·) or colon (:) per R11.

**Rationale.** Each atomic thought unit encodes one predication. A substantive temporal frame (`ὡς δὲ ἐπαύσατο λαλῶν` — "when he stopped speaking") is a complete predication with its own verb and subject. The finite speech-intro (`εἶπεν πρὸς τὸν Σίμωνα·` — "he said to Simon:") is a separate complete predication. Co-lineating two complete predications violates the one-predication-per-line generative principle. This rule applies the same split-discipline already operative for genitive absolutes (R19) and adverbial subordinate clauses (R9) to the speech-intro context.

**Scope.** Same-line co-occurrence of:
1. A finite speech verb in `SPEECH_LEMMAS_R28EXT` — 3rd-person indicative (λέγω, εἶπον, φημί)
2. A *substantive* preceding adverbial clause: either (a) a finite-verb temporal/causal clause introduced by ὡς/ὅτε/ὅταν/ἐπεί/ἐπειδή, or (b) a participial absolute with its own overt subject and object content (≥3 non-punctuation tokens in the participle's NP cluster)
3. The speech verb's line ends in ano teleia (·) or colon (:), confirming direct speech follows on the next line

**Exclusions (closed list).**

1. **ἀπεκρίθη + ὅτι (R10-governed indirect speech).** When ὅτι immediately follows the speech verb, the construction is R10's cognition/declaration-verb complement, not a direct-speech announcement. R10 governs; R28-ext does not fire. Canonical: John 3:28 ὅτι-clauses.

2. **ἀπεκρίθη + λέγων Hebraism (MERGE, not R11/R28-ext).** The `ἀπεκρίθη ... λέγων` double-verb construction is a Semitic idiom in which λέγων is a redundant manner marker, not a second speech introduction. The entire `ἀπεκρίθη ... λέγων·` collapses onto one line under R11. R28-ext does not fire because λέγων is participial (non-finite), not a standalone finite speech-intro. Canonical cases: Matt 11:25, Matt 12:38, Mark 9:5, Luke 17:17, etc.

3. **Structural minimum frame (§3.6 frame-aggregation carve-out).** When the preceding clause is a *bare* conditional or purpose marker with no substantive finite-clause body (e.g., trivial ἐάν + single-word subjunctive), the frame is not substantive; aggregation applies under §3.6 and R28-ext does not fire.

4. **R19 genitive absolute already handled.** When the frame contains a genitive absolute (anarthrous gen ptc + agreeing gen subject), R19 fires first — the gen abs gets its own line independent of any speech-verb on the same colometric line. R28-ext is therefore redundant in that case and should not be layered on top of an R19 application.

5. **Frame already on prior line (already compliant).** When the temporal/participial frame has already been placed on a separate line by a prior edit or is on a different v4/grk line from the speech verb, R28-ext does not re-fire.

**Precedence vs. other rules.**
- **vs. R9 (subordinate-clause break):** R9 covers the general case of subordinate-clause introduction. R28-ext is more specific: it governs only the subclass where the subordinate clause is immediately followed by a direct-speech verb. Both rules mandate a split; R28-ext provides the specific STRONG-SPLIT label for validator output.
- **vs. R10 (ὅτι complement):** R10 governs first for cognition/speech verbs + ὅτι. If R10 fires, R28-ext is out of scope.
- **vs. R19 (genitive absolute):** R19 governs first when the frame contains a gen abs.
- **vs. R11 (speech-intro own line):** R28-ext is a sub-rule of R11 that adds split discipline when a frame precedes the R11-governed speech verb.

**STRONG-SPLIT examples (compliant after split).**

```
ὡς δὲ ἐπαύσατο λαλῶν,        ← frame: "when he stopped speaking" (Luke 5:4)
εἶπεν πρὸς τὸν Σίμωνα·       ← speech verb + addressee
```

```
Ἀκούσας δέ τις τῶν συνανακειμένων ταῦτα   ← participial frame (Luke 14:15)
εἶπεν αὐτῷ·                               ← speech verb
```

```
ὅταν δὲ πάλιν εἰσαγάγῃ τὸν πρωτότοκον εἰς τὴν οἰκουμένην,   ← temporal frame (Heb 1:6)
λέγει·                                                          ← speech verb
```

**Excluded examples (do NOT split).**

```
ἀποκριθεὶς εἶπεν αὐτοῖς·    ← ἀπεκρίθη+λέγων Hebraism → one line (Exclusion 2)
```

```
αὐτοὶ ὑμεῖς μοι μαρτυρεῖτε ὅτι εἶπον·    ← ὅτι immediately follows → R10 governs (Exclusion 1)
```

**Validator:** `validators/colometry/check_r28_speech_act_frame.py`

**Corpus survey (2026-05-11).** Three STRONG-SPLIT-CANDIDATEs applied: Heb 1:6, Luke 5:4, Luke 14:15.

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

### 3.14a R25 ὥστε Short-Consecutive-Result Binding

**Rule Statement:** When a ὥστε-clause expresses the direct result of the preceding action AND meets all three conditions below, merge the ὥστε-clause onto the same line as its matrix clause. The cause-and-result form a single cognitive image; splitting them fragments what the author composed as one beat.

**Three-condition merge test (all three must hold):**
1. **≤8 words** — the ὥστε-clause (from ὥστε through clause end) contains eight or fewer Greek words (counting ὥστε itself).
2. **Co-referential subject** — the (explicit or implied) agent of the ὥστε infinitive is the same participant as the subject of the matrix clause.
3. **No camera shift** — no new scene participant or viewpoint pivot is introduced by the result clause (the clause stays inside the single image the matrix established).

**Morphological trigger:** ὥστε + **infinitive** (consecutive-result reading). The infinitive signals that ὥστε is binding a dependent result clause, not launching an independent sentence. When all three conditions hold: STRONG-MERGE-CANDIDATE.

**Illative-ὥστε exclusion — SPLIT-MAINTAINED (reason: illative-hoste):** ὥστε as an inferential conjunction ("therefore / so then / consequently") launches a NEW independent sentence. Three reliable surface markers:
- ὥστε + **2nd-person finite imperative** as the first verb (ὥστε μαρτυρεῖτε, ὥστε ἀδελφοί μου ἀγαπητοί — the clause is direct exhortation, not a dependent result).
- ὥστε + **vocative** (the presence of a vocative almost always signals an illative-ὥστε introducing a new address unit).
- ὥστε + **new-third-person declarative finite verb** where the subject differs from the matrix and ὥστε clearly has inferential force (ὥστε ἔξεστιν, ὥστε οὐκέτι εἶ — the prior context is reasoning and this is the conclusion).

**Word-count boundary:** Exactly 8 words qualifies (≤ is inclusive). 9+ words → SPLIT-MAINTAINED (reason: word-count-exceeded). Phase B or later will revisit 9-12 word boundary cases.

**Cross-verse ὥστε:** When ὥστε is the first token of a verse (verse-initial, idx=0), the matrix clause lives in the prior verse. These require cross-verse merge logic (§3.17 procedure) and are deferred to Phase B. Validator: flag as REVIEW-REQUIRED (reason: cross-verse-defer).

**Examples — STRONG-MERGE-CANDIDATE (Phase A applied, 2026-05-11):**

| Locus | ὥστε-clause | Word count | Merge rationale |
|-------|-------------|------------|-----------------|
| Matt 8:24 | ὥστε τὸ πλοῖον καλύπτεσθαι ὑπὸ τῶν κυμάτων | 7 | co-ref subject (storm), one image |
| Matt 10:1 | ὥστε ἐκβάλλειν αὐτὰ καὶ θεραπεύειν πᾶσαν νόσον | 7 | authority-granted-for-result, one act |
| Mark 1:27 | ὥστε συζητεῖν αὐτοὺς λέγοντας· | 4 | crowd amazement → immediate reaction |
| Mark 3:20 | ὥστε μὴ δύνασθαι αὐτοὺς μηδὲ ἄρτον φαγεῖν | 8 | exactly 8 words, co-ref |
| Mark 4:1 | ὥστε αὐτὸν εἰς πλοῖον ἐμβάντα καθῆσθαι | 6 | crowd pressure → single result |
| 1 Cor 13:2 | ὥστε ὄρη μεθιστάναι | 3 | faith → mountain-moving, one image |
| 1 Thess 1:8 | ὥστε μὴ χρείαν ἔχειν ἡμᾶς λαλεῖν τι | 8 | reputation spread → no need to speak |

Full Phase A corpus: Matt 8:24, 10:1, 12:22, 13:2, 13:54, 27:1, 27:14; Mark 1:27, 3:20, 4:1, 4:37, 15:5; Luke 4:29, 5:7, 12:1; Acts 15:39; 1 Cor 13:2; 2 Cor 1:8, 7:7; 1 Thess 1:8. (20 merges total.)

**Examples — SPLIT-MAINTAINED:**

| Locus | Reason | Surface marker |
|-------|--------|----------------|
| Matt 23:31 | illative-ὥστε | ὥστε μαρτυρεῖτε — 2p imperative |
| Matt 12:12 | illative-ὥστε | ὥστε ἔξεστιν — new 3P declarative conclusion |
| Gal 4:7 | illative-ὥστε | ὥστε οὐκέτι εἶ δοῦλος — new 2P declarative, inferential |
| Mark 1:45 | word-count-exceeded | 9 words (μηκέτι αὐτὸν δύνασθαι φανερῶς εἰς πόλιν εἰσελθεῖν) |

**Illative-ὥστε pattern clusters** (Phase C audit `aae0b801a5130b535` confirmed 22 corpus illatives; 4 named pattern clusters with canonical exemplars):

1. **Hortatory imperative / prohibitive** — ὥστε immediately followed by 2p/3p imperative, prohibitive subjunctive, or 1p hortatory subjunctive. *Canonical exemplar:* **1 Cor 4:5** `ὥστε μὴ πρὸ καιροῦ τι κρίνετε` (direct 2p prohibition). Family includes: 1 Cor 3:21, 5:8, 10:12, 14:39; 1 Thess 4:18; 1 Pet 4:19.

2. **Vocative + imperative opener** — ὥστε + direct vocative address + command. *Canonical exemplar:* **Phil 4:1** `ὥστε, ἀδελφοί μου ἀγαπητοί, οὕτως στήκετε ἐν κυρίῳ` (cross-chapter scope makes illative function undeniable). Family includes: 1 Cor 14:39.

3. **New 3P doctrinal-principle declaration** — ὥστε + new indefinite or general subject + timeless-present predication; no action-continuity with matrix. *Canonical exemplar:* **Gal 3:24** `ὥστε ὁ νόμος παιδαγωγὸς ἡμῶν γέγονεν` (doctrinal summary with new subject, often followed by purpose clause). Family includes: Mark 2:28; Rom 7:12, 13:2; 1 Cor 3:7, 14:22; 2 Cor 4:12, 5:17; Gal 3:9.

4. **Rhetorical inferential conclusion** — ὥστε + retrospective argument summary or rhetorical question; no narrative action to inherit. *Canonical exemplar:* **Gal 4:16** `ὥστε ἐχθρὸς ὑμῶν γέγονα ἀληθεύων ὑμῖν` (rhetorical question framing makes inferential function explicit). Family includes: 1 Cor 7:38; 2 Cor 2:7; Gal 4:7.

These 22 illatives are encoded in the validator's `_ILLATIVE_KNOWN` set so they emit `SPLIT-MAINTAINED` directly. Future ὥστε occurrences exhibiting any of the four pattern cluster signatures should be classified as illative without per-instance re-litigation.

**WHY (defensibility):** A ὥστε-infinitive consecutive-result clause is structurally dependent — it cannot stand alone and it names the outcome that the matrix clause caused. Cause + immediate short result = one cognitive image. The reader's eye-span covers both in a single perceptual unit. Splitting them imposes a line-break on a semantic boundary that doesn't exist in the author's composition.

**HOW WE KNOW:** Phase A sweep across all NT books using Grep + manual evaluation of ~30 candidates. The 3-condition test (≤8, co-ref, no camera shift) correctly identified 20 clean merges and correctly excluded all illative cases and all word-count-exceeded cases under adversarial review (task `a894941c72f5cc4e2`).

**SCOPE:** ὥστε + infinitive (result construction) only. Does NOT cover: (a) illative-ὥστε + finite verb; (b) ὥστε-clauses >8 words (Phase B territory); (c) cross-verse-initial ὥστε (Phase B); (d) ἵνα result clauses (governed by separate rule if one exists).

**Precedence vs. R9 (never-end-on-function-word):** R9 states that a line may not end on a conjunction. When a ὥστε-clause is split onto its own line (word count exceeded, illative, or cross-verse), ὥστε leads the new line — it does NOT stay at the end of the prior line. R25 never conflicts with R9 in the merge case (merged lines never end on ὥστε). R9 takes precedence for the split case.

**Validator:** `validators/colometry/check_r25_hoste_consecutive_result.py`

**Phase A applied:** 2026-05-11 (20 merges). Phase B (9-12 word cases, cross-verse) deferred to future session.

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

**When a single ATU crosses a Stephanus 1551 verse boundary, the line stays intact.** The verse boundary is an editorial overlay (imposed 1551 on a text that already had its own rhetorical structure); it does not constrain ATU formation. The ATU is formed by grammatical/rhetorical continuity, and the versification is carried along by an inline superscript marker.

**Canonical example — Matt 3:1-2:**

```
3:1
Ἐν δὲ ταῖς ἡμέραις ἐκείναις παραγίνεται Ἰωάννης ὁ βαπτιστὴς
κηρύσσων ἐν τῇ ἐρήμῳ τῆς Ἰουδαίας ²καὶ λέγων·

3:2
Μετανοεῖτε,
```

The speech-intro `κηρύσσων ... καὶ λέγων·` is one ATU (a preaching-speech-intro bond). SBLGNT places `καὶ λέγων·` at the start of 3:2. The cross-verse rule keeps `κηρύσσων ... καὶ λέγων·` as one ATU on a single line; the `²` superscript preserves the versification reference.

**Procedure (per `handoffs/04-editorial-workflow.md`):**

1. **Identify the boundary** — grammatical continuity indicator (participle chain, suspended main verb, subject/verb straddle, speech-intro straddle, discourse-adverb leading the next clause, etc.).
2. **Merge in place** — the ATU lives in the *earlier* verse's block (where its lead word sits), with the content that SBLGNT attributes to the later verse attached inline after a superscript digit (`²`/`³`/`⁴`/...) indicating where the later verse begins visually.
3. **Mirror in English** — the same merge, the same superscript position.
4. **Cite using the earlier verse's reference** when referring to the merged ATU.

**Both directions apply.** The Matt 3:1-2 case has SBLGNT pushing a word *forward* into the next verse (`καὶ λέγων·` is SBLGNT-3:2 but ATU-3:1). The John 4:35-36 case has the opposite: SBLGNT assigns `ἤδη` to the end of 4:35, but R8 makes `ἤδη` the lead of the clause in 4:36 (`ἤδη ὁ θερίζων μισθὸν λαμβάνει`). Same convention applies — keep the ATU intact (in the earlier verse's block, where `ἤδη` sits), mark the versification boundary with a `³⁶` superscript before the post-boundary content:

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

**Infrastructure:** `scripts/verify_word_order.py` recognizes these markers and splits a merged line at each superscript digit for per-verse word-order integrity comparison against SBLGNT. `scripts/build_books.py` renders superscripts as `<sup class="verse-marker">` HTML anchors so citation lookups still land at the exact inline location. A reader searching for "Matt 3:2" still finds `Μετανοεῖτε,` at the top of the 3:2 block; the superscript in 3:1's line is an additional anchor for the mid-line boundary.

**Why codify this in the canon?** Versification is not original. ATU formation is. When they collide, the rule is clear: ATU wins, versification becomes a secondary annotation. This principle sits alongside "editorial punctuation is not original; hide in display" (see feedback_no_editorial_overlays_as_signal) and "don't let editorial overlays drive structural decisions" — the general posture of seeing past 1550s editorial conventions to the text's own structure.

<!-- ===== M4-GNT-1 ===== -->
### 3.18 M4-GNT-1: Subject-Orphan Predicate Completion (Greek Instantiation)

**Status:** Active
**Category:** A (Mechanical, mandatory) for closed-list-eligible subject shapes; B (Editorial) for length-backstop or multi-line restructuring cases
**Decidability:** Surface-pattern + MorphGNT-aware (5 Greek-specific exclusions apply before firing)
**Layer:** 3
**Framework anchor:** Corpus-specific operational instantiation of framework M4 (fragmented atomic thought-unit; see [`atu-method/docs/framework.md §1.5`](../../atu-method/docs/framework.md)). GNT sibling of M4-BoFM-1 (codified 2026-05-11 in `readers-bofm`).

**Rule.** When a v4/grk line whose content is a **subject NP** (any of the closed-list-eligible shapes below) terminates in `,` or `·`, AND the immediately-next v4/grk line is a **bare finite predicate** (starts with finite verb, has no leading connective, has no independent subject NP on the same line), the predicate-line MUST be merged onto the subject-line as a single ATU. The atomic-thought principle governs: a subject NP standing alone is not an atomic thought (no predication), a bare predicate standing alone is not an atomic thought (no anchor on the line), and the merged subject+predicate IS one atomic thought (one proposition / one image).

**UD signature (surface-level).**
~~~yaml
trigger:
  line_A:
    role: subject_NP_of_eligible_shape  # see SUBJECT_SHAPES_M4_GNT1 closed list
    terminal_punct: comma_or_ano_teleia
    no_finite_verb_on_line_A: true      # G5 override for participial-only line A
  line_B:
    has_finite_root: true
    no_independent_nsubj: true
    no_leading_connective: true
    no_G1_attributive_participle_lead: true
    no_G3_periphrastic_lead: true
action: MERGE_FORWARD
length_backstop: merged > 130 chars -> REVIEW
~~~

**Closed lists (machine-readable).**
~~~yaml
SUBJECT_SHAPES_M4_GNT1:
  - C1_vocative_address_NP      # household-code vocative subject: Αἱ γυναῖκες, / οἱ ἄνδρες, etc.
  - C2_np_with_appositive       # NP-with-appositive subject: ὁ κύριος, ὁ θεὸς τῶν πνευμάτων,
  - C3_np_with_participial      # NP-with-participial modifier (G5 override applies)
  - C4_np_with_relcl            # NP-with-relative-clause subject
  - C5_biographical_intro       # καί τις X ὀνόματι Y, [appositive,] [participle,]

LEADING_CONNECTIVES_BLOCK_FIRE:
  # Line B starts with any of these → NOT a bare-predicate orphan
  - καί, δέ, γάρ, οὖν, ἀλλά, ἤ, εἰ, ὅτι, ἵνα, ὅταν, ὅτε, ὡς, ὥστε,
    ὅπου, ὁ, ἡ, τό  # article lead = new phrase, not bare predicate
~~~

**Scope.** A v4/grk line whose content is a subject NP of one of the closed-list-eligible shapes, with the matrix predicate orphaned on the immediately-next v4/grk line. The rule applies after Tier 1 vetoes (Layer 1 break-legality), formula integrity (R6, R11), and complement integrity (§3.5 R10) have settled. M4-GNT-1 is the GNT-specific Tier 4 merge-override operationalization of framework M4.

**Greek-specific exclusions (closed list — G-exclusions).**
1. **G1: Attributive participle on line B** (modifier of the NP on line A, not the main-clause verb). When line B begins with a participial form that is attributive to the NP on line A (e.g., `ποιῶν ναοὺς` modifying `ἀργυροκόπος` on line A), the participle is a modifier continuation, not a bare finite predicate. **STAY-SPLIT.** Acts 19:24 canonical instance.
2. **G2: Verbless nominal-sentence line A** (predicate NP or predicate ADJ; complete by Greek ellipsis). When line A is itself a complete verbless clause (implied `ἐστίν`), the following line is a separate predication, not the orphaned predicate of line A. **STAY-SPLIT.** Luke 1:38 `Ἰδοὺ ἡ δούλη κυρίου·` canonical instance.
3. **G3: Periphrastic-construction line B** (ἦν/ἐστίν/ἔσται + participle forming a single periphrastic predicate). When line B is the verbal component of a periphrastic formed with a participle on line A or an immediately-prior line, the periphrastic is a Layer 1 indivisible unit (R5). **STAY-SPLIT** (handled by R5 before M4-GNT-1 fires).
4. **G4: Doxological vocative-NP + infinitival-complement** (pattern: `Ἄξιος εἶ` + vocative NP + `λαβεῖν` infinitive). When line A is a doxological address unit and line B is the infinitival complement of a prior predicate, the infinitive is a complement (§3.5 Period Test governs), not a bare orphan predicate. **STAY-SPLIT.**
5. **G5: Line A has only participial verbs (no finite indicative/subjunctive)** → eligible for merge *despite* the surface `a_verb` heuristic firing on line A. The participial-only line A is not a complete clause; its subject NP is still orphaned from the finite predicate on line B. M4-GNT-1 FIRES. Matt 1:19 canonical instance (`δίκαιος ὢν καὶ μὴ θέλων αὐτὴν δειγματίσαι,` / `ἐβουλήθη`).

**Universal exclusions (same as M4-BoFM-1 cross-corpus variants).**
6. **R7 vocative-only on line A.** When line A is a bare vocative address unit (e.g., `ἀδελφοί,`), the vocative is not the predicate's subject. R7 governs vocative indivisibility; M4-GNT-1 does NOT fire.
7. **R11 / J3 speech-act parentheticals.** When line A ends in a speech-intro tag (e.g., `λέγει·`), the construction is R11-territory; not a subject-predicate orphan pattern.
8. **Leading connective on line B** (καί, δέ, γάρ, etc.). Line B is a coordinate or subordinate clause, not a bare-predicate orphan. M4-GNT-1 does NOT fire.
9. **Line A is a PP-object, not a grammatical subject.** When the NP on line A is governed by a preposition (e.g., object of `ἐν`, `διά`, `πρός`), it is not the subject of any following predicate. M4-GNT-1 does NOT fire.
10. **Line A is already a complete clause** (contains its own finite subject + predicate). When line A has a full finite verb whose subject is explicitly stated, line B is a coordinate clause, not a predicate orphan. M4-GNT-1 does NOT fire.
11. **R19 genitive-absolute on line B.** When line B begins with a genitive absolute (anarthrous gen ptc + agreeing gen subject), R19 governs and fires first. M4-GNT-1 does not layer on top.

**Precedence.** Tier 4 merge-override (framework M4). Yields to Tier 1–3 rules (Layer 1 vetoes, formula integrity, complement integrity, vocative integrity R7, genitive-absolute R19). When R7 and M4-GNT-1 fire on the same locus (vocative NP + orphan predicate), R7's interpretation governs if line A is purely a vocative address; M4-GNT-1 governs if line A is a substantive subject NP that happens to be in the vocative or addressed form (household-code pattern: `Αἱ γυναῖκες,` is both a nominative subject and an addressed group — M4-GNT-1 fires because the nominative grammatical function dominates).

**Examples.**

- *Compliant (C1 household-code vocative-subject):* `Αἱ γυναῖκες, ὑποτάσσεσθε τοῖς ἀνδράσιν, ὡς ἀνῆκεν ἐν κυρίῳ.` (Col 3:18 after merge)
- *Compliant (C1 household-code):* `οἱ ἄνδρες, ἀγαπᾶτε τὰς γυναῖκας` (Col 3:19, Eph 5:25 after merge)
- *Compliant (C1 household-code):* `Τὰ τέκνα, ὑπακούετε τοῖς γονεῦσιν κατὰ πάντα,` (Col 3:20 after merge)
- *Compliant (C1 household-code):* `οἱ δοῦλοι, ὑπακούετε κατὰ πάντα τοῖς κατὰ σάρκα κυρίοις,` (Col 3:22 after merge)
- *Compliant (C1 adverbial-address):* `ὁμοίως, νεώτεροι, ὑποτάγητε πρεσβυτέροις.` (1 Pet 5:5 after merge)
- *Compliant (C5 biographical-intro):* `καί τις γυνὴ ὀνόματι Λυδία, πορφυρόπωλις πόλεως Θυατείρων, σεβομένη τὸν θεόν, ἤκουεν,` (Acts 16:14 after merge)
- *Compliant (C3 NP-with-participial, G5 override):* `Ἰωσὴφ δὲ ὁ ἀνὴρ αὐτῆς, δίκαιος ὢν καὶ μὴ θέλων αὐτὴν δειγματίσαι, ἐβουλήθη λάθρᾳ ἀπολῦσαι αὐτήν.` (Matt 1:19 after merge)
- *Compliant (C2 NP-with-appositive, deity NP):* `ὅτι αὐτὸς ὁ κύριος ἐν κελεύσματι, ἐν φωνῇ ἀρχαγγέλου καὶ ἐν σάλπιγγι θεοῦ, καταβήσεται ἀπʼ οὐρανοῦ,` (1 Thess 4:16 after merge)
- *Already compliant (C2 NP-with-appositive, deity NP):* `καὶ ὁ κύριος, ὁ θεὸς τῶν πνευμάτων τῶν προφητῶν, ἀπέστειλεν τὸν ἄγγελον αὐτοῦ` (Rev 22:6 — already one line; no merge required)
- *Already compliant (C4 NP-with-appositive):* `Ὅθεν, ἀδελφοὶ ἅγιοι, κλήσεως ἐπουρανίου μέτοχοι, κατανοήσατε τὸν ἀπόστολον` (Heb 3:1 — already one line; no merge required)
- *Excluded (G1 attributive-participle):* `Δημήτριος γάρ τις ὀνόματι, ἀργυροκόπος,` / `ποιῶν ναοὺς ἀργυροῦς Ἀρτέμιδος παρείχετο...` — line B `ποιῶν` is attributive participle of `ἀργυροκόπος`; G1 exclusion. STAY-SPLIT. (Acts 19:24)
- *Excluded (G2 verbless nominal-sentence):* `Ἰδοὺ ἡ δούλη κυρίου·` — line A is a complete verbless clause by Greek ellipsis; `γένοιτό μοι` is a separate predication. G2 exclusion. STAY-SPLIT. (Luke 1:38)
- *Excluded (R7 vocative):* bare `ἀδελφοί,` alone on a line — pure vocative address, not a grammatical subject. R7 governs; M4-GNT-1 does NOT fire.

**Implementation.**

- Validator: `validators/colometry/check_m4_gnt_1_subject_orphan.py` (surface-pattern with G1–G5 exclusions; MorphGNT-aware Stage 2 filter)
- Applier: surface-pattern MERGE_FORWARD; 2026-05-11 sweep applied 11 clean Cat A merges across Col, Eph, 1 Pet, Acts, Matt, 1 Thess
- Closed-list definitions: §SUBJECT_SHAPES_M4_GNT1 (inline above)
- Audit trail: task `a0d7d74092a145179` (sweep audit completed 2026-05-11; ~149 surface candidates → ~15-20 clean Cat A after G-exclusions)
- Cross-corpus: sibling of M4-BoFM-1 (`readers-bofm`); framework anchor at `atu-method/docs/framework.md §1.5`

**Defensibility (WHY this rule exists).** The GNT canon's pre-existing rules handled complement integrity (R10 ὅτι-complements, §3.5 Period Test) and genitive-absolute own-line (R19) and participial discipline (R20), but did not operationally codify subject→predicate integrity — the dual of R10's predicate→complement integrity. The atomic-thought test in §1 served as foundational principle but was enforced editorially, not mechanically. The household-code cluster in Col 3 and Eph 5-6 exposed the pattern systematically: the apostolic household-code format consistently opens each directive with a bare nominative address NP (`Αἱ γυναῖκες,`, `οἱ ἄνδρες,`, `Τὰ τέκνα,`, `οἱ δοῦλοι,`) that is simultaneously the grammatical subject and the addressed group — and then places the imperative predicate on the next line. Split, each line fails the No-Anchor or atomic-thought test. Merged, each is one clear ATU: identity + directive. The biographical-introduction pattern (Acts 16:14, Matt 1:19) and deity-NP pattern (1 Thess 4:16) confirm the principle extends across the corpus beyond the household-code genre.

**HOW WE KNOW.** Sweep audit task `a0d7d74092a145179` (2026-05-11): ~149 surface-pattern candidates across all 27 NT books, narrowed to ~15-20 clean Cat A cases after applying all 5 G-exclusions + universal exclusions. The household-code cluster (8 cases), biographical-introduction cluster (3 cases), and deity-NP cases (2) were identified as the cleanest instances. Acts 19:24 (G1) and Luke 1:38 (G2) were confirmed exclusions by structural analysis.

**SCOPE.** A v4/grk line pairing where: (a) line A carries a grammatical subject NP of one of the five closed-list shapes, terminating in `,` or `·`; (b) line B is a bare finite predicate with no leading connective and no independent subject; (c) none of the 11 exclusions (G1–G5 + 6 universal) fires. Does NOT cover: bare vocative addresses (R7 governs), periphrastic constructions (R5 governs), verbless nominal sentences complete by ellipsis (G2), attributive-participle continuations on line B (G1), or lines where a leading connective on line B signals coordinate/subordinate structure.

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

**After any pipeline change (regen logic, scanner rewrite, validator update), manually diff the four gold-standard regression-test chapters above (Mark 4, Rom 2:12-13, Acts 1:1-4, Heb 1:3) — v4 + v4/eng-kjv, before and after. If any of the four breaks, the pipeline change is suspect.**

### The No-Anchor Test (Default Case of the Generative Force)

**What it checks:** Does every ATU carry at least one thought-marking anchor (finite verb, infinitive, predicate participle, or independently-predicated substantive head)?

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

**Pointer to framework.** Proposal requirements (defensibility capture — WHY / HOW WE KNOW / SCOPE), mandatory-audit triggers (12 categories), audit-skippable categories, audit-evidence in commit messages, self-test before commit, self-consistency audit trigger, and proposed-rule adoption protocol are codified at [`atu-method/docs/framework.md §7.2–§7.8`](../../atu-method/docs/framework.md). This canon does not duplicate that prose. The GNT-specific mechanical audit gate is the `validators/hooks/commit-msg` pre-commit hook (installed 2026-04-26; source at `validators/hooks/`).

**GNT-specific provenance and scope:**

### Precedent for colometric layout

We are not inventing a practice; we are recovering one with ancient and modern precedent.

- **Codex Bezae (D 05), 5th c.** — Luke/Acts laid out colometrically; each line a sense unit. Empirical comparison: current corpus agrees with Bezae at **61.3%** (caveat: Bezae's column width ~25-30 characters means many breaks are forced by writing space; agreement metric is meaningful but Bezae is not a colometric gold standard — it is one empirical datum).
- **Codex Claromontanus (Dp 06), 6th c.** — colometric Paul.
- **Jerome's Latin Vulgate *per cola et commata*, 4th c.** — Jerome's preface to Isaiah explicitly describes laying out the prophetic books "by cola and commas" for ease of reading.
- **Royal Skousen, *The Earliest Text* (2009/2022)** — modern precedent on the Book of Mormon; the trigger for this project's analogical extension to the GNT.

### Scope: what this project is NOT

- Not chiasm analysis (downstream rhetorical work our edition enables)
- Not discourse grammar (Runge 2010; Levinsohn 2000 — useful for pragmatics, not colometric)
- Not manuscript comparison (Swanson et al.)
- Not paragraph-level pagination (NA28, UBS5, SBLGNT — we rely on their text; everything about layout is ours)
- Not a test of any particular psycholinguistic or rhetorical-theory framework — we are producing a reading edition; theoretical alignment is a downstream question that a later phase may ask

### v4 as methodology application (not hand typing)

A reproducibility distinction that matters for scholarly defensibility:

- **v0–v3** (earlier stages of the text pipeline) are **bit-exactly reproducible** from source. Running the scripts on the source inputs produces byte-identical output.
- **v4/grk** is **methodologically checkable**, not bit-exactly reproducible. It is where the documented colometric methodology is *applied* through a mix of scan-and-apply tools (scripts), rule-application validators, and case-by-case editorial decisions where the rule set underdetermines. A different editor following the same canon should arrive at largely the same breaks — within the Category B/C bands of legitimate editorial variation.

**Implication:** v4 is not "hand-typed prose formatted nicely". It is the methodology *in operation*. Every line break in v4 either (a) applies a Category A rule mechanically, or (b) reflects a Category B/C editorial call traceable to a canon rule plus a defensibility rationale. The corpus is auditable against the canon; it is not reproducible from the canon alone, because the editorial calls require human (or Claude-with-Stan) judgment.

This matters for:
- **External reviewers** evaluating whether v4 is a "scholarly product" or a "personal annotation" — it is the former, grounded in an articulated methodology.
- **Future Claudes** auditing whether a corpus edit is defensible: trace it to a canon rule + warrant. If it can't be traced, it's a methodology gap (add to canon) or a bug (fix in corpus).
- **The scan-and-apply pattern**: mechanical sweeps ARE methodology application, not overrides of it. The script encodes a Category A rule; running it applies the rule at scale.

### §6.5 — Mandatory-audit triggers for canon changes (GNT-specific pointer)

**Pointer to framework.** The 12 mandatory-audit triggers, audit-skippable categories, commit-message declaration discipline, self-test, and audit-dispatch parallelization protocol are codified at [`atu-method/docs/framework.md §7.3–§7.6`](../../atu-method/docs/framework.md). Claude reads those sections literally before any GNT canon commit.

**GNT-specific audit-trail conventions:**
- Audit-evidence references in GNT commit messages cite parallel-agent verdicts and §10 Update Log entries.
- The `validators/hooks/commit-msg` hook mechanically gates commit messages touching this canon file against §7.5 audit-evidence keywords.
- Provenance note: the trigger list was codified in GNT on 2026-04-24 (see §10 Update Log entry 2026-04-24 for the cross-project-import context and GNT-side risk profile). It was subsequently promoted to the universal framework on 2026-05-12 (§7 in atu-method/docs/framework.md); this section now points to that universal statement.

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

### Marked Word Order (Fronting Paradox)

**The fronting paradox — marked word order argues for MERGE, not split.** When a grammatically tight unit (verb + its required-case complement, or other bound constituent) appears in a *marked* word order — e.g., object fronted before its governing verb — the natural editorial instinct is to split at the fronted element as a way of "visualizing the emphasis." **This instinct is wrong.** The rhetorical effect of fronting depends on the grammatical unity *staying intact*. The marked arrangement is felt as emphatic precisely because the hearer processes the fronted element in a non-default position *within a single breath unit*. Splitting at the fronted-element boundary mechanizes the emphasis — it imposes a pause that was not in the original oral delivery — and paradoxically *diminishes* the rhetorical force.

This subsection is the GNT-specific anti-scope-creep rule operationalizing the "reaching-for-split" warning under §1 Imposing-vs-Revealing scope discipline. It is not in the universal framework (no fronting / marked-word-order section in `framework.md`); it lives here because the rule is calibrated against Greek's case-marked freedom of word order — a per-language phenomenon.

**Case studies:**

- **Gal 2:9 — split** (pillars characterization on own line): two distinct thoughts (the named persons vs. their ironic characterization). Subject + substantival-participial-phrase appositive, where the appositive is six words, non-trivial, and introduces the *dokountes* motif. Grammatical warrant for split is the substantival-participle-as-own-thought rule.
- **Gal 2:10 — merge** (fronted `τὸν πτωχόν` kept with `μνημονεύωμεν` on one line): `μνημονεύω` requires genitive for its object. The fronted genitive + restrictive `μόνον` create a marked word order whose rhetorical force depends on the grammatical unity staying intact.

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

**Patriarch-deity-triad (Exod 3:6 LXX quotation; R18a-GNT, ported from BoFM R18a 2026-05-11).** The Exodus citation *ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ* (and its anchor-shared variants) appears at five NT loci: Matt 22:32, Mark 12:26, Luke 20:37, Acts 3:13, Acts 7:32. The triad-as-unit functions as a single fixed referring expression to YHWH; severing the span across lines fractures the unitary deity-reference into the apparent enumeration of three deities. **Rule.** A verse-block whose tokens contain `θεός`-lemma governing `Ἀβραάμ`, followed (in order, within the same verse) by `Ἰσαάκ`, followed by `Ἰακώβ`, MUST keep the entire spanning sequence whole on a single line. **Status:** Active. **Category:** A (Mechanical, mandatory). **Layer:** 3 (sister to the Revelation frozen-formula note above; ported from BoFM R18a). **Closed list of attested variants:** fully-distributed (`ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ` — Matt 22:32, Mark 12:26); anchor-shared (`τὸν θεὸν Ἀβραάμ καὶ θεὸν Ἰσαάκ καὶ θεὸν Ἰακώβ` — Luke 20:37); compressed (`ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ` — Acts 3:13, Acts 7:32); extended-lead (`ὁ θεὸς τῶν πατέρων σου, ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ` — Acts 7:32 full). **Exclusions.** (1) Personal-name list without θεός anchor (e.g., Acts 7:8 patriarchal genealogy) — coordinate-NP-object territory, R18a-GNT does not fire. (2) Non-canonical triad orderings — Ἀβραάμ → Ἰσαάκ → Ἰακώβ is the only attested order; no reversals. (3) Lead-in title phrases on separate lines (e.g., `ὁ θεὸς τῶν πατέρων ἡμῶν,` at Acts 3:13 line 60) — appositional continuations stay on their own line; the triad-line itself must be whole. **Precedence.** Tier 2 indivisibility, parallel to BoFM R18a §3.5 Tier 2. Wins over subtractive vetoes internal to the triad span. Where the triad follows a speech-intro verb (Mark 12:26: `λέγων·`, Luke 20:37: `ὡς λέγει`), the speech-intro lands on its own prior line per R11 and the triad opens the content line. **Validator:** `validators/colometry/check_r18a_patriarch_triad.py`. **Corpus survey (2026-05-11).** Matt 22:32, Mark 12:26, Acts 3:13 already compliant (triad whole); Luke 20:37 violation (triad split across lines 211-212); Acts 7:32 Category B Stan-review (triad whole on line 153, but extended formula `Ἐγὼ ὁ θεὸς τῶν πατέρων σου` on line 152 is appositional-lead boundary judgment).

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

Codex Bezae's line breaks reflect a mixture of ATU-level decisions and physical layout constraints. The column width (~25-30 characters) means many breaks are forced by writing space. Agreement metrics are meaningful but Bezae cannot be treated as a colometric gold standard without this caveat.

### Standalone Verb Test

Intransitive verbs of motion or state change can stand alone as a complete predication: eperthee (he was taken up), ekaumatisthe (it was scorched), anabainei (it grows up). The subject is implied, no object is required.

Transitive verbs and speech verbs CANNOT stand alone — they need their complement. eipen (he said) without its speech is a fragment. These must stay with their complement or function as a speech introduction followed by content.

### Four-Tier Pipeline

**Tier 1 — Pattern-Matching (v1-colometric).** Script: `auto_colometry.py`. Rule-based surface-text pattern matching. Known limitation: cannot detect participial phrases, genitive absolutes, or clause boundaries not marked by a surface conjunction.

**Tier 2 — Syntax-Tree-Driven (v2-colometric).** Script: `v2_colometry.py` using `macula_clauses.py`. Uses Macula Greek syntax trees (Clear Bible, CC-BY 4.0). Adds participial phrase isolation, genitive absolute identification, clause boundaries in long prose.

**Tier 3 — Rhetorical Pattern Layer (v3-colometric).** Applied on top of v2. Tricolon/bicolon stacking, men/de contrast display, climactic parallelism.

**Tier 4 — Editorial Hand (v4/grk).** Stan's hand editing. Makes final decisions. All 260 chapters hand-edited.

**Data sources:**
- **Macula Greek** (github.com/Clear-Bible/macula-greek) — SBLGNT syntax trees, CC-BY 4.0
- **MorphGNT** (github.com/morphgnt/sblgnt) — SBLGNT morphological tagging, CC-BY-SA

### Validation Benchmarks

| Benchmark | What it tests | Limitation |
|-----------|---------------|------------|
| **Marschall** | Scholarly colometric analysis of Paul | Limited to 2 Cor 10-13 |
| **Bezae** | Ancient scribal ATU-level practice | Physical layout constraints |
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

### 2026-05-02 — N=2 Adjudication Principle named in §1

Promoted the substance encoded in M1's existing tie-breaker language to a named, cross-cutting principle in §1 (between Imposing-vs-Revealing corollaries and the Acts 1:9 Showcase). Cross-project provenance: BofM-Reader coined the principle 2026-04-23; Tanakh-Reader ported 2026-04-26; GNT-Reader codifies 2026-05-02.

**What the principle resolves.** Several canon rules mandate MERGE for N=2 coordinate constructions (M1 gorgianic pair, R8 short-coordinate default, R28 textual-asymmetry, two-member coordinate clausal series); structural justification 1 mandates SPLIT for formally-marked parallel series. At N=2 both rules can fire on the same construction. Pre-codification, this collision was handled by M1's local tie-breaker; post-codification, the cross-cutting principle generalizes the resolution.

**The principle's logic** (full text in §1):
1. Synonymy / hendiadys / binomial idiom → merge wins.
2. Distinct semantic domains → M1's bonded-pair grounds withdraw, but the M1 strict-application caveat applies (check other merge protections — M2-M4, R8, R11, R28, default-merge — before flipping to split).
3. Default to merge when ambiguous.

**Scope boundaries:**
- Does NOT apply at N=3+ (parallel series wins; cognitive prong recoverable from series itself).
- Does NOT apply to appositional constructions (synonymy is definitional; appositives have own rules).

**M1 retains its specific tie-breaker text;** the new §1 subsection is the cross-cutting statement that M1's tie-breaker instantiates. M1's tie-breaker now carries a forward reference to §1 N=2 Adjudication Principle.

**Audit-status per §6.5:** Audit dispatched and applied. **Triggers fired:** #1 (named-category extension — promoting an implicit substance to a named, cross-cutting principle is a named-category change); #2 (rule status promotion — M1's tie-breaker substance now also exists at §1 cross-cutting level); #11 (cross-project import from BofM-Reader 2026-04-23 + Tanakh-Reader 2026-04-26). **Verdict: PROCEED WITH MODIFICATIONS** — two precision corrections to the "problem" paragraph applied: (a) R28 (textual asymmetry) removed from the lead list of merge-mandating rules — R28 governs parallel-passage comparison, not within-construction N=2 bonding; its proper home is step 2's secondary check-list. (b) R8 (framing-marker attachment) removed from the lead list and clarified in a parenthetical — R8 governs framing-marker attachment (ἰδού, διό, οὖν), not coordinate-pair bonding; it appears in step 2 as a secondary protection but does not generate the N=2 collision this principle adjudicates. Both modifications applied verbatim. The core principle (three-step logic, scope boundaries, cross-project provenance) audited as sound: substance matches M1 without over-extension; appositional exclusion accurately routes those cases to existing rules (R18, divine-title appositives); cross-project precedent verified against Tanakh canon line 1253 ("N=2 Adjudication Principle: from BoFM 2026-04-23") and Tanakh §1 named subsection.

**Why named now:** discoverability. The substance has been encoded in M1's tie-breaker for some time but readers entering the canon at §1 had no signal that a generalized N=2 adjudication principle exists. The named subsection at §1 surfaces it; the cross-reference in M1 grounds it specifically. Cross-project parallel ensures readers consulting any of the three sibling canons see the same principle.

---

### 2026-05-01 — Terminology migration: "sense-line" → "atomic thought unit (ATU)"

Stan greenlit a project-family-wide terminology migration after a sync with the BofM-Reader sibling project. Both terms had been treated as synonyms in canon §0, with "sense-line" as the historical-Skousen citation form and "atomic thought unit" as the internally-generated criterion-defined descriptor. Stan's reframe: the two are NOT synonymous in his model — sense-line carries Skousen's grammatical-unit framing; ATU names what the line actually IS in this method (a unit defined by what a reader can process as a single complete thought). The rename isn't a label swap; it's a claim about intellectual provenance and method distinctness.

**Lineage now codified in §0 Genesis paragraph:** Skousen's "sense-line" → retrospectively-named "thought-line" framing (visible in the archived 2026-04-20 scholarly-framing document and earlier session dialogue, but never canonically named as a stage at the time) → present **atomic thought unit (ATU)** model. Skousen credit preserved with full citation; the historical kernel is acknowledged, but the unit name now matches the criterion that defines it. The "thought-line" intermediate is named in retrospect — the framing existed before the term ATU was load-bearing — not as a contemporaneously-recognized stage.

**Stratification (per BofM-Reader's framing, adopted here):**

- **Yes-rename territory (scholarship + method docs):** canon (this file), CLAUDE.md, handoffs/*, README.md, index.html help/landing copy, data/syntax-reference/greek-break-legality.md, research/citations/*. "Sense-line" → "atomic thought unit (ATU)" or just "ATU" after first-use definition per document.
- **Leave-alone (internal plumbing):** CSS class names (.line, .gk, .en), data attributes, script filenames, v1/v2/v3-colometric/ directory paths, in-script comments and docstrings (unless scholarship-explanatory). These are internal-historical names; renaming them is high-cost CSS / build-pipeline / git-history churn for no reader benefit.
- **Preserve as historical record:** §9 superseded formulations and §10 update entries dated before today retain their original "sense-line" wording. Rewriting history would falsify the chronological trail.

**Term-discipline established for the new vocabulary:**

- **Acronym convention:** spell out "atomic thought unit (ATU)" on first use within each document; abbreviate to "ATU" thereafter. Standard academic acronym discipline.
- **Bare "line" preserved for typographic sense:** when prose discusses what each unit IS (the cognitive target), "ATU" is right; when prose discusses how ATUs are rendered (line-wrap, line-final tokens, layout), "line" stays. This mirrors how scholarly writing usually keeps the unit and its rendering as separate concepts.

**Cross-project coordination:** This is a method-family rename across three repos (BofM-Reader, Tanakh-Reader, GNT-Reader). Each repo's canon-extension gate fires per its local §6.5 (or analogous) trigger; each canon's §10 entry should narrate the same Skousen → thought-line → ATU provenance story so future readers see one rationale, not three.

**This commit's scope (GNT only):** active-prose rewrites in §§0-8. §9 and §10 historical entries preserved verbatim. Adjacent surfaces (CLAUDE.md, handoffs, README, index.html, etc.) follow in subsequent commits as the migration progresses.

**Audit-status per §6.5:** Three triggers fired, not one. **Trigger #1 (new named category):** "thought-line" introduced as a named — albeit retrospectively-named — intermediate stage in the lineage taxonomy. **Trigger #2 (rule status promotion):** the criterion-defined ATU is promoted from clarifying parenthetical (in the prior §0 "We use it here in an expanded sense") to primary load-bearing term. **Trigger #11 (cross-project import):** this is a method-family rename adopted from the BofM-Reader sibling project's parallel discussion. GNT-internal precedent: the archived scholarly-framing document `private/01-method/archive/colometry-canon-scholarly-framing-2026-04-20.md` already used "atomic thought unit" language at line 83, providing GNT-internal grounding for the term independent of the cross-project sync. Audit dispatched in parallel with this commit; verdict was PROCEED WITH MODIFICATIONS; both required modifications applied: (a) "thought-line" hedged as retrospective naming in both §0 and this §10 entry, (b) trigger #11 explicitly addressed with the GNT-internal precedent citation above.

---

### 2026-04-28 (later³) — Step 0 item 3 correction: validator-implementation check after-the-fact

After landing the Step 0 commit (later) and the hook-port-soft commit (later²), Stan asked whether the corpus needed any audit in light of the new modifications. A targeted Sonnet check on the R18 validator implementation (the rule my Step 0 item 3 example invoked) surfaced two factual errors in my Step 0 wording:

1. **R18 in canon §3 (line 499)** is "Vocative rule (three-way refined)." Canon nowhere uses the phrase "verse-initial vocative." The phrase exists only in the validator docstring (`validators/colometry/check_r18_vocative.py:5`) and was imported into Step 0 as a fabricated canonical-sounding example.
2. **Validator implementation** checks for same-line 2p-element absence (vocative + non-2p finite verb on same line + no 2p verb or 2p pronoun on same line) — `validators/colometry/check_r18_vocative.py:171-196`. My Step 0 framing "no preceding 2p anchor in scope" misstated the implementation: "scope" is same-line in the validator, not preceding-context.

Both errors are the same class — Step 0 was solving a non-problem (R18 doesn't use verse-position as a signal in our canon) with a description that didn't match the implementation. The Step 0 item 3 wording is now simplified to drop the false specifics: "R-rules fire on grammatical evidence, not on verse position. Where a validator docstring or didactic description uses 'verse-initial' or similar positional language, the actual detection criterion is grammatical (morphological context, anchor presence/absence, etc.), not the position itself."

**Process lesson:** when canon §1 cites implementation behavior, the §6.5 audit should include reading the implementation, not just canon and memory. The original Step 0 audit (later) was scoped to canon-only context per my prompt; it didn't read validator code, so the misstatement passed. Adding to mental discipline: canon-cites-implementation → audit must include implementation read.

**Audit-skippable:** same-session correction of a factual misstatement about validator implementation. No methodology change, no new claims, no closed-list extension. The §6.5 self-test answer to "reclassify or delete previously-settled canon content" is borderline (the content was settled <60 minutes earlier in this session); declared skippable as same-session correction.

---

### 2026-04-28 (later²) — Hook-automated cascade-staleness detection (port-soft from Tanakh)

Pre-commit hook (`validators/hooks/pre-commit`) gained a new Phase 1: cascade-staleness detection. When `data/text-files/v4/grk/` chapter files are staged, the hook now verifies that (a) the corresponding `v4/eng-kjv/` file has matching non-blank line count and (b) `books/<slug>.html` is also staged. If stale, the hook blocks the commit with an instructive message naming the books affected and the cascade commands to run.

**Architectural decision:** PORT-SOFT, not PORT-DIRECT. Tanakh's hook auto-runs `refresh_book.py` and auto-stages regenerated derived layers. The investigation agent flagged real hazards in adopting that pattern for GNT: `regenerate_english.py`'s proportional-redistribute heuristic produces misaligned output when line-counts change (memory `feedback_verify_cascade_output.md`), and auto-staging would commit that misaligned English before the two-check gate (`verify_word_order.py` + `scan_english_drift.py`) can catch it. The soft port detects staleness and blocks without modifying files; the editor runs the cascade and reviews output before re-staging.

**Trade-off accepted:** the hook does NOT detect the rarer case where Greek edits don't change line count but content semantics shift (e.g., reword a line without splitting it). The two-check gate (memory `feedback_two_check_cascade.md`) still catches this; the hook is first line of defense, not exhaustive.

**Audit-skippable:** code-only change, no canon claim. Architectural decision documented here for the audit trail.

---

### 2026-04-28 (later) — Step 0 Input Filter added to canon §1

Adapted from sibling Tanakh-Reader's "what is never a break signal" preamble in their decision procedure. We had the equivalent corollaries scattered across canon §1's "Imposing vs. Revealing" principle, memory `feedback_no_punctuation_criteria.md`, and `feedback_no_editorial_overlays_as_signal.md`. Promoting them to a closed-list Step 0 at the top of §1 makes the discipline discoverable on first read instead of leaving each editor to assemble it from scattered corollaries.

**Audit dispatched:** Sonnet adversarial agent (parallel with hook-cascade architecture review) ran a four-question audit on the proposed list:

1. *Closed-list completeness:* found one missing item — NA28/UBS5/SBLGNT editorial paragraph divisions (the direct GNT analogue of Tanakh's petucha/setuma). Added as item 6.
2. *Conflict check:* flagged R18.9 "verse-initial vocative" as a potential conflict with item 3 (verse references never a signal). Resolved as not-a-conflict — verse-initial language is detection shorthand for "no preceding 2p anchor in scope," and the break fires on the grammar. Added that clarification to item 3 itself.
3. *Closed-list discipline:* item 1 (punctuation) needs a detection-heuristic carve-out per §3.6 ano teleia practice. Added as a parenthetical to item 1.
4. *Bezae item framing:* the original Tanakh-mirroring "never a break signal" was too strong — §6 explicitly treats Bezae as scholarly comparanda with a 61.3% agreement metric. Reframed item 7 from "never a break signal" to "never an *authoritative* break warrant; consult as comparanda."

**Verdict applied:** PROCEED WITH MODIFICATIONS — all three modifications applied verbatim from audit findings.

**Section placement:** §1, between the opening three-forces paragraph and "Mission and Method" subsection — preamble before the framework opens, per audit recommendation.

**Audit-status for this commit per §6.5:** §6.5 trigger #3 (closed-list extension) — audit dispatched and applied per modifications above. The closed list itself is now part of canon §1, with explicit "new items may be added only after a §6.5 mandatory-audit cycle" gate to keep it closed.

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

After the later⁶ residue-purge commit, Stan asked whether the three vestigial scripts flagged as carry-forward (`diagnostic_scanner.py`, `v3_colometry.py`, `v4_pauline_review.py`) should be retired. I recommended **wide scope, framed as freeze-and-document rather than delete**: the project transitioned from a machine pipeline (v0→v1→v2→v3) to a hand-edited corpus (`v4/grk/` as single source of truth) when v4 reached 260/260 coverage. The producer scripts have been operationally vestigial since then; the documentation hadn't caught up. Stan greenlit ("be very careful, redundant, and smart about paralleling/double-checking, but proceed").

**Pre-flight audit (5 parallel Sonnet agents):**

1. **Live-readers audit:** Verified the scope claim "v4/grk is single source of truth, v1/v2/v3 have no live readers." Outcome: scope claim holds — *with one caveat.* `scripts/build_books.py` had a silent runtime fallback to `v3-colometric/` (`GK_FALLBACK_DIR`, `resolve_greek_path()` lines 226–245) that returned a v3 path if a v4 file was missing. Practically dead given v4 completeness, but the code path was active.
2. **Retirement-readiness for the 3 named scripts:** All three confirmed retire-ready — zero inbound module imports, all command-line references are doc-examples. Input paths point at `v3-colometric/` / `v2-colometric/`.
3. **morphgnt_lookup.py + sibling-script status:** `morphgnt_lookup.py` is **ACTIVE** (used by `validators/common.py` as the morphological backend for the production validator suite — must NOT archive). `v4_auto_fix.py` is **ACTIVE**. Five additional scripts surfaced as same-class vestigial: `v2_colometry.py`, `auto_colometry.py`, `build_v0_prose.py`, `generate_english_glosses.py` (SEED-ONLY, predates `regenerate_english.py`), `generate_pauline_english.py` (zero inbound refs).
4. **v4/grk completeness:** 260/260 confirmed (27 books, all expected chapter counts present). The `build_books.py` fallback is unreachable on every normal build.
5. **English-gloss generator status:** `generate_english_glosses.py` is SEED-ONLY (predates incremental-regen tool); `generate_pauline_english.py` is fully vestigial (no inbound refs, V1_DIR fallback).

**Archived this commit (8 scripts → `scripts/archive/`):**

- `build_v0_prose.py` (v0 producer)
- `auto_colometry.py` (v1 producer)
- `v2_colometry.py` (v2 producer)
- `v3_colometry.py` (v3 producer; "last machine tier")
- `diagnostic_scanner.py` (line-auditing tool, superseded by Layer 2 validators)
- `v4_pauline_review.py` (one-time editorial review pass)
- `generate_english_glosses.py` (v4/eng-kjv seeder, superseded by `regenerate_english.py`)
- `generate_pauline_english.py` (Pauline-subset seeder)

**Defensive code change:** Removed the `GK_FALLBACK_DIR` v3-colometric fallback from `scripts/build_books.py`. `resolve_greek_path()` now raises `FileNotFoundError` with a clear message if a v4/grk file is missing. Smoke-tested with `--book mark` and full-corpus build; both pass.

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

**Audit-status for this commit per §6.5:** This is a SCOPE claim about the project's architecture ("v4/grk is single source of truth, v0–v3 are frozen scaffolding"). Per §6.5 trigger #2 (scope claim), an audit was warranted and was satisfied by the 5-agent pre-flight verification documented above. The audit-evidence is the agent verdicts + the §10 entry capturing them; the scope claim has the empirical basis Stan asked for.

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

**Separate observation (not addressed this commit):** the script's input-discovery logic expects `data/text-files/v3-colometric/` paths that no longer exist (corpus structure migrated to `data/text-files/v4/grk/`). Smoke test on `mark-04` chapter failed at file-discovery. Suggests the script may be vestigial overall, not just the breath-unit test. Logged as carry-forward — Stan to decide whether to retire the script entirely or update its path-resolution.

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

**1. Regression-baseline pre-commit hook.** Extended `validators/run_all.py` with three new modes — `--summary` (per-rule dashboard), `--baseline-check` (compare to `validators/.baseline.json`; exit 1 on regression), `--update-baseline` (capture current counts). Created `validators/.baseline.json` with all 9 GNT validators at 0 candidates each. Wrote `validators/hooks/pre-commit` shell script gating commits that touch the canon, syntax-reference, v4/grk corpus, or validators/ — runs `--baseline-check` and blocks if any rule's candidate count increased. Installed to `.git/hooks/pre-commit`.

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

  - "Post-Split Function-Word Recheck" subsection had a duplicate gold-standard chapter list (already stated in the preceding "Gold-standard regression-test chapters — why these four" subsection). Replaced the duplicate list with an inline reference to the first list, preserving the operational instruction ("manually diff these four chapters' v4 + v4/eng-kjv before and after").

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
- `project_substrate_stable_api.md` — v4/grk as read-only API for
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
v4/grk; adding the canon protection prevents future adversarial flips
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

No corpus edits (the 17 candidates were already correctly merged in v4/grk;
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

No v4/grk text changes.

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

No v4/grk text changes. No corpus sweep needed — the 20+ OT-attribution
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

No editorial output changes. No v4/grk text touched.

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

No editorial output changes. No v4/grk text touched. Pure methodology-framing refactor. Rules, merge-overrides, and structural justifications operationally unchanged.

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

### 2026-05-12 — v3.0 Framework-Pointer Restructure

**What changed.** This canon was restructured from v2.0 (framework prose inline in §0/§1/§2/§6) to v3.0 (pointer-only for universal material; GNT-specific rule body preserved in full). The restructure mirrors the BoFM canon v3.0 pattern executed 2026-05-11 in the sibling readers-bofm repo.

**Sections repointed:**
- `## Foundational premise` + `## Posture` (v2.0 preamble) → Part I §0 pointer to `framework.md §0.1/§0.3`; GNT intellectual lineage (Skousen + Stan-arrival narrative) preserved in §0 GNT-specific framing.
- `## Architecture` (three-layer model) → Part I §0 pointer to `framework.md` + `architecture.md` (four-plane model supersedes); GNT-specific Layer 1/Layer 2 details preserved in §0 GNT-specific architecture.
- `## Section 1: The Framework` (three forces, Step 0 input filter, mission/method, container-not-originator, N=2 Adjudication Principle, Acts 1:9 Showcase) → stub pointer in §1; all GNT-specific worked examples (Gal 2:9/2:10, John 10:20, 2 Cor 11:27, Acts 1:9, Luke 3:1-2, John 1:1, etc.) preserved as GNT-corpus instantiations in Part I §1.
- `## Section 2: The Unless Conditions` (five structural justifications + four merge-overrides + complete decision procedure) → pointer to `framework.md §1.4–§1.9`; all GNT-corpus worked examples (Matt 22:30, 1 Cor 10:31, Mark 4:8, Matt 6:19/20, Rom 12:1-2, Matt 2:11, Acts 10:1-3, Pauline salutations, Phil 2:8, Acts 1:9, 2 Cor 6:4-7, Luke 3:1-2, John 1:1, 2 Cor 11:27, Rom 12:15, 2 Pet 2:10, Matt 4:3, Matt 8:15, Matt 23:34, Rom 1:29, Heb 1:1, Mark 1:6) preserved as GNT-corpus instantiations in §2.
- `## Section 6: Precedent and Scope` including §6.5 mandatory-audit triggers → pointer to `framework.md §7.2–§7.8`; GNT-specific provenance (Bezae 61.3% benchmark, Claromontanus, Jerome's Vulgate, Skousen citation, v4-as-methodology-application reproducibility distinction, `validators/hooks/commit-msg` gate, 2026-04-24 codification provenance) preserved in §6 GNT-specific sections.

**Sections kept in full (not touched):** §3 (Rules R1–M4-GNT-1), §4 (Operational Tests), §5 (Register Operationalization), §7 (retired 2026-04-20, number preserved), §8 (Greek-Specific Application), §9 (Superseded Formulations).

**Content NOT duplicated in this canon (pointered to framework.md):** universal mission, method discipline framing, pragmatic stance, scope statement, generative principle, three closed-list syntax-veto ways, image diagnostic, J1–J5 definitions and generating principles, M1–M4 definitions and generating principles, four forces summary table, five-step decision procedure, application-order step-by-step, N=2 Adjudication Principle (named statement), N=3+ cliff, Parallel-List Uniformity Principle, Authorial Asymmetry Principle, autonomy boundary (A/B/C) definitions, mechanical-rule authority, scope/precedence/closed-list diagnostic, 12 mandatory-audit triggers (exact text), audit-skippable categories, §7.5 commit-message discipline, §7.6 self-test, §7.7 self-consistency trigger, §7.8 proposed-rule adoption protocol.

**Audit-status:** Audit dispatched per §6.5 (triggers #1 — named-category reframe "v3.0 pointer-only restructure"; #5 — inline framework prose retired as live content; #11 — structure mirrors bofm v3.0 cross-project import). See commit message for audit evidence.

**Line count:** v2.0 was 2735 lines; v3.0 is ~2459 lines. Reduction of ~276 lines is pure universal-prose retirement plus one GNT-specific relocation (no deletion). The "Marked Word Order (Fronting Paradox)" subsection — Gal 2:9/2:10 case-study pair plus the anti-scope-creep principle that marked word order argues for MERGE not split — was relocated from the retired §1 prose into §8 Greek-Specific Application (its correct home, since the principle is calibrated against Greek's case-marked freedom of word order and is not universal framework content). The §1 Force 3 bullet pointer was updated to reference the new §8 subsection. This relocation was the only modification required by the audit verdict; all other content is either preserved as GNT-corpus instantiation bullets or genuinely universal and now correctly pointered to `framework.md`.

---

*Document created: 2026-04-09. Restructured: 2026-04-16. Canon consolidated: 2026-04-18. Foundational reframing: 2026-04-20. Framework-pointer restructure (v3.0): 2026-05-12.*
