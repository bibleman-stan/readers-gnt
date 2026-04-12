#!/usr/bin/env python3
"""
scan_overstacked_qualifiers.py — Find runs of 2-3 adjacent lines that were
stacked as "parallel" when they should have merged under the three-in-one
qualifier rule (methodology §5).

The three-in-one rule (session 8 refinement): the stacking rule applies to
separate predications, outcomes, or actions — NOT to co-referential
qualifiers of a single head. A triad of ≤3 co-referential modifiers of one
noun should merge into one line ("three-in-one") rather than stack as three
separate predications.

Canonical merged examples (don't flag — they're correct):
    Rom 12:1  θυσίαν ζῶσαν ἁγίαν εὐάρεστον τῷ θεῷ
    Rom 12:2  τὸ ἀγαθὸν καὶ εὐάρεστον καὶ τέλειον
    Matt 2:11 χρυσὸν καὶ λίβανον καὶ σμύρναν

Target — flag when the same pattern is wrongly STACKED:
    [head noun]
    + [modifier adj/gen/appositive]
    + [modifier adj/gen/appositive]

Tests for a run of 2-3 adjacent lines to be a candidate for merging:
    1. Run contains NO finite verbs (no indicative/subjunctive/imperative/
       optative), NO infinitives.
    2. A head noun is present in the first line of the run OR in the
       immediately preceding line.
    3. Each subsequent line is dominated by modifiers agreeing in
       case/gender/number with the head (pattern A: adjective chain), or is
       a genitive nominal modifying the head (pattern B), or is an
       appositive article+noun in the same case as the head (pattern C).

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_overstacked_qualifiers.py \\
        > private/overstacked-qualifiers-audit.txt
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
OUT_PATH = os.path.join(REPO_DIR, "private", "overstacked-qualifiers-audit.txt")

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
    # Normalize apostrophes / modifier letter primes so elided forms like
    # ἀφʼ / ἀφ' / ἀφ’ all collapse to the same key.
    word = word.replace("\u02BC", "\u2019").replace("\u0027", "\u2019")
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\(\)\[\]⟦⟧—\u037E\u0387\u00B7]',
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


# --- Parsing-code helpers ---------------------------------------------------
# Parsing string has 8 positions: person tense voice mood case number gender degree

def _mood(parsing):
    return parsing[3] if len(parsing) >= 4 else "-"


def _case(parsing):
    return parsing[4] if len(parsing) >= 5 else "-"


def _number(parsing):
    return parsing[5] if len(parsing) >= 6 else "-"


def _gender(parsing):
    return parsing[6] if len(parsing) >= 7 else "-"


def _is_finite(pos, parsing):
    return pos.startswith("V") and _mood(parsing) in ("I", "S", "D", "O")


def _is_infinitive(pos, parsing):
    return pos.startswith("V") and _mood(parsing) == "N"


def _is_participle(pos, parsing):
    return pos.startswith("V") and _mood(parsing) == "P"


def _is_noun(pos):
    return pos.startswith("N")


def _is_adjective(pos):
    return pos.startswith("A-")


def _is_article(pos):
    return pos == "RA"


def _is_relative(pos):
    return pos == "RR"


def _agrees(a, b):
    """Return True if two parsing codes agree in case/number/gender (ignoring '-')."""
    if _case(a) != _case(b):
        return False
    if _number(a) != _number(b):
        return False
    if _gender(a) != _gender(b):
        return False
    return True


def _line_words_with_morph(line_text, verse_queue):
    """Walk the line and annotate each Greek word.

    verse_queue: dict cleaned->list of (pos, parsing, lemma). Mutated (popped).
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
        }
        matches = verse_queue.get(cleaned)
        if matches:
            pos, parsing, lemma = matches.pop(0)
            entry.update(pos=pos, parsing=parsing, lemma=lemma)
        result.append(entry)
    return result


def _line_has_finite(words):
    return any(
        w["pos"] and w["parsing"] and _is_finite(w["pos"], w["parsing"])
        for w in words
    )


def _line_has_infinitive(words):
    return any(
        w["pos"] and w["parsing"] and _is_infinitive(w["pos"], w["parsing"])
        for w in words
    )


def _line_has_participle(words):
    return any(
        w["pos"] and w["parsing"] and _is_participle(w["pos"], w["parsing"])
        for w in words
    )


def _content_words(words):
    """Content words: exclude punctuation-only and pure connectives."""
    out = []
    for w in words:
        if not w["cleaned"]:
            continue
        # Skip bare conjunctions/particles that aren't content
        if w["pos"] == "C-":
            continue
        if w["pos"] == "X-":
            continue
        out.append(w)
    return out


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


def _build_queue(verse_words):
    q = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        q[cw].append((pos, parsing, lemma))
    return {k: list(v) for k, v in q.items()}


def _annotate_all_lines(lines, verse_words):
    """Return list of annotated-word lists, one per line, using a shared queue
    so duplicate tokens get consumed in order across the verse."""
    q = _build_queue(verse_words)
    return [_line_words_with_morph(ln, q) for ln in lines]


# --- Detection --------------------------------------------------------------

def _find_candidate_head(words):
    """Look for the primary head noun on a line — an unambiguous head would
    be a noun that modifiers can agree with. Prefer the last noun (as in
    Rom 12:1 where θυσίαν is the accusative head of the adjective chain).
    Return (index, entry) or (None, None)."""
    candidates = []
    for i, w in enumerate(words):
        if w["pos"] and w["parsing"] and (_is_noun(w["pos"]) or _is_adjective(w["pos"])):
            if _case(w["parsing"]) in ("N", "G", "D", "A", "V"):
                candidates.append((i, w))
    if not candidates:
        return None, None
    # Prefer last noun (final element before adjective run typically)
    return candidates[-1]


def _classify_run_line(line_words, head_parsing):
    """Classify a candidate run line as one of:
      - 'adj-chain'   : contains an adjective/participle agreeing with head,
                        no standalone noun-head-equivalent.
      - 'appositive'  : starts with article (RA) agreeing with head, followed
                        by a noun/participle agreeing with head — a true
                        apposition to the head on a prior line.
      - 'genitive'    : line is dominated by genitive modifiers of a
                        non-genitive head; NO preposition; no agreeing
                        new-head noun.
      - None          : does NOT match any three-in-one qualifier pattern
                        (e.g. coordinated name/noun list, prepositional
                        phrase, different predication).
    """
    content = _content_words(line_words)
    if not content:
        return None

    # Any verb (finite/infinitive) kills the pattern
    for w in content:
        if w["pos"] and w["parsing"]:
            mood = _mood(w["parsing"])
            if mood in ("I", "S", "D", "O", "N"):
                return None

    # Any preposition at line start means this is a prepositional phrase —
    # not a qualifier of the prior head. Reject.
    # (This kills "περὶ ἁμαρτίας / καὶ περὶ δικαιοσύνης" chains.)
    first_content = content[0]
    if first_content["pos"] == "P-":
        return None
    # Relative pronoun at line start = new relative clause, not a qualifier.
    # (Kills "ὅσα ἐστὶν ἀληθῆ / ὅσα σεμνά / ὅσα δίκαια" in Phil 4:8.)
    if first_content["pos"] == "RR":
        return None
    # Negation particle μή at start followed by an adjective is often a
    # vice-list marker in Pastoral lists (Titus 1:7, 1Tim 3:3). These are
    # ambiguous — still allowed but we'll fall through to adj-chain if it
    # matches.

    head_case = _case(head_parsing)

    has_agreeing_adjective = False
    has_agreeing_participle = False
    has_agreeing_article = False
    has_agreeing_noun = False
    has_agreeing_relative = False
    has_genitive_modifier = False
    has_disagreeing_noun = False
    has_prep_phrase_inline = False

    for w in content:
        pos = w["pos"]
        parsing = w["parsing"]
        if not pos or not parsing:
            continue
        if pos == "P-":
            has_prep_phrase_inline = True
            continue
        if pos == "D-":
            continue
        if pos == "RA":
            if _agrees(parsing, head_parsing):
                has_agreeing_article = True
            continue
        if pos.startswith("V"):
            # participle in agreement with head — attributive
            if _agrees(parsing, head_parsing):
                has_agreeing_participle = True
            elif _case(parsing) == "G" and head_case != "G":
                has_genitive_modifier = True
            else:
                has_disagreeing_noun = True
            continue
        if _is_adjective(pos):
            if _agrees(parsing, head_parsing):
                has_agreeing_adjective = True
            elif _case(parsing) == "G" and head_case != "G":
                has_genitive_modifier = True
            else:
                has_disagreeing_noun = True
            continue
        if _is_noun(pos):
            if _agrees(parsing, head_parsing):
                has_agreeing_noun = True
            elif _case(parsing) == "G" and head_case != "G":
                has_genitive_modifier = True
            else:
                has_disagreeing_noun = True
            continue
        if pos.startswith("R"):
            if _agrees(parsing, head_parsing):
                has_agreeing_relative = True
            elif _case(parsing) == "G" and head_case != "G":
                has_genitive_modifier = True
            else:
                has_disagreeing_noun = True
            continue

    if has_disagreeing_noun:
        return None

    # Classify
    # NOTE: appositive class is intentionally NOT emitted — in practice it
    # catches lists of distinct people (Matt 10:2-3 apostles, John 19:25
    # women at the cross, Eph 4:11 gifts list with μέν/δέ). Those are
    # distinct co-referents, not qualifiers.

    # adjective chain: has agreeing adjective or participle, no bare agreeing noun
    # (bare agreeing noun suggests coordinated co-head, not a qualifier)
    if (has_agreeing_adjective or has_agreeing_participle) and not has_agreeing_noun:
        return "adj-chain"

    # genitive chain: genitive modifier only, no agreeing noun, no prep phrase,
    # head is non-genitive
    if has_genitive_modifier and not has_agreeing_noun and not has_prep_phrase_inline and head_case != "G":
        return "genitive"

    return None


def _find_head_on_line(line_words):
    """Find a usable 'head' candidate on a line — the last NOUN in the line.
    Adjectives alone can't serve as heads (excludes vice-list starters like
    ἀσυνέτους where the whole run is a list of adjectives)."""
    last_noun = None
    last_idx = None
    for i, w in enumerate(line_words):
        pos = w["pos"]
        parsing = w["parsing"]
        if not pos or not parsing:
            continue
        if _is_noun(pos) and _case(parsing) in ("N", "G", "D", "A", "V"):
            last_noun = w
            last_idx = i
    return last_noun, last_idx


def _line_extends_chain(line_words, head_parsing):
    """Looser probe: does this line look like a potential continuation of a
    modifier chain? Used for sub-chunk bounds checking. True if the line has
    no finite verb/infinitive, starts with no preposition, and contains at
    least one token that agrees with the head in case/number/gender."""
    content = _content_words(line_words)
    if not content:
        return False
    for w in content:
        if w["pos"] and w["parsing"]:
            mood = _mood(w["parsing"])
            if mood in ("I", "S", "D", "O", "N"):
                return False
    # Don't reject pure prep-phrase starts here — a line like "καὶ τίμιον"
    # starts with a conjunction which is stripped from content
    if content[0]["pos"] == "P-":
        return False
    for w in content:
        if w["pos"] and w["parsing"]:
            if _agrees(w["parsing"], head_parsing):
                return True
    return False


def _line_is_bare_modifier_run(line_words):
    """Check that the line contains only modifier-ish tokens (no finite verb,
    no infinitive, no subordinator head)."""
    if _line_has_finite(line_words) or _line_has_infinitive(line_words):
        return False
    content = _content_words(line_words)
    if not content:
        return False
    return True


def _is_speech_line(words):
    """Cheap check: a line containing a speech-introducing verb."""
    for w in words:
        if w.get("lemma") in ("λέγω", "ἀποκρίνομαι", "φημί"):
            return True
    return False


def _dedup(candidates):
    """Prefer the longest run starting from each (file, ref, head_line_idx)."""
    by_key = {}
    for c in candidates:
        k = (c["file"], c["ref"], c["head_line_idx"])
        existing = by_key.get(k)
        if existing is None or c["run_len"] > existing["run_len"]:
            by_key[k] = c
    return list(by_key.values())


def _build_chapter_view(verses, morph):
    """Flatten all verse lines into a chapter-level list of records so that
    the scanner can see across verse boundaries (for vice-list detection).

    Each record: {text, annotated, ref, verse_idx_within}.
    """
    records = []
    for v in verses:
        verse_words = morph.get((v["chapter"], v["verse"]), [])
        if not verse_words:
            # Still add the lines with empty annotations so the flat index
            # is coherent, but mark as unannotated (they'll fail modifier
            # checks naturally)
            for line in v["lines"]:
                records.append({
                    "text": line,
                    "annotated": [],
                    "ref": v["ref"],
                })
            continue
        annotated_lines = _annotate_all_lines(v["lines"], verse_words)
        for line, ann in zip(v["lines"], annotated_lines):
            records.append({
                "text": line,
                "annotated": ann,
                "ref": v["ref"],
            })
    return records


def analyze_chapter(records, chapter_file):
    candidates = []
    n = len(records)

    for start in range(n):
        head_line_text = records[start]["text"]
        if ";" in head_line_text:
            continue
        head_words = records[start]["annotated"]
        if not head_words:
            continue

        head, head_idx = _find_head_on_line(head_words)
        if not head:
            continue
        head_parsing = head["parsing"]

        for run_len in (2, 3):
            end = start + run_len
            if end >= n:
                continue
            run_records = records[start + 1:end + 1]
            run_lines_ann = [r["annotated"] for r in run_records]
            raw_run = [r["text"] for r in run_records]

            reject_markers = False
            for rl in raw_run:
                if ";" in rl:
                    reject_markers = True
                    break
                tokens = rl.split()
                toks_clean = [_clean(t) for t in tokens]
                if "μὲν" in toks_clean or "μέν" in toks_clean:
                    reject_markers = True
                    break
                if "δὲ" in toks_clean or "δέ" in toks_clean:
                    reject_markers = True
                    break
            if reject_markers:
                continue

            ok_run = True
            modifier_classes = []
            for rw in run_lines_ann:
                if not _line_is_bare_modifier_run(rw):
                    ok_run = False
                    break
                cls = _classify_run_line(rw, head_parsing)
                if cls is None:
                    ok_run = False
                    break
                modifier_classes.append(cls)

            if not ok_run:
                continue

            if len(set(modifier_classes)) > 1:
                continue

            # Bounded-triad check against next line (can cross verse
            # boundaries — vice lists like 2Tim 3:2-4 span verses)
            if end + 1 < n:
                next_line_ann = records[end + 1]["annotated"]
                if next_line_ann and _line_extends_chain(next_line_ann, head_parsing):
                    continue

            # Bounded-triad check against previous line — only within the
            # SAME verse as the head line. Across a verse boundary we have
            # too many false matches from unrelated nouns that happen to
            # share case/gender/number with the head.
            if start - 1 >= 0:
                prev_rec = records[start - 1]
                if prev_rec["ref"] == records[start]["ref"]:
                    prev_line_ann = prev_rec["annotated"]
                    if prev_line_ann and _line_extends_chain(prev_line_ann, head_parsing):
                        continue

            max_tokens = max(
                len(_content_words(rw)) for rw in run_lines_ann
            )
            if max_tokens > 6:
                continue

            classes = set(modifier_classes)
            # adj-chain with short run lines = high confidence: textbook
            # three-in-one qualifier pattern.
            if classes == {"adj-chain"} and max_tokens <= 3:
                confidence = "high"
            elif classes == {"adj-chain"}:
                confidence = "medium"
            elif classes == {"genitive"} and max_tokens <= 2:
                confidence = "high"
            elif classes == {"genitive"}:
                confidence = "medium"
            else:
                confidence = "low"

            candidates.append({
                "file": os.path.basename(chapter_file),
                "dir": os.path.basename(os.path.dirname(chapter_file)),
                "ref": records[start]["ref"],
                "head_line_idx": start,
                "run_start_idx": start + 1,
                "run_end_idx": end,
                "run_len": run_len,
                "head_line_text": head_line_text,
                "run_lines": raw_run,
                "head_word": head["text"],
                "head_lemma": head["lemma"],
                "head_case": _case(head_parsing),
                "head_number": _number(head_parsing),
                "head_gender": _gender(head_parsing),
                "modifier_classes": modifier_classes,
                "confidence": confidence,
            })
    return candidates


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
            records = _build_chapter_view(verses, morph)
            cands = analyze_chapter(records, filepath)
            findings.extend(cands)

    return _dedup(findings)


CONF_ORDER = {"high": 0, "medium": 1, "low": 2}


def format_candidate(c):
    lines = []
    lines.append(f"{c['dir']}/{c['file']} {c['ref']}  [{c['confidence']}]")
    lines.append("  Current layout:")
    lines.append(f"      {c['head_line_text']}")
    for rl in c["run_lines"]:
        lines.append(f"    + {rl}")
    lines.append(
        f"  Head: {c['head_word']} (lemma={c['head_lemma']}, "
        f"case={c['head_case']} num={c['head_number']} gen={c['head_gender']})"
    )
    cls_str = ", ".join(c["modifier_classes"])
    lines.append(f"  Modifier class(es): {cls_str}")
    if c["run_len"] == 2:
        rec = "merge the 2 modifier lines into the head line (or into one line)"
    else:
        rec = "merge the 3 modifier lines into the head line (three-in-one)"
    lines.append(f"  Recommendation: {rec}")
    return "\n".join(lines)


def main():
    findings = scan_all()
    # Sort: confidence high first, then by book order
    findings.sort(key=lambda c: (CONF_ORDER.get(c["confidence"], 9), c["dir"], c["file"], c["ref"]))

    chapters = {(c["dir"], c["file"]) for c in findings}

    out_lines = []
    out_lines.append("=== OVER-STACKED QUALIFIER AUDIT ===")
    out_lines.append("")
    out_lines.append(
        f"Found {len(findings)} candidates across {len(chapters)} chapters"
    )
    out_lines.append("")
    out_lines.append(
        "Sorted by confidence (high -> medium -> low). Each candidate shows "
        "the current line layout with the head line and the stacked modifier "
        "run. Candidates may warrant merging into a three-in-one qualifier "
        "line under methodology section 5."
    )
    out_lines.append("")

    # Group by confidence
    for conf in ("high", "medium", "low"):
        subset = [c for c in findings if c["confidence"] == conf]
        if not subset:
            continue
        out_lines.append(f"--- {conf.upper()} CONFIDENCE ({len(subset)}) ---")
        out_lines.append("")
        for c in subset:
            out_lines.append(format_candidate(c))
            out_lines.append("")

    text = "\n".join(out_lines)
    # Ensure private/ exists
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)

    # Print summary to stdout
    print(f"Found {len(findings)} candidates across {len(chapters)} chapters")
    by_conf = defaultdict(int)
    for c in findings:
        by_conf[c["confidence"]] += 1
    for conf in ("high", "medium", "low"):
        print(f"  {conf}: {by_conf[conf]}")
    print(f"Full report written to: {OUT_PATH}")


if __name__ == "__main__":
    main()
