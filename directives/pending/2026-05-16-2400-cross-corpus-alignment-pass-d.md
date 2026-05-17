# Cross-corpus alignment Pass D — supplement-attachment fix at atu_method.kjv_alignment

## Context

Both 2300 alignment scans (GNT reply at `directives/replies/2026-05-16-2300-unanchored-alignment-scan.md`; Tanakh reply at `readers-tanakh/directives/replies/2026-05-16-2300-unanchored-alignment-scan.md`) confirm the same problem-class shape across corpora:

**Genuine high-confidence supplement-attachment failures (post vav-conjunctive-ATU-opener suppression):**

| Class | GNT volume | Tanakh volume |
|---|---:|---:|
| Pronoun-stranded (Mk 4:6 shape) | 272 | 1,405 |
| Auxiliary-stranded | 176 | ~3,500 |
| Came-to-pass cluster | n/a (NT) | 1,490 |
| O-vocative cluster | n/a (NT-rare) | 443 |

The conjunction-stranded category in both repos is dominated by line-leading "and" that UD parses as backward-coordinating but colometric convention licenses as ATU-opener — **NOT an alignment failure; do not "fix".**

The natural home for the fix is `atu_method.kjv_alignment` (the alignment module is shared by both consumers). Rules 1 + 2 are corpus-agnostic; Rules 3 + 4 are Tanakh-specific extensions.

This directive runs in GNT but the work lands in atu_method. After the atu_method update, both reader-repos pull the upgrade and rebuild.

**This trips §7.3 trigger #10 (discipline-shifting addition that shapes how the apparatus is operated) + adds a new mechanical-heuristic class. Per 2203 audit precedent, requires ≥2 parallel adversarial agents BEFORE implementation.**

## Items

### Phase 1 — Pre-build adversarial audit

1. **Dispatch ≥2 parallel Opus agents** against the proposed Pass D rules. Each agent receives:
   - Both 2300 reply files (GNT + Tanakh)
   - The proposed Pass D mechanical rules:
     - **Rule 1**: Unanchored subject pronoun forward-bind. When an unanchored pronoun is at line-N-final position AND the next non-empty ATU line N+1 starts with a finite verb (or auxiliary + finite verb) that has no explicit subject NP earlier in line N+1 AND no sentence-boundary punctuation separates them → move pronoun to line N+1.
     - **Rule 2**: Unanchored auxiliary forward-bind. When an unanchored auxiliary (was/were/is/are/am/be/has/have/had) is at line-N-final position AND line N+1 starts with a participle/past-participle form → move auxiliary to line N+1.
     - **Rule 3** (Tanakh-specific): Came-to-pass 5-token cluster bind. Treat `and it came to pass` as a 5-token frame; if any token is mis-attached AND the others are on the FEF protasis line, move stragglers to join the cluster.
     - **Rule 4** (Tanakh-specific): O-vocative cluster bind. Keep `O` with the vocative-NP on the same line.

   And probes for:
   - **False-positive risk** per rule: cases where forward-bind would actually be wrong (e.g., pronoun is genuinely a discourse marker on its own line; auxiliary is part of a relative-clause subject)
   - **Cross-rule interactions**: do Rules 1 + 2 compose cleanly when an unanchored aux + pronoun pair both want forward-binding?
   - **Cross-corpus generalization**: does Rule 1's heuristic work for both Greek and Hebrew source contexts, or does it need corpus-specific tightening?
   - **Cross-validator propagation**: 4+ validators consume the alignment output; will Pass D's re-attachment change validator outputs? Audit BoFM's validators if needed (BoFM doesn't consume this alignment but uses the same atu_method package surface)
   - **Conjunction false-positive risk**: Rule 1 + 2 should NOT touch conjunctions; confirm the implementation respects the vav-ATU-opener convention
   - **UD-parser fidelity assumptions**: Rule 1 + 2 rely on UD head identification; what happens when the parser is wrong?

2. **If audit clears (no must-fix findings)**: proceed to Phase 2. **If audit surfaces must-fix findings**: STOP and surface specifics for Stan-review per 2203 STOP-gate protocol. Do NOT implement based on audit-flagged design.

### Phase 2 — Implementation (only after Phase 1 clears)

3. **Implement Pass D in `atu_method/kjv_alignment/distribute.py`** (or wherever the alignment passes live). Rules 1 + 2 + 3 + 4 per Phase 1 specification. New code module: `Pass D — supplement forward-bind`.

4. **Conjunction-stranded suppression documented**, not implemented as code change — the existing alignment is correct; conjunction-stranded category is a false-positive at the colometric layer. Add docstring note in `atu_method/kjv_alignment/__init__.py` clarifying this.

5. **Run alignment fresh in BOTH repos**:
   - GNT: rebuild v4/eng-kjv alignment; capture before/after counts of unanchored mis-attachments (expected: ~450 mis-attachments resolved, dropping from 3,675 to ~3,225)
   - Tanakh: rebuild v2/eng alignment; capture before/after counts (expected: ~3,000-4,000 mis-attachments resolved after conjunction-stranded suppression nominally accounted for)

6. **Spot-check Mk 4:6 + 10 random verses per repo** to confirm:
   - Mk 4:6: "it" + "was" both bind to line 1 (with `scorched`)
   - No regressions in v4/eng / v2/eng on randomly-sampled verses

7. **Update consuming repos' baselines** to reflect new alignment output. Both GNT and Tanakh validators that consume aligned output need baseline regeneration + visual spot-check.

### Phase 3 — Residue measurement (deferred)

8. **Measure residue post-Pass-D**:
   - GNT: expected ~100 cases (low-confidence pronoun/auxiliary cases not caught by Rules 1 + 2)
   - Tanakh: expected ~20,000 cases including the OTHER-category and not-yet-classified residue

9. **Decide LLM-resolver path**: separate follow-on directive. After Pass D lands, measure actual residue volume + character; decide whether per-corpus LLM-resolver is worth building or whether residue is small enough for hand-fix / no action.

## Reporting

Reply at `directives/replies/2026-05-16-2400-cross-corpus-alignment-pass-d.md`:

- Phase 1 audit findings + cross-agent agreement
- Phase 2 implementation commit hash in atu_method
- GNT + Tanakh before/after counts (Item 5)
- Mk 4:6 spot-check + 10-random-verses-per-repo spot-check (Item 6)
- Baseline regeneration commit hashes per repo
- Phase 3 residue measurement (Items 8)
- Any cases where the audit-cleared rules produced unexpected behavior in implementation (surfacing required)

## Audit triggers

**§7.3 trigger #10 (discipline-shifting) + new mechanical-heuristic class (analogous to trigger #1 for code-side).** ≥2 parallel adversarial agents BEFORE implementation per CLAUDE.md + the 2203 precedent.

The Phase 1 audit IS the discipline check. If it fails, the directive halts at Phase 1.

## Tanakh-coordination note

This directive runs in GNT but produces work in atu_method that Tanakh will consume. Two coordination concerns:

- **Tanakh-Claude shouldn't independently process a parallel atu_method directive** — would cause conflicting commits to the shared package. Tanakh's pending queue does NOT include a 2300-followup directive for this reason.
- **After atu_method commit lands**: Tanakh-Claude should be notified via Stan (`directive atu-method-pull` or similar trigger) to pull the upgraded package + run validator/baseline regeneration. Surface this in the reply so Stan knows the cross-repo trigger sequence.

## Cost note

Phase 1: 2 Opus audit dispatches × ~5-8 min each. Per `feedback_model_selection_frugality`, Opus is the right tier for adversarial probing of new alignment-apparatus discipline.

Phase 2: implementation work; LOC TBD by audit-cleared rule shape.

Phase 3 (deferred): if LLM-resolver path pursued — Haiku-tier per 2300 GNT reply ($0.09 GNT-side; $12-45 Tanakh-side depending on residue).
