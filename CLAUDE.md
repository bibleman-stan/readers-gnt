# GNT Reader — Claude Code Instructions

Read this file completely before doing anything in this repo. It is your orientation document for every session.

---

## What This Project Is

A colometric reading edition of the Greek New Testament. The text is reformatted from standard prose paragraphs into **sense-lines (cola)** — each line is a natural breath unit based on Greek grammatical structure, designed for oral delivery and comprehension.

The colometric methodology draws on ancient manuscript precedent (Codex Bezae, Claromontanus, Jerome's Vulgate *per cola et commata*) and the modern precedent of Skousen's sense-line analysis of the Book of Mormon, empirically extended by Stan to the GNT. Foundational premise: humans think, compose, and read in sense-lines. Full canon: `private/01-method/colometry-canon.md`.

- **Repo:** github.com/bibleman-stan/readers-gnt (public)
- **Live site:** gnt-reader.com (GitHub Pages, custom domain, HTTPS enforced)
- **Base text:** SBL Greek New Testament (SBLGNT) — CC-BY-4.0
- **User:** Stan (thebibleman77@gmail.com)
- **Stage:** v4-editorial complete — all 260 chapters hand-edited, structural English glosses for all 260, web app live at gnt-reader.com

---

## Read the Handoff Docs First

Before any substantive work, read the handoffs directory in order:

| File | Covers |
|------|--------|
| `handoffs/00-index.md` | Index and update protocol |
| `handoffs/01-project-overview.md` | Vision, origin, scholarly landscape, research advantages, siloing decision |
| `handoffs/03-architecture.md` | Repo structure, scripts, web app, build pipeline, deployment |
| `handoffs/04-editorial-workflow.md` | How text goes from raw source to finished reading edition |

---

## Session bookend protocol

The overseer apparatus was retired 2026-04-20. Stan is now the sole authority for this project. Session bookends produce artifacts in a per-session folder. Historical record: `private/OVERSEER-DIRECTIONS-retired-2026-04-20.md` (archived, not actively consulted).

### Session folder convention

Each Claude Code session (JSONL boundary) gets its own folder:

`private/03-sessions/yyyy-mm-dd-brief_description/`

Use the **session start date**. A compaction-wake starts a new session; create a new folder with a new descriptor, even if the calendar date is the same as the pre-compaction folder. Multiple folders with the same date + different descriptors is correct and expected.

The folder is the persistent write surface for the session. Session memory evaporates at compaction; the folder survives.

### CHECK-IN (at session start)

**MANDATORY (read every wake, including short "hey wake up" signals):**
1. This CLAUDE.md in full
2. The most recent `private/03-sessions/yyyy-mm-dd-*/session-notes.md` (for carry-forwards and prior-session context)
3. `git log --oneline -10`

**CONSULT-ON-TRIGGER (evaluate the trigger; do NOT silently skip):**
- `private/01-method/colometry-canon.md` — **trigger:** ANY editorial, rule-interpretation, or methodology-touching work. **Skip when:** pure infrastructure / code / UX / deployment work with no canon touching.
- `data/syntax-reference/greek-break-legality.md` — **trigger:** applying or authoring a rule that touches generic Koine break-legality (R2-R7 Layer 1). **Skip when:** purely editorial sense-line decisions within permitted syntax.
- `private/README.md` — **trigger:** writing a new file under `private/` and don't already know the subdirectory layout. **Skip when:** only reading existing files or writing in standard locations.

**Self-report before first substantive response**: one line per mandatory file (e.g., `- CLAUDE.md: read`). A silent skip is a check-in failure.

### During the session

Log as things happen:
- Discipline failures (with common-mode grouping when clusters form)
- Withdrawn or discarded proposals (and why)
- Workflow use-count running tally (agent dispatches, commits, memory changes, cascade runs)

These can be drafted into a running `session-notes.md` throughout the session or assembled at WRAP-UP.

### WRAP-UP (at session end, or when context crosses ~60%)

Produce in the session folder:

1. **`full-transcript.md`** — verbatim dialogue extraction from the session JSONL. Dispatch a Sonnet agent with the JSONL path (`C:/Users/bibleman/.claude/projects/c--Users-bibleman-repos-readers-gnt/<session-id>.jsonl`) to stream-process and write the transcript. Format: numbered turns alternating Stan/Claude, strip tool_use and tool_result, strip `<system-reminder>` blocks.
2. **`session-notes.md`** — session arc, what landed (commits), discipline observations with common-mode grouping, withdrawn proposals, workflow use-count, carry-forwards for next session.
3. **`dialogue-notes.md`** — produce only for methodology-heavy sessions where the DIALOGUE arc itself is the work (vs. executing a pre-specified task). Captures the reasoning path that led to a decision, not just the decision.
4. **`review-lists/`** (subfolder) — only when the session produced candidate lists requiring Stan review (e.g., N sweep candidates from a validator run). One markdown file per list with decision checkboxes.

### Canon self-consistency audit trigger

**After any session with ≥2 new canon codifications (new subsections or rule revisions), run a canon self-consistency audit before WRAP-UP.** Not a time-based cadence — a content-trigger.

**What the audit checks:**
1. Do the new additions contradict existing canon sections? (grep for overlapping keywords; spot-read affected §§)
2. Do the new additions satisfy the §6 defensibility capture (WHY / HOW WE KNOW / SCOPE)?
3. Are there adjacent rules that should reference the new additions? (e.g., a new §3.7 subsection might warrant a cross-reference in M1 or R11)
4. Does the handoffs documentation still match the canon? (if a rule migrated from handoffs to canon, the handoff version should either update or deprecate)

**Light-touch**: this is a ~5-minute pass, not a full re-read. A single grep for the new subsection's key terms + spot-reads is usually sufficient. Flag contradictions or stale cross-references in the session-notes carry-forwards.

### Context-threshold discipline

- **Green zone (0-60%)**: execute normally.
- **Yellow zone (60-80%)**: start drafting `session-notes.md` in the background; consider wrapping at natural breakpoints.
- **Red zone (80%+)**: stop new execution, wrap up.

Compaction-resume: still run the full CHECK-IN protocol when resuming from a compaction summary. Short-form "hey wake up" still requires the 3 mandatory reads.

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Main web app — all CSS/JS inline (~2,500 lines), search, corpus filters, settings |
| `scripts/build_books.py` | Converts text files → HTML fragments (reads v4-editorial + eng-gloss) |
| `scripts/auto_colometry.py` | Rule-based sense-line formatter (~620 lines) — generates initial drafts only |
| `scripts/generate_english_glosses.py` | Generates structural English glosses |
| `scripts/regenerate_english.py` | Regenerates English glosses after Greek edits |
| `data/text-files/sblgnt-source/` | 27 raw SBLGNT source files — **NEVER EDIT** |
| `data/text-files/v4-editorial/*/` | 260 chapter files in book subfolders — **single source of truth for Greek text** |
| `data/text-files/eng-gloss/*/` | 260 chapter files in book subfolders — structural English glosses |
| `books/` | 27 generated HTML fragment files (rebuilt from v4-editorial + eng-gloss) |

---

## CRITICAL: Source Text Rules

The SBLGNT source files in `data/text-files/sblgnt-source/` are canonical reference.

**NEVER:**
- Modify a canonical SBLGNT source file
- Alter the Greek text itself (words, accents, breathing marks)
- Add or remove words
- Run auto_colometry.py without checking if hand-edited chapters will be overwritten

**ALWAYS:**
- Work in `v4-editorial/` — the only editorial tool is where lines break
- Present proposed changes for review before finalizing
- Preserve verse references for alignment with standard editions
- Use `PYTHONIOENCODING=utf-8` when running Python scripts on Windows

---

## Rule-Derivative vs. Ad-Hoc Changes

Line-break changes come in two classes that require different gating.

**Rule-derivative changes**: a line-break change that applies a codified MECHANICAL rule from the canon unambiguously. Example: R2 forbids line-final conjunction, a line ends on καί, the fix is a forced merge. **These do NOT require per-item Stan approval** — the canon's rule is the approval. Apply mechanically and report in the session's rollup summary.

**Ad-hoc changes**: a line-break change that is not directly licensed by a codified rule, or that applies an EDITORIAL/FUZZY rule (Category B), or that touches an exegetical hot spot (Category C). **These DO require Stan approval** before application — present the proposed change with its rationale and wait for explicit greenlight.

The distinction is important: gating rule-derivative changes on per-item approval treats the rule as advisory when it is mechanical, wastes context budget, and pushes the editor into a review queue rather than applying the validator's work queue. The canon's mechanical-rule-authority clause (§3 Autonomy Boundary) is the authoritative statement of this distinction.

**Corollary**: when a validator produces bulk output (e.g., "73 STRONG-MERGE-CANDIDATEs from Rule 27 sweep"), the correct move is to apply all of them as rule-derivative, report the rollup, and commit. Walking Stan through 73 verse-level confirmations is exactly the failure this corollary exists to prevent.

---

## Build Pipeline

The cascade rule: **Greek edit → English regen → HTML rebuild**.

After editing a Greek chapter in `v4-editorial/`:
1. Regenerate the English gloss for that chapter
2. Rebuild the HTML

```bash
# Regenerate English for one book
PYTHONIOENCODING=utf-8 py -3 scripts/regenerate_english.py --book mark

# Rebuild all HTML
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py

# Rebuild one book's HTML
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py --book mark
```

Pipeline: `v4-editorial/*/ → eng-gloss/*/ → books/*.html`

---

## Colometric Principles (Orientation Only)

**Authoritative canon:** `private/01-method/colometry-canon.md`. Fresh-read that file before any editorial or rule work — rules evolve fast and this summary drifts. The bullets below are orientation-at-load-time only, not rule reference.

### Four Criteria (hierarchy)
1. **Atomic Thought** (governs by default)
2. **Single Image**
3. **Breath Unit**
4. **Source-Language Syntax**

Collisions resolved via the "default + unless" mechanism (2026-04-16 reframe): criterion 1 wins by default; the four recognized structural justifications ("unless" cases) can override it when both cognitive and structural prongs are satisfied. See canon §1 for the current statement.

### Representative break points (non-exhaustive — canon is authoritative)
- Subordinate clauses introduced by ἵνα, ὥστε, ὅτι, ὅταν
- μέν/δέ antithetical stacks
- Genitive absolutes (always own line)
- Vocatives (universal rule — each is an atomic address act)

Full break-point and merge-override inventory (R1–R28 with six numbers retired 2026-04-18 — see §9 of canon, M1–M4, the 11 governor classes for parallelism-consistency, and all worked examples) lives in `private/01-method/colometry-canon.md`. Do not rely on CLAUDE.md for rule lookups.

---

## Agent Dispatch — Three-Tier Model Routing

When dispatching subagents via the Agent tool, match model to task complexity. Don't default everything to Opus — Stan pays per-token and routing matters.

- **Haiku** (cheapest, fastest): file moves, renames, glob/ls formatting, mechanical reference lookups, single-file reads-and-summarize with no judgment, yes/no checks against file content.
- **Sonnet** (mid-tier): scanner runs where rules are already defined, quick consistency checks with narrow scope, documentation updates following a clear template, short adversarial checks on a single specific question, cross-project consistency checks once both sides are stable, mirroring edits between files.
- **Opus** (reasoning-heavy): multi-angle adversarial audits requiring deep reasoning, methodology synthesis across multiple sources, restructuring major documents, novel rule design or hierarchy reframes, anything where the judgment IS the work product.

**When in doubt, Sonnet is the right default.** It handles most scoped tasks capably at a fraction of Opus cost. Reserve Opus for tasks where the reasoning quality directly determines the output's value. Stan should not have to think about this — the dispatching Claude makes the call.

---

## What Stan Does / What Claude Does

**Stan:**
- Makes all final editorial decisions on line breaks
- Reviews all proposed changes
- Pushes to GitHub
- Has final say on all colometric decisions
- Decides which books/chapters to work on next

**Claude Code:**
- Proposes line-break revisions with rationale
- Builds and maintains tooling (scripts, build pipeline, web app)
- Maintains documentation and handoffs
- Quantitative analysis (colon counts, pattern detection)
- Never touches source text without explicit approval
- Commits when finished; Stan pushes

---

## Connected Resources

- **Academic vault:** `C:\vaults-nano\my_brain\` — Greek grammar notes, Bible book files, scholar notes
- **Gospel vault:** `C:\vaults-nano\gospel\` — devotional scripture notes
- **Key scholarly references:**
  - Lee & Scott, *Sound Mapping the New Testament* (2009, 2nd ed.)
  - Priscille Marschall, *Colometric Analysis of Paul's Letters* (2024, WUNT II)
  - Runge, *Discourse Grammar of the Greek New Testament* (2010)
  - Levinsohn, *Discourse Features of New Testament Greek* (2000)
- **Domain registrar:** Cloudflare (same account as other domains)

---

## Git Workflow

- All work on `main` branch
- Stan pushes from his local machine via GitHub Desktop
- Claude Code prepares commits but cannot push (403 proxy error)
- Stan's standing instruction: "whenever you finish, do a commit and I'll push"

---

## Project Siloing

This project is **publicly independent** — no cross-references to any other projects in README, CLAUDE.md, handoffs, or any public-facing files. Respect this decision.

---

## Update Protocol

When updating handoff docs, append a dated block at the bottom — never overwrite history. After any session where decisions are made, principles are refined, or new patterns identified, update the relevant handoff file.
