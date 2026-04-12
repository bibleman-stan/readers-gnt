"""
detect_attributive_splits.py

Finds lines in v4-editorial where an attributive participle (or adjective)
has been split from its head noun across a line break.

Pattern detected:
  Line N ends with: [article (RA)] ... participle/adjective
  Line N+1 starts with: head noun agreeing in case/number/gender

Usage:
  PYTHONIOENCODING=utf-8 py -3 scripts/detect_attributive_splits.py
"""

import os
import re
import glob
from collections import defaultdict

# Paths
REPO = r"c:\Users\bibleman\repos\readers-gnt"
MORPHGNT_DIR = os.path.join(REPO, "research", "morphgnt-sblgnt")
V4_DIR = os.path.join(REPO, "data", "text-files", "v4-editorial")

# Book mapping: MorphGNT prefix -> v4-editorial folder name
BOOK_MAP = {
    "61": "matt", "62": "mark", "63": "luke", "64": "john", "65": "acts",
    "66": "rom", "67": "1cor", "68": "2cor", "69": "gal", "70": "eph",
    "71": "phil", "72": "col", "73": "1thess", "74": "2thess",
    "75": "1tim", "76": "2tim", "77": "titus", "78": "phlm",
    "79": "heb", "80": "jas", "81": "1pet", "82": "2pet",
    "83": "1john", "84": "2john", "85": "3john", "86": "jude", "87": "rev",
}

# Reverse: folder name -> morphgnt prefix
FOLDER_TO_PREFIX = {v: k for k, v in BOOK_MAP.items()}

# Folder number prefixes in v4-editorial
FOLDER_NUM = {
    "matt": "01", "mark": "02", "luke": "03", "john": "04", "acts": "05",
    "rom": "06", "1cor": "07", "2cor": "08", "gal": "09", "eph": "10",
    "phil": "11", "col": "12", "1thess": "13", "2thess": "14",
    "1tim": "15", "2tim": "16", "titus": "17", "phlm": "18",
    "heb": "19", "jas": "20", "1pet": "21", "2pet": "22",
    "1john": "23", "2john": "24", "3john": "25", "jude": "26", "rev": "27",
}


def strip_markers(word):
    """Strip punctuation and critical apparatus markers for matching."""
    return re.sub(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—\u037E\u0387\u00B7\u2019\u02BC]', '', word)


def normalize_for_match(word):
    """Normalize a word for matching between v4 text and MorphGNT."""
    w = strip_markers(word)
    # Remove combining characters issues, lowercase for comparison
    return w


class MorphGNTData:
    """Loads and indexes MorphGNT data for lookup."""

    def __init__(self):
        # Index: (book_prefix, chapter, verse) -> list of (pos, parsing, text, word, normalized, lemma)
        self.verses = defaultdict(list)
        self._load_all()

    def _load_all(self):
        for prefix, book_name in BOOK_MAP.items():
            filepath = os.path.join(MORPHGNT_DIR, f"{prefix}-{self._morphgnt_abbrev(prefix)}-morphgnt.txt")
            if not os.path.exists(filepath):
                # Try finding the file
                candidates = glob.glob(os.path.join(MORPHGNT_DIR, f"{prefix}-*"))
                if candidates:
                    filepath = candidates[0]
                else:
                    continue
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 7:
                        continue
                    ref = parts[0]  # BBCCVV
                    chapter = int(ref[2:4])
                    verse = int(ref[4:6])
                    pos = parts[1]
                    parsing = parts[2]
                    text = parts[3]
                    word = parts[4]
                    normalized = parts[5]
                    lemma = parts[6]
                    self.verses[(book_name, chapter, verse)].append({
                        'pos': pos,
                        'parsing': parsing,
                        'text': text,
                        'word': word,
                        'normalized': normalized,
                        'lemma': lemma,
                    })

    def _morphgnt_abbrev(self, prefix):
        """Get MorphGNT file abbreviation from prefix."""
        abbrevs = {
            "61": "Mt", "62": "Mk", "63": "Lk", "64": "Jn", "65": "Ac",
            "66": "Ro", "67": "1Co", "68": "2Co", "69": "Ga", "70": "Eph",
            "71": "Php", "72": "Col", "73": "1Th", "74": "2Th",
            "75": "1Ti", "76": "2Ti", "77": "Tit", "78": "Phm",
            "79": "Heb", "80": "Jas", "81": "1Pe", "82": "2Pe",
            "83": "1Jn", "84": "2Jn", "85": "3Jn", "86": "Jud", "87": "Re",
        }
        return abbrevs.get(prefix, "")

    def get_word_info(self, book_name, chapter, verse, word_text):
        """Find morphological info for a word in a given verse."""
        stripped = normalize_for_match(word_text)
        if not stripped:
            return None
        verse_words = self.verses.get((book_name, chapter, verse), [])
        for entry in verse_words:
            if normalize_for_match(entry['text']) == stripped or normalize_for_match(entry['word']) == stripped:
                return entry
        # Try case-insensitive
        stripped_lower = stripped.lower()
        for entry in verse_words:
            if normalize_for_match(entry['text']).lower() == stripped_lower or normalize_for_match(entry['word']).lower() == stripped_lower:
                return entry
        return None

    def get_verse_words(self, book_name, chapter, verse):
        """Get all words in a verse with their morphological info."""
        return self.verses.get((book_name, chapter, verse), [])


def is_participle(entry):
    """Check if a MorphGNT entry is a participle (verb with mood=P)."""
    if entry and entry['pos'] == 'V-':
        parsing = entry['parsing']
        if len(parsing) > 3 and parsing[3] == 'P':
            return True
    return False


def is_article(entry):
    """Check if a MorphGNT entry is an article."""
    return entry and entry['pos'] == 'RA'


def is_noun(entry):
    """Check if a MorphGNT entry is a noun."""
    return entry and entry['pos'] == 'N-'


def is_adjective(entry):
    """Check if a MorphGNT entry is an adjective."""
    return entry and entry['pos'] == 'A-'


def get_cng(entry):
    """Get case/number/gender from parsing field.
    For verbs (participles): positions [4]=case, [5]=number, [6]=gender
    For articles (RA): positions [4]=case, [5]=number, [6]=gender
    For nouns (N-): positions [4]=case, [5]=number, [6]=gender
    For adjectives (A-): positions [4]=case, [5]=number, [6]=gender
    """
    if not entry:
        return None
    parsing = entry['parsing']
    if len(parsing) < 7:
        return None
    # All relevant POS use positions 4,5,6 for case/number/gender
    # But the parsing format is: ----CNGD for nouns/articles or TVMPNSG- for verbs
    # Let me check: MorphGNT format is 8 chars
    # Verbs: [0]=tense, [1]=voice, [2]=mood, [3-7] depend on mood
    #   For participles (mood=P): [3]=P then [4]=case, [5]=number, [6]=gender
    # Wait, re-reading the user's spec:
    # "Parsing field for verbs: position [3] = mood (P = participle)"
    # "Parsing field: position [4] = case, [5] = number, [6] = gender"
    # "For articles (RA): parsing positions are [4]=case, [5]=number, [6]=gender"

    # Actually MorphGNT parsing is 8 chars:
    # For nouns/articles: ----CNGD (first 4 are dashes, then case, number, gender, degree)
    # For verbs: TVMPCNG- (tense, voice, mood, person/case, number, gender, -, -)
    # Wait let me look at actual data:
    # N- ----NSF-  -> positions 4=N(nominative), 5=S(singular), 6=F(feminine)
    # RA ----NSF-  -> same
    # V- -APP-NSM -> tense=A, voice=P, mood=P, person=-, N, S, M

    # From the file: "010101 N- ----NSF- Βίβλος"
    # So parsing is 8 chars. For nouns: ----CNGX where C=case, N=number, G=gender
    # positions: 0123 4567 -> [4]=case, [5]=number, [6]=gender

    # For verbs with participle, let me check actual morphgnt data
    # Actually the user said: position [3] = mood for verbs
    # So verb parsing: [0]=tense, [1]=voice, [2]=mood, then for participles:
    # [3]=? Let me just use [4],[5],[6] as user specified

    case = parsing[4] if len(parsing) > 4 else '-'
    number = parsing[5] if len(parsing) > 5 else '-'
    gender = parsing[6] if len(parsing) > 6 else '-'

    if case == '-' and number == '-' and gender == '-':
        return None
    return (case, number, gender)


def cng_agrees(cng1, cng2):
    """Check if two case/number/gender tuples agree."""
    if not cng1 or not cng2:
        return False
    # Allow dash to match anything
    for a, b in zip(cng1, cng2):
        if a == '-' or b == '-':
            continue
        if a != b:
            return False
    return True


def cng_label(cng):
    """Human-readable label for case/number/gender."""
    if not cng:
        return "???"
    return f"{cng[0]}{cng[1]}{cng[2]}"


def parse_v4_file(filepath):
    """Parse a v4-editorial file into verses with their lines.
    Returns list of (verse_ref, line_number, line_text) tuples.
    """
    results = []
    current_verse = None
    line_num = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line_num += 1
            line = raw_line.rstrip('\n').rstrip('\r')
            # Check if this is a verse reference line
            verse_match = re.match(r'^(\d+:\d+)\s*$', line)
            if verse_match:
                current_verse = verse_match.group(1)
                continue
            # Skip empty lines
            if not line.strip():
                continue
            if current_verse:
                results.append((current_verse, line_num, line))
    return results


def get_words_from_line(line):
    """Split a line into words, preserving order."""
    return line.split()


def detect_splits():
    """Main detection logic."""
    print("Loading MorphGNT data...")
    morph = MorphGNTData()
    print("MorphGNT loaded.\n")

    findings = []

    # Iterate over all v4-editorial files
    v4_folders = sorted(glob.glob(os.path.join(V4_DIR, "*-*")))

    for folder in v4_folders:
        folder_name = os.path.basename(folder)
        # Extract book name: "01-matt" -> "matt"
        parts = folder_name.split('-', 1)
        if len(parts) < 2:
            continue
        book_name = parts[1]

        txt_files = sorted(glob.glob(os.path.join(folder, "*.txt")))
        for txt_file in txt_files:
            filename = os.path.basename(txt_file)
            lines_data = parse_v4_file(txt_file)

            # Process pairs of consecutive lines
            for i in range(len(lines_data) - 1):
                verse_ref, line_num, line_text = lines_data[i]
                next_verse_ref, next_line_num, next_line_text = lines_data[i + 1]

                # Both lines should be in the same verse for this to be a split
                # (cross-verse splits are less likely to be errors)
                if verse_ref != next_verse_ref:
                    continue

                chapter = int(verse_ref.split(':')[0])
                verse = int(verse_ref.split(':')[1])

                words_this = get_words_from_line(line_text)
                words_next = get_words_from_line(next_line_text)

                if not words_this or not words_next:
                    continue

                # Pattern 1: Line ends with participle, article earlier on line,
                # next line starts with noun agreeing in CNG
                last_word = words_this[-1]
                last_info = morph.get_word_info(book_name, chapter, verse, last_word)

                if is_participle(last_info):
                    ptcp_cng = get_cng(last_info)
                    if ptcp_cng:
                        # Look for article earlier on same line that agrees
                        article_info = None
                        article_word = None
                        for w in words_this[:-1]:
                            info = morph.get_word_info(book_name, chapter, verse, w)
                            if is_article(info) and cng_agrees(get_cng(info), ptcp_cng):
                                article_info = info
                                article_word = w

                        if article_info:
                            # Check if next line starts with agreeing noun
                            first_next = words_next[0]
                            first_next_info = morph.get_word_info(book_name, chapter, verse, first_next)
                            if is_noun(first_next_info) and cng_agrees(get_cng(first_next_info), ptcp_cng):
                                findings.append({
                                    'file': filename,
                                    'verse': verse_ref,
                                    'lines': (line_num, next_line_num),
                                    'line1': line_text,
                                    'line2': next_line_text,
                                    'type': 'participle',
                                    'article': article_word,
                                    'modifier': strip_markers(last_word),
                                    'noun': strip_markers(first_next),
                                    'cng': cng_label(ptcp_cng),
                                })

                # Pattern 2: Line ends with article, next line starts with participle
                if is_article(last_info):
                    art_cng = get_cng(last_info)
                    if art_cng:
                        first_next = words_next[0]
                        first_next_info = morph.get_word_info(book_name, chapter, verse, first_next)
                        if is_participle(first_next_info) and cng_agrees(get_cng(first_next_info), art_cng):
                            findings.append({
                                'file': filename,
                                'verse': verse_ref,
                                'lines': (line_num, next_line_num),
                                'line1': line_text,
                                'line2': next_line_text,
                                'type': 'article-participle split',
                                'article': strip_markers(last_word),
                                'modifier': strip_markers(first_next),
                                'noun': '(participle on next line)',
                                'cng': cng_label(art_cng),
                            })

                # Pattern 3: Line ends with adjective, article earlier on line,
                # next line starts with agreeing noun
                if is_adjective(last_info):
                    adj_cng = get_cng(last_info)
                    if adj_cng:
                        # Look for article earlier on same line
                        article_info = None
                        article_word = None
                        for w in words_this[:-1]:
                            info = morph.get_word_info(book_name, chapter, verse, w)
                            if is_article(info) and cng_agrees(get_cng(info), adj_cng):
                                article_info = info
                                article_word = w

                        if article_info:
                            first_next = words_next[0]
                            first_next_info = morph.get_word_info(book_name, chapter, verse, first_next)
                            if is_noun(first_next_info) and cng_agrees(get_cng(first_next_info), adj_cng):
                                findings.append({
                                    'file': filename,
                                    'verse': verse_ref,
                                    'lines': (line_num, next_line_num),
                                    'line1': line_text,
                                    'line2': next_line_text,
                                    'type': 'adjective',
                                    'article': article_word,
                                    'modifier': strip_markers(last_word),
                                    'noun': strip_markers(first_next),
                                    'cng': cng_label(adj_cng),
                                })

    return findings


def main():
    findings = detect_splits()

    print("=== ATTRIBUTIVE PARTICIPLE SPLITS ===\n")

    files_with_splits = set()
    for f in findings:
        files_with_splits.add(f['file'])
        print(f"{f['file']} {f['verse']} (lines {f['lines'][0]}-{f['lines'][1]})")
        print(f"  {f['line1']}")
        print(f"  {f['line2']}")
        if f['type'] == 'article-participle split':
            print(f"  → article {f['article']} ({f['cng']}) split from participle {f['modifier']} on next line")
        else:
            print(f"  → article {f['article']} ({f['cng']}) + {f['type']} {f['modifier']} ({f['cng']}) split from noun {f['noun']} ({f['cng']})")
        print()

    print(f"SUMMARY: {len(findings)} splits found across {len(files_with_splits)} files")


if __name__ == '__main__':
    main()
