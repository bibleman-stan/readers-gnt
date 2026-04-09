"""
macula_valency.py — Verb valency satisfaction check using Macula Greek role annotations.

Determines whether a colometric line contains a participle whose grammatical
valency (transitivity) is unsatisfied — i.e., the participle's Macula clause
assigns an object (role=o) to a word that is NOT on the same line. Such lines
represent incomplete thoughts and should be merged forward.

Usage:
    from macula_valency import check_line_valency, ValencyResult

    result = check_line_valency("ἀκούσας δὲ", "matt", 2, 3)
    if result.unsatisfied:
        print(f"Merge: {result.reason}")
"""

import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Path and book mappings — reuse from macula_clauses.py
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_LOWFAT_DIR = os.path.join(_REPO_ROOT, "research", "macula-greek", "SBLGNT", "lowfat")

_SLUG_TO_MACULA = {
    "matt": "MAT", "mark": "MRK", "luke": "LUK", "john": "JHN",
    "acts": "ACT", "rom": "ROM", "1cor": "1CO", "2cor": "2CO",
    "gal": "GAL", "eph": "EPH", "phil": "PHP", "col": "COL",
    "1thess": "1TH", "2thess": "2TH", "1tim": "1TI", "2tim": "2TI",
    "titus": "TIT", "phlm": "PHM", "heb": "HEB", "jas": "JAS",
    "1pet": "1PE", "2pet": "2PE", "1john": "1JN", "2john": "2JN",
    "3john": "3JN", "jude": "JUD", "rev": "REV",
}

_MACULA_TO_FILE = {
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
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MaculaWord:
    """A word from the Macula XML with role and clause info."""
    ref: str           # e.g. "MAT 2:3!1"
    word_pos: int      # the !N position within the verse
    normalized: str    # normalized form from Macula
    role: str          # role within its clause: s, v, o, o2, io, p, adv, vc, or ''
    mood: str          # participle, indicative, infinitive, etc.
    voice: str         # active, passive, middle, etc.
    word_class: str    # noun, verb, conj, etc.
    clause_id: int     # id() of the innermost enclosing <wg class="cl">


@dataclass
class ClauseRoles:
    """Role summary for a single clause."""
    clause_id: int
    has_object: bool = False        # any child with role=o or role=o2
    has_subject: bool = False       # any child with role=s
    has_finite_verb: bool = False   # any word with finite mood (indicative, subjunctive, etc.)
    object_word_refs: list = field(default_factory=list)   # refs of object words
    subject_word_refs: list = field(default_factory=list)  # refs of subject words
    participle_refs: list = field(default_factory=list)    # refs of participle words


@dataclass
class ValencyResult:
    """Result of a valency check for a single line."""
    unsatisfied: bool = False
    reason: str = ""
    participle_text: str = ""
    missing_role: str = ""  # 'o' for object, 's' for subject


# ---------------------------------------------------------------------------
# Text normalization for matching
# ---------------------------------------------------------------------------

# Characters to strip when comparing words
_STRIP_CHARS = str.maketrans('', '', '.,;·\u0387\u00B7\u2019\u02BC')


def _normalize_for_match(text: str) -> str:
    """Normalize a Greek word for matching between our text and Macula.

    Strips punctuation, apostrophes, and normalizes unicode.
    """
    text = unicodedata.normalize('NFC', text)
    text = text.translate(_STRIP_CHARS)
    # Also strip the modifier letter apostrophe and right single quote
    text = text.replace('\u02bc', '').replace('\u2019', '')
    text = text.replace('\u02bd', '').replace('\u1fbd', '')
    # Strip ASCII apostrophe and prime
    text = text.replace("'", '').replace('\u2032', '')
    # Strip the combining comma above (smooth breathing sometimes encoded differently)
    return text.strip()


# ---------------------------------------------------------------------------
# Book-level parsing with cache
# ---------------------------------------------------------------------------

_book_cache: dict[str, dict[tuple[int, int], list[MaculaWord]]] = {}
_clause_roles_cache: dict[str, dict[int, ClauseRoles]] = {}

_REF_PATTERN = re.compile(r'^(\w+)\s+(\d+):(\d+)!(\d+)$')


def _parse_ref(ref_str):
    """Parse 'ACT 1:1!8' -> (book, chapter, verse, word_pos)."""
    m = _REF_PATTERN.match(ref_str)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    return None, None, None, None


def _parse_book_valency(macula_id: str):
    """Parse a book XML and extract per-verse word lists with role annotations.

    Populates both _book_cache and _clause_roles_cache.
    """
    if macula_id in _book_cache:
        return

    filename = _MACULA_TO_FILE.get(macula_id)
    if not filename:
        return

    filepath = os.path.join(_LOWFAT_DIR, filename)
    if not os.path.exists(filepath):
        return

    tree = ET.parse(filepath)
    root = tree.getroot()

    # Walk the tree to assign each <w> its innermost clause
    verse_words: dict[tuple[int, int], list[MaculaWord]] = {}
    clause_roles: dict[int, ClauseRoles] = {}

    def walk(elem, clause_stack):
        is_clause = (elem.tag == 'wg' and elem.get('class') == 'cl')

        if is_clause:
            clause_stack.append(elem)

        if elem.tag == 'w':
            ref = elem.get('ref', '')
            _, ch, vs, pos = _parse_ref(ref)
            if ch is None:
                if is_clause:
                    clause_stack.pop()
                return

            innermost_cl = clause_stack[-1] if clause_stack else None
            cl_id = id(innermost_cl) if innermost_cl is not None else 0

            mw = MaculaWord(
                ref=ref,
                word_pos=pos or 0,
                normalized=elem.get('normalized', '') or (elem.text or ''),
                role=elem.get('role', ''),
                mood=elem.get('mood', ''),
                voice=elem.get('voice', ''),
                word_class=elem.get('class', ''),
                clause_id=cl_id,
            )

            key = (ch, vs)
            if key not in verse_words:
                verse_words[key] = []
            verse_words[key].append(mw)

            # Also track roles at clause level
            # But roles come from DIRECT children of the clause, not deep descendants.
            # We need to check: is this <w> a direct child of the innermost clause?
            # OR: is this <w> inside a <wg role="o"> that is a direct child?
            # The approach: track roles from direct children of each clause separately.

        else:
            for child in elem:
                walk(child, clause_stack)

        if is_clause:
            clause_stack.pop()

    # First pass: collect words with their innermost clause
    walk(root, [])

    # Second pass: build clause roles from direct children of clauses
    # This requires walking the tree again, looking at direct children of <wg class="cl">
    def build_clause_roles(elem):
        is_clause = (elem.tag == 'wg' and elem.get('class') == 'cl')

        if is_clause:
            cl_id = id(elem)
            if cl_id not in clause_roles:
                clause_roles[cl_id] = ClauseRoles(clause_id=cl_id)
            cr = clause_roles[cl_id]

            # Check direct children for roles
            for child in elem:
                role = child.get('role', '')
                if child.tag == 'w':
                    ref = child.get('ref', '')
                    mood = child.get('mood', '')
                    if role in ('o', 'o2'):
                        cr.has_object = True
                        cr.object_word_refs.append(ref)
                    if role == 's':
                        cr.has_subject = True
                        cr.subject_word_refs.append(ref)
                    if mood == 'participle':
                        cr.participle_refs.append(ref)
                    if mood in ('indicative', 'subjunctive', 'imperative', 'optative'):
                        cr.has_finite_verb = True

                elif child.tag == 'wg':
                    # A word group with a role — collect all word refs within it
                    wg_role = child.get('role', '')
                    wg_class = child.get('class', '')
                    sub_refs = [w.get('ref', '') for w in child.iter('w')]

                    if wg_role in ('o', 'o2'):
                        cr.has_object = True
                        cr.object_word_refs.extend(sub_refs)
                    if wg_role == 's':
                        cr.has_subject = True
                        cr.subject_word_refs.extend(sub_refs)

                    # Check for participles in this word group
                    # (but only if the wg itself has role=v or the wg is a sub-clause)
                    if wg_class == 'cl':
                        # Sub-clause — its participles belong to the sub-clause, not this one
                        pass
                    else:
                        for w in child.iter('w'):
                            if w.get('mood') == 'participle' and w.get('role') == 'v':
                                cr.participle_refs.append(w.get('ref', ''))
                            if w.get('mood') in ('indicative', 'subjunctive', 'imperative', 'optative'):
                                cr.has_finite_verb = True

        # Recurse into all children
        for child in elem:
            build_clause_roles(child)

    build_clause_roles(root)

    # Sort verse words by word_pos
    for key in verse_words:
        verse_words[key].sort(key=lambda mw: mw.word_pos)

    _book_cache[macula_id] = verse_words
    _clause_roles_cache[macula_id] = clause_roles


# ---------------------------------------------------------------------------
# Word matching: align line words to Macula words within a verse
# ---------------------------------------------------------------------------

def _match_line_words_to_macula(line_text: str, verse_words: list[MaculaWord]) -> list[Optional[MaculaWord]]:
    """Match words in a line to Macula words in the verse by sequential matching.

    Returns a list parallel to the words in line_text, where each element is
    either a MaculaWord or None if no match was found.
    """
    line_words = line_text.split()
    if not line_words or not verse_words:
        return [None] * len(line_words)

    # Normalize both sides
    line_norms = [_normalize_for_match(w) for w in line_words]
    macula_norms = [_normalize_for_match(mw.normalized) for mw in verse_words]

    # Greedy sequential match: for each line word, find the first unmatched
    # Macula word that matches
    result = [None] * len(line_words)
    used = [False] * len(verse_words)

    for i, ln in enumerate(line_norms):
        if not ln:
            continue
        for j, mn in enumerate(macula_norms):
            if not used[j] and ln == mn:
                result[i] = verse_words[j]
                used[j] = True
                break

    return result


# ---------------------------------------------------------------------------
# Core valency check
# ---------------------------------------------------------------------------

def check_line_valency(
    line_text: str,
    book_slug: str,
    chapter: int,
    verse: int,
) -> ValencyResult:
    """Check if a line contains a participle with unsatisfied valency.

    Args:
        line_text: The colometric line text (Greek).
        book_slug: Project slug (e.g., 'matt', 'mark').
        chapter: Chapter number.
        verse: Verse number.

    Returns:
        ValencyResult with unsatisfied=True if the line should be merged.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return ValencyResult()

    _parse_book_valency(macula_id)

    verse_words = _book_cache.get(macula_id, {}).get((chapter, verse), [])
    clause_roles = _clause_roles_cache.get(macula_id, {})

    if not verse_words:
        return ValencyResult()

    # Match line words to Macula words
    matched = _match_line_words_to_macula(line_text, verse_words)

    # Collect refs of words on this line
    line_refs = set()
    for mw in matched:
        if mw is not None:
            line_refs.add(mw.ref)

    # Find all verbal elements on this line (participles AND finite verbs)
    verbs_on_line = []
    for mw in matched:
        if mw is not None and mw.role == 'v':
            verbs_on_line.append(mw)

    if not verbs_on_line:
        return ValencyResult()

    # Check each verb's clause for unsatisfied valency
    for verb in verbs_on_line:
        # Skip passive participles — the patient IS the subject, no object needed
        if verb.mood == 'participle' and verb.voice == 'passive':
            continue

        cl_id = verb.clause_id
        cr = clause_roles.get(cl_id)
        if cr is None:
            continue

        # Check object valency: clause has object but object is not on this line
        if cr.has_object:
            obj_refs_on_line = line_refs.intersection(cr.object_word_refs)
            if not obj_refs_on_line:
                return ValencyResult(
                    unsatisfied=True,
                    reason=f"verb '{verb.normalized}' (clause has object not on this line)",
                    participle_text=verb.normalized,
                    missing_role='o',
                )

        # Check for infinitive complement: if the clause has another verb
        # (e.g., an infinitive) that is NOT on this line, the finite verb's
        # complement is missing. This catches δοκέω + infinitive, etc.
        clause_verb_refs = set(cr.participle_refs)  # participle_refs includes all role=v
        # Get ALL role=v refs in this clause from verse_words
        all_clause_verb_refs = set()
        for vw in verse_words:
            if vw.clause_id == cl_id and vw.role == 'v':
                all_clause_verb_refs.add(vw.ref)
        other_verb_refs = all_clause_verb_refs - line_refs
        if other_verb_refs and len(all_clause_verb_refs) > 1:
            # The clause has verb(s) not on this line — check if this line's
            # verb is a finite verb and the missing verb is an infinitive
            verbs_here = [vw for vw in verse_words if vw.ref in line_refs and vw.role == 'v']
            verbs_elsewhere = [vw for vw in verse_words if vw.ref in other_verb_refs]
            has_finite_here = any(v.mood in ('indicative', 'subjunctive', 'imperative', 'optative')
                                 for v in verbs_here)
            has_inf_elsewhere = any(v.mood == 'infinitive' for v in verbs_elsewhere)
            if has_finite_here and has_inf_elsewhere:
                return ValencyResult(
                    unsatisfied=True,
                    reason=f"verb '{verb.normalized}' (infinitive complement not on this line)",
                    participle_text=verb.normalized,
                    missing_role='v',
                )

        # Check subject valency for participles (only if clause has no finite verb)
        if verb.mood == 'participle' and cr.has_subject and not cr.has_finite_verb:
            subj_refs_on_line = line_refs.intersection(cr.subject_word_refs)
            if not subj_refs_on_line:
                return ValencyResult(
                    unsatisfied=True,
                    reason=f"participle '{verb.normalized}' (clause has subject not on this line)",
                    participle_text=verb.normalized,
                    missing_role='s',
                )

    return ValencyResult()


def line_has_unsatisfied_valency(line_text: str, book_slug: str,
                                  chapter: int, verse: int) -> bool:
    """Convenience wrapper: returns True if the line should be merged."""
    return check_line_valency(line_text, book_slug, chapter, verse).unsatisfied


@dataclass
class StrandedVerbResult:
    """Result of a stranded finite verb check."""
    stranded: bool = False
    reason: str = ""
    verb_text: str = ""
    merge_direction: str = ""  # 'forward', 'backward', or ''
    missing_roles: list = field(default_factory=list)  # list of missing role types


def check_stranded_finite_verb(
    line_text: str,
    prev_line: str,
    next_line: str,
    book_slug: str,
    chapter: int,
    verse: int,
) -> StrandedVerbResult:
    """Check if a line contains a stranded finite verb separated from its arguments.

    A finite verb is 'stranded' when:
      1. The line contains only the verb (single-word) or the verb + a particle/conjunction
      2. The verb's Macula clause has arguments (role=o, role=s) on other lines
      3. Those arguments appear on an adjacent line

    Returns StrandedVerbResult with merge direction if stranded.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug.lower())
    if not macula_id:
        return StrandedVerbResult()

    _parse_book_valency(macula_id)

    verse_words = _book_cache.get(macula_id, {}).get((chapter, verse), [])
    clause_roles = _clause_roles_cache.get(macula_id, {})

    if not verse_words:
        return StrandedVerbResult()

    # Match line words to Macula words
    matched = _match_line_words_to_macula(line_text, verse_words)
    line_refs = set(mw.ref for mw in matched if mw is not None)

    # Find finite verbs on this line
    finite_verbs = []
    for mw in matched:
        if mw is not None and mw.mood in ('indicative', 'subjunctive', 'optative'):
            finite_verbs.append(mw)

    if not finite_verbs:
        return StrandedVerbResult()

    # Check each finite verb's clause for missing arguments
    for verb in finite_verbs:
        cl_id = verb.clause_id
        cr = clause_roles.get(cl_id)
        if cr is None:
            continue

        missing_roles = []

        # Check if clause has object not on this line
        if cr.has_object:
            obj_on_line = line_refs.intersection(cr.object_word_refs)
            if not obj_on_line:
                missing_roles.append('o')

        # Check if clause has subject not on this line
        if cr.has_subject:
            subj_on_line = line_refs.intersection(cr.subject_word_refs)
            if not subj_on_line:
                missing_roles.append('s')

        if not missing_roles:
            continue

        # Determine merge direction: check which adjacent line has the missing arguments
        # Match prev and next lines to the same verse
        forward_has_args = False
        backward_has_args = False

        if next_line:
            next_matched = _match_line_words_to_macula(next_line, verse_words)
            next_refs = set(mw.ref for mw in next_matched if mw is not None)
            if 'o' in missing_roles and next_refs.intersection(cr.object_word_refs):
                forward_has_args = True
            if 's' in missing_roles and next_refs.intersection(cr.subject_word_refs):
                forward_has_args = True

        if prev_line:
            prev_matched = _match_line_words_to_macula(prev_line, verse_words)
            prev_refs = set(mw.ref for mw in prev_matched if mw is not None)
            if 'o' in missing_roles and prev_refs.intersection(cr.object_word_refs):
                backward_has_args = True
            if 's' in missing_roles and prev_refs.intersection(cr.subject_word_refs):
                backward_has_args = True

        if forward_has_args or backward_has_args:
            # Prefer backward merge if arguments precede the verb (e.g., object before verb)
            # Prefer forward merge if arguments follow the verb
            if backward_has_args and not forward_has_args:
                direction = 'backward'
            elif forward_has_args and not backward_has_args:
                direction = 'forward'
            else:
                # Both directions have args — prefer forward (more common in Greek VSO order)
                direction = 'forward'

            return StrandedVerbResult(
                stranded=True,
                reason=f"finite verb '{verb.normalized}' missing {missing_roles} on adjacent line ({direction})",
                verb_text=verb.normalized,
                merge_direction=direction,
                missing_roles=missing_roles,
            )

    return StrandedVerbResult()


def line_has_predicate_role(line_text: str, book_slug: str,
                            chapter: int, verse: int) -> bool:
    """Check if a line contains a word with Macula role=p (predicate).

    A line with a predicate adjective/noun has an implied copula (εἰμί)
    and constitutes a complete thought — a verbless predication. Common
    in Pauline style. Such lines should NOT be merged by the verbless rule.
    """
    macula_id = _SLUG_TO_MACULA.get(book_slug)
    if not macula_id:
        return False

    if macula_id not in _book_cache:
        _parse_book_valency(macula_id)
    verse_words = _book_cache.get(macula_id, {}).get((chapter, verse), [])
    if not verse_words:
        return False

    matched = _match_line_words_to_macula(line_text, verse_words)
    return any(mw is not None and mw.role == 'p' for mw in matched)


# ---------------------------------------------------------------------------
# CLI for testing
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    test_cases = [
        ("ἀκούσας δὲ", "matt", 2, 3, "should be intransitive (no object in clause) → KEEP"),
        ("ὁ βασιλεὺς Ἡρῴδης ἐταράχθη", "matt", 2, 3, "finite verb → KEEP"),
        ("Καὶ ὑμνήσαντες", "mark", 14, 26, "intransitive ptc → KEEP"),
        ("καὶ ταῦτα εἰπὼν", "acts", 1, 9, "object on line → KEEP"),
        ("πυρέσσουσα,", "mark", 1, 30, "intransitive ptc → KEEP"),
        ("φυλασσόμενος,", "luke", 8, 29, "passive ptc → KEEP"),
        ("καθίσας δὲ", "luke", 5, 3, "check transitivity"),
        ("καὶ συναγαγὼν πάντας τοὺς ἀρχιερεῖς καὶ γραμματεῖς τοῦ λαοῦ", "matt", 2, 4, "object on line → KEEP"),
        ("καὶ πέμψας αὐτοὺς εἰς Βηθλέεμ", "matt", 2, 8, "object on line → KEEP"),
    ]

    print("Valency check test results:\n")
    for line, book, ch, vs, expected in test_cases:
        result = check_line_valency(line, book, ch, vs)
        status = "MERGE" if result.unsatisfied else "KEEP"
        reason = f" — {result.reason}" if result.reason else ""
        print(f"  {book.title()} {ch}:{vs}  [{status}]  '{line}'")
        print(f"    Expected: {expected}")
        if reason:
            print(f"    Reason: {reason}")
        print()
