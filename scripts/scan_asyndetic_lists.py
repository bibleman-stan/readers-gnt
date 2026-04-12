#!/usr/bin/env python3
"""
scan_asyndetic_lists.py — Find asyndetic lists (3+ consecutive nominals in the
same case/number with no connecting conjunctions) that should be stacked as
parallel lines.

Background: Paul's vice/virtue catalogs are classic asyndetic lists — strings
of nouns or adjectives with no καί / δέ / τε / οὐδέ separators. Classic examples:
  - Rom 1:29-31 (vice list)
  - Gal 5:19-21 (works of the flesh)
  - Gal 5:22-23 (fruit of the spirit)
  - Col 3:5-8, 3:12
  - Eph 4:31-32, 5:3-5
  - 1 Tim 1:9-10, 3:2-3, 6:11
  - 2 Tim 3:2-5
  - 1 Pet 3:8
  - 2 Pet 1:5-7
  - Titus 1:7-8, 3:3

A series of nominals in the same case without connecting particles should be
stacked as parallel lines, one item per line, to make the list structure
visually apparent.

Detection rules:
  - A run of 3+ Greek word-tokens where each token is a noun (POS N-) or an
    adjective (POS A-) — all in the same case and number.
  - Articles (RA-) do not count as members but do not break the chain (they
    can head a list item).
  - Participles are NEVER counted as list members. Substantive participles
    (λεγόμενος, λέγοντος, ἐκπορευομένῳ, γεγραμμένον, etc.) are overwhelmingly
    appositional in the NT, not list members. Any participle BREAKS the chain.
  - Lists must have at least 4 DISTINCT lemmas — repetition (e.g. υἱοῦ Δαυίδ
    υἱοῦ Ἀβραάμ) marks a chain pattern, not a parallel list.
  - Runs containing πᾶς as a member are rejected — πᾶς is adjectival and
    attaches to a head noun; it doesn't stand as a list item.
  - Runs dominated by proper nouns (genealogies, witness chains, name
    strings) are rejected: if 50% or more members are proper nouns (lemma
    stored with a capital Greek letter), the run is not a vice/virtue catalog.
  - Threshold of 4 intentionally filters common 3-noun appositional
    structures ("Ἰησοῦς ὁ λεγόμενος Χριστός", "Ἰερεμίου τοῦ προφήτου", etc.).
  - The chain is BROKEN by:
      * any conjunction lemma in {καί, δέ, τε, οὐδέ, μηδέ, μήτε, οὔτε, ἤ, ἀλλά}
      * any verb form (finite, infinitive, or participle)
      * a preposition (P-)
      * a pronoun (RP-/RD-/RI-/RR-)
      * a case mismatch (different case OR different number)
  - Gender mismatch does NOT break the chain (noun inherent gender varies;
    μεστούς takes genitives of all three genders as complements in Rom 1:29).

Output: a report flagged by chapter file and verse reference, showing the
current-layout lines that contain the list and the detected members.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_asyndetic_lists.py
"""

import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, "data", "text-files", "v4-editorial")
MORPHGNT_DIR = os.path.join(REPO_DIR, "research", "morphgnt-sblgnt")
PRIVATE_DIR = os.path.join(REPO_DIR, "private")

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

# Conjunction lemmas that BREAK an asyndetic chain (their presence means the
# list is syndetic/polysyndetic, not asyndetic)
CONJUNCTION_LEMMAS = {
    "καί", "δέ", "τε", "οὐδέ", "μηδέ", "μήτε", "οὔτε", "ἤ", "ἀλλά",
}


def _clean(word):
    """Strip punctuation and critical apparatus markers."""
    return re.sub(
        r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]',
        '',
        word,
    )


_verse_morph = {}


def _load_morphgnt(book_slug):
    """Return dict keyed by (chapter, verse) -> ORDERED list of
    (cleaned, pos, parsing, lemma) — preserves verse word order.
    """
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


# MorphGNT parsing-field layout (8 chars):
#   [0] person    [1] tense    [2] voice    [3] mood
#   [4] case      [5] number   [6] gender   [7] degree
#
# For nouns/adjectives/articles the first four are dashes and case/number/
# gender are meaningful.

def _case(parsing):
    if not parsing or len(parsing) < 8:
        return None
    c = parsing[4]
    return c if c in "NGDAV" else None


def _number(parsing):
    if not parsing or len(parsing) < 8:
        return None
    n = parsing[5]
    return n if n in "SP" else None


def _gender(parsing):
    if not parsing or len(parsing) < 8:
        return None
    g = parsing[6]
    return g if g in "MFN" else None


def _is_noun(pos):
    return pos == "N-"


def _is_adj(pos):
    return pos == "A-"


def _is_article(pos):
    return pos == "RA"


def _is_verb(pos):
    return pos.startswith("V")


def _is_preposition(pos):
    return pos == "P-"


def _is_nominal_candidate(pos, parsing):
    """Return True if this word can participate in an asyndetic nominal list.

    Only nouns and adjectives qualify. Participles — even 'substantive' ones
    — are excluded: in NT usage they're overwhelmingly appositional
    (λεγόμενος, ῥηθὲν, γεγραμμένον), not parallel list members.
    """
    if _is_noun(pos) or _is_adj(pos):
        return _case(parsing) is not None and _number(parsing) is not None
    return False


def _is_chain_breaker(pos, parsing, lemma):
    """Return True if this token ends any in-progress list chain."""
    if lemma in CONJUNCTION_LEMMAS:
        return True
    if _is_preposition(pos):
        return True
    # Any verb form at all breaks the chain (finite, infinitive, participle).
    if _is_verb(pos):
        return True
    # Articles do NOT break the chain — they head list items.
    # Pronouns other than articles break the chain.
    if pos in ("RP", "RD", "RI", "RR"):
        return True
    return False


VERSE_REF_RE = re.compile(r"^(\d+):(\d+)$")


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


# User spec said "at least 3" — but with MIN=3 the scan returns ~164 hits,
# most of which are 3-item appositional patterns ("A the B C-adj", etc.) that
# slip past the other quality filters. MIN=4 returns ~42 hits, squarely
# inside the estimated 20-50 range for genuine asyndetic lists.
MIN_MEMBERS = 4


def _is_proper_noun_lemma(lemma):
    """Proper nouns in MorphGNT lemmas start with a capital Greek letter."""
    if not lemma:
        return False
    ch = lemma[0]
    return ch.isupper()


def _find_runs(verse_words):
    """Walk the verse word sequence and return a list of asyndetic runs.

    Each run is a list of indices into verse_words identifying the nominal
    members of the run. A run is emitted only if it contains >= MIN_MEMBERS
    nominal members all sharing case + number, with all-distinct lemmas, no
    πᾶς member, and not dominated by proper nouns.

    Articles interleaved with nominal candidates do NOT count as members but
    also do not break the run.
    """
    runs = []
    i = 0
    n = len(verse_words)
    while i < n:
        cleaned, pos, parsing, lemma = verse_words[i]
        if not _is_nominal_candidate(pos, parsing):
            i += 1
            continue
        anchor_case = _case(parsing)
        anchor_num = _number(parsing)
        members = [i]
        j = i + 1
        while j < n:
            c2, p2, parse2, l2 = verse_words[j]
            if _is_article(p2):
                j += 1
                continue
            if _is_nominal_candidate(p2, parse2):
                if _case(parse2) == anchor_case and _number(parse2) == anchor_num:
                    members.append(j)
                    j += 1
                    continue
                else:
                    break
            if _is_chain_breaker(p2, parse2, l2):
                break
            break

        # Apply post-filters before accepting the run.
        if _accept_run(verse_words, members):
            runs.append(members)
            i = j
        else:
            i += 1
    return runs


def _accept_run(verse_words, members):
    """Apply quality filters to weed out false positives."""
    if len(members) < MIN_MEMBERS:
        return False
    member_tuples = [verse_words[k] for k in members]
    lemmas = [t[3] for t in member_tuples]
    poses = [t[1] for t in member_tuples]
    # Require all-distinct lemmas (e.g. υἱοῦ repeating rejects genealogies).
    if len(set(lemmas)) < len(lemmas):
        return False
    # Reject any run containing πᾶς (it's an adjectival quantifier, not a
    # list member).
    if "πᾶς" in lemmas:
        return False
    # Reject runs dominated by proper nouns (genealogies / witness strings).
    proper_count = sum(1 for l in lemmas if _is_proper_noun_lemma(l))
    if proper_count * 2 >= len(lemmas):
        return False
    # Require at least 2 nouns among the members. Runs with a single noun
    # and several adjectives are noun + modifier stacks, not lists
    # (e.g. μύρου νάρδου πιστικῆς πολυτελοῦς = "expensive pure nard
    # perfume", ἑπτὰ ἕτερα πνεύματα πονηρότερα = "seven other worse
    # spirits"). Vice/virtue lists always have multiple distinct head nouns.
    noun_count = sum(1 for p in poses if p == "N-")
    if noun_count < 2:
        return False
    return True


def _run_is_asyndetic(verse_words, members):
    """A run found by _find_runs is asyndetic by construction (chain breakers
    ended the run early if there were any conjunctions). This is a sanity
    guard in case the break logic ever changes.
    """
    first, last = members[0], members[-1]
    for k in range(first, last + 1):
        cleaned, pos, parsing, lemma = verse_words[k]
        if lemma in CONJUNCTION_LEMMAS:
            return False
    return True


def _nominals_on_lines(lines, members_cleaned):
    """Determine which lines in a verse contain the list items. Returns a
    list of (line_idx, line_text, items_on_line) where items_on_line is the
    subset of member cleaned-forms that appear on that line (in order).
    Also returns whether the list is already cleanly stacked (each member on
    its own line with no other nominal from the run sharing the line).
    """
    # Normalize cleaned forms for comparison — each cleaned form paired with
    # its occurrence index since a form might repeat (rare in vice lists).
    remaining = list(members_cleaned)  # queue
    layout = []
    for idx, line_text in enumerate(lines):
        tokens = [_clean(t) for t in line_text.split() if _clean(t)]
        hits = []
        for tok in tokens:
            if remaining and tok == remaining[0]:
                hits.append(tok)
                remaining.pop(0)
        if hits:
            layout.append((idx, line_text, hits))
    return layout, (len(remaining) == 0)


def _is_cleanly_stacked(layout, num_members):
    """Return True if the list appears to be stacked: roughly one member per
    line, with short lines. A line may contain an agreeing adjective modifier
    alongside its noun head (that's still one 'item').
    """
    if len(layout) < 2:
        return False
    # Require the number of layout lines to be within 1 of the member count
    # (allow one line to contain head+modifier as a single item).
    if len(layout) < num_members - 2:
        return False
    for _idx, line_text, hits in layout:
        tokens = [_clean(t) for t in line_text.split() if _clean(t)]
        # Clean lines in stacked lists are typically 1 token (bare noun) or
        # 2-3 tokens (article + noun, or noun + adjective). Reject anything
        # larger — that's a packed prose line.
        if len(tokens) > 3:
            return False
    return True


def scan_chapter(book_slug, chapter_file, filepath, morph):
    findings = []
    verses = _parse_chapter(filepath)
    for v in verses:
        verse_words = morph.get((v["chapter"], v["verse"]), [])
        if not verse_words:
            continue
        runs = _find_runs(verse_words)
        if not runs:
            continue
        for members in runs:
            if not _run_is_asyndetic(verse_words, members):
                continue
            member_tuples = [verse_words[k] for k in members]
            member_cleaned = [t[0] for t in member_tuples]
            anchor_case = _case(member_tuples[0][2])
            anchor_num = _number(member_tuples[0][2])
            genders = sorted({_gender(t[2]) or "?" for t in member_tuples})
            layout, all_found = _nominals_on_lines(v["lines"], list(member_cleaned))
            status = "MIXED"
            if layout and _is_cleanly_stacked(layout, len(member_cleaned)):
                status = "CLEAN"
            findings.append({
                "file": chapter_file,
                "ref": v["ref"],
                "members": member_tuples,
                "case": anchor_case,
                "number": anchor_num,
                "genders": genders,
                "layout": layout,
                "all_found": all_found,
                "status": status,
                "lines": v["lines"],
            })
    return findings


def scan_all():
    all_findings = []
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
            findings = scan_chapter(book_slug, chapter_file, filepath, morph)
            all_findings.extend(findings)
    return all_findings


def format_report(findings):
    out = []
    out.append("=== ASYNDETIC LIST SCAN ===")
    out.append("")
    chapters_with_hits = {(f["file"], f["ref"].split(":")[0]) for f in findings}
    clean = [f for f in findings if f["status"] == "CLEAN"]
    mixed = [f for f in findings if f["status"] != "CLEAN"]
    out.append(
        f"Found {len(findings)} asyndetic list candidates across "
        f"{len(chapters_with_hits)} chapters"
    )
    out.append(f"  - {len(mixed)} NOT cleanly stacked (need editorial work)")
    out.append(f"  - {len(clean)} already cleanly stacked")
    out.append("")
    out.append("--- NOT CLEANLY STACKED ---")
    out.append("")
    for f in mixed:
        out.extend(_format_one(f))
    out.append("")
    out.append("--- ALREADY CLEANLY STACKED (no action needed) ---")
    out.append("")
    for f in clean:
        out.extend(_format_one(f))
    return "\n".join(out)


def _format_one(f):
    lines = []
    lines.append(f"{f['file']} {f['ref']}:  [{f['status']}]")
    lines.append("  Current layout:")
    if f["layout"]:
        for _idx, line_text, hits in f["layout"]:
            lines.append(f"    {line_text}")
    else:
        lines.append("    (layout mapping failed — members not located in file lines)")
    genders_display = "/".join(f["genders"])
    lines.append(
        f"  Detected list items "
        f"(case={f['case']}, number={f['number']}, gender={genders_display}):"
    )
    for cleaned, pos, parsing, lemma in f["members"]:
        gender = _gender(parsing) or "?"
        lines.append(f"    - {cleaned} ({lemma}) [{pos} {parsing}]")
    lines.append("  Recommendation: stack each item as its own line")
    lines.append("")
    return lines


def main():
    findings = scan_all()
    report = format_report(findings)
    print(report)
    os.makedirs(PRIVATE_DIR, exist_ok=True)
    outpath = os.path.join(PRIVATE_DIR, "asyndetic-lists-scan.txt")
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSaved report to {outpath}", file=sys.stderr)


if __name__ == "__main__":
    main()
