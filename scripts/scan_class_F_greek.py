#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLASS F scanner (Greek): circumstantial participial adjunct possibly stranded
from its governing finite verb.

Adapted from parallel colometric work on archaic-English scripture text. In
that corpus, Class F (subject + participial adjunct) had the highest
false-positive rate under adversarial audit (~63%): circumstantial participles
routinely function as PROSODICALLY INDEPENDENT full predications, so merges
that are syntactically licensed still destroy the oral/rhetorical architecture
of the line.

Greek circumstantial participles have the same property — genitive absolutes,
scene-framing aorist participles, and nominative circumstantials carrying
distinct temporal beats all function as independent predications. See
handoffs §Goldilocks refinement (2026-04-13) and the Heb 1:3 tri-colon case
(sustaining / purifying / enthroning — NOT a main clause with two
subordinates).

OUTPUT POLICY
-------------
This scanner produces CANDIDATES ONLY. It does not merge, does not edit any
file, and does not claim any candidate is a genuine over-split. Every hit is
expected to pass through an adversarial audit agent that argues AGAINST the
merge using the subordinating-vs-coordinating (Goldilocks) diagnostic before
any edit is considered.

The scanner deliberately ERRS ON THE SIDE OF NOT FLAGGING:
  - Genitive absolutes are detected but marked HIGH-RISK (rarely legitimate merges).
  - Tri-colon / parallel-participial stacks are suppressed.
  - Participles with their own subject (functional absolutes) are suppressed.
  - Anything matching the Heb 1:3 coordinating shape is excluded.

USAGE
-----
    PYTHONIOENCODING=utf-8 py -3 scripts/scan_class_F_greek.py [--book heb]
                                                               [--limit N]
                                                               [--json PATH]
"""

import argparse
import glob
import json
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")

# ---------------------------------------------------------------------------
# Greek normalization + tokenizing
# ---------------------------------------------------------------------------

# Strip combining marks (accents, breathing, iota subscript) for pattern
# matching. We keep the original form for display.
_COMB_RE = re.compile(r"[\u0300-\u036f]")


def strip_accents(s):
    # Normalize to NFD, drop combining marks, recompose.
    nfd = unicodedata.normalize("NFD", s)
    bare = _COMB_RE.sub("", nfd)
    # Normalize final sigma to medial sigma for matching.
    return bare.replace("\u03c2", "\u03c3").lower()


GREEK_WORD_RE = re.compile(r"[\u0370-\u03ff\u1f00-\u1fff\u2019\u02bc']+")


def tokenize(line):
    return GREEK_WORD_RE.findall(line)


def bare_tokens(line):
    return [strip_accents(t) for t in tokenize(line)]


# ---------------------------------------------------------------------------
# Morphological shape detection (rule-based, accent-stripped)
# ---------------------------------------------------------------------------

# Participial endings (nominative, genitive, accusative, dative; masc/fem/neut;
# aorist/present/perfect/future active/middle/passive). This is a
# *shape-matcher*, not a lemmatizer — we accept some noise.
PARTICIPLE_ENDINGS = (
    # aor act masc/neut nom sg (λύσας, γνούς, λαβών)  NOTE accent stripped
    "σας", "σασα", "σαν",
    "ων", "ουσα", "ον",           # pres act masc/fem/neut nom sg
    "ωντες", "ουσαι", "οντα",      # pres act plural shapes
    "οντος", "ουσησ", "οντοσ",    # pres act genitives (accents stripped)
    "ων τοσ", "οντοσ",
    "αμενοσ", "αμενη", "αμενον",  # aor mid participle masc/fem/neut
    "αμενοι", "αμεναι", "αμενα",
    "αμενου", "αμενησ", "αμενοισ",
    "ομενοσ", "ομενη", "ομενον",  # pres mid/pass participle
    "ομενοι", "ομεναι", "ομενα",
    "ομενου", "ομενησ",
    "εισ", "εντοσ", "εντι", "εντα",  # aor pass (e.g. λυθείς)
    "θεισ", "θεντοσ", "θεντα", "θεντεσ", "θεντα",
    "θεισα", "θεισησ",
    "κωσ", "κοτοσ", "κοτα", "κοτεσ", "κοτι",  # perfect active (λελυκώς)
    "κυια", "κυιασ",
    "μενοσ", "μενη", "μενον",      # perfect mid/pass (λελυμένος)
    "μενοι", "μεναι", "μενα",
    "μενου", "μενησ", "μενοισ",
)

# High-signal circumstantial participle forms (classic scene-framing anchors).
# These are commonly used to open a circumstantial frame, so a line starting
# or ending with one is a strong Class F shape.
FRAMING_PARTICIPLES_BARE = {
    "λαβων", "λαβοντεσ", "λαβουσα",
    "γνουσ", "γνοντεσ",
    "ακουσασ", "ακουσαντεσ", "ακουσαντοσ",
    "ιδων", "ιδοντεσ", "ιδουσα",
    "ελθων", "ελθοντεσ", "ελθοντοσ", "ελθουσα",
    "απελθων", "εξελθων", "εισελθων", "προσελθων", "κατελθων",
    "αναστασ", "αναστασα",
    "καθισασ", "καθημενοσ",
    "ποιησασ", "ποιησαντεσ", "ποιησαμενοσ",
    "αποκριθεισ", "αποκριθεντεσ",
    "γενομενοσ", "γενομενη", "γενομενοι",
    "εγερθεισ",
    "στρεφομενοσ", "στραφεισ",
    "αρασ", "αραντεσ",
    "βαλων", "βαλοντεσ",
    "κρατησασ",
    "εμβασ",
    "προσκαλεσαμενοσ",
    "φερων", "φεροντεσ",
}

# Finite-verb endings (very rough — we accept false positives then filter
# by confirming the token is not also a participle shape).
FINITE_ENDINGS = (
    # present active / middle / passive
    "ω", "εισ", "ει", "ομεν", "ετε", "ουσι", "ουσιν",
    "ομαι", "ῃ", "εται", "ομεθα", "εσθε", "ονται",
    # imperfect
    "ον", "εσ", "ε", "ομεν", "ετε", "ον",
    "ομην", "ου", "ετο", "ομεθα", "εσθε", "οντο",
    # aorist active / middle / passive
    "σα", "σασ", "σε", "σεν", "σαμεν", "σατε", "σαν",
    "σαμην", "σω", "σατο", "σαμεθα", "σασθε", "σαντο",
    "θην", "θησ", "θη", "θημεν", "θητε", "θησαν",
    # perfect
    "κα", "κασ", "κεν", "καμεν", "κατε", "κασιν",
    # future
    "σω", "σεισ", "σει", "σομεν", "σετε", "σουσιν",
    "σομαι", "σῃ", "σεται",
)

# Core high-signal finite verbs frequently found as main verbs following a
# circumstantial participle (appearance is a red flag for a genuine strand).
COMMON_FINITE_MAIN_VERBS_BARE = {
    "ειπεν", "ελεγεν", "εφη", "απεκριθη",
    "εκαθισεν", "ανεστη", "απηλθεν", "ηλθεν", "εισηλθεν",
    "εβαλεν", "εδωκεν", "ελαβεν", "εποιησεν", "ειδεν",
    "εκρινεν", "απεκτεινεν", "εκραξεν",
    "προσηλθεν", "εξηλθεν", "κατεβη", "ανεβη",
    "εδιδασκεν", "ηρξατο",
}

# Coordinators / discourse markers that, when opening line N+1, suggest a
# COORDINATING (parallel, tri-colon) structure — suppress the candidate.
COORDINATING_OPENERS_BARE = {
    "και", "δε", "τε", "ουν", "αρα", "τοτε",
    "αλλα", "πλην", "ομωσ",
    # resumptive / fresh-subject NP openers handled below
}

# Subject pronouns / resumptives that signal a Goldilocks COORDINATE pickup:
# when line N+1 opens with one of these, the participle on line N is probably
# prosodically independent. Greek pronouns are sparse, so we use a narrow list.
RESUMPTIVE_SUBJECTS_BARE = {
    "αυτοσ", "αυτη", "αυτο",
    "εκεινοσ", "εκεινη", "εκεινο",
    "ουτοσ", "αυτη", "τουτο",
    "ο",  # definite article re-opening a NP (weak signal)
}

# Relative/complementizer starters that usually signal a distinct embedded
# clause and therefore suppress merge candidacy.
RELATIVE_COMPLEMENTIZERS_BARE = {
    "οσ", "η", "ο",
    "οστισ", "ητισ", "οτι",
    "ινα", "οπωσ", "ωστε",
    "οτε", "οταν", "επει", "επειδη",
    "εαν", "ει", "ωσ", "καθωσ",
    "γαρ",  # γάρ opens an explanation — parallel / coordinate
}

GENITIVE_PRONOUN_HINTS_BARE = {"αυτου", "αυτησ", "αυτων", "μου", "σου", "ημων", "υμων"}


# Exclusions: noun/adjective/article endings that superficially match
# participle shapes but are NOT verbal. Populated from corpus inspection.
NONVERBAL_EXCLUSIONS_BARE = {
    # articles / demonstratives / interrogatives
    "των", "ων", "ον", "τον", "τουτων", "τουτον",
    "αυτων", "εκεινων", "τινων", "παντων", "αλλων",
    "πολλων", "ιδιων",
    # common nouns with -ων / -ον / -ουσα / -ουσησ shape
    "ημερων", "ανθρωπων", "λογων", "εργων", "υιων", "θυσιων",
    "τοπον", "νομον", "λογον", "υιον", "θανατον", "χρονον",
    "βασιλεων", "αμαρτιων", "εντολων", "δικαιων",
    # feminine -ουσα nouns (very few but some; conservative exclusion)
}

# Endings that UNAMBIGUOUSLY mark verbal participles (not nouns).
STRONG_PARTICIPLE_ENDINGS = (
    "σασ", "σαντοσ", "σαντεσ", "σαντα",
    "αμενοσ", "αμενη", "αμενον", "αμενοι", "αμεναι",
    "ομενοσ", "ομενη", "ομενον", "ομενοι", "ομεναι",
    "μενοσ", "μενη", "μενοι", "μεναι",
    "θεισ", "θεντοσ", "θεντα", "θεντεσ", "θεισα",
    "κωσ", "κοτοσ", "κοτα", "κοτεσ", "κυια",
    "ουσα", "ουσησ",
    "γκασ", "γκοντα", "γκοντεσ",  # -εγκας type (προσενέγκας)
    "ψασ",  # -ψας type
    "ξασ",  # -ξας type
)


def looks_like_participle(bare):
    """Return True if the accent-stripped token appears to be a participle."""
    if bare in NONVERBAL_EXCLUSIONS_BARE:
        return False
    if bare in FRAMING_PARTICIPLES_BARE:
        return True
    # CRITICAL DISAMBIGUATION: 2sg aorist indicative (ἐμίσησας) has the same
    # surface as aor act masc sg participle (μισήσας). The augment ε-/η- at
    # the start marks the finite form. If augmented, treat as finite.
    if (bare.startswith("ε") or bare.startswith("η")) and bare.endswith("σασ"):
        return False
    # Strong endings: confident match.
    for end in STRONG_PARTICIPLE_ENDINGS:
        if bare.endswith(end) and len(bare) > len(end) + 1:
            return True
    return False


FINITE_AORIST_IMPERFECT_ENDINGS = (
    "σεν", "σαν", "σατο", "σαντο", "σαμην",
    "θη", "θησαν", "θημεν", "θητε",
    "ομην", "ετο", "οντο", "εσθε", "ομεθα",
    # 2sg aorist active: -σας on a verb (disambiguated from ptc masc sg -σασ
    # because our strip-accents normalizes final-sigma, so here we look for
    # verbs that begin with augment epsilon — e.g., ἐμίσησας, ἠθέλησας)
    # handled by the augment branch below.
)

# 2sg aorist active verbs with augment (epsilon or eta): εμισησας, ηθελησας.
# These are ambiguous with aorist active masc sg participle "-σας", but the
# participle form is already indexed — we use an augment-prefix heuristic.
FINITE_AUGMENT_2SG_ENDINGS = ("ησας", "ησασ")

FINITE_PRESENT_ENDINGS = (
    "ομεν", "ουσιν", "ουσι", "ετε", "εται", "ονται",
    "ομεθα", "εσθε", "ουμαι", "ουμεθα",
)

FINITE_PERFECT_ENDINGS = ("κεν", "κασιν", "κασι", "καμεν", "κατε", "κε")


def looks_like_finite(bare):
    """Crude finite-verb detector. Excludes participle shapes."""
    if bare in COMMON_FINITE_MAIN_VERBS_BARE:
        return True
    if looks_like_participle(bare):
        return False
    if len(bare) < 4:
        return False
    # Aorist/imperfect finite endings. Internal augments on compounds
    # (e.g., ὑπ-ή-κουσεν) mean we must NOT require an ε- prefix.
    for end in FINITE_AORIST_IMPERFECT_ENDINGS:
        if bare.endswith(end) and len(bare) > len(end) + 1:
            # Guard against -σαν overlapping with neut pl nouns: require
            # at least 5 chars and the char before -σ to be a vowel/consonant
            # consistent with a verb root.
            return True
    # Perfect endings.
    for end in FINITE_PERFECT_ENDINGS:
        if bare.endswith(end) and len(bare) > len(end) + 1:
            return True
    # Present 3pl / 1pl / 2pl that are distinctive.
    for end in FINITE_PRESENT_ENDINGS:
        if bare.endswith(end) and len(bare) > len(end) + 1:
            return True
    # Augmented 2sg aorist: ε-/η- prefix + -ησας  (ἐμίσησας, ἠθέλησας).
    if bare.startswith("ε") or bare.startswith("η"):
        for end in FINITE_AUGMENT_2SG_ENDINGS:
            if bare.endswith(end) and len(bare) > 4:
                return True
        # Common augmented imperfect/aorist tail: -εν, -ον on long stems.
        if len(bare) > 5:
            for end in ("εν", "ον"):
                if bare.endswith(end):
                    return True
    # Deponent / mid-pass 3sg present: "-εται" (e.g., επαισχυνεται, φαινεται)
    if bare.endswith("εται") and len(bare) > 6:
        return True
    # Common short present 3sg finites hard-coded (avoid broad "-ει" match).
    if bare in {"λεγει", "εστιν", "εστι", "εχει", "φησιν", "θελει",
                "δυναται", "γινωσκει", "ειδεν"}:
        return True
    return False


# ---------------------------------------------------------------------------
# Candidate detection
# ---------------------------------------------------------------------------

VERSE_RE = re.compile(r"^(\d+):(\d+)\s*$")


def read_chapter(path):
    """Return [(verse_ref, [lines...]), ...]."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().splitlines()
    blocks = []
    current = None
    current_lines = []
    for ln in raw:
        s = ln.rstrip()
        m = VERSE_RE.match(s.strip())
        if m:
            if current is not None:
                blocks.append((current, current_lines))
            current = s.strip()
            current_lines = []
        elif s.strip() == "":
            continue
        else:
            if current is not None:
                current_lines.append(s)
    if current is not None:
        blocks.append((current, current_lines))
    return blocks


def line_has_genitive_absolute(line):
    """Detect a likely genitive absolute: a genitive participle co-occurring
    with a genitive noun/pronoun on the same line.

    Accent-stripped heuristic. Genitive participle endings: -οντοσ, -ουσησ,
    -αντοσ, -σαντοσ, -μενου, -μενησ, -θεντοσ.
    """
    bares = bare_tokens(line)
    has_gen_ptc = False
    for b in bares:
        for end in ("οντοσ", "ουσησ", "αντοσ", "σαντοσ", "μενου", "μενησ",
                    "θεντοσ", "κοτοσ", "οντων", "ουσων", "μενων", "θεντων"):
            if b.endswith(end) and len(b) > len(end) + 1:
                has_gen_ptc = True
                break
        if has_gen_ptc:
            break
    if not has_gen_ptc:
        return False
    # Look for a genitive "subject" of the absolute: genitive pronoun, or a
    # genitive article (του/τησ/των) or common genitive ending.
    for b in bares:
        if b in GENITIVE_PRONOUN_HINTS_BARE:
            return True
        if b in ("του", "τησ", "των"):
            return True
        if b.endswith("ου") or b.endswith("ησ") or b.endswith("ων"):
            # crude but useful
            return True
    return True  # participle alone strongly suggests gen abs


def line_is_participle_dominant(line):
    """Does the line's 'head' verbal element look like a bare participial
    adjunct — a participle with NO finite verb on the same line?"""
    bares = bare_tokens(line)
    if not bares:
        return False
    has_ptc = any(looks_like_participle(b) for b in bares)
    has_fin = any(looks_like_finite(b) for b in bares)
    return has_ptc and not has_fin


def line_is_finite_dominant(line):
    """Does the line contain a finite verb (i.e., a main clause beat)?"""
    bares = bare_tokens(line)
    return any(looks_like_finite(b) for b in bares)


def first_bare(line):
    bs = bare_tokens(line)
    return bs[0] if bs else ""


def last_bare(line):
    bs = bare_tokens(line)
    return bs[-1] if bs else ""


def goldilocks_suppress(line_N, line_Nplus1):
    """Return (True, reason) if the candidate should be SUPPRESSED because it
    matches a coordinating/parallel pattern rather than a subordinating one.

    This is the load-bearing filter. When in doubt, suppress.
    """
    bN = bare_tokens(line_N)
    bN1 = bare_tokens(line_Nplus1)
    if not bN or not bN1:
        return True, "empty-line"

    first_N1 = bN1[0]

    # 1. Genitive absolute on line N → almost always a scene-frame, independent
    #    predication. Suppress.
    if line_has_genitive_absolute(line_N):
        return True, "genitive-absolute (independent predication)"

    # 2. Line N+1 opens with a coordinator / discourse pivot → coordinate
    #    chain (Heb 1:3 shape, tri-cola, καί-linked parallel participles).
    if first_N1 in COORDINATING_OPENERS_BARE:
        return True, "N+1 opens with coordinator/discourse pivot (%s)" % first_N1

    # 3. Line N+1 opens with a relative / complementizer / subordinator → a
    #    distinct embedded clause, not a main-verb pickup.
    if first_N1 in RELATIVE_COMPLEMENTIZERS_BARE:
        return True, "N+1 opens with relative/complementizer (%s)" % first_N1

    # 4. Line N+1 opens with a resumptive subject pronoun → prosodically
    #    independent main clause (coordinate pickup).
    if first_N1 in RESUMPTIVE_SUBJECTS_BARE:
        return True, "N+1 opens with resumptive subject (%s)" % first_N1

    # 5. Line N is also a participle (tri-colon / participle stack). Suppress.
    if line_is_participle_dominant(line_Nplus1):
        return True, "N+1 is itself participle-dominant (participle stack)"

    # 6. Line N has a vocative-only shape (κύριε, αδελφοι, etc.) → not Class F.
    vocative_bares = {"κυριε", "αδελφοι", "παιδια", "τεκνα", "τεκνον"}
    if any(b in vocative_bares for b in bN):
        return True, "vocative on line N"

    # 7. Speech-introduction marker on N+1 (λέγει, ἔφη, εἶπεν...) when N is a
    #    framing participle — classic ἀποκριθεὶς εἶπεν type. This IS the
    #    canonical "speech intro gets its own line" pattern codified by the
    #    methodology; never a Class F merge target.
    speech_verbs_bare = {"λεγει", "εφη", "ειπεν", "ελεγεν", "απεκριθη",
                         "αποκρινεται", "φησιν"}
    if first_N1 in speech_verbs_bare or (len(bN1) >= 2 and bN1[1] in speech_verbs_bare):
        return True, "speech-intro on N+1 (methodology: stays split)"

    return False, ""


def classify_candidate(line_N, line_Nplus1):
    """Identify WHICH Class F subtype this candidate is.

    Returns (subtype, risk_level) or None if not a candidate.

    Subtypes:
      - ptc-N_then_finite-N1: bare participial line followed by a finite line
      - finite-N_then_ptc-N1: finite line followed by a bare participial
    Risk levels: "low" / "medium" / "high" (higher = more likely FP).
    """
    ptc_N = line_is_participle_dominant(line_N)
    fin_N = line_is_finite_dominant(line_N)
    ptc_N1 = line_is_participle_dominant(line_Nplus1)
    fin_N1 = line_is_finite_dominant(line_Nplus1)

    # Participial line N → finite line N+1 (canonical strand shape).
    if ptc_N and fin_N1 and not fin_N:
        # Framing-participle head → stronger candidate.
        head_bare = bare_tokens(line_N)
        has_framing = any(b in FRAMING_PARTICIPLES_BARE for b in head_bare)
        return ("ptc-then-finite", "medium" if has_framing else "low")

    # Finite line N → bare participial line N+1 (trailing adjunct).
    if fin_N and ptc_N1 and not fin_N1:
        return ("finite-then-ptc", "low")

    return None


def scan_chapter(path):
    """Return list of candidate dicts for a single chapter file."""
    candidates = []
    book = os.path.basename(os.path.dirname(path))
    chapter_file = os.path.basename(path)
    blocks = read_chapter(path)
    for verse_ref, lines in blocks:
        # Within-verse adjacent pairs only. We explicitly do NOT cross verse
        # boundaries — prosodic structure respects verses as a scaffold.
        for j in range(len(lines) - 1):
            L = lines[j]
            Ln = lines[j + 1]
            cls = classify_candidate(L, Ln)
            if cls is None:
                continue
            subtype, risk = cls
            suppress, reason = goldilocks_suppress(L, Ln)
            if suppress:
                continue
            candidates.append({
                "book": book,
                "file": chapter_file,
                "verse": verse_ref,
                "subtype": subtype,
                "risk": risk,
                "line_N": L,
                "line_N_plus_1": Ln,
                "proposed_merge": L + " " + Ln,
                "note": "candidate only — run adversarial audit before merging",
            })
    return candidates


def scan_book(book_dir):
    cands = []
    for path in sorted(glob.glob(os.path.join(book_dir, "*.txt"))):
        cands.extend(scan_chapter(path))
    return cands


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--book", default=None,
                    help="Book slug (e.g. 'heb', '06-rom'). Default: Hebrews sample.")
    ap.add_argument("--limit", type=int, default=40,
                    help="Max candidates to print (default 40).")
    ap.add_argument("--json", default=None,
                    help="Optional path to write full candidate list as JSON.")
    args = ap.parse_args()

    # Resolve book dir.
    if args.book is None:
        book_dirs = [os.path.join(V4_DIR, "19-heb")]
    else:
        slug = args.book.lower()
        matches = [d for d in glob.glob(os.path.join(V4_DIR, "*"))
                   if os.path.isdir(d) and slug in os.path.basename(d).lower()]
        if not matches:
            print("No book directory matches %r" % slug, file=sys.stderr)
            sys.exit(2)
        book_dirs = matches

    all_cands = []
    for bd in book_dirs:
        all_cands.extend(scan_book(bd))

    # Report.
    print("=" * 72)
    print("CLASS F (Greek) — circumstantial participial adjunct candidates")
    print("=" * 72)
    print("Books scanned: %s" % ", ".join(os.path.basename(d) for d in book_dirs))
    print("Total candidates: %d" % len(all_cands))
    by_subtype = {}
    by_risk = {}
    for c in all_cands:
        by_subtype[c["subtype"]] = by_subtype.get(c["subtype"], 0) + 1
        by_risk[c["risk"]] = by_risk.get(c["risk"], 0) + 1
    print("By subtype: %s" % by_subtype)
    print("By risk   : %s" % by_risk)
    print("")
    print("NOTE: these are CANDIDATES ONLY. Do not merge without adversarial")
    print("audit. In parallel colometric work, ~63%% of Class F proposals were")
    print("false positives (coordinate structures, not subordinate ones).")
    print("")
    print("-" * 72)
    print("First %d candidates:" % min(args.limit, len(all_cands)))
    print("-" * 72)
    for i, c in enumerate(all_cands[: args.limit], 1):
        print("")
        print("[%02d] %s  %s  %s  (%s / risk=%s)"
              % (i, c["book"], c["file"], c["verse"], c["subtype"], c["risk"]))
        print("   N  : " + c["line_N"])
        print("   N+1: " + c["line_N_plus_1"])

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(all_cands, f, ensure_ascii=False, indent=2)
        print("")
        print("Wrote %d candidates to %s" % (len(all_cands), args.json))


if __name__ == "__main__":
    main()
