#!/usr/bin/env python3
"""
Independent English colometric formatter for WEB (World English Bible) text.

Applies three criteria to break English text into sense-lines:
  1. Atomic thought -- each line is one complete predication
  2. Single image   -- each line paints one picture
  3. Breath unit    -- each line is speakable in one natural breath (~3-25 words)

This formatter treats the English as the source text and does NOT consult
the Greek colometric breaks.  The result can then be compared against the
Greek editorial file to measure structural convergence.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/english_colometry.py
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR   = os.path.dirname(SCRIPT_DIR)
INPUT_FILE = os.path.join(REPO_DIR, 'research', 'web', 'raw', '41_4.json')
OUTPUT_DIR = os.path.join(REPO_DIR, 'data', 'text-files', 'web-independent')
OUTPUT_FILE= os.path.join(OUTPUT_DIR, 'mark-04.txt')
GREEK_FILE = os.path.join(REPO_DIR, 'data', 'text-files', 'v4-editorial', 'mark-04.txt')

# ---------------------------------------------------------------------------
# spaCy setup
# ---------------------------------------------------------------------------

import spacy

nlp = spacy.load('en_core_web_sm')

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

SUBORDINATORS = {
    'that', 'which', 'who', 'whom', 'whose', 'when', 'where', 'while',
    'if', 'because', 'since', 'although', 'though', 'unless', 'until',
    'before', 'after', 'lest', 'whereas',
}

COORDINATORS = {'and', 'but', 'for', 'or', 'nor', 'yet', 'so'}

# Patterns that indicate a speech introduction
SPEECH_INTRO_RE = re.compile(
    r'^(He|She|They|Jesus|Peter|John|James|Simon|Andrew|Philip|Thomas|'
    r'Judas|Bartholomew|Matthew|Nathanael|Pilate|The [a-z]+)\s+'
    r'(said|says|told|answered|asked|cried|shouted|replied|called|spoke)\b',
    re.IGNORECASE
)


def is_finite_verb(tok):
    """Return True if token is a finite verb form (not gerund/infinitive/participle)."""
    if tok.pos_ != 'VERB' and tok.pos_ != 'AUX':
        return False
    morph = tok.morph.to_dict()
    verb_form = morph.get('VerbForm', '')
    if verb_form in ('Inf', 'Ger', 'Part'):
        return False
    # If spaCy tagged it as VERB/AUX and it's not infinitive/gerund/participle,
    # treat it as finite
    return True


def has_verb(line_tokens):
    """Check if a list of tokens contains at least one finite verb."""
    for tok in line_tokens:
        if is_finite_verb(tok):
            return True
    return False


def is_legitimate_fragment(text):
    """Some fragments are legitimate: vocatives, exclamations, lists, ellipsis."""
    text = text.strip().strip('\u201c\u201d"\'')
    # Short exclamations / vocatives
    if text.endswith('!') or text.startswith('Listen') or text.startswith('Behold'):
        return True
    if text.startswith('Peace') or text.startswith('Be still'):
        return True
    if text.startswith('Teacher') or text.startswith('Master'):
        return True
    # List items (some thirty times, etc.)
    if re.match(r'^(some|first|then)\s', text, re.IGNORECASE):
        return True
    # Very short fragment that is an interjection / quoted speech
    if len(text.split()) <= 4:
        return True
    return False


def split_verse_into_lines(text):
    """
    Core colometric engine.  Takes a verse's English text and returns
    a list of sense-line strings.
    """
    text = text.strip()
    if not text:
        return []

    # ---- Step 0: separate quoted speech blocks that are clearly delimited ----
    # We'll work on the full text as one unit, but track quote boundaries.

    doc = nlp(text)
    tokens = list(doc)

    # ---- Step 1: identify potential break points ----
    # A break point is the index of a token that should START a new line.
    break_indices = set()

    for i, tok in enumerate(tokens):
        if i == 0:
            continue

        lower = tok.text.lower()

        # --- Speech introductions ---
        # Look for "He said," / "He said to them," patterns
        # These get their own line -- we break AFTER the speech intro
        if tok.text in (',', '\u201c', '"') and i >= 2:
            window = doc[max(0, i-6):i].text
            if SPEECH_INTRO_RE.match(window):
                # The comma/quote after "said" -- next token starts new line
                if i + 1 < len(tokens):
                    break_indices.add(i + 1)

        # --- Subordinating conjunctions ---
        # Skip "that" if preceded by "so" (handled as "so that" unit)
        if lower == 'that' and i > 0 and tokens[i-1].text.lower() == 'so':
            pass  # already handled as "so that"
        elif lower in SUBORDINATORS and tok.dep_ in ('mark', 'advmod', 'nsubj',
                                                      'nsubjpass', 'relcl',
                                                      'advcl', 'attr', 'dobj',
                                                      'pobj', 'ROOT'):
            break_indices.add(i)
        # Also catch relative pronouns via dependency
        if tok.dep_ in ('relcl',) and tok.pos_ == 'VERB':
            # find the relative pronoun that introduces this clause
            for child in tok.children:
                if child.dep_ in ('nsubj', 'nsubjpass', 'dobj', 'pobj', 'advmod') and \
                   child.text.lower() in ('who', 'whom', 'whose', 'which', 'where', 'when', 'that'):
                    # Don't break if the relative pronoun immediately follows
                    # its antecedent (e.g. "those who", "he who", "the ones who")
                    # -- this would leave a dangling antecedent
                    ci = child.i
                    if ci > 0:
                        prev_tok = tokens[ci - 1]
                        if prev_tok.text.lower() in ('those', 'these', 'ones', 'him',
                                                      'he', 'she', 'them', 'they',
                                                      'one', 'anyone', 'whoever'):
                            break  # skip this break
                        # Also skip if previous is a comma after short phrase
                        if prev_tok.text == ',' and ci >= 2:
                            before_comma = tokens[ci - 2]
                            if before_comma.text.lower() in ('those', 'these', 'ones',
                                                              'places', 'ground', 'seed'):
                                break
                    break_indices.add(ci)
                    break

        # --- Coordinating conjunctions with new clause ---
        if lower in COORDINATORS:
            # Break if this conjunction introduces a new finite clause
            # Heuristic: next non-punct token is a subject or verb
            j = i + 1
            while j < len(tokens) and tokens[j].is_punct:
                j += 1
            if j < len(tokens):
                next_tok = tokens[j]
                # "yet when" — don't break; let "when" trigger the break
                # and the coordinator will attach to the subordinate clause
                if lower == 'yet' and next_tok.text.lower() in SUBORDINATORS:
                    pass
                # New subject after coordinator
                elif next_tok.dep_ in ('nsubj', 'nsubjpass'):
                    break_indices.add(i)
                # Verb right after coordinator (implicit subject)
                elif is_finite_verb(next_tok) and next_tok.dep_ in ('ROOT', 'conj'):
                    break_indices.add(i)
                # "and said" / "and told" after narrative
                elif next_tok.pos_ == 'VERB' and next_tok.lemma_ in (
                    'say', 'tell', 'ask', 'answer', 'cry', 'call', 'rebuke', 'speak'):
                    break_indices.add(i)

        # --- "so that" / "so much that" ---
        if lower == 'so' and i + 1 < len(tokens) and tokens[i+1].text.lower() == 'that':
            break_indices.add(i)
        if lower == 'so' and i + 1 < len(tokens) and tokens[i+1].text.lower() == 'much':
            break_indices.add(i)

        # --- Semicolons as clause separators ---
        if tok.text == ';':
            if i + 1 < len(tokens):
                break_indices.add(i + 1)

        # --- "lest perhaps" ---
        if lower == 'lest':
            break_indices.add(i)

        # --- Sentence boundaries within a verse ---
        if tok.is_sent_start and i > 0:
            break_indices.add(i)

    # ---- Step 2: split into lines at break points ----
    sorted_breaks = sorted(break_indices)
    lines = []
    prev = 0
    for bp in sorted_breaks:
        if bp > prev:
            line_toks = tokens[prev:bp]
            line_text = doc[prev:bp].text.strip()
            if line_text:
                lines.append((line_text, line_toks))
        prev = bp
    # last segment
    if prev < len(tokens):
        line_text = doc[prev:len(tokens)].text.strip()
        line_toks = tokens[prev:]
        if line_text:
            lines.append((line_text, line_toks))

    if not lines:
        return [text]

    # ---- Step 3: merge fragments (no verb, not legitimate) ----
    # First pass: merge single-word conjunctions/adverbs forward into next line
    forward_merged = []
    skip_next = False
    for idx, (line_text, line_toks) in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        stripped = line_text.strip().rstrip('.,;:!?\u201c\u201d"\'')
        if (len(stripped.split()) <= 2
            and stripped.lower() in ('yet', 'so', 'but', 'and', 'for', 'or',
                                     'yet when', 'so that', 'so much')
            and idx + 1 < len(lines)):
            # Merge with next line
            next_text, next_toks = lines[idx + 1]
            combined_text = line_text.rstrip() + ' ' + next_text.lstrip()
            combined_toks = list(line_toks) + list(next_toks)
            forward_merged.append((combined_text, combined_toks))
            skip_next = True
        else:
            forward_merged.append((line_text, list(line_toks)))

    # Second pass: merge remaining fragments backward
    merged = []
    for line_text, line_toks in forward_merged:
        if merged and not has_verb(line_toks) and not is_legitimate_fragment(line_text):
            # Merge with previous line
            prev_text, prev_toks = merged[-1]
            combined_text = prev_text + ' ' + line_text
            combined_toks = list(prev_toks) + list(line_toks)
            merged[-1] = (combined_text, combined_toks)
        else:
            merged.append((line_text, list(line_toks)))

    # ---- Step 4: split overly long lines (>25 words with multiple predications) ----
    final = []
    for line_text, line_toks in merged:
        words = line_text.split()
        if len(words) > 25:
            # Try to find a mid-point coordinator or subordinator to split
            mid = len(line_toks) // 3  # don't split too early
            split_at = None
            for k in range(mid, len(line_toks)):
                if line_toks[k].text.lower() in COORDINATORS | SUBORDINATORS:
                    # Make sure there's content after
                    after_text = ''.join(t.text_with_ws for t in line_toks[k:]).strip()
                    if len(after_text.split()) >= 3:
                        split_at = k
                        break
            if split_at:
                part1 = ''.join(t.text_with_ws for t in line_toks[:split_at]).strip()
                part2 = ''.join(t.text_with_ws for t in line_toks[split_at:]).strip()
                if part1:
                    final.append(part1)
                if part2:
                    final.append(part2)
            else:
                final.append(line_text)
        else:
            final.append(line_text)

    # ---- Step 5: clean up whitespace / punctuation ----
    result = []
    for line in final:
        line = re.sub(r'\s+', ' ', line).strip()
        if line:
            result.append(line)

    # ---- Step 6: merge orphaned quotes/punctuation with adjacent lines ----
    cleaned = []
    for line in result:
        stripped = line.strip('\u201c\u201d"\'').strip()
        # If line is just a quote mark or empty after stripping, merge forward
        if not stripped or len(stripped) <= 1:
            if cleaned:
                cleaned[-1] = cleaned[-1] + ' ' + line
            # else drop it (shouldn't happen)
        else:
            cleaned.append(line)

    return cleaned if cleaned else [text]


# ---------------------------------------------------------------------------
# Greek file parser (count lines per verse)
# ---------------------------------------------------------------------------

def parse_greek_lines(filepath):
    """Parse the Greek editorial file, return {verse_num: line_count}."""
    verse_lines = {}
    current_verse = None
    line_count = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for raw in f:
            raw = raw.rstrip('\n')
            # Verse reference line like "4:1"
            m = re.match(r'^(\d+):(\d+)$', raw.strip())
            if m:
                if current_verse is not None:
                    verse_lines[current_verse] = line_count
                current_verse = int(m.group(2))
                line_count = 0
                continue
            # Blank line
            if raw.strip() == '':
                continue
            # Content line
            if current_verse is not None:
                line_count += 1

        # last verse
        if current_verse is not None:
            verse_lines[current_verse] = line_count

    return verse_lines


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    # ---- Load WEB text ----
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        verses = json.load(f)

    # Sort by verse number
    verses.sort(key=lambda v: v['verse'])

    # ---- Format each verse ----
    english_results = {}  # verse_num -> list of lines
    for v in verses:
        vnum = v['verse']
        text = v['text'].strip()
        # Clean up double spaces, smart quotes are fine
        text = re.sub(r'\s+', ' ', text)
        lines = split_verse_into_lines(text)
        english_results[vnum] = lines

    # ---- Write output ----
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for vnum in sorted(english_results.keys()):
            f.write(f'4:{vnum}\n')
            for line in english_results[vnum]:
                f.write(f'{line}\n')
            f.write('\n')

    print(f'Wrote {OUTPUT_FILE}')
    print(f'  {len(english_results)} verses, '
          f'{sum(len(v) for v in english_results.values())} total lines')
    print()

    # ---- Load Greek lines for comparison ----
    greek_lines = parse_greek_lines(GREEK_FILE)

    # ---- Comparison table ----
    print('=' * 78)
    print(f'{"Verse":>6}  {"Eng":>4}  {"Grk":>4}  {"Result":<20}')
    print('-' * 78)

    match = 0
    eng_more = 0
    eng_fewer = 0
    total = 0

    for vnum in sorted(english_results.keys()):
        e_count = len(english_results[vnum])
        g_count = greek_lines.get(vnum, 0)

        if e_count == g_count:
            label = 'MATCH'
            match += 1
        elif e_count > g_count:
            label = f'ENGLISH MORE (+{e_count - g_count})'
            eng_more += 1
        else:
            label = f'ENGLISH FEWER (-{g_count - e_count})'
            eng_fewer += 1
        total += 1

        print(f'  4:{vnum:<3}  {e_count:>4}  {g_count:>4}  {label}')

    print('-' * 78)
    print(f'  MATCH:        {match:>3} / {total}  ({100*match/total:.0f}%)')
    print(f'  ENGLISH MORE: {eng_more:>3} / {total}  ({100*eng_more/total:.0f}%)')
    print(f'  ENGLISH FEWER:{eng_fewer:>3} / {total}  ({100*eng_fewer/total:.0f}%)')
    print('=' * 78)
    print()

    # ---- Side-by-side for selected verses ----
    spotlight = [1, 4, 8, 12, 19, 32, 39, 41]
    print('SIDE-BY-SIDE COMPARISON')
    print('=' * 90)

    for vnum in spotlight:
        e_lines = english_results.get(vnum, ['(missing)'])
        # Read Greek lines for this verse from file
        g_lines = _read_greek_verse(vnum)

        max_lines = max(len(e_lines), len(g_lines))
        print(f'\n--- 4:{vnum} ---')
        print(f'  {"ENGLISH (WEB)":<44}  {"GREEK (SBLGNT)":<44}')
        for i in range(max_lines):
            e = e_lines[i] if i < len(e_lines) else ''
            g = g_lines[i] if i < len(g_lines) else ''
            # Truncate for display
            if len(e) > 42:
                e = e[:39] + '...'
            if len(g) > 42:
                g = g[:39] + '...'
            print(f'  {e:<44}  {g:<44}')

    print()
    print('=' * 90)


def _read_greek_verse(target_verse):
    """Read the actual Greek text lines for a specific verse."""
    lines = []
    in_verse = False
    with open(GREEK_FILE, 'r', encoding='utf-8') as f:
        for raw in f:
            raw = raw.rstrip('\n')
            m = re.match(r'^(\d+):(\d+)$', raw.strip())
            if m:
                if in_verse:
                    break
                if int(m.group(2)) == target_verse:
                    in_verse = True
                continue
            if in_verse:
                if raw.strip() == '':
                    break
                lines.append(raw.strip())
    return lines if lines else ['(missing)']


if __name__ == '__main__':
    main()
