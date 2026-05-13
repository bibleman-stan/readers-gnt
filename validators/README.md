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

- **`check_r19_genabs.py`** — `_KNOWN_FP_ALLOWLIST` (5 entries) is a symptom-patch for attributive-participle false-positives. The 2026-05-13 pass added Class B check 4 catching heb 11:1 as class-based; 4 entries remain (john 7:38, 2cor 6:16, matt 9:10, phil 2:15). Each remaining entry has its target class-fix documented in the file's inline comment (widen-window / inter-line-NP / ἐγένετο-formula). The audit-named "yield to R7/R6" framing doesn't match the actual FPs — they're attributive-ptc disambiguation cases.
- **`check_r18_vocative.py`** — R7-yield short-circuit added 2026-05-13 (defensive against future edits; current baseline unchanged).
- **`validators/run_all.py`** — alphabetical iteration; no runner-level precedence. With ~13 implemented detectors and the per-detector yield pattern above, runner-level ordering is not critical yet. Revisit when detector count grows or when a future detector cannot enforce its own yields internally.

### Known alignment-algorithm gaps (atu-method shared infrastructure)

These are bugs in the Pass C / Pass B / etc. alignment-distribution logic at `atu-method/atu_method/kjv_alignment/distribute.py`, not in GNT-local detectors. The fixes are cross-corpus (any change benefits bofm/tanakh/GNT). Documented here so future-Claude doesn't attempt GNT-side workarounds before the shared rewrite ships.

- **Matt 18:8 "thee, thee:" duplication** (named in Audit 3 of session 2026-05-13). KJV `cast them from thee:` distributes to GNT lines as: line 0 gets `Wherefore if thy hand or thy foot offend thee, thee:` (extra `thee:` pulled backward), line 1 gets `cut them off, and cast them from` (missing `thee:`). Root cause: Pass C `_should_force_backward` closed-list (`_OBJECT_PRONOUNS` + `_TRAILING_PREPOSITIONS`) heuristically forces `from` and `thee` backward — but the backward-attachment picks line 0's last anchor (closer by vpos) over line 1's vpos-range (which structurally owns `ἀπὸ σοῦ`). The closed-list substitutes surface form for Macula constituent structure. **Same architectural failure as tanakh's Pass-C closed-list** that Stan is replacing with a Macula-driven (Macula Greek for GNT) version. Fix awaits the cross-corpus rewrite; GNT will inherit automatically since `atu-method` is shared infrastructure.

- **Matt 21:3 ἐρεῖτε empty line** (named in session 2026-05-13 final state). Pass A1 rarity-sort processes G3754 (ὅτι recitative, src on line 2, rarity 2) before G2046 (say-verb, src on lines 0+1 via equivalents, rarity 3). G3754 claims vpos 10 ("say" — multi-Strong KJV word with G2046+G3754 tags), suppressing G2046's claim from line 1's ἐρεῖτε. Fix shape: prefer claiming via the kjv word's *primary* (first-listed) Strong's tag when contests arise. Not yet implemented — primary-tag salience is not always semantically primary (Luke 22:49 `Lord` has G1487 listed before G2962 despite κύριος being the obvious semantic match), so the heuristic needs care.

- **Cross-verse-boundary alignment (50 verses; `data/eng-kjv-coverage.baseline.json`).** SBLGNT places certain Greek tokens in verse V whose semantic content KJV places in verse V±1. Canonical instances: Acts 5:39 (last two grk lines `ἐπείσθησαν δὲ αὐτῷ` are KJV 5:40 content); Eph 5:14 (grk line 0 `πᾶν γὰρ τὸ φανερούμενον φῶς ἐστιν` is KJV 5:13 content); Matt 14:27 (grk line 3 `μὴ φοβεῖσθε` belongs to a KJV line that runs into 14:28 framing). Currently `align_verse(book, ch, vs, ...)` is *strictly intra-verse* — it pulls KJV from `MetaV[(book, ch, vs)]` only. Greek source lines whose KJV content lives in V±1 receive blank English.

  **Design sketch (cross-verse extension).** Three components:

  1. **Boundary-mismatch index.** Pre-compute, per (book, ch, vs), whether any source-line's lemma signatures match KJV words in V-1 or V+1 better than in V. Use TAGNT (source-side) + MetaV (KJV-side) Strong's. A line is a "cross-verse spillover candidate" when its source lemmas have ZERO Strong's matches in MetaV[V] but ≥1 match in MetaV[V±1]. Output: `{(book, ch, vs, line_idx) → (target_verse, confidence)}` table cached at `data/cross-verse-spillover.json`.

  2. **align_verse extension.** Take an optional `neighbor_kjv: dict[(book,ch,vs) → list[KjvWord]]` parameter. When a source line is in the spillover index AND its target_verse is provided in `neighbor_kjv`, allow Pass A1 / Pass B / Pass C to draw from the neighbor verse's KJV pool. Mark spillover-claimed words in output for downstream verification (e.g., a `provenance` field on the returned line indicating "drawn from V+1 vpos 3").

  3. **regenerate_english.py wiring.** When processing chapter N, load MetaV for the full chapter once and pass each verse's `align_verse` call a neighbor map containing the prior + next verse's KJV. Cross-chapter boundaries (verse 1 of chapter N drawing from verse last of chapter N-1) handled by a chapter-pair load.

  **Engineering cost estimate.** Substantial — multi-session work. Three reasons: (a) `align_verse`'s internal logic assumes per-verse claim accounting and would need to track cross-verse claims to avoid double-claiming; (b) the spillover index needs corpus-wide calibration (50 verses is the visible-failure count; true-positive cross-verse cases might be 200+, and false-positives would silently move correct KJV to wrong lines); (c) needs cross-corpus consideration since `atu-method/atu_method/kjv_alignment/` is shared infrastructure — bofm/tanakh would inherit.

  **Recommended sequence** (when this work is prioritized):
  1. Investigation pass: scan corpus-wide for source-line spillover candidates beyond the 50 baseline entries; quantify true-positive vs false-positive rate.
  2. Adversarial audit dispatch (≥2 parallel) on the proposed `align_verse` extension before any code.
  3. Spillover index + `align_verse` extension implemented in `atu-method/atu_method/kjv_alignment/cross_verse.py` (new module) — preserves the strictly-intra-verse `align_verse` as an importable API for callers that don't want spillover.
  4. `regenerate_english.py` opt-in via flag (`--cross-verse`) initially; promote to default after corpus verification.
  5. Three-check verification + baseline update of `eng-kjv-coverage.baseline.json` (the 50 entries should shrink toward 0 as spillover catches them).

  **Cross-corpus consideration.** Tanakh likely has analogous SBLGNT-vs-KJV-versification-style mismatches (BHS vs KJV-OT versification differs in some psalms and elsewhere). bofm has no analog (single English source). If the cross-verse extension lands, design it as a corpus-agnostic mechanism — caller passes `neighbor_kjv`, library handles distribution.

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
