# Reply — Cross-corpus alignment Pass D — Phase 1 audit, STOP-gate triggered

Directive: `2026-05-16-2400-cross-corpus-alignment-pass-d.md`.

## Phase 1 — Adversarial audit verdict: **NEEDS-MODIFICATION (both agents)**

Two parallel Opus agents dispatched per directive Phase 1 requirements + CLAUDE.md / 2203 precedent. Both returned independently: **VERDICT: NEEDS-MODIFICATION** with concrete must-fix findings before any code touches `atu_method/kjv_alignment/distribute.py`.

Per directive: *"If audit surfaces must-fix findings: STOP and surface specifics for Stan-review per 2203 STOP-gate protocol. Do NOT implement based on audit-flagged design."* — Phase 2 implementation blocked pending Stan response.

## Cross-agent agreement on must-fix modifications

### M1 — Rule 1 closed-list discipline + explicit `_TRAILING_COMPLEMENT` precedence (BOTH AGENTS)

The directive's prose says "unanchored pronoun (it/he/she/they/we/ye/you/I/...)". The trailing `/...` is dangerous — Pass C's existing `_TRAILING_COMPLEMENT` closed list at `distribute.py:103-113` enumerates `him, her, it, them, me, us, thee, you` as forced-BACKWARD-attach object pronouns. The overlap on `it`, `you` is intentional (subj/obj ambiguous); divergence on `him, her, them, me, us, thee` is also intentional (obj-only).

**Required:** Rule 1's pronoun closed list MUST be exactly `{it, he, she, they, we, ye, you, I, thou}` — hardcoded. Never widen by lazy extension. The implementation must also state explicit precedence vs `_TRAILING_COMPLEMENT`: when `_TRAILING_COMPLEMENT` would fire on a subject-pronoun candidate AND Rule 1's pre-condition holds (line N+1 starts with finite verb / aux + participle), Pass C SUPPRESSES the backward bind so Pass D's forward bind fires.

**Counter-example from corpus:** Matt 6:26 `your heavenly Father feedeth them.` / `Are ye not much better than they?` — `them` is the obj of `feedeth` on line N; moving forward to line N+1 (new interrogative with its own subject "ye") would be a real regression. Without the closed-list discipline, the rule misfires.

### M2 — Sentence-boundary punctuation must gate Rule 1 symmetrically with Pass C (AGENT B)

Pass C already gates italic attachment on `.` / `!` / `?` / `;` / `:` via `_SENTENCE_PUNCT` (line 93) and `_has_sentence_boundary_between` (line 199). The directive's Rule 1 wording "no sentence-boundary punctuation separates them" expresses this in prose; the implementation must literally reuse `_has_sentence_boundary_between` for consistency, not roll a parallel check.

**Concrete risk:** Matt 6:26's `.` after `them` (and Mark 7:18, Mark 11:22 interrogative-pivot cases) would mis-fire without this gate.

### M3 — Rule 2 surface heuristic is insufficient; structured-layer / MorphGNT check required (BOTH AGENTS)

This is the strongest finding from both agents and aligns with CLAUDE.md's anti-pattern flag.

**Agent A:** "Rule 2 must use a MorphGNT-side check on the SOURCE-LANGUAGE token aligned to the candidate participle — if the Greek anchor is a finite indicative, do not migrate the auxiliary (the Greek already has its own verb). Only fire when the Greek anchor is a participle / passive-participle / periphrastic-eligible form."

**Agent B:** "The right approach per CLAUDE.md 'Use the structured layer FIRST' is option (c) from the dispatch brief: lean on the Greek source side. Implementation must reach into `validators/_shared/morphgnt_lookup.py` (GNT) and the equivalent Hebrew morph layer (Tanakh) at apply-time, not key off English surface suffixes."

**Quantitative evidence (Agent B):** Corpus surface-scan finds only **16 verses** where `aux` ends line N AND `verbish-suffix` opens line N+1 — but the diagnostic flagged **176 aux-stranded cases** via spaCy UD. A naive surface suffix check (`-ed/-en/-ing`) would miss high-frequency irregulars (`done`, `come`, `gone`, `seen`, `known`, `taken`, `given`, `written`, `said`, `made`, `cast`, `set`, `put`, `cut`, `hit`, `read`) AND false-positive on adjectives (`good`, `dead`, `red`, `wicked`) and nouns (`bed`, `seed`, `friend`). The 16-vs-176 delta shows surface-heuristic detection would miss ~90% of true positives AND admit shape-only false-positives.

This is the same `_TRAILING_COMPLEMENT` closed-list anti-pattern CLAUDE.md flags as the cross-repo failure-mode evidence — repeating it on Rule 2 would be the second-occurrence engine-level smell that should be designed out, not coded in.

**Required:** Rule 2's "line N+1 starts with a participle" check MUST be a MorphGNT/source-side POS check, not an English-surface suffix or word-shape heuristic.

### M4 — Pass D requires a FIXPOINT iteration, not a single-pass scan (AGENT B)

Pass D needs a fixpoint loop because Rule 2's precondition (line N+1 starts with participle) depends on whether Rule 1 has fired (which moves the pronoun out of line N). Mark 4:6 demonstrates: Rule 1 fires on "it" first (line-N-final); after migration, "was" becomes the new line-N-final word; Rule 2 must then re-scan the updated state.

**Required:** Apply Rules 1 + 2 in a fixpoint loop — keep applying until no migrations happen in a sweep. Bound iterations (≤3 or ≤5) to detect oscillation.

### M5 — Rule 1 must suppress on fronted-emphasis intensifiers (AGENT A)

When the IMMEDIATELY-preceding token on line N is an adverbial intensifier (`thus` / `so` / `even` / `also` / `then`), the pronoun forms a fronted-emphasis frame with the intensifier and should not migrate.

**Concrete case:** Matt 3:15 line 2 `Suffer it to be so now: for thus it` / `becometh us to fulfil all righteousness.` — moving `it` forward yields `for thus` / `it becometh us` — stranding `thus` from its head and breaking the fronted-emphasis unit (canon §1 honoring-Greek-marks principle).

**Required:** Rule 1 pre-condition tightening — require that the IMMEDIATELY-preceding token on line N is NOT in `{thus, so, even, also, then}`. If it is, suppress the rule.

### M6 — Rule 3 (came-to-pass) must accept verb-form variants (AGENT B)

Tanakh corpus shows the FEF surface has 6 attested variants:

| Surface | Count |
|---|---:|
| `and it came to pass` | 337 |
| `and it shall come to pass` | 98 |
| `it came to pass` | 47 |
| `it shall come to pass` | 17 |
| `and it cometh to pass` | 1 |
| `it is come to pass` | 1 |
| **Total** | **501** |

Only 337 (67%) match a literal 5-token "and it came to pass". The other 164 cases use variant verb forms.

**Required:** Rule 3 pattern must be `(and )?it (came|shall come|cometh|is come) to pass` — anchored by `it ... to pass` with verb-slot variants. Otherwise ~170 verses with valid FEF apodosis/protasis structure go un-clustered.

### M7 — Rule 3 must respect Tanakh H16 deliberate splits (AGENT A)

Tanakh canon H16 deliberately keeps `וַיְהִי` separate from its temporal clause in some configurations. Rule 3 as stated ("if any token is mis-attached AND the others are on the FEF protasis line, move stragglers to join the cluster") would re-attach what an editor explicitly split.

**Required:** Rule 3 must skip when source `וַיְהִי` is alone on its editorial line — that's the H16 deliberate-split signature. The cluster-bind fires only when the editor has not asserted a deliberate split.

### M8 — Rule precedence: Rule 3 fires BEFORE Rule 1 in Tanakh (AGENT A)

In Tanakh `וַיְהִי X־` "and-it-came-to-pass X" cases, the literal `it` of "and it came to pass" is part of the formula. If Rule 1 fires first, it would move the `it` OUT of the formula before Rule 3 can cluster-bind. Rule 3 must run first (or Rule 1 must include a suppression for `it` adjacent to `came`/`pass` in came-to-pass formula context).

**Required:** Rule precedence specification — Rule 3 runs before Rule 1 (Tanakh path), OR Rule 1 includes a Tanakh-side suppression check for came-to-pass-formula adjacency.

## Findings where rules ARE sound (no modification needed)

### Conjunction false-positive risk — well-handled by closed-list (BOTH AGENTS)

Rule 1's closed list (`it / he / she / they / we / ye / you / I`) does not contain `and` / `but` / `or`. Rule 2's list (`was / were / is / are / am / be / has / have / had`) likewise excludes conjunctions. The conjunction risk is structurally avoided. The Tanakh 21,790-count vav-conjunctive false-positive cluster is correctly out of scope per the directive. 211 line-final "and" cases in eng-kjv are untouched. **Safe as-designed once M1's closed-list discipline is enforced.**

### Validator-regression surface — minimal (BOTH AGENTS)

Survey results across both repos:
- **GNT validators** (`validators/colometry/check_*.py` — m4_gnt_1, r10, r11, r17, r18, r19, r25, r28; `validators/syntax/check_r{8,9,...}.py`): NONE read v4/eng-kjv content. All are Greek-side (MorphGNT / Macula / v4/grk). Pass D output changes do NOT propagate into validator baselines.
- **`scripts/scan_english_drift.py`** (pre-commit Phase 2): ALREADY flags `AUX-VERB-SPLIT` / `DANGLING-AUX` / `DANGLING-PREP` on the Mk-4:6 shape. Pass D would REDUCE drift-scanner hits, not increase them. Baseline delta would be negative (improvement, allowed under `--update-baseline`). NOT a regression.
- **`scripts/scan_eng_kjv_coverage.py --baseline-check`** (pre-commit Phase 2): keys on line-count parity and per-line content presence — Pass D doesn't change line counts or create blanks. Unaffected.
- **Tanakh validators** referencing eng-output: 4-layer-integrity / doc-pointer / canon-retirement-residue checks — none key on per-line English token distribution. Validator regression surface is minimal.

### Mk 4:6 walk-through — works correctly with M4 fixpoint loop (AGENT B)

With M4 fixpoint iteration in place:
- Iteration 1: Rule 1 fires on "it" (line-N-final, line N+1 starts with verb-like sequence) → moves to line 1
- Iteration 2: Line 0 now ends `was`; Rule 2 fires (line N+1 starts with participle `scorched`) → moves "was" to line 1
- Iteration 3: No migrations; fixpoint reached
- Result: line 0 = `But when the sun was up,`; line 1 = `it was scorched;` — correct.

## Revised quantitative estimate after modifications

Both agents agree the diagnostic's headline counts (272 pronoun + 176 aux) are over-estimates of safe-to-fire cases once M1, M3, M5 suppressions apply:

- Pronoun forward-bind: 272 → ~220 (after M5 fronted-emphasis suppression + M2 sentence-boundary gate)
- Auxiliary forward-bind: 176 → ~120-150 (after M3 MorphGNT structural gate)
- Tanakh came-to-pass: 1,490 → ~1,400+ (after M6 variants expansion, may go UP)
- Tanakh O-vocative: 443 → ~430 (after exclusion of `O that ...` non-vocative cases)

Net expected GNT Pass D mechanical-yield: **~340–370 cases** (vs the directive's 450 estimate). Still substantial; still the right intervention. Just with tighter rules.

## STOP-gate disposition

Phase 1 audit completed per directive specification. Both Opus agents independently returned NEEDS-MODIFICATION with concrete must-fix lists (M1–M8 above; M1–M3 are STRONG consensus across both agents). Phase 2 implementation HALTED per directive STOP-gate protocol.

Phase 3 (residue measurement) blocked downstream of Phase 2.

## Cross-repo coordination

Tanakh-Claude has NOT been triggered for any parallel atu_method work (per directive's coordination note). The atu_method package is unchanged. Tanakh-side validator baselines are unaffected. No cross-repo notification needed at this stage.

When Stan responds with a modified rule spec (either by editing the original directive or issuing a new one), this reply's revised-quantitative-estimate gives a baseline expectation for the post-modification yield.

## Surfaced concerns

1. **CLAUDE.md "structured layer FIRST" anti-pattern at risk** — M3 is the most important finding. If Rule 2 ships with English-surface suffix detection rather than MorphGNT POS check, this would be the third documented recurrence of the same anti-pattern (cross-repo, BoFM-side `_OBJECT_PRONOUNS` precedent + GNT-side `_ARTICLE_FORMS` precedent + this would be the third). The fix is straightforward; the discipline matters.

2. **Tanakh-specific Rules 3 + 4 carry more design risk than the universal Rules 1 + 2** — Rules 3 + 4 interact with Tanakh's H16 canon directly (M7) and need verb-form variant handling (M6). If Stan prefers, the universal Rules 1 + 2 could land first (with M1–M5 modifications applied), Tanakh-specific Rules 3 + 4 could be deferred to a separate follow-on directive in readers-tanakh where Tanakh-Claude with its canon context handles the H16-aware design.

3. **No code written.** No commits to atu_method. No changes to v4/grk or v4/eng-kjv. No baseline mutations. Pure diagnostic + audit + Stan-surface.

## Per-item disposition

| # | Item | Status |
|---|---|---|
| 1 | Dispatch ≥2 parallel Opus agents | ✓ — 2 dispatched in single message, both completed |
| 2 | Phase 1 STOP-gate decision | ✓ — STOP triggered (both agents returned NEEDS-MODIFICATION) |
| 3 | Implementation in atu_method | BLOCKED — Phase 1 STOP-gate |
| 4 | Conjunction-stranded docstring note | DEFERRED — no atu_method edit yet |
| 5 | Run alignment fresh in both repos | BLOCKED |
| 6 | Mk 4:6 + 10-random spot-check | BLOCKED |
| 7 | Update consuming repos' baselines | BLOCKED |
| 8 | Phase 3 residue measurement | BLOCKED (downstream of Phase 2) |

Phase 1 completed; Phases 2 + 3 blocked pending Stan's response to the M1–M8 modification list. Recommended next step: Stan reviews M1–M8, either approves the revised rule spec (issue follow-on directive with modifications baked in) or pivots to a different intervention shape.
