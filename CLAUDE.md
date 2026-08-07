# Greek New Testament Reader — Claude Code Instructions (thin stub)

This repo is operated by the **unified user-home orchestrator-Claude** at `C:\Users\bibleman\`. Stan opens VSCode at user-home, not at this repo.

If you are a Claude that spawned in this workspace (VSCode opened at this repo): **hand off**. Tell Stan to switch to a vault-Claude window at `C:\Users\bibleman\`. The unified Claude has full cross-repo context; per-repo Claudes don't.

## What this project is (for collaborators / forks)

A colometric reading edition of the Greek New Testament at **gnt-reader.com**. Each line on the page is an atomic thought unit (ATU); structural English gloss + KJV verbatim aligned to Greek cola. Sibling to readers-bofm + readers-tanakh. Substrate for readers-gnt-morph (the morphological decomposition layer) and rev-reader (the Revelation background-swap layer).

- **Data sources**: SBLGNT (Greek text); SBLGNT-lowfat + MorphGNT (clause-atoms + morph); Macula Greek (clause structures)
- **Source files**: `data/text-files/v1.5/grk/` (Greek ATU lines) + `data/text-files/v1.5/eng-kjv/` (KJV gloss, aligned line-for-line). **GNT is at v1.5** — the SBLGNT-native mechanical fabric (`scripts/sblgnt_v1_fabric.py` + `sblgnt_generate.py`) + ported Layer-1 binding rules; a deploy-then-refine baseline (~72% on the idea-unit bar, pervasive over-splitting). **v2 (LLM adjudication on residuals) and v3 (editorial) are NOT yet built** — the path to a refined edition. See `data/text-files/README.md`. Canonical pipeline is mechanical-first per `~/repos/atu-method/1-method/framework.md`.
- **Build**: `scripts/build_books.py` reads `v1.5/grk` + `v1.5/eng-kjv` → `books/*.html` (what the web app serves)
- **Live deploy**: gnt-reader.com (GitHub Pages, auto-deploys from main)
- **Sibling consumers**: `readers-gnt-morph/` (morpheme layer) and `rev-reader/` (Revelation background-swap) consume from this repo; never write to it

## For more detail

- **Full prior operational discipline** (208-line CLAUDE.md, authored before the 2026-05-19 vault unification) is archived at [`_archive/2026-05-19-pre-unification/CLAUDE.md`](_archive/2026-05-19-pre-unification/CLAUDE.md). Includes editorial discipline, R-rule system, three-stage pipeline conventions (which were superseded — see archive README).
- **Prior cross-repo directives queue** (9 entries including 1 pending Greek Constraint Catalog directive that was rendered obsolete by the methodology pivot) archived at [`_archive/2026-05-19-pre-unification/directives/`](_archive/2026-05-19-pre-unification/directives/). See [`README-SUPERSESSION-NOTE.md`](_archive/2026-05-19-pre-unification/directives/README-SUPERSESSION-NOTE.md) inside that dir for context on the obsolete pending directive.
- **Canonical methodology** (cross-corpus): `~/repos/atu-method/docs/` — framework.md, toolset-architecture.md, apparatus.md. The Greek-specific binding-rule catalog (parallel to `binding-rules-hebrew.md`) is planned future work as part of the GNT-via-PROIEL pilot.
- **Per-repo GNT canon**: `private/01-method/` (gitignored).

## Migration arc

This thin stub is part of the **master-blaster vault unification** (2026-05-19). Stan retired per-repo Claudes in favor of a single orchestrator at `C:\Users\bibleman\`. See `~/.claude/projects/C--Users-bibleman/memory/_named_arcs.md` for the arc.

`Audit-skippable per §7.3 (master-blaster Phase 6 — documentation-only stub demotion + directives archive with supersession note; no code, no canon, no rule, no data)`
