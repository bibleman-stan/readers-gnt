#!/usr/bin/env python3
"""
scan_vocative_apposition.py — Find vocative-only lines that are
grammatically appositive to a preceding 2nd-person marker in the
same verse, and flag them as candidates for merging into the
preceding line.

Reflects (does not impose) the following structural criterion:

  A vocative is a candidate for merging when, within the same verse:
    1. The vocative-bearing line is NOT the first line of the verse
       (i.e., not verse-initial / sentence-initial)
    2. The vocative-bearing line is NOT the last line of the verse
       (verse-final vocatives are distinct tail-address acts)
    3. At least one preceding line in the same verse contains
       either (a) a 2nd-person personal pronoun (σύ / ὑμεῖς family)
       or (b) a 2nd-person finite verb

When all three are true, the vocative is grammatically in apposition
to an already-established second-person address and its own line
fragments a single thought for no rhetorical gain.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_vocative_apposition.py
"""
import os
import re
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


def _is_vocative(pos, parsing):
    # Case is parsing[4] for nouns/adjectives/participles/articles
    # POS starts with N (noun), A (adjective), RA (article)
    if not pos or len(pos) < 1:
        return False
    if not (pos.startswith("N") or pos.startswith("A") or pos.startswith("RA")):
        return False
    if len(parsing) < 5:
        return False
    return parsing[4] == "V"


def _is_2p_pronoun(pos, parsing, lemma):
    # Personal pronoun (RP) with 2nd person.
    # MorphGNT pronouns encode person via LEMMA (σύ for all forms of "you"
    # both singular and plural), not parsing[0] which is dashes for pronouns.
    if pos != "RP":
        return False
    return lemma == "σύ"


def _is_2p_finite_verb(pos, parsing):
    # Verb, finite mood (I=indicative, S=subjunctive, D=imperative, O=optative),
    # 2nd person
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    mood = parsing[3]
    if mood not in ("I", "S", "D", "O"):
        return False
    # Person is parsing[0]
    if len(parsing) < 1:
        return False
    return parsing[0] == "2"


def _line_words_with_morph(line_text, verse_queue):
    """Walk line with morphology attached positionally (consuming verse queue)."""
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
            "is_voc": False,
            "is_2p_pron": False,
            "is_2p_verb": False,
        }
        # Find next matching word in verse queue
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
            entry["is_voc"] = _is_vocative(pos, parsing)
            entry["is_2p_pron"] = _is_2p_pronoun(pos, parsing, lemma)
            entry["is_2p_verb"] = _is_2p_finite_verb(pos, parsing)
        result.append(entry)
    return result


def _is_vocative_only_line(words):
    """A line counts as 'vocative-only' if every content word is vocative
    or is a vocative modifier (possessive μου, article τοῦ, adjective).
    No finite verb, no non-vocative noun."""
    if not words:
        return False
    has_voc = any(w["is_voc"] for w in words)
    if not has_voc:
        return False
    # Any finite verb disqualifies
    for w in words:
        if w["pos"] and w["pos"].startswith("V"):
            if len(w["parsing"]) >= 4 and w["parsing"][3] in ("I", "S", "D", "O"):
                return False
    # Any non-vocative noun/adjective (not modifying the vocative) disqualifies
    # Approximation: if a noun/adj/article is not vocative, it's probably not part of the vocative phrase
    for w in words:
        if w["pos"] and (w["pos"].startswith("N") or w["pos"].startswith("A")):
            if not w["is_voc"]:
                # Exception: possessive pronouns, articles (RA), particles
                return False
    return True


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
                verse_words = list(morph.get((v["chapter"], v["verse"]), []))
                if not verse_words:
                    continue
                # Annotate each line with morph (consume the queue positionally)
                verse_queue = list(verse_words)
                annotated_lines = []
                for line_text in v["lines"]:
                    words = _line_words_with_morph(line_text, verse_queue)
                    annotated_lines.append(words)

                # Find vocative-only lines
                n = len(annotated_lines)
                for i, line_words in enumerate(annotated_lines):
                    if not _is_vocative_only_line(line_words):
                        continue

                    # Classify position
                    if i == 0:
                        position = "verse-initial"
                    elif i == n - 1:
                        position = "verse-final"
                    else:
                        position = "mid"

                    # For mid vocatives, check preceding lines for 2p marker
                    # BUT reset context at speech-intro punctuation: if a preceding
                    # line ends with "·" (middle dot), we treat that as a speech
                    # boundary — 2p markers before the boundary belong to a different
                    # discourse layer than the vocative after it.
                    preceding_has_2p_pron = False
                    preceding_has_2p_verb = False
                    preceding_pron_tokens = []
                    preceding_verb_tokens = []
                    reset_after = -1  # index of most recent speech-intro boundary
                    for j in range(i):
                        line_raw = v["lines"][j].rstrip()
                        if line_raw.endswith("·") or line_raw.endswith(":"):
                            reset_after = j
                    for j in range(reset_after + 1, i):
                        for w in annotated_lines[j]:
                            if w["is_2p_pron"]:
                                preceding_has_2p_pron = True
                                preceding_pron_tokens.append(w["cleaned"])
                            if w["is_2p_verb"]:
                                preceding_has_2p_verb = True
                                preceding_verb_tokens.append(w["cleaned"])

                    if position == "mid" and (preceding_has_2p_pron or preceding_has_2p_verb):
                        classification = "APPOSITION-CANDIDATE"
                    elif position == "mid" and reset_after >= 0 and reset_after == i - 1:
                        # Immediately preceded by a speech-intro boundary
                        classification = "INITIATING-QUOTED-SPEECH"
                    elif position == "verse-initial":
                        classification = "INITIATING"
                    elif position == "verse-final":
                        classification = "TRAILING"
                    else:
                        # mid without preceding 2p — still treat as initiating
                        classification = "MID-NO-2P"

                    voc_text = " ".join(w["text"] for w in line_words)
                    results.append({
                        "file": f"{book_entry}/{fname}",
                        "ref": v["ref"],
                        "line_idx": i,
                        "total_lines": n,
                        "voc_text": voc_text,
                        "classification": classification,
                        "preceding_2p_pronouns": preceding_pron_tokens,
                        "preceding_2p_verbs": preceding_verb_tokens,
                        "preceding_lines": v["lines"][:i],
                        "following_lines": v["lines"][i+1:],
                    })
    return results


def main():
    findings = scan_all()
    # Count by classification
    counts = defaultdict(int)
    for f in findings:
        counts[f["classification"]] += 1

    print("=== VOCATIVE APPOSITION SCAN ===\n")
    print(f"Total vocative-only lines found: {len(findings)}")
    for cls, n in sorted(counts.items()):
        print(f"  {cls}: {n}")
    print()

    # Print APPOSITION-CANDIDATE cases (the merge candidates)
    print("=== APPOSITION CANDIDATES (mid-verse, preceding 2nd-person marker) ===\n")
    for f in findings:
        if f["classification"] != "APPOSITION-CANDIDATE":
            continue
        print(f"{f['file']} {f['ref']} (line {f['line_idx']+1}/{f['total_lines']}):")
        for pl in f["preceding_lines"]:
            print(f"    {pl}")
        print(f"  >>> {f['voc_text']} <<<")
        for fl in f["following_lines"]:
            print(f"    {fl}")
        markers = []
        if f["preceding_2p_pronouns"]:
            markers.append(f"2p-pron: {','.join(f['preceding_2p_pronouns'])}")
        if f["preceding_2p_verbs"]:
            markers.append(f"2p-verb: {','.join(f['preceding_2p_verbs'])}")
        print(f"  [grammar: {'; '.join(markers)}]")
        print()


if __name__ == "__main__":
    main()
