# GNT v1.5 adjudication overrides

Render-stage ATU-line overrides for residual cases the mechanical v1.5 binding
fabric (`scripts/sblgnt_v1_fabric.py` + `sblgnt_generate.py`) cannot reach:
judgment-residuals where the parse is structurally sound but the line-break
needs editorial finesse.

## File

`overrides.json` — keyed `"<Book> <chapter>:<verse>"` using the canonical
`sblgnt_v1_fabric.NUM` labels VERBATIM (`Matt`, `Mark`, `Luke`, `John`,
`Acts`, `Rom`, `1Cor`, `2Cor`, `Gal`, `Eph`, `Phil`, `Col`, `1Thess`,
`2Thess`, `1Tim`, `2Tim`, `Titus`, `Phlm`, `Heb`, `Jas`, `1Pet`, `2Pet`,
`1John`, `2John`, `3John`, `Jude`, `Rev`). Matches Macula + SBLGNT-lowfat
conventions.

```json
{
  "Matt 5:20": [
    "λέγω γὰρ ὑμῖν",
    "ὅτι ἐὰν μὴ περισσεύσῃ ὑμῶν ἡ δικαιοσύνη πλεῖον τῶν γραμματέων καὶ Φαρισαίων,",
    "οὐ μὴ εἰσέλθητε εἰς τὴν βασιλείαν τῶν οὐρανῶν."
  ]
}
```

Values are arrays of strings — one ATU line per element, in surface order,
exactly as they would appear in `v1.5/grk/<NN-book>/<book>-<CC>.txt`.

## Parity gate

Every override entry must reassemble to the mechanical verse text alphabetically.
The check is NFD-normalized, lowercased, Greek-block (U+0370-03FF) + polytonic
(U+1F00-1FFF) + Latin alpha + digit comparison. Everything outside that allow-list
is dropped, including:
- SBLGNT editorial marks ⸂⸃⸀
- Ano teleia · and Greek question mark ;
- Superscript chapter-digits prepended to `_relocated` cross-verse tokens
- All punctuation and whitespace

A mismatch is silently REJECTED with a stderr warning; mechanical output is kept.

This means **an override can re-segment, never re-word**.

## Cross-verse relocation

`lead_forward_trailing_governors` in `sblgnt_generate.py` relocates tokens
between verses; `flush()` headers each segment by its CLAUSE-OWN verse (not
the relocated-token's home). A `Matt 5:20` override replaces precisely the
line-run under the `5:20` header — including any tokens led-FORWARD into v20
from v19 (which `flush()` renders with a superscript chapter-digit).

Editors authoring overrides should start from the mechanical output (copy
the file's verse block, then re-segment). Superscript markers can be
preserved or omitted — both pass parity because superscript digits are
non-alphanumeric — but preserving them keeps the rendered file visually
identical to mechanical for unmodified tokens.

## When to use an override

- The mechanical fabric over-splits or over-merges a specific verse where
  no general binding rule can be added without regressing elsewhere
- A scholarly editorial choice (e.g. Pauline doxology cola, Johannine prologue
  parallelism) the binding rules cannot make from Macula features alone

## When NOT to use an override

- A class of verses needs the same fix → add a binding rule in
  `sblgnt_generate.py` instead (or extend `macula_hoti.decisions` for ὅτι class)
- The underlying parse is wrong → fix the v0 substrate or Macula feature
  extraction

## Bypass

For validators or raw-mechanical-measurement runs:

```
GNT_BYPASS_OVERRIDES=1 python scripts/sblgnt_generate.py Matt 5 --write
```

## Architecture

Overrides apply at the **render stage** inside `emit_v4()`, AFTER the
`flush()` loop populates `out: List[str]` and BEFORE `return out`. The GNT
generate/flush pipeline operates on word-dict node-lists, not strings, so
overrides cannot drop in at generate-stage the way BoFM's do. The
render-stage injection is the architecturally clean answer; mirrors the
Vulgate + Tanakh solutions and is documented in the cross-corpus port
redesign work (session 2026-06-02).
