#!/usr/bin/env python3
"""
validate_r19_genabs.py — R19 genitive-absolute rule-application validator.

R19: A genitive absolute always gets its own line. It is grammatically
independent by definition (own subject, own predicate, not governed by the
main clause), and is one of the few rules with no "unless" carve-outs.

Violation signature:
  Line contains a genitive participle + a genitive noun/pronoun agreeing
  with it (the absolute's subject), AND the line contains other content
  — typically a finite verb (the main clause) or additional predication
  beyond the absolute itself.

Heuristic for distinguishing gen-abs from adnominal gen-participle:
  Adnominal: an article (RA in genitive) immediately precedes the participle
    — "τοῦ καταβαίνοντος" etc. — participle qualifies a gen noun.
  Gen abs: no article directly on the participle; the ptc + gen noun/pronoun
    together constitute an independent mini-clause.

This is not perfect (some articular participles are predicative, some
anarthrous gen ptcs are adnominal), but it catches the canonical case:
e.g., Acts 1:9 βλεπόντων αὐτῶν ἐπήρθη — gen abs + main clause on one line
would fire.

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/validate_r19_genabs.py
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

def is_gen_ptc(pos, p):
    return pos.startswith("V") and len(p) >= 5 and p[3] == "P" and p[4] == "G"

def is_gen_nom_or_pro(pos, p):
    return pos in ("N-", "RP", "RD", "A-") and len(p) >= 5 and p[4] == "G"

def is_article(pos, p):
    return pos == "RA"

def is_finite(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO"

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

def preceded_by_prep(tokens, idx, window=3):
    """Is token at idx within `window` positions after a preposition (P-)?"""
    for k in range(max(0, idx-window), idx):
        if tokens[k][1] == "P-":
            return True
    return False

def gen_abs_candidates(tokens):
    """Return list of (ptc_word, gen_subj_word) where ptc is likely gen abs.

    Anarthrous gen ptc (no immediately preceding RA-gen, not PP-governed)
    + gen nom/pro within 3 positions (not PP-governed), with number+gender
    match. The PP-governed check excludes cases like `διὰ τοῦ προφήτου
    λέγοντος` where the gen ptc modifies a preposition-governed noun.
    """
    out = []
    for i, (w, pos, p, l) in enumerate(tokens):
        if not is_gen_ptc(pos, p): continue
        # Adnominal signals: article directly before, or PP-governed
        if i > 0:
            pw, ppos, pp, _ = tokens[i-1]
            if is_article(ppos, pp) and len(pp) >= 5 and pp[4] == "G":
                continue
        if preceded_by_prep(tokens, i, window=3):
            continue
        ptc_num = p[5] if len(p) >= 6 else ""
        ptc_gen = p[6] if len(p) >= 7 else ""
        for j in range(max(0, i-2), min(len(tokens), i+3)):
            if j == i: continue
            w2, pos2, p2, l2 = tokens[j]
            if not is_gen_nom_or_pro(pos2, p2): continue
            if preceded_by_prep(tokens, j, window=3):
                continue
            num2 = p2[5] if len(p2) >= 6 else ""
            gen2 = p2[6] if len(p2) >= 7 else ""
            if num2 == ptc_num and gen2 == ptc_gen:
                out.append((w, l, w2, l2))
                break
    return out

def validate_line(line_tokens, all_tokens):
    """Return (ptc_word, subj_word, finite_word) if line has gen abs + finite, else None."""
    cands = gen_abs_candidates(line_tokens)
    if not cands: return None
    fins = [(w, l) for w, pos, p, l in line_tokens if is_finite(pos, p)]
    if not fins: return None
    return (cands[0], fins[0])

def bind_line(text, verse_tokens):
    """Positionally pop verse-tokens to the line, return the line's slice of tokens."""
    pool = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    line_tokens = []
    for raw in text.split():
        c = clean(raw)
        if c in pool and pool[c]:
            line_tokens.append(pool[c].pop(0))
    return line_tokens

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
                    lt = bind_line(line, vw)
                    r = validate_line(lt, vw)
                    if r:
                        (ptc, ptc_l, subj, subj_l), (fin, fin_l) = r
                        out.append({
                            "file": f"{ent}/{fn}",
                            "ref": v["ref"],
                            "line": line,
                            "gen_abs": (ptc, ptc_l, subj, subj_l),
                            "finite": (fin, fin_l),
                        })
    return out

if __name__ == "__main__":
    r = validate()
    print("=== R19 GENITIVE-ABSOLUTE VALIDATOR ===\n")
    print("Rule R19: gen abs always own line (grammatically independent by definition).\n")
    print("Violation signature: anarthrous gen ptc + gen subj (agreeing) + finite verb on same line.")
    print("Heuristic excludes adnominal gen ptcs (those with a gen article directly preceding).\n")
    print(f"{len(r)} R19 violation candidates corpus-wide:\n")
    for x in r:
        ptc, ptc_l, subj, subj_l = x["gen_abs"]
        fin, fin_l = x["finite"]
        print(f"{x['file']} {x['ref']}:")
        print(f"  Line: {x['line']}")
        print(f"  Gen abs: {ptc}({ptc_l}) + {subj}({subj_l})")
        print(f"  Main finite: {fin}({fin_l})")
        print(f"  R19 verdict: gen abs should separate from main clause.")
        print()
