# private/ — layout and conventions

**This folder is gitignored and Dropbox-backed.** It holds pre-publication material, session artifacts, and active working documents that should not land in the public repository.

## Numbered directory layout

| Dir | Purpose |
|---|---|
| `01-method/` | Methodology canon (colometry rules), Marschall alignment, methodology comparisons |
| `02-research/` | Thesis-grade material — prospectus, paper outlines, bibliography, research strategy |
| `03-sessions/` | Dated session artifacts — one subdirectory per session |
| `04-audits/` | Self-audits, scan outputs, and diagnostic findings |
| `06-red-team/` | Defense and reception-prep drafts |
| `07-affordances/` | Named scholarly-affordance drafts enabled by the colometric substrate |
| `08-comparisons/` | External benchmark comparisons — translation spot-checks, Macula data, non-method items |

Note: `05-scripts/` is skipped (GNT's mature scanners live in `readers-gnt/scripts/`).

## Root-level files

- `OVERSEER-DIRECTIONS.md` — live coordination file between this project and its sibling.
- `README.md` — this file.

## Cross-project parallel

The BofM side has a parallel numbered layout at `readers-bofm/private/`. Files with equivalent roles live in equivalent subdirectories.

## When creating new files

- **Methodology refinements** → `01-method/`
- **Session-specific findings** → `03-sessions/[date]-[session-name]/`
- **Scan/audit outputs** → `04-audits/`
- **Benchmark comparisons** → `08-comparisons/`
- **Cross-project traffic** → `OVERSEER-DIRECTIONS.md`
- **Anything unclear** → drop at `private/` root; next overseer pass will file it

## Reorganization history

Original flat structure (49+ files) reorganized 2026-04-13. Numbered directory structure established 2026-04-16 for clearer grouping and methodology isolation. History tracked in `c:/Users/bibleman/repos/overseer-workspace/`.
