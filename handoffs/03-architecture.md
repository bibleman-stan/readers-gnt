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
```

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

Converts v4-editorial Greek + web-colometric structural glosses to dual-text HTML.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py               # all books
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py --book mark    # one book
```

**Source priority:** v4-editorial (primary) → v3-colometric (fallback) for Greek. web-colometric for English structural glosses.

---

## CRITICAL: The Cascade Rule

**Every change to Greek breaks MUST cascade through the full pipeline:**

```
Greek edit (v4-editorial) → English regen (web-colometric) → HTML rebuild (books/) → commit → push
```

This is not optional. Skipping any step means the site serves stale or misaligned content. The cascade is a single atomic operation — if you change Greek, you MUST sync English and rebuild HTML in the SAME work unit. Not "next session." Not "I'll get to it later."

**When dispatching agents to edit Greek:** ALWAYS simultaneously dispatch agents to regenerate the corresponding English. When BOTH complete, rebuild ALL HTML, commit, and push. Never commit Greek changes without syncing English. Never push without rebuilding HTML.

**English structural glosses are NOT an alignment algorithm.** They are purpose-built translations written to match Greek clause order by construction. When Greek lines change, English lines must be REWRITTEN (not redistributed, not script-processed). Each English line is a fresh translation of its corresponding Greek sense-line.

**Verification after every cascade:** Run the line-count checker across all 260 files. Any mismatch means the cascade is incomplete.
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
- `data/text-files/web-colometric/` — WEB (World English Bible) aligned to colometric breaks (replaces ylt-colometric as active English layer)

New and updated scripts:
- **web_align.py** (new): Double-wire WEB alignment with spaCy dependency parsing validation. Approach: Greek to Macula English (perfect by construction) to WEB (LCS alignment). spaCy validates cut points to prevent splitting inside English phrases.
- **diagnostic_scanner.py** (new): Criteria-based line auditing tool. Applies the three core colometric criteria to flag lines that fail atomic thought, single image, or breath unit tests.
- **ylt_align_lcs.py** (new): Experimental LCS-based YLT alignment (R&D, superseded by web_align.py).
- **ylt_align_double.py** (new): Experimental double-wire YLT alignment (R&D, superseded by web_align.py).
- **build_books.py** (updated): Now checks v4-editorial before v3-colometric for Greek source (editorial hand takes priority). Checks web-colometric before ylt-colometric for English source.
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
                       web-colometric > ylt-colometric for English -> books/*.html)
```

build_books.py priority chain: v4-editorial (if exists) > v3-colometric for Greek; web-colometric (if exists) > ylt-colometric for English.

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
- **English:** web-colometric (structural glosses, purpose-built per line — no alignment algorithm)

The English layer is no longer an aligned translation. Each structural gloss was written to match its Greek line, so alignment is guaranteed by construction. `web_align.py` and `ylt_align.py` are no longer in the active pipeline.

#### Domain Status

**gnt-reader.com** is live with HTTPS enforced via GitHub Pages. Cloudflare DNS configured. CNAME in repo root.

#### v4 Editorial Coverage

120 of 260 chapters now have v4-editorial files produced by the system-wide editorial review. Approximately 52 chapters flagged for second-pass work. The v4-editorial directory is the authoritative Greek source wherever it exists; v3-colometric remains the fallback for chapters not yet editorially reviewed.
