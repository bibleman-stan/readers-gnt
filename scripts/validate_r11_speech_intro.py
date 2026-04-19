#!/usr/bin/env python3
"""
validate_r11_speech_intro.py — R11 direct-speech-introduction validator.

R11: speech-intro verb (λέγω, εἶπον, φημί + similar) + its frame (dative
indirect object, any qualifying clause now absorbed per R25 fold) gets its
own line. The quoted speech begins on the next line.

Violation signature:
  A line contains a speech-intro verb AND the line also carries content
  that looks like the beginning of the quoted speech (i.e., content past
  the frame). Operational proxy: the line ends without a colon/ano teleia
  (speech-intro boundary marker) AND contains post-frame content after
  the verb + dative.

This is a heuristic: editorial punctuation in v4-editorial is non-original,
so we use it for structural inference only, not as the rule's basis.
Primary signal: speech-intro verb present + line also contains imperative
or direct-address predication beyond the frame.

Excluded from violation (R11 allows these):
  - speech intro with full frame on one line ending in colon/ano teleia
  - synonymous-doublet imperative merge (Mark 4:39 Σιωπα, πεφίμωσο)
  - participial speech-intro forms (λέγων, εἰπών) — these are framing,
    not the main speech-intro predication

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/validate_r11_speech_intro.py
"""
import os, re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")
SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

SPEECH_LEMMAS = {
    "λέγω", "φημί", "ἀποκρίνομαι",
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

def is_finite_speech(pos, p, lemma):
    """Narrow: narrative speech-intros (εἶπεν, ἔλεγεν, φησίν, ἀπεκρίθη).
    Aorist or imperfect or present indicative, 3rd person, mood = indicative.
    Excludes 1p/2p forms (which are usually conversational, not narrative frames),
    imperatives, subjunctives, optatives, participles."""
    if not pos.startswith("V"): return False
    if lemma not in SPEECH_LEMMAS: return False
    if len(p) < 4: return False
    person, tense, _, mood = p[0], p[1], p[2], p[3]
    if mood != "I": return False
    if person != "3": return False
    if tense not in ("A", "I", "P"): return False
    return True

def is_imperative(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] == "D"

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

def bind_line(text, verse_tokens):
    pool = defaultdict(list)
    for t in verse_tokens:
        pool[t[0]].append(t)
    line_tokens = []
    for raw in text.split():
        c = clean(raw)
        if c in pool and pool[c]:
            line_tokens.append(pool[c].pop(0))
    return line_tokens

def ends_with_speech_boundary(line):
    """Does the line end with colon or ano teleia (speech-intro boundary)?"""
    stripped = line.rstrip()
    return stripped.endswith(":") or stripped.endswith("·")

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
                    speech_verbs = [(w, l) for w, pos, p, l in lt
                                    if is_finite_speech(pos, p, l)]
                    if not speech_verbs:
                        continue
                    # Line has a finite speech verb. Direct-speech violation
                    # signature (narrowed):
                    #   - line does NOT end in colon/ano teleia
                    #   - line does NOT contain ὅτι (would be indirect speech
                    #     per R10, outside R11's scope)
                    #   - line contains another finite verb or imperative
                    if ends_with_speech_boundary(line):
                        continue
                    has_hoti = any(l == "ὅτι" for w, pos, p, l in lt)
                    if has_hoti:
                        continue
                    other_fins = [(w, l) for w, pos, p, l in lt
                                  if is_finite(pos, p)
                                  and not (is_finite_speech(pos, p, l))]
                    imps = [(w, l) for w, pos, p, l in lt if is_imperative(pos, p)]
                    if other_fins or imps:
                        out.append({
                            "file": f"{ent}/{fn}",
                            "ref": v["ref"],
                            "line": line,
                            "speech_verbs": speech_verbs,
                            "other_fins": other_fins,
                            "imps": imps,
                        })
    return out

if __name__ == "__main__":
    r = validate()
    print("=== R11 DIRECT-SPEECH-INTRODUCTION VALIDATOR ===\n")
    print("Rule R11: speech-intro verb + frame on its own line; quoted content follows on next line.\n")
    print("Violation signature: line has finite speech-intro verb AND does not end on ano teleia/colon")
    print("AND line carries a second finite verb or imperative (suggesting quoted content leaked in).\n")
    print(f"{len(r)} R11 violation candidates corpus-wide:\n")
    for x in r:
        print(f"{x['file']} {x['ref']}:")
        print(f"  Line: {x['line']}")
        print(f"  Speech verbs: {', '.join(f'{w}({l})' for w,l in x['speech_verbs'])}")
        if x["other_fins"]:
            print(f"  Other finite: {', '.join(f'{w}({l})' for w,l in x['other_fins'])}")
        if x["imps"]:
            print(f"  Imperatives: {', '.join(f'{w}({l})' for w,l in x['imps'])}")
        print()
