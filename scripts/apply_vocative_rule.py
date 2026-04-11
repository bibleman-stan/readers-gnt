#!/usr/bin/env python3
"""
Apply the universal vocative rule to all v4-editorial files.

For every v4-editorial file, find any vocative that is NOT on its own line
and split it onto its own line. Exception: repeated vocatives like
"Κύριε κύριε" stay together.

Uses Macula XML files to identify vocative case words, with manual overrides
for extended vocative phrases (genitive modifiers, prepositional phrases, etc.)
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_DIR = os.path.join(BASE, "data", "text-files", "v4-editorial")
XML_DIR = os.path.join(BASE, "research", "macula-greek", "SBLGNT", "lowfat")

BOOK_MAP = {
    "matt": ("01-matthew.xml", "MAT"),
    "mark": ("02-mark.xml", "MRK"),
    "luke": ("03-luke.xml", "LUK"),
    "john": ("04-john.xml", "JHN"),
    "acts": ("05-acts.xml", "ACT"),
    "rom": ("06-romans.xml", "ROM"),
    "1cor": ("07-1corinthians.xml", "1CO"),
    "2cor": ("08-2corinthians.xml", "2CO"),
    "gal": ("09-galatians.xml", "GAL"),
    "eph": ("10-ephesians.xml", "EPH"),
    "phil": ("11-philippians.xml", "PHP"),
    "col": ("12-colossians.xml", "COL"),
    "1thess": ("13-1thessalonians.xml", "1TH"),
    "2thess": ("14-2thessalonians.xml", "2TH"),
    "1tim": ("15-1timothy.xml", "1TI"),
    "2tim": ("16-2timothy.xml", "2TI"),
    "titus": ("17-titus.xml", "TIT"),
    "phlm": ("18-philemon.xml", "PHM"),
    "heb": ("19-hebrews.xml", "HEB"),
    "jas": ("20-james.xml", "JAS"),
    "1pet": ("21-1peter.xml", "1PE"),
    "2pet": ("22-2peter.xml", "2PE"),
    "1john": ("23-1john.xml", "1JN"),
    "2john": ("24-2john.xml", "2JN"),
    "3john": ("25-3john.xml", "3JN"),
    "jude": ("26-jude.xml", "JUD"),
    "rev": ("27-revelation.xml", "REV"),
}

def strip_punct(word):
    return word.rstrip('\u00b7,;.!?\u0387:\u037E')


def extract_vocatives_from_xml(xml_path):
    """Extract vocative words grouped by verse.
    Returns { "ch:vs" -> [(word_pos, clean_text), ...] }
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    raw = defaultdict(list)
    for w in root.iter('w'):
        if w.get('case') == 'vocative':
            ref = w.get('ref', '')
            parts = ref.split(' ', 1)
            if len(parts) < 2:
                continue
            vp = parts[1]
            verse_ref = vp.split('!')[0]
            word_pos = int(vp.split('!')[1]) if '!' in vp else 0
            text = w.get('unicode', w.text or '')
            raw[verse_ref].append((word_pos, strip_punct(text)))
    for v in raw:
        raw[v].sort()
    return dict(raw)


def group_consecutive(words_list):
    """Group consecutive vocative words (gap <= 2) into phrases."""
    if not words_list:
        return []
    groups = []
    cur = [words_list[0]]
    for i in range(1, len(words_list)):
        if words_list[i][0] - cur[-1][0] <= 2:
            cur.append(words_list[i])
        else:
            groups.append([w for _, w in cur])
            cur = [words_list[i]]
    groups.append([w for _, w in cur])
    return groups


# Override table: maps "BOOK ch:vs" to list of vocative phrases (cleaned words).
# Each phrase is the FULL vocative to put on its own line (including modifiers, ὦ, etc.)
# Empty list = no vocatives to process in this verse.
# "SKIP" = skip this verse entirely.
VOCATIVE_OVERRIDES = {
    # Aramaic "Marana tha" - not a Greek vocative
    "1CO 16:22": [],

    # Rom 2 participial vocatives - these are rhetorical addresses that serve as
    # clause subjects. "ὁ διδάσκων ... κλέπτεις;" The vocative IS the subject.
    # Keep them as-is since they're already structured correctly with their verbs.
    "ROM 2:21": "SKIP",
    "ROM 2:22": "SKIP",
    # "ποιῶν" in 2:3 is continuation of vocative from prior clause
    "ROM 2:3": [["ὦ", "ἄνθρωπε", "ὁ", "κρίνων"]],

    # Extended vocative phrases with modifiers
    "1TI 6:11": [["ὦ", "ἄνθρωπε", "θεοῦ"]],
    "1TH 1:4": [["ἀδελφοὶ", "ἠγαπημένοι", "ὑπὸ", "θεοῦ"]],
    "2TH 2:13": [["ἀδελφοὶ", "ἠγαπημένοι", "ὑπὸ", "κυρίου"]],
    "MAT 2:6": [["Βηθλέεμ", "γῆ", "Ἰούδα"]],
    "MAT 3:7": [["Γεννήματα", "ἐχιδνῶν"]],
    "MAT 8:29": [["υἱὲ", "τοῦ", "θεοῦ"]],
    "LUK 4:34": [["Ἰησοῦ", "Ναζαρηνέ"]],
    "LUK 8:28": [["Ἰησοῦ", "υἱὲ", "τοῦ", "θεοῦ", "τοῦ", "ὑψίστου"]],
    "ACT 1:24": [["κύριε", "καρδιογνῶστα", "πάντων"]],
    "ACT 7:42": [["οἶκος", "Ἰσραήλ"]],
    "ROM 8:15": [["Αββα", "ὁ", "πατήρ"]],
    "GAL 4:6": [["Αββα", "ὁ", "πατήρ"]],
    "ROM 15:11": [["πάντα", "τὰ", "ἔθνη"]],
    "HEB 3:1": [["ἀδελφοὶ", "ἅγιοι", "κλήσεως", "ἐπουρανίου", "μέτοχοι"]],

    # Participial vocatives with objects - keep phrase together
    "JAS 4:12": [["ὁ", "κρίνων", "τὸν", "πλησίον"]],
    "JAS 4:13": [["οἱ", "λέγοντες"]],
    "GAL 4:21": [["οἱ", "ὑπὸ", "νόμον", "θέλοντες", "εἶναι"]],

    # Extended vocative addresses in Revelation doxologies
    "REV 4:11": [["ὁ", "κύριος", "καὶ", "ὁ", "θεὸς", "ἡμῶν"]],

    # Extended vocatives in Pauline letters needing split
    "1CO 15:58": [["ἀδελφοί", "μου", "ἀγαπητοί"]],
    "PHP 4:1": [["ἀδελφοί", "μου", "ἀγαπητοὶ", "καὶ", "ἐπιπόθητοι"],
                 ["χαρὰ", "καὶ", "στέφανός"]],

    # OT quotation vocative in Galatians
    "GAL 4:27": [["στεῖρα", "ἡ", "οὐ", "τίκτουσα"]],

    # Woe statements - vocative with temporal modifier
    "LUK 6:25": [["οἱ", "ἐμπεπλησμένοι", "νῦν"], ["οἱ", "γελῶντες", "νῦν"]],

    # Vocative with article - include article
    "EPH 5:14": [["ὁ", "καθεύδων"]],
    "EPH 5:22": [["Αἱ", "γυναῖκες"]],

    # "Καὶ" before household code vocatives - keep with vocative
    "EPH 6:4": [["οἱ", "πατέρες"]],
    "EPH 6:9": [["οἱ", "κύριοι"]],

    # John 1:38 - Ῥαββί with parenthetical
    "JHN 1:38": "SKIP",  # Complex parenthetical, leave as-is
}


def get_phrases_for_verse(book_abbrev, verse_ref, raw_vocatives):
    """Get vocative phrases for a verse, using overrides + raw vocatives.

    Overrides take priority; raw vocatives that don't overlap with overrides
    are also included. SKIP and empty-list overrides suppress all vocatives.
    """
    key = f"{book_abbrev} {verse_ref}"
    if key in VOCATIVE_OVERRIDES:
        val = VOCATIVE_OVERRIDES[key]
        if val == "SKIP" or val == []:
            return []
        # Start with override phrases
        phrases = list(val)
        # Also include raw vocatives not covered by overrides
        if verse_ref in raw_vocatives:
            override_words = set()
            for phrase in val:
                for w in phrase:
                    override_words.add(w)
            raw_groups = group_consecutive(raw_vocatives[verse_ref])
            for rg in raw_groups:
                # Include this group if none of its words appear in overrides
                if not any(w in override_words for w in rg):
                    phrases.append(rg)
        return phrases

    if verse_ref not in raw_vocatives:
        return []

    return group_consecutive(raw_vocatives[verse_ref])


def find_phrase_in_line(line_words_clean, phrase):
    """Find a phrase in cleaned line words. Returns (start, end) or None."""
    plen = len(phrase)
    for si in range(len(line_words_clean)):
        if si + plen > len(line_words_clean):
            break
        if all(line_words_clean[si+j] == phrase[j] for j in range(plen)):
            return (si, si + plen)
    return None


def try_split_vocative(line, phrases):
    """Try to split a line so vocatives get their own line.

    Returns list of line parts, or None if no split needed.
    """
    words = line.split()
    if not words:
        return None
    words_clean = [strip_punct(w) for w in words]

    for phrase in phrases:
        match = find_phrase_in_line(words_clean, phrase)
        if match is None:
            continue

        start_idx, end_idx = match

        # Check for preceding ὦ/Ὦ (only if not already in phrase)
        if phrase[0] not in ('ὦ', 'Ὦ') and start_idx > 0 and strip_punct(words[start_idx-1]) in ('ὦ', 'Ὦ'):
            start_idx -= 1

        # Check for following μου (only if not already in phrase)
        if end_idx < len(words) and strip_punct(words[end_idx]) == 'μου' and 'μου' not in phrase:
            end_idx += 1

        # If vocative is already the entire line, no split needed
        if start_idx == 0 and end_idx == len(words):
            return None

        # For Eph 6:4/6:9 pattern: "Καὶ οἱ πατέρες, ..." - keep Καὶ with vocative
        if start_idx > 0 and strip_punct(words[start_idx-1]) in ('Καὶ', 'καὶ'):
            # Only if it's the first word on the line
            if start_idx == 1:
                start_idx = 0

        parts = []
        before = words[:start_idx]
        voc = words[start_idx:end_idx]
        after = words[end_idx:]

        if before:
            parts.append(' '.join(before))
        if voc:
            parts.append(' '.join(voc))
        if after:
            parts.append(' '.join(after))

        if len(parts) > 1:
            return parts

    return None


def detect_line_ending(content):
    """Detect whether file uses CRLF or LF."""
    if '\r\n' in content:
        return '\r\n'
    return '\n'


def process_file(v4_path, book_abbrev, raw_vocatives, chapter_num):
    """Process a single v4 file."""
    with open(v4_path, 'rb') as f:
        raw = f.read()
    content = raw.decode('utf-8')
    le = detect_line_ending(content)
    lines = content.replace('\r\n', '\n').split('\n')

    new_lines = []
    changes = []
    current_verse = None

    for line in lines:
        stripped = line.rstrip()
        verse_match = re.match(r'^(\d+:\d+)\s*$', stripped)
        if verse_match:
            current_verse = verse_match.group(1)
            new_lines.append(stripped)
            continue

        if not stripped:
            new_lines.append('')
            continue

        if current_verse:
            phrases = get_phrases_for_verse(book_abbrev, current_verse, raw_vocatives)
            if phrases:
                result = try_split_vocative(stripped, phrases)
                if result and len(result) > 1:
                    changes.append(f"  {current_verse}: {stripped[:70]}")
                    for part in result:
                        changes.append(f"    -> {part}")
                    new_lines.extend(result)
                    continue

        new_lines.append(stripped)

    new_content = le.join(new_lines)
    return new_content, changes


def main():
    total_changes = 0
    files_changed = 0
    xml_cache = {}

    v4_files = sorted(os.listdir(V4_DIR))

    for v4_file in v4_files:
        if not v4_file.endswith('.txt'):
            continue

        book_prefix = v4_file.rsplit('-', 1)[0]
        chapter_str = v4_file.rsplit('-', 1)[1].replace('.txt', '')
        chapter_num = str(int(chapter_str))

        if book_prefix not in BOOK_MAP:
            print(f"WARNING: No mapping for {book_prefix}", file=sys.stderr)
            continue

        xml_file, book_abbrev = BOOK_MAP[book_prefix]
        xml_path = os.path.join(XML_DIR, xml_file)

        if xml_file not in xml_cache:
            xml_cache[xml_file] = extract_vocatives_from_xml(xml_path)

        raw_vocatives = xml_cache[xml_file]

        # Filter to this chapter
        chapter_vocs = {}
        for vr, words in raw_vocatives.items():
            if vr.split(':')[0] == chapter_num:
                chapter_vocs[vr] = words

        # Also check overrides for this book+chapter
        has_overrides = False
        for key in VOCATIVE_OVERRIDES:
            if key.startswith(f"{book_abbrev} {chapter_num}:"):
                has_overrides = True
                break

        if not chapter_vocs and not has_overrides:
            continue

        v4_path = os.path.join(V4_DIR, v4_file)
        new_content, changes = process_file(v4_path, book_abbrev, chapter_vocs, chapter_num)

        if changes:
            files_changed += 1
            total_changes += len([c for c in changes if c.startswith('  ')])
            print(f"\n{v4_file}:")
            for c in changes:
                print(c)

            with open(v4_path, 'wb') as f:
                f.write(new_content.encode('utf-8'))

    print(f"\n{'='*60}")
    print(f"Files changed: {files_changed}")
    print(f"Total vocative splits: {total_changes}")


if __name__ == '__main__':
    main()
