# scripts/substrate/

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

### `equational_cola.py`
Detects verbless equational predication — overt subject + nominal
predicate with elided copula. The Rom 8:10 / Matt 26:41 class.

Returns `True` when the cola's covering clause has `cltype ∈ {Verbless,
VerbElided}` AND `rule` contains both S and P slots (excludes
single-role fragments like P2CL, S2CL).

Self-test: precision=1.0 on 5-case truth set. The Macula data carries
912 Verbless + 1016 VerbElided clause nodes corpus-wide.

## Provenance

Both modules originated from pipeline-A Round 4 (hybrid spec+prototype
workflow, 2026-06-03). Code ran cleanly against the 137,741-word Macula
lowfat index with zero runtime errors. §7.3 audit flagged production-
quality concerns (edge cases on truth-set token-range alignment); these
are tracked but do not block landing as standalone substrate helpers —
the modules don't yet participate in the live merge-chain.

## Integration status

NOT WIRED to `sblgnt_generate.py` yet. These are standalone modules
available for import. Integration into the merge-chain (insertion at
line 758-763 between `merge_parallel_elided_verb` and
`merge_line_end_leaders`) is a separate gated decision.

## Usage

```python
from scripts.substrate.equational_cola import EquationalLookup, is_equational_cola

lookup = EquationalLookup.from_macula_dir(MACULA_DIR)
is_eq = is_equational_cola("ROM 8:10", ["ROM 8:10!1", "ROM 8:10!2", ...], lookup)
```

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
