# GNT Reader Validator Suite

Layer 2 validators for the colometry canon. Two categories matching the
project's three-layer architecture (canon §0):

```
validators/
  syntax/      — Layer 1 checks (generic Koine grammatical illegality)
  colometry/   — Layer 3 checks (project-specific editorial conventions)
  hooks/       — git hooks (pre-commit baseline gate + commit-msg canon-extension gate)
  run_all.py   — discovery + dashboard + baseline regression check
  check_canon_extensions.py — content-aware canon-diff gate (called by commit-msg hook)
  common.py    — shared infrastructure (Candidate dataclass, data loaders)
  .baseline.json — per-rule candidate counts; pre-commit blocks regressions vs this
```

## Error classes

| Tag | Layer | Meaning | Action |
|---|---|---|---|
| `MALFORMED` | `syntax/` | Hard grammatical failure — break violates generic Koine syntax | Fix before editorial review |
| `DEVIATION` | `colometry/` | Editorial-policy violation — break diverges from canon rule | Review; document exception or merge/split |

Each validator module exposes:

- `RULE_ID` — e.g. `"R2"`, `"R18"`
- `ERROR_CLASS` — `"MALFORMED"` or `"DEVIATION"`
- `check_book_chapter(book: str, chapter: int) -> list[Candidate]`

## Running validators

```bash
# Per-rule dashboard (no report file)
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --summary

# Compare current candidate counts to baseline (used by pre-commit hook)
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --baseline-check

# Capture current counts as the new baseline (after intentional changes)
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --update-baseline

# Full markdown report (requires --output)
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --output reports/validator-run.md

# Restrict to specific books or rules
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --summary --books matt mark
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --summary --validators R2 R18
```

## Git hooks

Two hooks live at `validators/hooks/`. Source-of-truth scripts are tracked in
git; installed copies live at `.git/hooks/` (not tracked).

### `pre-commit` — regression-baseline gate

Triggers when staged files include the canon, syntax-reference, v4-editorial
corpus, or validators themselves. Runs `validators/run_all.py
--baseline-check` and blocks if any rule's candidate count INCREASED vs
`validators/.baseline.json`.

When a regression is detected, either fix the new violations or update the
baseline if the increase is intentional:

```bash
PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --update-baseline
```

### `commit-msg` — content-aware canon-extension gate

Calls `validators/check_canon_extensions.py` with the proposed commit
message. Detects canon extensions matching §6.5 mandatory-audit triggers:

- New rule subsection (e.g. `### 3.18 New Rule`)
- New merge-override (e.g. `#### M5. ...`)
- New non-§10 `### ` heading (loosened from Tanakh's literal-date pattern)
- New §6.5 trigger entry
- New SCOPE-exclusion bullet
- New Layer 1 table row (`REQUIRED-MERGE` / `REQUIRED-BREAK` / `PERMITTED-EITHER`)

Blocks the commit unless the message contains either:

- An audit-evidence keyword: `audit`, `hostile audit`, `audit dispatched`,
  `trigger #`, `§6.5`, `§10 update log`, `post-codification`,
  `post-detection`, `corpus-fit`, `retract`, `stan-authorized`, or
  `stan-direct`.
- A skip-safe claim: `typo fix`, `formatting`, `internal formatting`,
  `defensibility-capture`, `cross-reference update`, `audit-skippable`, or
  `skip-safe`.

### Installation (one-time)

```bash
cp validators/hooks/pre-commit .git/hooks/pre-commit
cp validators/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/pre-commit .git/hooks/commit-msg
```

### Bypass

For Stan-authorized commits that must skip the gates explicitly:

```bash
git commit --no-verify -m '...'
```

## Cross-project provenance

The hook architecture and `check_canon_extensions.py` were ported from the
sibling Tanakh-reader project on 2026-04-26 after a three-audit cross-project
review (canon §10 entry "2026-04-26 (later) — Mechanical hook port from
Tanakh"). BofM-reader landed similar gating earlier; Tanakh built and
operated it productively; GNT followed.
