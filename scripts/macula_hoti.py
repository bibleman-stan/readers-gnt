"""Macula-sourced ὅτι bind/stand decisions for the GNT engine.

Per atu-method framework §2.1 (2026-05-26): a ὅτι-clause BINDS iff it is a
COMPLEMENT (Macula `rule="that-VP"`) with a SHARED deictic center; it STANDS iff
  (a) causal/adverbial  — Macula `rule="sub-CL"`, or the wrapper `role="adv"`, OR
  (b) a re-performed direct-discourse utterance with its OWN deictic center —
      a 2nd-person address inside the complement, or a 1st-SINGULAR speaker whose
      referent is not the matrix subject (a new speaker).
Quote-status has no independent force; the bidirectional ATU test decides, and the
discriminating features are sourced MECHANICALLY from the Macula treebank (not lemma
lists). `(chap, verse, wi)` align 1:1 with the engine's sblgnt-lowfat osisId indices
(verified 2026-05-26: 0 count- and 0 index-mismatches across all 14 ὅτι-bearing books).
"""
import xml.etree.ElementTree as ET
from pathlib import Path

MAC = Path(r"C:\Users\bibleman\repos\readers-gnt\research\macula-greek\SBLGNT\lowfat")
_CACHE = {}


def _innermost_cl(w, parent):
    """The IMMEDIATE <wg> wrapper enclosing the ὅτι — the node carrying the clause
    role/rule (that-VP / sub-CL / role=adv). Its `class` is typically empty; the
    `class='cl'` node sits one level out. Return the first <wg> ancestor bearing a
    `rule`/`role`, falling back to the first <wg> ancestor."""
    n, first_wg = w, None
    while n in parent:
        n = parent[n]
        if n.tag == "wg":
            if first_wg is None:
                first_wg = n
            if n.attrib.get("rule") or n.attrib.get("role"):
                return n
        if n.tag == "sentence":
            break
    return first_wg


def _enclosing_cl(hoti_cl, parent):
    """The governing (matrix) clause: nearest ancestor `<wg class='cl'>`."""
    n = hoti_cl
    while n in parent:
        n = parent[n]
        if n.tag == "wg" and n.attrib.get("class") == "cl":
            return n
        if n.tag == "sentence":
            break
    return None


def _matrix_subject_ids(enclosing_cl, wrapper):
    """Referent ids of the matrix subject: subjref of the governing finite verb in the
    enclosing cl, taking only words NOT inside the complement wrapper."""
    ids = set()
    if enclosing_cl is None:
        return ids
    wrapper_words = {id(w) for w in wrapper.iter("w")} if wrapper is not None else set()
    for w in enclosing_cl.iter("w"):
        if id(w) in wrapper_words:
            continue
        if w.attrib.get("class") == "verb" and w.attrib.get("subjref"):
            ids.update(w.attrib["subjref"].split())
    return ids


def _matrix_is_commanded_speech(enclosing_cl, wrapper):
    """True iff the matrix governing verb is an IMPERATIVE verb of COMMUNICATION
    (Louw-Nida domain 33: 'Εἴπατε ὅτι …', 'λεγέτω ὅτι …') — a COMMANDED utterance whose
    ὅτι introduces a re-performed direct quote (the commanded words), not an indirect
    complement. Restricted to LN domain 33 (speech): an imperative COGNITION/perception
    verb ('γινώσκετε ὅτι …' = 'know that X', domain 28/32; 'ἴδε ὅτι …') still BINDS its
    content complement — only commanded SAYING produces a standing quote. Macula tags
    both `that-VP`, and person-deixis alone misses the speech case (the quote may be
    3rd-person), so the imperative mood + communication-domain is the discriminator."""
    if enclosing_cl is None:
        return False
    wrapper_words = {id(w) for w in wrapper.iter("w")} if wrapper is not None else set()
    return any(w.attrib.get("class") == "verb" and w.attrib.get("mood") == "imperative"
               and (w.attrib.get("domain") or "").startswith("033")
               and id(w) not in wrapper_words for w in enclosing_cl.iter("w"))


def _complement_is_directive(hoti_cl):
    """True iff the complement is itself a re-performed DIRECTIVE — it carries an
    imperative-mood verb or a hortatory δεῦτε (e.g. Mark 12:7 'δεῦτε ἀποκτείνωμεν',
    2Thess 3:10 'μηδὲ ἐσθιέτω'). A directive utterance has its own deictic center →
    direct discourse → STAND, even when its person-deixis matches the matrix."""
    for w in hoti_cl.iter("w"):
        if w.attrib.get("class") == "verb" and w.attrib.get("mood") == "imperative":
            return True
        if w.attrib.get("lemma") == "δεῦτε":
            return True
    return False


def _deixis_anchors(hoti_cl):
    """1st/2nd-person deictic anchors inside the complement: (person, number, ids).
    Verbs carry `person` (subject id = subjref); personal pronouns carry no person in
    Macula lowfat (infer from lemma ἐγώ/σύ; antecedent id = referent)."""
    anchors = []
    for w in hoti_cl.iter("w"):
        number = w.attrib.get("number") or ""
        if w.attrib.get("class") == "verb":
            person = w.attrib.get("person")
            if person in ("first", "second"):
                anchors.append((person, number, set((w.attrib.get("subjref") or "").split())))
        if w.attrib.get("type") == "personal":
            person = {"ἐγώ": "first", "σύ": "second"}.get(w.attrib.get("lemma"))
            if person:
                anchors.append((person, number, set((w.attrib.get("referent") or "").split())))
    return anchors


def _classify(w, parent):
    cl = _innermost_cl(w, parent)
    if cl is None:
        return "STAND"
    rule, role = cl.attrib.get("rule", ""), cl.attrib.get("role", "")
    if rule == "sub-CL" or role == "adv":       # causal / adverbial
        return "STAND"
    if rule != "that-VP":                        # not a marked complement
        return "STAND"
    enclosing = _enclosing_cl(cl, parent)
    # Commanded / re-performed DIRECTIVE = direct discourse -> STAND (person-deixis
    # alone misses these: an imperative matrix, or an imperative/hortatory complement).
    if _matrix_is_commanded_speech(enclosing, cl) or _complement_is_directive(cl):
        return "STAND"
    matrix_ids = _matrix_subject_ids(enclosing, cl)
    for person, number, ids in _deixis_anchors(cl):
        if person == "second":                   # an addressee = re-performed utterance
            return "STAND"
        if person == "first" and number == "singular" and ids and not (ids & matrix_ids):
            return "STAND"                        # a new 1st-singular speaker
    return "BIND"                                 # shared-deixis indirect complement


def decisions(nn):
    """nn = 2-digit book-number string ('01'..'27'). Returns
    {(chap, verse, wi): 'BIND'|'STAND'} for every ὅτι in the book. Cached."""
    if nn in _CACHE:
        return _CACHE[nn]
    root = ET.parse(next(MAC.glob(f"{nn}-*.xml"))).getroot()
    parent = {c: p for p in root.iter() for c in p}
    out = {}
    for w in root.iter("w"):
        if w.attrib.get("lemma") != "ὅτι":
            continue
        ref = w.attrib.get("ref", "")
        if "!" not in ref:
            continue
        cv, wi = ref.split(" ", 1)[1].split("!")
        c, v = cv.split(":")
        out[(int(c), int(v), int(wi))] = _classify(w, parent)
    _CACHE[nn] = out
    return out
