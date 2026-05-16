# Colometry Methodology Canon — Reader's GNT

**Version:** 3.1 (2026-05-13 — focused trim + restructure: §10 history archived to git, §8 research findings retired, §9 compressed to index, §6.5 audit-workflow promoted to §7 slot, Rule Index gains Detector column)
**Predecessors:**
- v3.0 (2026-05-12) — framework extracted to atu-method/docs/framework.md
- v2.0 (2026-04-20) — superseded; framework material lived in §0/§1/§2/§6 prose. Now pointered to atu-method.
- v1.0 (document created 2026-04-09; restructured 2026-04-16; consolidated 2026-04-18) — retained for reference via git log; no longer authoritative as a version.

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
- **Editor making editorial decisions**: focus on §§3-4 and §7 (audit-workflow). Consult §§1-2 for grounding when proposing or evaluating rules.
- **Scholar reading the method as a published artifact**: focus on the GNT-specific framing below (§0 intellectual lineage + §8 Greek-specific application + exegetical convergence).
- **Tracking how a decision evolved**: §§9-10 carry the reasoning trail.

---

## 1. The Framework — Proposition-First, Syntax-Constrained

**Pointer to framework.** The framework specification — generative principle (each proposition splits by default); three closed-list ways syntax forbids splits (Layer 1 mid-phrase prohibitions, complement integrity, formula integrity); image diagnostic (camera-angle test); five structural justifications J1–J5 (formally-marked parallel series, portrait accumulation, speech-act announcement, classical commata, substantive adjunct); four merge-overrides M1–M4 (Gorgianic bonded pair, verb-object clause-nucleus bond, bare-governor indivisibility, fragmented atomic thought-unit); the four forces summary; the five-step decision procedure; the application-order step-by-step (Step 0 input filter through Step 4 diagnostic); the N=2 Adjudication Principle and N=3+ cliff; the punctuation-not-a-signal and versification-not-a-signal stances; the Parallel-List Uniformity Principle; and the Authorial Asymmetry Principle — is codified at [`atu-method/docs/framework.md §1`](../../atu-method/docs/framework.md). This canon does not duplicate that prose.

**GNT-corpus instantiations of the framework:**

- **Step 0 input filter — GNT-specific exclusions.** In addition to the universal filters (punctuation, versification, verse position), GNT editing also excludes from the evidence base: manuscript line divisions in scholarly comparanda (Codex Bezae, Claromontanus — consulted as empirical comparanda, not authoritative warrants; see §6 below); editorial paragraph divisions in printed GNT editions (NA28/UBS5/SBLGNT ¶ marks — never a break signal); and lectionary/pericope divisions.

- **Force 1 (Generative) — GNT resolution principle.** Atomic thought is relative to the author's resolution. For plainer narrative (Mark's simpler scenes), atomic usually means a complete sentence-level predication. For more literary authors (Luke, Paul, John at their most crafted), "atomic" often includes grammatically-independent sub-units — most notably genitive absolutes used as interjectory frames. See §8 for participial and FEF treatment.

- **J1 compound-list break signals — GNT extension: marked-coordinator climactic emphasis (5th signal).** Framework §1.4 J1 lists four compound-list-break signals (elided auxiliary + stacked participles / possessive restart / new demonstrative / attached relative clause). GNT adds a **fifth: marked-coordinator climactic emphasis on a final list-member**. Greek author marks the climax of a list with `ἔτι τε καί` (moreover-and-even), `μάλιστα δέ` / `καὶ μάλιστα` (especially), `μᾶλλον δέ` (rather), `οὐ μόνον ... ἀλλὰ καί` (not-only-but-also climactic addition). These markers elevate the marked item from compound-list peer to its own beat. The principle is consistency with the "honor what Greek marks" discipline (see also matt 11:25 / luke 10:21 keep-merge case): when the Greek grammar itself signals a beat-boundary via marked-coordinator, colometry reveals it; when there is no marker, colometry merges per J1 bare-compound default.

  **GNT corpus instantiations** (committed 2026-05-13 audit):
    - **luke 14:26** `ἔτι τε καὶ τὴν ψυχὴν ἑαυτοῦ` — Jesus' climactic demand: own life as deepest attachment. Splits before the marker.
    - **acts 21:28** `ἔτι τε καὶ Ἕλληνας εἰσήγαγεν εἰς τὸ ἱερὸν` — already split correctly.
    - **phil 4:22** `μάλιστα δὲ οἱ ἐκ τῆς Καίσαρος οἰκίας` — Caesar's-household greeting as climactic addition. Splits.
    - **gal 6:10** `μάλιστα δὲ πρὸς τοὺς οἰκείους τῆς πίστεως` — household-of-faith priority. Splits.
    - **acts 25:26** `καὶ μάλιστα ἐπὶ σοῦ, βασιλεῦ Ἀγρίππα` — Festus's deference to King Agrippa. Splits.
    - **`οὐ μόνον ... ἀλλὰ καί` family** (rom 1:32, 5:3, 5:11, 8:23, 9:10, acts 21:13, 2cor 8:10, 2cor 9:12, 1thess 1:8/2:8, 1tim 5:13, 2tim 4:8, etc.) — corpus splits at clause-major-boundary. The marker is the standard NT-Greek "climactic-addition" structure.
    - **`μᾶλλον δέ` family** (rom 8:34, eph 4:28, eph 5:11, 1cor 14:1/5, gal 4:9 internal-merge) — climactic correction/intensification.

  Edge-case principle: when the climactic-coordinator construction is INTERNAL to a short clause (rom 13:5, 2cor 7:7, 2cor 8:21, acts 27:10, eph 1:21), merge is defensible per the "modifier-phrase inside larger predication" reading. The split fires when the coordinator constitutes its OWN beat-boundary; the merge holds when it's a contrastive qualifier inside a larger thought.

  Scholarship backing: Runge §2 marked-coordinator analysis (e.g., μᾶλλον δέ as +development +correction); Levinsohn §10.1 Prospective Μέν chapter for the parallel μέν/δέ climactic discipline.

- **Bidirectional atomic-thought test (codified at framework §1.1, 2026-05-13).** "Single cognitive bite" requires the line to stand on its own **referentially**, not just **grammatically**. A line whose content is anaphoric to prior context fails atomic-thought standing alone, even when forward grammatical closure passes. The test is asymmetric: **anaphoric** unresolved-backward-dependence FAILS; **cataphoric** forward-pointing reference PASSES. The reader can process a line whose content is whole and merely sets up what follows (cataphoric); the reader cannot process a line whose content is a pointer to undefined prior context (anaphoric). See [`atu-method/docs/framework.md §1.1`](../../atu-method/docs/framework.md) for full statement.

  **Status (2026-05-13 corrective revision after adversarial audits).** Three parallel hostile audits run on a proposed corpus sweep of 5 anaphoric-gen-abs cases under this principle returned 2 REJECT + 1 NEEDS-MOD-on-scope verdicts. Key findings: (a) the codifying commit a33feca6 self-declared "no precedence change" but the prose below was being read as a precedence override over R19; (b) the worked example at Acts 1:9 was factually wrong; (c) Macula has no anaphoric/cataphoric flag on gen abs, so the classification rests on subjective deictic reading rather than a structured signal; (d) sibling-corpus Tanakh did the same codification with proper rigor (parallel Opus audits + Macula detector + 34-verse fixture + 23,213-verse corpus scan) and STILL deferred application. This section is therefore re-scoped to **informational diagnostic markers**, NOT a mechanical merge-override. Application of bidirectional-test merges in GNT requires the same rigor (detector + fixture + audit) Tanakh applied.

  **GNT diagnostic markers for potential anaphoric failure.** When a line's content is dominated by these markers AND the line stands alone (no apodosis on the same line), the bidirectional test CANDIDATE-flags it for editorial review. The "MUST merge" framing in the original codification was rolled back per audit findings — these are candidates, not Cat A mechanical fires:
  - **Deictic demonstratives**: `ταῦτα` / `τοῦτο` (these things / this), `οὕτως` (thus, in this manner), `ἐκείνῃ` / `ἐκείναις` / `ἐκείνῳ` (that / those — pointing offline), `αὐτό` / `αὐτή` (the same)
  - **Anaphoric particles** (where they LEAD the line and the line is otherwise frame-only): `διὰ τοῦτο` (because of this — already R8), `μετὰ ταῦτα` / `μετὰ τοῦτο` (after these things / after this), `ἀπὸ τότε` (from then), `ἐν ἐκείναις ταῖς ἡμέραις` (in those days — when no FEF temporal-frame predication follows on same line), `Ἐν τῷ καιρῷ ἐκείνῳ` (in that time)
  - **Pronouns without on-line antecedent**: 3p pronouns (αὐτός/αὐτή/αὐτό) when their antecedent is upstream and the line is otherwise content-empty
  - **Anaphoric-genitive-absolute formulae**: `Ταῦτα δὲ αὐτοῦ λέγοντος/εἰπόντος/ἀκούσαντος` (while/after he was saying/saying-having-said/hearing these things — gen abs containing `ταῦτα` referencing prior speech). NOTE: audit found 7 corpus instances of this formula (matt 1:20, matt 9:18, luke 9:34, luke 24:36, john 8:30, john 18:22, acts 26:24); plus the FEF showcase case at acts 1:9 (`καὶ ταῦτα εἰπών`). All currently split per R19+J5.

  **Cataphoric structures that PASS (do not flag):**
  - Presentative `ἰδού` + indefinite NP introducing fresh participants (Matt 2:1 `ἰδοὺ μάγοι ἀπὸ ἀνατολῶν παρεγένοντο…`)
  - `οὗτος` / `αὕτη` in cataphoric apposition pointing to forward content (`αὕτη δέ ἐστιν ἡ ζωή·` "this is the life [which is then defined]")
  - First-mention proper-noun + descriptor pairs
  - Speech-act announcement frames (R11/R28-ext): `λέγει αὐτοῖς·` cataphorically introduces the quote — the line is propositionally complete (the speech-act IS the proposition; the quote follows)

  **Relationship to GNT canon rules (revised post-audit).** This is a §1.1 test-refinement, NOT a new §1.5 merge-override. The bidirectional test surfaces candidate cases; it does NOT mechanically override R19, R20, M4-GNT-1, or other settled rules. Specifically:
  - **R19 (gen abs always own line) retains priority** by default. The audit established that anaphoric gen abs typically retains its OWN warrant for own-line treatment via J5 (substantive adjunct — camera-shift / interjectory function), independent of bidirectional considerations. The "R19 yields when anaphoric" reading was an inference (`P → Q` does NOT entail `¬P → ¬Q`) that was not properly grounded.
  - **J5 substantive adjunct (camera-shift)** can give a gen abs own-line warrant even when the gen abs is anaphoric. E.g., `ταῦτα δὲ αὐτοῦ λέγοντος` introduces a temporal interjectory frame with subject distinct from the matrix subject — the gen abs IS a camera shift to the subordinate-perspective beat, regardless of its anaphoric `ταῦτα`.
  - The bidirectional test catches cases that fail BOTH forward-grammatical AND backward-referential — and ALSO lack J5/J3/FEF independent warrant for own-line treatment. The narrower scope: lines that are PURE anaphoric scaffolding with no propositional content of their own (the Gen 22:1 archetype `wayehi achar ha-devarim ha-eleh` = "and-it-came-to-pass after these things" — zero new content beyond temporal-anaphoric pointer).

  **Worked GNT cases (revised):**
  - **Matt 2:1** — `Τοῦ δὲ Ἰησοῦ γεννηθέντος ἐν Βηθλέεμ…` is NOT anaphoric (Ἰησοῦ is a proper noun, not a deictic pointer). Gen abs is referentially self-contained → R19 split applies.
  - **Acts 1:9 (canonical FEF showcase)** — `καὶ ταῦτα εἰπών / βλεπόντων αὐτῶν / ἐπήρθη / καὶ νεφέλη ὑπέλαβεν…` is **currently split 4-ways in v4/grk** per R19 + J5 (gen abs camera-shift). The earlier codification of this entry incorrectly claimed the canon "already MERGES this" — the audit identified the factual error. The corrected reading: `καὶ ταῦτα εἰπών` does carry anaphoric `ταῦτα` (referencing Jesus' prior commission speech in acts 1:7-8), but it ALSO has J5 substantive-adjunct function as the FEF temporal frame opening the ascension scene. The bidirectional test SURFACES the anaphoric quality; the split-treatment STANDS per R19 + J5. This is the canon's primary illustration that anaphoric ≠ automatic merge; J5/R19 independent warrants matter.
  - **Counter-example (gen abs that splits)** — `Τοῦ δὲ Ἰησοῦ γεννηθέντος…` (Matt 2:1) — `Ἰησοῦ` is proper noun, not anaphoric; gen abs is self-contained → R19 split applies normally.

  **Audit evidence trail (2026-05-13 afternoon).** This section was rewritten in response to three parallel hostile-agent audits (`a9f21e5c8295e2fa0`, `ae817b9aed1d88339`, `aeeba3f9f6b255753`) attacking from framework-discipline, per-case-correctness, and R19-precedence angles. The audits' verdicts of REJECT + NEEDS-MOD were the trigger for this corrective revision. Future application of bidirectional-test merges in GNT requires: (1) a Macula-driven detector for anaphoric-gen-abs (porting Tanakh's `audit_anaphoric_frame_macula.py` approach), (2) a fixture of ≥20 positive/negative/cataphoric/speech-intro cases, (3) corpus-wide scan, (4) explicit per-case Stan editorial decision (Cat B, not Cat A). Audit-skippable was the wrong call at codification; this revision IS the audit.

  **Cat B editorial decision recorded (2026-05-13 close).** Detector built (`scripts/audit_anaphoric_gen_abs_macula.py` — commit 4e1cb89e), fixture 20/20 pass, corpus scan surfaced 10 candidates: matt 1:20, matt 9:18, luke 9:34, luke 13:17, luke 24:36, john 8:30, john 18:22, acts 23:7, acts 25:25, acts 26:24. Stan editorial decision: **KEEP ALL 10 SPLIT.** Rationale: all 10 have J5 substantive-adjunct camera-shift (different subject in matrix); R19+J5 retain default priority per audit consensus. The δέ-development-marker distinction (7 cases with δέ vs 3 without) is supplemental discourse-linguistic detail that does not override the J5 protection. This decision closes the bidirectional-test sweep effort; the detector + fixture + scan infrastructure remains available for future surfacing.

- **Force 2 (Subtractive) — GNT Layer 1 reference.** GNT Layer 1 break-legality lives at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md) (24-row table; R2–R7). Parse data: Macula-Greek + MorphGNT.

- **Force 3 (Diagnostic) — GNT image test.** In GNT application: close your eyes and picture the scene. Does the line make you see ONE thing? Canonical cases: Gal 2:9 (split — two distinct thoughts: the named persons vs. their ironic characterization); Gal 2:10 (merge — fronted genitive + restrictive *μόνον* form a marked word order whose rhetorical force depends on grammatical unity staying intact). The full principle and case-study pair live at §8 **Marked Word Order (Fronting Paradox)** — relocated there in the 2026-05-12 restructure because it is GNT-specific operational content (Greek's case-marked freedom of word order), not universal framework.

- **N=2 Adjudication Principle — GNT canonical cases.**
  - MERGE: `Δαιμόνιον ἔχει καὶ μαίνεται·` (John 10:20) — one diagnostic judgment expressed via two complementary terms.
  - MERGE: `κόπῳ καὶ μόχθῳ` (2 Cor 11:27) — "labor and toil" as one image of exhaustion.
  - SPLIT: `οὔτε γαμοῦσιν / οὔτε γαμίζονται` (Matt 22:30) — active and passive sides of the marriage transaction; distinct predicates.

- **M1 bonded-pair list (GNT corpus-attested):** `{κόπῳ, μόχθῳ}` (2 Cor 11:27 — labor+toil); `{χαίρειν μετὰ χαιρόντων, κλαίειν μετὰ κλαιόντων}` (Rom 12:15 — two classical-comma halves constituting one paraenetic command); `{Τολμηταί, αὐθάδεις}` (2 Pet 2:10 — asyndetic N=2 bonded adjective pair).

- **M1 paraphrase-test scope: hendiadys AND merism (codified 2026-05-13).** Framework §1.5 M1 defines a bonded pair as N=2 coordinate members where the pair functions as "a single unified hendiadys or bonded rhetorical image." The paraphrase test — "can the two members be paraphrased as a single unified image?" — covers TWO sub-rhetorics:

  - **Hendiadys (synonymy / cognate doubling)**: two near-synonymous terms naming ONE idea by redundant emphasis. The paraphrase collapses to one term. GNT examples: `χάρις καὶ εἰρήνη` (grace+peace — Pauline opening formula, 14/14 same-line); `κόπος καὶ μόχθος` (labor+toil — 2 Cor 11:27, already-M1); `δόξα καὶ τιμή` (glory+honor); `φόβος καὶ τρόμος` (fear+trembling — Phil 2:12).

  - **Merism (polar totality)**: two contrastive terms together representing the WHOLE via polar binary. The paraphrase collapses to "everything within the polar range." GNT examples: `Ἰουδαῖος καὶ Ἕλλην` (Jew+Greek = all humanity — Rom 1:16, Gal 3:28, 14/14 same-line); `οὐρανὸς καὶ γῆ` (heaven+earth = all creation — Matt 5:18, 11:25, 24:35; 12/12 same-line); `ἄρσεν καὶ θῆλυ` (male+female = all humans — Matt 19:4, Mark 10:6, Gal 3:28, 3/3 same-line); `Ἄλφα καὶ Ὦ` (Alpha+Omega = totality of being — Rev 1:8, 21:6, 22:13, 3/3 same-line); `πρῶτος καὶ ἔσχατος` (first+last); `μικρὸς καὶ μέγας` (small+great = everyone); `δοῦλος καὶ ἐλεύθερος` (slave+free).

  Both sub-rhetorics pass the M1 paraphrase test for the same operational reason: the two members are **referentially co-extensive** (hendiadys via synonymy; merism via polar-totality). The test is mechanism-neutral. **NO new sub-category in framework.md §1.5 M1** — the existing paraphrase test already covers both, and the GNT corpus is at 75/78 (96%) same-line conformance across the 15 surveyed candidate pairs without explicit framework codification. This note documents the implicit editorial discipline.

  **J1-distinct override remains.** When each member of an N=2 candidate pair carries its OWN independent modifier, sub-referent, or predication, J1 wins (split). Audited cross-line cases this discipline correctly preserves:
    - **heb 4:16** `ἵνα λάβωμεν ἔλεος / καὶ χάριν εὕρωμεν` — N=2 with DISTINCT finite verbs (λάβωμεν / εὕρωμεν) → J1 distinct purpose-clauses.
    - **1tim 6:11, 2tim 2:22** `πίστιν / ἀγάπην` — embedded in N≥4 virtue lists (δικαιοσύνη, εὐσέβεια, πίστις, ἀγάπη, ὑπομονή, πραϋπαθία) in asyndeton → J1 enumeration.
    - **col 3:11** `δοῦλος / ἐλεύθερος` — embedded in N≥4 social-category enumeration (Ἕλλην/Ἰουδαῖος, περιτομή/ἀκροβυστία, βάρβαρος, Σκύθης, δοῦλος, ἐλεύθερος) in asyndeton → J1 enumeration.

  **Corpus survey evidence**: `scripts/audit_hendiadys_merism_gnt.py` surveyed 18 candidate pairs, found 75/78 (96%) same-line conformance corpus-wide. The 3 cross-line cases are all J1-correct overrides. Audit-evidence: two parallel Sonnet adversarial agents (`a96a39a468fe38133`, `aad58f82b961b893c`) validated the J1 classifications and surfaced the framing recommendation (refinement of M1 paraphrase-test, not new sub-category). Scholarly-citation grounding deliberately omitted — Audit 1 found neither Smyth §3025-3026 nor BDF §443-444 unambiguously treat merism as a named category; Runge / Levinsohn don't mention it. The corpus survey itself is the empirical evidence.

  **Audit trigger acknowledgment (per §7.3).** This note touches Trigger #2 (scope claim — clarifying M1 paraphrase-test covers polar-totality alongside synonymy) and Trigger #8 (named pattern under existing rule — naming "merism" as a recognized M1 sub-rhetoric). Two parallel adversarial audits dispatched + NEEDS-MODIFICATION verdicts applied; per-audit-1 recommendation honored by keeping codification at GNT-canon level (not framework.md) and avoiding closed-list extension.

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

This diagnostic catches the failure mode where a canon change is self-framed as "documenting existing practice" or "scope clarification" but substantively asserts a new judgment. §7 "Audit-Workflow Reference" operationalizes this diagnostic for commit-time discipline.

**Greek-specific instances:**
- **Category A:** A dangling article (ton at line end) or a verb split from its direct object — mechanical error, fix confidently.
- **Category B:** Phil 2:6-8 kenosis hymn — whether thanatou de staurou gets its own line or stays with the preceding line changes how the descent structure reads.
- **Category C:** Rom 9:5 — whether ho on epi panton theos eulogetos attaches to ho Christos (Christological reading) or begins a new doxology (theistic reading). Break placement is a doctrinal decision.

### Rule Index

| Rule | Name | Type | Section | Detector |
|------|------|------|---------|----------|
| R1 | No-anchor rule | Mechanical | 3.1 | `scripts/scan_no_anchor_lines.py` + `scripts/apply_no_anchor_merges.py` |
| R2 | Never dangle a conjunction | Layer 1 | Layer 1 table | `validators/syntax/check_r2_no_dangle_conjunction.py` |
| R3 | Never end on article | Layer 1 | Layer 1 table | `validators/syntax/check_r3_no_line_end_article.py` |
| R4 | Never split negation from negated | Layer 1 | Layer 1 table | `validators/syntax/check_r4_no_split_negation.py` |
| R5 | Never split periphrastic construction | Layer 1 | Layer 1 table | `validators/syntax/check_r5_periphrastic.py` |
| R6 | Fixed phrases stay together | Layer 1 | Layer 1 table | `validators/syntax/check_r6_fixed_phrases.py` |
| R7 | Vocative units indivisible | Layer 1 | Layer 1 table | `validators/syntax/check_r7_vocative_units.py` |
| R8 | Framing devices attach | Mechanical | 3.3 | *(not yet implemented)* |
| R9 | Subordinate clause introduction breaks | Mechanical | 3.4 | *(not yet implemented)* |
| R10 | Complementizer hoti — cognition vs. speech | Mechanical | 3.5 | *(not yet implemented)* |
| R11 | Direct speech introduction | Mechanical | 3.6 | `validators/colometry/check_r11_speech_intro.py` |
| R11-ext / R28-ext | Speech-act announcement after adverbial frame (split) | Mechanical | 3.6 | `validators/colometry/check_r28_speech_act_frame.py` |
| R12 | Parallel stacking (if atomic) | Editorial | 3.7 | *(judgment-required; no auto-validator)* |
| R13 | Correlative pair treatment | Editorial | 3.7 | *(judgment-required; no auto-validator)* |
| R14 | Men/de contrast stacking | Editorial | 3.7 | *(judgment-required; no auto-validator)* |
| R17 | De-contrast overbreak | Mechanical | 3.8 | *(not yet implemented)* |
| R18 | Vocative rule (three-way refined) | Editorial | 3.9 | `validators/colometry/check_r18_vocative.py` |
| R18a-GNT | Patriarch-deity-triad indivisibility | Mechanical | 3.9a | `validators/colometry/check_r18a_patriarch_triad.py` |
| R19 | Genitive absolute always own line | Mechanical | 3.10 | `validators/colometry/check_r19_genabs.py` + `scripts/sweep_r19_genabs.py` |
| R20 | Participial phrase test (refined) | Editorial | 3.10 | `scripts/scan_line_ending_participles.py` *(scanner only)* |
| R22 | Orphaned adverbial completion | Editorial | 3.11 | *(judgment-required; no auto-validator)* |
| R23 | Dative subject of infinitive | Mechanical | 3.12 | `scripts/scan_r23_dative_infinitive.py` *(scanner only)* |
| R24 | Qualifying phrases: escalation vs. restriction | Editorial | 3.13 | *(judgment-required; no auto-validator)* |
| R25 | ὥστε short-consecutive-result binding | Mechanical | 3.14a | `validators/colometry/check_r25_hoste_consecutive_result.py` |
| R27 | Authorial style principle (uniform criteria) | Principle | 3.15 | *(principle, not a per-line rule)* |
| R28 | Textual asymmetry overrides editorial symmetry | Principle | 3.7 | *(principle, not a per-line rule)* |
| M4-GNT-1 | Subject-orphan predicate completion (Greek instantiation) | Mechanical | 3.18 | `validators/colometry/check_m4_gnt_1_subject_orphan.py` |

*Retired (see §9):* R15 (folded into R14), R16 (folded into R8), R21 (absorbed as operational mechanism for R12/R13/R14), R25-old (folded into R11 — superseded 2026-05-11 by R25 ὥστε-binding; see §9), R26 (pure restatement of M2), R29 (pointer-only; M1–M4 stand on their own in Section 2).

Rules are classified as MECHANICAL (any trained editor would apply them identically), EDITORIAL (defensible, documented, but require judgment), PRINCIPLE (governing stance, not a per-line rule), or LAYER 1 (pure Koine-Greek syntax facts at [`data/syntax-reference/greek-break-legality.md`](../../data/syntax-reference/greek-break-legality.md); Mechanical in effect, but their warrant is generic Greek grammar rather than a project-specific editorial choice).

### Closed-List Registry

Index of the closed-list lexical/syntactic sets that rules in §3 reference. Each list is **defined inline** in the cited section; this table is a findability index, not a duplicate definition. Any *extension* to a list is a §6.5 audit trigger (closed-list extension is a precedence/scope claim).

| List name | Members (canonical) | Defined in | Consumed by |
|---|---|---|---|
| **R8 framing devices** | ἰδού, διό, οὖν, νυν δέ, ἀλλά, γάρ, πλήν, τοιγαροῦν | §3.3 table | *(no validator yet — manual editorial)* |
| **R9 subordinate-clause openers** | ἵνα, ὥστε, ὅτι, διότι, ὅταν, ὅτε, εἰ, ἐάν, καθώς, μήποτε | §3.4 | *(no validator yet)* |
| **R10 cognition / perception / belief verbs** (merge with ὅτι) | οἶδα, γινώσκω, ὁράω/εἶδον/βλέπω/θεωρέω, πιστεύω, ἐπίσταμαι, νομίζω/δοκέω, εὑρίσκω, ἀκούω, συνίημι | §3.5 | *(no validator yet)* |
| **R10 declaration / speech / writing verbs** (split from ὅτι) | λέγω, εἶπον, γράφω, μαρτυρέω, ὁμολογέω, διδάσκω, κηρύσσω, ἀπαγγέλλω, καταγγέλλω, ἀναγγέλλω, ἐπαγγέλλομαι, προφητεύω | §3.5 | *(no validator yet)* |
| **R10 speech-intro frame class** | ἀποκρίνομαι (verb + ὅτι merges as speech-intro frame) | §3.5 | `validators/colometry/check_r11_speech_intro.py` (R11 family) |
| **R11 / R28-ext speech-frame verbs** (J3 instantiation) | λέγω, εἶπον, ἀποκρίνομαι, ἔφη + dative addressee | §3.6 | `validators/colometry/check_r11_speech_intro.py`, `validators/colometry/check_r28_speech_act_frame.py` |
| **R18a-GNT patriarch-triad variants** | fully-distributed `ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ`; anchor-shared `τὸν θεὸν Ἀβραάμ καὶ θεὸν Ἰσαάκ καὶ θεὸν Ἰακώβ`; compressed `ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ`; extended-lead `ὁ θεὸς τῶν πατέρων σου, ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ` | §3.9a | `validators/colometry/check_r18a_patriarch_triad.py` |
| **M1 GNT bonded pairs** | {κόπῳ, μόχθῳ} (2 Cor 11:27); {χαίρειν μετὰ χαιρόντων, κλαίειν μετὰ κλαιόντων} (Rom 12:15); {Τολμηταί, αὐθάδεις} (2 Pet 2:10) | §1 (GNT instantiations) | *(no validator yet — operational via M1 reasoning)* |
| **M4-GNT-1 SUBJECT_SHAPES** | C1 vocative_address_NP, C2 np_with_appositive, C3 np_with_participial, C4 np_with_relcl, C5 biographical_intro | §3.18 (inline YAML) | `validators/colometry/check_m4_gnt_1_subject_orphan.py` |
| **M4-GNT-1 LEADING_CONNECTIVES_BLOCK_FIRE** | καί, δέ, γάρ, οὖν, ἀλλά, ἤ, εἰ, ὅτι, ἵνα, ὅταν, ὅτε, ὡς, ὥστε, ὅπου, ὁ, ἡ, τό | §3.18 (inline YAML) | `validators/colometry/check_m4_gnt_1_subject_orphan.py` |
| **Period Test obligatory-complement verbs (non-R10)** | κελεύω, ἐντέλλομαι (command); θέλω, ἐπιθυμέω, βούλομαι (desire); δείκνυμι, δηλόω (demonstrate) | §4 Period Test | *(diagnostic test — used by humans, not by an auto-validator)* |
| **Layer 1 syntactic-bond pairs** (R2–R7) | conjunctions never-final; articles never-final; negation+verb never-split; periphrastic εἰμί+ptc never-split; fixed phrases (κατὰ + acc, εἰς τὸ + inf, etc.); vocative units never-split | `data/syntax-reference/greek-break-legality.md` | `validators/syntax/check_r{2,3,4,5,6,7}_*.py` |

**Extension protocol.** Adding a member to any list above (a new verb to R10's families, a new triad-variant to R18a-GNT, a new SUBJECT_SHAPE to M4-GNT-1, a new framing device to R8) is a closed-list extension per canon §6.5 trigger #3 — Category B by default, audit dispatched. Cross-reference the list's defining section in the audit-evidence.

### Pairwise Precedence Catalogue

Canon prose makes specific pairwise-precedence statements; it does NOT make a totally-ordered N-tier ranking claim across all rules. This section catalogues every pairwise precedence the canon actually states. Each row is a direct restatement, with the canon §-ref that warrants it.

Architecture.md §interface-contracts states: *"Precedence hierarchy — §3.5 of each per-repo canon. Detectors must filter candidates that match higher-tier rules out of lower-tier buckets."* Currently the GNT spec satisfies this contract by **pairwise statement**, not lattice ordering. A future revision may upgrade to a totally-ordered hierarchy *after* the detector implementations enforce tier-yield consistently (see "Known detector gaps" at the end of this subsection).

| Winning rule | Loses to / Yields | Scope | Warrant |
|---|---|---|---|
| **Layer 1 R2–R7** (syntactic vetoes) | — (top of stack for veto-level) | Never violated for the rule's named pattern. Generic Greek grammar. | §3.2 ("R2–R7 are pure Koine-Greek syntax facts"); framework §1.2 subtractive-force-as-floor |
| **R18a-GNT** (patriarch-deity-triad) | wins over subtractive vetoes *internal to the triad span* | When θεός-Ἀβραάμ-Ἰσαάκ-Ἰακώβ formula matches | §3.9a verbatim |
| **R11 / R28-ext speech-frame** | wins over default break placement when verb+frame is a fixed speech-intro span | Speech-intro formula integrity | §3.18 line 898 ("formula integrity (R6, R11)"); §3.6 |
| **R10 ὅτι-complement (cognition class)** | wins over R11 / R28-ext when ὅτι immediately follows speech verb | ὅτι→indirect speech routes to R10, not R11 | §3.6 R11 detector exclusion X1; §3.5 |
| **R10 / Period-test obligatory complement** | wins over generic split-default | Complement integrity | §3.5; §3.18 line 898 ("complement integrity (§3.5 R10)") |
| **R7 vocative-indivisibility** | wins over M4-GNT-1 when line A is pure vocative | Per universal exclusion #6 in §3.18 | §3.18 verbatim |
| **R5 periphrastic** | wins over M4-GNT-1 when line A/B forms a periphrastic | Per G3 exclusion in §3.18 | §3.18 verbatim |
| **R19 gen-abs own-line** | wins over M4-GNT-1 when line B begins with gen abs | Per universal exclusion #11 in §3.18 | §3.18 verbatim |
| **R19 gen-abs own-line** | wins over R28-ext when both match same locus | gen abs has priority over speech-frame routing | §3.6 R28-ext relation; corroborated by R28-ext code path |
| **R22 orphaned-adverbial-completion** | wins over R9 default in completing-predicate sub-case | R22 is the merge-override for the R9 split-default sub-case | §3.4 verbatim ("The default under R9 is split; R22 is the merge-override for the completing-predicate sub-case") |
| **R9 subordinate-clause break** | wins over R25 ὥστε-binding when the split case applies | R25's word-count + semantic conditions must all clear for R25 to win | §3.14a verbatim ("R9 takes precedence for the split case") |
| **R28 textual-asymmetry** | wins over R12 editorial parallelism, R14 men/de stacking | Authorial asymmetry preserved over editorial symmetry | §3.7 verbatim ("Textual asymmetry overrides editorial symmetry") |
| **M4-GNT-1** (and by extension framework M4) | yields to R2-R7 (Layer 1), R6, R11 (formula), R10 (complement), R7 (vocative), R19 (gen-abs) | Merge-override of last resort; runs only after higher-priority rules settle | §3.18 verbatim ("Tier 4 merge-override... Yields to Tier 1–3 rules (Layer 1 vetoes, formula integrity, complement integrity, vocative integrity R7, genitive-absolute R19)") |
| **M1 (Gorgianic bonded pair)** | exhausts M1→M2→M3→M4 chain before flipping to split | M1 strict-application caveat | §2 M1 caveat |
| **N=2 Adjudication Principle** | adjudicates within the legal-break space when forces leave ambiguity | Applies at N=2 ambiguity; per framework §1.x | framework §1; canon §1 |

**Architecture interface compliance.** Detectors are expected to filter candidates that match a higher-priority pairwise relationship out of lower-priority emission buckets. M4-GNT-1's G1–G5 exclusions + universal-6 list is the gold-standard implementation pattern (`validators/colometry/check_m4_gnt_1_subject_orphan.py`); it explicitly comments "R5 governs", "R7 governs", "R10 governs" at the yield points.

**Known detector gaps (audit 2026-05-13, pending engineering follow-up).** The following detectors do NOT yet implement explicit tier-yield filters per the pairwise table above:
- **`check_r19_genabs.py`** — lacks "skip if vocative-only line (R7)" and "skip if line spans a FIXED_PHRASES entry (R6)" filters. Current behavior leans on a 5-entry `_KNOWN_FP_ALLOWLIST` that captures the symptom; the class-based filter is missing.
- **`check_r18_vocative.py`** — silent on R7 yield. Currently fires independently on multi-word vocative units that R7 would normally constrain.
- **`validators/run_all.py`** — runs validators in alphabetical (`pkgutil.iter_modules`) order, not pairwise-precedence order. The "filter higher-priority matches out of lower buckets" discipline is currently the responsibility of each lower-priority detector internally; there is no runner-level pass.

These gaps are documented for visibility, not codified as new rules. Closing them is detector-engineering work (separate commits, normal validator-extension audit if scope expands).

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

These are not merely "break triggers" — they lead their content; never orphan them at the end of a line.

**Functional-gloss nuance (codified 2026-05-14, corroborated Runge §2.7 + Levinsohn §5.4.2).** The colometric rule — *lead your content, never line-final* — is uniform across the table. But the discourse FUNCTION varies, and the loose gloss "introduce what follows" is over-extended for one member: **γάρ does not frame-forward; it strengthens-backward.** γάρ-introduced material is offline background that confirms or grounds the *preceding* assertion — Levinsohn §5.4.2 verbatim: "The presence of γάρ constrains the material that it introduces to be interpreted as strengthening some aspect of the previous assertion, rather than as distinctive information." Runge §2.7 concurs (γάρ = +continuity, -development, +support per the §2 connectives matrix). The colometric placement (γάρ leads its clause) is unaffected — but the framing-device gloss should be read as: *these markers lead their content; their discourse direction varies — γάρ supports the prior unit, οὖν advances closely from it, ἀλλά corrects an expectation it set, διό draws an inference from it.* The table's "Function" column already encodes these per-marker; the blanket "introduce what follows" is the gloss being nuanced here.

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

Grammatical warrant: ὅτι is a complementizer — its function is to introduce the clause that follows. Placing it at line-end severs it from the clause it governs. Standard Koine grammar (BDF §416, Smyth §2017, Wallace p. 453-461, Burton §334–356 on indirect-discourse-ὅτι vs declarative-ὅτι distinction) describes ὅτι as introducing its complement; our placement convention honors that function visually.

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

**Linguistic grounding (Runge §2.3 + Levinsohn §5.4.1 + Buth 1992 table cited in Levinsohn §5.3 — PRIMARY discourse-linguistic sources).** δέ is fundamentally a **+development marker** (Runge: "Δέ is a coordinating conjunction like καί, but it includes the added constraint of signaling a new development"; Buth's table in Levinsohn §5.3 captures it as +development, -close-connection in contrast to καί's -development, +close-connection). Adversative force is **context-dependent**, not particle-marked — Runge §2.3.2: "Contrast has everything to do with the semantics of the elements present in the context… [δέ] does not mark [discontinuity's] presence or absence." The R17 rule's NAME ("De-Contrast Overbreak") captures the editorial **failure mode** — editors over-split because they read δέ as inherently adversative (the legacy English "but" gloss) — not the particle's underlying function. The colometric rule remains valid because both the development-marker reading and the legacy contrast reading coincide on the surface signature: δέ + new finite-verb clause = new development = own line.

Genre note (Levinsohn §5.2): Mark specifically has a HIGHER distinctiveness threshold than the other Synoptics for δέ — Buth (in Levinsohn): "adversative overtones must be present in Mark before δέ occurs." Mark δέ instances are therefore a stronger split signal than δέ in Matthew/Luke/Acts; the rule has its highest yield in Mark.

**De-contrast overbreak rule.** When two distinct clauses with a δέ pivot appear on one line — a comma before `ho de / he de / to de / hoi de / meson de / nyni de` — split at the δέ. The comma marks the clause boundary; the δέ signals a new development (which may include contextually-emergent topical shift, narrative-to-background switch, or adversative contrast as one of several motivations for marking the development).

**Canonical example:**
```
Hai alopekes pholeuous echousin
kai ta peteina tou ouranou kataskeenoseis,
ho de huios tou anthropou ouk echei pou ten kephalen kline.
```
(Matt 8:20)

**False positives to rule out** — in each case δέ marks no new development because there is no new finite-clause to develop *into*:
- Participial δέ (δέ inside a participial phrase; no new finite verb after)
- Intensifying `malista de` (adds emphasis to an item within the current clause)
- Appositional `thanatou de staurou` (emphatic specification of an existing element, not a new clause)

Test: is there a finite verb in the clause following δέ? If yes → split (a new finite-clause development is licensed). If the δέ introduces only a nominal or participial phrase without its own finite verb → likely false positive, leave merged.

*27 confirmed splits applied corpus-wide. Discourse-linguistic grounding refined 2026-05-13 (commit pending) — colometric behavior unchanged; rule's editorial warrant updated from legacy "contrast pivot" framing to Runge/Levinsohn "development marker" framing.*

### 3.9 Vocative Rule (Refined Three-Way Treatment)

**Default: vocatives get their own line** when they initiate or resume direct address. A vocative at the start of a discourse turn (paragraph-opening or post-speech-intro position) is opening a camera-angle turn — the speaker is now turning toward an addressee — and earns its own line as a complete address act.

**Apposition exception: a vocative merges into the preceding line when it is grammatically appositive to an already-established second-person address in the same clause-span.** The grammatical signature: somewhere in the preceding line(s) of the same clause-span, *not separated from the vocative by a speech-introducing boundary* (ano teleia or colon), there is either a second-person pronoun (any form of sy / hymeis) or a second-person finite verb. "Clause-span" here means the syntactic unit; intervening Stephanus 1551 verse-markers are irrelevant per §1 versification-not-a-signal.

Two justifications, not one:

1. **Subject-appositive rule** — when the vocative names the implicit subject of a 2p finite verb (`Hypage, Satana`, `Agnoeite, adelphoi`, `Tharsei, teknon`, `Ouai hymin, grammateis kai Pharisaioi hypokritai`). The verb and vocative form *one atomic predication*.
2. **Object-appositive rule** — when the vocative restates an explicit 2p pronoun already in the clause (`Parakalo hymas, adelphoi`, `Gnorizo hymin, adelphoi`). The address is already established; the vocative is affective restatement.

**Verb person is irrelevant.** The triggering condition is the 2p *pronoun*, not the person of the main verb. `Akoloutheso soi, kyrie:` (Luke 9:61) — kyrie merges because it is object-appositive to soi, regardless of akoloutheso being first person. Contrast Acts 9:10 `Idou ego, / kyrie.` (correctly split: ego is 1p, kyrie is not appositive to any 2p element).

**Boundary cases that stay on their own line:**
- **Turn-initial vocative** — opening a new discourse turn (paragraph-opening, post-speech-intro), no preceding grammar to lean on within the turn.
- **Tail vocative** — clause-final address, distinct act.
- **Vocative after speech-intro punctuation** — the prior 2p markers belong to the outer layer, not the inner address.
- **Stacked parallel vocatives** — treated as a parallel address structure (pateres / neaniskoi / paidia in 1 John 2:12-14).

**Discourse-frame + vocative cluster rule.** When a sentence-initial discourse marker (Loipon, To loipon, Loipon oun, Tauta de, Kago, etc.) co-occurs with a vocative, *both* are extra-clausal elements and cluster on one line; the proposition follows on the next line. Canonical example: `Loipon, adelphoi, / stekete en kyrio.` (Phil 4:1 pattern). The vocative still earns its line; it earns *that* line together with the frame particle.

**Repeated vocatives as a rhetorical unit still stay together.** `Kyrie kyrie` (Matt 7:21-22) is one speech act.

*125 vocative merges landed across 21 books.*

### 3.9a R18a-GNT — Patriarch-Deity-Triad Indivisibility

*Ported from BoFM R18a 2026-05-11. Mechanical Category A.*

**Patriarch-deity-triad (Exod 3:6 LXX quotation; R18a-GNT, ported from BoFM R18a 2026-05-11).** The Exodus citation *ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ* (and its anchor-shared variants) appears at five NT loci: Matt 22:32, Mark 12:26, Luke 20:37, Acts 3:13, Acts 7:32. The triad-as-unit functions as a single fixed referring expression to YHWH; severing the span across lines fractures the unitary deity-reference into the apparent enumeration of three deities. **Rule.** A verse-block whose tokens contain `θεός`-lemma governing `Ἀβραάμ`, followed (in order, within the same verse) by `Ἰσαάκ`, followed by `Ἰακώβ`, MUST keep the entire spanning sequence whole on a single line. **Status:** Active. **Category:** A (Mechanical, mandatory). **Layer:** 3 (sister to the Revelation frozen-formula note above; ported from BoFM R18a). **Closed list of attested variants:** fully-distributed (`ὁ θεὸς Ἀβραάμ καὶ ὁ θεὸς Ἰσαάκ καὶ ὁ θεὸς Ἰακώβ` — Matt 22:32, Mark 12:26); anchor-shared (`τὸν θεὸν Ἀβραάμ καὶ θεὸν Ἰσαάκ καὶ θεὸν Ἰακώβ` — Luke 20:37); compressed (`ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ` — Acts 3:13, Acts 7:32); extended-lead (`ὁ θεὸς τῶν πατέρων σου, ὁ θεὸς Ἀβραάμ καὶ Ἰσαάκ καὶ Ἰακώβ` — Acts 7:32 full). **Exclusions.** (1) Personal-name list without θεός anchor (e.g., Acts 7:8 patriarchal genealogy) — coordinate-NP-object territory, R18a-GNT does not fire. (2) Non-canonical triad orderings — Ἀβραάμ → Ἰσαάκ → Ἰακώβ is the only attested order; no reversals. (3) Lead-in title phrases on separate lines (e.g., `ὁ θεὸς τῶν πατέρων ἡμῶν,` at Acts 3:13 line 60) — appositional continuations stay on their own line; the triad-line itself must be whole. **Precedence.** Tier 2 indivisibility, parallel to BoFM R18a §3.5 Tier 2. Wins over subtractive vetoes internal to the triad span. Where the triad follows a speech-intro verb (Mark 12:26: `λέγων·`, Luke 20:37: `ὡς λέγει`), the speech-intro lands on its own prior line per R11 and the triad opens the content line. **Validator:** `validators/colometry/check_r18a_patriarch_triad.py`. **Corpus survey (2026-05-11).** Matt 22:32, Mark 12:26, Acts 3:13 already compliant (triad whole); Luke 20:37 violation (triad split across lines 211-212); Acts 7:32 Category B Stan-review (triad whole on line 153, but extended formula `Ἐγὼ ὁ θεὸς τῶν πατέρων σου` on line 152 is appositional-lead boundary judgment).

### 3.10 Participial Phrases and Genitive Absolutes

**Genitive absolutes are grammatically independent and ALWAYS get their own line.** A gen abs has its own subject (in genitive) and its own predicate (a genitive participle) — the literal meaning of "absolute" is "set apart" from the main clause. It functions as an interjectory frame: a camera shift, a scene-setter, an aside. Merging a gen abs into adjacent material absorbs an independent beat into something it is not. See Acts 1:9 showcase in Section 1.

**Default rule for circumstantial participles: merge with their main verb.** The default function of a Greek circumstantial participle is adverbial framing — temporal, causal, concessive, conditional, manner. All of these are DEPENDENT: they frame the main verb's action and are not complete thoughts without it.

**Exception — circumstantial participle with independent semantic weight:** A participial phrase earns its own line when it constitutes a **second predication** — that is, when the main verb can be implicitly repeated to reconstruct the participle as an independent thought. (Note: standard grammars reserve "supplementary participle" for participles completing specific verbs like τυγχάνω, λανθάνω, φθάνω, παύω per Smyth §2094-96 and Wallace §645-47, with Burton §445–446 on supplementary participles after these specific verbs. Our usage is broader than the technical "supplementary" category — any circumstantial participle that constitutes an independent predication via ellipsis of the main verb. Burton §434–450 enumerates the adverbial-participle classes — time, condition, concession, cause, purpose, means, manner, attendant circumstance — that our R20/R22 discipline navigates.)

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

When a Greek speech or command verb (λέγω, παραγγέλλω, παρακαλέω, κελεύω, etc.) takes a dative indirect object that is ALSO the semantic subject of an infinitive complement, the dative chunks with the infinitive content, not with the speech verb frame. (Note: standard Greek grammar reserves "subject of the infinitive" for the accusative case per BDF §392, Wallace §195, Burton §390 — the accusative-subject default in indirect discourse / object infinitives. The dative here is grammatically an indirect object that happens to be coreferential with the understood subject of the infinitive — but for colometric purposes, it belongs with the infinitive content it semantically controls.)

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

### 3.17 ATU Spans Versification Overlay (Inline Superscript Marker)

**When a single ATU happens to span a Stephanus 1551 verse-marker, the line stays intact.** Versification is editorial overlay (imposed 1551 on a text that already had its own rhetorical structure) — it does not constrain ATU formation per §1 versification-not-a-signal. The ATU is formed by grammatical/rhetorical continuity; the versification marker is carried along inline as a superscript, which is an indexing convenience for cross-references — not an analytical boundary the ATU is "crossing."

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

**Boundary note — M4-GNT-1 vs R9 (Runge §14 left-dislocation taxonomy, codified 2026-05-14).** Runge §14 treats "left-dislocation" as a single discourse construction with three sub-uses (streamlining / processing-aid / discourse-pragmatic highlighting — see the M4-GNT-1 YAML `refinement_candidates` block). M4-GNT-1 operationalizes only the **subject-NP** instantiation of left-dislocation — a fronted grammatical-subject NP orphaned from its matrix predicate. Runge's broader §14 enumeration also includes **locative** and **temporal** left-dislocations: `ὅπου γάρ ...` (Matt 6:21 "where your treasure is, there your heart will be"; Jas 3:16 "where jealousy is, there is disorder"), `ὅτε`-temporal frames (Matt 21:1), `καθώς`-comparative frames (John 15:4). Those are NOT M4-GNT-1 cases — they are governed by **R9 (subordinate-clause introduction breaks, §3.4)**: the `ὅπου` / `ὅτε` / `καθώς` clause is an adverbial subordinate clause taking its own line, with the resumptive `ἐκεῖ` / `τότε` / `οὕτως` apodosis following. M4-GNT-1's closed-list `SUBJECT_SHAPES` (C1–C5) deliberately scopes to subject NPs only; the locative/temporal/comparative left-dislocations have a different colometric mechanism (R9 adverbial-clause split) even though they share Runge's "left-dislocation" umbrella. No corpus action: the boundary is a clarification, not a gap — R9 already correctly handles the non-subject left-dislocations.

---

### Detector Signatures (machine-readable)

For rules with implemented detectors, the structured signature the detector consumes — extracted faithfully from each detector's docstring. Detector implementation is the source of truth; drift between this section and `validators/*/check_r*.py` is a failure mode (per `atu-method/docs/architecture.md §drift-prevention #1`).

Rules without a Detector Signature block below have no auto-validator yet (see Rule Index column "Detector"). When implementing a detector for an unsignatured rule, add the signature block here as part of the same commit.

**Reference grammar substrate.** YAML `references:` lines cite authoritative NT Greek reference grammars by their printed-edition section numbers / page numbers. Substrates live at `private/05-resources/{slug}/` with per-rule mapping in each slug's README:

- **Burton 1903** (`private/05-resources/burton-1903/`) — Ernest De Witt Burton, *Syntax of the Moods and Tenses in New Testament Greek*. Classic monograph on NT Greek verbal syntax (moods / tenses / infinitives / participles). Section numbers §1–§489 stable across editions 3–5. Cite as `Burton §N` or `Burton §N–M`. Covers R9 / R10 / R19 / R20 / R22 / R23 / R25 + J3/J5 partial.
- **Wallace 1996** (`private/05-resources/wallace-1996/`) — Daniel B. Wallace, *Greek Grammar Beyond the Basics: An Exegetical Syntax of the NT*. Modern comprehensive grammar covering cases, article, adjectives, pronouns, prepositions, all clause types, conjunctions, conditional sentences, plus the verb-and-verbal territory Burton also covers. Cite as `Wallace p.X` (print pages — established convention; canon already uses this form at §3.5). Section-heading citations OK when print page unknown: `Wallace, "Conjunctions: Contrastive"`. Covers ALL R-rules except R27 / R28 / discourse-marked-word-order.
- **BDF 1961** (`private/05-resources/bdf-1961/`) — F. Blass, A. Debrunner, R. W. Funk, *A Greek Grammar of the NT and Other Early Christian Literature* (Funk translation of the 9th–10th German editions). THE standard scholarly reference grammar; deepest philological + historical-grammar treatment. Section numbers §1–§500 stable across editions. Cite as `BDF §N` (canon already uses at §3.5 `BDF §416` and §3.12 `BDF §392`). Particularly strong on: particles + conjunctions (§§438–470 — primary scholarly source for R8 framing devices), Pendent Nominative (§466 — informs M4-GNT-1), Article repetition with apposition (§§268–269 — informs R18a-GNT), Coincident participle (§420 — Burton's attendant circumstance / Wallace's same).
- **Runge 2010** (`private/05-resources/runge-2010/`) — Steven E. Runge, *A Discourse Grammar of the Greek New Testament: A Practical Introduction for Teaching & Exegesis* (Lexham). Modern discourse-linguistic complement to the traditional reference grammars: information-structure, prominence-marking, framing devices, pragmatic effect. Cite as `Runge §N.M` (Runge's numbered subsections — stable) or `Runge p.X`. PRIMARY discourse-linguistic source for: R8 framing devices (§2 Connecting Propositions — entire chapter), R11 / R28-ext speech-frames (§7 Redundant Quotative Frames), R12-R14 point/counterpoint (§4), R17 δέ-as-development-marker (§2.3), M4-GNT-1 subject-orphan (§14 Left-Dislocations — entire chapter), §8 Marked Word Order / Fronting Paradox (§9 Information Structure — P1/P2 framework is the linguistic grounding for the canon's anti-imposition principle), R19 / R22 circumstantial frames (§12.3.2 / §12.3.4).
- **Levinsohn 2000** (`private/05-resources/levinsohn-2000/`) — Stephen H. Levinsohn, *Discourse Features of New Testament Greek: A Coursebook on the Information Structure of New Testament Greek*, 2nd ed., SIL International. The SIL-discourse-linguist's NT-Greek coursebook that Runge 2010 builds on (Runge cites Levinsohn extensively). SECONDARY discourse-linguistic substrate: corroborates Runge's framework with finer empirical detail and NT-Greek-specific statistics. Cite as `Levinsohn §N.M`. Particularly strong on: §5.4.2 Background Material with Γάρ (γάρ-strengthens-prior-not-advances — corroborates the Runge §2.7 claim that was previously a single-source refinement candidate); §10.1 Prospective Μέν (the dedicated chapter Runge §2.8 + §4 condense, primary citation for R12-R14); §2.6 Implications for Basic Constituent Order (verb-initial default; statistical backing 264 SV / 310 VS / 146 ∅ in Acts narrative); §5.2 + §5.4.1 finer Δέ classification (informs R17 De-Contrast Overbreak); §10.3 Use of Ἐγένετο (informs J3 + canon §5 Front-End Frame).
- *(Future)* Smyth — when ingested.

**Burton + Wallace + BDF + Runge + Levinsohn together cover ~all R-rule territory.** Burton + Wallace + BDF handle morphology + syntax structurally; Runge + Levinsohn handle information-structure + pragmatic-effect (the territory R8 / R12-R14 / R17 / R27 / R28 / §8 Fronting Paradox / M4-GNT-1 / §3.6 R11+R28-ext occupy). Per Stan reminder 2026-05-13: the grammars are SUBTRACTIVE per canon §1 — they constrain where ATUs can break (Layer 1 vetoes, complement integrity, frame integrity) but do not GENERATE ATU boundaries (propositions generate; single-image diagnoses). Citations feed canon's vetoes and refinements, not its generative engine. Per-rule mapping in each substrate's README documents which sections inform which rules. The `_full-text.txt` dumps are for spot-checking content during canon revisions — print editions are the citation primary.

~~~yaml
# R11 — Direct speech introduction (canon §3.6)
# Detector: validators/colometry/check_r11_speech_intro.py
R11:
  rule_id: R11
  category: Mechanical
  layer: 3
  signature:
    trigger:
      line_has: finite_speech_verb_third_person_indicative
      speech_verb_lemmas: [λέγω, φημί, ἀποκρίνομαι]
      AND:
        - line_also_has: another_finite_or_imperative_verb
        - line_does_not_end_with_speech_boundary  # · or :
        - no_hoti_immediately_after_speech_verb   # ὅτι → R10
    action: STRONG-SPLIT  # speech verb + frame → line 1; quoted content → line 2
  false_positive_filters:
    - class_A: negated_speech_verb           # non-occurrence
    - class_B: OT_attribution_tag            # λέγει κύριος / λέγει τὸ πνεῦμα — FULL FILTER
    - F1: speech_verb_inside_subordinate_clause_on_same_line
    - F2: translation_gloss_idiom            # ὃ λέγεται μεθερμηνευόμενον
    - F3: passive_speech_form                # is said / is called
    - F4: speech_verb_inside_already_opened_quote   # FULL FILTER
    - F5: parenthetical_mid_speech_attribution      # φησίν/λέγει — FULL FILTER
    - F6: hoso_hosoi_hoson_subordinator_variants
    - F7: post_positioned_attribution_tag
    - F8: narrative_explanatory_comment      # τοῦτο δὲ εἶπεν σημαίνων pattern
    - F9: descriptive_speech_as_behavior     # λέγουσιν ... ποιοῦσιν contrast
  closed_lists:
    - R11_speech_frame_verbs                  # see Closed-List Registry, §3 Rule Index area
  references: |
    PRIMARY discourse-linguistic source: Runge §7 Redundant Quotative Frames (especially §7.2.1 At Changes in Speaker/Hearer). Runge's framework: the participial-ἀποκρίνομαι + finite-εἶπεν pattern is a REDUNDANT-FRAME prominence-marker, not just a Semitic-influence holdover. Discourse function: (a) signal CHANGE OF DIRECTION in a conversation (counter / objection / rejection), or (b) introduce an AUTHORITATIVE PRONOUNCEMENT (Levinsohn). The redundancy IS the signal — the frame is a single prominence-marking unit, which is why R11 merges participle + finite onto one line.
    Wallace, "Person and Number" (3rd-person finite verbs) + "Indicative Mood" treatment of declarative verbs. Burton §168 (hortatory subj) + §180–184 (imperative) partial. BDF §§329–339 (periphrastic constructions; indicative speech-act-class verbs); BDF §420 cited in Runge §7's Suggested Reading for the "coincident" participle that grounds the Hebraism analysis.
  resolved_runge_§7_2_2_within_same_speaker:
    source: Runge §7.2.2 (Within the Same Speaker's Speech) + Mark 4:9 / 13 / 21 / 24 / 26 / 30 examples
    claim: |
      Mid-speech redundant quotative frames (καὶ ἔλεγεν / Καὶ λέγει αὐτοῖς·) where
      there is NO change of speaker function as DISCOURSE SEGMENTATION markers —
      they break a long speech into smaller chunks at thematic boundaries. The
      imperfect ἔλεγεν is characteristic (Wallace's "instantaneous imperfect"
      restricted to ἔλεγεν in narrative — which Runge reframes as discourse-
      segmentation, not aspectual ambiguity). This is functionally DIFFERENT from
      the canon §3.6 Parenthetical Mid-Speech Attribution rule (which treats
      mid-quote φησίν/λέγει as merge-not-split because they are parenthetical
      attribution tags, not segmentation markers).
    audit_2026-05-13_corpus_state:
      All six Mark 4 mid-speech segmentation frames Runge identifies are ALREADY
      on own lines in v4/grk via the normal R11 speech-intro discipline:
        - mark 4:9 line 44 — Καὶ ἔλεγεν· / Ὃς ἔχει ὦτα ἀκούειν ἀκουέτω.
        - mark 4:13 line 62 — Καὶ λέγει αὐτοῖς· / Οὐκ οἴδατε τὴν παραβολὴν ταύτην,
        - mark 4:21 line 108 — Καὶ ἔλεγεν αὐτοῖς· / Μήτι ἔρχεται ὁ λύχνος,
        - mark 4:24 line 123 — καὶ ἔλεγεν αὐτοῖς· / Βλέπετε τί ἀκούετε.
        - mark 4:26 line 134 — Καὶ ἔλεγεν· / Οὕτως ἐστὶν ἡ βασιλεία τοῦ θεοῦ
        - mark 4:30 line 156 — Καὶ ἔλεγεν· / Πῶς ὁμοιώσωμεν τὴν βασιλείαν τοῦ θεοῦ,
    resolution: |
      RESOLVED AS ALREADY APPLIED (2026-05-13 afternoon). The canon's R11
      speech-intro rule already produces own-line treatment for these frames
      because they surface-match the standard speech-intro pattern (καὶ +
      speech verb + speech-boundary · → next line is the quoted content). R11
      doesn't distinguish change-of-speaker speech-intros from same-speaker
      segmentation frames — but the colometric output is identical: each
      mid-speech frame gets its own line, segmenting the speech as Runge's
      §7.2.2 analysis recommends.
      The canon §3.6 Parenthetical Mid-Speech Attribution rule (merge) covers
      a DIFFERENT pattern: φησίν/λέγει embedded WITHIN a quote as an inline
      attribution tag — not a fresh speech-intro frame. These two classes
      are correctly distinguished by their surface signature (presence of
      speech-boundary · vs absence). No canon refinement needed.
    status: RESOLVED — canon R11 already produces Runge §7.2.2's recommended segmentation.
~~~

~~~yaml
# R18 — Vocative three-way refined treatment (canon §3.9)
# Detector: validators/colometry/check_r18_vocative.py
R18:
  rule_id: R18
  category: Editorial   # criterion mechanical; merge/split decisions reviewed
  layer: 3
  signature:
    trigger:
      line_has: vocative_NP
      AND:
        - line_has: non_2p_finite_verb
        - line_does_not_have: any_2p_element  # 2p verb OR 2p pronoun σύ/ὑμεῖς
    action: STRONG-SPLIT  # vocative owns own line (DEFAULT case)
  merge_overrides:
    - subject_appositive_merge: vocative_names_implicit_subject_of_2p_finite_verb
    - object_appositive_merge:  vocative_restates_explicit_2p_pronoun
    - discourse_frame_cluster:  frame_particle_plus_vocative_co_lined  # Loipon etc.
  references: |
    Wallace, "Vocative Case" — three uses (Direct Address [Simple / Emphatic-with-ὦ / Exceptional-Acts-usage], Exclamation, Apposition). Wallace's taxonomy is ORTHOGONAL to R18's colometric three-way (Default-own-line / Subject-Appositive-merge / Object-Appositive-merge): his categorizes vocative *usage type*, R18 categorizes *colometric placement* via same-clause-span 2p-element presence. The two interact at the **ὦ-emphasis signal** (refinement candidate, see below).
    BDF §§146–147 (Vocative Case — primary scholarly source).
  refinement_candidate_ω_emphasis:
    source: Wallace, "Direct Address — Emphatic (or Emotional)"
    claim: |
      In Koine, the ὦ-particle marks the vocative as emphatic / emotional (a reversal
      of the classical norm where bare ὦ was unmarked and bare-vocative was emphatic).
      Wallace cites Matt 15:28, Rom 2:1/3, 9:20, 1 Tim 6:11/20, Jas 2:20.
    corpus_survey_2026-05-13:
      8 instances:
        acts 1:1 ὦ Θεόφιλε / acts 18:14 ὦ Ἰουδαῖοι / acts 27:21 ὦ ἄνδρες /
        rom 2:1 ὦ ἄνθρωπε / rom 2:3 ὦ ἄνθρωπε / rom 9:20 ὦ ἄνθρωπε / 1tim 6:11 ὦ ἄνθρωπε /
        jas 2:20 ὦ ἄνθρωπε
    operational_question:
      Does ὦ-emphasis override R18's same-clause-2p-element merge-test (forcing own-line
      regardless of merge-conditions)? Initial hypothesis (2026-05-13 morning, single-source):
      yes — emphatic vocative IS a discourse-turn marker even when surface-embedded.
    audit_2026-05-13_corpus_state:
      8 instances audited against current v4/grk:
        - already own line (4): acts 1:1 ὦ Θεόφιλε / acts 18:14 ὦ Ἰουδαῖοι /
          acts 27:21 ὦ ἄνδρες / 1tim 6:11 ὦ ἄνθρωπε θεοῦ.
        - mid-line subject-appositive Class 2 (2): rom 2:3 (λογίζῃ δὲ τοῦτο, ὦ ἄνθρωπε
          ὁ κρίνων — 2p verb λογίζῃ on same line) / jas 2:20 (θέλεις δὲ γνῶναι, ὦ ἄνθρωπε
          κενέ — 2p verb θέλεις on same line).
        - line-initial, no 2p verb on line (2): rom 2:1 (ὦ ἄνθρωπε πᾶς ὁ κρίνων· ἐν ᾧ
          γὰρ κρίνεις τὸν ἕτερον,) / rom 9:20 (ὦ ἄνθρωπε, μενοῦνγε —).
    resolution_against_canon_§8:
      Applying Wallace's ω-emphasis reading WOULD force own-line splits on the 4 mid-line
      cases (rom 2:1, rom 2:3, rom 9:20, jas 2:20), overriding the existing R18 Class 2
      subject-appositive merge that 2p verbs λογίζῃ + θέλεις license. But this conflicts
      with canon §8 Marked Word Order (Fronting Paradox) — now linguistically grounded
      in Runge §9.2.5: "These effects are not an inherent meaning of the syntactic form;
      rather, they are an effect of using a form or structure in some marked way that
      breaks with the expected norm." The ω-marker carries the vocative's emphatic
      prominence WITHIN the breath unit; splitting onto its own line would IMPOSE
      editorial emphasis on top of what is already linguistically marked. Same anti-
      imposition principle that gates fronted-NP splits gates ω-vocative splits.
      Wallace's ω-emphasis is a SCHOLARLY OBSERVATION about discourse-pragmatic
      prominence — not a colometric mandate.
    status: |
      RESOLVED AGAINST refinement (2026-05-13 afternoon). After cumulative discourse-
      grammar reading (Runge §9.2.5 added to canon §8) + corpus audit, the ω-emphasis
      claim is interpreted as a discourse-pragmatic observation that the canon's
      anti-imposition principle (§8 Fronting Paradox) ARGUES AGAINST mechanizing as
      a split. Current R18 three-way treatment stands: ω-marked vocatives obey the
      same Class 2 subject-appositive / Class 3 object-appositive merge tests as
      bare vocatives. Wallace's reading is cited for completeness; canon does not
      split on the marker.
~~~

~~~yaml
# R18a-GNT — Patriarch-deity-triad indivisibility (canon §3.9a)
# Detector: validators/colometry/check_r18a_patriarch_triad.py
R18a-GNT:
  rule_id: R18a-GNT
  category: Mechanical
  layer: 3
  precedence_tier: 2   # indivisibility — wins over subtractive vetoes internal to triad span
  signature:
    trigger:
      verse_block_contains_in_order:
        - lemma: θεός
        - governing: Ἀβραάμ
        - then_within_same_verse: Ἰσαάκ
        - then_within_same_verse: Ἰακώβ
      split_across_lines: true
    action: STRONG-MERGE  # entire spanning sequence whole on a single line
  closed_lists:
    - R18a_patriarch_triad_variants           # see Closed-List Registry
  exclusions:
    - personal_name_list_without_theos_anchor  # Acts 7:8 genealogy
    - non_canonical_triad_orderings             # only Ἀβραάμ → Ἰσαάκ → Ἰακώβ
    - lead_in_title_phrases_on_separate_lines   # appositional continuations stay separate
  ported_from: BoFM_R18a_2026-05-11
  references: Wallace, "The Article: Special Uses — Apposition" (article repetition with apposition; the formula ὁ θεὸς Ἀβραὰμ καὶ ὁ θεὸς Ἰσαάκ... is article-repeated fixed apposition pattern Wallace's category covers). BDF §§268–269 (Article repetition with apposition — primary scholarly source).
~~~

~~~yaml
# R19 — Genitive absolute always own line (canon §3.10)
# Detector: validators/colometry/check_r19_genabs.py
R19:
  rule_id: R19
  category: Mechanical
  layer: 3
  signature:
    trigger:
      line_contains:
        - anarthrous_genitive_participle
        - agreeing_genitive_subject
        - main_clause_finite_verb   # gen abs co-linear with main clause
    action: STRONG-SPLIT
  exclusions:
    - adnominal: genitive_article_immediately_before_participle
    - PP_governed: preposition_within_3_tokens_before_ptc_or_subject
    - subordinator_finite: finite_verb_inside_subordinator_scope
        # ὅτε / ὅταν / ὡς / ἐπεί / ἐπειδή / ὅπως / relative pronouns
  known_FPs_allowlist:
    # See _KNOWN_FP_ALLOWLIST in detector — attributive NP structures the
    # adjacency heuristic can't resolve. If list grows past ~5 entries,
    # refine Class B filter (inter-line NP awareness) rather than extend.
    - (john, 7, 38)
    - (2cor, 6, 16)
    - (heb, 11, 1)
    - (matt, 9, 10)
    - (phil, 2, 15)
  references: |
    PRIMARY discourse-linguistic source: Runge §12.3.2 Genitive Circumstantial Frames. Runge (citing Fuller): "The function of the form of participle and noun/pronoun in the Genitive (without any other formal cause, such as a preposition) is to draw the reader's attention to certain information in a more detached way than other circumstantial participles.… The information in the GA acts as a frame in which to interpret the information of the main clause, or of an even larger discourse." Two primary discourse functions: (a) TEMPORAL TRANSITION without pericope-level discontinuity (Luke 4:40, 42); (b) TAIL-HEAD LINKAGE reiterating preceding action as background (Matt 2:1 Τοῦ δὲ Ἰησοῦ γεννηθέντος — Runge example 166, directly relevant to canon Matt 2 work). The "absolute" property (gen abs subject NOT in main clause) is what marks the discourse-detachment that warrants the own-line colometric treatment.
    Burton §451 (Genitive Absolute — construction definition + scope as separate from main clause); Wallace, "Verbal Participles: Absolute — Genitive Absolute" (modern aspect-aware treatment); BDF §§423–424 (Genitive Absolute — historical-grammar depth).
~~~

~~~yaml
# R25 — ὥστε Short-Consecutive-Result Binding (canon §3.14a)
# Detector: validators/colometry/check_r25_hoste_consecutive_result.py
R25:
  rule_id: R25
  category: Mechanical (mechanical detection) + Editorial (semantic conditions 2-3)
  layer: 3
  signature:
    trigger:
      line_starts_with: ὥστε
      AND:
        - line_word_count_inclusive_of_hoste: ≤8
        - co_referential_subject: implied_agent_of_infinitive_equals_matrix_subject  # SEMANTIC
        - no_camera_shift: true                                                       # SEMANTIC
    action: STRONG-MERGE-CANDIDATE   # merge ὥστε-clause onto matrix line
  verdicts_by_path:
    - words_le_8_after_illative_filter: STRONG-MERGE-CANDIDATE  # human review for conditions 2-3
    - words_gt_8: SPLIT-MAINTAINED  # word-count-exceeded
    - verse_initial_hoste: REVIEW-REQUIRED  # cross-verse defer
    - illative_hoste_surface_markers: SPLIT-MAINTAINED
  note: |
    Conditions 2 (co-referential subject) and 3 (no camera shift) are
    semantic/pragmatic and cannot be resolved by surface scan alone.
    The validator emits STRONG-MERGE-CANDIDATE; per-item human review
    applies the semantic conditions.
  references: Burton §234–237 (Result Clauses — ὥστε + indicative vs ὥστε + infinitive distinction), §371–374 (Infinitive of Result with τοῦ); Wallace, "Conjunctions: Adverbial — Result" + "Infinitive: Adverbial Uses — Result" (modern: actual vs conceived result); BDF §391 (Result clauses: ὥστε + indicative vs ὥστε + infinitive — the philological depth on this construction).
~~~

~~~yaml
# R28-ext — Speech-Act Announcement After Adverbial Frame (canon §3.6)
# Detector: validators/colometry/check_r28_speech_act_frame.py
R28-ext:
  rule_id: R28-ext  # extension of R28 / R11 family
  category: Mechanical
  layer: 3
  signature:
    trigger:
      line_ends_with_speech_boundary: [ano_teleia, colon]   # · or :
      line_contains:
        - finite_speech_verb_third_person_indicative
        - speech_verb_lemmas: [λέγω, εἶπον, φημί]
        - OR:
          - temporal_conjunction_with_inner_finite_verb     # ὡς/ὅτε/ὅταν + frame verb
          - participial_cluster_of_3plus_tokens_before_speech_verb
    action: STRONG-SPLIT  # frame → line 1; speech verb + dative-address → line 2
  exclusions:
    - X1: hoti_immediately_after_speech_verb         # R10 governs (indirect speech)
    - X2: legōn_eipōn_participial_adjacent_to_speech_verb  # ἀπεκρίθη+λέγων Hebraism
    - X3: frame_already_on_prior_line
    - X4: speech_verb_inside_subordinate_clause      # F1 from R11
  references: |
    PRIMARY discourse-linguistic source: Runge §7 Redundant Quotative Frames (§7.2.1 At Changes in Speaker/Hearer + §7.3.1 worked examples). R28-ext is the canon's name for the COMPLEX speech-act-announcement-after-frame pattern Runge analyzes: temporal/circumstantial frame → redundant quotative frame → quote. The split is licensed by the frame providing its own discourse-pragmatic unit BEFORE the speech-frame proper. Cross-linguistic warrant: the redundant frame's discourse function (slow down before authoritative pronouncement, signal change of direction) is what motivates own-line treatment for the speech-frame line.
    Wallace, "Conjunctions: Adverbial — Temporal" + "Verbal Participles: Dependent — Indirect Discourse" (frame + speech-act distinction). Burton §168 / §180–184 partial. BDF §§455–456 (Asyndeton + connective particles), §457 (Hebraistic ἀπεκρίθη καὶ εἶπεν speech-frame pattern — directly relevant to R28-ext class).
~~~

~~~yaml
# R1 — No-anchor rule (canon §3.1)
# Detector: scripts/scan_no_anchor_lines.py (scanner)
#           scripts/apply_no_anchor_merges.py (applier)
R1:
  rule_id: R1
  category: Mechanical
  layer: 3
  signature:
    trigger:
      line_lacks_anchor: true
      anchor_types:
        - finite_verb           # person 1/2/3, mood I/S/D/O
        - infinitive            # mood N
        - participle            # mood P (per detector; canon §3.1 narrows to predicate-ptc)
        - substantive_NAV       # nominative/accusative/vocative substantive
                                # NOT governed by a preposition on same line
    action: MERGE-CANDIDATE  # candidate for merging with neighbor (after two-prong exception check)
  exemptions:
    - single_line_verse         # atomic by definition
    - speech_intro_prefix
    - standalone_sentence_connective  # Ὥστε, Ἄρα οὖν, Διὰ τοῦτο
    - two_prong_exception_test_passes  # §2 / J1–J5 carve-out
  corpus_status: "860 no-anchor merges applied across 26 books (2026-04-12 sweep). Final scan: 0 unanchored lines remaining corpus-wide."
  references: Wallace, "Nominative Case" (Subject vs Predicate Nominative; Independent Nominative for proper names / titles / dependent statements — the substantive-head anchor cases). Burton's anchor classes (finite §156, infinitive §361, participle §418, substantive head implicit) inform the type taxonomy. BDF §§143–145 (Nominative — primary scholarly source), §466 (Pendent Nominative — left-dislocated subjects, also informs M4-GNT-1).
~~~

~~~yaml
# R8 — Framing Devices Attach (canon §3.3)
# No detector yet — manual editorial rule. Closest scanner: scan_line_ending_function_words.py (legality check post-split).
R8:
  rule_id: R8
  category: Mechanical (colometric placement) + Editorial (functional gloss)
  layer: 3
  signature:
    rule_form: |
      Framing devices LEAD their content — never sit line-final.
      A frame without its content is an orphan; content without its frame loses rhetorical context.
    closed_list:                       # see Closed-List Registry
      - R8_framing_devices             # ἰδού, διό, οὖν, νυν δέ, ἀλλά, γάρ, πλήν, τοιγαροῦν
    interaction_with_R2:
      note: R2 (never end on conjunction) already forbids most of these line-final.
              R8 is the FUNCTIONAL gloss on the colometric rule — explains WHY R2 holds for this set.
  references: |
    PRIMARY discourse-linguistic sources: Runge §2 Connecting Propositions (entire chapter — §2.1 ∅ asyndeton, §2.2 καί, §2.3 δέ, §2.4 narrative τότε, §2.5 οὖν, §2.6 διὰ τοῦτο, §2.7 γάρ, §2.8 μέν, §2.9 ἀλλά) + Levinsohn §5 Καί and Δέ in Narrative + §6 Τότε + §7 Thematic Development + §5.4.2 Background Material with Γάρ (Levinsohn is the SIL discourse linguist whose research Runge built on; Runge cites Levinsohn extensively throughout §2). Runge's 4-dimensional matrix (±continuity / ±development / ±correlation / ±forward-pointing + semantic-constraint slot) classifies every R8 framing device: οὖν = +cont +dev; διὰ τοῦτο = +cont +dev +causal; τότε = -cont +dev +temporal; ἀλλά = -cont -dev +correlation +correction. The matrix is the discourse-pragmatic grounding for R8 — each framing device leads its content because each constrains how the FOLLOWING discourse relates to context.

    BDF §§438–453 (Particles) + §§459–470 (Conjunctions) — primary philological source: γάρ §452, οὖν §451, ἄρα §451, διό §451, τοιγαροῦν §451, ἀλλά §448, πλήν §449. Wallace "Conjunctions: Logical Functions" (Inferential — ἄρα, διό, οὖν, πλήν, τοιγαροῦν; Contrastive — ἀλλά, πλήν; Explanatory — γάρ; Emphatic — οὖν; Transitional — οὖν).
  refinement_candidates:
    γάρ_is_backward_strengthening_not_forward_framing:
      sources_corroborating:
        - Runge §2.7 (Γάρ)
        - Levinsohn §5.4.2 (Background Material with Γάρ — verbatim:
          "The presence of γάρ constrains the material that it introduces to
          be interpreted as strengthening some aspect of the previous
          assertion, rather than as distinctive information.")
        - Heckert (Discourse Function of Conjoiners in the Pastoral Epistles)
        - Black (Sentence Conjunctions in the Gospel of Matthew)
      claim: |
        γάρ does NOT advance discourse — it strengthens/supports what PRECEDES.
        Two independent discourse-linguistic sources (Runge + Levinsohn) +
        two earlier monographs (Heckert + Black) converge: γάρ-introduced
        material is offline background that confirms or grounds a preceding
        assertion; it does not introduce a new development. The canon §3.3
        functional gloss ("framing devices whose function is to INTRODUCE WHAT
        FOLLOWS") is loose for γάρ — the COLOMETRIC rule (leads its content;
        never line-final) holds, but the functional gloss is over-extended:
        γάρ leads its content syntactically while functionally supporting
        the prior unit.
      operational_implication: |
        The "leads its content" colometric rule is unaffected — γάρ-line still
        must not be line-final. But the §3.3 prose "introduces what follows"
        gloss could be refined: "framing devices LEAD their content; their
        discourse function varies (γάρ supports prior; οὖν advances closely;
        ἀλλά corrects expectation)."
      status: |
        CORROBORATED across two independent discourse-linguistic sources
        (Runge + Levinsohn) — confidence elevated from single-source
        candidate. §3.3 prose refinement remains deferred until a canon
        editorial pass touches §3.3.
    δέ_is_development_marker_not_adversative:
      sources_corroborating:
        - Runge §2.3 (Δέ — entire section + §2.3.2 Function of Δέ)
        - Levinsohn §5.4.1 (Background Material with Δέ) + §5.3 (citing
          Buth 1992 table: δέ = +development, -close-connection)
        - Levinsohn §5.2 (Mark-specific: higher distinctiveness threshold —
          Mark δέ tends to carry adversative overtones, even though
          pan-Synoptic δέ is fundamentally a development marker)
      claim: |
        δέ is a +development marker with no inherent adversative/contrast load.
        Adversative force is context-dependent (semantic) not particle-marked.
        This RECASTS R17 (De-Contrast Overbreak / canon §3.8): the editorial
        discipline is not "weak-contrast vs strong-contrast" but "development-
        marker (default) vs contextually-emergent-adversative (special)." Most
        δέ in the GNT mark a new development without semantic discontinuity.
        Genre nuance: Mark has higher distinctiveness threshold than other
        Synoptics; Mark δέ skews adversative.
      operational_implication: |
        R17 §3.8 prose should be refined: δέ is fundamentally a development
        marker; "contrast" emerges from semantic context, not from δέ itself.
        Over-breaking on δέ-as-contrast is the failure mode R17 already names
        — Runge + Levinsohn give the linguistic warrant. The colometric rule
        (split on δέ + new-finite-clause) is unchanged because both readings
        coincide on the surface signature.
      status: |
        RESOLVED — applied (2026-05-13 afternoon). Canon §3.8 prose refined
        with Runge §2.3 + Levinsohn §5.4.1 + Buth-1992-via-Levinsohn-§5.3
        linguistic-grounding paragraph. Genre note added re: Mark's higher
        distinctiveness threshold (Levinsohn §5.2). False-positives list
        reframed in terms of "no new development" rather than "no new
        clause." Colometric rule unchanged (27 confirmed splits stand);
        editorial warrant updated from legacy contrast-pivot framing to
        development-marker framing.
    ἀλλά_is_correction_of_expectation_not_just_adversative:
      source: Runge §2.9 (Ἀλλά) + Heckert, *Discourse Function of Conjoiners in the Pastoral Epistles*
      claim: |
        ἀλλά is a "global marker of contrast" that introduces a CORRECTION of
        the expectation created by the prior conjunct. It cancels an incorrect
        expectation and puts a proper one in its place. Standard "adversative"
        gloss undercounts: ἀλλά is correction-marking, not just contrast.
      operational_implication: |
        R8 §3.3 table entry "alla — Adversative correction" is already partly
        right ("correction"). Could be sharpened: ἀλλά cancels expectation
        rather than merely contrasting. Minor refinement; no rule change.
      status: noted — already partly captured in §3.3 table gloss.
~~~
# Detector: scripts/scan_line_ending_participles.py (scanner only)
R20:
  rule_id: R20
  category: Editorial
  layer: 3
  signature:
    trigger:
      line_ends_with: participial_form
      AND:
        - next_line_starts_with: resolving_finite_verb
        - participle_is_predicate_not_attributive  # §3.10 distinction
    action: MERGE-CANDIDATE  # the participle resolves to next line's finite verb
  note: |
    Scanner surfaces candidates; canon §3.10 + §8 Participial Rules
    govern editorial application. Predicate vs attributive distinction
    is judgment-required per-construction.
  references: |
    PRIMARY discourse-linguistic source for post-matrix adverbial participles: Runge §12.3.4 Adverbial Participles Following the Main Verb. Runge: "Participles that follow the main verb have a somewhat different effect from those that precede it, in that they ELABORATE the action of the main verb, often providing more specific explanation of what is meant by the main action." The participle "relegates its action to supporting the main action" — by using a participle rather than a finite verb, the writer "places its action under the umbrella of the main verb." This IS the discourse-linguistic warrant for the 2026-05-13 15-merge sweep: post-matrix adverbial λέγω/εἶπον participles elaborate the matrix verb's speech-act, they don't introduce a new event, so they MERGE.
    Burton §418–457 (full Participle section); attributive (restrictive §420–421 / explanatory §427) vs predicative §429–433 distinction; adverbial subtypes §434–450 inform the predicate-vs-attributive judgment. Wallace, "The Participle" — Adjectival (Attributive / Predicate / Substantival) + Verbal (Dependent — Temporal, Manner, Means, Cause, Condition, Concession, Purpose, Result, Attendant Circumstance, Indirect Discourse, Complementary, Periphrastic, Redundant; Independent; Absolute — Nominative, Genitive) is the modern reorganization that adds aspect-theory framing (perfective vs imperfective vs stative) to Burton's tense-based treatment. BDF §§411–425 (Participle: Adjectival §413, Substantival §413, Predicate §414, Adverbial §417; **§420 Coincident/Accompanying participle = BDF's name for what Burton calls attendant circumstance and Wallace calls Attendant Circumstance**).
  refinement_candidate_runge_§12_3_4_enumerative_distinction:
    source: Runge §12.3.4 (Matt 4:23 διδάσκων/κηρύσσων/θεραπεύων + Rom 12:9-13 + Eph 5:17-22 chains)
    claim: |
      Runge's elaborating-participle analysis confirms R22 merge for 1-2 post-
      matrix participles (they elaborate the main verb). BUT Runge's worked
      examples include 3+ STACKED post-matrix participles that elaborate ONE
      main verb (Matt 4:23 three participles; Rom 12:9-13 chain of 12+; Eph
      5:19-22 chain). These ALSO subordinate to the matrix per Runge's analysis,
      yet the canon's enumerative-register modulation (§5 Register, line ~1533)
      stacks them as parallel ATUs because of the 3+ member threshold.
    operational_implication: |
      The canon's implicit distinction is sound: 1-2 elaborating participles
      MERGE to matrix (R22); 3+ STACK as parallel enumeration (§5 register
      modulation). Runge §12.3.4 grounds BOTH: discourse-subordination to the
      matrix is preserved in both treatments; the colometric distinction is
      about breath-unit vs visual-parallel-display, not about discourse
      hierarchy. Could be made explicit as a Runge-grounded distinction in
      §3.10 prose if a future refinement pass touches it.
    status: noted — canon implicitly captures via R22 + §5 enumerative-register cooperation.
~~~

~~~yaml
# R23 — Dative subject of infinitive (canon §3.12)
# Detector: scripts/scan_r23_dative_infinitive.py (scanner only;
#           empirical FP check — R23 may be one-verse crystallization)
R23:
  rule_id: R23
  category: Mechanical (canonical case Rom 12:3); under empirical review
  layer: 3
  signature:
    trigger:
      verse_contains:
        - speech_command_or_desire_class_verb
        - dative_NP_not_governed_by_preposition  # parsing[4] == 'D'
        - infinitive                              # parsing[3] == 'N'
      AND:
        dative_can_be_semantic_subject_of_infinitive: true  # SEMANTIC
    action: MERGE-CANDIDATE  # dative + infinitive bind as semantic unit
  note: |
    Adversarial over-structuring audit (2026-04-18) flagged R23 as
    most-suspect: possibly one-verse crystallization from Rom 12:3.
    Scanner empirically tests whether the pattern recurs elsewhere.
  references: Burton §361–417 (Infinitive section). Specifically §387–389 (Infinitive as object after verbs of commanding / desiring / hoping), §390 (Infinitive in Indirect Discourse — accusative subject), §406–417 (Infinitive with article governed by prepositions). The dative-subject-of-infinitive construction is unusual relative to Burton's accusative-subject default — Rom 12:3 may be classical-influenced. Wallace, "Dative Case" (uses including dative-of-reference) + "The Infinitive: Verbal Uses" (subject of infinitive, normally accusative; dative cases relatively rare per Wallace §195). BDF §§392 (Infinitive — accusative-subject default, already cited at canon §3.12), §§393–411 (Infinitive — uses + with article + with preposition).
~~~

~~~yaml
# M4-GNT-1 — Subject-orphan predicate completion (canon §3.18)
# Detector: validators/colometry/check_m4_gnt_1_subject_orphan.py
# (Full signature inline at §3.18; this block is the references-only summary.)
M4-GNT-1:
  rule_id: M4-GNT-1
  category: Mechanical (closed-list-eligible subject shapes); Editorial (length-backstop)
  layer: 3
  precedence_tier: 4   # merge-override; yields to Layer 1 vetoes + R6/R10/R7/R19
  signature_location: canon §3.18 (full UD-trigger + G1–G5 + universal-6 exclusions)
  references: |
    PRIMARY discourse-linguistic source: Runge §14 Left-Dislocations (entire chapter). Runge surveys the NT-grammarian aliases for this construction (cleft / hanging nominative / **pendent nominative** / casus pendens / independent nominative — §14.1) and grounds it in Chafe's cross-linguistic "one new concept at a time" constraint (§14.2). M4-GNT-1 IS Runge's left-dislocation as a colometric rule.

    Runge §14.3 identifies THREE functional sub-uses:
      §14.3.1 STREAMLINING — introduce complex entity in one clause not two; pronominal trace in unmarked post-verb position (<20% of NT instances).
      §14.3.2 PROCESSING FUNCTION — pronominal trace in clause-initial P1/P2 frame position to signal end-of-dislocation; entity complex enough to warrant the aid.
      §14.3.3 DISCOURSE-PRAGMATIC FUNCTION — pronominal trace creates THEMATIC HIGHLIGHTING of the topic (majority of NT usage). The pronoun's redundancy IS what produces the rhetorical effect.

    All three sub-uses receive the same colometric treatment under M4-GNT-1 (subject NP + matrix predicate = one ATU). The three sub-uses inform R27 authorial-style + §8 Marked Word Order — the same surface pattern carries different rhetorical weight depending on processing-vs-pragmatic motivation.

    BDF §466 (Pendent Nominative — primary scholarly source for the construction as a classical category; cited in canon §3.18 prose). Wallace, "Nominative Case — Independent Nominative" (modern complement). Burton has no dedicated treatment (verbal-syntax monograph; pendent constructions out of scope).
  refinement_candidates:
    sub_use_taxonomic_distinction:
      source: Runge §14.3.1–3 (three sub-uses)
      claim: |
        All three Runge sub-uses (streamlining / processing / discourse-pragmatic)
        currently receive the same M4-GNT-1 merge action. The taxonomic distinction
        IS NOT colometrically operative — colometry can't differentiate them — but
        IS rhetorically operative for downstream rules: R27 authorial-style and
        §8 Marked Word Order interact with sub-use #3 (discourse-pragmatic
        highlighting) in particular.
      operational_implication: |
        No change to M4-GNT-1 detector. Optional future enhancement: tag the
        merge-output with sub-use classification (P1/P2-resumptive vs
        post-verb-resumptive) for downstream R27/§8 analysis.
      status: noted — colometrically inert, downstream-rhetorically relevant.
    corpus_cross_check_runge_§14_examples:
      source: Runge §14.3.1 reference list (the long list at end of section)
      claim: |
        Runge enumerates ~50+ NT left-dislocation instances across all 3 sub-uses.
        Subset overlaps M4-GNT-1's 2026-05-11 sweep (~15-20 Cat A applied) but
        Runge's list is BROADER — many instances are streamlining (§14.3.1)
        cases the current SUBJECT_SHAPES_M4_GNT1 closed list doesn't capture
        (relative-clause-as-dislocation, ὅπου-locative-frame as dislocation,
        ὅτε-temporal-frame as dislocation).
      operational_implication: |
        The current 5-shape closed list (C1 vocative-subj / C2 NP-w-appositive /
        C3 NP-w-participial / C4 NP-w-relcl / C5 biographical-intro) covers the
        subject-NP cases but Runge's broader taxonomy includes locative + temporal
        left-dislocations (Matt 6:21 ὅπου-γάρ, Jas 3:16 ὅπου-γάρ, Matt 21:1
        ὅτε-frame, John 15:4 καθώς-frame). These are governed by §3.4 subordinate-
        clause-introduction breaks (R9) in the current canon, not by M4-GNT-1.
      status: noted — boundary clarification, not extension. R9 ≠ M4-GNT-1.
~~~

**Signature coverage status (2026-05-13).** 10 of ~26 rules signatured: R1, R8, R11, R18, R18a-GNT, R19, R20, R23, R25, R28-ext, M4-GNT-1 (R8 unsignatured-prior, now signatured with Runge §2 citation; M4-GNT-1 has both inline-§3.18 and refs-summary here). Unsignatured: R7, R9, R10, R12, R13, R14, R17, R22, R24, R27, R28, Layer-1 R2–R6. R7 and R2–R6 signatures live in Layer 1 syntax-floor (`data/syntax-reference/greek-break-legality.md`), not duplicated here. R12/R13/R14/R24/R27/R28 are Editorial / Principle — no auto-validator, signature would over-specify. R9/R10/R17/R22 detectors not yet implemented — signature pending detector authorship.

---

## Section 4: Operational Tests

*Purpose: **mainly operational** — diagnostic tests Claude runs to gate or sharpen editorial decisions (No-Anchor, Period, Image, Two-Prong, Q1/Q2, Completing-Predication, Validator Work-Queue). Each test has explicit inputs, outputs, and pass/fail criteria.*

These are the diagnostics actually run during editorial work.

### Runnable equivalents (test → invocation)

| Test | Runnable equivalent | Nature |
|---|---|---|
| **No-Anchor Test** | `py -3 scripts/scan_no_anchor_lines.py` (scanner) + `py -3 scripts/apply_no_anchor_merges.py` (applier) | mechanical |
| **Post-Split Function-Word Recheck** | `py -3 validators/run_all.py --baseline-check` (Layer 1 + Layer 3 sweep) + manual diff of the four gold-standard chapters (Mark 4, Rom 2:12-13, Acts 1:1-4, Heb 1:3) before/after the change | mechanical + manual diff |
| **Validator Work-Queue Convention** | `py -3 validators/run_all.py` (full sweep) + per-rule queue via `py -3 validators/colometry/check_r*.py --book <slug>` | mechanical |
| **Period Test** | judgment-only (no script — verb-class scope + grammatical ellipsis assessment is per-construction) | judgment |
| **Image Test** | judgment-only (close-eyes-picture-scene is human-cognitive) | judgment |
| **Two-Prong Exception Test** | judgment-only (cognitive + structural prongs require editorial assessment) | judgment |
| **Goldilocks Q1/Q2 Diagnostic** | judgment-only (prosodic-predication + pivot/resumption signatures require editorial reading) | judgment |
| **Completing-Predication Test** | judgment-only (paraphrase/remove/new-image diagnostics require human image-judgment) | judgment |

The judgment-only tests are deliberately not automated: each requires a per-construction reading that the structured layer (MorphGNT POS, Macula constituency) underdetermines. If you find yourself wishing one of them had a script, the right move is to ask "could Macula syntax-tree shape encode this?" — usually the answer is no, the test exists *because* the rule underdetermines and human judgment closes the gap.

**Wired automatic gates** (run by pre-commit hook, not by hand):
- Phase 1: cascade-staleness detection (v4/grk staged → eng-kjv + HTML must be staged with matching line counts)
- Phase 2: `py -3 scripts/scan_eng_kjv_coverage.py --baseline-check` (every Greek content line has English)
- Phase 3: `py -3 validators/run_all.py --baseline-check` (no new candidates vs baseline)

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

*Purpose: register-aware modulation layer. The three forces (§1) are register-flat at the base layer; actual practice modulates by **local** syntactic signatures, not coarse book-level genre. A chapter can shift register mid-verse — read the local signature, apply the appropriate modulation.*

**Register modulations** (not consumed by detectors; informs editorial judgment when rules leave room for variation):

- **Enumerative / stab-commata** — asyndetic or high-καί lists of parallel NPs/PPs (3+ members) → stack aggressively, each member its own ATU. 2 Cor 6:4-7 ἐν-catena, 2 Cor 11:23-27 κινδύνοις octet, Rom 1:29-31 vice catalog, Gal 5:19-23.
- **Gorgianic / bonded pair** — coordinate pairs with figura etymologica / sound echo / rhythmic balance (N=2 only) → merge as one ATU. M1 territory. `κόπῳ καὶ μόχθῳ` (2 Cor 11:27), `ἁγία καὶ ἄμωμος` (Eph 5:27).
- **Narrative frame-setting / FEF** — Front-End Frame: temporal/spatial/circumstantial protasis with deferred main clause suspending until the main verb lands. The frame is irreducible — no internal break produces a complete thought. Luke 3:1-2 paradigm (five genitive-phrase temporal adjuncts before ἐγένετο); Acts 1:1-4 periodic with participial chain; Eph 1:3-6 Pauline suspension. Lukan ἐγένετο + infinitive/ὅτι constructions are FEFs (ἐγένετο is a discourse marker, not semantically heavy).
- **Sermonic / indictment / woe-formula** — 2p imperatives stacked; vocatives paragraph-initial; οὐαί formulas; anaphoric rhetorical questions → tighter breaks; anaphoric stacking. Matt 23:13-29, Luke 11:42-52, Jude 11-16.
- **Argumentative / periodic** — γάρ / ὅτι / διότι / διὰ τοῦτο / ἄρα / οὖν causal-consecutive markers; ἵνα / ὥστε result chains; participial subordinate chains in main-clause matrix → **longer atomic-thought lines licensed by register.** Rom 1:4-5, Heb 1:1-2.
- **Apostrophic** — vocative density; 2p direct address; emotional appeal → vocative-indivisibility + framing-attach. Each vocative gets its own line. Gal 3:1, 4:19, 1 Cor 15:55.

The three forces govern; register changes which force is load-bearing in the local span. No new forces enter.

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

---

## Section 7: Audit-Workflow Reference (Mandatory-Audit Triggers for Canon Changes)

*Repurposed 2026-05-13 from a 2026-04-20 retired slot. Old §7 scholarly-grounding material (Chafe idea units, Kintsch propositions, Miller/Cowan chunking, dictation hypothesis, Marschall comparison) archived at `private/01-method/archive/colometry-canon-scholarly-framing-2026-04-20.md`. Audit-workflow content promoted here from prior §6.5 (placement under §6 "Precedent and Scope" was awkward — audit triggers are workflow, not precedent).*

**Pointer to framework.** The 12 mandatory-audit triggers, audit-skippable categories, commit-message declaration discipline, self-test, and audit-dispatch parallelization protocol are codified at [`atu-method/docs/framework.md §7.3–§7.6`](../../atu-method/docs/framework.md). Read those sections literally before any GNT canon commit.

**GNT-specific audit-trail conventions:**
- Audit-evidence references in GNT commit messages cite parallel-agent verdicts and §10 Update Log entries.
- The `validators/hooks/commit-msg` hook mechanically gates commit messages touching this canon file against §7.5 audit-evidence keywords. Source at `validators/hooks/commit-msg`; installed via `cp` to `.git/hooks/`.
- Provenance: trigger list codified in GNT on 2026-04-24 (cross-project import from BoFM); promoted to universal framework on 2026-05-12. This section now points to that universal statement.

---

## Section 8: Greek-Specific Application

*Purpose: Greek-specific operational supplements (verb valency table, marked word order paradox, exegetical hot-spot convergence, participial-rules detail, vocative/adverbial supplements, Standalone Verb Test, editorial-punctuation note, what-we-ignore scope). Subsections here amend §3 rules with Greek-language-specific detail. Research artefacts (stylometry findings, corpus statistics, multi-tier comparison results, Bezae caveat, four-tier pipeline, validation benchmarks) were archived to git history 2026-05-13 — not consumed by detectors.*

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

**Linguistic grounding (Runge §9 Information Structure — PRIMARY source; Levinsohn §2.6 + §3 — corpus-empirical backing).** Runge's discourse-grammar framework (drawing on Simon Dik's Functional Grammar and Lambrecht's cognitive-functional approach) provides the linguistic warrant for the Fronting Paradox. Levinsohn §2.6 provides the NT-Greek-empirical backing: out of 720 narrative-clauses-in-Acts with a subject or theme different from the preceding context, 310 have VS order vs 264 SV vs 146 ∅ — VS dominates as the default; SV is marked (point-of-departure OR focus/emphasis). Dik's preverbal template `(P1) (P2) VERB X` distinguishes two marked clause-initial positions:

- **P1 (Frame of Reference)** — contains PRESUPPOSED / topical information; establishes an explicit mental grounding point for the clause that follows (Runge §9.2.7).
- **P2 (Emphasis / Marked Focus)** — contains NEWLY-ASSERTED / focal information; the prominence added to the P2 element marks it as "what is relatively the most important … information in the setting" (Runge §9.2.6 quoting Dik).

The fronting paradox is the **P2-emphasis phenomenon**: an element placed in P2 is already syntactically marked for prominence by its position; the rhetorical effect IS the marked position. Crucially, Runge §9.2.5: *"These effects are not an inherent meaning of the syntactic form; rather, they are an effect of using a form or structure in some marked way that breaks with the expected norm for that context."* The prominence is carried by the position itself within the breath unit — splitting the fronted element onto its own line does not "preserve" the emphasis, it imposes EDITORIAL emphasis on top of what is already linguistically marked. This is precisely the §1 Imposing-vs-Revealing violation the canon's anti-imposition principle forbids.

**Diagnostic caution (Runge §9.2.7).** P1 vs P2 disambiguation is INFORMATION-STATUS analysis (presupposed vs newly-asserted), NOT word-order observation. The same fronted element in the same syntactic position can be EITHER a topical frame (P1) OR marked focus (P2) depending on what the surrounding context presupposes. The colometric default — keep the marked-word-order span as ONE atomic-thought line — is invariant across both readings: a P1 frame leads into its main clause as one breath unit; a P2 emphasis is realized within its main clause as one breath unit. In neither case does splitting recover something hidden; in both cases splitting imposes.

**Case studies:**

- **Gal 2:9 — split** (pillars characterization on own line): two distinct thoughts (the named persons vs. their ironic characterization). Subject + substantival-participial-phrase appositive, where the appositive is six words, non-trivial, and introduces the *dokountes* motif. Grammatical warrant for split is the substantival-participle-as-own-thought rule.
- **Gal 2:10 — merge** (fronted `τὸν πτωχόν` kept with `μνημονεύωμεν` on one line): `μνημονεύω` requires genitive for its object. The fronted genitive + restrictive `μόνον` create a marked word order whose rhetorical force depends on the grammatical unity staying intact. Per Runge §9.2.5: the P2-emphasis effect is carried by the marked position WITHIN the clause unit — splitting would mechanize what is already linguistically prominent.

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

*Purpose: index of retired rules + formulations. One-line-per-entry to prevent re-derivation of rejected ideas. For full retirement rationale, see git log + archived audit reports.*

### Retired rule numbers

| ID | Status | Folded into / replaced by | Retired |
|---|---|---|---|
| **R15** (μή/ἀλλά + οὐ/ἀλλά antithesis) | folded | R14 + §3.7 stacking framework | 2026-04-18 |
| **R16** (explanatory γάρ break) | folded | R8 framing-devices table (γάρ was already listed) | 2026-04-18 |
| **R21** (ellipsis principle) | absorbed | operational mechanism for R12/R13/R14, not a parallel rule | 2026-04-18 |
| **R25-old** (temporal-clause speech-intro merger) | folded | R11 speech-intro frame aggregation; superseded 2026-05-11 by R25 ὥστε-binding | 2026-04-18 / 2026-05-11 |
| **R26** (never split verb from direct object) | deleted | pure restatement of M2 | 2026-04-18 |
| **R29** (merge-override conditions pointer) | deleted | TOC entry, not a rule; M1–M4 stand alone | 2026-04-18 |
| **3 §3.7 subsections** (Need/Response, Imperative + Divine-Consequence, Cause-Consequence Bonded Beats) | retired | OVERFIT / FEEL-TEST / CORPUS-INCONSISTENT per 3-Opus hostile audit. Subsumed by M1 + J1 + R8 default + R28. Audit reports archived at `private/03-sessions/2026-04-24-bofm-discipline-imports/`. | 2026-04-25 |

Rule-number gaps (15, 16, 21, 25-old, 26, 29) preserved rather than renumbered to avoid breaking references in session notes, scanners, and prior commits.

### Retired criteria / formulations

| Formulation | Why retired | When |
|---|---|---|
| **Universal vocative rule** ("all vocatives get own line") | apposition exception: 2p-binding vocatives are inside one ATU, not beside it. Now §3.9 three-way treatment. | 2026-04-12 |
| **Verb-identity classification (fine-grained)** | exhaustive 131-construction audit found verb-class taxonomy doesn't generalize. COARSE cognition-vs-speech distinction (R10) DOES generalize; that's the only valid verb-identity rule. | 2026-04-13 |
| **Breath as a 4th criterion** | empirical test across 260 chapters found zero cases where breath was the sole deciding factor. Cognitive-chunking work absorbed by J5 substantive-adjunct justification. | 2026-04-20 |
| **Marschall posture** (load-bearing scholarly grounding) | reframed as opportunistic convergence, not load-bearing. Archived with other scholarly-framing material. | 2026-04-20 |
| **Earlier vocative explorations** (Attachment / Epistolary-vs-Narrative Distinction) | dissolved into universal + apposition rule on Luke 1:3 κράτιστε Θεόφιλε analysis — the correct distinction is grammatical (2p binding), not contextual. | 2026-04-12 |
| **Prior hierarchy versions** (Four-criteria-no-hierarchy 2026-04-09 → Syntax-as-floor 2026-04-11 → Absolutist "atomic-thought-wins-every-collision" 2026-04-12 → current Default + Unless 2026-04-16) | iterative refinement; only the current form is authoritative. | 2026-04-16 |
| **Duplicate "Section 6b"** (μή/ἀλλά antithesis + dative-subject-of-infinitive both labeled 6b) | restructured to R15 (§3.7, since retired) and R23 (§3.12). | document restructure |
| **Idou (ἰδού) three-type distinction** (deictic / mirative / logical-connective, adapted from parallel-corpus work) | Tested 2026-05-14 on the canon-named passages (Matt 1-2, Luke 1-2, Rev 1-3 — 24 instances). All three types are present in the sample, but colometric treatment is 100% uniform: ἰδού (or `καὶ ἰδού`) leads its content, never line-final, regardless of type. Type does not predict break behavior → not a colometric rule. Also requires authorial-intent interpretation to detect (deictic-vs-mirative is genuinely ambiguous on cases like `Ἰδοὺ ἡ παρθένος`) → out of scope per §1 Imposing-vs-Revealing. ἰδού is already correctly handled by §3.3 R8 (framing-device, leads content) + the §1 bidirectional-test cataphoric-presentative pass. The three-type distinction is a real discourse-semantic fact but belongs in exegetical commentary, not the colometric grid. | 2026-05-14 |

### Unsettled (active open question, not retired)

*(No active open questions. The ἰδού three-type distinction — the prior sole entry — was tested and retired 2026-05-14; see Retired criteria / formulations above.)*

### Goldilocks three-phase history (illustrative anti-pattern)

Phase 1 (early v4): over-enthusiastic splitting — particles and bare PPs got own lines. Phase 2 (session 9): over-correction via container-not-originator + no-anchor pass — 900+ merges, some collapsing parallel members into mega-lines. Phase 3 (session 10): subordinating-vs-coordinating refinement restored the right answer (current §3.16). Kept as a precedent that single-criterion enforcement without the "unless" mechanism produces oscillation.

---

## Section 10: Chronological Update Log

*Purpose: **dual-natured** — chronological reasoning trail. Recent entries documenting active-rule provenance are operationally referenced (cross-project import status, audit findings, retirement dates); older entries are historical narrative. When an entry documents an active rule, it is the canonical source for that rule's WHY/HOW WE KNOW/SCOPE.*

*The dated update blocks from the original document, preserved for the session-by-session reasoning trail.*

---

### 2026-05-13 — v3.1 focused trim + restructure

Per Stan's direction after a comparative review of the bofm/tanakh CLAUDE.md slim-down and an audit of canon-vs-architecture gaps. Pure restructure + history archive; no canon rule changed, no scope/precedence/closed-list claim added or modified.

**Trim (~1080 lines removed):**
- §10 chronological update log: pre-2026-05-01 entries archived to git history (run `git log -p --follow private/01-method/colometry-canon.md` for the full reasoning trail). Recent entries (2026-05-01 onwards) preserved as active-rule context.
- §8 research/justification subsections retired: Stylometry Findings preamble (per-author voice waveforms, epistolary-vs-narrative shift, Hebrews finding), Corpus Statistics table, Multi-Tier Comparison Results, Bezae Caveat, Four-Tier Pipeline (pre-4-plane framing), Validation Benchmarks. These were research artefacts, not rules detectors consume.
- §5 Six Registers table compressed from full-row taxonomy to bullet summary. FEF Framework folded into the FEF bullet (same content, half the lines).
- §9 Superseded Formulations compressed from prose-per-retirement to index tables (retired rule numbers, retired criteria/formulations). Full retirement narratives in git log.

**Restructure:**
- §3 Rule Index gains a **Detector** column: explicit pointer to `validators/{syntax,colometry}/check_r*.py` or `scripts/scan_*` for each rule (or `(not yet implemented)` / `(judgment-required)` markers). Closes the bofm-revealed gap where fresh-Claude didn't know which validator implemented which rule.
- §6.5 audit-workflow content promoted to §7 slot (previously a 2026-04-20 retired zombie). The audit-trigger pointer was awkwardly nested inside §6 "Precedent and Scope" — audit triggers are workflow, not precedent. §7 now houses the workflow reference; old §7 scholarly-grounding material remains archived.
- R18a-GNT Patriarch-Deity-Triad block relocated from §8 "Stylometry Findings" (where it was mis-shelved) to its proper home as new §3.9a, properly listed in the Rule Index.

**Extraction:** §10 entries that documented active rules' WHY/HOW WE KNOW/SCOPE (2026-04-21 ὅτι-leads convention, 2026-04-21 cross-verse continuity, 2026-04-20 H1/H2/H3/H4 reframes, etc.) have their substantive content already present in §3 rule entries + §1 framework pointers; the §10 entries duplicated it in chronological-narrative form. Removing the duplicates does not lose any active-rule provenance.

**Audit-status:** Audit-skippable per §6.5 (canon §6.5 trigger list, framework.md §7.3). This pass is pure history-archive + structural-relocation + Rule Index column-addition. No scope claim, no precedence claim, no closed-list extension, no carve-out, no rule reclassification. The §6.5 → §7 move is a cross-reference update; all live §6.5 cross-refs in active sections (§§0-4) updated to §7. Historical §6.5 references inside §10 entries preserved verbatim as period-accurate record.

**Cross-corpus consistency:** This restructure parallels the bofm/tanakh CLAUDE.md slim-down pattern Stan landed 2026-05-12/13 (verbose-orientation removal + Default-decisions table + structured-layer-first discipline). Sibling canons may benefit from analogous trim+restructure; flagged as a future cross-project task.

---

### 2026-05-12 — v3.0 Framework-Pointer Restructure

**What changed.** This canon was restructured from v2.0 (framework prose inline in §0/§1/§2/§6) to v3.0 (pointer-only for universal material; GNT-specific rule body preserved in full). The restructure mirrors the BoFM canon v3.0 pattern executed 2026-05-11 in the sibling readers-bofm repo.

**Sections repointed:**
- `## Foundational premise` + `## Posture` (v2.0 preamble) → Part I §0 pointer to `framework.md §0.1/§0.3`; GNT intellectual lineage (Skousen + Stan-arrival narrative) preserved in §0 GNT-specific framing.
- `## Architecture` (three-layer model) → Part I §0 pointer to `framework.md` + `architecture.md` (four-plane model supersedes); GNT-specific Layer 1/Layer 2 details preserved in §0 GNT-specific architecture.
- `## Section 1: The Framework` → stub pointer; all GNT-specific worked examples preserved as GNT-corpus instantiations in Part I §1.
- `## Section 2: The Unless Conditions` → pointer to `framework.md §1.4–§1.9`; all GNT-corpus worked examples preserved in §2.
- `## Section 6: Precedent and Scope` including §6.5 mandatory-audit triggers → pointer to `framework.md §7.2–§7.8`; GNT-specific provenance preserved.

**Sections kept in full:** §3 (Rules R1–M4-GNT-1), §4 (Operational Tests), §5 (Register Operationalization), §8 (Greek-Specific Application), §9 (Superseded Formulations).

**Audit-status:** Audit dispatched per §6.5 (triggers #1, #5, #11). See commit message for audit evidence.

**Line count:** v2.0 was 2735 lines; v3.0 was ~2459 lines. The "Marked Word Order (Fronting Paradox)" subsection was relocated from the retired §1 prose into §8 Greek-Specific Application (its correct home — Greek's case-marked freedom of word order is per-language phenomenon).

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

### Pre-2026-05-01 chronological entries — archived to git history

The pre-2026-05-01 update-log entries (covering the 2026-04-09 through 2026-04-28
development arc: foundational reframing, scholarly-framing retirement, six-rule
consolidation, the three §3.7 retirements, the §6.5 audit-trigger codification,
hook port from Tanakh, Step 0 input filter, terminology migration prep, and the
voice/AI-slop cleanup passes) lived here through 2026-05-12. They were a
chronological reasoning trail that git history captures verbatim:

```
git log --follow private/01-method/colometry-canon.md
git log -p --follow private/01-method/colometry-canon.md
```

Provenance of any active rule is now codified in the rule's own §3 entry
(WHY / HOW WE KNOW / SCOPE per defensibility-capture). Entries from
2026-05-01 onwards retained below for active-rule context.

---

*Document created: 2026-04-09. Major restructures: 2026-04-16 hierarchy reframe; 2026-04-18 six-rule consolidation; 2026-04-20 foundational/scholarly-framing retirement; 2026-05-12 v3.0 framework-pointer extraction; 2026-05-13 v3.1 focused trim. Full chronology in git history.*
