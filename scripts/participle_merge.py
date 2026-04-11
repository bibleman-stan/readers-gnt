#!/usr/bin/env python3
"""
participle_merge.py — Detect and merge dependent participial frames.

Principle: A circumstantial participle merges with its main verb by default.
A line that contains only participles (no finite verb) is a dependent frame —
it needs the next line's finite verb to complete the thought. Merge them.

Exception (camera-angle rule): When the PREVIOUS line already contains a
complete predication (finite verb + arguments), and the participle adds
supplementary spatial/postural info, it is an independent camera angle.
Test: can you reconstruct the participle as an independent predication by
supplying the main verb from the previous line? If yes, leave split.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/participle_merge.py --dry-run
    PYTHONIOENCODING=utf-8 py -3 scripts/participle_merge.py
    PYTHONIOENCODING=utf-8 py -3 scripts/participle_merge.py --book mark
"""

import argparse
import os
import re
import sys
from collections import defaultdict

# ---------- paths ----------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'v4-editorial')
MORPHGNT_DIR = os.path.join(REPO_DIR, 'research', 'morphgnt-sblgnt')

# ---------- MorphGNT book mapping ----------

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

# ---------- MorphGNT loading ----------

# Cache: {book_slug: {(chapter, verse): [(cleaned_word, pos, parsing, lemma), ...]}}
_verse_morph = {}


def _clean(word):
    """Strip MorphGNT critical-apparatus markers and punctuation."""
    return re.sub(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7]', '', word)


def _load_morphgnt(book_slug):
    """Load MorphGNT data for a book, keyed by (chapter, verse)."""
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
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(' ', 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, text, word, normalized, lemma = parts
            ch = int(ref[2:4])
            vs = int(ref[4:6])
            cleaned = _clean(word)
            if cleaned:
                verses[(ch, vs)].append((cleaned, pos, parsing, lemma))

    _verse_morph[book_slug] = dict(verses)
    return dict(verses)


# ---------- line analysis ----------

def _classify_words_on_line(line_text, book_slug, chapter, verse):
    """Classify each word on a line using MorphGNT data for this specific verse.

    Returns dict with keys:
        has_finite_verb: bool
        has_participle: bool
        has_infinitive: bool
        participle_only: bool  (has participle(s) but no finite verb or infinitive)
        word_count: int
        finite_verb_count: int
        participle_count: int
    """
    morph_data = _load_morphgnt(book_slug)
    verse_words = morph_data.get((chapter, verse), [])

    # Build a lookup: cleaned_word -> list of (pos, parsing, lemma)
    # We need to handle duplicate words in the verse carefully.
    # Strategy: for each word on the line, find matching MorphGNT entries.
    verse_lookup = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        verse_lookup[cw].append((pos, parsing, lemma))

    line_words = line_text.strip().split()
    has_finite = False
    has_participle = False
    has_infinitive = False
    finite_count = 0
    participle_count = 0
    total_words = 0

    for w in line_words:
        cleaned = _clean(w)
        if not cleaned:
            continue
        total_words += 1

        entries = verse_lookup.get(cleaned, [])
        for pos, parsing, lemma in entries:
            if not pos.startswith('V'):
                continue
            if len(parsing) >= 4:
                mood = parsing[3]
                if mood in ('I', 'S', 'D', 'O'):  # indicative, subjunctive, imperative, optative
                    has_finite = True
                    finite_count += 1
                elif mood == 'P':
                    has_participle = True
                    participle_count += 1
                elif mood == 'N':
                    has_infinitive = True

    return {
        'has_finite_verb': has_finite,
        'has_participle': has_participle,
        'has_infinitive': has_infinitive,
        'participle_only': has_participle and not has_finite and not has_infinitive,
        'word_count': total_words,
        'finite_verb_count': finite_count,
        'participle_count': participle_count,
    }


def _line_has_complete_predication(info):
    """A line has a complete predication if it has a finite verb.

    This is conservative: a finite verb with any arguments constitutes
    a complete atomic thought.
    """
    return info['has_finite_verb']


# ---------- file parsing ----------

VERSE_REF_RE = re.compile(r'^(\d+):(\d+)$')


def parse_chapter_file(filepath):
    """Parse a v4-editorial chapter file.

    Returns list of verse dicts:
        [{"ref": "5:2", "chapter": 5, "verse": 2, "lines": ["...", ...]}, ...]
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_lines = f.readlines()

    verses = []
    current = None
    for line in raw_lines:
        stripped = line.rstrip('\n')
        m = VERSE_REF_RE.match(stripped.strip())
        if m:
            if current is not None:
                verses.append(current)
            current = {
                'ref': stripped.strip(),
                'chapter': int(m.group(1)),
                'verse': int(m.group(2)),
                'lines': [],
            }
        elif current is not None:
            current['lines'].append(stripped)

    if current is not None:
        verses.append(current)

    return verses


def write_chapter_file(filepath, verses):
    """Write verses back to a chapter file."""
    out = []
    for v in verses:
        out.append(v['ref'])
        for line in v['lines']:
            out.append(line)
    # Ensure file ends with newline
    content = '\n'.join(out)
    if not content.endswith('\n'):
        content += '\n'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


# ---------- spatial/postural participle detection ----------

# Common aorist participles that indicate spatial/postural camera angles
# (supplementary participles that add independent visual info)
SPATIAL_POSTURAL_LEMMAS = {
    # Motion/position
    'ἔρχομαι', 'ἀνίστημι', 'στρέφω', 'ἐπιστρέφω', 'κάθημαι',
    'ἵστημι', 'πίπτω', 'ἀναβαίνω', 'καταβαίνω', 'εἰσέρχομαι',
    'ἐξέρχομαι', 'παράγω', 'προέρχομαι', 'ἀναχωρέω', 'πορεύομαι',
    'ἀπέρχομαι', 'ἐγγίζω', 'προσέρχομαι', 'ἀνακείμαι',
    # Postural
    'γονυπετέω', 'κλίνω', 'καθίζω',
    # Sight/perception (camera direction)
    'ἀναβλέπω', 'ἐμβλέπω', 'περιβλέπομαι',
}

# Temporal/causal participle lemmas — these are frame-type by nature
FRAME_PARTICIPLE_LEMMAS = {
    'ἀκούω', 'ὁράω', 'λαμβάνω', 'γιγνώσκω', 'γινώσκω', 'μανθάνω',
    'εὑρίσκω', 'βλέπω', 'θεωρέω', 'θεάομαι',
    'φοβέομαι', 'θαυμάζω', 'σπλαγχνίζομαι', 'χαίρω',
    'τελέω', 'πληρόω', 'παύω',
}


def _get_participle_lemmas_on_line(line_text, book_slug, chapter, verse):
    """Return set of lemmas for participles found on this line."""
    morph_data = _load_morphgnt(book_slug)
    verse_words = morph_data.get((chapter, verse), [])

    verse_lookup = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        verse_lookup[cw].append((pos, parsing, lemma))

    lemmas = set()
    for w in line_text.strip().split():
        cleaned = _clean(w)
        if not cleaned:
            continue
        for pos, parsing, lemma in verse_lookup.get(cleaned, []):
            if pos.startswith('V') and len(parsing) >= 4 and parsing[3] == 'P':
                lemmas.add(lemma)
    return lemmas


# ---------- clause-boundary and speech-intro detection ----------

# Clause-final punctuation: period, raised dot (ano teleia), Greek question mark
_CLAUSE_FINAL_RE = re.compile(r'[.\u00B7\u0387\u037E]$')

# Speech-intro pattern: line ends with · (after λέγων, λέγοντες, etc.)
_SPEECH_INTRO_RE = re.compile(r'(λέγων|λέγοντες|λέγουσα|λέγουσαι|λέγοντος|εἰπών|εἰπόντος|εἰποῦσα|εἰπόντες|κράξας|κράζων|κράζοντες|ἀποκριθείς|ἀποκριθεῖσα)\s*[\u00B7\u0387·:]?\s*$')

# Article + participle = substantival participle ("the one who...")
# These function as nouns and should NOT be merged.
# We detect articles via MorphGNT POS tag 'RA' rather than word forms,
# since accent varies by position (τόν vs τὸν).

# Relative pronouns — lines starting with these are relative clauses,
# not direct resolutions of a participial frame
_RELATIVE_PRONOUNS = {
    'ὃς', 'ὅς', 'ἥ', 'ἣ', 'ὅ', 'ὃ', 'οἵ', 'οἳ', 'αἵ', 'αἳ', 'ἅ', 'ἃ',
    'οὗ', 'ἧς', 'ὧν', 'ᾧ', 'ᾗ', 'οἷς', 'αἷς',
    'ὅν', 'ἥν', 'ἣν', 'οὕς', 'ἅς',
    'ὅστις', 'ἥτις',
}


def _line_ends_clause(line_text):
    """Check if a line ends with clause-final punctuation."""
    stripped = line_text.rstrip()
    if not stripped:
        return False
    last_char = stripped[-1]
    return last_char in '.·\u00B7\u0387\u037E;'


def _is_speech_intro(line_text):
    """Check if a line is a speech introduction (λέγων·, etc.)."""
    return bool(_SPEECH_INTRO_RE.search(line_text.strip()))


_POSTPOSITIVE_PARTICLES = {'δέ', 'δὲ', 'γάρ', 'μέν', 'μὲν', 'οὖν', 'τε', 'καί', 'καὶ'}


def _has_substantival_participle(line_text, book_slug, chapter, verse):
    """Check if the line has an article near a participle (substantival use).

    Pattern: ὁ [δέ] + participle = "the one who does X" — functions as a noun
    phrase, not a circumstantial frame. Allows intervening postpositive
    particles (δέ, μέν, γάρ). Uses MorphGNT POS 'RA' for article detection.
    """
    words = line_text.strip().split()
    if len(words) < 2:
        return False

    morph_data = _load_morphgnt(book_slug)
    verse_words = morph_data.get((chapter, verse), [])
    verse_lookup = defaultdict(list)
    for cw, pos, parsing, lemma in verse_words:
        verse_lookup[cw].append((pos, parsing, lemma))

    def _is_article(clean_word):
        for pos, parsing, lemma in verse_lookup.get(clean_word, []):
            if pos.strip() == 'RA':
                return True
        return False

    def _is_participle(clean_word):
        for pos, parsing, lemma in verse_lookup.get(clean_word, []):
            if pos.startswith('V') and len(parsing) >= 4 and parsing[3] == 'P':
                return True
        return False

    # Only check the first few words — substantival participles that START
    # the line are topic/subject continuations from a previous clause and
    # should not merge. Mid-line substantival participles are embedded in
    # larger phrases and the merge is often correct.
    for idx in range(min(3, len(words))):
        w_clean = _clean(words[idx])
        if not w_clean:
            continue
        if not _is_article(w_clean):
            # Allow skipping known postpositive particles at line start
            if w_clean in _POSTPOSITIVE_PARTICLES:
                continue
            break  # not an article or particle, stop
        # Found an article — look at next 1-3 words for a participle
        for offset in range(1, min(4, len(words) - idx)):
            next_clean = _clean(words[idx + offset])
            if not next_clean:
                continue
            if _is_participle(next_clean):
                return True
            # Allow skipping known postpositive particles
            if next_clean not in _POSTPOSITIVE_PARTICLES:
                break
        break  # only check the first article encountered

    return False


# ---------- merge logic ----------

def find_merge_candidates(filepath, book_slug):
    """Find participle-frame lines that should merge with the next line.

    Returns list of dicts:
        {
            'file': filepath,
            'verse_ref': '5:2',
            'line_idx': 0,          # index within verse lines
            'participle_line': str,
            'resolution_line': str,
            'action': 'merge' | 'flag',
            'reason': str,
        }
    """
    verses = parse_chapter_file(filepath)
    candidates = []

    for v in verses:
        ch = v['chapter']
        vs = v['verse']
        content_lines = [l for l in v['lines'] if l.strip()]

        if len(content_lines) < 2:
            continue

        for i in range(len(content_lines) - 1):
            line_cur = content_lines[i]
            line_next = content_lines[i + 1]

            # --- Pre-checks: skip lines that should never merge ---

            # If current line ends with clause-final punctuation, it's
            # already a complete clause — do not merge forward
            if _line_ends_clause(line_cur):
                continue

            # If current line is a speech introduction, keep it separate
            if _is_speech_intro(line_cur):
                continue

            # Classify current and next line
            info_cur = _classify_words_on_line(line_cur, book_slug, ch, vs)
            info_next = _classify_words_on_line(line_next, book_slug, ch, vs)

            # Current line must have participle(s) but no finite verb
            if not info_cur['participle_only']:
                continue

            # Next line must have a finite verb (the resolution)
            if not info_next['has_finite_verb']:
                continue

            # If current line has a substantival participle (article + ptc),
            # it functions as a noun phrase, not a circumstantial frame — skip
            if _has_substantival_participle(line_cur, book_slug, ch, vs):
                continue

            # If next line starts with a relative pronoun (ὃς, ἥ, ὅ, etc.),
            # it's a relative clause, not a resolution of the participle — flag
            next_first_word = _clean(line_next.strip().split()[0]) if line_next.strip() else ''
            if next_first_word in _RELATIVE_PRONOUNS:
                candidates.append({
                    'file': filepath,
                    'verse_ref': v['ref'],
                    'line_idx': i,
                    'participle_line': line_cur.strip(),
                    'resolution_line': line_next.strip(),
                    'action': 'flag',
                    'reason': f'Next line starts with relative pronoun ({next_first_word}) — not a direct resolution',
                })
                continue

            # If current line ends with comma and next line starts with καί
            # + a new subject, this is likely a new independent clause, not
            # a resolution. Flag for review.
            cur_stripped = line_cur.rstrip()
            next_stripped = line_next.strip()
            if cur_stripped.endswith(',') and next_stripped.startswith('καὶ '):
                # Check if the next line has a noun/pronoun subject before the verb
                # (simple heuristic: if καί is followed by a non-verb word)
                candidates.append({
                    'file': filepath,
                    'verse_ref': v['ref'],
                    'line_idx': i,
                    'participle_line': line_cur.strip(),
                    'resolution_line': line_next.strip(),
                    'action': 'flag',
                    'reason': 'Comma + καί — likely new clause, not participle resolution',
                })
                continue

            # Check merged line length — if too long, flag instead of merge
            merged_len = len(line_cur.strip()) + 1 + len(line_next.strip())

            # --- Camera-angle exception ---
            # Check previous line (if any) for complete predication
            prev_has_predication = False
            if i > 0:
                line_prev = content_lines[i - 1]
                info_prev = _classify_words_on_line(line_prev, book_slug, ch, vs)
                prev_has_predication = _line_has_complete_predication(info_prev)

            # Get participle lemmas on current line
            ptc_lemmas = _get_participle_lemmas_on_line(line_cur, book_slug, ch, vs)

            # Decision logic
            if prev_has_predication:
                # Previous line is a complete thought. The participle MIGHT be
                # supplementary (camera angle). Check lemmas.
                if ptc_lemmas & SPATIAL_POSTURAL_LEMMAS:
                    # Spatial/postural participle after complete predication —
                    # likely a camera angle. Flag for review, do not merge.
                    candidates.append({
                        'file': filepath,
                        'verse_ref': v['ref'],
                        'line_idx': i,
                        'participle_line': line_cur.strip(),
                        'resolution_line': line_next.strip(),
                        'action': 'flag',
                        'reason': f'Camera angle? Prev line has predication, ptc lemma(s): {ptc_lemmas & SPATIAL_POSTURAL_LEMMAS}',
                    })
                    continue
                elif ptc_lemmas & FRAME_PARTICIPLE_LEMMAS:
                    # Temporal/causal frame participle — these typically need
                    # their resolution even when previous line is complete.
                    # But previous complete predication means this could be
                    # starting a new clause. Merge.
                    pass  # fall through to merge
                else:
                    # Unknown lemma with previous predication — flag for safety
                    candidates.append({
                        'file': filepath,
                        'verse_ref': v['ref'],
                        'line_idx': i,
                        'participle_line': line_cur.strip(),
                        'resolution_line': line_next.strip(),
                        'action': 'flag',
                        'reason': f'Prev line has predication, participle lemma(s) not in known sets: {ptc_lemmas}',
                    })
                    continue

            # Merged line too long? Flag instead
            if merged_len > 140:
                candidates.append({
                    'file': filepath,
                    'verse_ref': v['ref'],
                    'line_idx': i,
                    'participle_line': line_cur.strip(),
                    'resolution_line': line_next.strip(),
                    'action': 'flag',
                    'reason': f'Merged line would be {merged_len} chars (>140)',
                })
                continue

            # Default: merge the participle frame into the resolution line
            candidates.append({
                'file': filepath,
                'verse_ref': v['ref'],
                'line_idx': i,
                'participle_line': line_cur.strip(),
                'resolution_line': line_next.strip(),
                'action': 'merge',
                'reason': 'Dependent participle frame → merge with finite verb',
            })

    return candidates


def apply_merges(filepath, book_slug, candidates):
    """Apply merge candidates to a file. Returns number of merges applied."""
    merge_set = set()
    for c in candidates:
        if c['action'] == 'merge':
            merge_set.add((c['verse_ref'], c['line_idx']))

    if not merge_set:
        return 0

    verses = parse_chapter_file(filepath)
    merges_applied = 0

    for v in verses:
        content_indices = []
        for idx, line in enumerate(v['lines']):
            if line.strip():
                content_indices.append(idx)

        # Process merges in reverse order so indices stay valid
        merge_indices = []
        for ci, real_idx in enumerate(content_indices):
            if (v['ref'], ci) in merge_set:
                merge_indices.append((ci, real_idx))

        for ci, real_idx in reversed(merge_indices):
            # Find the next content line's real index
            if ci + 1 < len(content_indices):
                next_real_idx = content_indices[ci + 1]
                # Merge: prepend current line content to next line
                merged = v['lines'][real_idx].strip() + ' ' + v['lines'][next_real_idx].strip()
                v['lines'][next_real_idx] = merged
                # Remove the current line
                v['lines'].pop(real_idx)
                merges_applied += 1

    write_chapter_file(filepath, verses)
    return merges_applied


# ---------- book discovery ----------

def get_book_slug(filename):
    """Extract book slug from filename like 'mark-05.txt'."""
    m = re.match(r'^([a-z0-9]+)-\d+\.txt$', filename)
    return m.group(1) if m else None


def discover_files(book_filter=None):
    """Discover all v4-editorial files, optionally filtered by book."""
    files = []
    for f in sorted(os.listdir(V4_DIR)):
        if not f.endswith('.txt'):
            continue
        slug = get_book_slug(f)
        if slug and (book_filter is None or slug == book_filter):
            files.append((os.path.join(V4_DIR, f), slug))
    return files


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description='Detect and merge dependent participial frames')
    parser.add_argument('--dry-run', action='store_true', help='Report only, do not modify files')
    parser.add_argument('--book', type=str, default=None, help='Process only this book (e.g. mark)')
    args = parser.parse_args()

    files = discover_files(args.book)
    if not files:
        print(f"No files found" + (f" for book '{args.book}'" if args.book else ""))
        sys.exit(1)

    total_merge = 0
    total_flag = 0
    total_candidates = 0
    files_modified = 0

    print(f"{'DRY RUN: ' if args.dry_run else ''}Scanning {len(files)} files...")
    print()

    for filepath, book_slug in files:
        fname = os.path.basename(filepath)
        candidates = find_merge_candidates(filepath, book_slug)

        if not candidates:
            continue

        merges = [c for c in candidates if c['action'] == 'merge']
        flags = [c for c in candidates if c['action'] == 'flag']

        total_candidates += len(candidates)
        total_merge += len(merges)
        total_flag += len(flags)

        if merges or flags:
            print(f"--- {fname} ---")

        for c in merges:
            print(f"  MERGE {c['verse_ref']} line {c['line_idx']}:")
            print(f"    {c['participle_line']}")
            print(f"    + {c['resolution_line']}")
            print(f"    Reason: {c['reason']}")

        for c in flags:
            print(f"  FLAG  {c['verse_ref']} line {c['line_idx']}:")
            print(f"    {c['participle_line']}")
            print(f"    + {c['resolution_line']}")
            print(f"    Reason: {c['reason']}")

        if not args.dry_run and merges:
            applied = apply_merges(filepath, book_slug, candidates)
            if applied:
                files_modified += 1
                print(f"  -> Applied {applied} merges")

        print()

    # Summary
    print("=" * 60)
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"{mode} SUMMARY")
    print(f"  Files scanned:     {len(files)}")
    print(f"  Total candidates:  {total_candidates}")
    print(f"  Would merge:       {total_merge}")
    print(f"  Flagged (review):  {total_flag}")
    if not args.dry_run:
        print(f"  Files modified:    {files_modified}")
    print("=" * 60)


if __name__ == '__main__':
    main()
