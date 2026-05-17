# Reply — Unanchored English-alignment scan

Directive: `2026-05-16-2300-unanchored-alignment-scan.md`.

## Implementation

Single diagnostic script at `scripts/scan_unanchored_alignment.py` (~370 lines). Reuses `regenerate_english.py`'s TAGNT loader + v4 parser; calls `atu_method.kjv_alignment.align_verse` for the per-line English output; loads `KjvIndex` separately to identify which KJV words carry Strong's tags. Walks the flat verbatim output in KJV-vpos order against the sorted KjvWord list (1:1 since `align_verse` preserves vpos order both within and across lines). Tokens with empty `strongs_list` → unanchored.

Per-token POS classification uses closed lists (PRONOUNS / AUXILIARIES / ARTICLES / CONJUNCTIONS / PARTICLES / PREPOSITIONS / "other"). UD attachment via spaCy `en_core_web_sm` 3.8.0 (Stanza unavailable in the environment — spaCy is the substitute; English UD label inventory + arc semantics are close enough for this diagnostic).

**No alignment changes. No v4 modifications.** Pure scan.

Full report written to `/tmp/scan-full.md`; counts + samples reproduced inline below.

## Per-category counts (full corpus: 7,939 verses)

| Category | Total | OK | MIS_ATTACHED | AMBIGUOUS | %MIS |
|---|---:|---:|---:|---:|---:|
| **pronoun** | 14,052 | 13,355 | 387 | 310 | 2.8% |
| **auxiliary** | 8,344 | 6,782 | 668 | 894 | 8.0% |
| **article** | 12,645 | 12,375 | 39 | 231 | 0.3% |
| **conjunction** | 2,935 | 2,428 | 440 | 67 | 15.0% |
| **particle** | 54 | 45 | 9 | 0 | 16.7% |
| **preposition** | 11,316 | 10,747 | 361 | 208 | 3.2% |
| **other** | 10,349 | 6,982 | 1,771 | 1,596 | 17.1% |
| **TOTAL** | 59,695 | 52,714 | 3,675 | 3,306 | 6.2% |

**Headline:** 88% of unanchored tokens land on the line where their UD-attachment head lives. 6.2% are mis-attached. 5.5% are ambiguous (root tokens or head-not-in-token-map).

## Top mis-attachment shapes

| Shape | Count | Reading |
|---|---:|---|
| OTHER_BACKWARD_MIS | 2,263 | "other"-category token whose head is on an earlier line — content-verb / NP fragment cases |
| OTHER_FORWARD_MIS | 524 | "other"-category token whose head is on a later line |
| CONJUNCTION_STRANDED_AT_PRIOR_CLAUSE | 440 | "and" / "but" / "or" on line N pointing backward to a verb on line N-1 |
| PRONOUN_STRANDED_BEFORE_VERB | 272 | **The Mk 4:6 shape** — subject pronoun on line N before its verb on line N+1 |
| AUX_STRANDED_AFTER_SUBJECT | 176 | Auxiliary on line N when its main verb is on line N+1 |

**Mk 4:6 confirmation:** the canonical motivating case appears in the scan output:
> `mark 4:6` line 0 → line 1 (→ later line) token `it` → head `scorched`
> `mark 4:6` line 0 → line 1 (→ later line) token `was` → head `scorched`

Both "it" and "was" flagged as mis-attached to line 0, with UD head `scorched` on line 1. The diagnostic correctly identifies the failure.

## Representative MIS-ATTACHED samples per category

### pronoun (forward, the Mk 4:6 family — high signal)

- **matt 3:15** line 1 → line 2: `it` → head `becometh`
- **matt 4:7** line 0 → line 1: `It` → head `written`
- **matt 4:10** line 1 → line 2: `it` → head `written`
- **matt 5:38** line 0 → line 1: `it` → head `said`
- **matt 5:43** line 0 → line 1: `it` → head `said`
- **matt 6:16** line 0 → line 1: `ye` → head `be`
- **matt 7:8** line 1 → line 2: `he` → head `opened`
- **matt 7:27** line 4 → line 5: `it` → head `fell`
- **mark 4:6** line 0 → line 1: `it` → head `scorched`
- **mark 4:32** line 0 → line 1: `it` → head `groweth`

Tight pattern: stranded subject pronoun whose finite-verb anchor is on the next ATU line. **272 corpus-wide**. Cleanest target for a mechanical heuristic.

### auxiliary (forward — clean supplement category)

- **matt 2:18** line 0 → line 2: `was` → head `weeping`
- **matt 2:19** line 0 → line 1: `was` → head `behold`
- **matt 2:22** line 1 → line 2: `was` → head `warned`
- **matt 5:3** line 0 → line 1: `are` → head `is`
- **mark 4:6** line 0 → line 1: `was` → head `scorched`
- **mark 4:32** line 0 → line 1: `is` → head `groweth`
- **mark 2:9** line 0 → line 1: `is` → head `forgiven`

KJV-supplied auxiliary stranded when the main predicate is on the next line. **176 corpus-wide**. Same intervention shape as the pronoun cases.

### conjunction (mostly false-positive at the colometric layer)

- **matt 2:8** line 1 → line 0: `and` → head `sent`
- **matt 2:16** line 2 → line 1: `and` → head `exceeding`
- **matt 4:4** line 1 → line 0: `and` → head `answered`
- **matt 5:23** line 1 → line 0: `and` → head `bring`
- **matt 5:32** line 3 → line 2: `and` → head `causeth`

**Caveat.** These are nearly all "and" / "but" / "or" leading line N where the UD parser identifies a coordination relation back to a verb on line N-1. Colometrically the conjunction SHOULD lead line N (J1 parallel-series convention; canon §3 R8 frame-marker family). The "MIS" verdict here is a UD-parse-vs-colometric-convention mismatch, **not a supplement-attachment failure**. Most of the 440-count is likely false positive for the directive's target problem class.

### article (low volume; mostly compositional)

- **matt 13:19** line 1 → line 2: `the` → head `one`
- **matt 26:5** line 0 → line 1: `the` → head `day`
- **mark 1:27** line 3 → line 4: `the` → head `spirits`
- **mark 12:31** line 0 → line 1: `the` → head `love`
- **luke 13:14** line 1 → line 2: `the` → head `day`

39 corpus-wide. Mostly KJV-supplied "the" before a noun on the next line. Low absolute volume but clean structural pattern when it fires.

### preposition (medium volume; mixed)

- **matt 2:15** line 2 → line 1: `Out` → head `saying`
- **matt 4:25** line 1 → line 0: `from` → head `followed`
- **matt 5:17** line 2 → line 1: `to` → head `come`
- **matt 5:18** line 2 → line 1: `in` → head `pass`
- **matt 5:22** line 2 → line 1: `without` → head `is`

361 corpus-wide. Split between forward and backward mis-attachment. Some are infinitive-marker "to" (which align_verse's `_TRAILING_COMPLEMENT` excludes deliberately — see `distribute.py:104-112`); some are genuine prep-stranding.

### particle (low volume)

9 corpus-wide. Includes 3 `Behold` / `Behold,` stranded.

### other (dominant volume; mixed root cause)

- **matt 1:18** line 2 → line 3: `came` → head `found`
- **matt 1:20** line 0 → line 1: `thought` → head `appeared`
- **matt 1:23** line 1 → line 0: `bring` → head `be`
- **matt 1:25** line 1 → line 0: `brought` → head `knew`
- **matt 2:9** line 1 → line 0: `went` → head `departed`

**Caveat.** The "other" bucket is dominated by KJV content words (`came`, `thought`, `bring`, `went`, etc.) that **should have** Strong's anchors but don't — these are MetaV tagging gaps where KJV's word corresponds to a Greek lemma that MetaV's MainIndex didn't tag at this vpos. The mis-attachment verdict in many of these is genuine, but the **root cause is upstream of `align_verse`**: the word should never have been unanchored in the first place. Fixing here means either (a) widening MetaV tag coverage, (b) adding a synonymy fallback to Pass A, or (c) running a TAGNT-side lookup for unanchored content words. These are NOT the supplement-attachment failure mode the directive targets.

## Intervention-scope recommendation

**HYBRID — heavy mechanical, light LLM-resolver, light upstream-fix.**

### Mechanical heuristic — high-confidence shapes (no LLM)

Implement two rules in `atu_method.kjv_alignment.distribute` Pass C (or a new Pass D run after C):

1. **Unanchored subject pronoun forward-bind.** When `_TRAILING_COMPLEMENT` Pass-C attached an unanchored pronoun (`it` / `he` / `she` / `they` / `we` / `ye` / `you` / `I`) to line N, AND the next non-empty ATU line N+1 begins with a finite verb (or auxiliary + finite verb) that has no explicit subject NP earlier in line N+1, AND no sentence-boundary punctuation separates them — re-attach the pronoun to line N+1. Target: ~272 cases (PRONOUN_STRANDED_BEFORE_VERB).

2. **Unanchored auxiliary forward-bind.** When Pass C attached an unanchored auxiliary (`was` / `were` / `is` / `are` / `am` / `be` / `has` / `have` / `had`) to line N AND its UD-head (the main verb / passive participle) is on line N+1, re-attach the auxiliary to line N+1. Target: ~176 cases (AUX_STRANDED_AFTER_SUBJECT). Detection without spaCy at runtime: heuristic — "unanchored auxiliary at line-N-final position when line N+1 starts with a participle / past-participle form" covers most.

Both rules use only local-window surface features and existing MorphGNT POS access (already available via `validators/_shared/morphgnt_lookup.py`); no LLM call needed.

Expected coverage from mechanical heuristics: **~450 cases / ~88%** of the high-confidence supplement-attachment failure mode.

### LLM-resolver — low-confidence residue (optional, deferred)

If the mechanical-heuristic pass leaves a residue of ambiguous pronoun/auxiliary cases (forward vs backward unclear because the next line starts with a connective or has its own subject NP), surface those to an LLM-resolver sibling to `resolve_review_required.py`. Expected volume: ≤100 cases.

**Cost estimate** (if LLM-resolver path used for residue): Haiku 4.5 at ~$1/MTok input + $5/MTok output. Per-verse context prompt ~600 tokens (Greek lines + English lines + token of interest) + ~50-token verdict → ~$0.0006 + $0.00025 = $0.00085 per resolve. 100 cases × $0.00085 = **~$0.09 total per corpus pass**. Negligible.

### Conjunction shape — NOT recommended for intervention

The 440 CONJUNCTION_STRANDED_AT_PRIOR_CLAUSE cases are a UD-parse-vs-colometric-convention mismatch ("and" leads a coordinate line per canon §3 J1 / R8 convention, even when UD says it coordinates back to a prior verb). Moving these would VIOLATE colometric convention, not improve alignment. **Treat as false positive for this directive's problem class.**

### OTHER bucket — separate root-cause investigation needed

The 1,771 "other" MIS cases are dominated by KJV content words that should be Strong's-anchored but aren't — a MetaV tagging-coverage gap, not a supplement-attachment failure. **Recommend a separate diagnostic** to characterize the MetaV gap before designing an intervention. Could be addressed by:
- Widening MetaV-side synonymy in `distribute.py` Pass B
- Running TAGNT-side lemma lookup for unanchored content words
- Manual MetaV tag patching for high-frequency missed lemmas

This is out of the current directive's diagnostic scope; flagging as a follow-up directive candidate.

### Particle / article / preposition — small-volume targeted fixes

39 article + 9 particle + ~50 cleanly forward-mis preposition cases. Could fold into Rule 1's "forward-bind unanchored function word" generalization. Total marginal-coverage gain: ~100 cases. Worth including in the same mechanical pass.

## Recommended next-directive shape

If Stan approves the recommendation:

1. **Next directive: implement the mechanical forward-bind pass** (Rules 1 + 2 above + the function-word generalization). Target: `atu_method.kjv_alignment.distribute` Pass D or extended Pass C. Estimated coverage: ~550 cases / ~89% of the high-confidence problem volume.
2. **Defer (separate directive): MetaV tagging-coverage gap audit** for the 1,771 "other" cases.
3. **Document (no action): conjunction shape** as a UD-vs-colometric-convention mismatch; not a real failure.

## Cross-repo coordination note

The directive flags a parallel `readers-tanakh/directives/pending/2026-05-16-2300-unanchored-alignment-scan.md` running the same scan against Hebrew→KJV. If Tanakh's scan produces a similar shape table (pronoun/auxiliary stranding dominant; conjunction false-positive cluster present), the mechanical-heuristic intervention should live at `atu_method.kjv_alignment` (cross-corpus shared) rather than per-repo. The Tanakh report should land soon and inform the location decision.

## Surfaced concerns

- **spaCy English UD parser fidelity on KJV-archaic syntax** — some MIS_ATTACHED labels (especially in the conjunction + "other" buckets) may be UD-parser errors rather than real mis-attachments. The pronoun + auxiliary categories are more reliable (modern English UD handles these cleanly). The conjunction-false-positive observation above is one consequence.
- **AMBIGUOUS count is high (3,306 / 5.5%)** — most are root tokens or tokens whose head couldn't be mapped to a KJV-word position. Not a problem class on its own; just a measurement limit.
- **Mark 4:6 confirmed in samples.** The diagnostic correctly identifies the canonical motivating case. The mechanical-heuristic Rule 1 would resolve it (pronoun "it" + auxiliary "was" both forward-bind to line 1's `scorched`).

## Reporting

All directive items addressed:
- Item 1 (unanchored token identification): ✓ — 59,695 tokens identified corpus-wide
- Item 2 (POS classification): ✓ — 7 categories enumerated
- Item 3 (attachment classification): ✓ — OK / MIS / AMBIG per token via spaCy UD
- Item 4 (per-category report): ✓ — counts table + samples above
- Item 5 (top mis-attachment shapes): ✓ — 5 shapes named + counted
- Item 6 (intervention-scope estimate): ✓ — hybrid mechanical-heavy / LLM-light recommendation
- Item 7 (no fixes): ✓ — diagnostic only, no v4 changes, no aligner changes

No items blocked.
