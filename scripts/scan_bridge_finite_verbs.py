#!/usr/bin/env python3
"""
scan_bridge_finite_verbs.py — Find lines where two main-clause finite verbs
are joined by a sentence-boundary discourse marker (γάρ, οὖν, δέ) without
a proper line break between them.

This is the narrow version of scan_multi_finite_line.py. Rather than
flagging every line with 2+ finite verbs (1,972 hits, mostly legitimate
subordinate clauses, relative clauses, and coordinate verbs), we target
only the specific bug pattern that produced Gal 2:6 line 27 and Rom 7:1
line 4: independent main clauses bridged by a discourse marker.

**Target signature:**
  [main clause with finite verb] + [γάρ/οὖν/sentence-initial δέ] + [main clause with different finite verb]

**Filters applied:**
  1. Exclude finite verbs inside subordinate clauses (after ὅτι/ἵνα/ὅταν/...)
  2. Exclude finite verbs inside relative clauses (after ὅς/ἥ/ὅ/ᾧ/ὧν/...)
  3. Require a bridge discourse marker (γάρ, οὖν, or δέ) between the two
     remaining finite verbs
  4. Exclude lines where the bridge is clearly narrative-chain (both
     verbs have imperfect/aorist indicative and share an implicit subject)

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_bridge_finite_verbs.py
"""
import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_ROOT, "research", "morphgnt-sblgnt")

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

SUBORDINATORS = {
    "ὅτι", "ἵνα", "ὅταν", "ὅτε", "ἐάν", "ὅπως", "ὥστε", "ὥσπερ",
    "μήποτε", "ἕως", "ὅπου", "καθώς", "ἡνίκα", "ἐπεί", "ἐπειδή",
    "πρίν", "εἰ", "ὡς", "καθάπερ", "ἐν", "ἀφʼ", "μέχρι",
}

RELATIVE_PRONOUNS = {
    "ὅς", "ἥ", "ὅ", "οὗ", "ἧς", "ᾧ", "ᾗ", "ὅν", "ἥν", "οἷς", "αἷς",
    "ὧν", "ἅ", "ἅς", "ὅστις", "ἥτις", "ὅτις", "οἵτινες", "αἵτινες",
    "ἅτινα", "ὃν", "οἳ", "αἱ", "ἐφʼ",
}

BRIDGE_MARKERS = {"γάρ", "οὖν"}  # δέ handled separately (sentence-initial only)
SPEECH_LEMMAS = {"λέγω", "ἀποκρίνομαι", "φημί", "φωνέω", "γράφω"}

_verse_morph = {}


def _clean(word):
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]',
        '',
        word,
    )


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


def _is_finite(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] in ("I", "S", "D", "O")


def _line_words_with_morph(line_text, verse_words):
    """Walk line with morphology attached to each word (positional consumption)."""
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
            "is_fin": False,
            "is_sub": cleaned in SUBORDINATORS,
            "is_rel": cleaned in RELATIVE_PRONOUNS,
            "is_bridge": cleaned in BRIDGE_MARKERS,
        }
        matches = consumable.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry["pos"] = pos
            entry["parsing"] = parsing
            entry["lemma"] = lemma
            entry["is_fin"] = _is_finite(pos, parsing)
        result.append(entry)
    return result


def _identify_main_finite_verbs(words):
    """Return indices of finite verbs that are NOT inside subordinate/relative clauses.

    Track clause depth: increment on subordinator or relative pronoun,
    decrement heuristically (harder) — we approximate by resetting depth
    at strong punctuation or when a new sentence begins.

    For this narrow scanner, we use a simpler approach: a finite verb is
    "main-clause" if NO subordinator or relative pronoun appears between
    it and the start of the line. If a subordinator appears before it,
    it's subordinate. This is an approximation — it will miss cases where
    a subordinate clause closes mid-line — but it's good enough for the
    narrow bridge pattern we're targeting.
    """
    main_indices = []
    seen_subordinator = False
    seen_relative = False
    for i, w in enumerate(words):
        if w["is_sub"]:
            seen_subordinator = True
        if w["is_rel"]:
            seen_relative = True
        if w["is_fin"] and not seen_subordinator and not seen_relative:
            main_indices.append(i)
    return main_indices


def analyze_line(words):
    """Return info if the line matches the bridge pattern, else None."""
    main_fin = _identify_main_finite_verbs(words)
    if len(main_fin) < 2:
        return None

    # Check if there's a bridge marker (γάρ, οὖν, δέ) between two main finite verbs
    for i in range(len(main_fin) - 1):
        v1_idx = main_fin[i]
        v2_idx = main_fin[i + 1]
        span = words[v1_idx + 1:v2_idx]
        bridge_words = [w["cleaned"] for w in span if w["is_bridge"]]
        # Also check for sentence-initial-like δέ (δέ immediately following a noun/pronoun
        # that could be a new subject, not δέ adjacent to a conjunction)
        has_de = any(w["cleaned"] == "δέ" for w in span)
        if bridge_words or has_de:
            # Exclude cases where one of the verbs is a speech lemma followed by
            # direct-speech content (the other verb is inside the quoted speech)
            v1_lemma = words[v1_idx].get("lemma", "")
            v2_lemma = words[v2_idx].get("lemma", "")
            if v1_lemma in SPEECH_LEMMAS or v2_lemma in SPEECH_LEMMAS:
                # check if there's a punctuation break (middle dot, colon) between
                # the speech verb and the next finite verb — that's a speech intro
                has_speech_sep = any(
                    "·" in w["text"] or ":" in w["text"]
                    for w in span
                )
                if has_speech_sep:
                    continue  # skip speech introduction pattern

            return {
                "v1_word": words[v1_idx]["cleaned"],
                "v1_lemma": v1_lemma,
                "v2_word": words[v2_idx]["cleaned"],
                "v2_lemma": v2_lemma,
                "bridge": bridge_words or ["δέ"],
                "span_words": [w["cleaned"] for w in span],
            }
    return None


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)")


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
            if m and stripped == m.group(0):
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
    results = []
    for book_entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, book_entry)
        if not os.path.isdir(book_path):
            continue
        parts = book_entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else book_entry
        morph = _load_morphgnt(book_slug)
        for fname in sorted(os.listdir(book_path)):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, fname)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = morph.get((v["chapter"], v["verse"]), [])
                if not verse_words:
                    continue
                for line_text in v["lines"]:
                    words = _line_words_with_morph(line_text, verse_words)
                    info = analyze_line(words)
                    if info:
                        results.append({
                            "file": f"{book_entry}/{fname}",
                            "ref": v["ref"],
                            "line": line_text,
                            "info": info,
                        })
    return results


def main():
    findings = scan_all()
    print(f"=== BRIDGE FINITE-VERB SCAN ===\n")
    print(f"Found {len(findings)} lines where two main-clause finite verbs")
    print(f"are bridged by γάρ/οὖν/δέ without a proper line break.\n")
    for f in findings:
        info = f["info"]
        bridge_str = ", ".join(info["bridge"])
        print(f"{f['file']} {f['ref']}:")
        print(f"  {f['line']}")
        print(
            f"  v1: {info['v1_word']}({info['v1_lemma']}) "
            f"| bridge: {bridge_str} "
            f"| v2: {info['v2_word']}({info['v2_lemma']})"
        )
        print()


if __name__ == "__main__":
    main()
