#!/usr/bin/env python3
"""
scan_alla_antitheses.py — Find lines where ἀλλά introduces a corrective/
antithetical clause that should break to its own line.

Pattern (μή/οὐ ... ἀλλά antithesis):
    A line contains ἀλλά (or ἀλλʼ / ἀλλὰ) MID-LINE, AND the words before the
    ἀλλά on that line contain a negation (μή, οὐ, οὐχ, οὐκ, μηδέ, οὐδέ, etc.).
    The ἀλλά introduces the corrective positive and should start its own line.

Existing subordinator scanners only check ἵνα/ὅτι/ὅταν/etc., not ἀλλά. The
correlative pair μή/ἀλλά (and οὐ/ἀλλά) is a standard colometric break point
per the methodology doc. Rom 12:3 was missed by all scanners — it had a
μή ὑπερφρονεῖν / ἀλλὰ φρονεῖν antithesis buried mid-line.

Excludes:
  * ἀλλά at line start (already correct)
  * ἀλλά not preceded by negation on the same line
  * Splits that would leave a <10 char prefix

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_alla_antitheses.py
"""

import os
import re
import sys
import unicodedata

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")

MIN_PREFIX_CHARS = 10

VERSE_REF_RE = re.compile(r"^(\d+):(\d+)$")


# Combining marks to STRIP (accents, but NOT breathing marks).
# We keep smooth breathing (U+0313) and rough breathing (U+0314) so that
# οὐ (negation, smooth breathing) is distinguishable from οὗ (relative,
# rough breathing) — these collapse to the same letters otherwise.
_ACCENTS_TO_STRIP = {
    "\u0300",  # combining grave
    "\u0301",  # combining acute
    "\u0302",  # combining circumflex
    "\u0304",  # combining macron
    "\u0306",  # combining breve
    "\u0308",  # combining diaeresis
    "\u0342",  # combining greek perispomeni
    "\u0344",  # combining greek dialytika tonos
    "\u0345",  # combining greek ypogegrammeni (iota subscript)
}


def _strip_accents(text):
    """Normalize to NFD, drop accent marks (keep breathing marks), recompose."""
    decomposed = unicodedata.normalize("NFD", text)
    no_accents = "".join(c for c in decomposed if c not in _ACCENTS_TO_STRIP)
    return unicodedata.normalize("NFC", no_accents)


# Negation lemmas/forms — accent-stripped (but breathing-preserved) for matching.
# Smooth breathing on οὐ matters: it distinguishes negation οὐ from relative οὗ.
_NEGATION_RAW = [
    "μή", "μὴ",
    "οὐ", "οὔ", "οὒ",
    "οὐχ", "οὐχί", "οὐχὶ",
    "οὐκ", "οὐκέτι",
    "οὐδέ", "οὐδέποτε", "οὐδαμῶς",
    "μηδέ", "μηκέτι", "μηδέποτε",
]
NEGATIONS = {_strip_accents(w) for w in _NEGATION_RAW}

# ἀλλά forms (with various accents and elision)
_ALLA_RAW = ["ἀλλά", "ἀλλὰ", "ἀλλʼ", "ἀλλ'"]
ALLA_FORMS = {_strip_accents(w) for w in _ALLA_RAW}

# Punctuation/marker chars to strip from words for matching
PUNCT_RE = re.compile(
    r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\(\)\[\]⟦⟧—\u037E\u0387\u00B7"\u201C\u201D\u2018\u2019]'
)


def _clean_word(word):
    """Strip punctuation from a token (preserve apostrophe-elision marks)."""
    # Keep ʼ and ' since ἀλλʼ uses them
    return re.sub(
        r'[,.\;\·⸀⸁⸂⸃⸄⸅\(\)\[\]⟦⟧—\u037E\u0387\u00B7"\u201C\u201D]',
        '',
        word,
    ).strip()


def _norm(word):
    """Clean punctuation and strip accents for matching."""
    return _strip_accents(_clean_word(word))


def _parse_chapter(filepath):
    """Return list of {ref, chapter, verse, lines}."""
    verses = []
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


def _is_alla_token(norm_token):
    """Match ἀλλά / ἀλλὰ / ἀλλʼ in any accent form (already accent-stripped)."""
    if not norm_token:
        return False
    return norm_token in ALLA_FORMS


def _is_negation_token(norm_token):
    if not norm_token:
        return False
    return norm_token in NEGATIONS


def analyze_line(line_text):
    """Return dict with break info if this line is a μή/οὐ ... ἀλλά antithesis
    that should break before ἀλλά, else None.
    """
    stripped_line = line_text.strip()
    if not stripped_line:
        return None

    tokens = stripped_line.split()
    if len(tokens) < 2:
        return None

    # Find an ἀλλά token that is NOT the first token
    alla_idx = None
    for i, tok in enumerate(tokens):
        if i == 0:
            continue
        # Allow leading conjunction attached: e.g., "καί" before ἀλλά —
        # we still flag if ἀλλά itself is mid-line (not first).
        if _is_alla_token(_norm(tok)):
            alla_idx = i
            break

    if alla_idx is None:
        return None

    # Check the prefix tokens for any negation
    prefix_tokens = tokens[:alla_idx]
    has_negation = any(_is_negation_token(_norm(t)) for t in prefix_tokens)
    if not has_negation:
        return None

    # Compute prefix character length (joined with spaces, as it would appear)
    prefix_text = " ".join(prefix_tokens).rstrip(",··;")
    # Strip trailing punctuation for the length check
    prefix_clean = re.sub(r'[\s,.\;\·]+$', '', prefix_text)
    if len(prefix_clean) < MIN_PREFIX_CHARS:
        return None

    # Find which negation matched (for reporting)
    neg_form = None
    for t in prefix_tokens:
        if _is_negation_token(_norm(t)):
            neg_form = _clean_word(t)
            break

    return {
        "alla_token": _clean_word(tokens[alla_idx]),
        "negation": neg_form,
        "prefix_text": prefix_text,
        "alla_idx": alla_idx,
    }


def scan_all():
    findings = []
    for entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, entry)
        if not os.path.isdir(book_path):
            continue
        for chapter_file in sorted(os.listdir(book_path)):
            if not chapter_file.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, chapter_file)
            verses = _parse_chapter(filepath)
            for v in verses:
                for idx, line_text in enumerate(v["lines"]):
                    flag = analyze_line(line_text)
                    if not flag:
                        continue
                    findings.append({
                        "file": chapter_file,
                        "ref": v["ref"],
                        "line_idx": idx,
                        "line": line_text,
                        "negation": flag["negation"],
                        "alla_token": flag["alla_token"],
                    })
    return findings


def main():
    findings = scan_all()
    print(f"Found {len(findings)} μή/ἀλλά antithesis candidates\n")
    for f in findings:
        print(f"{f['file']} {f['ref']}:{f['line_idx']}:")
        print(f"  {f['line']}")
        print(
            f"  proposed: break before {f['alla_token']} "
            f"(negation: {f['negation']})"
        )
        print()


if __name__ == "__main__":
    main()
