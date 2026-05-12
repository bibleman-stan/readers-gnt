# GNT Reader — Claude Code Instructions

Read this file completely before doing anything in this repo. It is your orientation document.

---

## What This Project Is

A colometric reading edition of the Greek New Testament. The text is reformatted from standard prose paragraphs into **atomic thought units (ATUs)** (cola) — each line is one ATU reflecting Greek grammatical structure, designed for oral delivery and comprehension.

The colometric methodology draws on ancient manuscript precedent (Codex Bezae, Claromontanus, Jerome's Vulgate *per cola et commata*) and the modern precedent of Skousen's "sense-line" analysis of the Book of Mormon, empirically extended by Stan to the GNT. Foundational premise: humans think, compose, and read in ATUs. Full canon: `private/01-method/colometry-canon.md`.

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

## Wake & standing issues

Work is continuous. There are no sessions — only the standing set of pending decisions, blocked items, and in-flight actions. Orient toward that set, not toward wrapping arbitrary time-slices.

**On wake (compaction-resume or new conversation):**
1. Re-read the prior conversation JSONL at `C:/Users/bibleman/.claude/projects/c--Users-bibleman-repos-readers-gnt/<session-id>.jsonl` to re-acquire context — grep for the most recent activity, decisions, and unresolved items. The JSONL is the verbatim record of everything that's been said; treat it as your durable memory.
2. `git log --oneline -10` for current code state.
3. Self-report both reads in one line each before the first substantive response.

**Consult on trigger (evaluate the trigger; do NOT silently skip):**
- `private/01-method/colometry-canon.md` — ANY editorial / rule-interpretation / methodology-touching work.
- `data/syntax-reference/greek-break-legality.md` — touching R2-R7 Layer 1 break-legality.
- `../atu-method/docs/apparatus.md` + `../atu-method/docs/architecture.md` — English-layer / swap-system / cross-sibling architectural work; pull back to the picture when ambiguity surfaces.
- `private/README.md` — writing a new file under `private/` and don't already know the layout.

**Surface standing issues** in the conversation when you find them — pending decisions, blocked items, things Stan needs to direct. Don't let items drift silently; the JSONL captures everything but visibility happens in the live conversation.

### Canon self-consistency audit trigger

After any commit batch with ≥2 new canon codifications (new subsections or rule revisions), run a canon self-consistency audit before the commit lands. Content-triggered, not time-triggered.

The audit checks: do new additions contradict existing canon sections (grep for overlapping keywords + spot-read affected §§); do they satisfy §6 defensibility capture (WHY / HOW WE KNOW / SCOPE); are there adjacent rules that should cross-reference the new additions; does the handoffs documentation still match the canon. Light-touch — ~5-minute pass, not a full re-read.

---

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Main web app — all CSS/JS inline (~2,500 lines), search, corpus filters, settings |
| `scripts/build_books.py` | Converts v4-editorial + eng-gloss → HTML fragments under `books/` |
| `scripts/regenerate_english.py` | Thin wrapper over `atu_method.kjv_alignment.align_verse()`; redistributes KJV verbatim per Greek ATU line via Strong's-number matching against TAGNT |
| `scripts/v4_auto_fix.py` | Mechanical fixes against v4-editorial (read/write in place) |
| `validators/_shared/morphgnt_lookup.py` | MorphGNT morphological backend (used by `validators/common.py`) |
| `validators/_shared/macula_clauses.py` | Macula syntax-tree clause-boundary extractor (used by `validators/common.py`) |
| `scripts/archive/` | Tier-producer scripts (v0–v3) frozen 2026-04-26; see `scripts/archive/README.md` |
| `data/text-files/sblgnt-source/` | 27 raw SBLGNT source files — **NEVER EDIT** |
| `data/text-files/v4-editorial/*/` | 260 chapter files in book subfolders — **single source of truth for Greek text** |
| `data/text-files/eng-gloss/*/` | 260 chapter files in book subfolders — KJV verbatim per Greek ATU line (produced by `regenerate_english.py`) |
| `books/` | 27 generated HTML fragment files (rebuilt from v4-editorial + eng-gloss) |

---

## CRITICAL: Source Text Rules

The SBLGNT source files in `data/text-files/sblgnt-source/` are canonical reference.

**NEVER:**
- Modify a canonical SBLGNT source file
- Alter the Greek text itself (words, accents, breathing marks)
- Add or remove words
- Run any `scripts/archive/` tier-producer script (v0–v3) — they write to frozen scaffolding directories and almost never produce a desired outcome on a hand-edited corpus

**ALWAYS:**
- Work in `v4-editorial/` — the only editorial tool is where lines break
- Present proposed changes for review before finalizing
- Preserve verse references for alignment with standard editions
- Use `PYTHONIOENCODING=utf-8` when running Python scripts on Windows

---

## Rule-Derivative vs. Ad-Hoc Changes

Line-break changes come in two classes that require different gating.

**Rule-derivative changes**: a line-break change that applies a codified MECHANICAL rule from the canon unambiguously. Example: R2 forbids line-final conjunction, a line ends on καί, the fix is a forced merge. **These do NOT require per-item Stan approval** — the canon's rule is the approval. Apply mechanically and report in the commit's rollup summary.

**Ad-hoc changes**: a line-break change that is not directly licensed by a codified rule, or that applies an EDITORIAL/FUZZY rule (Category B), or that touches an exegetical hot spot (Category C). **These DO require Stan approval** before application — present the proposed change with its rationale and wait for explicit greenlight.

The distinction is important: gating rule-derivative changes on per-item approval treats the rule as advisory when it is mechanical, wastes context budget, and pushes the editor into a review queue rather than applying the validator's work queue. The canon's mechanical-rule-authority clause (§3 Autonomy Boundary) is the authoritative statement of this distinction.

**Corollary**: when a validator produces bulk output (e.g., "73 STRONG-MERGE-CANDIDATEs from Rule 27 sweep"), the correct move is to apply all of them as rule-derivative, report the rollup, and commit. Walking Stan through 73 verse-level confirmations is exactly the failure this corollary exists to prevent.

---

## Pre-commit adversarial-audit discipline

**Before any commit that modifies `private/01-method/colometry-canon.md`, check whether the change matches a mandatory-audit trigger per canon §6.5.** The 12 triggers are listed in canon §6.5; re-read them when uncertain. If the change matches any trigger, audit evidence (hostile-agent dispatch + verdict + application) must be present in the commit message or the canon §10 Update Log entry.

**Audit-skippable.** Canon edits that do NOT match any trigger (typo fixes, cross-reference updates without precedence claims, deletions of same-batch reverts, defensibility-capture additions to already-settled rules without scope changes, Category A mechanical corpus edits that are not part of a ≥5-instance sweep) proceed without audit.

**When uncertain.** Dispatch the audit. The cost of a false-positive audit (Stan reads a no-op audit result) is small; the cost of a false-negative audit (a fake rule commits) is large.

**Required commit-message declaration.** Every commit message that touches `private/01-method/colometry-canon.md` must declare audit-status explicitly: either `Audit-skippable per §6.5 ([reason])` with the reason citing one of the named audit-skippable categories above, OR `Audit dispatched: [evidence]` with concrete reference (parallel-agent verdicts, §10 entry, prior-commit pointer). Omission is itself a discipline failure — visible at a glance in `git log`. As of 2026-04-26 this is also **mechanically gated** by the commit-msg hook (see "Validator hooks" below).

**Validator hooks (installed 2026-04-26, ported from sibling Tanakh project):**

- **`validators/hooks/pre-commit`** — runs `validators/run_all.py --baseline-check` when canon, syntax-reference, v4-editorial corpus, or validators are staged. Blocks commit if any rule's candidate count INCREASED vs `validators/.baseline.json`. Update the baseline after intentional changes: `PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --update-baseline`.
- **`validators/hooks/commit-msg`** — runs `validators/check_canon_extensions.py` against the proposed commit message. Detects canon extensions matching §6.5 trigger patterns (new rule subsections, merge-overrides, Layer 1 table rows, audit triggers, SCOPE bullets) and blocks the commit if no audit-evidence keyword OR skip-safe claim is present in the message.
- **Bypass (Stan-only, explicit decision)**: `git commit --no-verify`.
- **Install (one-time)**: `cp validators/hooks/pre-commit .git/hooks/pre-commit && cp validators/hooks/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/pre-commit .git/hooks/commit-msg` (already done in this clone; the source-of-truth scripts live in `validators/hooks/` and are tracked in git; the installed copies in `.git/hooks/` are not tracked).

**Self-test to run pre-commit** (faster than full trigger-list scan):
- Does this change include a scope claim, a precedence claim, a closed-list extension, or a named-category carve-out? → audit.
- Does this change rest on spot-check evidence rather than a full-corpus classification? → audit.
- Does this change reclassify or delete previously-settled canon content? → audit.
- If no to all three → probably skip-safe.

**Parallelize audits by default.** When triggered, dispatch multiple audit dimensions in parallel (one assistant message, multiple Agent tool calls). Sequential only when audit A's verdict determines whether audit B should run. Same-trigger audits across distinct angles (discipline / scope / cross-project consistency / corpus impact) should fire in one batch, not in series. Memory `feedback_adversarial.md` and `feedback_parallelize.md` capture the operational discipline.

This discipline complements (does NOT replace) the **Canon self-consistency audit trigger** above. Pre-commit is per-change; self-consistency is batch-rollup (fires when ≥2 codifications accumulate). See canon §3 "Scope/precedence/closed-list/carve-out diagnostic" for the Category-B-by-default rule this self-test instantiates, and canon §6.5 for the full trigger list.

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

The script is a thin wrapper over `atu_method.kjv_alignment.align_verse()`; the alignment algorithm lives in `../atu-method`, not here. The English layer is KJV verbatim distributed per Greek ATU line via Strong's-number matching (TAGNT → MetaV).

**The cascade is ONE atomic operation.** Greek edit → English regen → HTML rebuild → commit → push. If you change Greek without syncing English and rebuilding HTML in the same work unit, you have failed.

**Two-check verification before any cascade commit:**
- `py -3 scripts/verify_word_order.py` — integrity (every Greek word present in expected verse per SBLGNT)
- `py -3 scripts/scan_english_drift.py --min-confidence high` — English-quality drift detector

Both should return 0 before committing. If high-confidence drift hits are confirmed false positives (gen abs detector cases, known carve-outs), document the rationale in the commit message and proceed.

---

## Colometric Principles (Orientation Only)

**Authoritative canon:** `private/01-method/colometry-canon.md` (GNT-specific rule body); universal framework at `../atu-method/docs/framework.md` (§0 Mission, §1 Three Forces + 5 Structural Justifications + 4 Merge-Overrides, §2 Categories A/B/C, §7 Change Protocol). Fresh-read both before any editorial or rule work — rules evolve fast and this summary drifts. The bullets below are orientation-at-load-time only, not rule reference.

### Three forces (canon §1)
1. **Generative — Propositions.** Default SPLIT at every proposition boundary; each proposition is an atomic thought.
2. **Subtractive — Syntax.** Vetoes any break that would violate Koine break-legality (Layer 1) or complement/formula integrity. Syntax is the floor; no line may sit below it.
3. **Diagnostic — Single image.** Sharpens ambiguous cases: a line carrying multiple distinct images forces a split.

The generative force proposes; the subtractive force vetoes; the diagnostic force adjudicates within the legal-break space. The mission is sense-driven; the method is syntax-constrained.

### Representative break points (non-exhaustive — canon is authoritative)
- Subordinate clauses introduced by ἵνα, ὥστε, ὅτι, ὅταν
- μέν/δέ antithetical stacks
- Genitive absolutes (always own line)
- Vocatives (universal rule — each is an atomic address act)

Full inventory — five structural justifications (§2), four merge-overrides (M1–M4), R-rules (R1–R28 with retirements logged in §9), the 11 governor classes for parallelism-consistency, and all worked examples — lives in `private/01-method/colometry-canon.md`. Do not rely on CLAUDE.md for rule lookups.

---

## Agent Dispatch — Three-Tier Model Routing

When dispatching subagents via the Agent tool, match model to task complexity. Don't default everything to Opus — Stan pays per-token and routing matters.

- **Haiku** (cheapest, fastest): file moves, renames, glob/ls formatting, mechanical reference lookups, single-file reads-and-summarize with no judgment, yes/no checks against file content.
- **Sonnet** (mid-tier): scanner runs where rules are already defined, quick consistency checks with narrow scope, documentation updates following a clear template, short adversarial checks on a single specific question, cross-project consistency checks once both sides are stable, mirroring edits between files.
- **Opus** (reasoning-heavy): multi-angle adversarial audits requiring deep reasoning, methodology synthesis across multiple sources, restructuring major documents, novel rule design or hierarchy reframes, anything where the judgment IS the work product.

**When in doubt, Sonnet is the right default.** It handles most scoped tasks capably at a fraction of Opus cost. Reserve Opus for tasks where the reasoning quality directly determines the output's value. Stan should not have to think about this — the dispatching Claude makes the call.

### Right-size the tool: scripts → bash → agents

Before dispatching ANY agent, ask: *is this script-fixable?* Scripts run in milliseconds at zero token cost; agents take 60–300 seconds and consume context. If the pattern is deterministic (character/word replacement, regex match, structural edit that scales by line-count or fixed marker), write the Python or run a one-shot Bash command. Dispatch agents only when the task requires Greek-grammar interpretation, per-verse judgment, or editorial discretion the script can't encode.

**Diagnostic:** if the agent prompt is "for each item, do X" and X is deterministic, you wanted a script. If X is "decide whether to do the thing," dispatch.

### Parallelize by default

If parallelism is possible, dispatch immediately — never ask "serial or parallel?" The bar is "is there a genuine data dependency preventing parallelism?" not "would Stan prefer it?" Only serialize when output of A must inform the design of B.

**Corpus-wide split by genre group** (for XML parsing, MorphGNT lookup, rule-consistency audit, mass review): Mark / Matt / Luke-Acts / John (+Johannine epistles) / Pauline corpus / Hebrews / General Epistles / Revelation. Eight agents in parallel beats one agent on 27 books every time. **Threshold: any batch of ≥25 surgical fixes spanning 3+ genre groups MUST split by genre group.**

**Two-phase pipeline for code changes:** Phase 1 = one agent for the code change (single file). Phase 2 = N agents for the corpus rebuild (split by genre group). Never combine — every violation has caused a bottleneck.

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
- Commits when finished and pushes autonomously (see Git Workflow exceptions)

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

All work on `main`. After any clean commit, run `git push origin main` immediately — no "want me to push?" hedge. Stan authorized blanket autonomous push 2026-05-11 (SSH transport via `bibleman-windows-desktop` key, silent, no prompts). The prior "Stan reviews in GitHub Desktop before push" gate was replaced by branch-policy + commit-message discipline.

**Exceptions** — still warrant Stan's confirmation BEFORE push:
- Force-pushes (`--force`, `--force-with-lease`)
- Any branch other than `main`
- Commits containing agent-applied bulk corpus changes I haven't personally diff-reviewed (R1-sweep / canon-restructure / mass-edit class)

---

## Project Siloing

This project is **publicly independent** — no cross-references to any other projects in README, CLAUDE.md, handoffs, or any public-facing files. Respect this decision.

---

## Update Protocol

When updating handoff docs, append a dated block at the bottom — never overwrite history. After any work where decisions are made, principles are refined, or new patterns identified, update the relevant handoff file.

