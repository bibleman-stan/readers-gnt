#!/usr/bin/env python3
"""
Regenerate English structural glosses for all v4-editorial files.

Each English line corresponds 1:1 to a Greek line.
Strategy:
1. Where verse line counts match, keep existing English unchanged.
2. Where counts differ, merge all existing English for the verse,
   then redistribute across the new Greek line structure using
   proportional word allocation (based on Greek word counts per line).
3. For vocative-only lines, use a known translation rather than proportional split.
"""

import os
import re
import sys
from collections import OrderedDict, defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_DIR = os.path.join(BASE, "data", "text-files", "v4-editorial")
WEB_DIR = os.path.join(BASE, "data", "text-files", "web-colometric")


def strip_punct(word):
    return word.rstrip('\u00b7,;.!?\u0387:\u037E')


# Full vocative phrase translations (Greek line -> English line)
VOCATIVE_PHRASE_MAP = {
    'ἀδελφοί,': 'brothers,',
    'ἀδελφοί·': 'brothers;',
    'Ἀδελφοί,': 'Brothers,',
    'ἀδελφέ,': 'brother,',
    'ἀδελφέ.': 'brother.',
    'ἀδελφοί μου,': 'my brothers,',
    'ἀγαπητοί μου,': 'my beloved,',
    'ἀγαπητοί,': 'beloved,',
    'ἀγαπητοί.': 'beloved.',
    'Ἀγαπητοί,': 'Beloved,',
    'Κύριε,': 'Lord,',
    'κύριε·': 'Lord;',
    'κύριε.': 'Lord.',
    'Πάτερ,': 'Father,',
    'πάτερ,': 'father,',
    'Τέκνον,': 'Child,',
    'τέκνα μου,': 'my children,',
    'τέκνον μου,': 'my child,',
    'Ῥαββί,': 'Rabbi,',
    'Ἐπιστάτα,': 'Master,',
    'Διδάσκαλε,': 'Teacher,',
    'Ἄνθρωπε,': 'Man,',
    'Σατανᾶ·': 'Satan!',
    'Φίλε,': 'Friend,',
    'γύναι,': 'wife,',
    'ἄνερ,': 'husband,',
    'θάνατε,': 'death,',
    'ἄφρονες,': 'fools,',
    'ἄφρων,': 'fool,',
    'ὑποκριτά,': 'hypocrite,',
    'μοιχαλίδες,': 'adulteresses,',
    'ἁμαρτωλοί,': 'sinners,',
    'δίψυχοι.': 'double-minded.',
    'κεχαριτωμένη,': 'favored one,',
    'Ζαχαρία,': 'Zechariah,',
    'Μαριάμ,': 'Mary,',
    'Ἰατρέ,': 'Physician,',
    'παιδίον,': 'child,',
    'Ἁνανία,': 'Ananias,',
    'Αἰνέα,': 'Aeneas,',
    'Ταβιθά,': 'Tabitha,',
    'Κύριε Ἰησοῦ,': 'Lord Jesus,',
    'Σαοὺλ Σαούλ,': 'Saul, Saul,',
    'Σαοὺλ ἀδελφέ,': 'Brother Saul,',
    'Ἄνδρες Ἰσραηλῖται,': 'Men of Israel,',
    'Ἄνδρες,': 'Men,',
    'Αἱ γυναῖκες,': 'Wives,',
    'Αἱ γυναῖκες': 'Wives',
    'οἱ ἄνδρες,': 'Husbands,',
    'Οἱ ἄνδρες,': 'Husbands,',
    'Τὰ τέκνα,': 'Children,',
    'οἱ πατέρες,': 'Fathers,',
    'Καὶ οἱ πατέρες,': 'And fathers,',
    'οἱ δοῦλοι,': 'Servants,',
    'Οἱ δοῦλοι,': 'Servants,',
    'οἱ κύριοι,': 'Masters,',
    'Καὶ οἱ κύριοι,': 'And masters,',
    'ὁ καθεύδων,': 'you who sleep,',
    'γνήσιε σύζυγε,': 'true companion,',
    'Φιλιππήσιοι,': 'Philippians,',
    'Κορίνθιοι,': 'Corinthians,',
    'πάντα τὰ ἔθνη,': 'all nations,',
    'ἔθνη,': 'nations,',
    'Πάτερ Ἀβραάμ,': 'Father Abraham,',
    'πάτερ Ἀβραάμ,': 'father Abraham,',
    'ὦ ἄνθρωπε θεοῦ,': 'O man of God,',
    'Ὦ Τιμόθεε,': 'O Timothy,',
    'ὦ ἄνθρωπε πᾶς ὁ κρίνων·': 'O man, every one who judges!',
    'ὦ ἄνθρωπε ὁ κρίνων': 'O man who judges',
    'ὦ ἄνθρωπε,': 'O man,',
    'τέκνον Τιμόθεε,': 'child Timothy,',
    'ἀδελφοὶ ἅγιοι, κλήσεως ἐπουρανίου μέτοχοι,': 'holy brothers, partakers of a heavenly calling,',
    'ἀδελφοὶ ἠγαπημένοι ὑπὸ θεοῦ,': 'brothers beloved by God,',
    'ἀδελφοὶ ἠγαπημένοι ὑπὸ κυρίου,': 'brothers beloved by the Lord,',
    'Αββα ὁ πατήρ·': 'Abba, Father!',
    'Αββα ὁ πατήρ.': 'Abba, Father.',
    'Βηθλέεμ γῆ Ἰούδα,': 'Bethlehem, land of Judah,',
    'Γεννήματα ἐχιδνῶν,': 'Brood of vipers,',
    'υἱὲ τοῦ θεοῦ;': 'Son of God?',
    'Ἰησοῦ Ναζαρηνέ;': 'Jesus of Nazareth?',
    'Ἰησοῦ υἱὲ τοῦ θεοῦ τοῦ ὑψίστου;': 'Jesus, Son of the Most High God?',
    'κύριε καρδιογνῶστα πάντων,': 'Lord, knower of all hearts,',
    'οἶκος Ἰσραήλ;': 'house of Israel?',
    'Κύριε κύριε,': 'Lord, Lord,',
    'Ἐπιστάτα ἐπιστάτα,': 'Master, Master,',
    'Ἡ παῖς,': 'Little girl,',
    'Ῥακά,': 'Raca,',
    'Μωρέ,': 'Fool,',
    'οἱ ὑπὸ νόμον θέλοντες εἶναι,': 'you who want to be under the law,',
    'οἱ ἐμπεπλησμένοι νῦν,': 'you who are full now,',
    'οἱ γελῶντες νῦν,': 'you who laugh now,',
    'ὁ κρίνων τὸν πλησίον;': 'you who judge your neighbor?',
    'οἱ λέγοντες·': 'you who say:',
    'Υἱέ μου,': 'My son,',
    'Ἀδελφέ,': 'Brother,',
    'ὁ κύριος καὶ ὁ θεὸς ἡμῶν,': 'our Lord and God,',
    'ἀδελφοί μου ἀγαπητοί,': 'my beloved brothers,',
    'ἀδελφοί μου ἀγαπητοὶ καὶ ἐπιπόθητοι,': 'my beloved and longed-for brothers,',
    'χαρὰ καὶ στέφανός μου,': 'my joy and crown,',
    'στεῖρα ἡ οὐ τίκτουσα,': 'O barren one who does not bear,',
    'ἡ οὐκ ὠδίνουσα·': 'you who are not in labor!',
}


def parse_verses(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.replace('\r\n', '\n').split('\n')
    verses = OrderedDict()
    current = None
    for line in lines:
        s = line.rstrip()
        m = re.match(r'^(\d+:\d+)$', s)
        if m:
            current = m.group(1)
            verses[current] = []
            continue
        if not s: continue
        if current: verses[current].append(s)
    return verses


def parse_file_structure(path):
    with open(path, 'rb') as f:
        raw = f.read()
    content = raw.decode('utf-8')
    le = '\r\n' if '\r\n' in content else '\n'
    lines = content.replace('\r\n', '\n').split('\n')
    structure = []
    current_verse = None
    for line in lines:
        stripped = line.rstrip()
        vm = re.match(r'^(\d+:\d+)\s*$', stripped)
        if vm:
            current_verse = vm.group(1)
            structure.append(('verse', current_verse))
            continue
        if not stripped:
            structure.append(('blank',))
            continue
        if current_verse:
            structure.append(('content', stripped, current_verse))
    return structure, le


def redistribute_verse(greek_lines, english_lines):
    """Redistribute English text to match the Greek line count.

    Strategy:
    1. Identify vocative-only Greek lines and assign known translations.
    2. Identify which existing English lines are vocative translations to exclude.
    3. Merge remaining English and distribute proportionally across non-vocative lines.
    """
    n_greek = len(greek_lines)
    n_english = len(english_lines)

    if n_greek == n_english:
        return english_lines

    # Identify vocative Greek lines
    vocative_indices = {}
    for i, gl in enumerate(greek_lines):
        stripped = gl.strip()
        if stripped in VOCATIVE_PHRASE_MAP:
            vocative_indices[i] = VOCATIVE_PHRASE_MAP[stripped]

    # Build reverse lookup: known vocative English translations
    known_voc_english = set()
    for eng in VOCATIVE_PHRASE_MAP.values():
        known_voc_english.add(eng.strip())
        known_voc_english.add(eng.strip().rstrip('.,;:!?'))

    # Filter out English lines that are vocative translations
    non_voc_english = []
    for el in english_lines:
        stripped = el.strip()
        if stripped in known_voc_english or stripped.rstrip('.,;:!?') in known_voc_english:
            continue
        non_voc_english.append(el)

    # Merge non-vocative English
    remaining_english = ' '.join(non_voc_english).strip()
    remaining_english = re.sub(r'\s+', ' ', remaining_english)

    # Non-vocative Greek line indices
    non_voc_indices = [i for i in range(n_greek) if i not in vocative_indices]
    n_non_voc = len(non_voc_indices)

    if n_non_voc == 0:
        result = [''] * n_greek
        for i, eng in vocative_indices.items():
            result[i] = eng
        return result

    # Proportional distribution
    eng_words = remaining_english.split() if remaining_english else []
    total_eng_words = len(eng_words)
    non_voc_greek_counts = [len(greek_lines[i].split()) for i in non_voc_indices]
    total_greek_words = sum(non_voc_greek_counts)

    distributed = {}
    eng_idx = 0
    for j, nvi in enumerate(non_voc_indices):
        gwc = non_voc_greek_counts[j]
        if j == len(non_voc_indices) - 1:
            distributed[nvi] = ' '.join(eng_words[eng_idx:])
        else:
            if total_greek_words > 0:
                proportion = gwc / total_greek_words
                n_words = max(1, round(proportion * total_eng_words))
            else:
                n_words = max(1, total_eng_words // n_non_voc)
            distributed[nvi] = ' '.join(eng_words[eng_idx:eng_idx + n_words])
            eng_idx += n_words

    result = []
    for i in range(n_greek):
        if i in vocative_indices:
            result.append(vocative_indices[i])
        elif i in distributed:
            result.append(distributed[i])
        else:
            result.append('')

    return result


def check_vocative_quality(greek_lines, english_lines):
    """Check if any vocative-only Greek lines have wrong English translations."""
    for i, gl in enumerate(greek_lines):
        stripped = gl.strip()
        if stripped in VOCATIVE_PHRASE_MAP:
            if i < len(english_lines) and english_lines[i].strip() != VOCATIVE_PHRASE_MAP[stripped]:
                return True
    return False


def process_file(v4_file, force=False):
    v4_path = os.path.join(V4_DIR, v4_file)
    web_path = os.path.join(WEB_DIR, v4_file)
    if not os.path.exists(web_path):
        return 0

    v4_structure, le = parse_file_structure(v4_path)
    v4_verses = parse_verses(v4_path)
    web_verses = parse_verses(web_path)

    new_english = OrderedDict()
    changes = 0

    for verse_ref, greek_lines in v4_verses.items():
        existing = web_verses.get(verse_ref, [])
        needs_regen = len(greek_lines) != len(existing)
        if not needs_regen and (force or check_vocative_quality(greek_lines, existing)):
            needs_regen = True
        if needs_regen:
            changes += 1
            new_lines = redistribute_verse(greek_lines, existing)
            new_english[verse_ref] = new_lines
        else:
            new_english[verse_ref] = list(existing)

    if changes == 0:
        return 0

    # Reconstruct output following v4 structure
    output_lines = []
    verse_line_idx = defaultdict(int)
    for item in v4_structure:
        if item[0] == 'verse':
            output_lines.append(item[1])
        elif item[0] == 'blank':
            output_lines.append('')
        elif item[0] == 'content':
            vr = item[2]
            idx = verse_line_idx[vr]
            eng = new_english.get(vr, [])
            if idx < len(eng):
                output_lines.append(eng[idx])
            else:
                output_lines.append('')
            verse_line_idx[vr] += 1

    new_content = le.join(output_lines)
    with open(web_path, 'wb') as f:
        f.write(new_content.encode('utf-8'))

    return changes


def main():
    force = '--force' in sys.argv
    total_changes = 0
    files_changed = 0

    for v4_file in sorted(os.listdir(V4_DIR)):
        if not v4_file.endswith('.txt'):
            continue
        changes = process_file(v4_file, force=force)
        if changes > 0:
            files_changed += 1
            total_changes += changes
            print(f"{v4_file}: {changes} verses redistributed")

    print(f"\n{'='*60}")
    print(f"Files changed: {files_changed}")
    print(f"Total verses redistributed: {total_changes}")


if __name__ == '__main__':
    main()
