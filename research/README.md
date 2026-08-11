# research/ — third-party corpora (payloads untracked, this manifest tracked)

Nothing in this directory is our work, and nothing here is committed except this
file. Both directories below are clones; if one is missing, restore it with the
command given.

**Our own analysis does not live here.** It goes in the numbered tiers —
`2-evidence/` for findings and baselines, `5-machinery/` for scripts.

## Why this file exists

On 2026-08-10 both directories below were found missing. `research/` was covered
by a blanket ignore, so the clones had never been tracked and their deletion left
no trace. Nothing failed loudly:

- Fifteen validators returned **zero** candidates and reported success.
- `M4-GNT-1` emitted **4158** candidates against a recorded baseline of **409** —
  an order of magnitude of false positives, read as real findings.

After restoring both, the suite returned 814 candidates against a baseline total
of 821, with `R19` (129) and `R7` (2) matching their recorded values exactly.

A missing corpus must be a loud failure, not a quiet zero. Until the validators
assert their inputs exist, this manifest is what makes the absence noticeable.

## Expected contents

| Directory | Source | Pinned |
|---|---|---|
| `macula-greek/` | https://github.com/Clear-Bible/macula-greek | `8423afe` |
| `morphgnt-sblgnt/` | https://github.com/morphgnt/sblgnt | `aaed91e` |

### macula-greek

Syntax trees, morphology, and linguistic annotations for the Greek New Testament,
covering both SBLGNT and Nestle1904 in three formats: `lowfat/`, `nodes/`, `tei/`.

    git clone --depth 1 https://github.com/Clear-Bible/macula-greek.git

`5-machinery/validators/_shared/macula_clauses.py` reads
`research/macula-greek/SBLGNT/lowfat/`, expecting `01-matthew.xml` naming, and
uses the `class` and `rule` attributes.

**Format caveat.** `lowfat/` carries `class`, `rule` and `role` but *not*
`ClType`. That attribute exists only in `nodes/`, is spelled with capitals, and
marks the clause types with no finite verb — `Verbless`, `VerbElided`, `Minor`.
`5-machinery/scripts/substrate/matrix_finite.py` asks for lowercase `cltype`
while otherwise expecting `lowfat` structure (`wg` elements, `class="cl"`), which
`nodes/` does not have. Its Tier 1 exclusion therefore cannot fire against either
format. Tracked on the board.

For comparison, the Hebrew Macula spells the same idea `clausetype`.

### morphgnt-sblgnt

Morphologically parsed SBLGNT, one `*-morphgnt.txt` per book. Supplies the mood
parsing that rules R3 and R7 depend on; without it both raise on every verse.

    git clone --depth 1 https://github.com/morphgnt/sblgnt.git morphgnt-sblgnt

Note the directory name differs from the upstream repo name (`sblgnt`), so the
target argument above is required.

## Restoring everything

    cd research
    git clone --depth 1 https://github.com/Clear-Bible/macula-greek.git
    git clone --depth 1 https://github.com/morphgnt/sblgnt.git morphgnt-sblgnt

Then confirm with `python -m validators.run_all --summary` from `5-machinery/`:
a total near 814 across 8 non-zero rules means both corpora are readable. A total
in the thousands, or rules pinned at zero, means one is missing.
