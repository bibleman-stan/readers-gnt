#!/usr/bin/env python3
"""
enumerate_m1_candidates.py — properly-scoped M1 gorgianic-pair candidate
enumerator (rebuild after 2026-04-18 scope failure).

M1 preconditions enforced BEFORE agent dispatch:

  1. COORDINATOR SCOPE — M1 applies to καί-joined (or asyndetic) N=2 pairs.
     Correlative pairs (εἴτε/οὔτε/μήτε/οὐδέ/μηδέ) are a DIFFERENT rule class
     and are routed out. ἀλλά (antithetical), δέ (discourse pivot), ἤ
     (alternative) are also not M1. This scan surfaces only καί-initial
     line-2 pairs.

  2. PREDICATION FILTER — if BOTH lines carry an independent finite verb
     (mood I/S/D/O as the main predication), they're STACK by definition —
     two distinct predications cannot be hendiadys. Reject before dispatch.

  3. LENGTH — both lines ≤ MAX_TOKENS=5. M1 is tight-bonded; long members
     are structurally ineligible.

Output: private/m1-v2-candidates.json — JSON array of surviving candidates
with context and MorphGNT features for agent adjudication.

Asyndetic M1 (like 2 Pet 2:10 Τολμηταί αὐθάδεις) is NOT handled here —
it's a separate detection problem (morphology-matching agreement scan).
"""
import os, re, json
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
ENG = os.path.join(REPO, "data", "text-files", "eng-gloss")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")

MAX_TOKENS = 5
CONTEXT_LINES = 3

SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

KAI_FORMS = {"καί", "καὶ", "Καί", "Καὶ"}
# Everything else starting a line-2 marks a DIFFERENT rule class; we skip:
CORRELATIVES = {"εἴτε", "οὔτε", "μήτε", "οὐδέ", "οὐδὲ", "μηδέ", "μηδὲ"}
ANTITHESIS = {"ἀλλά", "ἀλλὰ"}
ALTERNATIVE = {"ἤ", "ἢ"}
DISCOURSE = {"δέ", "δὲ"}

def clean(w):
    return re.sub(r"[,.\;\·\s'\u2019\"\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]", "", w)

def tokenize(line):
    return [clean(t) for t in line.split() if clean(t)]

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

def is_finite(pos, parsing):
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in "ISDO"

def bind_line(line_text, verse_pool_copy):
    """Pop line tokens from a shared verse pool (left-to-right)."""
    bound = []
    for raw in line_text.split():
        c = clean(raw)
        lst = verse_pool_copy.get(c)
        if lst:
            bound.append(lst.pop(0))
    return bound

def line_has_finite_predicate(bound):
    for _, pos, p, _ in bound:
        if is_finite(pos, p):
            return True
    return False

def classify_coord(line):
    toks = tokenize(line)
    if not toks: return None
    first = toks[0]
    if first in KAI_FORMS: return "καί"
    if first in CORRELATIVES: return "correlative"
    if first in ANTITHESIS: return "ἀλλά"
    if first in ALTERNATIVE: return "ἤ"
    if first in DISCOURSE: return "δέ"
    return None  # no recognized coordinator → asyndetic (skip for now)

def load_chapter(path):
    verses = []
    cur_ref, cur_lines = None, []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            m = VERSE_RE.match(s)
            if m:
                if cur_ref is not None:
                    verses.append((cur_ref, cur_lines))
                cur_ref = (int(m.group(1)), int(m.group(2)))
                cur_lines = []
            elif s:
                cur_lines.append(s)
        if cur_ref is not None:
            verses.append((cur_ref, cur_lines))
    return verses

def load_english(eng_path):
    out = {}
    cur_ref, cur_lines = None, []
    if not os.path.isfile(eng_path):
        return out
    with open(eng_path, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            m = VERSE_RE.match(s)
            if m:
                if cur_ref is not None:
                    out[cur_ref] = cur_lines
                cur_ref = (int(m.group(1)), int(m.group(2)))
                cur_lines = []
            elif s and cur_ref is not None:
                cur_lines.append(s)
        if cur_ref is not None:
            out[cur_ref] = cur_lines
    return out

def process_chapter(v4_path, eng_path, book, morph):
    verses = load_chapter(v4_path)
    english = load_english(eng_path)
    out = []
    rejected = defaultdict(int)
    for vi, (ref, lines) in enumerate(verses):
        verse_tokens = morph.get(ref, [])
        for i in range(len(lines) - 1):
            line1, line2 = lines[i], lines[i+1]
            coord = classify_coord(line2)
            # Route non-M1 coordinators out
            if coord != "καί":
                if coord is not None:
                    rejected[f"coord_{coord}"] += 1
                else:
                    rejected["asyndetic"] += 1
                continue
            # SERIES FILTER: if line1 or line_i+2 also starts with καί,
            # this pair is inside a longer N=3+ series, not a bonded N=2
            # pair. M1 is N=2 specifically. Triadic / extended series are
            # R12 territory (parallel stacking), not M1.
            prev_line = lines[i-1] if i > 0 else ""
            next_next_line = lines[i+2] if i+2 < len(lines) else ""
            if classify_coord(line1) == "καί":
                rejected["series_prev_kai"] += 1; continue
            if classify_coord(next_next_line) == "καί":
                rejected["series_next_kai"] += 1; continue
            t1 = tokenize(line1)
            t2 = tokenize(line2)
            # Length filter
            if not t1 or len(t1) > MAX_TOKENS:
                rejected["line1_too_long"] += 1; continue
            if len(t2) < 2 or len(t2) > MAX_TOKENS:
                rejected["line2_too_long"] += 1; continue
            # Predication filter — bind both lines to morphology and check
            # whether BOTH carry an independent finite verb.
            pool = defaultdict(list)
            for t in verse_tokens:
                pool[t[0]].append(t)
            b1 = bind_line(line1, pool)
            b2 = bind_line(line2, pool)
            if line_has_finite_predicate(b1) and line_has_finite_predicate(b2):
                rejected["both_finite"] += 1
                continue
            # Context
            prev_lines = lines[max(0, i-CONTEXT_LINES):i]
            next_lines = lines[i+2:i+2+CONTEXT_LINES]
            out.append({
                "book": book,
                "ref": f"{ref[0]}:{ref[1]}",
                "coord": "καί",
                "line1": line1,
                "line2": line2,
                "tokens_line1": len(t1),
                "tokens_line2": len(t2),
                "line1_has_finite": line_has_finite_predicate(b1),
                "line2_has_finite": line_has_finite_predicate(b2),
                "context_before": prev_lines,
                "context_after": next_lines,
                "english": english.get(ref, []),
            })
    return out, rejected

def main():
    all_cands = []
    agg_rej = defaultdict(int)
    for ent in sorted(os.listdir(V4)):
        bp_v4 = os.path.join(V4, ent)
        bp_eng = os.path.join(ENG, ent)
        if not os.path.isdir(bp_v4): continue
        parts = ent.split("-", 1)
        book = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(book)
        for fn in sorted(os.listdir(bp_v4)):
            if not fn.endswith(".txt"): continue
            v4_path = os.path.join(bp_v4, fn)
            eng_path = os.path.join(bp_eng, fn) if os.path.isdir(bp_eng) else ""
            cands, rej = process_chapter(v4_path, eng_path, book, morph)
            all_cands.extend(cands)
            for k, v in rej.items(): agg_rej[k] += v
    for i, c in enumerate(all_cands):
        c["_id"] = f"m1v2-{i:04d}"
    out_path = os.path.join(REPO, "private", "m1-v2-candidates.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_cands, f, ensure_ascii=False, indent=1)
    print(f"=== M1 V2 ENUMERATION ===\n")
    print(f"Surviving candidates (καί, both ≤{MAX_TOKENS} tokens, NOT both-finite): {len(all_cands)}\n")
    print(f"Rejected by filter:")
    for k, v in sorted(agg_rej.items(), key=lambda x: -x[1]):
        print(f"  {k:25s} {v}")
    print(f"\nWritten: {out_path}")
    # By book
    by_book = defaultdict(int)
    for c in all_cands: by_book[c["book"]] += 1
    print(f"\nBy book (top 15):")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1])[:15]:
        print(f"  {k:10s} {v}")

if __name__ == "__main__":
    main()
