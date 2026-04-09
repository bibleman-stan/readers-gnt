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
