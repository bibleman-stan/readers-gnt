#!/usr/bin/env python3
"""
scan_bare_subject.py — M3 violation detector: lines with nominative substantive but no finite verb.

A nominative subject on its own line without its predicate fails the atomic-thought test.
Canonical case: John 3:8 line `τὸ πνεῦμα` alone (subject of πνεῖ on next line).
Uses MorphGNT POS tags. Review pass triages FPs (vocatives, portrait-building, speech-intros).

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/scan_bare_subject.py
"""
import os, re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")
SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

def clean(w): return re.sub(r'[,.\;\·\s⸀⸁⸂⸃⸄⸅\'\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]', '', w)

def load_morph(slug):
    if slug in _cache: return _cache[slug]
    fn = SLUG_TO_FN.get(slug)
    path = next((os.path.join(MORPH, f) for f in os.listdir(MORPH) if fn and f.startswith(fn+"-")), None)
    if not path: _cache[slug] = {}; return {}
    verses = defaultdict(list)
    for line in open(path, encoding="utf-8"):
        parts = line.strip().split(" ", 6)
        if len(parts) < 7: continue
        ref, pos, parsing, _, word, _n, lemma = parts
        c = clean(word)
        if c: verses[(int(ref[2:4]), int(ref[4:6]))].append((c, pos, parsing, lemma))
    _cache[slug] = dict(verses); return _cache[slug]

def is_finite(pos, p): return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO"
def is_nom(pos, p): return pos in ("N-","RA","RP","RD","RR","RI","A-") and len(p) >= 5 and p[4] == "N"

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def parse_chapter(fp):
    verses, cur = [], None
    for raw in open(fp, encoding="utf-8"):
        s = raw.strip()
        if not s: continue
        m = VERSE_RE.match(s)
        if m:
            if cur: verses.append(cur)
            cur = {"ref":s, "ch":int(m.group(1)), "vs":int(m.group(2)), "lines":[]}
        elif cur: cur["lines"].append(raw.rstrip("\r\n"))
    if cur: verses.append(cur)
    return verses

def analyze(text, words):
    pool = defaultdict(list)
    for w,pos,p,l in words: pool[w].append((pos,p,l))
    has_nom, has_finite, noms = False, False, []
    for raw in text.split():
        c = clean(raw)
        if c in pool and pool[c]:
            pos, p, lemma = pool[c].pop(0)
            if is_finite(pos, p): has_finite = True
            if is_nom(pos, p): has_nom = True; noms.append((c, lemma))
    return has_nom, has_finite, noms

def scan():
    out = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        slug = parts[1] if len(parts)==2 and parts[0].isdigit() else ent
        morph = load_morph(slug)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            for v in parse_chapter(os.path.join(bp, fn)):
                vw = morph.get((v["ch"], v["vs"]), [])
                if not vw: continue
                for line in v["lines"]:
                    hn, hf, noms = analyze(line, vw)
                    if hn and not hf:
                        out.append({"file": f"{ent}/{fn}", "ref": v["ref"], "line": line, "noms": noms})
    return out

if __name__ == "__main__":
    r = scan()
    print(f"=== BARE-SUBJECT (M3) SCAN ===\n\n{len(r)} candidates: lines with nominative substantive but no finite verb\n")
    for x in r:
        print(f"{x['file']} {x['ref']}:\n  {x['line']}\n  noms: {', '.join(f'{w}({l})' for w,l in x['noms'])}\n")
