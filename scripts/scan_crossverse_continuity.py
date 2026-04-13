#!/usr/bin/env python3
"""
scan_crossverse_continuity.py — Find verse pairs where a single atomic
thought crosses the Stephanus 1551 verse boundary.

All previous scanners operate within a verse. The verse division is
hard-coded as a scanning frontier, which means any atomic thought the
16th-century editor accidentally bisected is systematically invisible.
This scanner looks at inter-verse boundaries — specifically, the last
line of verse N and the first line of verse N+1 — and flags boundaries
where grammatical continuity straddles the verse division.

Detected patterns (each has a confidence tier):

  1. PARALLEL-PTC (high) — verse N's last line ends with a
     circumstantial participle in a specific case; verse N+1's first
     line begins with καί + another participle in the same case. Both
     are parallel circumstantial modifiers of the same implicit verb.
     Matt 3:1-2 (κηρύσσων / καὶ λέγων) is the canonical case.

  2. SUSPENDED-MAIN-VERB (high) — verse N contains no finite verb
     anywhere; verse N+1's first line has the first finite verb. Common
     in Pauline periods and FEF straddles. Eph 1:3-14 is the extreme.

  3. RELATIVE-STRADDLE (high) — verse N+1's first line begins with a
     relative pronoun (ὅς/ἥ/ὅ in any case, accent-insensitive). The
     relative refers back to a head noun in verse N's last line.

  4. CONTENT-CLAUSE-STRADDLE (med) — verse N's last line ends with a
     verb of saying/thinking/knowing; verse N+1's first line begins
     with ὅτι / ἵνα / ὅπως + finite verb. The content clause straddles
     the boundary.

  5. PROTASIS-APODOSIS-STRADDLE (med) — verse N has a protasis marker
     (εἰ/ἐάν + subjunctive or indicative) and no apodosis finite verb;
     verse N+1 has the apodosis main clause.

  6. ARTICULAR-INF-STRADDLE (med) — verse N has ἐν τῷ + articular
     infinitive (temporal frame); verse N+1 has the main clause.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_crossverse_continuity.py
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_crossverse_continuity.py --book matt
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_crossverse_continuity.py --summary-only
"""
import os
import re
import sys
import argparse
import unicodedata
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
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7²³¹⁰⁴⁵⁶⁷⁸⁹]',
        '',
        word,
    )


def _strip_accents(w):
    decomposed = unicodedata.normalize("NFD", w)
    no_marks = "".join(c for c in decomposed if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", no_marks).lower()


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


def _is_participle(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] == "P"


def _is_infinitive(pos, parsing):
    if not pos.startswith("V"):
        return False
    if len(parsing) < 4:
        return False
    return parsing[3] == "N"


def _case(parsing):
    if len(parsing) < 5:
        return None
    return parsing[4]


def _line_words_with_morph(line_text, verse_queue):
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


def _annotate_verse(verse_words, lines):
    """Return list of annotated lines (each a list of word dicts)."""
    queue = list(verse_words)
    annotated = []
    for line in lines:
        annotated.append(_line_words_with_morph(line, queue))
    return annotated


_GREEK_SUBORDINATORS = {"οτι", "ινα", "οπως", "οταν", "οτε"}
_GREEK_RELATIVES = {"ος", "η", "ο", "ου", "ης", "ω", "ης", "ον", "ην",
                     "οις", "αις", "ων", "α", "ας", "οστις", "ητις"}
_SPEECH_THINK_LEMMAS = {
    "λέγω", "εἶπον", "φημί", "γράφω",
    "οἶδα", "γινώσκω", "ἐπίσταμαι",
    "νομίζω", "δοκέω", "λογίζομαι", "ἡγέομαι",
    "πιστεύω", "ἐλπίζω", "ὁμολογέω",
    "ἀκούω",
}


def _line_has_finite(annotated_line):
    for w in annotated_line:
        if w["pos"] and _is_finite(w["pos"], w["parsing"]):
            return True
    return False


def _verse_has_finite(annotated):
    return any(_line_has_finite(ln) for ln in annotated)


def _line_last_participle(annotated_line):
    """Return (word_dict, case) of the last participle in the line, or None."""
    for w in reversed(annotated_line):
        if w["pos"] and _is_participle(w["pos"], w["parsing"]):
            return (w, _case(w["parsing"]))
    return None


def _line_first_significant(annotated_line, skip={"και", "δε", "γαρ", "ουν", "τε", "μεν"}):
    """Return the first non-connective word, accent-stripped."""
    for w in annotated_line:
        if not w["cleaned"]:
            continue
        stripped = _strip_accents(w["cleaned"])
        if stripped in skip:
            continue
        return w
    return None


def _line_starts_with_ptc_no_finite(annotated_line):
    """True if the line starts with a participle (after skipping leading
    conjunctions/particles) AND contains no finite verb anywhere on the
    line. This is the 'dangling participial frame' signature —  the line
    hasn't resolved into a main-clause predication, so its grammatical
    completion must come from elsewhere."""
    if not annotated_line:
        return False, None
    # Check: no finite verb anywhere on the line
    for w in annotated_line:
        if w["pos"] and _is_finite(w["pos"], w["parsing"]):
            return False, None
    # Find first significant word (skip conj/particle/interjection)
    for w in annotated_line:
        if not w["pos"]:
            continue
        if (w["pos"].startswith("C") or w["pos"] == "X-" or
                w["pos"] == "I-"):
            continue
        if _is_participle(w["pos"], w["parsing"]):
            return True, w
        return False, None
    return False, None


def _check_parallel_ptc(last_line_n, first_line_n1):
    """Parallel participles pattern. Matt 3:1-2 type.

    Requirements:
    - Verse N's last line is a dangling participial frame: starts with
      ptc (after leading connectives), no finite verb anywhere.
    - Verse N+1's first line is also a dangling participial frame,
      starts specifically with καί + ptc, no finite verb.
    - Both participles in the same morphological case (so they can
      both be circumstantial modifiers of the same implicit head verb).
    """
    # Verse N's last line must be a dangling ptc frame
    is_ptc_frame_n, ptc_n = _line_starts_with_ptc_no_finite(last_line_n)
    if not is_ptc_frame_n:
        return None
    case_n = _case(ptc_n["parsing"])
    if not case_n:
        return None

    # Verse N+1's first line: check it's also a dangling ptc frame
    is_ptc_frame_n1, _ = _line_starts_with_ptc_no_finite(first_line_n1)
    if not is_ptc_frame_n1:
        return None

    # And it specifically starts with καί + ptc (not just any ptc)
    if len(first_line_n1) < 2:
        return None
    first = first_line_n1[0]
    first_stripped = _strip_accents(first["cleaned"]) if first["cleaned"] else ""
    if first_stripped != "και":
        return None
    # Find first ptc after the καί
    ptc_n1 = None
    for w in first_line_n1[1:]:
        if not w["pos"]:
            continue
        if (w["pos"].startswith("C") or w["pos"] == "X-" or
                w["pos"] == "I-"):
            continue
        if _is_participle(w["pos"], w["parsing"]):
            ptc_n1 = w
        break
    if ptc_n1 is None:
        return None
    if _case(ptc_n1["parsing"]) != case_n:
        return None
    return {
        "pattern": "PARALLEL-PTC",
        "confidence": "high",
        "detail": (f"{ptc_n['cleaned']} ({case_n}, {ptc_n['lemma']}) / "
                   f"καὶ {ptc_n1['cleaned']} ({case_n}, {ptc_n1['lemma']})"),
    }


def _line_is_genabs_frame(line_words):
    """True if the line is a genitive absolute frame: no finite verb,
    starts with a genitive substantive/article (after any leading
    connective), and contains at least one participle in genitive case."""
    if not line_words:
        return False
    for w in line_words:
        if w["pos"] and _is_finite(w["pos"], w["parsing"]):
            return False
    first = None
    for w in line_words:
        if not w["pos"]:
            continue
        if w["pos"].startswith("C") or w["pos"] == "X-" or w["pos"] == "I-":
            continue
        first = w
        break
    if first is None:
        return False
    if not (first["pos"].startswith("N") or first["pos"].startswith("A-") or
            first["pos"] == "RA" or first["pos"].startswith("R")):
        return False
    if _case(first["parsing"]) != "G":
        return False
    has_gen_ptc = any(
        w["pos"] and _is_participle(w["pos"], w["parsing"]) and _case(w["parsing"]) == "G"
        for w in line_words
    )
    return has_gen_ptc


def _check_suspended_main_verb(verse_n_annotated, verse_n1_annotated):
    """Verse N ends with a dangling participial frame (circumstantial
    ptc at start-of-line OR genitive absolute) and has no finite verb
    anywhere; verse N+1 carries the main verb.

    FEF straddle / suspended main verb pattern. The key tightening:
    verse N's LAST line must be the dangling frame itself, not just
    "any verse without a finite verb." This excludes:

    - Nominal list closures (Matt 10:4 "καὶ Ἰούδας ὁ Ἰσκαριώτης...")
    - Rhetorical questions with elided copula
    - Woe exclamations
    - Attributive participial phrases at the tail of a noun
    """
    if _verse_has_finite(verse_n_annotated):
        return None
    if not _verse_has_finite(verse_n1_annotated):
        return None
    if not verse_n_annotated:
        return None
    last_line = verse_n_annotated[-1]
    # Last line must be a circumstantial ptc-frame OR a genitive absolute
    is_ptc_frame, _ = _line_starts_with_ptc_no_finite(last_line)
    is_gen_abs = _line_is_genabs_frame(last_line)
    if not (is_ptc_frame or is_gen_abs):
        return None
    detail = "gen-abs frame" if is_gen_abs else "circumstantial ptc frame"
    return {
        "pattern": "SUSPENDED-MAIN-VERB",
        "confidence": "high",
        "detail": f"verse N ends with {detail}; verse N+1 carries the main verb",
    }


def _check_relative_straddle(last_line_n, first_line_n1):
    """Verse N+1 begins with a DEFINITE relative pronoun (not an indefinite
    "whoever" conditional like ὃς ἄν, ὅστις, ὃς ἐάν — those start new
    sentences). The definite relative refers to a specific head noun in
    verse N's last line.
    """
    first = _line_first_significant(first_line_n1) if first_line_n1 else None
    if not first:
        return None
    if not first["pos"] or first["pos"] != "RR":
        return None
    # Exclude ὅστις / ἥτις / οἵτινες / ἅτινα family (correlative /
    # indefinite relatives often beginning general conditional sentences)
    stripped = _strip_accents(first["cleaned"])
    if stripped.startswith("οστις") or stripped.startswith("ητις") or \
       stripped.startswith("οιτινες") or stripped.startswith("αιτινες") or \
       stripped.startswith("ατινα"):
        return None
    # Exclude if followed by ἄν / ἐάν (indefinite relative clause)
    for w in first_line_n1[1:5]:  # look in next few words
        if not w["cleaned"]:
            continue
        s = _strip_accents(w["cleaned"])
        if s in {"αν", "εαν"}:
            return None
    # Exclude if the clause verb is subjunctive (indefinite / conditional
    # relative; definite relatives take indicative)
    for w in first_line_n1:
        if w["pos"] and _is_finite(w["pos"], w["parsing"]):
            if len(w["parsing"]) >= 4 and w["parsing"][3] == "S":
                return None
            break
    return {
        "pattern": "RELATIVE-STRADDLE",
        "confidence": "med",
        "detail": f"verse N+1 begins with definite relative pronoun {first['cleaned']}",
    }


def _check_content_clause_straddle(last_line_n, first_line_n1):
    """Verse N ends with a verb of saying/thinking + verse N+1 begins with
    ὅτι / ἵνα / ὅπως + finite verb."""
    # Find any verb of saying/thinking anywhere on last line of verse N
    has_speech_verb = False
    for w in last_line_n:
        if w["pos"] and w["pos"].startswith("V") and w["lemma"] in _SPEECH_THINK_LEMMAS:
            has_speech_verb = True
            break
    if not has_speech_verb:
        return None
    first = _line_first_significant(first_line_n1) if first_line_n1 else None
    if not first:
        return None
    first_stripped = _strip_accents(first["cleaned"]) if first["cleaned"] else ""
    if first_stripped not in {"οτι", "ινα", "οπως"}:
        return None
    return {
        "pattern": "CONTENT-CLAUSE-STRADDLE",
        "confidence": "med",
        "detail": f"speech/think verb on verse N last line; verse N+1 begins with {first['cleaned']}",
    }


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
            # Annotate each verse
            annotated_verses = []
            for v in verses:
                verse_words = list(morph.get((v["chapter"], v["verse"]), []))
                if not verse_words:
                    annotated_verses.append((v, None))
                    continue
                annotated = _annotate_verse(verse_words, v["lines"])
                annotated_verses.append((v, annotated))

            # Check each adjacent verse pair
            for i in range(len(annotated_verses) - 1):
                v_n, ann_n = annotated_verses[i]
                v_n1, ann_n1 = annotated_verses[i + 1]
                if ann_n is None or ann_n1 is None:
                    continue
                if not ann_n or not ann_n1:
                    continue
                # Must be same chapter (no chapter-boundary crossings)
                if v_n["chapter"] != v_n1["chapter"]:
                    continue
                # Must be consecutive verses
                if v_n1["verse"] != v_n["verse"] + 1:
                    continue

                last_line_n = ann_n[-1] if ann_n else []
                first_line_n1 = ann_n1[0] if ann_n1 else []

                # Sentence-boundary punctuation on verse N's last line
                # signals a completed thought — skip cross-verse checks
                # for straddle patterns (but not speech-intro patterns).
                last_line_text = v_n["lines"][-1].rstrip() if v_n["lines"] else ""
                ends_with_full_stop = last_line_text.endswith((".", "·"))

                flags = []

                # Pattern 1: parallel participles
                flag = _check_parallel_ptc(last_line_n, first_line_n1)
                if flag:
                    flags.append(flag)

                # Pattern 2: suspended main verb (skip if full-stop)
                if not ends_with_full_stop:
                    flag = _check_suspended_main_verb(ann_n, ann_n1)
                    if flag:
                        flags.append(flag)

                # Pattern 3: relative straddle
                flag = _check_relative_straddle(last_line_n, first_line_n1)
                if flag:
                    flags.append(flag)

                # Pattern 4: content clause straddle
                flag = _check_content_clause_straddle(last_line_n, first_line_n1)
                if flag:
                    flags.append(flag)

                for flag in flags:
                    results.append({
                        "file": f"{book_entry}/{fname}",
                        "ref_n": v_n["ref"],
                        "ref_n1": v_n1["ref"],
                        "last_line_n": v_n["lines"][-1] if v_n["lines"] else "",
                        "first_line_n1": v_n1["lines"][0] if v_n1["lines"] else "",
                        "pattern": flag["pattern"],
                        "confidence": flag["confidence"],
                        "detail": flag["detail"],
                    })
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None)
    ap.add_argument("--summary-only", action="store_true")
    ap.add_argument("--min-confidence", default="med",
                    choices=["low", "med", "high"])
    args = ap.parse_args()

    conf_rank = {"low": 0, "med": 1, "high": 2}
    threshold = conf_rank.get(args.min_confidence, 1)

    findings = scan_all(book_filter=args.book)
    findings = [f for f in findings if conf_rank[f["confidence"]] >= threshold]

    print("=== CROSS-VERSE CONTINUITY SCAN ===\n")
    print(f"Total flagged verse pairs: {len(findings)}\n")

    by_pattern = defaultdict(int)
    for f in findings:
        by_pattern[f["pattern"]] += 1
    for pattern, n in sorted(by_pattern.items()):
        print(f"  {pattern}: {n}")
    print()

    by_book = defaultdict(int)
    for f in findings:
        by_book[f["file"].split("/")[0]] += 1
    for book, n in sorted(by_book.items()):
        print(f"  {book}: {n}")
    print()

    if args.summary_only:
        return

    for f in findings:
        print(f"{f['file']} {f['ref_n']}→{f['ref_n1']}  [{f['pattern']}, {f['confidence']}]")
        print(f"  ...{f['last_line_n']}")
        print(f"  {f['first_line_n1']}...")
        print(f"  [{f['detail']}]")
        print()


if __name__ == "__main__":
    main()
