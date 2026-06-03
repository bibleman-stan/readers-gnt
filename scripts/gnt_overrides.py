"""Render-stage ATU-line override layer for the Greek New Testament reader.

Sibling to scripts/bofm_generate.py _overrides() / _apply_override() in BoFM,
but architected around GNT's word-dict pipeline: overrides are applied on
the rendered List[str] for each verse INSIDE sblgnt_generate.emit_v4(), AFTER
the flush() loop materializes the strings — never inside generate() or flush().

Override file: data/text-files/v1.5-adjudicated/grk/overrides.json
  Schema: {"<Book> <chapter>:<verse>": ["ATU line 1", "ATU line 2", ...]}
  Keys use the canonical sblgnt_v1_fabric.NUM book labels VERBATIM (Matt,
  Mark, Luke, John, Acts, Rom, 1Cor, 2Cor, ..., 1John, 2John, 3John, Jude,
  Rev). Matches Macula + SBLGNT-lowfat conventions.

Parity gate: NFD-normalized, lowercased, retaining Greek (U+0370-03FF +
polytonic U+1F00-1FFF) + Latin alpha + digits. SBLGNT editorial marks
(⸂⸃⸀ + ano teleia · + semicolon ;) and superscript chapter-digits prepended
to `_relocated` cross-verse tokens by flush() are all non-alphanumeric and
naturally drop out of the comparison — meaning override authors may omit
superscripts without breaking parity, though we prefer they keep them so
the rendered file stays visually identical to mechanical for unmodified
tokens.

Env bypass: GNT_BYPASS_OVERRIDES=1 short-circuits to mechanical for
validators that want raw mechanical output.

Cross-verse relocation: `lead_forward_trailing_governors` relocates tokens
between verses with `_relocated` flags, and flush() labels each segment by
its CLAUSE-OWN verse (not the relocated-token's home). A `Matt 5:20` override
replaces precisely the line-run under the `5:20` header — i.e. the verse the
relocated token was led INTO, not its home. Authoring works correctly when
the editor starts from mechanical output (copy + re-segment).
"""
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADJUDICATED = REPO_ROOT / "data" / "text-files" / "v1.5-adjudicated" / "grk" / "overrides.json"
BYPASS_ENV = "GNT_BYPASS_OVERRIDES"

_OVERRIDES = None


def _overrides():
    """Cached singleton loader. Honors GNT_BYPASS_OVERRIDES."""
    global _OVERRIDES
    if os.environ.get(BYPASS_ENV):
        return {}
    if _OVERRIDES is None:
        if ADJUDICATED.exists():
            _OVERRIDES = json.loads(ADJUDICATED.read_text(encoding="utf-8"))
        else:
            _OVERRIDES = {}
    return _OVERRIDES


# Allow-list: Greek block U+0370-03FF + polytonic extended U+1F00-1FFF +
# ASCII a-z + 0-9. Everything else (editorial marks, ano teleia, semicolon,
# superscript digits, punctuation, whitespace) is dropped.
_KEEP_RE = re.compile(r"[^Ͱ-Ͽἀ-῿a-z0-9]")


def greek_alnum(s):
    """NFD-normalized, lowercased, Greek-block-aware alnum stripper.

    NFD first decomposes precomposed characters (αΛ, ΐ, etc.) into base +
    combining marks; lowercasing folds capitals; the Greek + polytonic +
    Latin allow-list keeps the alphabetic content while dropping editorial
    marks ⸂⸃⸀, ano teleia ·, semicolon ;, superscript digits, punctuation,
    and whitespace. The result is a strict-but-orthography-tolerant parity
    key suitable for verifying that an override's joined lines reassemble
    to the source verse text.

    NB: NFD leaves base Greek letters intact and pushes accents to
    combining marks; the [\\u0370-\\u03FF\\u1F00-\\u1FFF] retention range
    PRESERVES polytonic precomposed forms AND base forms; the lowercase
    pass handles the case fold; the regex drops anything outside both
    ranges, including combining marks (which are in U+0300-036F, outside
    our keep ranges). So effectively the comparison is on base-letter
    sequence — which is what we want, since SBLGNT surface forms are
    polytonic-precomposed and an LLM-authored override may carry either
    composed or decomposed forms.
    """
    nfd = unicodedata.normalize("NFD", s).lower()
    return _KEEP_RE.sub("", nfd)


def apply_chapter_overrides(book_label, chap, out_lines):
    """Walk emit_v4's `out` list, identify each verse's block via "chap:verse"
    header lines, and swap the mechanical ATU lines for adjudicated ones iff
    an override exists AND its joined greek_alnum equals the mechanical
    block's same normalization.

    `out_lines` shape per emit_v4 (sblgnt_generate.py:flush): alternating
    blocks of [header, atu_line_1, atu_line_2, ..., "", header, atu_line_1, ...].
    The blank-line separator and the "chap:verse" pattern make verse blocks
    unambiguous.

    Returns a NEW list (does not mutate `out_lines`). Empty overrides ->
    structural copy of input.
    """
    overrides = _overrides()
    if not overrides:
        return list(out_lines)

    header_re = re.compile(rf"^{chap}:(\d+)$")
    result = []
    i = 0
    n = len(out_lines)
    while i < n:
        line = out_lines[i]
        m = header_re.match(line)
        if not m:
            result.append(line)
            i += 1
            continue
        verse_num = int(m.group(1))
        # Collect mechanical block: from header (exclusive) until next header
        # or end-of-list. The blank-line separator (if present) stays inside
        # the block we record but is not part of the parity input.
        block_start = i
        i += 1  # past header
        atu_lines = []
        while i < n:
            nxt = out_lines[i]
            if header_re.match(nxt):
                break
            if nxt == "":
                # Trailing blank separator: skip; it'll be re-added on the
                # NEXT iteration's header path (via "if out: out.append('')").
                # We don't preserve it here because the override decides its
                # own line list.
                break
            atu_lines.append(nxt)
            i += 1
        ref = f"{book_label} {chap}:{verse_num}"
        ov = overrides.get(ref)
        if ov:
            mech_joined = " ".join(atu_lines)
            ov_joined = " ".join(ov)
            if greek_alnum(ov_joined) == greek_alnum(mech_joined):
                # Parity OK: emit header + override lines + (blank if any)
                result.append(out_lines[block_start])  # header
                result.extend(ov)
                if i < n and out_lines[i] == "":
                    result.append("")
                    i += 1
                continue
            else:
                print(f"  !! adjudication override REJECTED (text mismatch): {ref}",
                      file=sys.stderr, flush=True)
        # No override or parity failed: emit mechanical block verbatim.
        result.append(out_lines[block_start])  # header
        result.extend(atu_lines)
        if i < n and out_lines[i] == "":
            result.append("")
            i += 1
    return result
