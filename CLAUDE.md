# GNT Reader — Claude Code Instructions

A colometric reading edition of the Greek New Testament at **gnt-reader.com**. Each line is an atomic thought unit (ATU) reflecting Koine grammatical structure, designed for oral delivery and comprehension. Base text: SBLGNT (CC-BY-4.0). Stage: v4/grk complete — all 260 chapters hand-edited, KJV-verbatim English aligned per ATU line, web app live. Sibling readers: bomreader.com (BoFM, reference impl) and tanakh-reader.com (Hebrew Bible); shared methodology + alignment-tooling plane at `../atu-method/`.

---

## Orientation reads

**MANDATORY at every wake (including short pings; compaction-resume runs from scratch):**
1. This CLAUDE.md
2. `private/01-method/colometry-canon.md` — at least §0/§1/§2 framework pointers + §3 Quick-Reference
3. `git log --oneline -10`
4. Most recent `private/` pending notes if present

**CONSULT-ON-TRIGGER:**
- `private/01-method/colometry-canon.md` — anything touching `validators/`, `scripts/regenerate_english.py`, `data/text-files/v4/grk/`, syntax-reference, or rule-interpretation.
- `data/syntax-reference/greek-break-legality.md` — R2–R7 Layer 1 break-legality.
- `../atu-method/docs/framework.md` — methodology, rule-design, autonomy-boundary. Authoritative cross-corpus body.
- `../atu-method/docs/apparatus.md` + `architecture.md` — English-layer / alignment-pipeline / cross-sibling architectural work. Picture-shaped: what the reader sees on gnt-reader.com when done.
- `../atu-method/docs/change-protocol.md` — any canon revision.
- `../atu-method/docs/glossary.md` — ambiguous term (ATU, M1–M4, J1–J5).

**Self-report before first substantive response:** one line per mandatory file read; pending-item disposition (each = executing-now / retired-with-rationale / re-deferred-with-concrete-trigger; "awaiting Stan direction" is drift not a defer); red flags. Silent skip = orientation failure.

JSONL at `~/.claude/projects/c--Users-bibleman-repos-readers-gnt/<session-id>.jsonl` is the verbatim record. After compaction, grep into it. Don't write wrap artifacts / session-notes / full-transcript dumps; surface state inline.

---

## Editorial discipline (highest-violation surface)

### Use the structured layer FIRST. Heuristics and agents are last resort.

GNT vendors a stack of structured syntactic signals:

| Layer | Wrapper | What it encodes |
|---|---|---|
| **Macula Greek** (constituent trees, clause roles) | `validators/_shared/macula_clauses.py` | clause boundaries, constituent membership, role labels |
| **MorphGNT** (per-word POS + morph) | `validators/_shared/morphgnt_lookup.py` | POS, case, number, tense, voice, mood, lemma per token |
| **TAGNT** (per-token Strong's + lemma group) | parsed in `regenerate_english.py` | Strong's number + lemma-equivalence cluster per Greek token |
| **MetaV** (per-KJV-word Strong's) | `atu_method.kjv_alignment.metav_loader` | Strong's per KJV-1769 word |
| **Existing per-rule validators** | `validators/colometry/*.py` | named-syntactic-signature corpus queries |

Before reaching for either:

**(a) a surface-form heuristic** (closed-list "trailing prepositions" / "speech verbs" / "object pronouns" at the algorithm level) — ask whether Macula's constituent structure or MorphGNT POS already encodes the constraint. The structural binding is the answer, not the surface form.

**(b) a grep-agent dispatch** to survey the corpus for a pattern — ask whether MorphGNT + Macula + the existing validator suite already answer the question via deterministic query. Most "let me survey all instances of X" questions have a UD-style signature that resolves in seconds, not minutes.

**Cross-repo failure-mode evidence:** Tanakh's `atu-method/atu_method/kjv_alignment/distribute.py` Pass-C closed-list (`_OBJECT_PRONOUNS` / `_TRAILING_PREPOSITIONS` for KJV trailing-complement attachment) substituted surface-form for Macula Hebrew constituent structure — cost 3 cascades + audit waves before Stan caught it. bofm dispatched 4 parallel grep-agents to survey N-INF / COMP / RELCL patterns when `validate_rule_17_ud.py` already had the exact signature + an inline comment marking the gap — 7 min + 80k tokens for an over/under-counted estimate vs. 6 seconds of UD query.

### Stan-flagged verse = class-investigation directive

When Stan flags a problem at a specific verse, that's a directive to investigate the rule set, NOT patch the verse. Right shape:
1. Diagnose: what's the underlying class/pattern Stan's intuition is responding to?
2. **Audit yourself FIRST** — walk M1 / M2 / M3 / M4 / J1–J5 / formula-integrity / R-rules explicitly against the actual canon. Pay attention to **explicit exclusions** (e.g., complement integrity in framework §1.2 scopes to VERB+ADJ only — NOUN-headed is out of scope, not a gap). If the framework's existing answer is "split, this is excluded," that's a real answer.
3. Only if step 2 finds a real gap, investigate corpus-wide via the structured layer (see above), not via grep-agents.
4. **New rules trigger canon §6.5 mandatory-audit** — ≥2 parallel adversarial agents BEFORE any validator infrastructure. NO scanner / applier / closed-list entry until the rule passes. Building infrastructure first is the "fake rule" failure mode.
5. If audit holds: codify with WHY/HOW WE KNOW/SCOPE per canon §6 defensibility-capture, build validator, apply mechanically corpus-wide.
6. If audit fails or framework already answers: report Stan the actual framework answer; offer Category B per-verse editorial-judgment fallback ONLY if genuinely needed.

### Anchor in Koine syntax, not English-translation surface

KJV systematically smooths Koine grammar into English-idiomatic constructions that don't exist in the Greek (English "when X, then Y" for a participial circumstance; English "to do" for ἵνα + subjunctive). Before agreeing OR disagreeing with an editorial intuition sourced from the English layer, check MorphGNT + Macula:
- Genitive absolutes (`GAV` / `GAS` / `GAP` signatures) → always own line per canon, regardless of how KJV smooths them
- Vocatives (`N-V*` morph code) → universal own-line rule
- ἵνα / ὥστε / ὅτι / ὅταν → subordinate clause break point per R-rules
- KJV's "when" / "and then" are translation choices, not Koine syntactic facts

### Editorial-call structure

When Stan names a verse with a specific desired partition or proposes a fix: line 1 = "Got it — [Stan's reading]"; line 2-N = the diff. **NO leading analytical defense of an alternative.** Analysis is value-add ONLY when Stan asks "what should it be?" or "explain what's going on there."

### Class-fix vs instance-fix

Same FP class in 2+ rules OR 2+ validators OR 2+ verses in one session = engine-level fix at `validators/_shared/*` / `atu-method/atu_method/*` / canon rule extension. Per-verse / per-validator guard the second time = whack-a-mole. **Swat the bug class, not the instance.**

### Rule-derivative vs ad-hoc

Rule-derivative changes (a codified MECHANICAL rule fires unambiguously via its validator or clean trigger match) auto-apply — the canon's rule is the approval. STRONG-MERGE-CANDIDATE / STRONG-SPLIT-CANDIDATE tags are application-ready; only REVIEW-REQUIRED needs per-item editorial judgment. Walking Stan through verse-level confirmations on rule-derivative changes is the inverted-discipline failure mode.

Ad-hoc changes (no codified rule, or Category B editorial, or Category C exegetical hot spot) DO require Stan approval before application.

### Adversarial-audit discipline

Before non-trivial implementation (new validator with classification logic, new rule subsection, new closed-list extension, new shared helper, **OR ANY edit to `../atu-method/atu_method/*` cross-corpus shared infrastructure**), FIRST tool call must be ≥2 parallel Agent adversarial dispatches in one message OR an explicit `Audit-skippable: <named-trivial-class>` declaration.

Pre-commit on canon-touching commits: every commit message touching `private/01-method/colometry-canon.md` includes `Audit-skippable per §6.5 ([reason])` OR `Audit dispatched: [evidence]`. The commit-msg hook detects canon-extension patterns and requires the declaration. When uncertain, dispatch.

Same-trigger audits across distinct angles (discipline / scope / cross-project consistency / corpus impact) fire in ONE batch via parallel Agent calls, not in series.

**First-round-reframes is the default.** When dispatching the audit panel on a canon addition framed as "restatement / no new claim," expect at least one of the three audits to flag a scope/precedence/closed-list claim I didn't see. Schedule re-drafting time as part of the commit timeline; don't commit as-drafted on a NEEDS-MODIFICATION verdict. Specific anti-pattern: list-order in one operational sentence (e.g., "after Tier 1 vetoes, formula integrity, complement integrity have settled") is sequence-of-application within ONE rule's resolution, NOT a tier-rank assertion. Generalizing it is scope-creep.

### Apply causes regression

Revert the apply → root-cause why → fix the apply → re-attempt with integrity gate verified post-apply. Do NOT build downstream-recovery tools first.

### Stan-escalation phrasing ("WHY are you still doing this", "stop wasting my time", "you screwed up again", "did i or did i not say...")

STOP iterating on the surface fix. Frame-reset to class level. Ask: what's the COMMON pattern across recent attempts that I've been treating as separate instances? The escalation is a signal that the loop has run too long; the meta-pattern is what needs the answer.

### Proactive open-item surfacing

Every deferred item must be visible in chat. Periodically re-examine whether held items have become canon/code/precedent-derivable as the method matures. If yes, surface "I previously needed your input on X; canon now resolves it via Y; applying unless you say stop" — don't re-defer derivable items.

---

## Source text rules

`data/text-files/sblgnt-source/` is canonical reference, NEVER edited. `data/text-files/v4/grk/` is single source of truth, hand-edited by Stan. The only editorial tool is where lines break. NEVER alter Greek text (words, accents, breathing marks), add or remove words. ALWAYS preserve verse-refs. Use `PYTHONIOENCODING=utf-8` on Windows. NEVER run `scripts/archive/` tier-producer scripts (v0–v3 frozen 2026-04-26; they write to scaffolding directories and break the hand-edited corpus).

---

## Methodology stack

Three forces operating simultaneously: **generative** (atomic thought drives line creation; J1–J5 structural justifications), **subtractive** (Koine syntax + complement + formula integrity trigger merges; M1–M4 merge-overrides), **diagnostic** (single image as tiebreaker). Authoritative body: [`../atu-method/docs/framework.md`](../atu-method/docs/framework.md). GNT-specific rule body: `private/01-method/colometry-canon.md`. Fresh-read both before any editorial or rule work — rules evolve fast and any in-line summary drifts.

**Categories** (autonomy boundary per `framework.md` §2):
- **Category A** (Mechanical, mandatory) — rule firing IS the approval; auto-apply.
- **Category B** (Editorial, judgment-required) — flag and discuss with Stan.
- **Category C** (Theological / textual-critical) — hand-curation only.

---

## Pipeline & files

| Tier | Directory | Engine |
|---|---|---|
| Source | `data/text-files/sblgnt-source/` | SBLGNT raw, NEVER edited |
| v4 | `data/text-files/v4/grk/` | Stan + Claude hand-edited, single source of truth |
| Eng | `data/text-files/v4/eng-kjv/` | `scripts/regenerate_english.py` → `atu_method.kjv_alignment.align_verse()` (KJV verbatim per Greek ATU line via Strong's-number matching: TAGNT → MetaV) |
| HTML | `books/` | `scripts/build_books.py` |

**Cascade rule:** Greek edit → English regen → HTML rebuild → three-check → commit → push. ONE atomic operation. If you change Greek without syncing English and rebuilding HTML in the same work unit, you have failed.

**Three-check verification before any cascade commit** (all return 0):
- `py -3 scripts/verify_word_order.py` — integrity (every Greek word present in expected verse per SBLGNT)
- `py -3 scripts/scan_english_drift.py --min-confidence high` — English-quality drift detector
- `py -3 scripts/scan_eng_kjv_coverage.py --baseline-check` — eng-kjv coverage (every Greek content line has English; baseline guards against new blank lines; closes the bracket-pericope blind spot — commit 7f3c361c)

The coverage check is also wired into the pre-commit hook (Phase 2) and runs automatically when `v4/grk`, `v4/eng-kjv`, or `regenerate_english.py` are staged.

---

## Validators & mechanical gates

**Hooks** (tracked at `validators/hooks/`, installed via `cp ... .git/hooks/`):
- **`pre-commit` Phase 1** — cascade-staleness detection (v4/grk staged → v4/eng-kjv + `books/<slug>.html` must also be staged with matching line counts).
- **`pre-commit` Phase 2** — `scan_eng_kjv_coverage.py --baseline-check` (added 2026-05-12).
- **`pre-commit` Phase 3** — `validators/run_all.py --baseline-check` blocks regressions vs `validators/.baseline.json`.
- **`commit-msg`** — `validators/check_canon_extensions.py` detects canon-extension patterns; requires audit-evidence keyword OR skip-safe claim in commit message.

**Bypass:** `git commit --no-verify` = Stan-only explicit override. New validators stage `--update-baseline` in the same commit. Canon commits include the audit-status declaration substring or fail the hook.

---

## Default decisions (do NOT surface as menus to Stan)

| Decision point | Standing answer |
|---|---|
| Corpus pattern survey | Query Macula/MorphGNT via `validators/_shared/{macula_clauses,morphgnt_lookup}.py` or write a deterministic Python script. NEVER dispatch agents to grep the corpus for syntactic patterns — the structured layer already exists. |
| Surface heuristic vs structured-layer query | Structured-layer first. Closed-list rules at the algorithm level are last-resort; if Macula/MorphGNT/TAGNT encode the constraint, use them. |
| Adversarial audit on non-trivial implementation | ≥2 parallel Agent dispatches in one message, OR `Audit-skippable: <named-trivial-class>`. Never sequential. |
| Extending existing validator vs creating new | Extension. New = explicit justification with substantive criterion. |
| Same FP class in 2+ rules/validators/verses in session | STOP. Engine-level / canon-level fix. No more per-instance guards. |
| Apply causes regression | Revert → root-cause → fix → re-apply with integrity gate. NEVER build recovery tools first. |
| Commit attempt fails | `git log -3` + `git status --short` BEFORE retry. Use `git commit -m "$(cat <<'EOF'...EOF)"` (NEVER `-F /dev/stdin` — Linux-only). Never run two `git commit` in parallel — they race on HEAD lock. |
| "Should I commit now or wait?" | Commit substantive work proactively; status claims AFTER commit. |
| Cascade rebuild after pipeline change | Parallel cluster agents by genre group; never one agent on 27 books. |
| Per-item judgment work at corpus scale | Parallel cluster-Opus dispatch (one per genre group); never hand-pass. |
| Stan asks "explain what's going on there" / "what is the correct approach" | Diagnose the rule-set gap. Do NOT propose Option A / Option B menus on the surface verse. |
| Stan names a verse with a desired partition | "Got it — [reading]" + diff. No leading analytical defense. |

When outside this table, surface. When inside, dispatch the standing answer and report the result.

**Genre-group split** (for cluster-cascade routing): Mark / Matt / Luke-Acts / John+Johannine / Pauline / Hebrews / General Epistles / Revelation. Threshold: any batch ≥25 surgical fixes spanning 3+ groups MUST be split.

**Agent model routing:** Haiku for mechanical lookups; Sonnet for narrow-scope scans where rules are defined; Opus for adversarial audits / methodology synthesis / novel rule design / cross-corpus shared-infrastructure edits (`atu-method/atu_method/*`). Sonnet default; reserve Opus for reasoning-heavy work.

---

## Git workflow

All work on `main`. **Commit AND push autonomously after any clean commit on main** (Stan blanket-authorized 2026-05-11; SSH transport `bibleman-windows-desktop` key, silent pushes). Sequence: `git commit` → if exit 0 → `git push origin main` → THEN report.

**Confirm BEFORE push:** force-pushes (`--force` / `--force-with-lease`); pushes to non-main; pushes containing agent-applied bulk corpus changes Stan hasn't diff-reviewed.

**Tree-state self-check before commit (mandatory):** `git status --short`. If unrelated work is staged, separate it before committing — commit titles must describe actual scope. Either ask first, commit separately, or `git stash --keep-index`.

---

## Project siloing

Publicly independent — no cross-references to any other projects in README, public-facing docs, or the web app. Internal CLAUDE.md may reference sibling repos as cross-failure-mode evidence (see Editorial Discipline) since this file is dev-facing, not reader-facing.
