# Bulk-migration design questions + navigability follow-on

## Context

M4-GNT-1 worked-example migration committed at `708feeef`. Three bulk-migration design questions block migrating the remaining ~20 §5 rules. Plus two follow-on items not in the original M4-GNT-1 paste: alignment-script protocol update + scripts/README survey.

## Items

1. **§3.7 cluster (R12/R13/R14/R28) — split vs grouped.** Stan recommends SPLIT into per-rule §3.x entries. Reasoning: the template is per-rule by design; grouping makes audit harder and complicates the alignment script's per-rule expectations. Default to split. If any one of the four rules genuinely doesn't split cleanly (semantic interdependence so tight that splitting degrades meaning), surface that specific rule for Stan review before proceeding; otherwise proceed.

2. **Principle entry kind — force template vs add new kind.** Stan recommends ADD a "Principle" entry kind to canon §3 quick-reference. Reasoning: R27 and R28 aren't per-line rules — they're principles that inform other rules. Forcing them into the per-line-rule template with n/a fields is formal-conformance over substantive-fit. Adding "Principle" as an entry kind acknowledges the genuine type difference. Per change-protocol.md §7.3 trigger #9 (meta-rule change), commit-message audit-evidence is required for the meta-template change.

3. **Layer 1 rules (R2-R7) — full entries vs redirect.** Stan recommends keep REDIRECT with clarifying note. Reasoning: L1 rules are universal-grammatical-floor in framework.md §1.2, not corpus-specific editorial methodology. Full template entries would duplicate framework material; redirect + a clarifying note ("the L1 floor lives at framework.md §1.2; GNT's L1 vetoes are the universal set") respects the framework-canon division.

4. **Alignment-script protocol update.** Tanakh's implementation surfaced two search-scope blind spots, codified at `atu-method/docs/canon-validator-alignment-protocol.md` (commit `49ee753`). Apply both fixes to GNT's alignment script: (a) search `validators/_shared/` in addition to named-detector files; (b) parse inline-prose detector references in addition to YAML list-form `detectors:` fields. Re-run after; report any verdict-count changes (probably no change since GNT mostly uses YAML, but worth verifying).

5. **scripts/README survey.** The 17 scripts in `scripts/` lack a folder-level README explaining which are active pipeline tools vs archival/diagnostic. Survey them; categorize: active pipeline (regular use) vs archival/diagnostic/one-off (candidates for `scripts/archive/`, which already exists with 8 entries). Propose categorization for Stan review BEFORE writing `scripts/README.md`.

## Reporting

Per item: completed (commit hash) / proposed-for-Stan-review / blocked (reason).

For #1, #2, #3: after the directive is reviewed and triggered, implement and commit the bulk migration starting with whatever rules naturally come first under each decision. Surface any rule-specific divergences from the default pattern as you go.

For #4: implement autonomously; report verdict changes.

For #5: propose categorization for Stan review BEFORE writing the README.

## Audit triggers

Item #2 (adding Principle entry kind) trips §7.3 trigger #9 (meta-rule change to change protocol itself). Commit-message audit-evidence required. Items #1, #3 are rule-derivative migrations of existing canon content; audit-skippable per §7.4 (formatting cleanup; no rule scope change). Item #4 is tooling improvement; audit-skippable. Item #5 is navigability infrastructure; audit-skippable.
