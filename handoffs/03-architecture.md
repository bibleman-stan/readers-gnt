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
      v2-colometric/                     # 260 syntax-tree-driven chapter files (tier 2, active)
        matt-01.txt ... rev-22.txt
  books/                                 # 27 generated HTML fragment files (from v2)
    matt.html, mark.html, ... rev.html
  scripts/
    auto_colometry.py                    # Tier 1: rule-based sense-line formatter
    v2_colometry.py                      # Tier 2: Macula syntax-tree-driven formatter
    macula_clauses.py                    # Clause boundary extractor from Macula XML
    build_books.py                       # Text→HTML fragment builder (reads v2-colometric)
  handoffs/                              # Project documentation (this folder)
  research/                              # Gitignored — external datasets
    morphgnt-sblgnt/                     # MorphGNT SBLGNT morphological tagging
    macula-greek/                        # Macula Greek syntax trees (Clear Bible)
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

### build_books.py

Converts v2-colometric text files to HTML fragment files.

**Usage:**
```bash
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py               # all books
PYTHONIOENCODING=utf-8 py -3 scripts/build_books.py --book mark    # one book
```

**What it does:**
1. Globs all `.txt` files in `data/text-files/v2-colometric/`
2. Groups by book prefix (everything before last dash in filename)
3. Parses each chapter file into verse blocks (verse ref line, then sense-lines, separated by blank lines)
4. Skips header lines before first verse reference
5. HTML-escapes Greek text
6. Writes one HTML fragment per book to `books/{book}.html`

**HTML output structure:**
```html
<div class="chapter" id="ch-4">
  <div class="verse"><span class="verse-num">4:1</span>
    <span class="line">Καὶ πάλιν ἤρξατο διδάσκειν παρὰ τὴν θάλασσαν.</span>
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
