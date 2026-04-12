#!/usr/bin/env python3
"""
scan_genabs_absorbed.py — Find genitive absolutes absorbed into line merges.

A genitive absolute is a grammatically independent temporal/circumstantial
frame (participle in genitive + subject in genitive, distinct from the main
clause subject). Per handoffs/02-colometry-method.md, genitive absolutes
should stand alone as their own colometric lines.

This scanner finds lines where a genitive-absolute construction is present
alongside OTHER content (another participle, a finite verb, or non-gen-abs
material), meaning the gen abs was absorbed into an adjacent element rather
than standing as its own frame.

Example — Acts 1:9 (before fix):
    καὶ ταῦτα εἰπὼν βλεπόντων αὐτῶν ἐπήρθη
                    ^^^^^^^^^^^^^^^ <-- gen abs absorbed with εἰπών and ἐπήρθη

After the fix:
    καὶ ταῦτα εἰπὼν
    βλεπόντων αὐτῶν       <-- gen abs on its own line (interjectory)
    ἐπήρθη
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")

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


def _clean(word):
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]',
        '',
        word,
    )


_verse_morph = {}


def _load_morphgnt(book_slug):
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

    verses = defaultdict(list)
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


def _parse_field(parsing, idx):
    """Safe access to MorphGNT parsing field characters."""
    if idx < len(parsing):
        return parsing[idx]
    return ""


def _is_gen_participle(pos, parsing):
    """Verb, participle mood, genitive case."""
    if not pos.startswith("V"):
        return False
    if _parse_field(parsing, 3) != "P":
        return False
    if _parse_field(parsing, 4) != "G":
        return False
    return True


def _is_genitive(pos, parsing):
    """Nominal (noun, pronoun, article, adjective) in genitive case."""
    if pos.startswith("N-") or pos.startswith("RA") or pos.startswith("RP") or pos.startswith("RD") or pos.startswith("A-") or pos.startswith("RR") or pos.startswith("RI"):
        return _parse_field(parsing, 2) == "G"
    return False


def _is_finite(pos, parsing):
    return pos.startswith("V") and _parse_field(parsing, 3) in ("I", "S", "D", "O")


def _is_nom_participle(pos, parsing):
    return (
        pos.startswith("V")
        and _parse_field(parsing, 3) == "P"
        and _parse_field(parsing, 4) == "N"
    )


def _line_morph(line_text, verse_words):
    """Walk line and attach morphology to each word (positional consumption)."""
    consumable = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        consumable[cw].append((pos, parsing, lemma))
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
        }
        matches = consumable.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry["pos"] = pos
            entry["parsing"] = parsing
            entry["lemma"] = lemma
        result.append(entry)
    return result


def detect_absorbed_genabs(line_morph):
    """Return info if the line contains a gen abs construction alongside other
    content that suggests absorption, else None.

    A genitive absolute needs:
    - A genitive participle (V...PG...)
    - A nearby genitive noun/pronoun acting as its subject
    - Content on the same line that is NOT part of the gen abs construction
      (another participle of different case, a finite verb, etc.)
    """
    # Find genitive participles and their indices
    gen_ptc_indices = [
        i for i, w in enumerate(line_morph)
        if w["pos"] and _is_gen_participle(w["pos"], w["parsing"])
    ]
    if not gen_ptc_indices:
        return None

    # For each gen participle, check if there's a genitive nominal within ±3 words
    gen_abs_spans = []
    for gpi in gen_ptc_indices:
        start = max(0, gpi - 3)
        end = min(len(line_morph), gpi + 4)
        has_gen_subject = False
        for j in range(start, end):
            if j == gpi:
                continue
            w = line_morph[j]
            if w["pos"] and _is_genitive(w["pos"], w["parsing"]):
                has_gen_subject = True
                break
        if has_gen_subject:
            gen_abs_spans.append(gpi)

    if not gen_abs_spans:
        return None

    # Now check if the line also contains:
    # - A non-genitive participle (e.g. nominative attending circumstantial)
    # - OR a finite verb
    # - OR an accusative/dative participle
    # If so, the gen abs is "absorbed" — it should stand alone.
    has_other_ptc = False
    has_finite = False
    other_ptc_examples = []
    for i, w in enumerate(line_morph):
        if not w["pos"]:
            continue
        if _is_finite(w["pos"], w["parsing"]):
            has_finite = True
        elif _parse_field(w["parsing"], 3) == "P" and _parse_field(w["parsing"], 4) != "G":
            has_other_ptc = True
            other_ptc_examples.append(w["cleaned"])

    if not (has_other_ptc or has_finite):
        return None

    # Build the gen abs surface form for reporting
    gen_abs_word = line_morph[gen_abs_spans[0]]["cleaned"]
    return {
        "gen_abs_word": gen_abs_word,
        "gen_abs_count": len(gen_abs_spans),
        "has_other_ptc": has_other_ptc,
        "has_finite_verb": has_finite,
        "other_ptc_examples": other_ptc_examples,
    }


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)$")


def _parse_chapter(filepath):
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


def scan_all():
    findings = []
    for entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, entry)
        if not os.path.isdir(book_path):
            continue
        parts = entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else entry
        morph = _load_morphgnt(book_slug)

        for chapter_file in sorted(os.listdir(book_path)):
            if not chapter_file.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, chapter_file)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = morph.get((v["chapter"], v["verse"]), [])
                if not verse_words:
                    continue
                for line_text in v["lines"]:
                    line_words = _line_morph(line_text, verse_words)
                    info = detect_absorbed_genabs(line_words)
                    if not info:
                        continue
                    findings.append({
                        "file": chapter_file,
                        "ref": v["ref"],
                        "line": line_text,
                        "info": info,
                    })
    return findings


def main():
    findings = scan_all()
    print(f"Found {len(findings)} lines with absorbed genitive absolutes\n")
    for f in findings:
        info = f["info"]
        signal = []
        if info["has_other_ptc"]:
            signal.append(f"other ptc ({', '.join(info['other_ptc_examples'][:3])})")
        if info["has_finite_verb"]:
            signal.append("finite verb")
        print(f"{f['file']} {f['ref']}:")
        print(f"  {f['line']}")
        print(f"  gen abs: {info['gen_abs_word']} | absorbed with: {', '.join(signal)}")
        print()


if __name__ == "__main__":
    main()
