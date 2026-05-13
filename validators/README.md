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

Triggers when staged files include the canon, syntax-reference, v4/grk
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

## Detector precedence discipline

Per canon §3 "Pairwise Precedence Catalogue" + architecture.md §interface-contracts: *"Detectors must filter candidates that match higher-tier rules out of lower-tier buckets."*

The GNT validator suite enforces precedence at the **per-detector** level — each lower-priority detector contains yield-checks that skip emissions when a higher-priority rule's signature matches the same locus. There is no runner-level precedence pass (currently `run_all.py` iterates validators in alphabetical order).

### Gold-standard implementation pattern

`validators/colometry/check_m4_gnt_1_subject_orphan.py` is the reference for tier-yield discipline. It documents 5 G-exclusions + 6 universal exclusions, each explicitly commenting which higher-priority rule governs at the yield point:

```python
# G3: Periphrastic-construction line B → R5 governs
# G4: Doxological vocative-NP + infinitival-complement → R7 governs
# Universal #11: R19 genitive-absolute on line B → R19 governs
```

When implementing a new detector at Layer 3 (`validators/colometry/`), follow this pattern: list every higher-priority rule the new detector might overlap with, add an exclusion check for each, comment which rule governs at the yield point.

### Known detector tier-yield gaps (audit 2026-05-13)

The canon §3 Pairwise Precedence Catalogue documents these gaps explicitly. Closing them is engineering work that surfaces when the corpus baseline regresses (currently all three detectors emit 0 candidates against v4/grk, so the gaps are theoretical-only).

- **`check_r19_genabs.py`** — `_KNOWN_FP_ALLOWLIST` (5 entries) is a symptom-patch for attributive-participle false-positives. The audit-named class-based fix is widening Class B's adjacency window + adding inter-line NP awareness (the file's own comment says so). The audit-named "yield to R7/R6" framing doesn't actually match the 5 FPs — they're attributive-ptc disambiguation cases, not vocative/fixed-phrase yields. Don't blindly implement "skip if R7 fires" — investigate the actual class first.
- **`check_r18_vocative.py`** — silent on R7-yield. When a multi-word vocative is split across lines (R7 MALFORMED territory), R18 could false-positively fire on the line-2 fragment seeing it as "vocative + finite verb + no 2p element." R7 fix (re-merge the split unit) will eliminate the apparent R18 violation; R18 should defer.
- **`validators/run_all.py`** — alphabetical iteration; no runner-level precedence. With ~13 implemented detectors and the per-detector yield pattern above, runner-level ordering is not critical yet. Revisit when detector count grows or when a future detector cannot enforce its own yields internally.

### When to add a yield check

If a new candidate emission would fire on a locus where:
- Layer 1 (R2–R7) already prohibits the relevant break → yield
- A higher-tier formula-integrity rule (R6, R11, R18a-GNT) governs the span → yield
- A complement-integrity rule (M2, R10) governs → yield
- A merge-override (M1, M3, M4, M4-GNT-1) is the proper resolution → yield

Reference the canon Pairwise Precedence Catalogue for the authoritative list of stated precedences.

## Cross-project provenance

The hook architecture and `check_canon_extensions.py` were ported from the
sibling Tanakh-reader project on 2026-04-26 after a three-audit cross-project
review (canon §10 entry "2026-04-26 (later) — Mechanical hook port from
Tanakh"). BofM-reader landed similar gating earlier; Tanakh built and
operated it productively; GNT followed.
