# 03 — Architecture & Build Pipeline

## Repo Structure (as of 2026-04-09)

```
readers-gnt/
  CLAUDE.md                              # Claude Code orientation doc
  README.md                              # Public-facing description
  index.html                             # Main web app (all CSS/JS inline, ~340 lines)
  .gitignore                             # Ignores research/, __pycache__, OS files
  data/
    text-files/
      sblgnt-source/                     # 27 raw SBLGNT files (canonical, NEVER edit)
        Matt.txt, Mark.txt, ... Rev.txt
      v1-colometric/                     # 260 pattern-matched chapter files (tier 1)
        matt-01.txt ... rev-22.txt
      v2-colometric/                     # 260 syntax-tree-driven chapter files (tier 2)
        matt-01.txt ... rev-22.txt
      v3-colometric/                     # 260 rhetorical+refined chapter files (tier 3, active)
        matt-01.txt ... rev-22.txt
      ylt-colometric/                    # YLT English aligned to colometric breaks
        matt-01.txt ... rev-22.txt
    ylt-verses.json                      # Parsed YLT text keyed by book/chapter/verse
  books/                                 # 27 generated HTML fragment files (dual-text)
    matt.html, mark.html, ... rev.html
  scripts/
    auto_colometry.py                    # Tier 1: rule-based sense-line formatter
    v2_colometry.py                      # Tier 2: Macula syntax-tree-driven formatter
    macula_clauses.py                    # Clause boundary extractor from Macula XML
    v3_colometry.py                      # Tier 3: rhetorical patterns + merge rules
    morphgnt_lookup.py                   # MorphGNT word-level morphological lookup
    ylt_parse.py                         # Downloads/parses YLT into ylt-verses.json
    ylt_align.py                         # Sequential forward-scan YLT alignment
    build_books.py                       # Text→HTML fragment builder (reads v3 + ylt)
  handoffs/                              # Project documentation (this folder)
  research/                              # Gitignored — external datasets
    morphgnt-sblgnt/                     # MorphGNT SBLGNT morphological tagging
    macula-greek/                        # Macula Greek syntax trees (Clear Bible)
    ylt/                                 # YLT source files (USFM from eBible.org)
  private/                               # Gitignored — Stan's strategic research workspace
                                         # (Windows junction → Dropbox, see note below)
```

## Private Research Workspace (`private/`)

The `private/` folder contains Stan's strategic research materials that are intentionally kept out of the public repo: the PhD prospectus draft, the scholarly impact opportunity space document, the annotated bibliography, paper outlines, session observations, adversarial audit reports, triage documents, scan outputs, and all strategic planning work. The folder is excluded via `.gitignore` per the project-siloing decision (see `handoffs/01-project-overview.md` on siloing) — nothing in `private/` ever reaches the public GitHub repo.

**Physical location (as of 2026-04-12):** The actual files live in **`C:\Users\bibleman\Dropbox\gnt-reader-private\`**. The `private/` path in the repo root is a **Windows directory junction** pointing at the Dropbox folder:

```
C:\Users\bibleman\repos\readers-gnt\private  →  C:\Users\bibleman\Dropbox\gnt-reader-private
```

**Why the junction:** Dropbox auto-syncs the folder to the cloud, provides automatic version history, and enables cross-machine access without interfering with the repo's `.gitignore` rule or any local read/write workflows. Every edit Claude Code makes to `private/` is automatically backed up within seconds.

**How it was created** (one-time setup, already done):
```batch
mkdir "C:\Users\bibleman\Dropbox\gnt-reader-private"
robocopy "C:\Users\bibleman\repos\readers-gnt\private" "C:\Users\bibleman\Dropbox\gnt-reader-private" /E
rmdir /S /Q "C:\Users\bibleman\repos\readers-gnt\private"
mklink /J "C:\Users\bibleman\repos\readers-gnt\private" "C:\Users\bibleman\Dropbox\gnt-reader-private"
```

**How to verify the junction is in place:**
```bash
# Unix-style (git bash):
ls -la private  # should show "private -> /c/Users/bibleman/Dropbox/gnt-reader-private"

# Windows cmd:
dir /AL | findstr private  # should show "<JUNCTION>     private [C:\Users\bibleman\Dropbox\gnt-reader-private]"
```

**Read/write transparency:** All normal file operations work exactly as if `private/` were a regular local folder. Claude Code reads and writes to `private/` without needing to know about the junction. The Read, Write, Edit, Bash, and Grep tools all operate on `private/` normally.

**One caveat for `find`:** the Unix `find` command does NOT follow junctions by default. If you need to traverse `private/` with find, use `find -L private/` (the `-L` flag follows symbolic links and junctions). Bare `ls private/`, `wc -l private/*.md`, Read tool, and grep-via-Grep-tool all work fine without `-L`.

**If the junction ever needs to be recreated** (e.g., after cloning the repo to a new machine that already has the Dropbox folder synced):
```batch
rmdir "C:\Users\bibleman\repos\readers-gnt\private"  REM only if an empty private/ exists
mklink /J "C:\Users\bibleman\repos\readers-gnt\private" "C:\Users\bibleman\Dropbox\gnt-reader-private"
```

**Cross-machine implications:** if Stan wants to work with Claude Code on a second machine, that machine needs: (a) Dropbox installed with the `gnt-reader-private` folder synced locally, and (b) the junction recreated from the repo's `private/` to the local Dropbox path. The repo itself is still cloned from GitHub normally; only the `private/` junction is machine-specific.

## Base Text: SBLGNT

Source: LogosBible/SBLGNT on GitHub (CC-BY-4.0, Society of Biblical Literature + Logos Bible Software, 2010).

The raw text files are in `data/text-files/sblgnt-source/`. Format per line:
```
Book Chapter:Verse\tGreek text with apparatus markers
```

First line of each file is the Greek book title (e.g., `ΚΑΤΑ ΜΑΡΚΟΝ`).

**Apparatus markers** in the source text: `⸀ ⸁ ⸂ ⸃ ⸄ ⸅` — these mark variant readings in the SBLGNT apparatus. The auto-formatter strips them during processing. The v1-colometric files contain clean text without these markers.

## Scripts

### auto_colometry.py

Rule-based sense-line formatter. Takes raw SBLGNT source and applies colometric line-breaking.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py              # all 27 books
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py --book Mark  # one book
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py --book Mark --chapter 4  # one chapter
```

**What it does (7 passes):**
1. Break at major punctuation (ano teleia `·`)
2. Break before subordinating conjunctions (ἵνα, ὥστε, ὅταν, ὅτε, ἐάν, μήποτε, καθώς, etc.)
3. Break before discourse markers (ἀλλά, πλήν, οὐδέ, μηδέ)
4. Break at speech introductions (ἔλεγεν, εἶπεν, λέγει, etc.)
5. Break before καί after commas (heuristic for clause boundaries)
6. Break before ὅτι (content/causal clauses, with minimum-length guard)
7. Break before relative pronouns after commas (ὅς, ἥτις, οἵτινες, etc.)
8. Merge very short fragments (< 12 chars) back into neighbors (with standalone exceptions for imperatives, vocatives, ἰδού)

**Input:** `data/text-files/sblgnt-source/*.txt`
**Output:** `data/text-files/v1-colometric/*.txt` (one file per chapter, named `{abbrev}-{chapter}.txt`)

**IMPORTANT:** Running auto_colometry.py will **overwrite** all files in v1-colometric. If hand edits have been made, they will be lost. Once hand editing begins on specific chapters, those chapters should be protected from re-runs (a mechanism for this doesn't exist yet — it's a future need).

### v2_colometry.py (Tier 2 — syntax-tree-driven)

Uses Macula Greek syntax trees to determine clause boundaries, then maps those boundaries onto the canonical SBLGNT text to produce colometric output. This is the primary formatter as of 2026-04-09.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/v2_colometry.py                    # all 27 books
PYTHONIOENCODING=utf-8 py -3 scripts/v2_colometry.py --book Acts         # one book
PYTHONIOENCODING=utf-8 py -3 scripts/v2_colometry.py --book Acts --chapter 1  # one chapter
```

**What it does:**
1. Reads SBLGNT source text (canonical words with punctuation)
2. Reads Macula clause boundaries via `macula_clauses.py`
3. Aligns Macula clause labels to SBLGNT word positions
4. Breaks lines at clause boundaries
5. Cleanup: merges isolated particles/articles, fixes dangling function words

**Input:** `data/text-files/sblgnt-source/*.txt` + `research/macula-greek/SBLGNT/lowfat/*.xml`
**Output:** `data/text-files/v2-colometric/*.txt`

**Requires:** Macula Greek dataset in `research/macula-greek/` (gitignored, cloned separately).

### macula_clauses.py

Library module that extracts clause boundaries from Macula Greek Lowfat XML syntax trees. Used by `v2_colometry.py`.

**Key functions:**
- `get_chapter_clauses(book, chapter)` → `{verse: [clause_text, ...]}`
- `get_chapter_clauses_detailed(book, chapter)` → `{verse: [ClauseInfo, ...]}` with metadata (participle flags, genitive absolute detection)

### ylt_parse.py

Downloads and parses the YLT (Young's Literal Translation) into a structured JSON file.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/ylt_parse.py
```

**What it does:**
1. Reads YLT source files (USFM format from eBible.org) from `research/ylt/`
2. Parses into book/chapter/verse structure
3. Writes `data/ylt-verses.json` — keyed by book, chapter, verse with plain text content

**Input:** `research/ylt/*.usfm` (gitignored, downloaded separately)
**Output:** `data/ylt-verses.json`

### ylt_align.py

Aligns YLT verse text to the colometric line breaks established in the Greek text.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py                    # all 27 books
PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --book Acts         # one book
PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --book Acts --chapter 9  # one chapter
```

**What it does:**
1. Reads the Greek colometric chapter files (v3-colometric) to get line counts per verse
2. Reads the corresponding YLT verse text from `data/ylt-verses.json`
3. Splits YLT text at clause boundaries that correspond to the Greek colometric breaks
4. Writes aligned YLT text files with the same line count as the Greek

**Input:** `data/text-files/v3-colometric/*.txt` + `data/ylt-verses.json`
**Output:** `data/text-files/ylt-colometric/*.txt` (one file per chapter, same naming as Greek)

**Alignment is ~60% automated, ~40% hand-refinement.** Where YLT departs from Greek clause order, manual adjustment is needed.

### build_books.py

Converts v4-editorial Greek + eng-gloss structural glosses to dual-text HTML.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py               # all books
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py --book mark    # one book
```

**Source priority:** v4-editorial (primary) → v3-colometric (fallback) for Greek. eng-gloss for English structural glosses.

---

## The Substrate-as-Stable-API Principle

**The `v4-editorial/` text format is the API between the reader and any analytical tool built on top of it. It does not change shape by policy.**

The colometric text files are the canonical substrate. Their format is minimal and fixed:
- Verse numbers on their own lines (`9:1`, `9:2`, etc.)
- One sense-line per intended colometric break
- UTF-8 with polytonic Greek accents
- Blank lines between verses

That is the entire grammar. Nothing richer lives in the substrate — no inline structural tags, no depth indicators, no rhetorical annotations, no morpheme boundaries, no audio timing cues.

### Why the substrate stays simple

**Third-party usability.** Any scholar who wants clean colometric Greek can grab `v4-editorial/` and use it without parsing project-specific annotations. That is valuable for external tools and future projects.

**Format stability forever.** There is nothing in the substrate that could change shape. Verse numbers, line breaks, text. That is the whole grammar.

**Enrichments are additive, not transformative.** New analytical layers (morpheme decomposition, rhetorical depth mapping, stylometry dashboards, audio sync) become side-projects that CONSUME the substrate as input. They never modify it.

**Publication stability.** "Here's the reading edition. Here's what it enables." The substrate doesn't drift under the feet of either the reader OR the analyst. Both can cite a stable corpus.

### When something "needs" richer markup

If an analytical need arises that genuinely requires inline structural markup (e.g., `[FEF]` tags, depth indentation, phrase-level boundaries), **fork it into its own path (`readers-gnt/structures/` or similar) or its own repo.** Do NOT modify the substrate to accommodate. The substrate's value is its simplicity; compromising that compromises the whole platform.

### The analytical layer pattern

Analytical tools built on the substrate live at `readers-gnt/analysis/<tool-name>/` (deployed to `gnt-reader.com/analysis/<tool-name>/`). Examples (current and planned):

- `/analysis/morph/` — Morpheme-decomposed reader (Greek word internal structure)
- `/analysis/depth/` — Rhetorical depth mapping (planned)
- `/analysis/style/` — Stylometry dashboard (planned)

Each analytical layer:
- Consumes `v4-editorial/` as read-only input
- Lives in its own subdirectory with its own build process
- Can evolve independently of the main reader
- Shares the gnt-reader.com domain but not the main reader's UI

This is the Unix philosophy applied to a reading edition: simple things compose; complex things don't. The substrate stays on the simple side of the line, and complexity lives in tools that consume it.

---

## CRITICAL: The Cascade Rule

**Every change to Greek breaks MUST cascade through the full pipeline:**

```
Greek edit (v4-editorial) → English regen (eng-gloss) → HTML rebuild (books/) → commit → push
```

This is not optional. Skipping any step means the site serves stale or misaligned content. The cascade is a single atomic operation — if you change Greek, you MUST sync English and rebuild HTML in the SAME work unit. Not "next session." Not "I'll get to it later."

**When dispatching agents to edit Greek:** ALWAYS simultaneously dispatch agents to regenerate the corresponding English. When BOTH complete, rebuild ALL HTML, commit, and push. Never commit Greek changes without syncing English. Never push without rebuilding HTML.

**English structural glosses are NOT an alignment algorithm.** They are purpose-built translations written to match Greek clause order by construction. When Greek lines change, English lines must be REWRITTEN (not redistributed, not script-processed). Each English line is a fresh translation of its corresponding Greek sense-line.

**Verification after every cascade:** Run the line-count checker across all 260 files. Any mismatch means the cascade is incomplete.

## Efficiency Principle: Scripts Before Agents

When fixing violations at scale, ALWAYS ask: "Is this pattern-matchable?" If yes, write a script that fixes it across all 260 files in seconds. Only dispatch agents for judgment calls that require reading comprehension.

Examples of script-fixable violations:
- Dangling postpositive conjunctions (δέ/γάρ/οὖν orphaned at line start)
- Vocative-case words not on their own line (detectable via Macula XML case="vocative")
- Lines >140 characters containing subordinating conjunctions (split at conjunction)
- Lines >80 characters containing ἵνα/ὅτι/ὥστε/ὅταν/ὅτε/ἐάν (split at conjunction)

Examples that REQUIRE agent judgment:
- Camera-angle participle splits (requires understanding the image)
- Parallel stacking decisions (requires recognizing the rhetorical structure)
- FEF protection (requires understanding periodic sentence architecture)
- Category B/C editorial decisions (rhetorical shape, theological weight)

One script run replaces hundreds of agent dispatches. Tokens are precious. Use them for judgment, not for mechanical pattern-matching.
7. Emits dual-text HTML: each line wrapped with language class for CSS show/hide
8. Writes one HTML fragment per book to `books/{book}.html`

**HTML output structure (dual-text):**
```html
<div class="chapter" id="ch-4">
  <div class="verse"><span class="verse-num">4:1</span>
    <span class="line greek-line">Καὶ πάλιν ἤρξατο διδάσκειν παρὰ τὴν θάλασσαν.</span>
    <span class="line english-line">And again he began to teach by the sea.</span>
  </div>
</div>
```

**IMPORTANT:** `PYTHONIOENCODING=utf-8` is required on Windows for both scripts due to Greek Unicode characters in console output.

## Full Rebuild Workflow

After any text edits:

```bash
cd C:\Users\bibleman\repos\readers-gnt
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py
# Then commit the changed books/*.html files
```

If re-running the auto-formatter (caution — overwrites hand edits):
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/auto_colometry.py
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py
```

## Web App (index.html)

Single-page app, all CSS and JS inline. No external dependencies except Google Fonts (Literata).

### UI Design
- **Dark grey background** (`#1c1f24`) — matches the design language of scholarly reading tools
- **Literata serif font** from Google Fonts — excellent for extended reading
- **CSS variable system** for consistent theming: `--bg`, `--text`, `--accent` (#7cafc2 blue), `--text-dim`, `--text-faint`, `--border`, etc.
- **Line-height 2.35**, wrap-indent 0.75em, max-width 42em — same reading metrics
- **Verse numbers:** small, sans-serif, muted color, block-level above each verse
- **Progress line** at top of viewport showing scroll position

### Display Mode Toggle
- **Settings panel** includes a three-way display mode: **Greek** (default) / **English** (YLT) / **Both** (interleaved)
- Greek mode: only `.greek-line` spans visible (default, matches original behavior)
- English mode: only `.english-line` spans visible (YLT rendering of colometric breaks)
- Both mode: both spans visible, interleaved (Greek line followed by its English equivalent)
- Toggle state persisted in localStorage
- CSS classes control visibility — no DOM manipulation needed, just class swapping on the container

### Navigation
- **Topbar (44px fixed):** book name + chapter number (accent color) on left, "GNT Reader" branding (italic, faint) on right. Clicking the book/chapter opens the nav panel.
- **Nav panel:** full-screen overlay (`#0e1014` background). Lists all 27 books as rows with chapter count. Clicking a book expands a chapter number grid inline. Clicking a chapter navigates and closes the panel. Single-chapter books (Philemon, 2 John, 3 John, Jude) navigate directly.
- **Chapter nav buttons:** Previous/Next at bottom of text area. Cross book boundaries (end of Mark → Luke 1). Disabled at Matt 1 and Rev 22.
- **Hash routing:** URL format `#mark-4`, `#acts-17`. Parsed on load and hashchange. Defaults to Mark 1.

### Data Loading
- Book HTML loaded via `fetch('books/' + slug + '.html')` on demand
- Cached in memory per book (`bookCache` object) — no re-fetching
- After load, scrolls to `#ch-{n}` element

### GitHub Pages Compatible
- Pure static — no server, no build step for the web app itself
- `index.html` in repo root, `books/` directory alongside it
- Served at `bibleman-stan.github.io/readers-gnt/` (Pages must be enabled: Settings → Pages → main branch, root)

## Book Inventory

| Key | Name | Chapters | Source | v1 Colometric | HTML |
|-----|------|----------|--------|---------------|------|
| matt | Matthew | 28 | Matt.txt | matt-01..28.txt | matt.html |
| mark | Mark | 16 | Mark.txt | mark-01..16.txt | mark.html |
| luke | Luke | 24 | Luke.txt | luke-01..24.txt | luke.html |
| john | John | 21 | John.txt | john-01..21.txt | john.html |
| acts | Acts | 28 | Acts.txt | acts-01..28.txt | acts.html |
| rom | Romans | 16 | Rom.txt | rom-01..16.txt | rom.html |
| 1cor | 1 Corinthians | 16 | 1Cor.txt | 1cor-01..16.txt | 1cor.html |
| 2cor | 2 Corinthians | 13 | 2Cor.txt | 2cor-01..13.txt | 2cor.html |
| gal | Galatians | 6 | Gal.txt | gal-01..06.txt | gal.html |
| eph | Ephesians | 6 | Eph.txt | eph-01..06.txt | eph.html |
| phil | Philippians | 4 | Phil.txt | phil-01..04.txt | phil.html |
| col | Colossians | 4 | Col.txt | col-01..04.txt | col.html |
| 1thess | 1 Thessalonians | 5 | 1Thess.txt | 1thess-01..05.txt | 1thess.html |
| 2thess | 2 Thessalonians | 3 | 2Thess.txt | 2thess-01..03.txt | 2thess.html |
| 1tim | 1 Timothy | 6 | 1Tim.txt | 1tim-01..06.txt | 1tim.html |
| 2tim | 2 Timothy | 4 | 2Tim.txt | 2tim-01..04.txt | 2tim.html |
| titus | Titus | 3 | Titus.txt | titus-01..03.txt | titus.html |
| phlm | Philemon | 1 | Phlm.txt | phlm-01.txt | phlm.html |
| heb | Hebrews | 13 | Heb.txt | heb-01..13.txt | heb.html |
| jas | James | 5 | Jas.txt | jas-01..05.txt | jas.html |
| 1pet | 1 Peter | 5 | 1Pet.txt | 1pet-01..05.txt | 1pet.html |
| 2pet | 2 Peter | 3 | 2Pet.txt | 2pet-01..03.txt | 2pet.html |
| 1john | 1 John | 5 | 1John.txt | 1john-01..05.txt | 1john.html |
| 2john | 2 John | 1 | 2John.txt | 2john-01.txt | 2john.html |
| 3john | 3 John | 1 | 3John.txt | 3john-01.txt | 3john.html |
| jude | Jude | 1 | Jude.txt | jude-01.txt | jude.html |
| rev | Revelation | 22 | Rev.txt | rev-01..22.txt | rev.html |

**Total: 27 books, 260 chapters, 7,957 verses**

## Deployment

### GitHub Pages Setup
1. Go to github.com/bibleman-stan/readers-gnt → Settings → Pages
2. Source: Deploy from a branch → main → / (root) → Save
3. Wait 1-2 minutes for first deploy
4. Site live at: `bibleman-stan.github.io/readers-gnt/`

### Custom Domain (future)
- Registrar: Cloudflare (same account as bomreader.com)
- Domain candidates: `gntreader.com`, `gnt-reader.com`
- Once purchased: add CNAME file to repo root, configure DNS in Cloudflare dashboard

## Git Workflow

- All work on `main` branch
- Claude Code commits; Stan pushes via GitHub Desktop
- Stan confirmed: "from now on, whenever you finish, do a commit and i'll push"
- Claude cannot push (403 proxy error, same as BOM Reader)

---

### Established — 2026-04-09
- Full repo structure created
- Both scripts built and tested
- Web app built with BOM Reader design language
- All 27 books formatted, built, and committed
- GitHub Pages deployment instructions documented

---

### Update — 2026-04-09 (session 2)
- Tier 1 auto-formatter expanded: added γάρ, οὖν (postpositive handling), δέ, εἰ, ἐπεί, ὅπως, ἄχρι, μέχρι, διό, ἄρα, ὥσπερ, ὅπου; μέν/δέ stacking; vocative detection
- Tier 2 formatter built: v2_colometry.py + macula_clauses.py
- MorphGNT and Macula Greek datasets cloned to research/ (gitignored)
- v2-colometric directory created with all 260 chapters
- build_books.py now reads from v2-colometric (was v1-colometric)
- Web app now serves v2 syntax-tree-driven output
- Repo renamed from readers-nt to readers-gnt; all branding updated to "GNT Reader"

---

### Update — 2026-04-09 (session 2, continued)

#### New and Updated Scripts

- **morphgnt_lookup.py** (new): MorphGNT word-level morphological lookup utility. Provides verbal element detection (finite verbs, participles, infinitives) for any word in the SBLGNT. Used by v3_colometry.py to identify verbless lines that need merging.
- **bezae_compare.py** (updated): Now supports `--tier` flag (v1/v2/v3) to compare a specific tier's output against Codex Bezae line breaks, and `--all-tiers` flag to run all three comparisons in a single invocation and produce a summary table.
- **v3_colometry.py** (updated): Now uses MorphGNT data via morphgnt_lookup.py for verbless line detection. Lines without any verbal element (finite verb, participle, or infinitive) are merged into their nearest verbal neighbor.

#### Updated Build Pipeline

The active pipeline is now three stages:

```
v2_colometry.py  (syntax-tree clause boundaries)
       |
       v
v3_colometry.py  (rhetorical patterns + infinitive merge-back + verbless line merge via MorphGNT)
       |
       v
build_books.py   (reads v3-colometric/ -> books/*.html)
```

build_books.py now reads from `data/text-files/v3-colometric/` (was v2-colometric).

---

### Update — 2026-04-09 (YLT integration)

- New directories added: `data/text-files/ylt-colometric/`, `research/ylt/`
- New data file: `data/ylt-verses.json` (parsed YLT keyed by book/chapter/verse)
- New scripts: `ylt_parse.py` (downloads/parses YLT source), `ylt_align.py` (aligns YLT to colometric breaks)
- `build_books.py` updated: now reads both v3-colometric and ylt-colometric, emits dual-text HTML with language-class spans
- `index.html` updated: display mode toggle (Greek / English / Both) in settings panel, CSS-driven visibility
- Repo structure diagram updated to reflect all new files and directories

---

### Update — 2026-04-09 (session 3)

#### New and Updated Scripts

- **macula_predication.py** (new): Unified predication test using Macula tree walk. Determines whether a participle governs its own clause or is governed by a matrix verb, replacing patchwork heuristics with a single tree-traversal decision.
- **macula_sentences.py** (new): Sentence boundary detection using Macula `<sentence>` elements. Provides hard-constraint sentence breaks — no colon may span a sentence boundary. Produced 1,298 splits corpus-wide.
- **macula_wordgroups.py** (new): Sub-clause splitting using Macula `<wg>` (word group) elements. Targets lines >80 chars that contain multiple word-group boundaries. Produced ~1,100 splits; reduced lines >120 chars to zero.
- **ylt_download.py** (new): Downloads YLT source files (USFM format) from eBible.org into `research/ylt/`.
- **ylt_parse.py** (updated): Parses downloaded YLT USFM files into `data/ylt-verses.json`.
- **ylt_align.py** (updated): Aligns YLT verse text to Greek colometric line breaks. Achieved 99.8% gloss match rate.
- **v3_colometry.py** (major update): Now includes unified predication test, sentence boundary detection, sub-clause splitting, dangling function word fix, post-split safety guards (genitive articles, negations, possessives, postpositives), stranded finite verb merge (451 merges), stranded participle/noun merge (128 merges), relative clause splits (529 splits), complement participle backward merge (560 merges), conditional fixes, staccato commata + asyndeton imperatives, periphrastic εἰμί + participle merge (11 merges), correlative pair merge, ἰδού presentative particle handling, verb valency majority threshold (50%), and role=vc valency tracking.

#### Updated Build Pipeline

The full pipeline now includes YLT alignment:

```
v2_colometry.py       (syntax-tree clause boundaries)
       |
       v
v3_colometry.py       (unified predication + sentence boundaries + sub-clause splits
                       + merge rules + safety guards + valency checks)
       |
       v
ylt_align.py          (align YLT English to Greek colometric breaks)
       |
       v
build_books.py        (reads v3-colometric/ + ylt-colometric/ -> dual-text books/*.html)
```

#### New Data Files

- `data/ylt-verses.json` — parsed YLT keyed by book/chapter/verse
- `data/text-files/ylt-colometric/` — 260 YLT chapter files aligned to Greek colometric breaks

#### v3 Processing Counters (corpus-wide)

| Operation | Count |
|-----------|-------|
| Sentence boundary splits | 1,298 |
| Multi-image splits | 378 |
| Sub-clause splits | ~1,100 |
| Dangling function word fixes | 530+ |
| Stranded finite verb merges | 451 |
| Stranded participle/noun merges | 128 |
| Relative clause splits | 529 |
| Complement participle backward merges | 560 |
| Periphrastic εἰμί merges | 11 |

#### Web App Features Added

- **Landing page:** Book grid TOC showing all 27 books with chapter counts; replaces direct book load
- **Home button:** In topbar, returns to landing page
- **Help overlay:** `?` icon opens overlay explaining navigation, display modes, and keyboard shortcuts
- **Text size controls:** S/M/L buttons in settings panel, persisted to localStorage
- **Search return button:** After navigating from search results, a button returns to the previous search
- **Back-to-top button:** Floating button appears on scroll, returns to top of current chapter
- **Floating chapter arrows:** Left/right arrows for chapter navigation, always visible during reading
- **Display toggle:** Greek / English / Both modes for dual-text reading

---

### Update — 2026-04-10 (session 4)

#### Repo Structure Changes

New directories:
- `data/text-files/v4-editorial/` — Tier 4 editorial hand output (Stan's hand-edited chapters)
- `data/text-files/eng-gloss/` — WEB (World English Bible) aligned to colometric breaks (replaces ylt-colometric as active English layer)

New and updated scripts:
- **web_align.py** (new): Double-wire WEB alignment with spaCy dependency parsing validation. Approach: Greek to Macula English (perfect by construction) to WEB (LCS alignment). spaCy validates cut points to prevent splitting inside English phrases.
- **diagnostic_scanner.py** (new): Line auditing tool. Applies the framework's forces to flag lines that fail atomic-thought or single-image tests. (The script's prior breath-unit test was purged 2026-04-26 alongside the canon retirement; see canon §10 2026-04-26 final-residue-purge entry. Path discovery may still be stale — flagged for future review.)
- **ylt_align_lcs.py** (new): Experimental LCS-based YLT alignment (R&D, superseded by web_align.py).
- **ylt_align_double.py** (new): Experimental double-wire YLT alignment (R&D, superseded by web_align.py).
- **build_books.py** (updated): Now checks v4-editorial before v3-colometric for Greek source (editorial hand takes priority). Checks eng-gloss before ylt-colometric for English source.
- **index.html** (updated): UI updated for WEB display, English punctuation hideable via toggle, landing page verse navigation popover.

#### Updated Build Pipeline

```
v2_colometry.py       (syntax-tree clause boundaries)
       |
       v
v3_colometry.py       (unified predication + sentence boundaries + sub-clause splits
                       + merge rules + safety guards + valency checks)
       |
       v
[v4-editorial/]       (Stan's hand edits — overrides v3 where present)
       |
       v
web_align.py          (align WEB English to Greek colometric breaks via double-wire + spaCy)
       |
       v
build_books.py        (reads v4-editorial > v3-colometric for Greek,
                       eng-gloss > ylt-colometric for English -> books/*.html)
```

build_books.py priority chain: v4-editorial (if exists) > v3-colometric for Greek; eng-gloss (if exists) > ylt-colometric for English.

#### Domain and Deployment

- **gnt-reader.com** purchased and configured (Cloudflare DNS to GitHub Pages)
- CNAME file added to repo root
- HTTPS enforced via GitHub Pages settings
- Custom domain section no longer "future" — it is live

---

### Update — 2026-04-11 (post v4 editorial review)

#### Updated Pipeline Priority Chain

The build pipeline now operates with the following priority:
- **Greek:** v4-editorial (if exists) > v3-colometric
- **English:** eng-gloss (structural glosses, purpose-built per line — no alignment algorithm)

The English layer is no longer an aligned translation. Each structural gloss was written to match its Greek line, so alignment is guaranteed by construction. `web_align.py` and `ylt_align.py` are no longer in the active pipeline.

#### Domain Status

**gnt-reader.com** is live with HTTPS enforced via GitHub Pages. Cloudflare DNS configured. CNAME in repo root.

#### v4 Editorial Coverage

120 of 260 chapters now have v4-editorial files produced by the system-wide editorial review. Approximately 52 chapters flagged for second-pass work. The v4-editorial directory is the authoritative Greek source wherever it exists; v3-colometric remains the fallback for chapters not yet editorially reviewed.

---

### Update — 2026-04-12 (session 9: mechanical-merge infrastructure + cross-verse support)

#### New scanners + appliers (scan-and-apply pattern)

Session 9 introduced two new pairs of scanner+apply scripts that implement the "scan-then-mechanically-apply" pattern corpus-wide. Both operate on v4-editorial Greek and eng-gloss English in lockstep, avoiding the English-alignment drift that proportional regen introduces. This is a departure from the earlier "dispatch agents for mass editorial work" pattern, and should be preferred whenever a class of errors can be described structurally.

**`scripts/scan_vocative_apposition.py`** — classifies every vocative-only line in the corpus and emits merge candidates with grammatical justification:

- `INITIATING` — verse-initial, own line (atomic address act)
- `TRAILING` — verse-final, own line (tail address)
- `APPOSITION-CANDIDATE` — mid-verse with a preceding 2p pronoun or 2p finite verb in the same verse (not separated by a `·`/`:` speech-intro boundary) → merge candidate
- `INITIATING-QUOTED-SPEECH` — immediately after a `·`/`:` speech-intro → own line, initiating quoted discourse
- `MID-NO-2P` — mid-verse with no preceding 2p marker → own line

Every APPOSITION-CANDIDATE cites the specific preceding pronoun or verb that licenses the merge. Reflect-not-impose: the grammatical justification is in the scan output.

**`scripts/apply_vocative_merges.py`** — applies the APPOSITION-CANDIDATE merges. Supports `--english` (to apply to eng-gloss), `--save-candidates` / `--load-candidates` (to share the candidate list between Greek and English passes without re-scanning), and `--dry-run`. Processes merges within a verse in reverse order so that deletions don't shift earlier line indices.

**`scripts/scan_no_anchor_lines.py`** — finds every line in the corpus that lacks a thought-marking anchor (finite verb, infinitive, participle, or head substantive in N/A/D/V case). Features:

- Conjunction/particle skip when finding the head word (catches `Καὶ τῇ πρώτῃ ἡμέρᾳ...` as anchored by `τῇ`)
- Single-line verse exemption (atomic by definition — catches Luke 3:23-38 genealogy, Benedictus tails, elliptical nominal claims)
- First-content-word head-substantive test in N/A/D/V (catches epistolary addressee datives like Col 1:2)

Emits for each flagged line: file, ref, line index, full verse context, and the reason (why it fails) plus the nearest preceding anchored line as merge target.

**`scripts/apply_no_anchor_merges.py`** — applies the no-anchor merges. Default is upward merge (flagged line → line directly above). **Downward-merge fallback** for verse-initial unanchored lines: if the upward target doesn't exist, the flagged line merges with the next content line instead. Handles verse-opening prep catenae and connective hinges that frame a following main verb (Mark 3:8, Rev 10:7, Rom 5:12, Rom 12:1).

**`scripts/scan_english_drift.py`** — heuristic detector for probable English-gloss alignment drift. Classifies flags at three confidence tiers (high / med / low). Detects:

- `ARTICLE-SPLIT` — article dangling at line end
- `PREP-NP-SPLIT` — preposition followed by article/possessive/demonstrative
- `AUX-VERB-SPLIT` — auxiliary + verb form split
- `PTC-NP-SPLIT` — participle (-ing/-ed) split from direct object NP
- `APPOSITIVE-SPLIT` — proper noun at line end + possessive on next line
- `DANGLING-CONJ` — coordinating conjunction dangling (low confidence)

Punctuation-boundary filter skips lines ending with sentence-terminating marks. Default `--min-confidence high`; med/low available for tighter audits.

#### Cross-verse continuation support

**Editorial rule codified in `private/01-method/colometry-canon.md` §3.17** (2026-04-22). This section describes the infrastructure — integrity checker recognition, HTML rendering. Refer to the canon for the editorial rule itself.

The Stephanus 1551 verse divisions occasionally cut through grammatically-continuous thought units (e.g., Matt 3:1-2 where `κηρύσσων` in 3:1 and `λέγων` in 3:2 are parallel participles modifying `παραγίνεται`). Session 9 added infrastructure for inline-verse-marker cross-verse merging:

**Source format convention.** A merged colometric line that crosses a verse boundary lives in the *earlier* verse's block, with an inline superscript digit (`²`/`³`/`⁴`/...) marking where the next verse begins visually:

```
3:1
Ἐν δὲ ταῖς ἡμέραις ἐκείναις παραγίνεται Ἰωάννης ὁ βαπτιστὴς
κηρύσσων ἐν τῇ ἐρήμῳ τῆς Ἰουδαίας ²καὶ λέγων·

3:2
Μετανοεῖτε,
ἤγγικεν γὰρ ἡ βασιλεία τῶν οὐρανῶν.
```

**`scripts/verify_word_order.py`** recognizes these markers. The loader splits a line at each superscript digit and assigns the post-marker content to the indicated verse for word-order comparison. This preserves the SBLGNT integrity guard: the per-verse word list still matches the source even when the colometric file has merged visual lines across verse boundaries.

**`scripts/build_books.py`** renders inline superscripts as `<sup class="verse-marker" id="v-{chapter}-{verse}-inline">N</sup>` HTML elements. The verse-marker is visible inline in the flowing colometric text; the anchor id lets TOC/search functionality jump to the exact inline location where the subsequent verse begins. Verse `div` blocks still carry their primary `id="v-{chapter}-{verse}"` anchors so citation targeting works unchanged.

This mirrors the Nestle-Aland typographic convention for inline verse numbering, ported down to the colometric-line level.

#### The scan-and-apply workflow

```bash
# 1. Save candidates from a fresh scan (Greek files)
PYTHONIOENCODING=utf-8 py -3 scripts/apply_no_anchor_merges.py --save-candidates /tmp/merges.json

# 2. Apply to Greek
PYTHONIOENCODING=utf-8 py -3 scripts/apply_no_anchor_merges.py --load-candidates /tmp/merges.json

# 3. Apply same candidates to English
PYTHONIOENCODING=utf-8 py -3 scripts/apply_no_anchor_merges.py --load-candidates /tmp/merges.json --english

# 4. Rebuild
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py

# 5. Re-scan to confirm residual
PYTHONIOENCODING=utf-8 py -3 scripts/scan_no_anchor_lines.py --summary-only
```

The `--save-candidates` step is essential when running Greek-then-English: the English scan after the Greek merge would find a different (stale) set of candidates because the Greek line structure has changed. Using the saved JSON guarantees the English merge mirrors the Greek merge exactly.

#### Lesson learned: `regenerate_english.py --force` is destructive

The `--force` flag bypasses the "skip if line counts match" guard and mechanically redistributes every verse's English content proportionally. When applied to already-aligned content, it reliably worsens alignment quality. **Never use `--force` on already-aligned content.** Plain `regenerate_english.py --book X` is the correct invocation — it only touches verses where Greek and English line counts differ.

#### The mechanical-merge pattern as future-standard

The vocative pass (125 merges) and the no-anchor pass (860 merges) both demonstrate the same pattern:

1. Build a scanner that finds a specific structural class of errors and cites its grammatical evidence
2. Build an apply tool that mirrors the operation on both Greek and English files in lockstep
3. Run corpus-wide, commit atomically, re-scan to confirm zero residual

This is the replacement for the "dispatch agents to do mass editorial work" approach. It's faster, cheaper, more auditable, and — critically — deterministic. Every merge in a mechanical pass can be traced to a specific grammatical signature in the source. No agent hallucination, no selective application, no author-style variance. Future editorial passes should default to the mechanical pattern whenever a class of errors can be described structurally.

---

## Update — 2026-04-14 (text-pipeline restructure: five-tier arc with reproducibility framing)

The `data/text-files/` directory was restructured to present the project's text pipeline as a **five-tier reproducibility arc**: v0 (canonical prose) → v1 (pattern-matched) → v2 (Macula syntax-tree-driven) → v3 (rhetorical refinement) → v4 (methodology-applied editorial layer). Every tier uses the same `{NN-book}/` subfolder layout as `v4-editorial/`, so a chapter is navigable at the same path across all five tiers.

**A precision note on v4.** v4 is NOT "hand editing" in the sense of a human manually typing out every break decision for every chapter. v4 is where the project's *documented colometric methodology* — atomic thought, cognitive hierarchy, register sensitivity, semantic grouping, the no-anchor rule, the universal vocative rule, the Goldilocks refinement, and the other rules recorded in the methodology canon — is *applied* to the text. Application happens through a mix of systematic scan-and-apply tools (the vocative pass, the no-anchor pass, adversarial-audit-driven merges, Class F audits, and similar mechanical passes that can be described structurally) and case-by-case editorial decisions where the rule set conflicts or underdetermines. The editor is the methodology's operator, not a manual typist. The project's contribution lives in the documented rule set; v4 is its application, not its stenography.

**Two reproducibility regimes.** v0-v3 are bit-exactly reproducible: given the same inputs, running the scripts produces byte-for-byte copies of those tiers. v4 is NOT bit-exactly reproducible (because judgment calls enter where rules underdetermine) but IS methodologically checkable: any chapter can be audited against the documented rule set to confirm whether breaks conform to the rules. Disagreement at an individual line is resolvable by consulting the methodology, not by dispute over "what the editor happened to type."

### New directory layout

```
data/text-files/
  README.md                              # Top-level 5-tier arc documentation
  sblgnt-source/                         # 27 canonical SBLGNT whole-book files (untouched)
    Matt.txt, Mark.txt, ... Rev.txt
  v0-prose/                              # NEW — per-chapter SBLGNT prose (apparatus markers retained)
    README.md
    01-matt/matt-01.txt ... matt-28.txt
    02-mark/mark-01.txt ... mark-16.txt
    ... 27 book subfolders, 260 chapter files total
  v1-colometric/                         # RESTRUCTURED — flat → NN-book/ subfolders
    README.md
    01-matt/matt-01.txt ... matt-28.txt
    ... (same shape as v0)
  v2-colometric/                         # RESTRUCTURED — flat → NN-book/ subfolders
    README.md
    01-matt/matt-01.txt ...
    ...
  v3-colometric/                         # RESTRUCTURED — flat → NN-book/ subfolders
    README.md
    01-matt/matt-01.txt ...
    ...
  v4-editorial/                          # UNCHANGED — already in NN-book/ subfolders
    01-matt/matt-01.txt ...
    ...
  eng-gloss/                             # UNCHANGED — structural English glosses aligned line-for-line with v4
    01-matt/matt-01.txt ...
    ...
```

### Why the restructure

**Transparency and reproducibility.** The previous structure buried v1/v2/v3 as flat directories while v4 was book-subfoldered, making cross-tier navigation awkward. The restructured layout lets anyone open the same chapter at all five stages of the pipeline by walking the same path in each tier, and the top-level `data/text-files/README.md` documents how to reproduce every mechanical tier (v0-v3) from source.

**Honest framing of the project's starting point.** Unlike the Book of Mormon Reader (a sibling project that uses Royal Skousen's published sense-lines as its v1 tier), GNT Reader had no pre-existing scholar-annotated colometric edition to lean on. The three mechanical tiers (v1 pattern-matched, v2 Macula-tree-driven, v3 rhetorical-refined) are the record of how we bootstrapped our own starting point from raw SBLGNT prose plus external syntax-tree data. Preserving them in navigable form shows the mechanical baseline we built before any editorial decisions entered.

**Reproducibility for external validation.** Every mechanical tier (v0, v1, v2, v3) is deterministic: given the same inputs (`sblgnt-source/` for v0/v1; `sblgnt-source/` + Macula Greek trees for v2; v2 output for v3), running the corresponding script produces a bit-exact copy of that tier. This is the "different persons analysing the same text" reproducibility standard that the broader scholarly colometric literature aspires to but rarely delivers. A skeptical scholar checking our work can literally re-run `auto_colometry.py`, `v2_colometry.py`, `v3_colometry.py` and confirm our mechanical output. The v3 → v4 transition is explicitly NOT deterministic — it is editorial hand work governed by the colometric methodology documented in the handoffs.

### v0-prose specifics

v0 is new in this restructure. It is a per-chapter split of `sblgnt-source/*.txt` into `v0-prose/{NN-book}/{abbrev}-{NN}.txt`, with the SBLGNT apparatus markers (`⸀ ⸁ ⸂ ⸃ ⸄ ⸅`) **retained**. Keeping the markers is a deliberate choice: v0 should be a faithful slice of the published scholarly text, not a preprocessed derivative. The first apparatus-marker stripping happens at the v1 step as part of `scripts/auto_colometry.py`, where it has always happened. A reader diffing `sblgnt-source/Matt.txt` against `v0-prose/01-matt/matt-*.txt` should see only chapter splitting, no content changes.

v0 is generated by `scripts/build_v0_prose.py`, which reads each file in `sblgnt-source/`, splits on the `{BookAbbrev} {chapter}:{verse}` line prefix, and writes per-chapter files into the book-subfolder layout.

### v1/v2/v3 restructuring

The chapter files in `v1-colometric/`, `v2-colometric/`, and `v3-colometric/` were moved from flat top-level layout (e.g., `v1-colometric/matt-01.txt`) into matching book subfolders (e.g., `v1-colometric/01-matt/matt-01.txt`). File contents are unchanged; only locations moved. Each directory gained a `README.md` documenting what that tier is, how it was produced, and how to reproduce it.

### Script updates

Four scripts had output path constants updated to reflect the new subfolder layout:

- `scripts/auto_colometry.py` — writes to `v1-colometric/{NN-book}/{abbrev}-{NN}.txt`
- `scripts/v2_colometry.py` — writes to `v2-colometric/{NN-book}/{abbrev}-{NN}.txt`
- `scripts/v3_colometry.py` — writes to `v3-colometric/{NN-book}/{abbrev}-{NN}.txt`
- `scripts/build_books.py` — the v3 fallback in `resolve_greek_path` now walks the book-subfolder layout to find v3 files. In practice the fallback is dead code (every chapter has v4), but it's kept correct for safety.

### Script added

- `scripts/build_v0_prose.py` — NEW. Chapter-split tool that generates `v0-prose/` from `sblgnt-source/`. See the top-level `data/text-files/README.md` for invocation.

### What this restructure did NOT change

- No content changes to any Greek text file at any tier. v1, v2, v3, v4 all contain the exact same bytes they contained before the move (just in different locations).
- No changes to `sblgnt-source/`, `v4-editorial/`, or `eng-gloss/` layout. Those directories were already correct.
- No changes to the web app (`index.html`), the HTML fragment builds (`books/*.html`), or the live site.
- No changes to the colometric methodology or any editorial decisions. This is purely a directory restructure plus documentation work.

### Documentation added

- `data/text-files/README.md` — top-level five-tier arc with reproducibility framing and pipeline diagram
- `data/text-files/v0-prose/README.md`
- `data/text-files/v1-colometric/README.md`
- `data/text-files/v2-colometric/README.md`
- `data/text-files/v3-colometric/README.md`
- This entry in `handoffs/03-architecture.md`
- Corresponding update in `handoffs/04-editorial-workflow.md`
