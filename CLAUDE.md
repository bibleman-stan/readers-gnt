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

Also check `private/OVERSEER-DIRECTIONS.md` if present — local-only session directives (gitignored). It carries active directives and a sync log; read it before starting substantive work.

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
