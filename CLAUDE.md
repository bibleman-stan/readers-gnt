# GNT Reader — Claude Code Instructions

Read this file completely before doing anything in this repo. It is your orientation document for every session.

---

## What This Project Is

A colometric reading edition of the Greek New Testament. The text is reformatted from standard prose paragraphs into **sense-lines (cola)** — each line is a natural breath unit based on Greek grammatical structure, designed for oral delivery and comprehension.

The colometric methodology draws on the scholarly tradition of Lee & Scott (sound mapping), Marschall (colometric analysis of Paul), and ancient manuscript practice.

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

Also check `private/OVERSEER-DIRECTIONS.md` if present — local-only session directives (gitignored, Dropbox-backed). It carries active directives, the pointer to the full methodology canon, and a sync log. **Read it before starting substantive work, and update it before ending the session or committing — whichever comes first.** It contains its own documentation protocol; follow it. Session memory evaporates at compaction but that file survives, so treat it as the persistent write surface for anything the overseer needs to know about your session.

---

## Session bookend protocol

Canonical shared source: [`overseer-workspace/SESSION-BOOKEND-PROTOCOL.md`](../overseer-workspace/SESSION-BOOKEND-PROTOCOL.md) — CHECK-IN, WRAP-UP, context thresholds, and compaction-resume protocol. **Read it at the start of every session.**

### GNT-specific CHECK-IN file list (structured as mandatory + consult-on-trigger per shared protocol)

**MANDATORY (read every wake — including short "hey wake up" signals):**
1. This CLAUDE.md in full
2. `private/OVERSEER-DIRECTIONS.md` active-directives section (NOT the archive)
3. `c:/Users/bibleman/repos/overseer-workspace/LANDSCAPE-MAP.md`
4. `C:\vaults-nano\my_brain\00_Inbox\claude-brainstorming.md` — scope per shared protocol (GNT items only)
5. `git log --oneline -10`

**CONSULT-ON-TRIGGER (evaluate the trigger; do NOT silently skip):**
- `c:/Users/bibleman/repos/overseer-workspace/METHODOLOGY-TIMELINE.md` — **trigger:** task touches scan outputs, canon entries, or methodology artifacts from a prior session that you need to verify. **Skip when:** pure new work with no prior-session artifact dependencies.
- `c:/Users/bibleman/repos/overseer-workspace/OPEN-QUESTIONS.md` — **trigger:** Stan's request bears on a named open question OR you're about to propose something that might overlap an unresolved thread. **Skip when:** request is clearly scoped with no open-question overlap.
- `private/01-method/colometry-canon.md` — **trigger:** ANY editorial decision, rule interpretation, or methodology-touching work. **Skip when:** pure infrastructure / code / UX / deployment work with no canon touching.
- `private/README.md` — **trigger:** writing a new file under `private/` and don't already know the subdirectory layout. **Skip when:** only reading existing files or writing in standard locations.

**Self-report is mandatory before your first substantive response** — see the shared protocol's SELF-REPORT section for the one-line-per-file format. A silent skip is a check-in failure.

### GNT-specific WRAP-UP additions (in addition to the shared protocol's generic wrap-up)

Session notes go to `private/03-sessions/[YYYY-MM-DD]-[topic-slug]/session-notes.md` (or `dialogue-notes.md` for methodology dialogues). The "What the notes should contain" bullet list from the shared protocol applies in full — especially the three additions landed 2026-04-18 (self-log of discipline failures with common-mode grouping, withdrawn-proposal logging, workflow use-count).

### Context-threshold and compaction-resume — see shared protocol

Threshold discipline and compaction-resume rules live in the shared protocol (revised 2026-04-19 so execution-heavy work isn't interrupted at 40% — see the shared file for details).

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

Full break-point and merge-override inventory (R1–R29, M1–M4, the 11 governor classes for parallelism-consistency, and all worked examples) lives in `private/01-method/colometry-canon.md`. Do not rely on CLAUDE.md for rule lookups.

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
