# 04 — Editorial Workflow

## The Pipeline

```
SBLGNT source (canonical, never edit)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
  auto_colometry.py (tier 1)    v2_colometry.py + macula_clauses.py (tier 2)
        │                                  │
        ▼                                  ▼
  v1-colometric/*.txt            v2-colometric/*.txt  ← active
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
              build_books.py  (text → HTML, currently reads v2)
                       │
                       ▼
              books/*.html  (served by web app)
                       │
                       ▼
              index.html loads fragments via fetch()
```

## Current State (2026-04-09)

**All 260 chapters have v2 syntax-tree-driven text.** The web app serves v2 output. v1 pattern-matched output is preserved in v1-colometric/ for comparison. No hand editing has begun yet. The v2 output uses scholar-annotated clause boundaries from the Macula Greek syntax trees, representing a significant improvement over v1 in participial phrase detection, genitive absolute isolation, and prose segmentation.

## Hand-Editing Process

When Stan is ready to hand-edit a chapter:

1. Open the chapter file in VS Code (e.g., `data/text-files/v1-colometric/mark-04.txt`)
2. Edit line breaks only — never change the Greek words, accents, or breathing marks
3. Use the methodology in `02-colometry-method.md` as the guide
4. Run `PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py --book mark` to rebuild that book's HTML
5. Test locally with `python -m http.server 8000` and visit `localhost:8000`
6. Commit both the edited text file and the rebuilt HTML

## Source Text Format

Each chapter file in `v1-colometric/`:

```
4:1
Καὶ πάλιν ἤρξατο διδάσκειν παρὰ τὴν θάλασσαν.
καὶ συνάγεται πρὸς αὐτὸν ὄχλος πλεῖστος,

4:2
καὶ ἐδίδασκεν αὐτοὺς ἐν παραβολαῖς πολλά,
καὶ ἔλεγεν αὐτοῖς
ἐν τῇ διδαχῇ αὐτοῦ·
```

- Verse reference on its own line (e.g., `4:1`)
- Sense-lines below, one per line
- Blank line between verses
- No header lines (auto-formatter output is clean)
- No indentation (flat structure)

## What Never Changes

- The Greek text itself (words, accents, breathing marks, punctuation)
- Verse references
- The canonical SBLGNT source files

## What Stan Edits

- **Line break positions only** — where one line ends and the next begins
- This is the only editorial tool in the project

## Protection of Hand-Edited Chapters

**WARNING:** Running `auto_colometry.py` will overwrite ALL files in v1-colometric, destroying any hand edits. There is currently no protection mechanism for this.

**Future need:** A way to mark chapters as "hand-edited, do not overwrite" — possibly a manifest file, or moving hand-edited chapters to a `v2-editorial/` directory (mirroring the BOM Reader's v1→v2 distinction).

**For now:** Be careful. If running the auto-formatter, ensure no hand-edited chapters will be lost. Check `git diff` before committing.

## Review Process

When Claude proposes line-break changes, use the same category framework as the methodology:

- **Category A — Mechanical improvement:** suboptimal break, no rhetorical or theological stakes. Propose confidently.
- **Category B — Rhetorical shape:** changing the break changes how the speaker builds an argument. Flag and ask.
- **Category C — Theological weight:** break placement makes a doctrinal point. Flag and discuss.

## Comparison: Auto-Formatter vs. Hand-Crafted Quality

Example — Mark 4:8 (auto-formatted):
```
καὶ ἄλλα ἔπεσεν εἰς τὴν γῆν τὴν καλήν,
καὶ ἐδίδου καρπὸν ἀναβαίνοντα καὶ αὐξανόμενα,
καὶ ἔφερεν ἓν τριάκοντα καὶ ἓν ἑξήκοντα καὶ ἓν ἑκατόν.
```

Same verse, hand-crafted:
```
καὶ ἄλλα ἔπεσεν εἰς τὴν γῆν τὴν καλήν,
καὶ ἐδίδου καρπὸν ἀναβαίνοντα καὶ αὐξανόμενα,
καὶ ἔφερεν ἓν τριάκοντα
καὶ ἓν ἑξήκοντα
καὶ ἓν ἑκατόν.
```

The hand-crafted version stacks the triadic yield — making Mark's climactic parallelism visible. This is the editorial refinement that turns a functional first pass into a genuine colometric reading edition.

## Priority for Hand Editing

No priorities have been set yet. Some natural starting points:

- **Mark** — shortest Gospel, narrative-heavy, paratactic style makes colometry especially revelatory
- **Acts 17** — Areopagus speech tests rhetorical colometry
- **Romans 8** — dense Pauline argumentation, good test for epistolary style
- **John 1:1-18** — prologue has known poetic structure, good validation case
- **Hebrews 1** — elevated prose style, interesting comparison to Paul

---

### Established — 2026-04-09
- Full editorial workflow documented
- Auto-formatter vs. hand-crafted quality comparison demonstrated
- Protection mechanism for hand-edited chapters flagged as future need
- No hand editing has begun yet — all 260 chapters are at v1 quality

---

### Update — 2026-04-09 (session 2)
- Pipeline updated to four-tier model (v1 pattern → v2 syntax trees → v3 rhetorical patterns → v4 editorial hand)
- v2 output now active — web app serves syntax-tree-driven colometry
- v1 output preserved for comparison
- Comparison: v2 resolves the major v1 limitation (long unbroken lines with participial phrases, genitive absolutes, infinitival clauses). Acts 1:2, which was one line in v1, now breaks into four clauses. Mark 4:8 triadic yield stacks automatically from the tree structure.

---

### Update — 2026-04-09 (session 2, continued)

#### v3 Validation Against Gold Standard

v3 output was validated against the hand-crafted Mark 4 gold standard (preserved in `C:\tmp\gnt-colometry-test\`). The match is near-complete — the automated pipeline now produces output that closely approximates editorial judgment on the test chapter that originally defined the project's vision.

#### Key v4 Editorial Decisions Identified

During review of v3 output, several cases were identified where automated rules cannot resolve the breaking decision — these are genuine editorial judgments for v4:

- **Participial phrase attachment:** Whether a circumstantial participle merges with its main verb or stands alone as its own colon is often an editorial judgment. The grammar permits both readings; the choice depends on whether the participle frames the action (own line) or is tightly integrated with it (merged). Example: a genitive absolute that is short and closely tied to the main clause vs. one that sets an independent temporal scene.

#### The Automated/Editorial Boundary

The distinction between automated rules (v1-v3) and editorial judgment (v4) is now clearer:

- **Automated rules (v1-v3)** enforce consistent, defensible grammatical criteria. Every rule has independent warrant (Wallace, Marschall, Macula tree structure). The same rule applied to the same text always produces the same output. This consistency is what makes downstream quantitative analysis valid.
- **Editorial judgment (v4)** handles cases where multiple valid breakings exist. The grammar permits more than one analysis; the editor chooses based on rhetorical effect, performative feel, theological sensitivity, or contextual flow. These decisions are legitimate and necessary but inherently non-algorithmic.

This distinction matters for the publishable research: the automated tiers produce replicable data suitable for quantitative analysis; the editorial tier produces a reading edition optimized for human use.

#### Quality Assurance: Adversarial Testing Pattern

After any significant change to merge/split rules, dispatch parallel adversarial agents before committing:

1. **Feature-specific adversary** — tests the new rule for over-merges, under-merges, and edge cases
2. **Rule-interaction adversary** — tests all rules together for cascading errors and fights between passes
3. **Benchmark regression adversary** — re-runs Marschall comparison and Bezae multi-tier to check for regressions

This pattern catches HIGH severity issues (rule interactions, sentence boundary violations, over-splitting of particles) that code review alone misses. Established in session 3 after discovering the adversarial approach caught issues across Rev 1:5, Heb 1:3, Mark 4:22, and 94 ἰδού over-splits.

#### Standard Operating Procedures

**When fixing a bug:**
1. Identify the class of problem (not just the single instance)
2. Enumerate ALL instances of that class in the Greek language
3. Fix them all in one commit
4. Example: finding elided ἀλλʼ not handled → immediately add ALL Greek elided forms (παρʼ, ἀπʼ, ἐπʼ, ὑπʼ, κατʼ, μετʼ, διʼ, ἀφʼ, ἐφʼ), not just ἀλλʼ

**When changing the pipeline (MANDATORY two-phase pattern):**
1. **Phase 1 — Algorithm change:** One agent modifies the script (v3_colometry.py, macula_*.py, etc.). This is a single-file code change.
2. **Phase 2 — Corpus rebuild:** 8 SEPARATE agents run the modified script on genre groups: Mark / Matthew / Luke-Acts / John+Johannine / Pauline / Hebrews / General Epistles / Revelation
3. These are ALWAYS two separate dispatches. NEVER dispatch one agent to do both code change AND full corpus rebuild.
4. Never run one agent on all 27 books — Luke-Acts alone is a quarter of the NT.
5. When the task is "find and fix," each agent should find AND fix in its section, not just report.
6. This is not optional. Every violation of this pattern has resulted in a bottleneck.

**When proposing rule changes:**
1. Generate multiple candidate approaches (3-5 angles)
2. Dispatch parallel adversarial agents to evaluate EACH approach against real corpus data
3. Each evaluation agent tests: accuracy rate, false positive rate, implementation complexity
4. Compile ranked recommendation with data before implementing anything
5. Only implement the top-ranked approach (or top 2 if they're complementary)
6. This prevents building the wrong solution and having to undo it

**When running adversarial agents:**
1. Give specific, scoped mandates — not "review all of Luke-Acts" but "check Luke 1, 15, Acts 1, 2, 17 for these 5 specific patterns"
2. Use haiku model for read-only review tasks (faster, cheaper)
3. Use opus for tasks requiring code changes or complex reasoning
4. Each agent should find AND fix, not just find (avoid sequential bottleneck)
5. Split by genre group for corpus-wide reviews

**When adding split/merge rules:**
1. Every split must validate both halves are viable cola
2. Never split: article+noun, preposition+object, negation+verb, noun+genitive modifier, noun+possessive pronoun
3. After any split pass, re-run the dangling function word fix
4. Test on Mark 4 (gold standard), Rom 2:12-13 (Marschall), Acts 1:1-4 (most-reviewed), Heb 1:3 (participial images)

---

## YLT Alignment Editorial Workflow

### Overview

The YLT English layer aligns Young's Literal Translation (1898, public domain) to the colometric line breaks established in the Greek text. The alignment is approximately **60% automated and 40% hand-refinement**.

### Automated Alignment

The `ylt_align.py` script performs the initial alignment:

1. Reads the Greek colometric chapter file to determine how many lines each verse has
2. Reads the corresponding YLT verse text from `data/ylt-verses.json`
3. Splits the YLT text at clause boundaries that correspond to the Greek colometric breaks
4. Writes aligned YLT files with the same line count as the Greek

Where YLT closely follows Greek clause order (which is frequent, given Young's methodology), the automated alignment produces clean results.

### Manual Adjustment

Where YLT departs from Greek clause order, manual adjustment is needed. Common cases:

- **Rearranged clauses:** Young sometimes moves a subordinate clause for English readability. The YLT text must be re-split to match the Greek line structure.
- **Merged clauses:** Where the Greek has two lines but YLT renders the content as a single English phrase, the English must be split into two coherent lines.
- **Expanded/contracted rendering:** Where YLT uses more or fewer words than the Greek for a given colon, the English line must still read as a complete thought.

### Review Process

The review process for each chapter:

1. Run `ylt_align.py` to generate the initial automated alignment
2. Open the Greek and YLT chapter files side by side
3. Compare line by line: does each English line represent a coherent thought?
4. Where an English line is incoherent or fragmentary, adjust the split point
5. Verify the line counts match (Greek and YLT must have identical line counts per verse)
6. Run `build_books.py` to rebuild the HTML
7. Test in the web app: toggle between Greek/English/Both and verify each view reads correctly

### Two Independent Claims

With the YLT layer, the project now makes two claims that must be reviewed independently:

1. **Claim 1 — Colometric structure:** The line breaks reflect Greek discourse structure. This is validated by the existing methodology (Marschall benchmark, Bezae comparison, grammar-driven rules).
2. **Claim 2 — YLT alignment accuracy:** The YLT splitting accurately represents those breaks in English. This requires its own review: does each English line read as a complete thought? Does the English faithfully represent the structural claim made by the Greek break?

A bad YLT split can undermine confidence in the Greek colometry even if the Greek break is correct. Both claims deserve independent scrutiny.

### YLT Editorial Files

YLT chapter files follow the same format as Greek colometric files:

```
9:1
And Saul, yet breathing out threatenings and slaughter to the disciples of the Lord,
having gone to the chief priest,

9:2
asked from him letters to Damascus unto the synagogues,
that if he may find any being of the way,
both men and women, he may bring them bound to Jerusalem.
```

- Verse reference on its own line
- Sense-lines below, one per line (matching Greek line count)
- Blank line between verses
- Same file naming convention: `{abbrev}-{chapter}.txt` in `data/text-files/ylt-colometric/`

---

### Update — 2026-04-09 (YLT integration)

- YLT alignment editorial workflow documented
- Automation/hand-refinement ratio estimated at 60/40
- Two-claim review framework established: colometric structure and YLT alignment accuracy are independently reviewable
- Manual adjustment cases identified: rearranged clauses, merged clauses, expanded/contracted rendering
- Review process: line-by-line comparison, coherence check, line count verification, web app toggle testing

---

### Update — 2026-04-10 (YLT alignment rewrite)

#### The Problem

The original YLT alignment algorithm (session 3) used a **bag-of-words gloss matching** approach: Macula glosses were pooled per colometric line, then each YLT word was fuzzy-matched against all lines simultaneously. This destroyed word-position information and caused cascading failures:

- **False anchors from prefix matching:** "he" matched "heaven" via a 4-char prefix rule, poisoning downstream assignments.
- **Bag-of-words pooling:** Collecting glosses per line as unordered sets lost the sequential correspondence between Greek word order and English word order.
- **Monotonicity enforcement cascade:** One bad anchor forced all subsequent words onto wrong lines via the non-decreasing line-assignment constraint.
- **Interpolation failures:** Unmatched words were distributed proportionally between anchors, which produced gibberish when anchors were wrong (e.g., Mark 4:4 "and it; devour").

Mark 4 was used as the diagnostic thermometer. Initial spot-checking revealed obvious problems in 4:4, 4:5, 4:6, 4:7, 4:8 — verses where the YLT is highly literal and alignment should have been trivial.

#### The Fix: Sequential Forward-Scan Alignment

The algorithm was completely rewritten around a different principle: **walk both the Macula gloss sequence and the YLT text left-to-right in parallel**, matching content words against ordered anchors. The approach:

1. **Map each Macula word to its colometric line** (Greek word → line index via normalized form matching against colometric text).
2. **Build an ordered anchor sequence** from the Macula words: each content word's gloss/english attributes become matchable tokens, tagged with the line index. Stop words (the, a, of, and, it, etc.) are excluded as anchors.
3. **Forward-scan the YLT text:** for each YLT content word, try to match against the next few anchors in sequence. When a match is found, record the line assignment and advance the anchor pointer.
4. **Find line transitions:** where consecutive matched words jump from line K to line K+1, that's where the English split goes.
5. **Gap split heuristic:** for the words between two matched anchors on different lines, prefer clause-starting conjunctions > punctuation boundaries > midpoint.

This preserves word-position information (no pooling), handles repeated words naturally (sequential consumption), and automatically re-pegs when Greek breaks change.

#### Three Refinement Rounds via Adversarial Audit

After the initial rewrite fixed the gross failures (4:4 "and it; devour", 4:6 scrambled lines), an adversarial audit of all 41 Mark 4 verses found 12 remaining problems in three pattern classes:

**Pattern 1 — Truncation/merge (5 verses: 4:16, 4:18, 4:20, 4:22, 4:24):**
Greek function words (ὅς, οὗτοι, τίς) glossed as "who", "these", "what" were acting as false content anchors, causing the algorithm to split too early and produce short stubs ("'And these are they," / rest of line merged with next). Fix: added relative/interrogative/demonstrative pronouns to stop words; raised substring match minimum from 5 to 6 characters; added hide/secret synonym for Macula vocabulary gaps.

**Pattern 2 — Dangling words (3 verses: 4:8, 4:21, 4:25):**
Words at line boundaries pulled onto the wrong line. Two sub-causes: (a) the word-order-swap lookback was re-matching already-consumed anchors for repeated glosses like "one" (ἕν appears on both lines 41 and 42); (b) negation/additive markers ("not", "also") were invisible as stop words even though they start new clauses. Fix: track consumed anchors to prevent re-matching; removed "not" from stop words since it's semantically significant at clause boundaries.

**Pattern 3 — Line count mismatch (2 verses: 4:32, 4:41):**
Some Greek lines (like Τίς ἄρα οὗτός ἐστιν — "Who then is this") consist entirely of stop-word glosses, producing zero anchors and causing the line to be merged with its neighbor. Fix: detect anchorless lines and promote their stop-word glosses to anchors; prefer midpoint clause starters in gap splits (not first one); re-split longest line at clause boundary instead of empty-padding.

#### Results After All Fixes

| Metric | Before (session 3) | After rewrite |
|--------|-------------------|---------------|
| Gloss-aligned | ~99.8% | 99.9% (7,935/7,939) |
| Clause fallbacks | ~15 | 2 |
| Mark 4 problems | 12+ obvious | 0 (adversarial-verified) |
| Algorithm | Bag-of-words + interpolation | Sequential forward-scan |

The alignment now automatically re-pegs when Greek colometric breaks change — it derives English splits from the Macula word-level Greek→line mapping, so future editorial changes to Greek line breaks cascade correctly to the English layer.

#### Key Design Principles Established

- **Greek breaks are the source of truth.** The English simply needs to be brought into alignment.
- **YLT is literal enough that alignment should normally be easy.** When it's not, the algorithm is wrong — not the data.
- **Sequential matching, not bag-of-words.** Word-position information must be preserved.
- **Adversarial audit after every significant change.** The Mark 4 thermometer pattern: fix, rebuild, audit all verses, fix what the audit finds, repeat until clean.
- **Three parallel adversarial agents per problem class.** Each agent diagnoses one pattern, proposes a fix, and tests it. Fixes are then synthesized and applied together.

---

### Update — 2026-04-10 (session 4)

#### YLT Alignment Rewrite and Abandonment

The session began with further refinement of YLT alignment. Manual review of Mark 4 YLT output (after the adversarial audit fixes from session 3's update) revealed 6 additional errors: orphaned pronouns, split phrasal verbs, and split conjunctions. The fundamental problem: the alignment algorithm has no English quality gate — it can match words to lines but cannot evaluate whether the resulting English lines read as coherent phrases.

This, combined with YLT's archaic language barriers, led to the decision to abandon YLT in favor of WEB (World English Bible).

#### Switch from YLT to WEB

- **WEB** (World English Bible, public domain, modern English) replaces YLT as the English rendering layer
- Alignment approach changed to "double-wire": Greek to Macula English (perfect by construction) to WEB (LCS alignment), with spaCy dependency parsing as a cut-point validator
- Known limitation: WEB sometimes restructures sentences differently from Greek, causing unavoidable alignment mismatches on approximately 10% of verses
- YLT alignment scripts retained for historical reference but are no longer in the active pipeline

#### Colometric Methodology Reset

YLT/WEB alignment work revealed that the v3 colometric pipeline has an approximately 10-12% error rate — problems in the GREEK breaks, not just English alignment:
- Mark 4:1: subject split from verb
- Matt 16:25: inconsistent conditional treatment

Critical finding: v1 (simple conjunction rules) got some verses RIGHT that v3 (sophisticated Macula-driven pipeline) BROKE. Root cause: v3 optimizes for grammar rules, not the framework's primary forces (atomic thought, single image), with syntax operating as a subtractive constraint rather than a primary driver. The v2/v3 layers were actively degrading some of v1's principle-driven breaks.

This does not mean v3 is worse overall — it is better on most verses. But "more sophisticated" does not equal "more correct" in every case. The v4 editorial pass is now understood as essential corrective work, not optional polish.

#### Mark 4 v4 Editorial Gold Standard

Stan hand-edited Mark 4 as the first v4 editorial chapter. The `v4-editorial/` directory was created as the tier 4 (editorial hand) output location.

Five new colometric principles were established during this editing pass and documented in `02-colometry-method.md`:

1. **Ellipsis:** Elided verbs are real predications — triadic stacks (e.g., "thirty... sixty... hundred") each get their own line because each implied verb is a separate predication.
2. **Subordinate clause attachment:** Adjectival subordinate clauses merge with their head noun; adverbial subordinate clauses stand alone as separate cola.
3. **Vocative attachment:** Vocatives join the speech they introduce; imperatives stand alone as their own cola.
4. **Paradox pairs:** Antithetical pairs ("whoever wants to save his life will lose it") merge as one unit — the paradox is a single image.
5. **καί + finite verb:** Primary break signal in narrative Greek. This is the most reliable indicator of a new colon in Markan narrative.

Additional refinements from the editing pass:
- Verbs describing the same phenomenon merge (sprout and grow = one image)
- Sequential causation splits; simultaneous paradox merges
- Short genitive absolutes modifying speech introductions merge (adverbial framing)
- Indirect questions stay with their governing verb

#### Updated Pipeline Diagram

```
SBLGNT source (canonical, never edit)
        |
        v
  v2_colometry.py + macula_clauses.py (tier 2: syntax-tree clause boundaries)
        |
        v
  v3_colometry.py (tier 3: rhetorical patterns + merge rules + safety guards)
        |
        v
  v4-editorial/ (tier 4: Stan's hand edits — overrides v3 where present)
        |
        v
  web_align.py (double-wire WEB alignment with spaCy validation)
        |
        v
  build_books.py (reads v4 > v3 for Greek, web > ylt for English -> books/*.html)
        |
        v
  books/*.html -> index.html loads via fetch()
```

#### What's Next (established end of session 4)

- Build the diagnostic scanner for English alignment quality (apply three criteria to English output)
- Extend v4 editorial to more chapters: Acts 17 (rhetoric), Romans 8 (argumentation)
- Evaluate tree-first colometric approach: start from Macula clause structure instead of pattern matching
- The English alignment problem is partially solved but has inherent limitations when translations restructure sentences

---

### Update — 2026-04-11 (post v4 editorial review)

#### System-Wide v4 Editorial Review Completed

120 chapters now have v4-editorial files, produced by 6 genre-group agents operating in parallel across the corpus. Approximately 944 line changes total. Most common fix patterns:

- **Fragment merges:** Short orphaned lines (articles, particles, prepositions) merged back into adjacent cola
- **Dangling postpositive repairs:** Postpositive particles (δέ, γάρ, οὖν, μέν) that ended up at line-end moved to start of next line
- **Parallel stacking corrections:** Parallel structures (μέν/δέ, triadic lists, antithetical pairs) vertically aligned
- **Speech intro isolation:** Direct speech introductions (λέγει αὐτοῖς·, ἀπεκρίθη καὶ εἶπεν·) given their own line
- **Adjectival clause attachment:** Relative clauses modifying a head noun merged with that noun's line

Approximately 52 chapters still need second-pass editorial work.

#### English Layer: Structural Glosses

The English is now a purpose-built rendering tracking Greek clause order by construction. No alignment algorithm — alignment is guaranteed because each English line was written to match its Greek line. 260 chapters complete. This eliminates the WEB/YLT alignment problem entirely.

#### Universal Vocative Rule

All vocatives get their own line — each is an atomic thought (complete address act, with natural pause before and after). One exception: repeated vocatives (Κύριε κύριε). Supersedes the earlier three-category vocative distinction.

#### Cross-Pollination from BOM Reader

Ten principles ported and adapted for Greek: FEFs, three-category framework, framing devices, ἰδού distinction, syntactic bonds, escalation/restriction, vocative rule, ὅτι distinction, authorial style principle, parallel diagnostic scanner.

#### Methodology Maturation

The framework's three forces (atomic thought, single image, syntax-as-constraint) are now supported by approximately 15 sub-principles, all tested against editorial practice in the Mark 4 and Acts 1 gold standard chapters.

#### Gold Standards

- **Mark 4** — original gold standard (session 4), narrative parable discourse
- **Acts 1** — second gold standard (v4 editorial review), mixed narrative/speech with complex participial chains

---

### Update — 2026-04-11 (session 6: all 260 chapters v4-editorial)

#### All 260 Chapters Now v4-Editorial

The v4-editorial directory is now the single source of truth for all 260 chapters of the Greek New Testament. No gaps remain. The final 72 previously-unreviewed chapters were editorially reviewed by 9 parallel agents across genre groups.

#### English Gloss Quality Audit

260/260 structural English glosses are in place. Most are real translations written to match Greek clause structure by construction. Known quality concerns:

- **Mark 8-16:** English may be script-generated quality rather than hand-verified structural glosses. Needs audit before publication use.
- **Some Acts chapters:** English needs verification.
- Recommendation: run a quality audit pass on English glosses before any publication or external review.

#### Pauline Opportunity Space

Paul's compressed style (ellipsis, anacoluthon, dense argumentation) is where colometric formatting yields the highest marginal benefit. Key findings:

- **Ellipsis detection:** Paul frequently elides verbs in parallel constructions. Colometric formatting makes these implied predications visible through vertical stacking.
- **Compression-as-lucidity thesis:** Paul's most compressed passages become MORE readable (not less) when formatted colometrically, because the visual structure disambiguates what the prose obscures.
- **Marschall comparison on 2 Cor 10:8-11:** 3 specific divergences identified, providing concrete data points for methodological comparison.

#### Cognitive Hierarchy

Established ordering: **chunking > oral > rhetorical**. Colometry first aids comprehension through cognitive chunking, then supports oral performance, then reveals rhetorical structure. This hierarchy governs editorial decisions when criteria conflict.

#### Skousen Intellectual Genealogy

The project's relationship to Royal Skousen's textual criticism methodology has been documented, connecting colometric editing to established traditions in critical text work.

---

### Update — 2026-04-12 (session 9: mechanical-merge workflow as default)

#### Default editorial workflow is now scan-and-apply, not agent-dispatch

Session 9 crystallized the **mechanical-merge pattern** as the default workflow for any error class that can be described structurally. The previous pattern — "dispatch parallel agents to do mass editorial work" — remains available, but should only be used when the error class requires per-verse judgment (e.g., translation quality, semantic alignment cleanup).

**Mechanical-merge pattern:**

1. **Describe the error class structurally** — what grammatical / syntactic signature identifies the problem?
2. **Build a scanner** (`scripts/scan_*.py`) that finds the signature and cites the evidence
3. **Build an apply tool** (`scripts/apply_*.py`) that mirrors the operation on both Greek and English files in lockstep
4. **Pilot on 2-3 books** representing different genres; verify 0 residual
5. **Run corpus-wide** with `--save-candidates` for Greek+English lockstep
6. **Rebuild and confirm integrity** (`build_books.py` runs `verify_word_order.py` automatically)
7. **Commit atomically** with a message that includes the merge count per book

**Session 9 applied this pattern to three error classes:**

- **Vocative apposition** (125 merges) — vocatives appositive to 2p pronouns/verbs in the same clause. Scanner + apply in `scan_vocative_apposition.py` / `apply_vocative_merges.py`.
- **No-anchor lines** (860 merges) — lines lacking a thought-marking anchor (finite verb, infinitive, participle, or head substantive in N/A/D/V). Scanner + apply in `scan_no_anchor_lines.py` / `apply_no_anchor_merges.py`. Pilot: Rom (118 → 0), Mark (62 → 0), Rev (83 → 0). Corpus-wide: 977 flagged → 0 residual after upward merge + downward-merge fallback + 3 manual edge cases.
- **English alignment drift** (47 + 61 in two waves) — heuristic detection via `scan_english_drift.py`. First wave used cleanup via a dispatched agent (the drift class doesn't reduce to a mechanical apply since each case requires rearranging words across a specific boundary). Second wave tightened the scanner to catch participle-NP splits and proper-noun appositive splits.

#### When to use mechanical vs. agent-dispatch

| Use mechanical (scan+apply) when... | Use agent-dispatch when... |
|---|---|
| The error class has a grammatical signature | The error requires per-verse judgment |
| Every merge can cite a specific evidence token | Semantic quality matters more than position |
| The fix is always "merge line N into line N-1" (or similar) | The fix requires reading context and rewriting |
| You can verify success by re-running the scanner | You need a human-like review of the output |

Bridge finite-verb scanning, vocative apposition, no-anchor lines, three-in-one qualifier merging → mechanical.

Translation quality, LLM-generated book cleanup, English drift correction within existing line boundaries, cross-verse atomic-thought detection → agent-dispatch (for now).

#### Cross-verse continuation workflow

**Canonical rule now in `private/01-method/colometry-canon.md` §3.17** (codified 2026-04-22). The editorial procedure summary below is retained for workflow reference; refer to the canon for the authoritative rule + rationale + examples.

When a single atomic thought crosses a Stephanus 1551 verse boundary (e.g., Matt 3:1-2, John 4:35-36), the editorial procedure is:

1. **Identify the boundary:** grammatical continuity indicator — participle chain, suspended main verb, subject/verb straddle, speech-intro straddle, discourse-adverb leading the next clause
2. **Edit in place:** the sense-line lives in the *earlier* verse's block (where its lead word sits), with an inline superscript digit (`²`/`³⁶`/...) marking where the next verse begins visually
3. **Update the corresponding English gloss** with the same merge and the same superscript marker
4. **Rebuild** — the integrity checker recognizes superscripts and splits the merged line at markers for per-verse word-order comparison. HTML renders superscripts as `<sup class="verse-marker">` anchors.
5. **Cite using the earlier verse's ref** when referring to the merged colometric line

This is a low-frequency editorial act (~30-80 cases estimated corpus-wide; 18 applied as of 2026-04-22). Candidates should be identified and applied case-by-case with canon §3.17 as authority; no mechanical scanner for cross-verse continuation exists yet.

#### Drift scanner in the cascade

Every Greek edit cascade now ends with two checks, not one:

1. **`verify_word_order.py`** (automatic, runs inside `build_books.py`) — catches word-order bugs
2. **`scan_english_drift.py --summary-only`** (manual, run after any regen) — catches English alignment drift

Both should return 0 before committing a pass. The drift scanner has three confidence tiers; the cascade check should use `--min-confidence high` to avoid false positives from narrative English conventions.

#### Commit message conventions for mechanical passes

```
<pass name>: <scope> (<count> edits, <residual> residual)

<one-sentence problem statement>

<how the scanner identifies the class>

<per-book counts or per-class breakdown>

<any manual residual noted>

<rebuild / integrity status>

Co-Authored-By: ...
```

See commits fa5725d (vocative), 48df980 (no-anchor pilot), 5847940 (no-anchor corpus-wide) for examples.

---

## Update — 2026-04-14 (five-tier reproducibility arc)

The `data/text-files/` directory now presents the project's text pipeline as a five-tier arc: **v0 (canonical prose) → v1 (pattern-matched) → v2 (Macula syntax-tree-driven) → v3 (rhetorical refinement) → v4 (methodology-applied editorial layer).** Every tier uses the same `{NN-book}/{abbrev}-{NN}.txt` layout, so the same chapter is navigable at the same path across every stage of the pipeline.

**Framing note for v4 specifically.** v4 is not "hand editing" in the sense of manual typing. It is where the project's documented colometric methodology — atomic thought, cognitive hierarchy, register sensitivity, the no-anchor rule, the universal vocative rule, the Goldilocks refinement, the other rules in the canon — is *applied* to the text, through a mix of systematic scan-and-apply tools (the mechanical merge pattern documented elsewhere in this file) and case-by-case editorial decisions where the rule set underdetermines. The editor operates the methodology; the methodology is the contribution. See the 2026-04-14 update block in `handoffs/03-architecture.md` for the longer version of this precision and the two-reproducibility-regimes note that goes with it.

For the editorial workflow specifically this means:

- **The editorial source of truth is still `v4-editorial/`.** Nothing about the workflow has changed. All edits go to `v4-editorial/{NN-book}/{abbrev}-{NN}.txt`, cascade to `eng-gloss/`, then to `books/*.html`. The editorial workflow itself remains as documented elsewhere in this file — the update here is terminological precision, not a behavioral change.
- **The mechanical tiers (v0-v3) are frozen artifacts.** They are the record of how the machine-produced baseline was built. They should not be edited by hand. If a mechanical script is re-run (e.g., `auto_colometry.py` against new `sblgnt-source/` content), it will write to the correct subfolder paths automatically — the scripts were updated in this restructure to use the new layout.
- **For reproducibility work (Phase 2 defensibility and future methodology papers), the v0-v3 tiers are citable.** A skeptical reader can run the mechanical pipeline against the same source data and verify our mechanical output bit-exactly. The v3 → v4 diff is the editorial value-add and is governed by the colometric methodology canon.

Full restructure details are in `handoffs/03-architecture.md` under the 2026-04-14 update block. The top-level `data/text-files/README.md` is the entry point for anyone (including future Claude sessions) trying to understand the pipeline at a glance.
