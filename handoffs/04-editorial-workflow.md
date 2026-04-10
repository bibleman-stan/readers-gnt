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
