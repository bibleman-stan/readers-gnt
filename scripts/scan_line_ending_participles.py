#!/usr/bin/env python3
"""
Scan all 260 v4-editorial chapter files for lines where a participial phrase
ends the line and its resolving finite verb starts the next line.

This catches cases like Matt 2:8:
  ἀπαγγείλατέ μοι, ὅπως κἀγὼ ἐλθὼν
  προσκυνήσω αὐτῷ.

where the participle_merge.py script missed it because the participle line
has other content before the participle.

Output: private/line-ending-participle-splits.md
"""

import os
import re
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MORPHGNT_DIR = os.path.join(BASE, "research", "morphgnt-sblgnt")
V4_DIR = os.path.join(BASE, "data", "text-files", "v4-editorial")

# Mapping from morphgnt file prefix to v4-editorial folder/file prefix
BOOK_MAP = {
    "61": ("01-matt", "matt"),
    "62": ("02-mark", "mark"),
    "63": ("03-luke", "luke"),
    "64": ("04-john", "john"),
    "65": ("05-acts", "acts"),
    "66": ("06-rom", "rom"),
    "67": ("07-1cor", "1cor"),
    "68": ("08-2cor", "2cor"),
    "69": ("09-gal", "gal"),
    "70": ("10-eph", "eph"),
    "71": ("11-phil", "phil"),
    "72": ("12-col", "col"),
    "73": ("13-1thess", "1thess"),
    "74": ("14-2thess", "2thess"),
    "75": ("15-1tim", "1tim"),
    "76": ("16-2tim", "2tim"),
    "77": ("17-titus", "titus"),
    "78": ("18-phlm", "phlm"),
    "79": ("19-heb", "heb"),
    "80": ("20-jas", "jas"),
    "81": ("21-1pet", "1pet"),
    "82": ("22-2pet", "2pet"),
    "83": ("23-1john", "1john"),
    "84": ("24-2john", "2john"),
    "85": ("25-3john", "3john"),
    "86": ("26-jude", "jude"),
    "87": ("27-rev", "rev"),
}

PUNCT_RE = re.compile(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]')

# Speech introduction lemmas
SPEECH_INTRO_LEMMAS = {"λέγω", "ἀποκρίνομαι"}


def strip_punct(word):
    return PUNCT_RE.sub('', word)


def load_morphgnt(book_num):
    """Load MorphGNT data for a book."""
    fname = None
    for f in os.listdir(MORPHGNT_DIR):
        if f.startswith(book_num + "-") and f.endswith(".txt"):
            fname = f
            break
    if not fname:
        return {}, {}

    by_ref = defaultdict(list)
    with open(os.path.join(MORPHGNT_DIR, fname), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 7:
                continue
            ref = parts[0]
            pos = parts[1]
            parsing = parts[2]
            text = parts[3]
            word = parts[4]
            normalized = parts[5]
            lemma = parts[6]
            stripped = strip_punct(text)
            by_ref[ref].append({
                'pos': pos,
                'parsing': parsing,
                'text': text,
                'word': word,
                'normalized': normalized,
                'lemma': lemma,
                'stripped': stripped,
            })

    by_form = defaultdict(list)
    for ref, entries in by_ref.items():
        for e in entries:
            by_form[e['stripped']].append({**e, 'ref': ref})

    return by_ref, by_form


def is_participle(entry):
    return entry['pos'].startswith('V') and len(entry['parsing']) > 3 and entry['parsing'][3] == 'P'


def is_finite_verb(entry):
    if not entry['pos'].startswith('V'):
        return False
    if len(entry['parsing']) > 3 and entry['parsing'][3] in ('P', 'N'):
        return False
    return True


def is_genitive_participle(entry):
    if len(entry['parsing']) > 4 and entry['parsing'][4] == 'G':
        return True
    return False


def is_speech_intro(entry):
    if entry.get('lemma', '') in SPEECH_INTRO_LEMMAS and is_participle(entry):
        return True
    return False


def find_morphgnt_entry(word_stripped, verse_ref, by_ref, by_form):
    if verse_ref in by_ref:
        for e in by_ref[verse_ref]:
            if e['stripped'] == word_stripped:
                return e
    if word_stripped in by_form:
        for e in by_form[word_stripped]:
            if e['ref'] == verse_ref:
                return e
        return by_form[word_stripped][0]
    return None


def find_all_entries_on_line(line_words, verse_ref, by_ref, by_form):
    """Find morphgnt entries for all words on a line."""
    entries = []
    for w in line_words:
        s = strip_punct(w)
        if not s:
            continue
        e = find_morphgnt_entry(s, verse_ref, by_ref, by_form)
        if e:
            entries.append(e)
    return entries


def line_has_finite_verb(entries):
    """Check if any entry on this line is a finite verb."""
    return any(is_finite_verb(e) for e in entries)


def is_substantival_participle(line, participle_stripped):
    """Check if the participle is preceded by an article (substantival use)."""
    words = line.strip().split()
    for i, w in enumerate(words):
        if strip_punct(w) == participle_stripped and i > 0:
            prev = strip_punct(words[i-1])
            # Common article forms
            articles = {'ὁ', 'ἡ', 'τό', 'τοῦ', 'τῆς', 'τοῦ', 'τῷ', 'τῇ', 'τῷ',
                        'τόν', 'τήν', 'τό', 'οἱ', 'αἱ', 'τά', 'τῶν', 'τοῖς', 'ταῖς',
                        'τούς', 'τάς', 'τά', 'τὸν', 'τὴν', 'τὸ', 'τοὺς', 'τὰς', 'τὰ'}
            if prev in articles:
                return True
    return False


def parse_chapter_file(filepath):
    verses = []
    current_verse = None
    current_lines = []
    with open(filepath, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip('\n').rstrip('\r')
            m = re.match(r'^(\d+):(\d+)', line)
            if m:
                if current_verse is not None:
                    verses.append((current_verse, current_lines))
                current_verse = line.strip()
                current_lines = []
            elif line.strip() == '':
                continue
            else:
                if current_verse is not None:
                    current_lines.append(line)
    if current_verse is not None:
        verses.append((current_verse, current_lines))
    return verses


def get_last_word(line):
    words = line.strip().split()
    if not words:
        return None
    return strip_punct(words[-1])


def verse_ref_to_morphgnt(book_num, verse_str):
    m = re.match(r'(\d+):(\d+)', verse_str)
    if not m:
        return None
    ch = int(m.group(1))
    vs = int(m.group(2))
    bb = int(book_num)
    return f"{bb-60:02d}{ch:02d}{vs:02d}"


def assess_split(participle_entry, line, next_line, finite_entry, line_entries, has_finite_on_line):
    """Assess whether this split should be merged."""
    words_on_line = len(line.strip().split())

    # Check if the next line starts with the finite verb (strong signal for merge)
    next_words = next_line.strip().split()
    next_first_stripped = strip_punct(next_words[0]) if next_words else ""
    finite_stripped = strip_punct(finite_entry['text'])

    if has_finite_on_line:
        return "LIKELY MERGE — participle after subordinating conjunction, verb on next line"

    if next_first_stripped == finite_stripped:
        # Finite verb is first word on next line — strong merge signal
        if words_on_line <= 4:
            return "LIKELY MERGE — verb starts next line, short participle line"
        else:
            return "LIKELY MERGE — verb starts next line"
    else:
        return "NEEDS REVIEW — verb not at start of next line"


def main():
    results = []
    total_files = 0

    for book_num, (folder, prefix) in sorted(BOOK_MAP.items()):
        folder_path = os.path.join(V4_DIR, folder)
        if not os.path.isdir(folder_path):
            print(f"  WARNING: folder not found: {folder_path}", file=sys.stderr)
            continue

        by_ref, by_form = load_morphgnt(book_num)
        if not by_ref:
            print(f"  WARNING: no morphgnt data for {book_num}", file=sys.stderr)
            continue

        chapter_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.txt')])
        for cf in chapter_files:
            total_files += 1
            filepath = os.path.join(folder_path, cf)
            verses = parse_chapter_file(filepath)

            for verse_str, lines in verses:
                for i in range(len(lines) - 1):
                    line = lines[i]
                    next_line = lines[i + 1]

                    last_word = get_last_word(line)
                    if not last_word:
                        continue

                    ref = verse_ref_to_morphgnt(book_num, verse_str)
                    if not ref:
                        continue

                    entry = find_morphgnt_entry(last_word, ref, by_ref, by_form)
                    if not entry:
                        continue

                    if not is_participle(entry):
                        continue

                    # EXCLUDE: participle-only lines (1 word)
                    line_words = [w for w in line.strip().split() if strip_punct(w)]
                    if len(line_words) <= 1:
                        continue

                    # EXCLUDE: genitive absolutes
                    if is_genitive_participle(entry):
                        continue

                    # EXCLUDE: speech introductions
                    if is_speech_intro(entry):
                        continue

                    # EXCLUDE: substantival participles (preceded by article)
                    if is_substantival_participle(line, last_word):
                        continue

                    # Check if the line already has a finite verb
                    line_entries = find_all_entries_on_line(line.strip().split(), ref, by_ref, by_form)
                    has_finite = line_has_finite_verb(line_entries)

                    if has_finite:
                        # If the line has a finite verb, only include if the participle
                        # follows a subordinating conjunction (ὅπως, ἵνα, ὥστε, ἐάν, etc.)
                        # which suggests the participle is in a NEW subordinate clause
                        # that resolves on the next line (like Matt 2:8: ὅπως κἀγὼ ἐλθὼν / προσκυνήσω)
                        subord_conjs = {'ὅπως', 'ἵνα', 'ὥστε', 'ἐάν', 'ἐὰν', 'ἄν', 'εἰ',
                                        'ὅταν', 'ὅτε', 'ἐπεί', 'ἐπειδή', 'ἐπάν', 'ἐπὰν',
                                        'μήποτε', 'πρίν'}
                        # Check if any word between the finite verb and the participle
                        # is a subordinating conjunction
                        words = line.strip().split()
                        found_subord = False
                        # Find the last finite verb position
                        last_finite_pos = -1
                        for idx, w in enumerate(words):
                            ws = strip_punct(w)
                            we = find_morphgnt_entry(ws, ref, by_ref, by_form)
                            if we and is_finite_verb(we):
                                last_finite_pos = idx
                        # Check for subordinating conjunction after the last finite verb
                        if last_finite_pos >= 0:
                            for idx in range(last_finite_pos + 1, len(words)):
                                ws = strip_punct(words[idx])
                                if ws in subord_conjs:
                                    found_subord = True
                                    break
                        if not found_subord:
                            continue

                    # Check if next line has a finite verb in its first few words
                    next_words = next_line.strip().split()[:5]
                    finite_verb_entry = None
                    for nw in next_words:
                        ns = strip_punct(nw)
                        if not ns:
                            continue
                        fe = find_morphgnt_entry(ns, ref, by_ref, by_form)
                        if fe and is_finite_verb(fe):
                            finite_verb_entry = fe
                            break

                    if not finite_verb_entry:
                        continue

                    book_name = prefix.upper()
                    assessment = assess_split(entry, line, next_line, finite_verb_entry, line_entries, has_finite)

                    results.append({
                        'file': os.path.relpath(filepath, BASE).replace('\\', '/'),
                        'book': book_name,
                        'verse': verse_str,
                        'line': line,
                        'next_line': next_line,
                        'participle': entry['text'],
                        'participle_lemma': entry['lemma'],
                        'finite_verb': finite_verb_entry['text'],
                        'finite_verb_lemma': finite_verb_entry['lemma'],
                        'assessment': assessment,
                        'line_word_count': len(line_words),
                    })

    # Write output
    out_path = os.path.join(BASE, "private", "line-ending-participle-splits.md")
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("# Line-Ending Participle Splits\n\n")
        out.write(f"**Scan date:** 2026-04-11\n")
        out.write(f"**Files scanned:** {total_files}\n")
        out.write(f"**Total hits:** {len(results)}\n\n")
        out.write("These are lines where a participle ends the line (with other content before it),\n")
        out.write("and the next line starts with or contains a finite verb -- suggesting the participle\n")
        out.write("was split from its resolving verb.\n\n")
        out.write("**Excluded:**\n")
        out.write("- Genitive absolutes (genitive case participles)\n")
        out.write("- Speech introductions (lemmas: λέγω, ἀποκρίνομαι)\n")
        out.write("- Participle-only lines (already handled by participle_merge.py)\n")
        out.write("- Substantival participles (preceded by article)\n")
        out.write("- Lines that already contain a finite verb (participle is supplementary/manner)\n\n")
        out.write("---\n\n")

        # Group by assessment
        by_assessment = defaultdict(list)
        for r in results:
            by_assessment[r['assessment']].append(r)

        for assessment in sorted(by_assessment.keys()):
            items = by_assessment[assessment]
            out.write(f"## {assessment} ({len(items)})\n\n")
            for r in items:
                out.write(f"### {r['book']} {r['verse']}\n")
                out.write(f"**File:** `{r['file']}`\n\n")
                out.write(f"```\n{r['line']}\n{r['next_line']}\n```\n\n")
                out.write(f"- **Participle:** {r['participle']} ({r['participle_lemma']})\n")
                out.write(f"- **Finite verb:** {r['finite_verb']} ({r['finite_verb_lemma']})\n")
                out.write(f"- **Words on participle line:** {r['line_word_count']}\n\n")

        out.write("---\n\n")
        out.write(f"*Total: {len(results)} line-ending participle splits found across {total_files} chapter files.*\n")

    print(f"Done. {len(results)} results written to {out_path}")
    for assessment in sorted(by_assessment.keys()):
        print(f"  {assessment}: {len(by_assessment[assessment])}")


if __name__ == "__main__":
    main()
