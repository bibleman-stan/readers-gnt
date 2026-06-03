#!/usr/bin/env python3
"""SBLGNT-native generator: clause-atoms from our fabric (gnt_v1_sblgnt) ->
ported v1.5 binding rules -> v1.5/grk emitted DIRECTLY from osisId verse+position.
No PROIEL, no reconciler. The rules are the same ones validated on PROIEL; only
the substrate changed.

Usage: cd /c/tmp && PYTHONIOENCODING=utf-8 python gnt_generate_sblgnt.py Matt 2
"""
import sys
import unicodedata
from pathlib import Path
import sblgnt_v1_fabric as V1
import macula_hoti
import gnt_overrides

# Reverse map: 2-digit book index ("01" -> "Matt", "23" -> "1John"). Used to
# derive the override-key book label inside emit_v4(), where only `nn` is in
# scope. Matches sblgnt_v1_fabric.NUM by construction.
LABEL_FROM_NN = {f"{v:02d}": k for k, v in V1.NUM.items()}

FINITE = set("IDSO")
SPEECH = {"λέγω", "εἶπον", "γράφω", "μαρτυρέω", "ὁμολογέω", "διδάσκω", "κηρύσσω",
          "ἀπαγγέλλω", "ἀναγγέλλω", "ἐξομολογέω", "φημί", "ἀποκρίνομαι", "βοάω", "κράζω"}
COGNITION = {"οἶδα", "γινώσκω", "ὁράω", "βλέπω", "θεωρέω", "πιστεύω", "ἐπίσταμαι",
             "νομίζω", "δοκέω", "εὑρίσκω", "ἀκούω", "συνίημι", "πείθω"}
SUBORD_BREAK = {"ἵνα", "ὅπως", "ὅταν", "ὅτε", "εἰ", "ἐάν", "καθώς", "μήποτε", "ὥστε", "ἐπάν", "ἕως"}
HOTI = {"ὅτι", "διότι"}
POSTPOS = {"δέ", "γάρ", "οὖν", "μέν", "τε", "μέντοι", "ἄρα", "γε", "δή"}
GLUE_CLS = {"conj", "ptcl"}
V4GRK = Path(r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v1.5\grk")  # deployed (compare target)
V0PROSE = Path(r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v0-prose")
# Writer target. Default = scratch experiment dir so a regen never silently
# overwrites the deployed v1.5/grk; point DRAFT at V4GRK only to deploy.
DRAFT = Path(r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v1.5-binding-experiment\grk")
V4DIR = {"Matt": "01-matt/matt", "Phil": "11-phil/phil", "Rev": "27-rev/rev", "John": "04-john/john"}
V0DIR = {"Matt": "01-matt/matt", "Phil": "11-phil/phil", "Rev": "27-rev/rev", "John": "04-john/john"}


def load_v0_tokens(v0dir, slug, chap):
    """{verse: [punctuated SBLGNT token, ...]} from v0-prose (display forms)."""
    path = v0dir / f"{slug}-{chap:02d}.txt"
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        ref, text = line.split("\t", 1)
        out[int(ref.split(":")[1])] = text.split()
    return out


def cl_features(words):
    """Features of a clause from its DIRECT words (those whose innermost cl is it).
    The clause head is its FINITE verb when it has one — a fronted circumstantial
    participle (Ἐγερθεὶς παράλαβε, Ἀποκριθεὶς εἶπεν) must NOT make the clause read
    as a participle and bind away as a satellite; the finite imperative/indicative
    is the predication. Only verbless/non-finite clauses fall back to first verb."""
    verbs = [w for w in words if w["mpos"].startswith("V")]
    verb = next((w for w in verbs if w["mood"] in FINITE), None) or (verbs[0] if verbs else None)
    kind = ("FIN" if verb and verb["mood"] in FINITE else "ptcp" if verb and verb["mood"] == "P"
            else "inf" if verb and verb["mood"] == "N" else "verbless")
    first = min(words, key=lambda w: (w["verse"], w["wi"]))
    intro = first["lemma"] if (first["cls"] in GLUE_CLS or first["lemma"] in HOTI
                               or first["lemma"] in SUBORD_BREAK) else ""
    return {
        "kind": kind, "lemma": verb["lemma"] if verb else "", "intro": intro,
        "is_rel": any(w["mpos"].startswith("RR") for w in words),
        "is_glue": all(w["cls"] in GLUE_CLS or w["lemma"] in POSTPOS for w in words),
    }


def generate(lowfat, morph, chap):
    """Nesting-based ATU assignment: each word -> its innermost clause that is an
    ATU-ROOT. A clause is a root unless it BINDS to an ancestor: non-finite
    (participle/inf) clauses bind to their finite governor; relative + cognition-
    ὅτι finite clauses bind; glue-only clauses ride with their parent. Verbless
    predications and main/coordinate/ἵνα-subordinate finite clauses are roots."""
    atoms = V1.extract(lowfat, morph, chap)
    all_words = sorted((w for a in atoms for w in a), key=lambda w: (w["verse"], w["wi"]))
    cl_words = {}
    for w in all_words:
        cl_words.setdefault(w["chain"][-1], []).append(w)
    feats = {cl: cl_features(ws) for cl, ws in cl_words.items()}
    rep_chain = {cl: ws[0]["chain"] for cl, ws in cl_words.items()}
    verse_of = {cl: ws[0]["verse"] for cl, ws in cl_words.items()}

    def fin_gov_cl(cl):
        """Nearest FINITE-headed ancestor clause in the nesting chain (the governor
        a dependent clause would bind to), or None."""
        chain = rep_chain[cl]
        for anc in reversed(chain[:chain.index(cl)]):
            f = feats.get(anc)
            if f and f["kind"] == "FIN":
                return anc
        return None

    def is_root(cl):
        f = feats[cl]
        if f["is_glue"]:
            return False
        gov = fin_gov_cl(cl)
        has_gov = gov is not None                                  # governor any verse
        has_gov_samev = has_gov and verse_of[gov] == verse_of[cl]  # within-verse
        # WITHIN-VERSE BINDING (framework §3) gates SECOND PREDICATIONS, not sub-
        # predicational dependents. A FINITE subordinate/relative clause is its own
        # predication: it binds only to a SAME-VERSE governor; a cross-verse finite
        # clause = REVIEW (kills the Acts 1:1-3 relative CHAIN — ἧς…ἀνελήμφθη /
        # οἷς…παρέστησεν — that collapsed several predications across verses). A
        # NON-FINITE dependent (participle/infinitive) is part of ONE predicate and
        # rides with its finite governor EVEN ACROSS a verse marker: this preserves
        # the Greek-prominent cross-verse cases the blanket guard wrongly split —
        # speech frames (²λέγοντες / λέγων), supplementary participles (παύομαι …
        # εὐχαριστῶν, Eph 1:15-16), circumstantial-participle chains (Mark 5:25-27).
        # (Refined 2026-05-24 after the §7.3 audit pair flagged the non-finite over-
        # split; the blanket same-verse form over-split intra-predicate binds.)
        if f["kind"] == "FIN":
            if f["is_rel"]:
                return not has_gov_samev   # finite relative -> same-verse head only
            if f["intro"] in HOTI:
                # cognition-ὅτι binds to a SAME-VERSE cognition verb; speech-ὅτι and
                # any cross-verse ὅτι -> own ATU.
                return not (has_gov_samev and feats[gov]["lemma"] in COGNITION)
            return True
        if f["kind"] in ("ptcp", "inf"):
            return not has_gov   # non-finite: rides its finite governor, any verse
        return True  # verbless predication -> own ATU

    def atu_of(w):
        for cl in reversed(w["chain"]):
            if cl in feats and is_root(cl):
                return cl
        return w["chain"][-1]

    def is_glue(w):
        return w["cls"] in GLUE_CLS or w["lemma"] in POSTPOS

    # content words -> ATU via nesting; glue words -> surface-adjacent content's
    # ATU (postpositive δέ/γάρ -> previous content; prepositive καί/ἰδού -> next).
    # Done at the WORD level in surface order, so a cross-verse pull (²λέγοντες)
    # can't strand a later verse's glue on the wrong line.
    n = len(all_words)
    next_content = [None] * n
    nxt = None
    for i in range(n - 1, -1, -1):
        if not is_glue(all_words[i]):
            nxt = atu_of(all_words[i])
        next_content[i] = nxt
    # postpositive δέ/γάρ binds to the IMMEDIATELY PRECEDING token's ATU (not the
    # last *content* word) — so "ἐπὰν δὲ εὕρητε" stays one ATU. Binding to last
    # content skipped back past a prepositive opener (ἐπάν/ὅταν), stranding δέ in
    # the previous clause and shattering the clause in surface-order emit.
    prev_tok = None
    for i, w in enumerate(all_words):
        if is_glue(w):
            if w["lemma"] in POSTPOS:
                w["_atu"] = prev_tok if prev_tok is not None else next_content[i]
            else:
                w["_atu"] = next_content[i] if next_content[i] is not None else prev_tok
        else:
            w["_atu"] = atu_of(w)
        prev_tok = w["_atu"]

    groups = {}
    for w in all_words:
        groups.setdefault(w["_atu"], []).append(w)
    lines = sorted(groups.values(), key=lambda ws: (ws[0]["verse"], ws[0]["wi"]))
    for ws in lines:
        ws.sort(key=lambda w: (w["verse"], w["wi"]))
    return merge_contentless(genabs_merge(lines))


_FUNC_CLS = {"conj", "ptcl", "prep", "det", "particle", "subjunction", "x", ""}


def _has_content(ws):
    """True if the line has a content-bearing word (not pure function words)."""
    for w in ws:
        if w["cls"] not in _FUNC_CLS and w["lemma"] not in (HOTI | SUBORD_BREAK | POSTPOS):
            return True
    return False


def merge_contentless(lines):
    """No ATU line may be content-less (a thought needs a content word). Fold a
    function-word-only line (stray ὅτι/ὅπως/δέ/καί) into a neighbor: postpositive
    -> backward, else forward. Guarantees every ATU line is KJV-mappable so the
    Greek/English layers stay 1:1."""
    out, pend = [], []
    for ws in lines:
        if not _has_content(ws):
            if all(w["lemma"] in POSTPOS for w in ws) and out:
                out[-1].extend(ws)
            else:
                pend.extend(ws)
            continue
        out.append(pend + ws if pend else list(ws))
        pend = []
    if pend:
        (out[-1].extend(pend) if out else out.append(pend))
    for ws in out:
        ws.sort(key=lambda w: (w["verse"], w["wi"]))
    return out


def genabs_merge(lines):
    """Gen-abs / leading-circumstantial frames are SIBLINGS of their main clause
    in lowfat (not nested), so they survive as their own line; merge such a
    leading non-finite frame FORWARD into the next ATU it frames."""
    out, pend = [], []
    for ws in lines:
        has_fin = any(w["mpos"].startswith("V") and w["mood"] in FINITE for w in ws)
        has_gen_ptcp = any(w["mpos"].startswith("V") and w["mood"] == "P" and w["case"] == "G"
                           for w in ws)
        if not has_fin and has_gen_ptcp:
            pend.extend(ws)
            continue
        out.append(pend + ws if pend else list(ws))
        pend = []
    if pend:
        (out[-1].extend(pend) if out else out.append(pend))
    for ws in out:
        ws.sort(key=lambda w: (w["verse"], w["wi"]))
    return out


# --- Layer-1 break-legality (mechanical, mandatory): a line may not END on a
# leader that grammatically governs what FOLLOWS. R3 (article), R4 (negation),
# R8 (framing device) all share one fix: such a line MERGES FORWARD into the
# next. R7 (multi-word vocative) shares one fix too: keep consecutive vocative-
# case tokens on one line. Predicates copied verbatim from validators/syntax/
# check_r{3,4,7,8}_*.py so the pre-commit canon gate is guaranteed to pass. ---

_FRAMING = {"ἰδού", "διό", "οὖν", "ἀλλά", "γάρ", "πλήν", "τοιγαροῦν"}   # R8 closed list
_NUN = {"νῦν", "νυν", "νύν"}                                          # R8 "νῦν δέ"
_DE = {"δέ", "δε"}
_NEG_LEM = {"οὐ", "μή", "οὐδέ", "μηδέ", "οὐκέτι", "μηκέτι", "μήποτε", "οὐχί", "μήτι"}  # R4
_NEG_SURF = {"οὐ", "οὐκ", "οὐχ", "μή", "οὐδέ", "μηδέ", "οὐκέτι", "μηκέτι", "μήποτε"}
_R9_OPENERS = {"ἵνα", "ὥστε", "ὅτι", "διότι", "ὅταν", "ὅτε", "εἰ", "ἐάν", "καθώς", "μήποτε"}  # R9
_SENT_TERM = {".", ";", "·", "·"}   # period, ; (Greek '?'), ano teleia, middle dot


def _strip_p(s):
    """NFC + strip leading/trailing punctuation (incl. SBLGNT editorial marks)."""
    s = unicodedata.normalize("NFC", s)
    i, j = 0, len(s)
    while i < j and unicodedata.category(s[i]).startswith("P"):
        i += 1
    while j > i and unicodedata.category(s[j - 1]).startswith("P"):
        j -= 1
    return s[i:j]


def _rtok(w, v0):
    """The rendered (v0-prose, punctuated) surface token for a word — what the
    validators actually see in v1.5/grk."""
    toklist = v0.get(w["verse"], [])
    return toklist[w["wi"] - 1] if 0 <= w["wi"] - 1 < len(toklist) else w["text"]


def merge_split_vocatives(lines):
    """R7: 2+ consecutive vocative-case tokens (parse case == 'V') that fall on
    different ATU lines form one indivisible address unit -> merge. Skip the
    stacked-parallel case (a line carrying its own genitive/adjective modifier
    alongside the vocative — each such address keeps its own line, canon §3.9)."""
    def is_voc(w):
        return w.get("case") == "V"

    def has_modifier(ws):  # genitive complement or non-voc adjective on the line
        for w in ws:
            if is_voc(w):
                continue
            if w["case"] == "G" and (w["mpos"].startswith(("N", "A")) or w["mpos"] in ("RP", "RR", "RD")):
                return True
            if w["mpos"].startswith("A") and w["case"] not in ("V", ""):
                return True
        return False

    out = []
    for ws in lines:
        if (out and is_voc(ws[0]) and is_voc(out[-1][-1])
                and not has_modifier(out[-1]) and not has_modifier(ws)):
            out[-1].extend(ws)
            out[-1].sort(key=lambda w: (w["verse"], w["wi"]))
        else:
            out.append(list(ws))
    return out


def merge_cognition_hoti(lines, hoti_dec):
    """R10 (canon §2.1): bind a ὅτι-COMPLEMENT to its matrix verb; leave a causal/
    adverbial ὅτι and a re-performed direct-discourse ὅτι standing. The bind/stand
    call is sourced MECHANICALLY from the Macula treebank (`rule=that-VP` complement
    vs `sub-CL`/`role=adv` causal; deixis test for direct-vs-indirect), keyed
    (verse, wi) via `hoti_dec` — NOT lemma classes. Quote-status has no force; only
    the bidirectional test (operationalized as these Macula features) decides. A line
    opening with ὅτι merges back iff Macula says BIND and the junction is WITHIN one
    verse (framework §3 — no silent cross-verse merge)."""
    out = []
    for ws in lines:
        h = ws[0]
        if (out and h["lemma"] == "ὅτι"
                and hoti_dec.get((h["verse"], h["wi"])) in ("BIND", "BIND_GROUND")
                and _junction_same_verse(out[-1], ws)):
            out[-1].extend(ws)
            out[-1].sort(key=lambda w: (w["verse"], w["wi"]))
        else:
            out.append(list(ws))
    return out


# --- Subordinate-clause binding (idea-unit convergence; revises canon §3.4/R9
# "adverbial subordinate clauses can stand on their own line"). The 2026-05-24
# genre-spread measurement found over-split = 90-95% of all idea-unit failures,
# dominated by FINITE subordinate clauses stranded from their matrix. A finite
# subordinate clause is half a thought; per the bidirectional test it BINDS to
# its matrix. Direction by clause type + surface position:
#   FRAME (temporal/conditional/concessive) preceding its main clause -> bind FORWARD
#   purpose / result / complement / relative clause following its head -> bind BACKWARD
# NOT bound: coordinate main clauses (no subordinator); a direct-speech quote after
# a finite speech-verb intro (R11 cataphoric frame is itself an ATU). ὅτι is left to
# merge_cognition_hoti (cognition binds; recitative/speech ὅτι stays a quote). ---
_FWD_FRAME = {"ὅτε", "ὅταν", "εἰ", "ἐάν", "ἐπάν", "ἐπειδή", "ἐπεί", "ἡνίκα",
              "ὁπότε"}                                        # frame precedes apodosis
_BWD_SUB = {"ἵνα", "ὅπως", "μήποτε", "διότι",                  # purpose/cause follows head
            "ὅπου", "ὅθεν", "ἔνθα", "καθότι", "καθὸ",          # relative adverb -> binds to head
            "ἕως", "ἄχρι", "μέχρι", "πρίν"}                    # terminative: "until/before" POSTPOSES
# ἕως/ἄχρι/μέχρι/πρίν are terminative-limit subordinators: the clause they head
# follows its matrix ("sit at my right hand UNTIL I make…", Heb 1:13; "you will not
# get out UNTIL you pay", Matt 5:26), so it binds BACKWARD, not forward. (Moved out
# of _FWD_FRAME 2026-05-24 per the §7.3 Greek-lens audit — as forward-frames they
# stranded.) The rarer fronted πρίν (John 8:58) is left as a residual.
# NOTE: ὥστε is deliberately NOT here. Consecutive-result ὥστε is governed by R25
# (canon §3.14a), which has its own gated test (<=8 words, co-referential subject,
# illative-exclusion list). Binding ὥστε under this flat pass would override R25
# and merge illative-ὥστε cases R25 split-maintains. Leave ὥστε to R25.
# Verbs of entreaty/command take a ἵνα COMPLEMENT (not a final clause); the
# complement binds to that verb, so a ἵνα directly after one of these binds back
# normally — but a ἵνα must never bind across an intervening clause (guarded by
# the finite-verb-count gate below).
_ENTREATY = {"παρακαλέω", "ἐρωτάω", "δέομαι", "παραγγέλλω", "αἰτέω", "προσεύχομαι"}
# RESERVED — not yet wired into the bind logic (ἵνα already binds backward via
# _BWD_SUB regardless of governor). Kept for a future complement-vs-purpose
# refinement. Flagged not-consumed by the 2026-05-24 §7.3 Greek-lens audit.
_BIDIR_SUB = {"καθώς", "ὥσπερ", "καθάπερ"}                     # comparative: direction by position


def _seg_opener(ws):
    """(opener_lemma, is_relative) for a segment, skipping a leading coordinating
    καί and any postpositives (δέ/γάρ/οὖν/...). is_relative is True for a bare
    relative pronoun opener AND for a PIED-PIPED relative (preposition + relative,
    e.g. ἐν ᾧ / δι' οὗ / ἐξ οὗ — the Pauline norm), which binds to its head like a
    bare relative. Returns ('', False) if the first substantive token is neither a
    subordinator nor (the start of) a relative."""
    sw = sorted(ws, key=lambda w: (w["verse"], w["wi"]))
    i = 0
    while i < len(sw) and (sw[i]["lemma"] == "καί" or sw[i]["lemma"] in POSTPOS):
        i += 1
    if i >= len(sw):
        return "", False
    first = sw[i]
    # pied-piped relative: preposition immediately followed by a relative pronoun
    if (first["mpos"].startswith("P") or first["cls"] == "prep") and i + 1 < len(sw) \
            and sw[i + 1]["mpos"].startswith("RR"):
        return first["lemma"], True
    return first["lemma"], first["mpos"].startswith("RR")


def _has_finite(ws):
    return any(w["mpos"].startswith("V") and w["mood"] in FINITE for w in ws)


def _is_speech_frame(ws):
    """Segment that introduces a direct-speech quote (a speech verb, FINITE or a
    PARTICIPIAL λέγων/λεγούσης/λέγοντες): the NEXT segment is the quote and must NOT
    bind back into it (R11 — the announcement is its own cataphoric ATU). Including
    the participial form stops a quote binding back into 'ἤκουσα φωνὴν...λεγούσης·'."""
    return any(w["mpos"].startswith("V") and (w["mood"] in FINITE or w["mood"] == "P")
               and w["lemma"] in SPEECH for w in ws)


def _rel_is_correlative(ws):
    """A relative-led segment is a NEW coordinate/correlative predication (not a
    restrictive modifier of the prior clause), so it must NOT bind backward, when
    EITHER:
      - a coordinating καί immediately PRECEDES the relative pronoun
        ('καὶ ὃς οὐκ ἔχει' — a fresh sorites/antithesis member, Mark 4:25), OR
      - a coordinating particle (δέ / μέν / γάρ) or additive καί immediately
        FOLLOWS it ('ὃς δʼ ἄν…', 'ὃ γὰρ…', 'ὅς καί ἐστιν … ὃς καὶ ἐντυγχάνει' —
        coordinate relative chains, Rom 8:30/8:34).
    Binding any of these backward fuses two distinct predications (over-merge); the
    2026-05-24 before/after re-measure surfaced both as the engine's only regression
    class (coordinate-relative chains collapsing onto their neighbor)."""
    sw = sorted(ws, key=lambda w: (w["verse"], w["wi"]))
    # leading coordinating καί directly before the relative pronoun -> coordinate
    if len(sw) > 1 and sw[0]["lemma"] == "καί" and sw[1]["mpos"].startswith("RR"):
        return True
    i = 0
    while i < len(sw) and (sw[i]["lemma"] == "καί" or sw[i]["lemma"] in POSTPOS):
        i += 1
    # sw[i] is the relative pronoun; check the coordinator right after it
    return i + 1 < len(sw) and sw[i + 1]["lemma"] in {"δέ", "μέν", "γάρ", "καί"}


# Single-cognitive-bite cap (content words). A bind binds a half-thought to its
# matrix to form ONE ATU; it must NOT snowball a whole periodic sentence (Pauline
# ἐν ᾧ / ἧς relative chains) into a mega-line, which fails the bar as badly as the
# over-split. If a bind would push the combined line past this many content words,
# the dependent stays its own line (framework: over-long residual is left, not
# force-merged). Tuned so frame+apodosis and short relatives bind; chains break.
_BIND_CAP = 18


def _ccount(ws):
    """Content-word count (excludes pure function words / connectives)."""
    return sum(1 for w in ws if w["cls"] not in _FUNC_CLS
               and w["lemma"] not in (HOTI | SUBORD_BREAK | POSTPOS))


def _fvcount(ws):
    """Finite-verb count. The PRIMARY single-cognitive-bite gate (replacing the raw
    content-word cap as the chief test, per the 2026-05-24 audit): one bind joins a
    matrix to ONE subordinate frame, so a legitimate result has at most 2 finite
    verbs (matrix predication + the subordinate frame's). A bind producing >2 finite
    verbs is fusing a distinct independent predication (Heb 4:16 'ἵνα λάβωμεν ἔλεος /
    καὶ χάριν εὕρωμεν'; Mark 4:25 sorites) and is refused. This is the canon's
    'second-predication' criterion (R20) operationalized for finite clauses."""
    return sum(1 for w in ws if w["mpos"].startswith("V") and w["mood"] in FINITE)


def _is_rel_conditional(ws):
    """Relative pronoun + ἄν/ἐάν = a 'whoever/whatever' conditional protasis
    (ὃς ἂν…, ὅστις ἐὰν…, ὅσοι ἄν…). It behaves like an ἐάν frame — it PRECEDES and
    binds FORWARD to its apodosis, NOT backward to a prior clause (Mark 4:25 'ὃς γὰρ
    ἔχει' / 'δοθήσεται αὐτῷ'; Acts 2:39 'ὅσους ἂν προσκαλέσηται')."""
    _, is_rel = _seg_opener(ws)
    return is_rel and any(w["lemma"] in {"ἄν", "ἐάν"} for w in ws)


# Levinsohn/Runge developmental connectives — a clause headed by one is a new
# development / its own grounds, and resists binding BACKWARD. CLOSED LIST (§7.3):
#   δέ (development) · γάρ (grounds) · μέν (anticipatory correlative-setup).
# Deliberately EXCLUDED: καί (continuity — MORE likely to bind), τε (tight phrase-
# coordination), γε/δή (emphatics, not connectives). οὖν is a held candidate
# (inferential in Paul → resists; Johannine οὖν is resumptive ≈ continuity → binds):
# test in audit before adding. ἀλλά/διό are prepositive framing (R8 leads).
_DEV_CONNECTIVE = {"δέ", "γάρ", "μέν"}


def _dev_connective(ws):
    """A clause headed by a developmental connective (`_DEV_CONNECTIVE`) must NOT bind
    BACKWARD into the prior line (Rom 2:1 'ἐν ᾧ γὰρ κρίνεις … κατακρίνεις' is its own
    ATU, not a tail of 'ὦ ἄνθρωπε πᾶς ὁ κρίνων'). The marker is postpositive (2nd
    position), sitting after the fronted element and before the clause's finite verb
    (ἐν ᾧ ΓΑΡ κρίνεις; τὰ ΓΑΡ αὐτὰ πράσσεις; Τὸν ΜΕΝ πρῶτον λόγον …). These are
    CLAUSE-level connectives — they mark a clause-level development (δέ/γάρ head their
    own finite predication; μέν sets up a forward correlative beat), so leaning on
    them is firewall-safe (syntax, not aesthetics) and costs nothing against the
    bidirectional test, unlike the sub-clausal yea-marker license. High-precision,
    low-recall: presence signals a boundary; absence implies nothing (asyndeton breaks
    too) — so this only BLOCKS a backward bind, never forces a split. Detected only
    when the connective precedes the first finite verb; a γάρ after the main verb is
    parenthetical (Mark's ἦν γὰρ … asides) and not the clause connective."""
    if not _has_finite(ws):
        return False   # a verbless phrase-fragment (phrase-internal μέν) is not a clause
    for w in sorted(ws, key=lambda w: (w["verse"], w["wi"])):
        if w["mpos"].startswith("V") and w["mood"] in FINITE:
            return False
        if w["lemma"] in _DEV_CONNECTIVE:
            return True
    return False


def _junction_same_verse(earlier, later):
    """Framework §3: bindings fire WITHIN a single verse; a cross-verse bind is a
    REVIEW case, never a silent merge. A bind is allowed only when the junction is
    inside one verse — the earlier segment's last (max) verse equals the later
    segment's first (min) verse. Forbidding cross-verse merges is what stopped the
    over-merge defect (verse-N-end fused with verse-N+1-start) the 2026-05-24
    before/after measurement surfaced in every genre cluster."""
    return max(w["verse"] for w in earlier) == min(w["verse"] for w in later)


def _bind_ok(host, dep):
    """Shared gate for every bind: within one verse (framework §3), the combined
    line is one cognitive bite (PRIMARY: <=2 finite verbs — matrix + one subordinate
    frame), and a content-word cap as a secondary fuse against catena snowball."""
    return (_junction_same_verse(host, dep)
            and _fvcount(host) + _fvcount(dep) <= 2
            and _ccount(host) + _ccount(dep) <= _BIND_CAP)


def merge_subordinate_clauses(segments):
    """Bind finite subordinate clauses to their matrix (see header). Backward pass
    (purpose/cause/relative -> previous content segment), then forward pass
    (temporal/conditional frame + relative-conditional protasis -> next segment),
    then comparative by position. Every bind is gated by _bind_ok (within-verse +
    <=2 finite verbs + content cap). Quotes are protected: a segment that is itself
    a direct-speech quote (its predecessor was a speech frame) is never bound into."""
    # Backward: ἵνα/ὅπως/μήποτε/διότι + relative-adverb + restrictive relative ->
    # previous segment. `qflag` marks each out-segment that is a direct-speech quote
    # (its predecessor is a speech frame), so a later purpose clause can't pierce it.
    out, qflag = [], []
    for ws in segments:
        opener, is_rel = _seg_opener(ws)
        bind_back = (opener in _BWD_SUB) or is_rel
        if is_rel and (_rel_is_correlative(ws) or _is_rel_conditional(ws)):
            bind_back = False   # ὃς δέ/ὅστις δέ (new correlative) or ὃς ἄν (forward conditional)
        if _dev_connective(ws):
            bind_back = False   # δέ/γάρ/μέν-headed clause = new development (Levinsohn/Runge)
        prev_is_quote = bool(qflag) and qflag[-1]
        if (bind_back and out and _has_finite(ws)
                and not _is_speech_frame(out[-1]) and not prev_is_quote
                and _bind_ok(out[-1], ws)):
            out[-1].extend(ws)
            out[-1].sort(key=lambda w: (w["verse"], w["wi"]))
        else:
            out.append(list(ws))
            qflag.append(len(out) >= 2 and _is_speech_frame(out[-2]))
    # Forward: a finite temporal/conditional frame OR a relative-conditional protasis
    # (ὃς ἄν…) preceding its matrix binds FORWARD into the next segment. `pend` holds
    # the frame (or a same-verse stack) until its matrix arrives.
    fwd, pend = [], None
    for ws in out:
        opener, _ = _seg_opener(ws)
        is_frame = (opener in _FWD_FRAME and _has_finite(ws)) or _is_rel_conditional(ws)
        if pend is not None:
            if _bind_ok(pend, ws):
                if is_frame:
                    pend = pend + list(ws)        # stack same-verse frames; keep waiting
                    continue
                fwd.append(pend + list(ws))        # frame(s) + matrix = one ATU
                pend = None
                continue
            fwd.append(pend)                       # cross-verse / over-cap / 2-verb: frame stands alone
            pend = None
        if is_frame:
            pend = list(ws)
        else:
            fwd.append(list(ws))
    if pend is not None:
        fwd.append(pend)
    for ws in fwd:
        ws.sort(key=lambda w: (w["verse"], w["wi"]))
    # Comparative (καθώς/ὥσπερ/καθάπερ): bind to the adjacent finite clause.
    res = []
    for ws in fwd:
        opener, _ = _seg_opener(ws)
        if (opener in _BIDIR_SUB and res and _has_finite(res[-1])
                and not _is_speech_frame(res[-1]) and not _dev_connective(ws)
                and _bind_ok(res[-1], ws)):
            res[-1].extend(ws)
            res[-1].sort(key=lambda w: (w["verse"], w["wi"]))
        else:
            res.append(list(ws))
    return res


_SENT_END_CHARS = set(".·;")


def _seg_ends_sentence(ws, v0):
    """True if the LAST rendered token of a segment ends in a sentence
    terminator (period / middle-dot / Greek question mark/semicolon).
    Uses v0-prose punctuation (what the deployed grk shows)."""
    sw = sorted(ws, key=lambda w: (w["verse"], w["wi"]))
    tok = _rtok(sw[-1], v0)
    return bool(tok) and tok[-1] in _SENT_END_CHARS


def merge_parallel_elided_verb(segments, v0):
    """Parallel-elided-verb merge (added 2026-05-31).

    Lowfat clause-atoms occasionally split a contrastive parallel clause with
    an elided verb across multiple segments — Rom 8:5 is the canonical case:

        Source: "οἱ γὰρ κατὰ σάρκα ὄντες τὰ τῆς σαρκὸς φρονοῦσιν,
                 οἱ δὲ κατὰ πνεῦμα τὰ τοῦ πνεύματος."
        Lowfat: atom4 = "οἱ τὰ τοῦ πνεύματος" (verbless subj+complement)
                atom6 = "κατὰ πνεῦμα"        (verbless PP)
        Surface order interleaves them, so after surface re-segmentation:
                seg "οἱ δὲ" / seg "κατὰ πνεῦμα" / seg "τὰ τοῦ πνεύματος."
        Result: 4 ATU lines where 2 belongs (the parallel-elided-verb tail
                "οἱ δὲ κατὰ πνεῦμα τὰ τοῦ πνεύματος." is ONE ATU).

    Rule: merge a run of 2+ consecutive verbless segments when each is
    short (<= 4 content words), same-verse, and no sentence terminator
    (. · ;) appears between them. Comma-internal breaks (the SBL editorial
    layout) do NOT block. Stops at the first sentence terminator or finite
    or long verbless segment.

    Safe by construction:
    - Mat 5:3-12 Beatitudes: each "Μακάριοι οἱ X" verbless predication is
      followed by a finite ὅτι clause — finite breaks the run.
    - Stand-alone verbless aphorisms ending in period (Greek period or ano
      teleia) self-block — they stop the accumulation.
    - Cross-verse runs blocked by the same-verse gate.
    """
    out, i = [], 0
    n = len(segments)
    while i < n:
        ws = segments[i]
        if _has_finite(ws) or _ccount(ws) > 4 or _seg_ends_sentence(ws, v0):
            out.append(list(ws))
            i += 1
            continue
        # Start of a possible run. Accumulate forward.
        verse_start = min(w["verse"] for w in ws)
        run = [list(ws)]
        k = i + 1
        while k < n:
            nxt = segments[k]
            if _has_finite(nxt):
                break
            if min(w["verse"] for w in nxt) != verse_start:
                break
            if _ccount(nxt) > 4:
                break
            run.append(list(nxt))
            if _seg_ends_sentence(nxt, v0):
                k += 1
                break
            k += 1
        if len(run) >= 2:
            merged = [w for r in run for w in r]
            merged.sort(key=lambda w: (w["verse"], w["wi"]))
            out.append(merged)
            i = k
        else:
            out.append(run[0])
            i += 1
    return out


def merge_line_end_leaders(lines, v0):
    """R3/R4/R8: no ATU line may END on a forward-governing leader — an article
    (R3, MorphGNT POS 'RA'), a non-terminal negation whose scope is off-line
    (R4), or a framing device (R8: ἰδού/διό/οὖν/ἀλλά/γάρ/πλήν/τοιγαροῦν, νῦν δέ).
    Such a line merges FORWARD into the next (STRONG-MERGE). Last-line carry that
    can't merge forward is left as-is."""
    def is_article(w):
        return w["mpos"] == "RA" or w["cls"] == "det"

    def is_framing(ws):
        last = _strip_p(_rtok(ws[-1], v0))
        if last in _FRAMING:
            return True
        return len(ws) >= 2 and _strip_p(_rtok(ws[-2], v0)) in _NUN and last in _DE

    def is_stranded_neg(ws):
        w = ws[-1]
        surf = _strip_p(_rtok(w, v0))
        is_neg = (w["mpos"] in ("D-", "ADV", "PART", "C-") and w["lemma"] in _NEG_LEM) or surf in _NEG_SURF
        if not is_neg or len(ws) == 1:
            return False
        raw = _rtok(w, v0).rstrip()                       # Filter A: sentence-terminal
        if raw and raw[-1] in _SENT_TERM:
            return False
        for prev in ws[:-1]:                              # Filter B: finite verb on line
            if prev["mpos"].startswith("V"):
                return False
        return True

    def is_subord_opener(ws):   # R9: subordinate-clause opener must not trail
        last = ws[-1]
        return _strip_p(_rtok(last, v0)) in _R9_OPENERS or last["lemma"] in _R9_OPENERS

    def is_leader(ws):
        last = ws[-1]
        return (is_article(last) or is_framing(ws)
                or is_stranded_neg(ws) or is_subord_opener(ws))

    out, carry = [], []
    for ws in lines:
        cur = carry + list(ws)
        cur.sort(key=lambda w: (w["verse"], w["wi"]))
        if is_leader(cur):
            carry = cur
        else:
            out.append(cur)
            carry = []
    if carry:
        (out[-1].extend(carry) if out else out.append(carry))
        if out:
            out[-1].sort(key=lambda w: (w["verse"], w["wi"]))
    return out


# A forward-governing function word governs what FOLLOWS it: a preposition, or a
# subordinator that introduces a following clause (temporal/conditional frame,
# purpose/cause, comparative, terminative ἄχρι/ἕως/μέχρι/πρίν, ὅτι/ὅταν/…). No ATU
# line may END on one — "ending a thought on 'until' is incoherent"; it must LEAD
# the next line. (Canon §3.4 + the §3.5 ὅτι-leads-its-complement convention.)
_FWD_GOV_LEM = _FWD_FRAME | _BWD_SUB | _BIDIR_SUB | _R9_OPENERS
# χάριν ("for the sake of") is POSTPOSITIVE -- it follows its genitive object and
# never preposes one onto the next line, so it must NOT be treated as a forward
# governor (otherwise it gets peeled off the end of verse N onto verse N+1's line:
# Titus 1:11, 1Tim 5:14, Jude 1:16). Verified postpositive in all 9 GNT occurrences.
_POSTPOS_PREP = {"χάριν"}


def _is_fwd_governor(w):
    if w["lemma"] in _POSTPOS_PREP:
        return False
    return w["cls"] == "prep" or w["mpos"] == "P-" or w["lemma"] in _FWD_GOV_LEM


def lead_forward_trailing_governors(segments):
    """No ATU line may END on a forward-governing token (preposition or subordinator):
    it governs what follows, so it must LEAD the next line, never dangle. When a verse
    boundary or a parse attachment strands a governor at a line tail — Acts 1:1
    `…ποιεῖν τε καὶ διδάσκειν ἄχρι |` `1:2 ἧς ἡμέρας…ἀνελήμφθη` — peel the trailing
    governor run and prepend it to the next segment (`ἄχρι` now LEADS the v2 line).
    Distinct from merge_line_end_leaders' STRONG-MERGE: only the trailing token moves,
    not the whole line (strong-merging here would recreate the cross-verse mega-line).
    Relocated tokens are flagged so emit labels the line by its own clause's verse."""
    for i in range(len(segments) - 1):
        seg = segments[i]
        k = len(seg)
        while k > 1 and _is_fwd_governor(seg[k - 1]):
            k -= 1
        if 1 <= k < len(seg):                 # trailing governor(s) + >=1 content token
            moved = seg[k:]
            for w in moved:
                w["_relocated"] = True
            del seg[k:]
            segments[i + 1][0:0] = moved
            segments[i + 1].sort(key=lambda w: (w["verse"], w["wi"]))
    return [s for s in segments if s]


def emit_v4(lowfat, morph, v0dir, slug, chap):
    """v1.5/grk lines rendered from v0-prose PUNCTUATED tokens. A display line is a
    maximal run of surface-CONSECUTIVE words sharing one ATU id — so the flattened
    text always equals the SBLGNT source word order (verify_word_order gate). A
    discontinuous ATU (its words interleaved with an embedded clause) renders as
    two contiguous segments, the only order-preserving rendering. Blank line
    between verse groups; a cross-verse word in a segment gets a superscript."""
    sup = {str(i): c for i, c in enumerate("⁰¹²³⁴⁵⁶⁷⁸⁹")}
    supn = lambda v: "".join(sup[d] for d in str(v))
    v0 = load_v0_tokens(v0dir, slug, chap)
    base_lines = generate(lowfat, morph, chap)

    # Re-segment into surface-CONTIGUOUS display segments by ATU id, THEN apply
    # the binding-merge rules to those actual display boundaries (not to the
    # grouped clause-atoms — a discontinuous clause-atom must split at its gap to
    # preserve word order, and the binding rules act on the resulting cuts).
    flat = [(w, lid) for lid, ws in enumerate(base_lines) for w in ws]
    flat.sort(key=lambda x: (x[0]["verse"], x[0]["wi"]))
    segments, cur, cur_lid = [], [], None
    for w, lid in flat:
        if lid != cur_lid and cur:
            segments.append(cur); cur = []
        cur.append(w); cur_lid = lid
    if cur:
        segments.append(cur)
    # Macula-sourced ὅτι bind/stand decisions for this book, filtered to this chapter.
    nn = Path(lowfat).stem.split("-")[0]
    hoti_dec = {(v, wi): d for (c, v, wi), d in macula_hoti.decisions(nn).items() if c == chap}
    segments = merge_split_vocatives(segments)
    segments = merge_cognition_hoti(segments, hoti_dec)
    segments = merge_subordinate_clauses(segments)
    segments = merge_parallel_elided_verb(segments, v0)
    segments = merge_line_end_leaders(segments, v0)
    segments = lead_forward_trailing_governors(segments)

    out, headered = [], set()

    def flush(seg_words):
        if not seg_words:
            return
        # Label by the line's OWN clause verse, not a token relocated in from the
        # prior verse (a led-forward ἄχρι must not drag the header back a verse).
        own = [w["verse"] for w in seg_words if not w.get("_relocated")]
        fv = min(own) if own else seg_words[0]["verse"]
        if fv not in headered:
            if out:
                out.append("")            # blank-line separator between verses
            out.append(f"{chap}:{fv}")
            headered.add(fv)
        toks, segv = [], fv
        for w in seg_words:
            toklist = v0.get(w["verse"], [])
            t = toklist[w["wi"] - 1] if 0 <= w["wi"] - 1 < len(toklist) else w["text"]
            if w["verse"] > segv:
                t = supn(w["verse"]) + t; segv = w["verse"]
            toks.append(t)
        out.append(" ".join(toks))

    for seg in segments:
        flush(seg)
    # Render-stage adjudication overrides: per verse, swap mechanical ATU
    # lines for adjudicated ones iff the override's joined greek_alnum
    # (NFD + Greek block + polytonic + Latin + digit) equals the mechanical
    # block's same normalization. Otherwise mechanical stands. Empty
    # overrides.json -> structural copy (no behavior change). See
    # scripts/gnt_overrides.py + data/text-files/v1.5-adjudicated/grk/README.md.
    book_label = LABEL_FROM_NN.get(nn)
    if book_label is not None:
        out = gnt_overrides.apply_chapter_overrides(book_label, chap, out)
    return out


def write_draft_num(num, chap):
    """Generate + write draft v1.5/grk for book `num` (1-27), chapter `chap`."""
    lowfat, morph, v0dir, slug, nn = V1.book_paths(num)
    lines = emit_v4(lowfat, morph, v0dir, slug, chap)
    d = DRAFT / f"{nn}-{slug}"
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{slug}-{chap:02d}.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main():
    book = sys.argv[1] if len(sys.argv) > 1 else "Matt"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    write = "--write" in sys.argv
    num = V1.NUM[book]
    lowfat, morph, v0dir, slug, nn = V1.book_paths(num)
    out = emit_v4(lowfat, morph, v0dir, slug, chap)
    if write:
        print(f"wrote {write_draft_num(num, chap)}")
        return
    print(f"=== {book} {chap}: SBLGNT-native v1.5/grk (no reconciler) ===\n")
    print("\n".join(out))
    hp = V4GRK / f"{nn}-{slug}" / f"{slug}-{chap:02d}.txt"
    if hp.exists():
        hand = [l for l in hp.read_text(encoding="utf-8").splitlines() if l.strip()]
        ismark = lambda l: l and l[0].isdigit() and ":" in l.split()[0]
        gl = [l for l in out if l.strip() and not ismark(l)]
        hl = [l for l in hand if l.strip() and not ismark(l)]
        print(f"\n--- lines: SBLGNT-native={len(gl)}  hand-v4={len(hl)} ---")


if __name__ == "__main__":
    main()
