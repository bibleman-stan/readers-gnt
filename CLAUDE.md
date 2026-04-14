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

## Session bookend protocol (standing rule — CHECK-IN + WRAP-UP)

**Sessions have two mandatory bookends: a check-in at the start, a report at the end.** The overseer (cross-project Claude) cannot see your conversation — it only sees files you leave behind. The bookends are how the overseer stays oriented across sessions without having to guess or have Stan paste everything manually.

### CHECK-IN — at session start

When Stan signals start-of-session with phrases like **"hey, let's start a new session," "new session," "fresh start," "let's begin," "let's kick off,"** or any similar opening language — before you do any substantive work, read these files in this order:

1. **This CLAUDE.md file in full** — you may already be doing this on orientation, but confirm it.
2. **`private/OVERSEER-DIRECTIONS.md`** — active cross-project directives, sync log, documentation protocol. This is your primary coordination surface with the overseer.
3. **`private/README.md`** — subdirectory layout of `private/` so you know where to find things and where to write new files.
4. **`c:/Users/bibleman/repos/overseer-workspace/LANDSCAPE-MAP.md`** — one-glance snapshot of where the whole program is right now. Tells you what's hot, what's resolved, what's open. **Read this every session — it's the overseer's dip-in file and it's kept fresh.**
5. **`c:/Users/bibleman/repos/overseer-workspace/METHODOLOGY-TIMELINE.md`** — dated log of methodology state changes on both projects. Check this if you're going to touch any scan/audit/findings files from prior sessions — the timeline tells you what methodology state they reflect.
6. **`c:/Users/bibleman/repos/overseer-workspace/OPEN-QUESTIONS.md`** — unresolved threads that might intersect with whatever Stan is asking for. Skim for relevance.
7. **`private/handoffs/02-colometry-method.md`** — the methodology canon. Always fresh-read before any editorial or rule work. Rules evolve fast.
8. **`git log --oneline -10`** — see what's committed since the last session. Any commit you don't recognize is a state change you should understand before working.

**After reading:** send Stan a brief check-in message confirming orientation. Something like: "Checked in. Current state: [one-sentence summary]. Top 2-3 hot threads per LANDSCAPE-MAP: [...]. Anything specific you want me to focus on, or should I continue the queued work?" Keep this to 4-5 lines. The goal is to prove you read the files, not to summarize them exhaustively.

**Why this matters:** sessions that skip the check-in tend to propose things contradicting recent state, re-argue decisions already made, miss open questions that affect the current task, and waste Stan's time on corrections the overseer already wrote down. The overseer workspace and the OVERSEER-DIRECTIONS file are the cumulative state — reading them puts you in the same frame the overseer operates from.

### WRAP-UP REPORT — at session end

When Stan signals end-of-session with phrases like **"let's wrap it up for now," "wrap it up," "let's stop here," "that's enough for today," "commit and wrap,"** or any similar winding-down language — do these things BEFORE you commit or stop, in this order:

1. **Write dialogue-notes if a substantive methodology dialogue happened.** If the session produced a methodology correction, rule refinement, theoretical framing, enthusiastic adoption walked back, or pushback Stan thinks is dangerous → write `private/sessions/[YYYY-MM-DD]-[topic-slug]/dialogue-notes.md` capturing:
   - What you initially proposed
   - Stan's pushback or refinement
   - The reasoning chain (not just the outcome — the *why* matters more than the *what*)
   - What was ultimately decided
   - Any load-bearing phrases Stan used verbatim — they may become prospectus language and need to be preserved exactly

2. **Update `private/OVERSEER-DIRECTIONS.md`** per its documentation protocol:
   - Transform any applied items from "Status: active" to "APPLIED [date] — commit [hash]" with a brief resolution note
   - Add any new findings to the "push FROM HERE" section for cross-project porting
   - Append a dated sync-log entry at the bottom summarizing: commit hashes, files touched, items closed, new items opened, anything surprising

3. **Send Stan a wrap-up report message** before committing. Something like: "Session wrap-up. Commits landing: [hashes]. Files touched: [list]. Items closed: [list]. New items opened: [list]. Dialogue notes written at [path] covering [topic]. Anything unsurprising elsewhere that the overseer should also know?" 4-8 lines. The goal is to give the overseer a one-message summary that captures everything important without requiring it to read the full diff.

4. **Then commit and stop.**

**Why this matters:** Stan's standing complaint about trench Claudes is that they forget to document, hit compaction, and lose progress. The wrap-up report is the single most important thing you do in a session — it's the handoff to the next session (same Claude or different Claude, doesn't matter). If you only have time for one thing at end-of-session, it's the wrap-up report. Commits can wait five minutes; a compacted context cannot be recovered.

### CONTEXT-AWARE SELF-DISCIPLINE — watch your own context usage

Compaction is your equivalent of Stan saying "wrap it up" — but unlike Stan's verbal signal, compaction is gradual and doesn't announce itself. The cost of hitting compaction mid-operation is real: aggregation steps get lost, reasoning chains get truncated, in-flight batch state evaporates. **Don't let it get down to "oh crap we just lost something beautiful."**

Apply these three thresholds to your own context meter and treat them as standing rules, not suggestions:

**At ~50% context remaining — informal checkpoint.** Don't stop working, but do these things cheaply:
- Save any in-flight batch state to a file (scanner output partial results, audit aggregations, anything you'd lose if compacted)
- Commit any WIP code changes even if the work isn't complete — commits are cheap insurance, working memory is not
- Add a dated entry to `private/OVERSEER-DIRECTIONS.md` sync log capturing "session so far" in one paragraph. If compaction happens unexpectedly after 50%, you've got a recoverable mid-session checkpoint.

**At ~40% context remaining — defensive wrap-up, proactively.** This matches the overseer's own threshold. Treat the 40% mark as equivalent to Stan saying "let's wrap it up for now," even if he hasn't said it. Execute the full WRAP-UP REPORT protocol above (dialogue-notes if applicable, OVERSEER-DIRECTIONS update, wrap-up message, commits). Don't start new major operations after this point — only finish what's already in progress. **Tell Stan you've hit 40% and are wrapping up** so he can decide whether to continue in a fresh session or stop for the night.

**At ~30% context remaining — hard stop.** If you're still working past 30%, you've already taken on too much risk. At this threshold: finish ONLY the wrap-up. Don't continue substantive work. Don't start any new operation even if it seems small. The runway between 30% and auto-compact is your margin for error — preserve it. Every minute past 30% is a minute closer to losing the wrap-up itself.

**Why these thresholds are conservative for trench Claudes:** execution work (corpus-wide scans, adversarial audits, merge applications, file reorganizations, stylometry runs) has more in-flight state than pure synthesis. A single compaction during an aggregation step can lose hours of work if the intermediate results only exist in working memory. The cost of triggering a checkpoint too early is low (you write some files and continue); the cost of triggering too late is "oh crap we just lost something beautiful" — Stan's phrasing, and the thing these thresholds are designed to prevent.

**When in doubt, write it down.** Files survive compaction; working memory does not. This is the same discipline the overseer applies to itself.

### Why BOTH bookends + context discipline matter

Check-in without wrap-up = you start oriented but leave nothing for the next session.
Wrap-up without check-in = you document cleanly but start from "what Stan just said" instead of "the full accumulated state."
Bookends without context discipline = you're great at planned wrap-ups but lose sessions when compaction sneaks up.
**All three together = the overseer has full and robust visibility, and compaction never costs you beautiful work.** Stan gets to work at the speed of direction-giving, not the speed of context-watching-and-rescue.

See `private/OVERSEER-DIRECTIONS.md` documentation protocol for additional details, including what counts as a "substantive methodology dialogue" worth capturing.

---

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

## Colometric Principles (Summary)

The full methodology reference is pointed to from `private/OVERSEER-DIRECTIONS.md` (local only). Key points:

### Four Criteria
1. **Atomic Thought:** each line = one complete thought unit
2. **Single Image:** each line paints one image
3. **Breath Unit:** each line = one natural breath for oral delivery
4. **Source-Language Syntax:** grammar reveals structure — breaks are descriptive, not interpretive

### Greek Break Points
- Subordinate clauses: ἵνα, ὥστε, ὅτι, ὅταν, ὅτε, ἐάν, μήποτε
- Discourse markers: ἀλλά, δέ (with contrast), γάρ
- Speech introductions: ἔλεγεν αὐτοῖς· gets its own line
- Parallel structures: stack vertically
- μέν/δέ contrasts: stack as parallel lines
- Participial phrases / genitive absolutes: frame their own line

### Rules
- Never dangle conjunctions at line end
- Never split verb from direct object on short phrases
- All vocatives get their own line (universal rule — each is an atomic address act)
- Line length is a signal, not a rule

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
