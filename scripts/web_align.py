#!/usr/bin/env python3
"""
web_align.py — Align WEB (World English Bible) text to GNT Reader
colometric line breaks using a double-wire approach.

Double-wire alignment:
  Hop 1: Greek → Macula English
    For each Greek word on each colometric line, collect its 'english'
    attribute from Macula XML. This produces a per-line interlinear that
    is perfectly aligned by construction.

  Hop 2: Macula English → WEB (English-to-English LCS)
    Run word-level LCS between Macula English tokens and WEB tokens using
    exact, stem, and synonym matching. Each matched WEB word inherits the
    line index of its Macula counterpart. Unmatched WEB words get the line
    of the NEXT matched word (forward bias). Trailing unmatched words get
    the PREVIOUS match's line.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/web_align.py                  # all books
    PYTHONIOENCODING=utf-8 py -3 scripts/web_align.py --book mark      # one book
    PYTHONIOENCODING=utf-8 py -3 scripts/web_align.py --test           # test on Mark 4
"""

import argparse
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
WEB_OUT_DIR = REPO / "data" / "text-files" / "web-colometric"
WEB_RAW_DIR = REPO / "research" / "web" / "raw"
LOWFAT_DIR = REPO / "research" / "macula-greek" / "SBLGNT" / "lowfat"

# ---------------------------------------------------------------------------
# Book number -> slug mapping (NT only, books 40-66)
# ---------------------------------------------------------------------------
BOOKNUM_TO_SLUG = {
    40: "matt", 41: "mark", 42: "luke", 43: "john", 44: "acts",
    45: "rom", 46: "1cor", 47: "2cor", 48: "gal", 49: "eph",
    50: "phil", 51: "col", 52: "1thess", 53: "2thess",
    54: "1tim", 55: "2tim", 56: "titus", 57: "phlm",
    58: "heb", 59: "jas", 60: "1pet", 61: "2pet",
    62: "1john", 63: "2john", 64: "3john", 65: "jude", 66: "rev",
}
SLUG_TO_BOOKNUM = {v: k for k, v in BOOKNUM_TO_SLUG.items()}

# Chapter counts per book (NT)
BOOK_CHAPTERS = {
    40: 28, 41: 16, 42: 24, 43: 21, 44: 28,
    45: 16, 46: 16, 47: 13, 48: 6, 49: 6,
    50: 4, 51: 4, 52: 5, 53: 3,
    54: 6, 55: 4, 56: 3, 57: 1,
    58: 13, 59: 5, 60: 5, 61: 3,
    62: 5, 63: 1, 64: 1, 65: 1, 66: 22,
}

# Macula book ID -> file mapping
SLUG_TO_MACULA = {
    "matt": "MAT", "mark": "MRK", "luke": "LUK", "john": "JHN",
    "acts": "ACT", "rom": "ROM", "1cor": "1CO", "2cor": "2CO",
    "gal": "GAL", "eph": "EPH", "phil": "PHP", "col": "COL",
    "1thess": "1TH", "2thess": "2TH", "1tim": "1TI", "2tim": "2TI",
    "titus": "TIT", "phlm": "PHM", "heb": "HEB", "jas": "JAS",
    "1pet": "1PE", "2pet": "2PE", "1john": "1JN", "2john": "2JN",
    "3john": "3JN", "jude": "JUD", "rev": "REV",
}

MACULA_TO_FILE = {
    "MAT": "01-matthew.xml", "MRK": "02-mark.xml",
    "LUK": "03-luke.xml", "JHN": "04-john.xml",
    "ACT": "05-acts.xml", "ROM": "06-romans.xml",
    "1CO": "07-1corinthians.xml", "2CO": "08-2corinthians.xml",
    "GAL": "09-galatians.xml", "EPH": "10-ephesians.xml",
    "PHP": "11-philippians.xml", "COL": "12-colossians.xml",
    "1TH": "13-1thessalonians.xml", "2TH": "14-2thessalonians.xml",
    "1TI": "15-1timothy.xml", "2TI": "16-2timothy.xml",
    "TIT": "17-titus.xml", "PHM": "18-philemon.xml",
    "HEB": "19-hebrews.xml", "JAS": "20-james.xml",
    "1PE": "21-1peter.xml", "2PE": "22-2peter.xml",
    "1JN": "23-1john.xml", "2JN": "24-2john.xml",
    "3JN": "25-3john.xml", "JUD": "26-jude.xml",
    "REV": "27-revelation.xml",
}

# ---------------------------------------------------------------------------
# Synonym sets — copied from ylt_align.py for matching Macula english to WEB
# ---------------------------------------------------------------------------
_SYNONYM_SETS = [
    ("listen", "hearken", "hear", "heard"),
    ("behold", "lo", "look", "see", "saw", "seen"),
    ("say", "said", "saying", "saith", "says"),
    ("go", "went", "gone", "goeth", "goes"),
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
    ("ask", "asked", "asketh", "request", "requested", "asks"),
    ("tell", "told", "telleth", "tells"),
    ("write", "wrote", "written", "writes"),
    ("begin", "began", "begun", "begins"),
    ("put", "placed", "set"),
    ("raise", "raised", "rose", "arise", "arose", "risen", "rise", "rising"),
    ("die", "died", "dead", "death", "dies", "dying"),
    ("kill", "killed", "slew", "slain", "slay", "slaughter"),
    ("eat", "ate", "eaten", "devour", "devoured", "eats"),
    ("drink", "drank", "drunk", "drinks"),
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
    ("brother", "brethren", "brothers"),
    ("lord", "master"),
    ("servant", "slave", "bondman"),
    ("nation", "nations", "gentile", "gentiles", "heathen"),
    ("draw", "draws", "approach", "approaching", "nigh"),
    ("suddenly", "straightway", "immediately"),
    ("shine", "shone", "shining", "flash", "flashed"),
    ("proceed", "proceeding", "traveled", "going", "journeying", "journey"),
    ("manifest", "manifested", "appeared"),
    ("righteous", "justified"),
    ("preach", "preached", "proclaimed"),
    ("believe", "believed", "believes"),
    ("receive", "received", "receives"),
    ("glory", "glorious"),
    ("godliness", "piety"),
    ("mystery", "secret"),
    ("angel", "angels", "messenger", "messengers"),
    ("sow", "sowed", "sowing", "sown", "sower"),
    ("spring", "sprang", "sprung"),
    ("bear", "bore", "bare", "born", "borne", "bearing", "bears"),
    ("bird", "birds", "fowl", "fowls"),
    ("way", "road", "path"),
    ("grow", "grew", "grown", "increase", "increased", "grows"),
    ("earth", "soil", "ground"),
    ("good", "beautiful", "fair"),
    ("hundred", "hundredfold"),
    ("thirty", "thirtyfold"),
    ("sixty", "sixtyfold"),
    ("run", "ran"),
    ("throw", "threw", "thrown", "cast"),
    ("break", "broke", "broken"),
    ("choose", "chose", "chosen"),
    ("hide", "hid", "hidden", "concealed"),
    ("wake", "woke", "woken", "awake", "awoke"),
    ("swear", "swore", "sworn"),
    ("tear", "tore", "torn"),
    ("shake", "shook", "shaken"),
    ("forgive", "forgave", "forgiven"),
    ("forbid", "forbade", "forbidden"),
    ("yield", "yielded", "yields"),
    ("choke", "choked", "chokes"),
    ("wither", "withered", "withers"),
    ("scorch", "scorched"),
    ("fruit", "fruits", "grain"),
    # WEB-specific additions (modern English forms)
    ("lamp", "light"),
    ("basket", "bushel"),
    ("bed", "couch"),
    ("measure", "measured"),
    ("parable", "parables"),
    ("kingdom", "reign"),
    ("sea", "lake"),
    ("boat", "ship"),
    ("crowd", "multitude"),
    ("rebuke", "rebuked", "rebukes"),
    ("calm", "still", "peace"),
    ("afraid", "fear", "feared", "fearful"),
    ("obey", "obeyed", "obeys"),
    ("cease", "ceased", "stop", "stopped"),
    ("sleep", "slept", "asleep", "sleeping"),
    ("sickle", "harvest"),
]

# Build lookup: word -> set of synonyms
_SYNONYM_MAP = {}
for syn_set in _SYNONYM_SETS:
    for word in syn_set:
        w = word.lower()
        if w not in _SYNONYM_MAP:
            _SYNONYM_MAP[w] = set()
        for other in syn_set:
            _SYNONYM_MAP[w].add(other.lower())


def _are_synonyms(a, b):
    """Check if two normalized words are synonyms."""
    if a in _SYNONYM_MAP and b in _SYNONYM_MAP[a]:
        return True
    if b in _SYNONYM_MAP and a in _SYNONYM_MAP[b]:
        return True
    return False


def _normalize(word):
    """Normalize an English word: lowercase, strip punctuation."""
    return re.sub(r'[^a-z0-9]', '', word.lower())


def _normalize_greek(word):
    """Normalize a Greek word for matching: strip punctuation, lowercase."""
    cleaned = re.sub(r'[.,;·\u0387\u00B7\u037E\'\"()\[\]!?—–\-]', '', word)
    return cleaned.strip().lower()


def _stem_english(word):
    """Simple English stemmer for alignment matching.

    Strips common suffixes to find a root form. Irregular forms need the
    synonym map.
    """
    w = word.lower()
    if len(w) <= 3:
        return w
    if w.endswith('ying') and len(w) > 5:
        return w[:-3]  # "denying" -> "deny" (approx)
    if w.endswith('ied') and len(w) > 4:
        return w[:-3] + 'y'  # "carried" -> "carry"
    if w.endswith('ies') and len(w) > 4:
        return w[:-3] + 'y'  # "carries" -> "carry"
    if w.endswith('ing') and len(w) > 5:
        base = w[:-3]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]  # "running" -> "run"
        return base  # "sowing" -> "sow"
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


# ---------------------------------------------------------------------------
# WEB data loading
# ---------------------------------------------------------------------------
def download_web_chapter(booknum, chapter):
    """Download a single WEB chapter from bolls.life API and cache it."""
    raw_path = WEB_RAW_DIR / f"{booknum}_{chapter}.json"
    if raw_path.exists():
        return json.loads(raw_path.read_text(encoding="utf-8"))

    WEB_RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = f"https://bolls.life/get-chapter/WEB/{booknum}/{chapter}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR downloading {url}: {e}", file=sys.stderr)
        return []

    raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def load_web_data(booknum):
    """Load all chapters for a book. Returns {chapter: {verse: text}}."""
    chapters = BOOK_CHAPTERS[booknum]
    book_data = {}
    for ch in range(1, chapters + 1):
        raw_path = WEB_RAW_DIR / f"{booknum}_{ch}.json"
        if raw_path.exists():
            verses_list = json.loads(raw_path.read_text(encoding="utf-8"))
        else:
            print(f"  Downloading WEB {BOOKNUM_TO_SLUG[booknum]} ch {ch}...")
            verses_list = download_web_chapter(booknum, ch)
            time.sleep(0.3)
        verse_dict = {}
        for v in verses_list:
            verse_dict[v["verse"]] = v["text"].strip()
        book_data[ch] = verse_dict
    return book_data


# ---------------------------------------------------------------------------
# Macula XML parsing (same as ylt_align.py)
# ---------------------------------------------------------------------------
_macula_cache = {}

_REF_RE = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_macula_ref(ref_str):
    """Parse 'ACT 1:1!8' -> (book, chapter, verse, word_pos)."""
    m = _REF_RE.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


def load_macula_book(slug):
    """Load Macula XML for a book, caching per book.

    Returns: {(chapter, verse): [(word_pos, greek_text, gloss, english), ...]}
    """
    if slug in _macula_cache:
        return _macula_cache[slug]

    macula_id = SLUG_TO_MACULA.get(slug)
    if not macula_id:
        _macula_cache[slug] = {}
        return {}

    filename = MACULA_TO_FILE.get(macula_id)
    if not filename:
        _macula_cache[slug] = {}
        return {}

    filepath = LOWFAT_DIR / filename
    if not filepath.exists():
        print(f"  WARNING: Macula file not found: {filepath}", file=sys.stderr)
        _macula_cache[slug] = {}
        return {}

    tree = ET.parse(str(filepath))
    root = tree.getroot()

    verse_words = defaultdict(list)
    for w in root.iter('w'):
        ref = w.get('ref', '')
        book, ch, vs, pos = _parse_macula_ref(ref)
        if ch is None:
            continue
        greek_text = w.get('normalized', '') or (w.text or '')
        gloss = w.get('gloss', '')
        english = w.get('english', '')
        verse_words[(ch, vs)].append((pos, greek_text, gloss, english))

    for key in verse_words:
        verse_words[key].sort(key=lambda x: x[0])

    result = dict(verse_words)
    _macula_cache[slug] = result
    return result


# ---------------------------------------------------------------------------
# Parse colometric Greek files (v4-editorial first, fallback to v3)
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
            if line.strip():
                current_lines.append(line)

    if current_verse is not None:
        while current_lines and not current_lines[-1].strip():
            current_lines.pop()
        verses[current_verse] = current_lines

    return verses


def find_greek_file(slug, ch_num):
    """Find the Greek colometric file for a chapter. Checks v4 first, then v3."""
    fname = f"{slug}-{ch_num:02d}.txt"
    v4_path = V4_DIR / fname
    if v4_path.exists():
        return v4_path
    v3_path = V3_DIR / fname
    if v3_path.exists():
        return v3_path
    return None


# ---------------------------------------------------------------------------
# Hop 1: Greek -> Macula English (build interlinear)
# ---------------------------------------------------------------------------
def build_macula_interlinear(greek_lines, macula_words):
    """For each Greek colometric line, collect Macula english tokens.

    Returns: [(english_token, line_idx), ...] in order — a flat sequence
    of Macula English words, each tagged with their Greek line index.
    Returns None if mapping fails.
    """
    if not greek_lines or not macula_words:
        return None

    # Build flat list of Greek words from colometric lines, tracking line index
    line_words = []  # [(normalized_greek, line_index), ...]
    for line_idx, line in enumerate(greek_lines):
        for w in line.split():
            norm = _normalize_greek(w)
            if norm:
                line_words.append((norm, line_idx))

    # Build normalized Macula words
    macula_norm = []
    for pos, greek_text, gloss, english in macula_words:
        norm = _normalize_greek(greek_text)
        macula_norm.append((norm, english))

    # Match Macula words to colometric line words via sequential alignment
    result = []
    col_idx = 0

    for m_norm, english in macula_norm:
        if not m_norm:
            current_line = line_words[min(col_idx, len(line_words) - 1)][1] if line_words else 0
            # Split english into tokens
            for tok in english.split():
                result.append((_normalize(tok), current_line))
            continue

        # Look ahead for a match
        best_match = None
        search_limit = min(col_idx + 8, len(line_words))
        for i in range(col_idx, search_limit):
            if line_words[i][0] == m_norm:
                best_match = i
                break

        if best_match is not None:
            line_idx = line_words[best_match][1]
            col_idx = best_match + 1
        else:
            # Try prefix match
            found = False
            for i in range(col_idx, search_limit):
                if line_words[i][0].startswith(m_norm) or m_norm.startswith(line_words[i][0]):
                    line_idx = line_words[i][1]
                    col_idx = i + 1
                    found = True
                    break
            if not found:
                line_idx = line_words[min(col_idx, len(line_words) - 1)][1] if line_words else 0

        # Split english attribute into individual tokens
        for tok in english.split():
            n = _normalize(tok)
            if n:
                result.append((n, line_idx))

    return result if result else None


# ---------------------------------------------------------------------------
# Hop 2: Macula English -> WEB (English-to-English LCS)
# ---------------------------------------------------------------------------
def _match_tokens(a, b):
    """Check if two normalized English tokens match (exact, stem, or synonym)."""
    if a == b:
        return True
    # Stem match
    sa = _stem_english(a)
    sb = _stem_english(b)
    if sa == sb and len(sa) >= 3:
        return True
    # Synonym match
    if _are_synonyms(a, b):
        return True
    if sa != a and _are_synonyms(sa, b):
        return True
    if sb != b and _are_synonyms(a, sb):
        return True
    return False


def lcs_align(macula_tokens, web_tokens):
    """LCS alignment between Macula English tokens and WEB tokens.

    macula_tokens: [(normalized_token, line_idx), ...]
    web_tokens: [normalized_token, ...]

    Returns: [line_idx, ...] for each web token (same length as web_tokens).
    Unmatched tokens get line of NEXT matched token (forward bias),
    trailing unmatched get PREVIOUS match's line.
    """
    m_len = len(macula_tokens)
    w_len = len(web_tokens)

    if m_len == 0 or w_len == 0:
        return [0] * w_len

    # Build LCS table (optimized: only need two rows)
    # But we need to traceback, so use full table approach
    # For performance with large verses, use a banded approach if needed
    # Most verses are small enough for O(m*n) to be fine

    # dp[i][j] = length of LCS of macula_tokens[:i] and web_tokens[:j]
    # Use rolling arrays for memory, but we need traceback, so store directions
    # Actually for traceback we need the full table. Let's cap and use sparse approach.

    # For very large verses, cap the search
    if m_len * w_len > 500000:
        # Fallback: greedy forward scan instead of full LCS
        return _greedy_align(macula_tokens, web_tokens)

    dp = [[0] * (w_len + 1) for _ in range(m_len + 1)]
    for i in range(1, m_len + 1):
        m_tok = macula_tokens[i - 1][0]
        for j in range(1, w_len + 1):
            w_tok = web_tokens[j - 1]
            if _match_tokens(m_tok, w_tok):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Traceback to find matched pairs
    matches = []  # [(macula_idx, web_idx), ...]
    i, j = m_len, w_len
    while i > 0 and j > 0:
        m_tok = macula_tokens[i - 1][0]
        w_tok = web_tokens[j - 1]
        if _match_tokens(m_tok, w_tok):
            matches.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    matches.reverse()

    # Assign line indices to WEB tokens
    return _assign_lines_from_matches(matches, macula_tokens, web_tokens)


def _greedy_align(macula_tokens, web_tokens):
    """Greedy forward-scan alignment fallback for very large verses."""
    matches = []
    m_ptr = 0
    for w_idx, w_tok in enumerate(web_tokens):
        # Search forward in macula tokens for a match
        search_limit = min(m_ptr + 15, len(macula_tokens))
        for m_idx in range(m_ptr, search_limit):
            if _match_tokens(macula_tokens[m_idx][0], w_tok):
                matches.append((m_idx, w_idx))
                m_ptr = m_idx + 1
                break
    return _assign_lines_from_matches(matches, macula_tokens, web_tokens)


def _assign_lines_from_matches(matches, macula_tokens, web_tokens):
    """Given LCS match pairs, assign line indices to all WEB tokens.

    Unmatched WEB words get line of NEXT matched word (forward bias).
    Trailing unmatched words get PREVIOUS match's line.
    """
    w_len = len(web_tokens)
    line_assignments = [None] * w_len

    # Set matched tokens
    for m_idx, w_idx in matches:
        line_assignments[w_idx] = macula_tokens[m_idx][1]

    # Forward bias: unmatched tokens get line of NEXT matched token
    # Walk backwards, propagating the next known line
    next_line = None
    for i in range(w_len - 1, -1, -1):
        if line_assignments[i] is not None:
            next_line = line_assignments[i]
        else:
            line_assignments[i] = next_line

    # Trailing unmatched (no next match): use previous match's line
    prev_line = 0
    for i in range(w_len):
        if line_assignments[i] is not None:
            prev_line = line_assignments[i]
        else:
            line_assignments[i] = prev_line

    return line_assignments


# ---------------------------------------------------------------------------
# Main double-wire split function
# ---------------------------------------------------------------------------
def split_web_by_double_wire(web_text, greek_lines, macula_words):
    """Split WEB text to match Greek colometric line breaks.

    Uses double-wire: Greek -> Macula English -> WEB.
    Returns list of WEB lines (same count as greek_lines), or None on failure.
    """
    num_lines = len(greek_lines)
    if num_lines <= 1:
        return [web_text.strip()]

    # Hop 1: Build Macula interlinear (Greek -> Macula English with line indices)
    macula_interlinear = build_macula_interlinear(greek_lines, macula_words)
    if not macula_interlinear:
        return None

    # Tokenize WEB text
    web_raw_tokens = re.findall(r'\S+', web_text)
    if not web_raw_tokens:
        return None

    web_norm_tokens = [_normalize(t) for t in web_raw_tokens]

    # Filter out empty macula tokens for LCS
    macula_filtered = [(tok, idx) for tok, idx in macula_interlinear if tok]

    if not macula_filtered:
        return None

    # Hop 2: LCS align Macula English -> WEB
    line_assignments = lcs_align(macula_filtered, web_norm_tokens)

    # Build WEB lines by cutting at line transitions
    result_lines = [[] for _ in range(num_lines)]
    for i, raw_token in enumerate(web_raw_tokens):
        line_idx = line_assignments[i] if i < len(line_assignments) else num_lines - 1
        # Clamp to valid range
        line_idx = max(0, min(line_idx, num_lines - 1))
        result_lines[line_idx].append(raw_token)

    result = [' '.join(words) for words in result_lines]

    # Cleanup: move dangling conjunctions/prepositions
    result = _cleanup_english_dangles(result)

    return result


def _cleanup_english_dangles(lines):
    """Move dangling English conjunctions/prepositions from line end to next line."""
    ENGLISH_DANGLES = {
        'and', 'but', 'for', 'or', 'nor', 'yet', 'so',
        'that', 'which', 'who', 'whom', 'whose', 'where', 'when',
        'if', 'though', 'although', 'because', 'since', 'while',
        'the', 'a', 'an', 'of', 'to', 'in', 'on', 'at', 'by',
        'with', 'from', 'into', 'upon', 'unto', 'through',
        'also',
    }
    if len(lines) < 2:
        return lines

    for i in range(len(lines) - 1):
        words = lines[i].split()
        if not words:
            continue
        dangle_count = 0
        for w in reversed(words):
            cleaned = w.rstrip('.,;:!?\u201c\u201d\u2018\u2019"\'').lower()
            if cleaned in ENGLISH_DANGLES:
                dangle_count += 1
            else:
                break
        if dangle_count > 0 and dangle_count < len(words):
            dangling_words = words[-dangle_count:]
            lines[i] = ' '.join(words[:-dangle_count])
            lines[i + 1] = ' '.join(dangling_words) + ' ' + lines[i + 1]

    return lines


# ---------------------------------------------------------------------------
# Clause-boundary fallback (simplified from ylt_align.py)
# ---------------------------------------------------------------------------
def split_text_into_n(text, n):
    """Split text into n lines using clause boundaries. Fallback method."""
    text = text.strip()
    if n <= 1:
        return [text]

    CLAUSE_WORDS = [
        "and ", "but ", "for ", "that ", "which ", "who ", "whom ",
        "if ", "when ", "where ", "while ", "since ", "because ",
        "so that ", "in order that ", "lest ", "unless ", "until ",
        "after ", "before ", "though ", "although ", "whether ",
        "nor ", "or ", "yet ", "then ", "therefore ", "also ",
    ]

    candidates = []
    for word in CLAUSE_WORDS:
        start = 1
        while True:
            idx = text.lower().find(word.lower(), start)
            if idx <= 0:
                break
            if idx > 0 and text[idx - 1] in " ,;:":
                candidates.append((idx, 1))
            start = idx + 1

    for punct in ["; ", ", ", "-- ", " -- "]:
        start = 1
        while True:
            idx = text.find(punct, start)
            if idx < 0:
                break
            split_pos = idx + len(punct)
            if split_pos < len(text):
                candidates.append((split_pos, 2))
            start = idx + 1

    # Deduplicate
    best = {}
    for pos, pri in candidates:
        if pos not in best or pri < best[pos]:
            best[pos] = pri
    candidates = sorted(best.items(), key=lambda x: x[0])

    if not candidates:
        words = text.split()
        if len(words) <= n:
            result = list(words)
            while len(result) < n:
                result.append("")
            return result
        per = len(words) / n
        result = []
        for i in range(n):
            s = round(per * i)
            e = round(per * (i + 1))
            result.append(" ".join(words[s:e]))
        return result

    # Pick best n-1 splits
    needed = n - 1
    if len(candidates) <= needed:
        splits = [pos for pos, pri in candidates]
    else:
        total_len = len(text)
        ideal_segment = total_len / (needed + 1)
        used = set()
        splits = []
        for i in range(1, needed + 1):
            target = ideal_segment * i
            best_pos = None
            best_dist = float("inf")
            for pos, pri in candidates:
                if pos in used:
                    continue
                dist = abs(pos - target)
                if dist < best_dist:
                    best_pos = pos
                    best_dist = dist
            if best_pos is not None:
                used.add(best_pos)
                splits.append(best_pos)
        splits.sort()

    # Apply splits
    segments = []
    prev = 0
    for pos in splits:
        seg = text[prev:pos].strip()
        if seg:
            segments.append(seg)
        prev = pos
    seg = text[prev:].strip()
    if seg:
        segments.append(seg)

    # Pad/merge
    while len(segments) < n:
        segments.append("")
    while len(segments) > n:
        segments[-2] = (segments[-2] + ' ' + segments[-1]).strip()
        segments.pop()

    return segments


# ---------------------------------------------------------------------------
# Book-level alignment
# ---------------------------------------------------------------------------
def align_book(slug, verbose=False):
    """Process all chapters for one book. Returns stats dict."""
    booknum = SLUG_TO_BOOKNUM[slug]
    web_data = load_web_data(booknum)
    macula_data = load_macula_book(slug)

    # Find all chapter files (v4 first, fallback v3)
    chapters = BOOK_CHAPTERS[booknum]
    chapter_files = []
    for ch in range(1, chapters + 1):
        gf = find_greek_file(slug, ch)
        if gf:
            chapter_files.append((ch, gf))

    if not chapter_files:
        print(f"  WARNING: No colometric files found for {slug}", file=sys.stderr)
        return {"total_verses": 0, "double_wire": 0, "clause_fallback": 0,
                "missing_web": 0, "v4_chapters": 0}

    WEB_OUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"total_verses": 0, "double_wire": 0, "clause_fallback": 0,
             "missing_web": 0, "v4_chapters": 0}

    for ch_num, greek_file in chapter_files:
        if "v4-editorial" in str(greek_file):
            stats["v4_chapters"] += 1

        greek_verses = parse_greek_chapter(greek_file)
        web_ch = web_data.get(ch_num, {})

        out_lines = []

        for verse_num in sorted(greek_verses.keys()):
            greek_lines = greek_verses[verse_num]
            web_text = web_ch.get(verse_num, "")

            stats["total_verses"] += 1

            if not web_text:
                stats["missing_web"] += 1
                out_lines.append(f"{ch_num}:{verse_num}")
                out_lines.append("[WEB text not available]")
                out_lines.append("")
                continue

            english_lines = None

            # Try double-wire alignment
            macula_words = macula_data.get((ch_num, verse_num), [])
            if macula_words:
                english_lines = split_web_by_double_wire(web_text, greek_lines, macula_words)

            if english_lines is not None:
                stats["double_wire"] += 1
            else:
                # Fallback to clause-boundary heuristic
                english_lines = split_text_into_n(web_text, len(greek_lines))
                stats["clause_fallback"] += 1

            # Ensure exact line count
            while len(english_lines) < len(greek_lines):
                english_lines.append("")
            if len(english_lines) > len(greek_lines):
                english_lines = english_lines[:len(greek_lines) - 1] + [
                    " ".join(english_lines[len(greek_lines) - 1:])
                ]

            # Write output
            out_lines.append(f"{ch_num}:{verse_num}")
            for el in english_lines:
                out_lines.append(el)
            out_lines.append("")

        # Write output file
        out_fname = f"{slug}-{ch_num:02d}.txt"
        out_path = WEB_OUT_DIR / out_fname
        out_path.write_text("\n".join(out_lines), encoding="utf-8")
        if verbose:
            print(f"  Wrote {out_path.name} ({len(greek_verses)} verses)")

    return stats


# ---------------------------------------------------------------------------
# Test: side-by-side comparison on Mark 4 selected verses
# ---------------------------------------------------------------------------
def run_tests():
    """Run Mark 4 test verses and print side-by-side comparison."""
    print("=" * 70)
    print("DOUBLE-WIRE ALIGNMENT TEST — Mark 4 selected verses")
    print("=" * 70)

    web_data = load_web_data(41)
    macula_data = load_macula_book("mark")

    test_verses = [1, 4, 9, 19, 21, 32, 38, 39]

    # Find the Greek file for Mark 4
    greek_file = find_greek_file("mark", 4)
    if not greek_file:
        print("ERROR: No colometric file found for Mark 4", file=sys.stderr)
        return
    print(f"Using Greek file: {greek_file}")
    print()

    greek_verses = parse_greek_chapter(greek_file)

    for v in test_verses:
        greek_lines = greek_verses.get(v, [])
        web_text = web_data.get(4, {}).get(v, "")

        if not greek_lines or not web_text:
            print(f"--- Mark 4:{v} — MISSING DATA ---")
            print()
            continue

        macula_words = macula_data.get((4, v), [])
        english_lines = split_web_by_double_wire(web_text, greek_lines, macula_words)

        method = "double-wire"
        if english_lines is None:
            english_lines = split_text_into_n(web_text, len(greek_lines))
            method = "clause-fallback"

        while len(english_lines) < len(greek_lines):
            english_lines.append("")
        if len(english_lines) > len(greek_lines):
            english_lines = english_lines[:len(greek_lines) - 1] + [
                " ".join(english_lines[len(greek_lines) - 1:])
            ]

        print(f"--- Mark 4:{v} ({len(greek_lines)} lines, {method}) ---")
        for i, (gl, el) in enumerate(zip(greek_lines, english_lines)):
            print(f"  GRK {i+1}: {gl}")
            print(f"  WEB {i+1}: {el}")
            print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Align WEB to GNT colometric line breaks (double-wire)")
    parser.add_argument("--book", type=str,
                        help="Process single book by slug (e.g. 'mark')")
    parser.add_argument("--test", action="store_true",
                        help="Run test cases on Mark 4")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    if args.book:
        slug = args.book.lower()
        if slug not in SLUG_TO_BOOKNUM:
            print(f"ERROR: Unknown book slug '{slug}'", file=sys.stderr)
            print(f"Valid slugs: {', '.join(sorted(SLUG_TO_BOOKNUM.keys()))}",
                  file=sys.stderr)
            sys.exit(1)
        slugs = [slug]
    else:
        slugs = [BOOKNUM_TO_SLUG[n] for n in sorted(BOOKNUM_TO_SLUG.keys())]

    grand_stats = {"total_verses": 0, "double_wire": 0, "clause_fallback": 0,
                   "missing_web": 0, "v4_chapters": 0}

    print("WEB Double-Wire Alignment")
    print()

    for slug in slugs:
        print(f"Processing {slug}...")
        stats = align_book(slug, verbose=args.verbose)
        for k in grand_stats:
            grand_stats[k] += stats[k]
        if stats["total_verses"] > 0:
            dw_pct = stats["double_wire"] / stats["total_verses"] * 100
            fb_pct = stats["clause_fallback"] / stats["total_verses"] * 100
            print(f"  {stats['total_verses']} verses: "
                  f"{stats['double_wire']} double-wire ({dw_pct:.1f}%), "
                  f"{stats['clause_fallback']} fallback ({fb_pct:.1f}%), "
                  f"{stats['missing_web']} missing WEB"
                  + (f", {stats['v4_chapters']} v4 chapters" if stats['v4_chapters'] else ""))

    print()
    print("=" * 60)
    print("GRAND TOTALS")
    print("=" * 60)
    total = grand_stats["total_verses"]
    if total > 0:
        dw_pct = grand_stats["double_wire"] / total * 100
        fb_pct = grand_stats["clause_fallback"] / total * 100
        print(f"Total verses:      {total}")
        print(f"Double-wire:       {grand_stats['double_wire']} ({dw_pct:.1f}%)")
        print(f"Clause fallback:   {grand_stats['clause_fallback']} ({fb_pct:.1f}%)")
        print(f"Missing WEB:       {grand_stats['missing_web']}")
        print(f"V4 chapters used:  {grand_stats['v4_chapters']}")


if __name__ == "__main__":
    main()
