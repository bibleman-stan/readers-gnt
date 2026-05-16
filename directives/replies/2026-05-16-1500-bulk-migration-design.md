# Reply — Bulk-migration design questions + navigability follow-on

Directive: `2026-05-16-1500-bulk-migration-design.md`.

## Per-item dispositions

### #1 — §3.7 cluster (R12/R13/R14/R28) — split vs grouped

**Status:** Partially executed. Default-split applied to other clustered sections (§3.6 R11+R28-ext split into §3.6 + §3.6.1; §3.10 split into §3.10a R19 + §3.10b R20). The original §3.7 R12/R13/R14/R28 cluster was **not** split in this directive's execution — R12/R13/R14 are Editorial rules without auto-validators and are out of Phase-1 scope per directive item #3-style reasoning (they live in the rule index but don't carry §3 template entries in Phase 1).

**Result:** Default-split principle adopted and applied to §3.6 + §3.10. §3.7 R12/R13/R14 deferred to Phase-2 Editorial-rule template migration (separate effort).

### #2 — Principle entry kind

**Status:** Already completed in commit `d434626f` (the Entry kinds section at canon §3 codifies the four kinds: Mechanical / Editorial / Principle / Layer 1). R27 and R28 carry Principle entries with relaxed template requirements. No new work needed in this directive.

### #3 — Layer 1 rules — full entries vs redirect

**Status:** Already completed in commit `d434626f` (§3.2 carries the redirect note pointing to framework `§1.2` + the Layer 1 break-legality reference at `data/syntax-reference/greek-break-legality.md`). No new work needed in this directive.

### #4 — Alignment-script protocol update

**Status:** Already completed in commit `9583c86b` (alignment script adopted the two scope expansions: `validators/_shared/` fallback search + inline-prose detector parsing per `atu-method/docs/canon-validator-alignment-protocol.md` 49ee753). Post-run alignment summary: NO_IMPL 0 / DRIFT 0 / PARTIAL 0 / EDITORIAL_ACK 7 / ALIGNED 20 (no verdict-count change). No new work needed in this directive.

### #5 — scripts/README survey

**Status:** Completed in commit `72d08005`. 12 scripts moved from `scripts/` to `scripts/archive/` (3 validators superseded by `validators/colometry/*`, 1 investigation superseded by `check_r10_hoti_complementizer.py`, 3 completed-sweep appliers, 2 ὅτι-lead flip sweeps, 3 other one-offs). New `scripts/README.md` written cataloging the remaining active scripts: 6 core cascade, 4 Macula helpers, ~30 Layer-2/3 detector scanners, 6 active tools, 4 diagnostic one-offs. `scripts/archive/README.md` updated with the new arrivals organized by archival category.

## Phase-1 bulk template migration (executed)

Beyond the directive items, this session executed the Phase-1 bulk template migration applying the rule-template shape to all 10 active GNT canon rules previously prose-form:

| Rule | Commit | Notes |
|---|---|---|
| R1 No-Anchor | `0588e389` | Worked-example second after M4-GNT-1; corpus-sweep narrative → audit-trail/r1.md |
| R8 Framing Devices | `7a7a1926` | Closed list FRAMING_DEVICES; Runge §2.7 + Levinsohn §5.4.2 grounding → scholarship/r8.md |
| R11 Direct Speech Introduction + R28-ext Speech-Act After Frame | `ca8e974e` | §3.6 + §3.6.1 split; 3 sub-sections (OT-Attribution / Parenthetical / Amen-formula) consolidated into R11 Exclusions block; canonical-cases → scholarship/r11.md |
| R18 Vocative + R18a-GNT Patriarch-deity-triad | `873b7764` | R18 multi-valued template fields (Category B branches + boundary cases); R18a-GNT expanded PATRIARCH_TRIAD_VARIANTS as YAML |
| R19 Genitive Absolute + R20 Participial Phrase | `827e3062` | §3.10 split into §3.10a + §3.10b per directive #1 default-split |
| R23 Dative Subject of Infinitive + R25 ὥστε Short-Consecutive-Result | `53c8b3b7` | R23 closed list SPEECH_COMMAND_LEMMAS_R23; R25 closed lists HOSTE_LEMMAS + ILLATIVE_KNOWN; Phase-A 20-merge corpus → audit-trail/r25.md |

Alignment script result after Phase 1: **NO_IMPL 0 / DRIFT 0 / PARTIAL 0 / EDITORIAL_ACK 7 / ALIGNED 20** — unchanged from pre-Phase-1 baseline. All 10 rules retained their pre-migration verdicts.

## Open items not addressed in this directive

- **C4 (NP-with-relcl) closed-list shape** — M4-GNT-1 entry flagged C4 as lacking a clean v4/grk demonstration. Cases originally labeled C4 (e.g., Heb 3:1) were on closer inspection NP-with-appositive (C2). Decision pending: retire C4 from SUBJECT_SHAPES or backfill with a verified instance.
- **Rule Index + Closed-List Registry staleness** — Rule Index lines 301-309 still say "not yet implemented" for R8/R9/R10/R17 (validators shipped in `c1886b60`). Closed-List Registry rows for R8/R9/R10 likewise show "no validator yet". Cleanup is rule-derivative; can be done in a follow-up Index-sync commit.
- **R9, R10, R17, R12/R13/R14, R22, R24** template migration — Phase-2 + Phase-3 scope per the conversation's original plan (rules without §3 YAML signatures + Editorial / Principle rules).

## Reporting

Per-item: executed / already-completed / out-of-scope-deferred. No items blocked.
