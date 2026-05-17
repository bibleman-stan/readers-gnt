# C4 retirement + Rule Index / Closed-List Registry cleanup

## Context

The 1500-bulk-migration-design reply (`directives/replies/2026-05-16-1500-bulk-migration-design.md`) surfaced two open items needing cleanup:

1. **C4 (NP-with-relcl SUBJECT_SHAPE)** — flagged in the M4-GNT-1 entry as lacking a clean v4/grk demonstration. Cases originally labeled C4 (e.g., Heb 3:1) were on closer inspection NP-with-appositive (C2). Stan-decision: **retire C4** unless a verified instance can be backfilled.

2. **Rule Index + Closed-List Registry staleness** — Rule Index lines 301-309 and Closed-List Registry rows for R8 / R9 / R10 / R17 still say "not yet implemented" / "no validator yet" despite validators shipped in commit `c1886b60`.

Both are mechanical cleanup. Bundled because both are small enough that splitting would be more overhead than warranted.

## Items

### Item 1 — C4 retirement

1. **Backfill check first.** If you have a candidate v4/grk verse that's genuinely NP-with-relcl as the subject (NOT appositive — the relative-clause restricts the head NP rather than supplying a non-restrictive identifying clause), surface the citation BEFORE retiring. Default is retire; backfill only if a verified instance is in hand.

2. **If no backfill found** (default path): update the M4-GNT-1 entry to remove C4 from SUBJECT_SHAPES. Add an inline retirement note:

   > C4 (NP-with-relcl) retired 2026-05-16: no clean v4/grk demonstration; cases originally labeled C4 (e.g., Heb 3:1) are NP-with-appositive (C2). License to re-add if a verified C4 instance surfaces in v4/grk.

   Match the format used for any prior retirement notes in the canon.

3. **Cross-check downstream consumers** — if any validator, applier, or detector enumerates SUBJECT_SHAPES, confirm none depends on C4 being present. (Likely none, since C4 wasn't firing on real cases, but worth verifying.)

### Item 2 — Rule Index update

1. Lines 301-309: update R8 / R9 / R10 / R17 rows from "not yet implemented" to reflect the implementation in commit `c1886b60` (or current shipped state).

2. Match the format used for other implemented rules in the Index — same columns, same level of detail (validator filename, closed-list reference if applicable, etc.).

### Item 3 — Closed-List Registry update

1. Rows for R8 / R9 / R10 (and R17 if applicable): change "no validator yet" to point at the implementing validator + closed list.

2. Match the format used for other registered closed lists.

## Reporting

Reply at `directives/replies/2026-05-16-2205-c4-and-index-cleanup.md`:

- **C4 disposition**: backfill found (with citation) OR retired (default path). If retired: confirmation that no downstream consumer depends on C4.
- **Rule Index update**: commit hash + sample of before/after rows
- **Closed-List Registry update**: commit hash + sample of before/after rows
- Single commit OR bundled commit — your judgment, document the choice

## Audit triggers

Mechanical cleanup. No rule scope change. No new closed list. No new rule. Audit-skippable per §7.4.
