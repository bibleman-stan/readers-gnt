#!/usr/bin/env python3
"""
validate_r18_vocative.py — R18 vocative rule-application validator.

R18 default: each vocative-addressed element occupies its own line.
R18 unless (appositive merge): vocative merges into a line containing a 2p
  element (2p finite verb or 2p pronoun) — the addressee the vocative names.
R18 unless (stacked parallel, N>=3): parallel vocative appositions each own line.
M1 override (judgment, not validated here): N=2 coordinate vocative pair may
  bond onto one line if they form a unified image.

Violation signature (the rule-application test, not a shape detector):
  line has vocative(s)
  AND line has at least one finite verb that is NOT 2p
  AND line has no 2p pronoun
  AND line has no 2p finite verb

This captures the Acts 13:26 jam: vocative(s) + third-person predication on
same line with no 2p addressee element. It does NOT fire on:
  - vocative-only lines (no finite verb present)
  - `Ὕπαγε, Σατανᾶ` (2p imperative present → R18 appositive merge territory)
  - compound vocative joined by καί (M1 bonded-pair territory; no finite verb)

Unlike scan_vocative_jam.py (shape: vocative + any finite verb → 209 noisy
candidates), this validator applies the rule's actual logic, so the output
should be small and high-signal.

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/validate_r18_vocative.py
"""
import os, re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")
SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

def clean(w):
    return re.sub(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]', '', w)

def load_morph(slug):
    if slug in _cache: return _cache[slug]
    fn = SLUG_TO_FN.get(slug)
    path = next((os.path.join(MORPH, f) for f in os.listdir(MORPH) if fn and f.startswith(fn+"-")), None)
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

def is_finite(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO"

def is_voc(pos, p):
    return pos in ("N-","A-","RP","RD") and len(p) >= 5 and p[4] == "V"

def is_2p_verb(pos, p):
    return is_finite(pos, p) and len(p) >= 1 and p[0] == "2"

def is_2p_pronoun(pos, p, lemma):
    # MorphGNT RP parsing doesn't encode person in parsing[0] for pronouns
    # (it's `-`); person is carried by the lemma. σύ = 2p (sg + pl both
    # lemmatize to σύ in MorphGNT).
    return pos == "RP" and lemma == "σύ"

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def parse_chapter(fp):
    verses, cur = [], None
    for raw in open(fp, encoding="utf-8"):
        s = raw.strip()
        if not s: continue
        m = VERSE_RE.match(s)
        if m:
            if cur: verses.append(cur)
            cur = {"ref": s, "ch": int(m.group(1)), "vs": int(m.group(2)), "lines": []}
        elif cur:
            cur["lines"].append(raw.rstrip("\r\n"))
    if cur: verses.append(cur)
    return verses

def classify_line(text, words):
    """Return (vocs, fins_non2p, twop_verbs, twop_pros) — lists of (word, lemma)."""
    pool = defaultdict(list)
    for w, pos, p, l in words:
        pool[w].append((pos, p, l))
    vocs, fins_non2p, twop_v, twop_p = [], [], [], []
    for raw in text.split():
        c = clean(raw)
        if c in pool and pool[c]:
            pos, p, lemma = pool[c].pop(0)
            if is_voc(pos, p):
                vocs.append((c, lemma))
            if is_2p_verb(pos, p):
                twop_v.append((c, lemma))
            elif is_finite(pos, p):
                fins_non2p.append((c, lemma))
            if is_2p_pronoun(pos, p, lemma):
                twop_p.append((c, lemma))
    return vocs, fins_non2p, twop_v, twop_p

def validate():
    out = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(slug)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            for v in parse_chapter(os.path.join(bp, fn)):
                vw = morph.get((v["ch"], v["vs"]), [])
                if not vw: continue
                for line in v["lines"]:
                    vocs, fins, twop_v, twop_p = classify_line(line, vw)
                    if vocs and fins and not twop_v and not twop_p:
                        out.append({
                            "file": f"{ent}/{fn}",
                            "ref": v["ref"],
                            "line": line,
                            "vocs": vocs,
                            "fins_non2p": fins,
                        })
    return out

if __name__ == "__main__":
    r = validate()
    print("=== R18 VOCATIVE VALIDATOR ===\n")
    print("Rule R18 default: vocative on own line.")
    print("Unless R18 appositive-merge: 2p element on line (2p verb or 2p pronoun).")
    print("Unless R18 stacked-parallel: N>=3 parallel vocatives each own line.")
    print("M1 (judgment) override for N=2 coordinate pair not validated here.\n")
    print("Violation signature: vocative + finite non-2p verb + no 2p pronoun + no 2p verb.")
    print("This is the rule's actual logic, not a shape match. Output should be small.\n")
    print(f"{len(r)} R18 violation candidates corpus-wide:\n")
    for x in r:
        print(f"{x['file']} {x['ref']}:")
        print(f"  Line: {x['line']}")
        print(f"  Vocatives: {', '.join(f'{w}({l})' for w,l in x['vocs'])}")
        print(f"  Non-2p finite: {', '.join(f'{w}({l})' for w,l in x['fins_non2p'])}")
        print(f"  R18 verdict: no 2p element on line → vocative should separate from predication.")
        print()
