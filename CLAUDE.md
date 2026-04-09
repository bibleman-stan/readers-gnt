# NT Reader — Claude Code Instructions

Read this file completely before doing anything in this repo. It is your orientation document for every session.

---

## What This Project Is

A colometric reading edition of the Greek New Testament. The text is reformatted from standard prose paragraphs into **sense-lines (cola)** — each line is a natural breath unit based on Greek grammatical structure, designed for oral delivery and comprehension.

This is a sister project to the **BOM Reader** (`C:\Users\bibleman\repos\readers-bofm`), applying the same colometric philosophy to the GNT. The BOM Reader is the methodological precedent — its handoffs (especially `10-colometry.md`) contain the editorial theory.

- **Repo:** github.com/bibleman-stan/readers-nt (public)
- **Base text:** SBL Greek New Testament (SBLGNT) — freely available for research
- **User:** Stan (thebibleman77@gmail.com)
- **Stage:** Early development — colometric formatting of source text

---

## Project Vision

No one has produced a complete, publicly accessible reading edition of the GNT reformatted into grammatically-motivated sense-lines. Scholarly work exists (Lee & Scott's sound mapping, Marschall's colometric analysis of Paul, Runge's discourse segmentation), but it's all analytical — monographs and datasets, not a reading format.

This project fills that gap: take the Greek text, set aside the punctuation, versification, and pericope divisions that accumulated over centuries, and rebuild the line-breaking from the grammar up.

### Four Research Advantages
1. **Authorial intent** — reveals compositional patterns obscured by prose formatting
2. **Structure/consistency** — makes patterns countable and comparable across books
3. **Text-critical implications** — variant readings that break or preserve colometric patterns become evidence
4. **Stylometry-plus** — colon length, participial density, clause-type frequency become quantifiable per author

---

## Repo Structure

```
readers-nt/
  CLAUDE.md              # This file
  README.md              # Public-facing description
  data/
    text-files/
      sblgnt-source/     # Raw SBLGNT by book (canonical, never edit)
      v1-colometric/     # Sense-line formatted versions (working text)
  books/                 # Generated HTML (future)
  scripts/               # Build tools (future)
  research/              # Symlink to vault (gitignored, future)
  handoffs/              # Documentation
```

---

## Colometric Principles (Greek-Adapted)

These are adapted from the BOM Reader's settled rules (`readers-bofm/handoffs/10-colometry.md`), applied to Koine Greek grammar.

### The Foundational Test (unchanged)
**Each line must be an atomic thought, an atomic breath unit, or ideally both.**

### The Image Test (unchanged)
Each line should paint a single image. Two images = candidate for splitting.

### Grammar Reveals Structure (Greek-specific applications)

Greek grammatical break points — these are where the author's own structuring becomes visible:

| Greek Structure | Rule | Example |
|----------------|------|---------|
| καί introducing new main clause | Break before καί | καὶ γίνεται λαῖλαψ μεγάλη ἀνέμου, |
| Participial phrases | Each major participle is a frame | διερχόμενος γὰρ καὶ ἀναθεωρῶν τὰ σεβάσματα ὑμῶν |
| Genitive absolute | Gets its own line (temporal/circumstantial) | ὀψίας γενομένης |
| ἵνα clause (purpose) | Break before ἵνα | ἵνα βλέποντες βλέπωσι καὶ μὴ ἴδωσιν |
| ὥστε clause (result) | Break before ὥστε | ὥστε αὐτὸν εἰς πλοῖον ἐμβάντα καθῆσθαι |
| ὅτι clause (content/causal) | Break before ὅτι | ὅτι τὸν χριστὸν ἔδει παθεῖν |
| ὅταν / ὅτε (temporal) | Break before temporal | καὶ ὅταν ἀκούσωσιν |
| Relative clause (ὅς, ὅστις) | Break if substantial | οἵτινες ἐδέξαντο τὸν λόγον μετὰ πάσης προθυμίας |
| μέν / δέ contrast | Stack as parallel lines | οἱ μὲν ἐχλεύαζον / οἱ δὲ εἶπαν |
| Direct speech introduction | Speech intro on its own line | καὶ ἔλεγεν αὐτοῖς· |
| Tricolon / parallel lists | Stack vertically | ζῶμεν / κινούμεθα / ἐσμέν |
| γάρ clause (explanatory) | Often starts a new line | ἐν αὐτῷ γὰρ ζῶμεν |

### Carry-Over Rules from BOM Reader
- **Never dangle a conjunction** at line end — καί, δέ, ἀλλά lead their line
- **Never split verb from direct object** on short phrases
- **Framing devices attach** — discourse markers lead their content
- **Parallel structures stack vertically** to show rhetorical pattern
- **Line length is a signal, not a rule** — short = emphasis, long = flow

---

## Source Text Rules

The SBLGNT source files in `data/text-files/sblgnt-source/` are canonical reference.

**NEVER:**
- Modify a canonical SBLGNT source file
- Alter the Greek text itself (words, accents, breathing marks)
- Add or remove words

**ALWAYS:**
- Work in `v1-colometric/` — the only editorial tool is where lines break
- Present proposed changes for review before finalizing
- Preserve verse references for alignment with standard editions

---

## Source Text Format

Each file in `v1-colometric/` follows this format:

```
[Book] [Chapter] — Colometric [Version]
SBLGNT base text, sense-line formatting by grammatical cola

[verse ref]
[sense-line 1]
[sense-line 2]
[sense-line 3]

[verse ref]
[sense-line 1]
[sense-line 2]
```

- Verse reference on its own line (e.g., `4:1`)
- Sense-lines below, one per line
- Blank line between verses
- No indentation (flat structure for now)

---

## What Stan Does / What Claude Does

**Stan:**
- Makes all final editorial decisions on line breaks
- Reviews all proposed changes
- Pushes to GitHub
- Has final say on all colometric decisions
- Decides which books/chapters to work on next

**Claude Code:**
- Formats raw SBLGNT text into initial colometric draft
- Proposes line-break revisions with rationale
- Builds and maintains tooling (scripts, build pipeline)
- Maintains documentation and handoffs
- Quantitative analysis (colon counts, pattern detection)
- Never touches source text without explicit approval

---

## Connected Resources

- **BOM Reader repo:** `C:\Users\bibleman\repos\readers-bofm` — methodological precedent
- **Academic vault:** `C:\vaults-nano\my_brain\` — Greek grammar notes, Bible book files, scholar notes
- **Gospel vault:** `C:\vaults-nano\gospel\` — devotional scripture notes
- **Key scholarly references:**
  - Lee & Scott, *Sound Mapping the New Testament* (2009, 2nd ed.)
  - Marschall, *Colometric Analysis of Paul's Letters* (2024, WUNT II)
  - Runge, *Discourse Grammar of the Greek New Testament* (2010)
  - Levinsohn, *Discourse Features of New Testament Greek* (2000)

---

## Git Workflow

- All work on `main` branch
- Stan pushes from his local machine
- Claude Code prepares commits but cannot push (same 403 proxy as BOM Reader)
