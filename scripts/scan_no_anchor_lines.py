#!/usr/bin/env python3
"""
scan_no_anchor_lines.py — Find lines that lack a thought-marking anchor
and are therefore candidates for merging into a neighbor.

A line is "anchored" if it has at least one of:
  1. A finite verb (person 1/2/3, mood I/S/D/O)
  2. An infinitive (mood N)
  3. A participle (mood P)
  4. A substantive (noun/adjective/pronoun) in nominative/accusative/vocative
     case that is NOT governed by a preposition on the same line

A line is UNANCHORED (merge candidate) if it has none of the above —
only prep phrases, bare genitive/dative modifiers, particles, articles,
or other structural-only material.

Rationale: per the container-not-originator principle, a line must carry
a thought-marking element (predication OR independent substantive). Lines
consisting only of structural-syntax scaffolding (prep phrases, modifier
cases, particles) are containers without originators and belong inside
the atomic thought unit of a neighboring anchored line.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_no_anchor_lines.py
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_no_anchor_lines.py --book rom
"""
import os
import re
import sys
import argparse
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


def _is_finite_verb(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] in ("I", "S", "D", "O")


def _is_infinitive(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] == "N"


def _is_participle(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] == "P"


def _is_preposition(pos):
    return pos == "P-"


def _is_substantive(pos):
    # Noun, adjective, pronoun (any kind), article can all be substantive heads
    # But articles alone don't count; adjectives alone rarely count
    # Safest: nouns and substantive pronouns (RP personal, RD demonstrative,
    # RI interrogative, RR relative)
    return (pos.startswith("N") or pos.startswith("A-") or
            pos in ("RP", "RD", "RI", "RR", "RX"))


def _case_of(pos, parsing):
    if len(parsing) < 5:
        return None
    return parsing[4]


def _line_words_with_morph(line_text, verse_queue):
    """Attach morph to each word, consuming verse queue positionally."""
    result = []
    for raw in line_text.split():
        cleaned = _clean(raw)
        if not cleaned:
            continue
        entry = {"text": raw, "cleaned": cleaned,
                 "pos": None, "parsing": None, "lemma": None}
        matched = None
        for i, (cw, pos, parsing, lemma) in enumerate(verse_queue):
            if cw == cleaned:
                matched = i
                break
        if matched is not None:
            cw, pos, parsing, lemma = verse_queue.pop(matched)
            entry["pos"] = pos
            entry["parsing"] = parsing
            entry["lemma"] = lemma
        result.append(entry)
    return result


def _line_has_anchor(words):
    """Return (has_anchor, reason) where reason is a short tag.

    A line is anchored if it has:
    - A finite verb (tag: 'fin-verb')
    - An infinitive (tag: 'inf')
    - A participle (tag: 'ptc')
    - A substantive in N/A/V case that is not preceded on the line by a
      preposition whose object it is (tag: 'subst-NAV')
    """
    # First check verbs
    for w in words:
        if not w["pos"]:
            continue
        if _is_finite_verb(w["pos"], w["parsing"]):
            return True, f"fin-verb:{w['cleaned']}"
        if _is_infinitive(w["pos"], w["parsing"]):
            return True, f"inf:{w['cleaned']}"
        if _is_participle(w["pos"], w["parsing"]):
            return True, f"ptc:{w['cleaned']}"

    # Noun-phrase-led line: if the first significant content word
    # (skipping leading conjunctions, particles, and interjections) is
    # a substantive or article in case N/A/D/V, the line opens with its
    # own head NP and counts as anchored. Catches epistolary addressee
    # datives (Col 1:2) and conjunction-led noun phrases (Mark 14:12
    # "Καὶ τῇ πρώτῃ ἡμέρᾳ τῶν ἀζύμων").
    for first in words:
        if not first["pos"]:
            continue
        # Skip conjunctions, particles, interjections
        if (first["pos"].startswith("C") or first["pos"] == "X-" or
                first["pos"] == "I-"):
            continue
        is_nph = (first["pos"].startswith("N") or
                  first["pos"].startswith("A-") or
                  first["pos"] == "RA" or
                  first["pos"] in ("RP", "RD", "RI", "RR", "RX"))
        if is_nph:
            case = _case_of(first["pos"], first["parsing"])
            if case in ("N", "A", "D", "V"):
                return True, f"head-subst-{case}:{first['cleaned']}"
        # First significant word is something else (prep, verb already
        # checked above, etc.) — fall through to substantive-search test
        break

    # No verbal anchor — look for substantive anchor
    # Walk the line tracking whether we're inside a prep phrase.
    # A prep phrase extends from a preposition until the next non-article,
    # non-adjective, non-conjunction, non-pronoun (approximation).
    # Simpler heuristic: a substantive is prep-governed if ANY preposition
    # appeared earlier on the line AND the substantive is in a case governed
    # by a prep (G/D/A — not N/V).
    # Even simpler: if the line contains any preposition, and the only
    # substantives are in cases compatible with prep government, treat
    # them all as prep-objects.

    has_prep = any(w["pos"] and _is_preposition(w["pos"]) for w in words)

    substantives = []
    for w in words:
        if not w["pos"]:
            continue
        if _is_substantive(w["pos"]):
            case = _case_of(w["pos"], w["parsing"])
            substantives.append((w, case))

    # Find a substantive in N/A/V that's not the object of a prep on this line.
    # Rule of thumb: if there's no prep, any N/A/V substantive is a standalone
    # anchor. If there IS a prep, substantives governed by it would be in G/D/A,
    # and we should only accept N/V (never prep-governed) as standalone anchors;
    # accept A only if it appears BEFORE the first preposition on the line.
    first_prep_idx = None
    for i, w in enumerate(words):
        if w["pos"] and _is_preposition(w["pos"]):
            first_prep_idx = i
            break

    for i, w in enumerate(words):
        if not w["pos"] or not _is_substantive(w["pos"]):
            continue
        case = _case_of(w["pos"], w["parsing"])
        if case in ("N", "V"):
            # Nominative or vocative — never a prep-object, always an anchor
            return True, f"subst-{case}:{w['cleaned']}"
        if case == "A":
            # Accusative — could be a direct object / topic, or a prep-object
            if first_prep_idx is None or i < first_prep_idx:
                return True, f"subst-A:{w['cleaned']}"
            # After a prep — assume prep-governed, skip
            continue
        # G / D / other — treat as modifier, skip
        continue

    return False, "no-anchor"


def _is_bare_structural(words):
    """True if the line contains only structural material: preps, particles,
    articles, conjunctions, modifier-case substantives (G/D), adjectives
    agreeing with absent head. This is the complement of _line_has_anchor
    but phrased as a positive test for reporting."""
    has_anchor, reason = _line_has_anchor(words)
    return not has_anchor


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


def scan_all(book_filter=None):
    results = []
    for book_entry in sorted(os.listdir(V4_DIR)):
        book_path = os.path.join(V4_DIR, book_entry)
        if not os.path.isdir(book_path):
            continue
        parts = book_entry.split("-", 1)
        book_slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else book_entry
        if book_filter and book_slug != book_filter:
            continue
        morph = _load_morphgnt(book_slug)
        for fname in sorted(os.listdir(book_path)):
            if not fname.endswith(".txt"):
                continue
            filepath = os.path.join(book_path, fname)
            verses = _parse_chapter(filepath)
            for v in verses:
                verse_words = list(morph.get((v["chapter"], v["verse"]), []))
                if not verse_words:
                    continue
                verse_queue = list(verse_words)
                annotated = []
                for line_text in v["lines"]:
                    annotated.append(_line_words_with_morph(line_text, verse_queue))

                n = len(annotated)
                for i, line_words in enumerate(annotated):
                    if not line_words:
                        continue
                    has_anchor, reason = _line_has_anchor(line_words)
                    if has_anchor:
                        continue

                    # Unanchored line — find merge target (nearest preceding
                    # anchored line in the same verse)
                    merge_target_idx = None
                    for j in range(i - 1, -1, -1):
                        if _line_has_anchor(annotated[j])[0]:
                            merge_target_idx = j
                            break

                    results.append({
                        "file": f"{book_entry}/{fname}",
                        "ref": v["ref"],
                        "line_idx": i,
                        "total_lines": n,
                        "line_text": v["lines"][i],
                        "reason": reason,
                        "merge_target_idx": merge_target_idx,
                        "merge_target_text": (v["lines"][merge_target_idx]
                                              if merge_target_idx is not None else None),
                        "verse_lines": v["lines"],
                    })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None, help="Filter to one book slug (e.g., rom)")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args()

    findings = scan_all(book_filter=args.book)
    print(f"=== NO-ANCHOR LINE SCAN ===\n")
    print(f"Total unanchored lines found: {len(findings)}\n")

    # Bucket by book
    by_book = defaultdict(int)
    for f in findings:
        book = f["file"].split("/")[0]
        by_book[book] += 1
    for book, n in sorted(by_book.items()):
        print(f"  {book}: {n}")
    print()

    if args.summary_only:
        return

    for f in findings:
        print(f"{f['file']} {f['ref']} (line {f['line_idx']+1}/{f['total_lines']}):")
        for j, ln in enumerate(f["verse_lines"]):
            marker = ""
            if j == f["line_idx"]:
                marker = "  >>>"
            elif j == f["merge_target_idx"]:
                marker = "  TGT"
            else:
                marker = "     "
            print(f"  {marker} {ln}")
        print(f"  [{f['reason']}]")
        print()


if __name__ == "__main__":
    main()
