# 01 — Greek Colometric Methodology

## Foundation

This project applies sense-line (colometric) formatting to the Greek New Testament. The method is grounded in the scholarly tradition of Lee & Scott (sound mapping), Marschall (colometric analysis), and ancient manuscript practice (Codex Bezae, Codex Claromontanus).

## Core Premise

Ancient authors composed for oral delivery. The text was heard, not silently read. Modern verse-and-paragraph formatting obscures the original compositional structure. By breaking the text at its natural grammatical joints, we recover the author's own phrasing — the cola (κῶλα) and periods (περίοδοι) that structured the original composition.

## What We Ignore (Deliberately)

These are later additions that do not reflect authorial intent:

- **Versification** (Stephen Langton, 13th c. / Robert Estienne, 1551)
- **Modern punctuation** (editorial, not original)
- **Pericope divisions** (liturgical, not compositional)
- **Paragraph breaks** (editorial convention in NA28/UBS5)

We preserve verse references for alignment with standard editions, but they do not drive line-breaking decisions.

## What We Follow

- **Greek clause structure** — main clauses, subordinate clauses, participial phrases
- **Discourse markers** — καί, δέ, γάρ, οὖν, ἀλλά as structural signals
- **Rhetorical patterns** — parallelism, tricolon, chiasm, μέν/δέ contrast
- **Breath and thought units** — each line processable as a single cognitive chunk

## Greek-Specific Break Points

### 1. Main Clause Boundaries
Each new finite verb introducing a new action or state is a candidate for a new line. In Markan narrative, the paratactic καί chain becomes visible as a sequence of images:

```
καὶ γίνεται λαῖλαψ μεγάλη ἀνέμου,
καὶ τὰ κύματα ἐπέβαλλεν εἰς τὸ πλοῖον,
ὥστε ἤδη γεμίζεσθαι τὸ πλοῖον.
```

### 2. Subordinate Clause Introductions
Purpose (ἵνα), result (ὥστε), causal (ὅτι, διότι), temporal (ὅταν, ὅτε), conditional (εἰ, ἐάν) — each introduces a new line:

```
ἵνα βλέποντες βλέπωσι καὶ μὴ ἴδωσιν,
καὶ ἀκούοντες ἀκούωσι καὶ μὴ συνιῶσιν,
μήποτε ἐπιστρέψωσιν καὶ ἀφεθῇ αὐτοῖς.
```

### 3. Participial Phrases
Major participial phrases (especially genitive absolutes) function as temporal or circumstantial framing and earn their own line:

```
Σταθεὶς δὲ Παῦλος ἐν μέσῳ τοῦ Ἀρείου Πάγου ἔφη·
```

When participial chains describe the same action, they may stay together:

```
διερχόμενος γὰρ καὶ ἀναθεωρῶν τὰ σεβάσματα ὑμῶν
```

### 4. Direct Speech
Speech introductions (ἔλεγεν, εἶπεν, ἔφη + dative) get their own line. The speech content begins on the next line:

```
καὶ ἔλεγεν αὐτοῖς·
Ὑμῖν τὸ μυστήριον δέδοται τῆς βασιλείας τοῦ θεοῦ·
```

### 5. Parallel Stacking
When the author builds parallel structures, stack them vertically to make the rhetoric visible:

```
καὶ αἱ μέριμναι τοῦ αἰῶνος
καὶ ἡ ἀπάτη τοῦ πλούτου
καὶ αἱ περὶ τὰ λοιπὰ ἐπιθυμίαι
εἰσπορευόμεναι συμπνίγουσιν τὸν λόγον,
```

### 6. μέν/δέ Contrast
Greek's built-in contrast structure becomes spatially visible:

```
οἱ μὲν ἐχλεύαζον
οἱ δὲ εἶπαν·
```

### 7. Explanatory γάρ
Often introduces a new line, since it signals a shift to explanation:

```
ἐν αὐτῷ γὰρ ζῶμεν
καὶ κινούμεθα
καὶ ἐσμέν,
```

## Decisions Still Open

- **How short is too short?** Single-word lines (e.g., ἐκαυματίσθη) — dramatic emphasis or fragmentation?
- **Genitive absolute attachment:** always its own line, or sometimes attached to main clause?
- **ὅτι recitativum:** stays with speech intro, or breaks?
- **Cross-verse continuity:** when a sentence spans verses, should we visually indicate the continuation?
- **Indentation:** should subordinate clauses be indented? (BOM Reader uses flat; discourse displays use indentation)

## Test Chapters

Initial colometric formatting applied to:
- **Mark 4** — parables + storm narrative (tests discourse speech and action narrative)
- **Acts 17** — Thessalonica/Beroea travel + Areopagus speech (tests Lukan narrative and Pauline rhetoric)

Files: `data/text-files/v1-colometric/mark-04.txt`, `acts-17.txt`

---

### Established — 2026-04-09
- Initial methodology document created
- Two test chapters formatted (Mark 4, Acts 17)
- Greek-specific break-point rules drafted from BOM Reader principles
