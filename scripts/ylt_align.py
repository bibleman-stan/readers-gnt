#!/usr/bin/env python3
"""
ylt_align.py — Align YLT (Young's Literal Translation) text to GNT Reader
colometric line breaks.

Two alignment methods:
  --method gloss   (default) Uses Macula Greek word-level English glosses to
                   anchor alignment — each Greek colometric line's glosses are
                   fuzzy-matched against YLT words to find semantic split points.
  --method clause  Falls back to the original clause-boundary heuristic.

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py                     # all books, gloss
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --method clause     # all books, clause
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --book acts         # one book
    PYTHONIOENCODING=utf-8 py -3 scripts/ylt_align.py --test              # run test cases
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
V3_DIR = REPO / "data" / "text-files" / "v3-colometric"
YLT_OUT_DIR = REPO / "data" / "text-files" / "ylt-colometric"
YLT_RAW_DIR = REPO / "research" / "ylt" / "raw"
BOOKS_JSON = REPO / "research" / "ylt" / "books.json"
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
# YLT data download / cache
# ---------------------------------------------------------------------------
def download_chapter(booknum, chapter):
    """Download a single chapter from bolls.life API and cache it."""
    raw_path = YLT_RAW_DIR / f"{booknum}_{chapter}.json"
    if raw_path.exists():
        return json.loads(raw_path.read_text(encoding="utf-8"))

    YLT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = f"https://bolls.life/get-chapter/YLT/{booknum}/{chapter}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  ERROR downloading {url}: {e}", file=sys.stderr)
        return []

    raw_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def ensure_ylt_data(booknum):
    """Ensure all chapters for a book are downloaded. Returns dict {chapter: {verse: text}}."""
    chapters = BOOK_CHAPTERS[booknum]
    book_data = {}  # {chapter_int: {verse_int: text}}
    for ch in range(1, chapters + 1):
        raw_path = YLT_RAW_DIR / f"{booknum}_{ch}.json"
        if raw_path.exists():
            verses_list = json.loads(raw_path.read_text(encoding="utf-8"))
        else:
            print(f"  Downloading {BOOKNUM_TO_SLUG[booknum]} ch {ch}...")
            verses_list = download_chapter(booknum, ch)
            time.sleep(0.3)  # polite rate limit
        verse_dict = {}
        for v in verses_list:
            verse_dict[v["verse"]] = v["text"].strip()
        book_data[ch] = verse_dict
    return book_data


# ---------------------------------------------------------------------------
# Macula XML parsing with per-book cache
# ---------------------------------------------------------------------------
_macula_cache = {}  # slug -> {(chapter, verse): [(word_pos, greek_text, gloss, english), ...]}

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
    Words are sorted by word_pos within each verse.
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

    # Sort by word position within each verse
    for key in verse_words:
        verse_words[key].sort(key=lambda x: x[0])

    result = dict(verse_words)
    _macula_cache[slug] = result
    return result


# ---------------------------------------------------------------------------
# Parse v3-colometric Greek files
# ---------------------------------------------------------------------------
def parse_greek_chapter(filepath):
    """Parse a v3-colometric file. Returns {verse_num: [line1, line2, ...]}."""
    lines = Path(filepath).read_text(encoding="utf-8").splitlines()
    verses = {}
    current_verse = None
    current_lines = []

    verse_re = re.compile(r"^(\d+):(\d+)$")

    for line in lines:
        line = line.rstrip()
        m = verse_re.match(line)
        if m:
            # Save previous verse
            if current_verse is not None:
                # Strip trailing blank lines
                while current_lines and not current_lines[-1].strip():
                    current_lines.pop()
                verses[current_verse] = current_lines
            current_verse = int(m.group(2))
            current_lines = []
        elif current_verse is not None:
            if line.strip():  # skip blank lines within verse
                current_lines.append(line)

    # Save last verse
    if current_verse is not None:
        while current_lines and not current_lines[-1].strip():
            current_lines.pop()
        verses[current_verse] = current_lines

    return verses


# ---------------------------------------------------------------------------
# Gloss-based alignment
# ---------------------------------------------------------------------------

def _normalize(word):
    """Normalize an English word for fuzzy matching: lowercase, strip punctuation."""
    return re.sub(r'[^a-z0-9]', '', word.lower())


def _normalize_greek(word):
    """Normalize a Greek word for matching: strip punctuation marks, lowercase.

    Preserves Greek characters (accents, breathing marks, etc.) but removes
    sentence-ending punctuation like periods, commas, semicolons, middle dots.
    """
    # Strip common punctuation that appears in colometric text
    cleaned = re.sub(r'[.,;·\u0387\u00B7\u037E\'\"()\[\]!?—–\-]', '', word)
    return cleaned.strip().lower()


def _gloss_to_tokens(gloss_str):
    """Split a gloss string like '[The] beginning' into normalized tokens.

    Strips bracketed content markers like [one], [-], etc. but keeps
    meaningful bracketed words.
    """
    # Remove bracketed placeholders like [-], [one], [The]
    # But split multi-word glosses into individual tokens
    tokens = []
    for part in gloss_str.split():
        # Strip brackets: [The] -> The, [them] -> them
        cleaned = re.sub(r'[\[\]]', '', part)
        cleaned = cleaned.strip()
        if cleaned and cleaned != '-':
            tokens.append(_normalize(cleaned))
    return tokens


def _build_word_line_map(greek_lines, macula_words):
    """Map each Macula word to a colometric line index.

    Args:
        greek_lines: list of Greek colometric line strings
        macula_words: list of (word_pos, greek_text, gloss, english) for the verse

    Returns:
        list of (line_index, gloss, english) for each Macula word in order,
        or None if mapping fails.
    """
    if not greek_lines or not macula_words:
        return None

    # Build a flat list of Greek words from colometric lines, tracking line index
    line_words = []  # [(normalized_greek, line_index), ...]
    for line_idx, line in enumerate(greek_lines):
        words_in_line = line.split()
        for w in words_in_line:
            norm = _normalize_greek(w)
            if norm:  # skip empty after normalization
                line_words.append((norm, line_idx))

    # Build normalized Macula words
    macula_norm = []
    for pos, greek_text, gloss, english in macula_words:
        norm = _normalize_greek(greek_text)
        macula_norm.append((norm, gloss, english))

    # Match Macula words to colometric line words using sequence alignment.
    # The Macula word order should match the colometric word order.
    # We walk through both sequences, matching normalized Greek forms.
    result = []
    col_idx = 0  # pointer into line_words

    for m_norm, gloss, english in macula_norm:
        if not m_norm:
            # Empty normalized form — assign to current line context
            current_line = line_words[min(col_idx, len(line_words) - 1)][1] if line_words else 0
            result.append((current_line, gloss, english))
            continue

        # Look ahead in line_words for a match (allow some skipping for
        # punctuation differences etc.)
        best_match = None
        search_limit = min(col_idx + 8, len(line_words))
        for i in range(col_idx, search_limit):
            if line_words[i][0] == m_norm:
                best_match = i
                break

        if best_match is not None:
            result.append((line_words[best_match][1], gloss, english))
            col_idx = best_match + 1
        else:
            # No exact match found — try partial match (prefix)
            found = False
            for i in range(col_idx, search_limit):
                if line_words[i][0].startswith(m_norm) or m_norm.startswith(line_words[i][0]):
                    result.append((line_words[i][1], gloss, english))
                    col_idx = i + 1
                    found = True
                    break
            if not found:
                # Assign to current line context
                current_line = line_words[min(col_idx, len(line_words) - 1)][1] if line_words else 0
                result.append((current_line, gloss, english))

    return result


# ---------------------------------------------------------------------------
# Synonym sets for matching Macula glosses to YLT vocabulary.
# Each tuple is a set of words treated as equivalent for alignment.
# ---------------------------------------------------------------------------
_SYNONYM_SETS = [
    ("listen", "hearken", "hear", "heard"),
    ("behold", "lo", "look", "see", "saw", "seen"),
    ("say", "said", "saying", "saith"),
    ("go", "went", "gone", "goeth"),
    ("come", "came", "cometh"),
    ("make", "made", "maketh"),
    ("give", "gave", "giveth", "given"),
    ("take", "took", "taketh", "taken"),
    ("know", "knew", "knoweth", "known"),
    ("send", "sent", "sendeth"),
    ("do", "did", "doeth", "done"),
    ("speak", "spoke", "spake", "speaketh", "spoken"),
    ("call", "called", "calleth"),
    ("answer", "answered", "answereth"),
    ("ask", "asked", "asketh", "request", "requested"),
    ("tell", "told", "telleth"),
    ("write", "wrote", "written"),
    ("begin", "began", "begun"),
    ("put", "placed", "set"),
    ("raise", "raised", "rose", "arise", "arose", "risen", "rise", "rising"),
    ("die", "died", "dead", "death"),
    ("kill", "killed", "slew", "slain", "slay", "slaughter"),
    ("eat", "ate", "eaten", "devour", "devoured"),
    ("drink", "drank", "drunk"),
    ("sit", "sat", "sitteth"),
    ("stand", "stood", "standeth"),
    ("fall", "fell", "fallen"),
    ("find", "found"),
    ("leave", "left"),
    ("bring", "brought", "bringeth"),
    ("think", "thought"),
    ("teach", "taught"),
    ("seek", "sought"),
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
    ("draw", "draws", "approach", "approaching", "nigh"),
    ("suddenly", "straightway", "immediately"),
    ("shine", "shone", "shining", "flash", "flashed"),
    ("proceed", "proceeding", "traveled", "going", "journeying", "journey"),
    ("manifest", "manifested", "appeared"),
    ("righteous", "justified"),
    ("preach", "preached", "proclaimed"),
    ("believe", "believed"),
    ("receive", "received"),
    ("glory", "glorious"),
    ("godliness", "piety"),
    ("mystery", "secret"),
    ("angel", "angels", "messenger", "messengers"),
    # New entries for broader coverage:
    ("sow", "sowed", "sowing", "sown", "sower"),
    ("spring", "sprang", "sprung"),
    ("bear", "bore", "bare", "born", "borne", "bearing"),
    ("bird", "birds", "fowl", "fowls"),
    ("way", "road", "path"),
    ("grow", "grew", "grown", "increase", "increased"),
    ("earth", "soil"),
    ("good", "beautiful", "fair"),
    ("hundred", "hundredfold"),
    ("thirty", "thirtyfold"),
    ("sixty", "sixtyfold"),
    ("run", "ran"),
    ("throw", "threw", "thrown", "cast"),
    ("break", "broke", "broken"),
    ("choose", "chose", "chosen"),
    ("hide", "hid", "hidden", "secret", "concealed"),
    ("wake", "woke", "woken", "awake", "awoke"),
    ("swear", "swore", "sworn"),
    ("tear", "tore", "torn"),
    ("shake", "shook", "shaken"),
    ("forgive", "forgave", "forgiven"),
    ("forbid", "forbade", "forbidden"),
    ("yield", "yielded"),
    ("choke", "choked"),
    ("wither", "withered"),
    ("scorch", "scorched"),
    ("fruit", "fruits", "grain"),
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


def _are_synonyms(g, y):
    """Check if two normalized words are synonyms."""
    if g in _SYNONYM_MAP and y in _SYNONYM_MAP[g]:
        return True
    if y in _SYNONYM_MAP and g in _SYNONYM_MAP[y]:
        return True
    return False


# Stop words for alignment — too common/ambiguous to be reliable anchors.
_ALIGNMENT_STOP_WORDS = frozenset({
    'the', 'a', 'an', 'of', 'in', 'to', 'and', 'or', 'but', 'for',
    'on', 'by', 'at', 'no', 'it', 'he', 'she', 'they',
    'his', 'her', 'its', 'their', 'him', 'them', 'this', 'that',
    'is', 'was', 'are', 'were', 'be', 'been', 'with', 'from',
    'as', 'so', 'do', 'did', 'does', 'has', 'had', 'have', 'having',
    'may', 'might', 'shall', 'should', 'will', 'would',
    'can', 'could', 'nor', 'yet', 'if', 'then', 'than',
    'own',
    # Relative/interrogative pronouns — too common as function words to anchor
    'who', 'whom', 'whose', 'which', 'what', 'where', 'when', 'how',
    # Demonstratives and existentials that gloss Greek articles/particles
    'these', 'those', 'there', 'here',
    # "thing/things" glosses Greek articles and creates false substring matches
    'thing', 'things',
})
# Note: 'not' and 'also' removed from stop words — they are semantically
# significant at line boundaries (negation clauses, additive markers) and
# their glosses serve as important anchors for alignment.


def _stem_english(word):
    """Simple English stemmer for alignment matching.

    Strips common suffixes to find a root form. Only handles regular
    morphology — irregular forms (rose/risen, bore/bare) need the
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
        return w[:-3]  # "giveth" -> "giv"
    if w.endswith('est') and len(w) > 5:
        return w[:-3]
    if w.endswith('ed') and len(w) > 4:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]  # "scorched" doesn't double, but "stopped" -> "stop"
        return base  # "scorched" -> "scorch", "sowed" -> "sow"
    if w.endswith('en') and len(w) > 4 and not w.endswith('men') and not w.endswith('ten'):
        return w[:-2]  # "spoken" -> "spok"
    if w.endswith('er') and len(w) > 4:
        base = w[:-2]
        if len(base) > 2 and base[-1] == base[-2]:
            return base[:-1]
        return base  # "sower" -> "sow"
    if w.endswith('s') and len(w) > 3 and not w.endswith('ss') and not w.endswith('us'):
        return w[:-1]  # "thorns" -> "thorn"
    return w


def _content_matches(ylt_normalized, anchor_tokens):
    """Check if a normalized YLT word matches any token in an anchor set.

    Uses exact match, stem match, synonym lookup, and substring containment.
    Stricter than fuzzy matching — no prefix shortcuts that create false
    positives like 'he' matching 'heaven'.
    """
    yn = ylt_normalized
    yn_stem = _stem_english(yn)

    for t in anchor_tokens:
        # Exact match
        if yn == t:
            return True
        # Stem match (both sides stemmed)
        t_stem = _stem_english(t)
        if yn_stem == t_stem and len(yn_stem) >= 3:
            return True
        # Synonym (original forms)
        if _are_synonyms(yn, t):
            return True
        # Synonym (stemmed forms)
        if yn_stem != yn and _are_synonyms(yn_stem, t):
            return True
        if t_stem != t and _are_synonyms(yn, t_stem):
            return True
        # Substring: "thirtyfold" contains "thirty" (handles hyphenated compounds)
        # Require minimum length 6 to avoid false positives like "thing" in "anything"
        if len(t) >= 6 and t in yn:
            return True
        if len(yn) >= 6 and yn in t:
            return True

    return False


def _tokenize_ylt(text):
    """Tokenize YLT text into (word, start_char, end_char) tuples.

    Preserves whitespace boundaries for reconstruction.
    """
    tokens = []
    for m in re.finditer(r'\S+', text):
        tokens.append((m.group(), m.start(), m.end()))
    return tokens


def _find_gap_split(ylt_tokens, prev_pos, next_pos):
    """Find the best split point in a gap between two matched anchors.

    Returns the ylt_token index where the new line should START.
    Prefers: clause-starting conjunctions > punctuation boundaries > midpoint.
    """
    if next_pos <= prev_pos + 1:
        return next_pos

    CLAUSE_STARTERS = {'and', 'but', 'for', 'or', 'nor', 'yet', 'so', 'then',
                       'therefore', 'because', 'since', 'that', 'which', 'who',
                       'whom', 'where', 'when', 'if', 'though', 'although',
                       'lest', 'unless', 'until', 'after', 'before', 'while'}

    # Look for clause-starting word in the gap — prefer the one closest to
    # the gap midpoint.  When multiple clause starters exist (e.g. "then" and
    # "that"), the first one is often a parenthetical while the last one marks
    # the real clause boundary (e.g. ὅτι → "that").  Midpoint preference
    # balances both directions.
    gap_mid = (prev_pos + next_pos) / 2
    best_clause_pos = None
    best_clause_dist = float("inf")
    for pos in range(prev_pos + 1, next_pos):
        word = _normalize(ylt_tokens[pos][0])
        if word in CLAUSE_STARTERS:
            dist = abs(pos - gap_mid)
            if dist <= best_clause_dist:
                best_clause_pos = pos
                best_clause_dist = dist
    if best_clause_pos is not None:
        return best_clause_pos

    # Look for punctuation boundary on word before a gap position (split BEFORE)
    for pos in range(prev_pos + 1, next_pos):
        prev_raw = ylt_tokens[pos - 1][0] if pos > 0 else ''
        if prev_raw and prev_raw[-1] in '.,;:!?':
            return pos

    # Look for punctuation on gap words themselves (split AFTER the punctuated word)
    for pos in range(prev_pos + 1, next_pos):
        raw = ylt_tokens[pos][0]
        if raw and raw[-1] in '.,;:!?':
            if pos + 1 <= next_pos:
                return pos + 1

    # Midpoint fallback
    return (prev_pos + next_pos + 1) // 2


def split_ylt_by_glosses(ylt_text, greek_lines, macula_words):
    """Split YLT text using sequential forward-scan alignment.

    The Greek colometric breaks are the source of truth. Each Macula word
    is mapped to its colometric line, and its English gloss provides a
    bridge to the YLT text. We walk YLT content words left-to-right,
    matching them against the ordered sequence of Macula glosses. Where
    the matched glosses transition from line K to line K+1, we place the
    English split.

    This approach:
    - Preserves word-position information (no bag-of-words pooling)
    - Uses sequential matching (no false anchors from repeated words)
    - Automatically re-pegs when Greek breaks change
    - Handles Greek/English word-order divergence gracefully

    Returns list of English lines (same count as greek_lines), or None
    if alignment fails and caller should fall back to clause heuristic.
    """
    num_lines = len(greek_lines)
    if num_lines <= 1:
        return [ylt_text.strip()]

    # Step 1: Map each Macula word to its colometric line index
    word_line_map = _build_word_line_map(greek_lines, macula_words)
    if not word_line_map:
        return None

    # Step 2: Build ordered content-anchor sequence from Macula word order.
    # Each anchor: (line_idx, set of matchable tokens) for one Greek content word.
    anchors = []
    for line_idx, gloss, english in word_line_map:
        tokens = set()
        for t in _gloss_to_tokens(gloss) + _gloss_to_tokens(english):
            tn = _normalize(t)
            if tn and len(tn) >= 3 and tn not in _ALIGNMENT_STOP_WORDS:
                tokens.add(tn)
                stemmed = _stem_english(tn)
                if stemmed and len(stemmed) >= 3:
                    tokens.add(stemmed)
        if tokens:
            anchors.append((line_idx, tokens))

    # Step 2b: Detect lines with zero anchors (all glosses are stop words).
    # For those lines, promote their stop-word glosses to anchors AND mark
    # them so the forward scan will try matching stop-word YLT tokens too.
    # Without this, lines like "Τίς ἄρα οὗτός ἐστιν" (glosses: who/then/
    # this/is — all stop words) produce no anchors and get merged.
    anchor_lines = {a[0] for a in anchors}
    stopword_anchor_lines = set()
    for line_idx in range(num_lines):
        if line_idx in anchor_lines:
            continue
        # This line has no anchors — promote its stop-word glosses
        for wlm_line_idx, gloss, english in word_line_map:
            if wlm_line_idx != line_idx:
                continue
            tokens = set()
            for t in _gloss_to_tokens(gloss) + _gloss_to_tokens(english):
                tn = _normalize(t)
                if tn and len(tn) >= 3:  # allow stop words
                    tokens.add(tn)
            if tokens:
                anchors.append((line_idx, tokens))
                stopword_anchor_lines.add(line_idx)
        anchor_lines.add(line_idx)

    # Re-sort anchors to maintain line order for the forward scan.
    anchors.sort(key=lambda a: a[0])

    if not anchors:
        return None

    # Step 3: Tokenize YLT
    ylt_tokens = _tokenize_ylt(ylt_text)
    if not ylt_tokens:
        return None

    # Step 4: Forward scan — match YLT content words to Macula anchors in order.
    # Walk both sequences left-to-right. When a YLT content word matches the
    # current anchor, record the match and advance the anchor pointer.
    #
    # Word-order swap handling: Greek and English sometimes order words
    # differently within the same line (e.g., Greek γῆν πολλήν = "earth much"
    # but YLT says "much earth"). When the forward scan would jump to a new
    # line, we first check if a recently skipped anchor on the SAME line as
    # the last match would also match. If so, prefer the same-line match
    # (it's a within-line word-order swap, not a real line transition).
    ylt_matches = []  # [(ylt_word_idx, line_idx), ...]
    anchor_ptr = 0
    consumed_anchors = set()  # Track which anchor indices have been matched

    for yi, (word, _, _) in enumerate(ylt_tokens):
        yn = _normalize(word)
        is_stop = not yn or len(yn) < 3 or yn in _ALIGNMENT_STOP_WORDS

        # For normal content words, always try to match.
        # For stop words, only try if the next unmatched anchor belongs to a
        # promoted stop-word line — otherwise skip to avoid false positives.
        if is_stop:
            # Check if any upcoming anchor is on a stop-word-only line
            has_promoted = False
            for ai in range(anchor_ptr, min(anchor_ptr + 4, len(anchors))):
                if anchors[ai][0] in stopword_anchor_lines:
                    has_promoted = True
                    break
            if not has_promoted:
                continue

        # Try to match against upcoming anchors (limited lookahead)
        forward_match = None  # (anchor_index, line_idx)
        limit = min(anchor_ptr + 8, len(anchors))
        for ai in range(anchor_ptr, limit):
            line_idx, tokens = anchors[ai]
            if _content_matches(yn, tokens):
                forward_match = (ai, line_idx)
                break

        if forward_match is not None:
            fwd_ai, fwd_line = forward_match
            last_line = ylt_matches[-1][1] if ylt_matches else 0

            # If forward match jumps to a new line, check if a skipped anchor
            # on the SAME line as the last match also matches this word.
            # This catches within-line word-order swaps.
            # Only consider anchors that haven't already been consumed by a
            # different YLT word — otherwise repeated glosses (e.g., "one"
            # appearing on both lines) cause false same-line matches.
            if fwd_line != last_line and ylt_matches:
                same_line_match = False
                for ai in range(max(0, anchor_ptr - 6), anchor_ptr):
                    if ai in consumed_anchors:
                        continue  # Already matched to a different YLT word
                    skip_line, skip_tokens = anchors[ai]
                    if skip_line == last_line and _content_matches(yn, skip_tokens):
                        ylt_matches.append((yi, skip_line))
                        consumed_anchors.add(ai)
                        same_line_match = True
                        break
                if not same_line_match:
                    ylt_matches.append((yi, fwd_line))
                    consumed_anchors.add(fwd_ai)
                    anchor_ptr = fwd_ai + 1
            else:
                ylt_matches.append((yi, fwd_line))
                consumed_anchors.add(fwd_ai)
                anchor_ptr = fwd_ai + 1
        else:
            # No forward match — check recently skipped anchors on same line
            if ylt_matches:
                last_line = ylt_matches[-1][1]
                for ai in range(max(0, anchor_ptr - 6), anchor_ptr):
                    if ai in consumed_anchors:
                        continue  # Already matched to a different YLT word
                    skip_line, skip_tokens = anchors[ai]
                    if skip_line == last_line and _content_matches(yn, skip_tokens):
                        ylt_matches.append((yi, last_line))
                        consumed_anchors.add(ai)
                        break

    if not ylt_matches:
        return None

    # Step 5: Find line transitions — where consecutive matches jump to a new line
    boundaries = []  # [(last_pos_on_prev_line, first_pos_on_next_line), ...]
    for mi in range(1, len(ylt_matches)):
        prev_pos, prev_line = ylt_matches[mi - 1]
        curr_pos, curr_line = ylt_matches[mi]
        if curr_line > prev_line:
            boundaries.append((prev_pos, curr_pos))

    # Step 6: Find best split point in each gap between boundary anchors
    split_positions = []
    for prev_pos, next_pos in boundaries:
        split_positions.append(_find_gap_split(ylt_tokens, prev_pos, next_pos))

    # Step 7: Build lines from split positions
    cuts = sorted(set([0] + split_positions + [len(ylt_tokens)]))

    result = []
    for i in range(len(cuts) - 1):
        words = [ylt_tokens[j][0] for j in range(cuts[i], cuts[i + 1])]
        result.append(' '.join(words))

    # Step 8: Pad or merge to match exact line count
    while len(result) < num_lines:
        # Split the longest line at a clause boundary
        longest_idx = max(range(len(result)), key=lambda i: len(result[i]))
        parts = split_text_into_n(result[longest_idx], 2)
        if len(parts) == 2 and parts[0] and parts[1]:
            result = result[:longest_idx] + parts + result[longest_idx + 1:]
        else:
            result.append('')
            break
    while len(result) > num_lines:
        # Merge shortest adjacent pair
        best_idx = min(range(len(result) - 1),
                       key=lambda i: len(result[i]) + len(result[i + 1]))
        result[best_idx] = (result[best_idx] + ' ' + result[best_idx + 1]).strip()
        result.pop(best_idx + 1)

    # Step 9: Cleanup
    result = cleanup_english_dangles(result)
    result = cleanup_ylt_fragments(result, num_lines, greek_lines)

    return result


def cleanup_english_dangles(lines):
    """Move dangling English conjunctions/prepositions from line end to next line start.

    Same principle as the Greek dangling function word fix: 'and', 'but', 'for',
    'or', 'that', 'which', 'who', 'whom', etc. should never end a line.

    Handles multi-word trailing clusters: if a line ends with consecutive
    function words (e.g., "and one", "not that"), move the entire cluster
    to the next line. This catches cases where a conjunction + short word
    pair belongs with the following clause.
    """
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
        # Count how many trailing words are all function words
        # (walk backwards from end of line)
        dangle_count = 0
        for w in reversed(words):
            cleaned = w.rstrip('.,;:!?').lower()
            if cleaned in ENGLISH_DANGLES:
                dangle_count += 1
            else:
                break
        # Move the trailing cluster if: at least one dangling word,
        # and we'd leave at least one content word on this line
        if dangle_count > 0 and dangle_count < len(words):
            dangling_words = words[-dangle_count:]
            lines[i] = ' '.join(words[:-dangle_count])
            lines[i + 1] = ' '.join(dangling_words) + ' ' + lines[i + 1]

    return lines


def cleanup_ylt_fragments(lines, target_count, greek_lines=None):
    """Merge fragment lines (1-2 words) into their neighbors.

    The gloss alignment can create tiny fragments when short words get
    assigned to their own line. A 1-2 word English line is almost never
    a valid sense-line — UNLESS the corresponding Greek line is also
    short (1-2 words), meaning the alignment intentionally made it brief.

    When merging, DON'T try to restore line count by splitting the longest
    line at midpoint (that creates new fragments). Instead, just merge and
    accept the line count difference. The build_books.py handles mismatched
    line counts gracefully (empty .en spans for extra Greek lines).
    """
    if len(lines) <= 1:
        return lines

    MAX_ITERATIONS = 10
    for _ in range(MAX_ITERATIONS):
        fragment_idx = None
        for i, line in enumerate(lines):
            word_count = len(line.split()) if line.strip() else 0
            if 0 < word_count <= 1 and len(lines) > 1:
                # Only merge if the corresponding Greek line is NOT also short
                if greek_lines and i < len(greek_lines):
                    gk_words = len(greek_lines[i].split()) if greek_lines[i].strip() else 0
                    if gk_words <= 2:
                        continue  # Greek line is also short — intentional
                fragment_idx = i
                break

        if fragment_idx is None:
            break

        idx = fragment_idx
        if idx + 1 < len(lines):
            lines[idx + 1] = (lines[idx] + ' ' + lines[idx + 1]).strip()
            lines.pop(idx)
        elif idx > 0:
            lines[idx - 1] = (lines[idx - 1] + ' ' + lines[idx]).strip()
            lines.pop(idx)
        else:
            break

    # Final line count enforcement — re-split longest or merge to match target
    while len(lines) < target_count:
        # Instead of padding with empty lines, try to split the longest line
        longest_idx = max(range(len(lines)), key=lambda i: len(lines[i]))
        parts = split_text_into_n(lines[longest_idx], 2)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            lines = lines[:longest_idx] + parts + lines[longest_idx + 1:]
        else:
            lines.append('')
            break
    while len(lines) > target_count:
        lines[-2] = (lines[-2] + ' ' + lines[-1]).strip()
        lines.pop()

    return lines


# ---------------------------------------------------------------------------
# English text splitting (clause-boundary heuristic — original method)
# ---------------------------------------------------------------------------

# Clause-introducing words that correspond to Greek conjunctions/subordinators.
# These are preferred split points. We split BEFORE these words.
CLAUSE_WORDS = [
    "and ", "but ", "for ", "that ", "which ", "who ", "whom ",
    "if ", "when ", "where ", "while ", "since ", "because ",
    "so that ", "in order that ", "lest ", "unless ", "until ",
    "after ", "before ", "though ", "although ", "whether ",
    "nor ", "or ", "yet ", "then ", "therefore ", "also ",
    "saying, ", "saying ",
]

# Punctuation that marks natural clause boundaries
PUNCT_SPLITS = ["; ", ", ", "-- ", " -- "]


def find_split_candidates(text):
    """Find all candidate split positions in text.

    Returns list of (position, priority) tuples.
    position = char index where the new line would START.
    priority = lower is better (clause words > punctuation > midpoint).
    """
    candidates = []

    # Priority 1: clause-introducing words (split before the word)
    for word in CLAUSE_WORDS:
        # Find all occurrences, but not at the very start
        start = 1
        while True:
            idx = text.lower().find(word.lower(), start)
            if idx <= 0:
                break
            # Only split if preceded by space or punctuation
            if idx > 0 and text[idx - 1] in " ,;:":
                # The split point is at idx (start of clause word)
                candidates.append((idx, 1))
            start = idx + 1

    # Priority 2: semicolons and commas
    for punct in PUNCT_SPLITS:
        start = 1
        while True:
            idx = text.find(punct, start)
            if idx < 0:
                break
            split_pos = idx + len(punct)
            if split_pos < len(text):
                candidates.append((split_pos, 2))
            start = idx + 1

    # Deduplicate by position, keeping best priority
    best = {}
    for pos, pri in candidates:
        if pos not in best or pri < best[pos]:
            best[pos] = pri
    return sorted(best.items(), key=lambda x: x[0])


def split_text_into_n(text, n):
    """Split text into exactly n lines, using clause boundaries when possible.

    Returns list of n strings.
    """
    text = text.strip()
    if n <= 1:
        return [text]

    candidates = find_split_candidates(text)
    if not candidates:
        # No natural breaks at all — split evenly by word
        return _split_evenly_by_words(text, n)

    # We need n-1 split points.
    # Strategy: pick the best n-1 splits from candidates.
    # "Best" = good priority + even distribution.
    splits = _pick_best_splits(text, candidates, n - 1)

    if len(splits) < n - 1:
        # Not enough natural breaks. Use what we have, then subdivide
        # the longest segments.
        segments = _apply_splits(text, splits)
        while len(segments) < n:
            segments = _subdivide_longest(segments)
        return segments

    return _apply_splits(text, splits)


def _pick_best_splits(text, candidates, needed):
    """Pick `needed` split points from candidates that distribute text evenly."""
    if len(candidates) <= needed:
        return [pos for pos, pri in candidates]

    total_len = len(text)
    ideal_segment = total_len / (needed + 1)

    # Greedy: for each target position, pick the nearest candidate
    used = set()
    result = []
    for i in range(1, needed + 1):
        target = ideal_segment * i
        best_pos = None
        best_dist = float("inf")
        best_pri = float("inf")
        for pos, pri in candidates:
            if pos in used:
                continue
            dist = abs(pos - target)
            # Prefer closer to target, break ties by priority
            if dist < best_dist or (dist == best_dist and pri < best_pri):
                best_pos = pos
                best_dist = dist
                best_pri = pri
        if best_pos is not None:
            used.add(best_pos)
            result.append(best_pos)

    result.sort()
    return result


def _apply_splits(text, split_positions):
    """Apply split positions to produce segments."""
    segments = []
    prev = 0
    for pos in sorted(split_positions):
        seg = text[prev:pos].strip()
        if seg:
            segments.append(seg)
        prev = pos
    # Last segment
    seg = text[prev:].strip()
    if seg:
        segments.append(seg)
    return segments


def _subdivide_longest(segments):
    """Split the longest segment at its midpoint (by words)."""
    if not segments:
        return segments

    # Find longest segment
    idx = max(range(len(segments)), key=lambda i: len(segments[i]))
    seg = segments[idx]

    # Try to find a natural break in this segment
    candidates = find_split_candidates(seg)
    if candidates:
        # Pick the one closest to midpoint
        mid = len(seg) / 2
        best_pos = min(candidates, key=lambda x: abs(x[0] - mid))[0]
        left = seg[:best_pos].strip()
        right = seg[best_pos:].strip()
    else:
        # Split at word boundary nearest midpoint
        words = seg.split()
        if len(words) < 2:
            return segments  # Can't split single word
        mid_idx = len(words) // 2
        left = " ".join(words[:mid_idx])
        right = " ".join(words[mid_idx:])

    if left and right:
        return segments[:idx] + [left, right] + segments[idx + 1:]
    return segments


def _split_evenly_by_words(text, n):
    """Split text into n roughly equal parts by word count."""
    words = text.split()
    if len(words) <= n:
        # More lines than words — some lines will be single words
        result = []
        for w in words:
            result.append(w)
        while len(result) < n:
            result.append("")
        return result

    per = len(words) / n
    result = []
    for i in range(n):
        start = round(per * i)
        end = round(per * (i + 1))
        result.append(" ".join(words[start:end]))
    return result


# ---------------------------------------------------------------------------
# Main alignment logic
# ---------------------------------------------------------------------------
def align_book(slug, method="gloss", verbose=False):
    """Align YLT text for one book. Returns stats dict."""
    booknum = SLUG_TO_BOOKNUM[slug]
    ylt_data = ensure_ylt_data(booknum)

    # Load Macula data if using gloss method
    macula_data = {}
    if method == "gloss":
        macula_data = load_macula_book(slug)

    # Find all v3-colometric chapter files for this book
    chapter_files = sorted(V3_DIR.glob(f"{slug}-*.txt"))
    if not chapter_files:
        print(f"  WARNING: No v3-colometric files found for {slug}", file=sys.stderr)
        return {"total_verses": 0, "gloss_aligned": 0, "clause_fallback": 0,
                "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    YLT_OUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"total_verses": 0, "gloss_aligned": 0, "clause_fallback": 0,
             "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    for greek_file in chapter_files:
        # Extract chapter number from filename: e.g. "acts-09.txt" -> 9
        fname = greek_file.stem  # "acts-09"
        ch_str = fname.split("-")[-1]
        ch_num = int(ch_str)

        greek_verses = parse_greek_chapter(greek_file)
        ylt_ch = ylt_data.get(ch_num, {})

        out_lines = []

        for verse_num in sorted(greek_verses.keys()):
            greek_lines = greek_verses[verse_num]
            greek_line_count = len(greek_lines)
            ylt_text = ylt_ch.get(verse_num, "")

            stats["total_verses"] += 1

            if not ylt_text:
                stats["missing_ylt"] += 1
                # Write verse ref and placeholder
                out_lines.append(f"{ch_num}:{verse_num}")
                out_lines.append("[YLT text not available]")
                out_lines.append("")
                continue

            english_lines = None
            used_gloss = False

            # Try gloss-based alignment first (if method is gloss)
            if method == "gloss" and macula_data:
                macula_words = macula_data.get((ch_num, verse_num), [])
                if macula_words:
                    english_lines = split_ylt_by_glosses(ylt_text, greek_lines, macula_words)
                    if english_lines is not None:
                        used_gloss = True

            # Fall back to clause-boundary heuristic
            if english_lines is None:
                english_lines = split_text_into_n(ylt_text, greek_line_count)

            # Ensure exactly the right count
            while len(english_lines) < greek_line_count:
                english_lines.append("")
            if len(english_lines) > greek_line_count:
                # Merge extras onto last line
                english_lines = english_lines[:greek_line_count - 1] + [
                    " ".join(english_lines[greek_line_count - 1:])
                ]

            # Track stats
            if used_gloss:
                stats["gloss_aligned"] += 1
            else:
                stats["clause_fallback"] += 1
                # Check if clause split was natural or forced
                candidates_in_text = find_split_candidates(ylt_text)
                natural_breaks_available = len(candidates_in_text)
                breaks_needed = greek_line_count - 1
                if breaks_needed > 0 and natural_breaks_available >= breaks_needed:
                    stats["natural_splits"] += 1
                elif breaks_needed > 0:
                    stats["forced_splits"] += 1
                else:
                    stats["natural_splits"] += 1

            # Write output
            out_lines.append(f"{ch_num}:{verse_num}")
            for el in english_lines:
                out_lines.append(el)
            out_lines.append("")

        # Write output file with same filename
        out_path = YLT_OUT_DIR / greek_file.name
        out_path.write_text("\n".join(out_lines), encoding="utf-8")
        if verbose:
            print(f"  Wrote {out_path.name} ({len(greek_verses)} verses)")

    return stats


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------
def run_tests(method="gloss"):
    """Run test cases on specific passages."""
    print(f"Alignment method: {method}")
    print()

    # ---- Mark 4:3 ----
    print("=" * 70)
    print("TEST: Mark 4:3 — 'Hearken' should be line 1 alone")
    print("=" * 70)

    ylt_data = ensure_ylt_data(41)
    macula_data = load_macula_book("mark") if method == "gloss" else {}
    greek_file = V3_DIR / "mark-04.txt"
    greek_verses = parse_greek_chapter(greek_file)

    for v in [3, 4]:
        greek_lines = greek_verses[v]
        ylt_text = ylt_data[4][v]

        if method == "gloss" and macula_data:
            macula_words = macula_data.get((4, v), [])
            english_lines = split_ylt_by_glosses(ylt_text, greek_lines, macula_words)
            if english_lines is None:
                english_lines = split_text_into_n(ylt_text, len(greek_lines))
                print(f"  [FALLBACK to clause method]")
        else:
            english_lines = split_text_into_n(ylt_text, len(greek_lines))

        while len(english_lines) < len(greek_lines):
            english_lines.append("")
        if len(english_lines) > len(greek_lines):
            english_lines = english_lines[:len(greek_lines) - 1] + [
                " ".join(english_lines[len(greek_lines) - 1:])
            ]

        print(f"\n--- Mark 4:{v} ({len(greek_lines)} Greek lines) ---")
        for i, (gl, el) in enumerate(zip(greek_lines, english_lines)):
            print(f"  GRK {i+1}: {gl}")
            print(f"  YLT {i+1}: {el}")
            print()

    # ---- Acts 9:1-3 ----
    print("=" * 70)
    print("TEST: Acts 9:1-3")
    print("=" * 70)

    ylt_acts = ensure_ylt_data(44)
    macula_acts = load_macula_book("acts") if method == "gloss" else {}
    greek_file_acts = V3_DIR / "acts-09.txt"
    greek_verses_acts = parse_greek_chapter(greek_file_acts)

    for v in [1, 2, 3]:
        greek_lines = greek_verses_acts[v]
        ylt_text = ylt_acts[9][v]

        if method == "gloss" and macula_acts:
            macula_words = macula_acts.get((9, v), [])
            english_lines = split_ylt_by_glosses(ylt_text, greek_lines, macula_words)
            if english_lines is None:
                english_lines = split_text_into_n(ylt_text, len(greek_lines))
                print(f"  [FALLBACK to clause method]")
        else:
            english_lines = split_text_into_n(ylt_text, len(greek_lines))

        while len(english_lines) < len(greek_lines):
            english_lines.append("")
        if len(english_lines) > len(greek_lines):
            english_lines = english_lines[:len(greek_lines) - 1] + [
                " ".join(english_lines[len(greek_lines) - 1:])
            ]

        print(f"\n--- Acts 9:{v} ({len(greek_lines)} Greek lines) ---")
        for i, (gl, el) in enumerate(zip(greek_lines, english_lines)):
            print(f"  GRK {i+1}: {gl}")
            print(f"  YLT {i+1}: {el}")
            print()

    # ---- 1 Timothy 3:16 ----
    print("=" * 70)
    print("TEST: 1 Timothy 3:16 (hymn — expecting 6+ Greek lines)")
    print("=" * 70)

    ylt_1tim = ensure_ylt_data(54)
    macula_1tim = load_macula_book("1tim") if method == "gloss" else {}
    greek_file_1tim = V3_DIR / "1tim-03.txt"
    greek_verses_1tim = parse_greek_chapter(greek_file_1tim)

    v = 16
    greek_lines = greek_verses_1tim[v]
    ylt_text = ylt_1tim[3][v]

    if method == "gloss" and macula_1tim:
        macula_words = macula_1tim.get((3, v), [])
        english_lines = split_ylt_by_glosses(ylt_text, greek_lines, macula_words)
        if english_lines is None:
            english_lines = split_text_into_n(ylt_text, len(greek_lines))
            print(f"  [FALLBACK to clause method]")
    else:
        english_lines = split_text_into_n(ylt_text, len(greek_lines))

    while len(english_lines) < len(greek_lines):
        english_lines.append("")
    if len(english_lines) > len(greek_lines):
        english_lines = english_lines[:len(greek_lines) - 1] + [
            " ".join(english_lines[len(greek_lines) - 1:])
        ]

    print(f"\n--- 1 Tim 3:16 ({len(greek_lines)} Greek lines) ---")
    for i, (gl, el) in enumerate(zip(greek_lines, english_lines)):
        print(f"  GRK {i+1}: {gl}")
        print(f"  YLT {i+1}: {el}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Align YLT to GNT colometric line breaks")
    parser.add_argument("--book", type=str, help="Process single book by slug (e.g. 'acts')")
    parser.add_argument("--method", type=str, default="gloss",
                        choices=["gloss", "clause"],
                        help="Alignment method: 'gloss' (Macula-anchored) or 'clause' (heuristic)")
    parser.add_argument("--test", action="store_true", help="Run test cases")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.test:
        run_tests(method=args.method)
        return

    if args.book:
        slug = args.book.lower()
        if slug not in SLUG_TO_BOOKNUM:
            print(f"ERROR: Unknown book slug '{slug}'", file=sys.stderr)
            print(f"Valid slugs: {', '.join(sorted(SLUG_TO_BOOKNUM.keys()))}", file=sys.stderr)
            sys.exit(1)
        slugs = [slug]
    else:
        slugs = [BOOKNUM_TO_SLUG[n] for n in sorted(BOOKNUM_TO_SLUG.keys())]

    grand_stats = {"total_verses": 0, "gloss_aligned": 0, "clause_fallback": 0,
                   "natural_splits": 0, "forced_splits": 0, "missing_ylt": 0}

    print(f"Alignment method: {args.method}")
    print()

    for slug in slugs:
        print(f"Processing {slug}...")
        stats = align_book(slug, method=args.method, verbose=args.verbose)
        for k in grand_stats:
            grand_stats[k] += stats[k]
        if stats["total_verses"] > 0:
            gloss_pct = stats["gloss_aligned"] / stats["total_verses"] * 100
            fb_pct = stats["clause_fallback"] / stats["total_verses"] * 100
            print(f"  {stats['total_verses']} verses: "
                  f"{stats['gloss_aligned']} gloss ({gloss_pct:.1f}%), "
                  f"{stats['clause_fallback']} fallback ({fb_pct:.1f}%), "
                  f"{stats['missing_ylt']} missing YLT")

    print()
    print("=" * 60)
    print("GRAND TOTALS")
    print("=" * 60)
    total = grand_stats["total_verses"]
    if total > 0:
        gloss_pct = grand_stats["gloss_aligned"] / total * 100
        fb_pct = grand_stats["clause_fallback"] / total * 100
        print(f"Total verses:      {total}")
        print(f"Gloss-aligned:     {grand_stats['gloss_aligned']} ({gloss_pct:.1f}%)")
        print(f"Clause fallback:   {grand_stats['clause_fallback']} ({fb_pct:.1f}%)")
        if grand_stats["clause_fallback"] > 0:
            nat = grand_stats["natural_splits"]
            forced = grand_stats["forced_splits"]
            print(f"  (natural: {nat}, forced: {forced})")
        print(f"Missing YLT:       {grand_stats['missing_ylt']}")


if __name__ == "__main__":
    main()
