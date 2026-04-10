#!/usr/bin/env python3
"""
ylt_align_double.py — Double-wiring alignment prototype for Mark 4.

Two-hop alignment:
  Hop 1: Greek colometric lines → Macula English interlinear (per-line)
  Hop 2: Macula English → Translation (YLT or WEB) via word-level LCS

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align_double.py
"""

import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
V4_DIR = REPO / "data" / "text-files" / "v4-editorial"
V3_DIR = REPO / "data" / "text-files" / "v3-colometric"
YLT_RAW_DIR = REPO / "research" / "ylt" / "raw"
WEB_RAW_DIR = REPO / "research" / "web" / "raw"
LOWFAT_DIR = REPO / "research" / "macula-greek" / "SBLGNT" / "lowfat"

# ---------------------------------------------------------------------------
# Synonym sets (imported from ylt_align.py concept)
# ---------------------------------------------------------------------------
_SYNONYM_SETS = [
    ("listen", "hearken", "hear", "heard"),
    ("behold", "lo", "look", "see", "saw", "seen"),
    ("say", "said", "saying", "saith", "says"),
    ("go", "went", "gone", "goeth"),
    ("come", "came", "cometh", "comes"),
    ("make", "made", "maketh", "makes"),
    ("give", "gave", "giveth", "given", "gives"),
    ("take", "took", "taketh", "taken", "takes"),
    ("know", "knew", "knoweth", "known", "knows"),
    ("send", "sent", "sendeth", "sends"),
    ("do", "did", "doeth", "done", "does"),
    ("speak", "spoke", "spake", "speaketh", "spoken", "speaks"),
    ("call", "called", "calleth", "calls"),
    ("answer", "answered", "answereth", "answers"),
    ("ask", "asked", "asketh", "request", "requested"),
    ("tell", "told", "telleth", "tells"),
    ("write", "wrote", "written", "writes"),
    ("begin", "began", "begun", "begins"),
    ("put", "placed", "set", "puts"),
    ("raise", "raised", "rose", "arise", "arose", "risen", "rise", "rising"),
    ("die", "died", "dead", "death", "dies"),
    ("kill", "killed", "slew", "slain", "slay", "slaughter"),
    ("eat", "ate", "eaten", "devour", "devoured"),
    ("drink", "drank", "drunk"),
    ("sit", "sat", "sitteth", "sits"),
    ("stand", "stood", "standeth", "stands"),
    ("fall", "fell", "fallen", "falls"),
    ("find", "found", "finds"),
    ("leave", "left", "leaves"),
    ("bring", "brought", "bringeth", "brings"),
    ("think", "thought", "thinks"),
    ("teach", "taught", "teaches"),
    ("seek", "sought", "seeks"),
    ("buy", "bought"),
    ("catch", "caught"),
    ("fight", "fought"),
    ("child", "children"),
    ("man", "men"),
    ("woman", "women"),
    ("brother", "brethren"),
    ("lord", "master"),
    ("servant", "slave", "bondman"),
    ("nation", "nations", "gentile", "gentiles", "heathen"),
    ("suddenly", "straightway", "immediately", "at once"),
    ("sow", "sowed", "sowing", "sown", "sower", "sows"),
    ("spring", "sprang", "sprung", "springs"),
    ("bear", "bore", "bare", "born", "borne", "bearing", "bears"),
    ("bird", "birds", "fowl", "fowls"),
    ("way", "road", "path"),
    ("grow", "grew", "grown", "increase", "increased", "grows", "increasing"),
    ("earth", "soil", "ground"),
    ("good", "beautiful", "fair"),
    ("hundred", "hundredfold"),
    ("thirty", "thirtyfold"),
    ("sixty", "sixtyfold"),
    ("throw", "threw", "thrown", "cast", "casts"),
    ("hide", "hid", "hidden", "secret", "concealed"),
    ("wake", "woke", "woken", "awake", "awoke"),
    ("forgive", "forgave", "forgiven"),
    ("yield", "yielded", "yields"),
    ("choke", "choked", "chokes"),
    ("wither", "withered", "withers"),
    ("scorch", "scorched"),
    ("fruit", "fruits", "grain"),
    ("reign", "kingdom"),
    ("simile", "parable", "parables", "similes"),
    ("sleep", "slept", "sleeping", "sleeps"),
    ("night", "evening"),
    ("blade", "grass"),
    ("ear", "ears", "head"),
    ("corn", "wheat", "grain"),
    ("harvest", "reaping"),
    ("sickle", "scythe"),
    ("mustard", "grain"),
    ("seed", "seeds"),
    ("herb", "herbs", "plant", "plants", "garden plants", "vegetables"),
    ("branch", "branches"),
    ("shade", "shadow"),
    ("rest", "nest", "lodge"),
    ("lamp", "light", "candle"),
    ("measure", "bushel"),
    ("bed", "couch"),
    ("lampstand", "lamp-stand", "candlestick"),
    ("boat", "ship"),
    ("storm", "tempest", "squall"),
    ("wind", "gale"),
    ("wave", "waves", "billows"),
    ("pillow", "cushion"),
    ("teacher", "master", "rabbi"),
    ("perish", "die", "destroyed"),
    ("peace", "quiet", "still", "calm"),
    ("rebuke", "rebuked", "rebukes"),
    ("fear", "feared", "afraid", "fearful"),
    ("obey", "obeys", "obeyed"),
    ("able", "can"),
    ("great", "large", "big"),
    ("anxieties", "cares", "worries", "anxiety", "care"),
    ("deceitfulness", "deceit", "deception"),
    ("riches", "wealth", "rich"),
    ("desire", "desires", "lust", "lusts"),
    ("unfruitful", "fruitless", "unproductive"),
    ("manifest", "manifested", "revealed", "disclosed"),
    ("light", "open"),
]

_SYNONYM_MAP = {}
for syn_set in _SYNONYM_SETS:
    for word in syn_set:
        w = word.lower()
        if w not in _SYNONYM_MAP:
            _SYNONYM_MAP[w] = set()
        for other in syn_set:
            _SYNONYM_MAP[w].add(other.lower())


def _are_synonyms(a, b):
    a, b = a.lower(), b.lower()
    if a in _SYNONYM_MAP and b in _SYNONYM_MAP[a]:
        return True
    if b in _SYNONYM_MAP and a in _SYNONYM_MAP[b]:
        return True
    return False


def _stem_english(word):
    """Simple English stemmer for alignment matching."""
    w = word.lower()
    if len(w) <= 3:
        return w
    if w.endswith('ying') and len(w) > 5:
        return w[:-3]
    if w.endswith('ied') and len(w) > 4:
        return w[:-3] + 'y'
    if w.endswith('ies') and len(w) > 4:
        return w[:-3] + 'y'
    if w.endswith('ing') and len(w) > 5:
        base = w[:-3]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]
        return base
    if w.endswith('eth') and len(w) > 5:
        return w[:-3]
    if w.endswith('est') and len(w) > 5:
        return w[:-3]
    if w.endswith('ed') and len(w) > 4:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]
        return base
    if w.endswith('en') and len(w) > 4 and not w.endswith('men') and not w.endswith('ten'):
        return w[:-2]
    if w.endswith('er') and len(w) > 4:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]
        return base
    if w.endswith('s') and len(w) > 3 and not w.endswith('ss') and not w.endswith('us'):
        return w[:-1]
    return w


def _words_match(a, b):
    """Check if two words match via exact, stem, or synonym."""
    a_low, b_low = a.lower(), b.lower()
    if a_low == b_low:
        return True
    a_stem = _stem_english(a_low)
    b_stem = _stem_english(b_low)
    if a_stem == b_stem and len(a_stem) >= 3:
        return True
    if _are_synonyms(a_low, b_low):
        return True
    if _are_synonyms(a_stem, b_stem):
        return True
    return False


# ---------------------------------------------------------------------------
# Macula XML parsing
# ---------------------------------------------------------------------------
_REF_RE = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_macula_ref(ref_str):
    m = _REF_RE.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


def load_macula_mark():
    """Load Macula XML for Mark.
    Returns: {(chapter, verse): [(word_pos, normalized_greek, english), ...]}
    """
    filepath = LOWFAT_DIR / "02-mark.xml"
    tree = ET.parse(str(filepath))
    root = tree.getroot()

    verse_words = defaultdict(list)
    for w in root.iter('w'):
        ref = w.get('ref', '')
        book, ch, vs, pos = _parse_macula_ref(ref)
        if ch is None:
            continue
        normalized = w.get('normalized', '') or (w.text or '')
        english = w.get('english', '')
        verse_words[(ch, vs)].append((pos, normalized, english))

    for key in verse_words:
        verse_words[key].sort(key=lambda x: x[0])

    return dict(verse_words)


# ---------------------------------------------------------------------------
# Parse colometric Greek file
# ---------------------------------------------------------------------------
def parse_greek_chapter(filepath):
    """Parse a colometric file. Returns {verse_num: [line1, line2, ...]}."""
    lines = Path(filepath).read_text(encoding="utf-8").splitlines()
    verses = {}
    current_verse = None
    current_lines = []

    verse_re = re.compile(r"^(\d+):(\d+)$")

    for line in lines:
        line = line.rstrip()
        m = verse_re.match(line)
        if m:
            if current_verse is not None:
                while current_lines and not current_lines[-1].strip():
                    current_lines.pop()
                verses[current_verse] = current_lines
            current_verse = int(m.group(2))
            current_lines = []
        elif current_verse is not None:
            if line.strip() == '' and not current_lines:
                continue  # skip leading blanks
            current_lines.append(line)

    if current_verse is not None:
        while current_lines and not current_lines[-1].strip():
            current_lines.pop()
        verses[current_verse] = current_lines

    return verses


# ---------------------------------------------------------------------------
# Hop 1: Build per-line Macula English interlinear
# ---------------------------------------------------------------------------
def build_macula_interlinear(macula_words, greek_lines):
    """For a single verse, assign each Macula word to a colometric line.

    macula_words: [(word_pos, normalized_greek, english), ...]
    greek_lines: [line1_text, line2_text, ...]

    Returns: [(english_word_or_phrase, line_idx), ...] — one entry per Macula word
    """
    # Build list of Greek words per line (strip punctuation for matching)
    def strip_greek_punct(s):
        return re.sub(r'[·;,.\-—\'ʼ\u0027\u2019\u02BC]', '', s).strip()

    line_greek_words = []
    for idx, line in enumerate(greek_lines):
        words = line.split()
        for w in words:
            stripped = strip_greek_punct(w)
            if stripped:
                line_greek_words.append((stripped, idx))

    # For each Macula word, find its line by matching against the Greek line words
    # Use sequential matching — each Macula word matches the next unmatched Greek word
    result = []
    greek_ptr = 0

    for pos, norm_greek, english in macula_words:
        stripped_norm = strip_greek_punct(norm_greek)
        if not english:
            continue

        # Try to find this Greek word starting from greek_ptr
        best_idx = None
        for i in range(greek_ptr, len(line_greek_words)):
            if line_greek_words[i][0] == stripped_norm:
                best_idx = i
                greek_ptr = i + 1
                break

        if best_idx is not None:
            line_idx = line_greek_words[best_idx][1]
        else:
            # Fallback: try broader search from beginning
            for i in range(len(line_greek_words)):
                if line_greek_words[i][0] == stripped_norm:
                    best_idx = i
                    break
            if best_idx is not None:
                line_idx = line_greek_words[best_idx][1]
            else:
                # Last resort: assign to the line of the previous word or 0
                line_idx = result[-1][1] if result else 0

        # Split multi-word english values into individual tokens
        eng_tokens = english.split()
        for tok in eng_tokens:
            result.append((tok, line_idx))

    return result


# ---------------------------------------------------------------------------
# Hop 2: LCS-based English-to-English alignment
# ---------------------------------------------------------------------------
def lcs_word_align(macula_tokens, trans_tokens):
    """Find longest common subsequence between Macula English and translation.

    macula_tokens: [(word, line_idx), ...] — Macula english attrs with line assignments
    trans_tokens: [word, ...] — translation words

    Returns: [line_idx_or_None, ...] for each translation token
    """
    m_words = [t[0].lower() for t in macula_tokens]
    t_words = [t.lower() for t in trans_tokens]
    n = len(m_words)
    m = len(t_words)

    if n == 0 or m == 0:
        return [0] * m

    # DP table for LCS
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if _words_match(m_words[i - 1], t_words[j - 1]):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtrack to find aligned pairs
    aligned = [None] * m  # line_idx for each trans token
    i, j = n, m
    while i > 0 and j > 0:
        if _words_match(m_words[i - 1], t_words[j - 1]):
            aligned[j - 1] = macula_tokens[i - 1][1]  # inherit line_idx
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    # Forward-fill unmatched: assign to NEXT matched word's line
    # Walk right to left to find the next matched word
    next_line = None
    for k in range(m - 1, -1, -1):
        if aligned[k] is not None:
            next_line = aligned[k]
        else:
            aligned[k] = next_line

    # If still None (no match found after this point), back-fill from previous
    prev_line = None
    for k in range(m):
        if aligned[k] is not None:
            prev_line = aligned[k]
        else:
            aligned[k] = prev_line if prev_line is not None else 0

    return aligned


def align_translation_to_lines(macula_interlinear, trans_text, num_lines):
    """Align a translation text to colometric lines using double-wiring.

    Returns: [line_text_0, line_text_1, ...] — translation text split per line
    """
    # Tokenize translation, preserving punctuation attached to words
    trans_words = trans_text.split()
    if not trans_words:
        return [""] * num_lines

    # Strip punctuation for matching, but keep original for output
    def strip_punct(w):
        return re.sub(r"[^a-zA-Z'-]", '', w).strip("'-")

    trans_clean = [strip_punct(w) for w in trans_words]

    # Filter out empty tokens from macula for matching
    macula_for_lcs = [(w, idx) for w, idx in macula_interlinear if strip_punct(w)]

    # Run LCS alignment
    line_assignments = lcs_word_align(macula_for_lcs, trans_clean)

    # Group translation words by line
    lines = defaultdict(list)
    for k, word in enumerate(trans_words):
        line_idx = line_assignments[k] if k < len(line_assignments) else 0
        lines[line_idx].append(word)

    result = []
    for i in range(num_lines):
        result.append(" ".join(lines.get(i, [])))

    return result


# ---------------------------------------------------------------------------
# Download / cache chapter data
# ---------------------------------------------------------------------------
def download_chapter(translation, booknum, chapter):
    """Download a chapter from bolls.life API and cache it."""
    if translation == "YLT":
        raw_dir = YLT_RAW_DIR
    else:
        raw_dir = WEB_RAW_DIR

    raw_path = raw_dir / f"{booknum}_{chapter}.json"
    if raw_path.exists():
        return json.loads(raw_path.read_text(encoding="utf-8"))

    raw_dir.mkdir(parents=True, exist_ok=True)
    url = f"https://bolls.life/get-chapter/{translation}/{booknum}/{chapter}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        print(f"  Downloading {translation} {booknum}:{chapter} ...", file=sys.stderr)
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR downloading {url}: {e}", file=sys.stderr)
        return []

    raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def load_translation_chapter(translation, booknum, chapter):
    """Load a chapter's verse text. Returns {verse_num: text}."""
    data = download_chapter(translation, booknum, chapter)
    result = {}
    for v in data:
        result[v["verse"]] = v["text"].strip()
    return result


# ---------------------------------------------------------------------------
# Quality assessment
# ---------------------------------------------------------------------------
def assess_alignment(aligned_lines, macula_lines_text):
    """Assess quality of an alignment. Returns (is_clean, issues)."""
    issues = []

    for i, line in enumerate(aligned_lines):
        if not line.strip() and macula_lines_text[i].strip():
            issues.append(f"L{i+1}: empty (macula has content)")
        # Check for orphaned single function words
        words = line.split()
        if len(words) == 1 and words[0].lower().rstrip('.,;:!?\'"') in {
            'the', 'a', 'an', 'of', 'and', 'or', 'to', 'in', 'for'
        }:
            issues.append(f"L{i+1}: orphaned function word '{words[0]}'")

    # Check for split phrases — a content word at end of one line and its
    # article/preposition at the start
    for i in range(len(aligned_lines) - 1):
        words_curr = aligned_lines[i].split()
        words_next = aligned_lines[i + 1].split()
        if words_curr and words_next:
            last = words_curr[-1].lower().rstrip('.,;:!?\'"')
            if last in {'the', 'a', 'an', 'of', 'to', 'in', 'for', 'by', 'with'}:
                issues.append(f"L{i+1}->L{i+2}: dangling '{last}' at end of line")

    is_clean = len(issues) == 0
    return is_clean, issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("Double-Wiring Alignment Prototype — Mark 4")
    print("=" * 70)
    print()

    # Load data
    print("Loading Macula XML for Mark...", file=sys.stderr)
    macula_data = load_macula_mark()

    # Load colometric Greek — prefer v4, fall back to v3
    greek_path = V4_DIR / "mark-04.txt"
    if not greek_path.exists():
        greek_path = V3_DIR / "mark-04.txt"
    print(f"Loading Greek colometric: {greek_path}", file=sys.stderr)
    greek_verses = parse_greek_chapter(greek_path)

    # Load translations
    ylt_verses = load_translation_chapter("YLT", 41, 4)
    web_verses = load_translation_chapter("WEB", 41, 4)

    # Test verses
    test_verses = [1, 4, 9, 19, 21, 26, 32, 35]

    print("=" * 70)
    print("SELECTED VERSE ANALYSIS")
    print("=" * 70)

    for vn in test_verses:
        if vn not in greek_verses:
            print(f"\n=== Mark 4:{vn} === (not found in colometric)")
            continue

        g_lines = greek_verses[vn]
        macula_words = macula_data.get((4, vn), [])
        num_lines = len(g_lines)

        # Hop 1: Build Macula interlinear
        macula_interlinear = build_macula_interlinear(macula_words, g_lines)

        # Build per-line Macula English text for display
        macula_lines_text = defaultdict(list)
        for eng, line_idx in macula_interlinear:
            macula_lines_text[line_idx].append(eng)

        # Hop 2: Align YLT and WEB
        ylt_text = ylt_verses.get(vn, "")
        web_text = web_verses.get(vn, "")

        ylt_aligned = align_translation_to_lines(macula_interlinear, ylt_text, num_lines)
        web_aligned = align_translation_to_lines(macula_interlinear, web_text, num_lines)

        print(f"\n=== Mark 4:{vn} ===")
        print("GREEK:")
        for i, line in enumerate(g_lines):
            print(f"  L{i+1}: {line}")

        print("MACULA INTERLINEAR:")
        for i in range(num_lines):
            words = macula_lines_text.get(i, [])
            print(f"  L{i+1}: {' '.join(words)}")

        print("YLT ALIGNED:")
        for i, line in enumerate(ylt_aligned):
            print(f"  L{i+1}: {line}")

        print("WEB ALIGNED:")
        for i, line in enumerate(web_aligned):
            print(f"  L{i+1}: {line}")

    # -----------------------------------------------------------------------
    # Full chapter analysis
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("FULL CHAPTER ANALYSIS — ALL 41 VERSES")
    print("=" * 70)

    ylt_clean = 0
    ylt_problem_verses = []
    web_clean = 0
    web_problem_verses = []
    total = 0

    for vn in sorted(greek_verses.keys()):
        g_lines = greek_verses[vn]
        macula_words = macula_data.get((4, vn), [])
        num_lines = len(g_lines)
        if num_lines == 0:
            continue
        total += 1

        macula_interlinear = build_macula_interlinear(macula_words, g_lines)

        macula_lines_text = defaultdict(list)
        for eng, line_idx in macula_interlinear:
            macula_lines_text[line_idx].append(eng)
        macula_display = []
        for i in range(num_lines):
            macula_display.append(" ".join(macula_lines_text.get(i, [])))

        # YLT
        ylt_text = ylt_verses.get(vn, "")
        ylt_aligned = align_translation_to_lines(macula_interlinear, ylt_text, num_lines)
        ylt_ok, ylt_issues = assess_alignment(ylt_aligned, macula_display)
        if ylt_ok:
            ylt_clean += 1
        else:
            ylt_problem_verses.append((vn, ylt_issues))

        # WEB
        web_text = web_verses.get(vn, "")
        web_aligned = align_translation_to_lines(macula_interlinear, web_text, num_lines)
        web_ok, web_issues = assess_alignment(web_aligned, macula_display)
        if web_ok:
            web_clean += 1
        else:
            web_problem_verses.append((vn, web_issues))

    print(f"\nTotal verses analyzed: {total}")
    print()
    print(f"YLT clean alignments: {ylt_clean}/{total} ({100*ylt_clean/total:.0f}%)")
    print(f"WEB clean alignments: {web_clean}/{total} ({100*web_clean/total:.0f}%)")
    print()

    if web_clean != ylt_clean:
        better = "WEB" if web_clean > ylt_clean else "YLT"
        diff = abs(web_clean - ylt_clean)
        print(f"{better} aligns better by {diff} verse(s).")
    else:
        print("YLT and WEB align equally well.")

    print()
    print("--- YLT PROBLEM VERSES ---")
    for vn, issues in ylt_problem_verses:
        print(f"  4:{vn}: {'; '.join(issues)}")

    print()
    print("--- WEB PROBLEM VERSES ---")
    for vn, issues in web_problem_verses:
        print(f"  4:{vn}: {'; '.join(issues)}")

    # -----------------------------------------------------------------------
    # Detailed side-by-side for problem verses (show first 10)
    # -----------------------------------------------------------------------
    all_problem_vns = set()
    for vn, _ in ylt_problem_verses:
        all_problem_vns.add(vn)
    for vn, _ in web_problem_verses:
        all_problem_vns.add(vn)

    print()
    print("=" * 70)
    print("DETAILED VIEW OF PROBLEM VERSES (first 10)")
    print("=" * 70)

    shown = 0
    for vn in sorted(all_problem_vns):
        if shown >= 10:
            break
        shown += 1

        g_lines = greek_verses[vn]
        macula_words = macula_data.get((4, vn), [])
        num_lines = len(g_lines)
        macula_interlinear = build_macula_interlinear(macula_words, g_lines)

        macula_lines_text = defaultdict(list)
        for eng, line_idx in macula_interlinear:
            macula_lines_text[line_idx].append(eng)

        ylt_text = ylt_verses.get(vn, "")
        web_text = web_verses.get(vn, "")
        ylt_aligned = align_translation_to_lines(macula_interlinear, ylt_text, num_lines)
        web_aligned = align_translation_to_lines(macula_interlinear, web_text, num_lines)

        print(f"\n--- Mark 4:{vn} ---")
        for i in range(num_lines):
            mac = " ".join(macula_lines_text.get(i, []))
            print(f"  L{i+1} MAC: {mac}")
            print(f"  L{i+1} YLT: {ylt_aligned[i]}")
            print(f"  L{i+1} WEB: {web_aligned[i]}")
            print()

    # LCS match statistics
    print()
    print("=" * 70)
    print("LCS MATCH STATISTICS")
    print("=" * 70)

    for label, trans_verses in [("YLT", ylt_verses), ("WEB", web_verses)]:
        total_trans_words = 0
        total_matched = 0
        for vn in sorted(greek_verses.keys()):
            g_lines = greek_verses[vn]
            macula_words = macula_data.get((4, vn), [])
            num_lines = len(g_lines)
            if num_lines == 0:
                continue
            macula_interlinear = build_macula_interlinear(macula_words, g_lines)
            trans_text = trans_verses.get(vn, "")
            trans_words = trans_text.split()
            total_trans_words += len(trans_words)

            def strip_punct(w):
                return re.sub(r"[^a-zA-Z'-]", '', w).strip("'-")

            trans_clean = [strip_punct(w) for w in trans_words]
            macula_for_lcs = [(w, idx) for w, idx in macula_interlinear if strip_punct(w)]
            line_assignments = lcs_word_align(macula_for_lcs, trans_clean)

            # Count how many were directly matched (not forward/back-filled)
            # Re-run LCS just for counting
            m_words = [t[0].lower() for t in macula_for_lcs]
            t_words = [t.lower() for t in trans_clean]
            n = len(m_words)
            m_len = len(t_words)
            if n > 0 and m_len > 0:
                dp = [[0] * (m_len + 1) for _ in range(n + 1)]
                for i in range(1, n + 1):
                    for j in range(1, m_len + 1):
                        if _words_match(m_words[i - 1], t_words[j - 1]):
                            dp[i][j] = dp[i - 1][j - 1] + 1
                        else:
                            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                total_matched += dp[n][m_len]

        pct = 100 * total_matched / total_trans_words if total_trans_words else 0
        print(f"{label}: {total_matched}/{total_trans_words} words matched ({pct:.1f}%)")


if __name__ == "__main__":
    main()
