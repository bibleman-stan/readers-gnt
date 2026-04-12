#!/usr/bin/env python3
"""
scan_elided_parallels.py — Find paired parallel constructions (μέν...δέ,
εἴτε...εἴτε, οὔτε...οὔτε, ἢ...ἤ, ὁ μέν...ὁ δέ, τοῦτο μέν...τοῦτο δέ, and
select ἀλλά contrasts) where one or both halves lack a finite verb AND the
current layout either (A) compresses both halves onto a single line or
(B) splits them asymmetrically — a dangling fragment before a line that
buries the pair-marker mid-line.

Per handoffs/02-colometry-method.md (the ellipsis principle): an elided
(gapped) verb is a real predication. Both halves of a parallel construction
that share one verb should be stacked as parallel lines.

Showcase bug (Gal 2:9, since fixed):

    BEFORE:
        ἵνα ἡμεῖς                             ← 2-word dangling fragment
        εἰς τὰ ἔθνη, αὐτοὶ δὲ εἰς τὴν περιτομήν·   ← both halves compressed

    AFTER:
        ἵνα ἡμεῖς εἰς τὰ ἔθνη,
        αὐτοὶ δὲ εἰς τὴν περιτομήν·

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_elided_parallels.py
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_elided_parallels.py --book gal
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
DEFAULT_OUTPUT = os.path.join(REPO_DIR, "private", "elided-parallel-scan.txt")

_FILE_MAP = {
    "61": "matt", "62": "mark", "63": "luke", "64": "john",
    "65": "acts", "66": "rom", "67": "1cor", "68": "2cor",
    "69": "gal", "70": "eph", "71": "phil", "72": "col",
    "73": "1thess", "74": "2thess", "75": "1tim", "76": "2tim",
    "77": "titus", "78": "phlm", "79": "heb", "80": "jas",
    "81": "1pet", "82": "2pet", "83": "1john", "84": "2john",
    "85": "3john", "86": "jude", "87": "rev",
}
_SLUG_TO_FILE = {v: k for k, v in _FILE_MAP.items()}

# ---------------------------------------------------------------------------
# MorphGNT loader
# ---------------------------------------------------------------------------

def _clean(word: str) -> str:
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]',
        '',
        word,
    )


# Map grave-accented vowels to acute equivalents. Greek prose uses the grave
# at word end where the word would have an acute in isolation. Pair markers
# listed in PAIR_TOKEN_CLASSES use the acute (dictionary) form — so we
# normalize the line form before lookup.
_GRAVE_TO_ACUTE = str.maketrans({
    "ὰ": "ά", "ὲ": "έ", "ὴ": "ή", "ὶ": "ί",
    "ὸ": "ό", "ὺ": "ύ", "ὼ": "ώ",
    "ἂ": "ἄ", "ἒ": "ἔ", "ἢ": "ἤ", "ἲ": "ἴ",
    "ὂ": "ὄ", "ὒ": "ὔ", "ὢ": "ὤ",
    "ἃ": "ἅ", "ἓ": "ἕ", "ἣ": "ἥ", "ἳ": "ἵ",
    "ὃ": "ὅ", "ὓ": "ὕ", "ὣ": "ὥ",
})


def _normalize_accent(word: str) -> str:
    return word.translate(_GRAVE_TO_ACUTE)


_verse_morph: dict[str, dict] = {}


def _load_morphgnt(book_slug: str):
    if book_slug in _verse_morph:
        return _verse_morph[book_slug]
    file_num = _SLUG_TO_FILE.get(book_slug)
    if not file_num:
        _verse_morph[book_slug] = {}
        return {}
    filepath = None
    for fname in os.listdir(MORPHGNT_DIR):
        if fname.startswith(file_num + "-"):
            filepath = os.path.join(MORPHGNT_DIR, fname)
            break
    if not filepath:
        _verse_morph[book_slug] = {}
        return {}

    verses: dict[tuple[int, int], list] = defaultdict(list)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, _text, word, _norm, lemma = parts
            ch = int(ref[2:4])
            vs = int(ref[4:6])
            cleaned = _clean(word)
            if cleaned:
                verses[(ch, vs)].append((cleaned, pos, parsing, lemma))
    _verse_morph[book_slug] = dict(verses)
    return dict(verses)


def _is_finite(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in ("I", "S", "D", "O")


def _is_participle(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "P"


def _is_infinitive(pos: str, parsing: str) -> bool:
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] == "N"


# ---------------------------------------------------------------------------
# Chapter parsing
# ---------------------------------------------------------------------------

VERSE_REF_RE = re.compile(r"^(\d+):(\d+)$")


def _parse_chapter(filepath: str) -> list[dict]:
    verses: list[dict] = []
    current = None
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            stripped = line.strip()
            if not stripped:
                continue
            m = VERSE_REF_RE.match(stripped)
            if m:
                if current:
                    verses.append(current)
                current = {
                    "ref": stripped,
                    "chapter": int(m.group(1)),
                    "verse": int(m.group(2)),
                    "lines": [],
                }
                continue
            if current is None:
                continue
            current["lines"].append(line)
    if current:
        verses.append(current)
    return verses


# ---------------------------------------------------------------------------
# Per-line morphology annotation
# ---------------------------------------------------------------------------

def _line_words(line_text: str, verse_consumable: dict) -> list[dict]:
    """Annotate one line's words with morphology by consuming from verse_consumable.

    Mutates verse_consumable (pops matched entries), so lines must be
    processed in order for a given verse.
    """
    result = []
    for raw in line_text.split():
        cleaned = _clean(raw)
        if not cleaned:
            continue
        entry = {
            "text": raw,
            "cleaned": cleaned,
            "pos": None,
            "parsing": None,
            "lemma": None,
            "is_fin": False,
            "is_ptc": False,
            "is_inf": False,
        }
        matches = verse_consumable.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry.update(pos=pos, parsing=parsing, lemma=lemma)
            entry["is_fin"] = _is_finite(pos, parsing)
            entry["is_ptc"] = _is_participle(pos, parsing)
            entry["is_inf"] = _is_infinitive(pos, parsing)
        result.append(entry)
    return result


def _build_verse_consumable(verse_words: list) -> dict:
    q: dict[str, list] = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        q[cw].append((pos, parsing, lemma))
    return {k: list(v) for k, v in q.items()}


# ---------------------------------------------------------------------------
# Pair-marker detection
# ---------------------------------------------------------------------------

# Tokens we consider pair markers. Note μέν and δέ always pair with ANOTHER
# token. εἴτε/οὔτε/ἤ pair with themselves.
PAIR_TOKEN_CLASSES = {
    "μέν": "men_de",
    "δέ": "men_de",
    "εἴτε": "eite",
    "οὔτε": "oute",
    "μήτε": "mete",
    "ἤ": "e",
    # ἀλλά: only used as a secondary signal when line is a compressed
    # participle-contrast (2 Cor 4:8-9 style).
    "ἀλλά": "alla",
    "ἀλλʼ": "alla",
}


def _pair_marker_indices(words: list[dict]) -> dict[str, list[int]]:
    """Return a map from pair-class to list of token indices where a marker
    of that class appears."""
    out: dict[str, list[int]] = defaultdict(list)
    for i, w in enumerate(words):
        norm = _normalize_accent(w["cleaned"])
        cls = PAIR_TOKEN_CLASSES.get(norm)
        if cls:
            out[cls].append(i)
    return out


def _token_normal(word: dict) -> str:
    return _normalize_accent(word["cleaned"])


def _has_mens_and_des(pair_idx: dict[str, list[int]], words: list[dict]) -> bool:
    """True iff this line contains a μέν...δέ pair *in order* (μέν before δέ).

    Discourse-level δέ ("νῦν δέ" / "ἐγὼ δέ" at the start of a line) followed
    later by a μέν is NOT a within-line pair — the μέν is pointing to a δέ
    on the next line. We require μέν index < δέ index.
    """
    if "men_de" not in pair_idx:
        return False
    cls_idxs = pair_idx["men_de"]
    men_positions = [i for i in cls_idxs if _token_normal(words[i]) == "μέν"]
    de_positions = [i for i in cls_idxs if _token_normal(words[i]) == "δέ"]
    if not men_positions or not de_positions:
        return False
    return min(men_positions) < max(de_positions)


def _has_doubled(pair_idx: dict[str, list[int]], cls: str) -> bool:
    return len(pair_idx.get(cls, [])) >= 2


# ---------------------------------------------------------------------------
# Analyzers
# ---------------------------------------------------------------------------

def _finite_count(words: list[dict]) -> int:
    return sum(1 for w in words if w["is_fin"])


def _imperative_or_finite_anywhere(words: list[dict]) -> bool:
    return any(w["is_fin"] for w in words)


def _classify_pair_marker(words: list[dict]) -> str | None:
    """Return the pair-class (as a human-readable label) if this line's words
    contain a self-contained paired construction, else None.

    Self-contained means both halves of the pair appear on this one line.
    """
    pair_idx = _pair_marker_indices(words)
    if _has_mens_and_des(pair_idx, words):
        # Additional check: the μέν and δέ should be reasonably close — and
        # they should not just be a speech-level sentence contrast. We catch
        # everything here and let downstream filters prune.
        return "μέν/δέ"
    if _has_doubled(pair_idx, "eite"):
        return "εἴτε/εἴτε"
    if _has_doubled(pair_idx, "oute"):
        return "οὔτε/οὔτε"
    if _has_doubled(pair_idx, "mete"):
        return "μήτε/μήτε"
    if _has_doubled(pair_idx, "e"):
        return "ἢ/ἤ"
    return None


def _classify_alla_contrast(words: list[dict]) -> bool:
    """Return True if line contains ≥2 ἀλλά/ἀλλʼ markers (bicola like
    2 Cor 4:8-9's participle contrast-chains)."""
    pair_idx = _pair_marker_indices(words)
    return len(pair_idx.get("alla", [])) >= 2


# ---------------------------------------------------------------------------
# Main analysis per verse
# ---------------------------------------------------------------------------

def analyze_verse(verse: dict, verse_words: list) -> list[dict]:
    """Return a list of finding-dicts for this verse."""
    findings: list[dict] = []
    if not verse_words:
        return findings

    consumable = _build_verse_consumable(verse_words)
    # Annotate every line in order so consumable is properly walked
    annotated_lines: list[list[dict]] = []
    for line_text in verse["lines"]:
        annotated_lines.append(_line_words(line_text, consumable))

    # ---- Pattern A: self-contained pair on one line with no finite verb ----
    for idx, words in enumerate(annotated_lines):
        if not words:
            continue
        pair_label = _classify_pair_marker(words)
        if pair_label:
            fin_count = _finite_count(words)
            if fin_count == 0:
                findings.append({
                    "line_idx": idx,
                    "line_text": verse["lines"][idx],
                    "pair": pair_label,
                    "pattern": "A-compressed",
                    "note": "both halves verbless on one line (elided)",
                })
            elif fin_count == 1:
                # Could still be compressed-asymmetric: one half has the
                # verb, the other shares it via ellipsis. Only flag if the
                # line is clearly compressible — i.e. long enough that
                # stacking would help readability. Require ≥8 words.
                if len(words) >= 8 and pair_label == "μέν/δέ":
                    findings.append({
                        "line_idx": idx,
                        "line_text": verse["lines"][idx],
                        "pair": pair_label,
                        "pattern": "A-compressed-one-finite",
                        "note": "one finite verb, long line — likely stackable",
                    })

    # ---- Pattern A': 2+ ἀλλά contrasts on one line (participle bicola) ----
    for idx, words in enumerate(annotated_lines):
        if not words:
            continue
        if _classify_alla_contrast(words):
            fin_count = _finite_count(words)
            if fin_count == 0:
                findings.append({
                    "line_idx": idx,
                    "line_text": verse["lines"][idx],
                    "pair": "ἀλλά/ἀλλά",
                    "pattern": "A-compressed-alla-chain",
                    "note": "multiple ἀλλά-contrasts compressed, no finite verb",
                })

    # ---- Pattern B: dangling short fragment then next line has mid-line δέ ----
    # Line N: short (≤3 Greek words), no finite verb.
    # Line N+1: contains μέν/δέ pair mid-line with no finite verb OR contains
    #   a δέ not at word-index 0/1 AND no finite verb.
    for idx in range(len(annotated_lines) - 1):
        cur = annotated_lines[idx]
        nxt = annotated_lines[idx + 1]
        if not cur or not nxt:
            continue
        if len(cur) > 3:
            continue
        if _imperative_or_finite_anywhere(cur):
            continue
        # Next line: does it have a mid-line δέ that buries a contrast?
        pair_idx = _pair_marker_indices(nxt)
        nxt_has_mens_des = _has_mens_and_des(pair_idx, nxt)
        nxt_has_de_midline = False
        de_positions = [i for i in pair_idx.get("men_de", []) if _token_normal(nxt[i]) == "δέ"]
        # δέ is postpositive so it appears at position ≥1. "Mid-line" meaning
        # there are real words after it forming a second half, i.e. δέ not
        # within the first 2 tokens isn't enough — we want to see that δέ
        # splits the line into two comparable halves.
        for dp in de_positions:
            # Words before δέ (excluding δέ itself): need to include word
            # immediately before δέ which is the leading noun/pronoun.
            before_real = [w for w in nxt[:dp]]
            after_real = [w for w in nxt[dp + 1:]]
            if len(before_real) >= 2 and len(after_real) >= 2:
                nxt_has_de_midline = True
                break
        if not (nxt_has_mens_des or nxt_has_de_midline):
            continue
        # Require next line to have NO finite verb (both halves elided)
        if _finite_count(nxt) > 0:
            # Some classic cases have ONE finite verb shared via ellipsis; still
            # surface if line is long enough AND there's a dangling cur.
            if len(nxt) < 8:
                continue
        findings.append({
            "line_idx": idx,
            "line_text": verse["lines"][idx],
            "next_line_idx": idx + 1,
            "next_line_text": verse["lines"][idx + 1],
            "pair": "μέν/δέ" if nxt_has_mens_des else "δέ (postpositive)",
            "pattern": "B-asymmetric",
            "note": (
                f"{len(cur)}-word dangling fragment followed by compressed "
                f"contrast line"
            ),
        })

    # NOTE: An earlier Pattern C ("two adjacent verbless lines bridged by δέ")
    # was removed because it flagged the DESIRED stacked layout as a bug.
    # Ellipsis-stacking puts each half on its own verbless line — exactly
    # the shape Pattern C matched.

    return findings


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def scan_all(books_filter: set[str] | None = None) -> list[dict]:
    all_findings: list[dict] = []
    for entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, entry)
        if not os.path.isdir(book_path):
            continue
        parts = entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else entry
        if books_filter and book_slug not in books_filter:
            continue
        morph = _load_morphgnt(book_slug)
        for chapter_file in sorted(os.listdir(book_path)):
            if not chapter_file.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, chapter_file)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = morph.get((v["chapter"], v["verse"]), [])
                flags = analyze_verse(v, verse_words)
                for flag in flags:
                    flag["file"] = chapter_file
                    flag["ref"] = v["ref"]
                    flag["book_slug"] = book_slug
                    all_findings.append(flag)
    return all_findings


def format_findings(findings: list[dict]) -> str:
    """Return the human-readable report block."""
    lines: list[str] = []
    lines.append("=== ELIDED PREDICATION PARALLEL SCAN ===")
    lines.append("")
    chapters_touched = {(f["book_slug"], f["file"]) for f in findings}
    lines.append(
        f"Found {len(findings)} candidates across "
        f"{len(chapters_touched)} chapters"
    )
    lines.append("")

    # Group by file for readability
    by_file: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        by_file[f["file"]].append(f)

    for fname in sorted(by_file.keys()):
        for f in by_file[fname]:
            lines.append(f"{f['file']} {f['ref']}  [{f['pattern']}]")
            lines.append(f"  Pair marker: {f['pair']}")
            lines.append(f"  Note: {f['note']}")
            lines.append("  Current layout:")
            if "next_line_text" in f:
                lines.append(f"    {f['line_text']}")
                lines.append(f"    {f['next_line_text']}")
            else:
                lines.append(f"    {f['line_text']}")
            lines.append("  Recommended: stack as parallel predications")
            lines.append("")

    # Per-book summary
    by_book: dict[str, int] = defaultdict(int)
    for f in findings:
        by_book[f["book_slug"]] += 1
    lines.append("=== PER-BOOK SUMMARY ===")
    for slug in sorted(by_book.keys()):
        lines.append(f"  {slug:<8} {by_book[slug]}")
    lines.append("")

    # Per-pattern summary
    by_pattern: dict[str, int] = defaultdict(int)
    for f in findings:
        by_pattern[f["pattern"]] += 1
    lines.append("=== PER-PATTERN SUMMARY ===")
    for pat in sorted(by_pattern.keys()):
        lines.append(f"  {pat:<28} {by_pattern[pat]}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--book",
        action="append",
        help="Limit scan to one or more book slugs (e.g. --book gal --book rom). Default: all.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Path to save full output (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Skip saving to disk.",
    )
    args = parser.parse_args()

    books_filter = set(args.book) if args.book else None
    findings = scan_all(books_filter)
    report = format_findings(findings)
    print(report)
    if not args.no_save:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Full output saved to {args.output}")


if __name__ == "__main__":
    main()
