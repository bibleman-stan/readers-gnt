# Reply — C4 retirement + Rule Index / Closed-List Registry cleanup

Directive: `2026-05-16-2205-c4-and-index-cleanup.md`.

## Commit

Single bundled commit — all three items are mechanical cleanup against the same canon file with no rule-scope change; splitting into three commits would be more overhead than warranted.

## Per-item status

### Item 1 — C4 retirement: **completed (default path: retired)**

**Backfill check.** No verified v4/grk instance of NP-with-relative-clause as subject found. Searched M4-GNT-1's documented clusters (household-code, biographical-intro, deity-NP-with-appositive) — all are C1 / C2 / C5 / C3. Heb 3:1 was explicitly identified as C2 (NP-with-appositive) on prior audit. Defaulted to retirement.

**Downstream consumer check.** `validators/colometry/check_m4_gnt_1_subject_orphan.py` does NOT depend on C4 — the validator implements subject-shape detection inline rather than via named C1–C5 constants (per the comment block at `validators/canon/check_canon_alignment.py:356-363`). Only mention of C4 in validator code was an inline comment in the alignment script's RULES metadata. Retiring C4 from canon has zero behavioral impact on the validator.

**Canon edits applied:**
- §3.18 SUBJECT_SHAPES YAML: `C4_np_with_relcl` line commented out with retirement marker.
- §3.18 Examples-block trailing note: replaced the "flagged for follow-up audit" sentence with the canonical retirement note per the directive template:
  > *C4 (NP-with-relcl) retired 2026-05-16: no clean v4/grk demonstration; cases originally labeled C4 (e.g., Heb 3:1) are NP-with-appositive (C2). License to re-add if a verified C4 instance surfaces in v4/grk. SUBJECT_SHAPES active membership: C1, C2, C3, C5.*
- §3 Closed-List Registry M4-GNT-1 SUBJECT_SHAPES row: members list updated to omit C4 with inline retirement cross-reference.

### Item 2 — Rule Index update: **completed**

Lines 301–309 four rows updated from `*(not yet implemented)*` to actual validator paths shipped in commit `c1886b60` (and `0a7cfb36` for R17 narrowing):

Before / after:

```
| R8 | … | Mechanical | 3.3 | *(not yet implemented)*                              |  →  | R8  | … | Mechanical | 3.3 | `validators/syntax/check_r8_framing_devices.py`     |
| R9 | … | Mechanical | 3.4 | *(not yet implemented)*                              |  →  | R9  | … | Mechanical | 3.4 | `validators/syntax/check_r9_subordinate_clause.py`  |
| R10| … | Mechanical | 3.5 | *(not yet implemented)*                              |  →  | R10 | … | Mechanical | 3.5 | `validators/colometry/check_r10_hoti_complementizer.py` |
| R17| … | Mechanical | 3.8 | *(not yet implemented)*                              |  →  | R17 | … | Mechanical | 3.8 | `validators/colometry/check_r17_de_contrast_overbreak.py` |
```

Format matches the other implemented-rule rows.

### Item 3 — Closed-List Registry update: **completed**

Four R8/R9/R10 rows updated from `*(no validator yet …)*` to actual validator paths:

Before / after:

```
| **R8 framing devices**                       | … | §3.3 table | *(no validator yet — manual editorial)* |  →  | … | `validators/syntax/check_r8_framing_devices.py`        |
| **R9 subordinate-clause openers**            | … | §3.4       | *(no validator yet)*                    |  →  | … | `validators/syntax/check_r9_subordinate_clause.py`     |
| **R10 cognition / perception / belief verbs**| … | §3.5       | *(no validator yet)*                    |  →  | … | `validators/colometry/check_r10_hoti_complementizer.py`|
| **R10 declaration / speech / writing verbs** | … | §3.5       | *(no validator yet)*                    |  →  | … | `validators/colometry/check_r10_hoti_complementizer.py`|
```

R17 has no Closed-List Registry row (rule keys on surface-pattern article + δέ pivot heads enumerated inline in §3.8) — "if applicable" → not applicable, no edit.

The R10 "speech-intro frame class" row was already pointing at `check_r11_speech_intro.py` (ἀπεκρίθη special case lives in R11 family per canon §3.5) and is unchanged.

## Alignment-script verification

Post-cleanup: **NO_IMPL 0 / DRIFT 0 / PARTIAL 0 / EDITORIAL_ACK 7 / ALIGNED 20** — unchanged from pre-cleanup baseline. The script reads the alignment RULES table directly from `check_canon_alignment.py`, which already encoded the actual validator paths; this cleanup brings canon prose into agreement with what the script was already checking.

## Surfaced concerns

None. All three items were narrow mechanical edits with no rule scope change, no closed-list extension, no new rule. Audit-skippable per change-protocol §7.4 as the directive declared.
