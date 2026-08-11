# 5-machinery/scripts/substrate/

Substrate-exposure helpers — read Macula's rich annotation layer and
surface it for fabric-rule consumption.

These modules sit BETWEEN the third-party Macula treebank and the
sblgnt_generate.py merge-chain. They expose what Macula already tags
(cltype, rule, role, clauseType) at the per-token / per-cola level so
fabric rules don't have to re-derive structure from lemma lists.

## Modules

### `matrix_finite.py`
4-tier matrix-vs-embedded finite-verb detection over Macula sblgnt-lowfat
XML. Returns `True` if a clause node has its own matrix finite verb,
distinguishing from:
- Verbless / VerbElided / Minor cltype (tier 1)
- Embedded subordinate finite verbs (relative clauses, complement clauses) (tier 3)
- Participial / infinitival heads (tier 2 nominal-mood gating)

Self-test passes 5/5 on Romans + 1 Corinthians anchors (precision=1.0, recall=1.0).

## Provenance

`matrix_finite.py` originated from pipeline-A Round 4 (hybrid spec+prototype
workflow, 2026-06-03). Code ran cleanly against the Macula lowfat substrate
with zero runtime errors on 5 hand-picked anchor cases.

A sibling module `equational_cola.py` was initially landed alongside but
removed 2026-06-03 after a hostile audit found the predicate fails its own
named anchor (ROM 8:10 — the headline target — returns False against
expected True). The commit message's "precision=1.0, recall 0.333 is
truth-set mismatch not predicate bug" framing was a rationalization;
the predicate has not been demonstrated to handle the verbless equational
class it claims to detect. Re-attempt requires either (a) a predicate
that handles ROM 8:10 / MAT 5:3 / similar verbless equational cola, or
(b) a truth set rebuilt against actual Macula clause-token alignment.

## Integration status

NOT WIRED to `sblgnt_generate.py` yet. Standalone module available for
import. Integration into the merge-chain is a separate gated decision.

## Usage

```python
from scripts.substrate.matrix_finite import matrix_finite_predicate, find_innermost_cl

cl = find_innermost_cl("ROM 8:5!9")
has_matrix = matrix_finite_predicate(cl)
```

## Source

Macula sblgnt-lowfat XML at
`research/macula-greek/SBLGNT/lowfat/` (NOT
`biblical-corpora/.../sblgnt-lowfat/xml/` — the latter lacks the rich
cltype / rule / role attributes per the Pipeline B substrate-location
empirical finding).
