#!/usr/bin/env python3
"""
scan_r23_dative_infinitive.py — Empirical check on R23 (dative subject of
infinitive).

R23's canonical example is Rom 12:3. Adversarial over-structuring audit
(2026-04-18) flagged R23 as most-suspect: possibly one-verse crystallization.
This scan tests whether the pattern fires on other verses.

Pattern (broad, for empirical surfacing):
  A verse contains
    - a speech/command/desire-class verb lemma
    - a dative NP (parsing[4] == 'D') not governed by a preposition
    - an infinitive (parsing[3] == 'N')
  and the dative can plausibly be the semantic subject of the infinitive
  (not just the indirect object of the main verb).

The "plausibly subject of infinitive" prong is editorial — this scan
surfaces candidates; Stan decides which qualify.

Command-class lemma list (open; Stan can narrow):
  λέγω, παραγγέλλω, παρακαλέω, κελεύω, ἐπιτάσσω, διαστέλλομαι, ἐντέλλομαι,
  ἐρωτάω, αἰτέω, δέομαι, συμβουλεύω, θέλω, βούλομαι, δοκέω, δεῖ, μέλλω.

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/scan_r23_dative_infinitive.py
"""
import os, re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")
SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

COMMAND_LEMMAS = {
    "λέγω", "παραγγέλλω", "παρακαλέω", "κελεύω", "ἐπιτάσσω",
    "διαστέλλομαι", "ἐντέλλομαι", "ἐρωτάω", "αἰτέω", "δέομαι",
    "συμβουλεύω", "θέλω", "βούλομαι", "δοκέω", "δεῖ", "μέλλω",
    "δίδωμι",  # "give [dat] to [inf]" construction
}

def clean(w):
    return re.sub(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]', '', w)

def load_morph(slug):
    if slug in _cache: return _cache[slug]
    fn = SLUG_TO_FN.get(slug)
    if not os.path.isdir(MORPH):
        _cache[slug] = {}; return {}
    path = next((os.path.join(MORPH, f) for f in os.listdir(MORPH)
                 if fn and f.startswith(fn+"-") and f.endswith(".txt")), None)
    if not path:
        _cache[slug] = {}; return {}
    verses = defaultdict(list)
    for line in open(path, encoding="utf-8"):
        parts = line.strip().split(" ", 6)
        if len(parts) < 7: continue
        ref, pos, parsing, _, word, _n, lemma = parts
        c = clean(word)
        if c:
            verses[(int(ref[2:4]), int(ref[4:6]))].append((c, pos, parsing, lemma))
    _cache[slug] = dict(verses); return _cache[slug]

def is_cmd_verb(pos, p, lemma):
    return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO" and lemma in COMMAND_LEMMAS

def is_dative_np(pos, p):
    return pos in ("N-", "RP", "RD", "A-") and len(p) >= 5 and p[4] == "D"

def is_prep(pos, p):
    return pos == "P-"

def is_infinitive(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] == "N"

def has_unprepped_dative(tokens):
    """Return a dative NP that is not immediately preceded by a preposition (within 2 positions)."""
    for i, (w, pos, p, l) in enumerate(tokens):
        if not is_dative_np(pos, p): continue
        prep_near = False
        for k in range(max(0, i-2), i):
            if is_prep(tokens[k][1], tokens[k][2]):
                prep_near = True; break
        if not prep_near:
            return (w, l)
    return None

def scan():
    out = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(slug)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            verses = {}
            cur_ref, cur_lines = None, []
            for raw in open(os.path.join(bp, fn), encoding="utf-8"):
                s = raw.strip()
                if not s: continue
                m = re.match(r"^(\d+):(\d+)$", s)
                if m:
                    if cur_ref: verses[cur_ref] = cur_lines
                    cur_ref = (int(m.group(1)), int(m.group(2)))
                    cur_lines = []
                elif cur_ref is not None:
                    cur_lines.append(raw.rstrip("\r\n"))
            if cur_ref: verses[cur_ref] = cur_lines
            for (ch, vs), lines in verses.items():
                vw = morph.get((ch, vs), [])
                if not vw: continue
                cmds = [(w, l) for w, pos, p, l in vw if is_cmd_verb(pos, p, l)]
                dat = has_unprepped_dative(vw)
                infs = [(w, l) for w, pos, p, l in vw if is_infinitive(pos, p)]
                if cmds and dat and infs:
                    out.append({
                        "file": f"{ent}/{fn}",
                        "ref": f"{ch}:{vs}",
                        "verse": " / ".join(lines),
                        "cmds": cmds,
                        "dat": dat,
                        "infs": infs,
                    })
    return out

if __name__ == "__main__":
    r = scan()
    print("=== R23 DATIVE-SUBJECT-OF-INFINITIVE EMPIRICAL SCAN ===\n")
    print("Question: does R23's pattern (command verb + dative + inf where dat = subj of inf)")
    print("fire beyond Rom 12:3? If canonical examples are ≤2-3 verses, R23 is one-verse crystallization.\n")
    print(f"{len(r)} candidate verses corpus-wide (broad net — Stan triages):\n")
    for x in r:
        print(f"{x['file']} {x['ref']}:")
        print(f"  {x['verse']}")
        print(f"  cmd-verbs: {', '.join(f'{w}({l})' for w,l in x['cmds'])}")
        print(f"  dative: {x['dat'][0]}({x['dat'][1]})")
        print(f"  infs: {', '.join(f'{w}({l})' for w,l in x['infs'])}")
        print()
