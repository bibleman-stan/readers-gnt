#!/usr/bin/env python3
"""
sweep_r19_correct_acc.py — Corrective for sweep_r19_genabs.py's
accusative-predicate-slurp bug.

The prior sweep extended aggressively through accusative tokens, which
correctly handles accusative objects of the gen ptc (τὸν λόγον in Matt
13:19) but incorrectly absorbs main-clause predicates of infinitives
(ποταποὺς in 2 Pet 3:11 ποταποὺς δεῖ ὑπάρχειν).

Signature of the bug (in already-split v4-editorial state):
  line N: contains a gen-case participle AND ends on an accusative token
  line N+1: starts with a finite verb

Fix: move the trailing accusative(s) from line N to the start of line N+1.

Dry-run default; --apply writes changes.
Usage: PYTHONIOENCODING=utf-8 py -3 scripts/sweep_r19_correct_acc.py [--apply]
"""
import os, re, sys
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

def bind_line(text, verse_pool):
    out = []
    for raw in text.split():
        c = clean(raw)
        lst = verse_pool.get(c)
        if lst and lst[0] is not None:
            out.append(lst.pop(0))
        else:
            out.append(None)
    return out

def is_gen_ptc(pos, p):
    return pos.startswith("V") and len(p) >= 5 and p[3] == "P" and p[4] == "G"

def is_finite(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO"

def word_positions(line_text):
    out, i, n = [], 0, len(line_text)
    while i < n:
        while i < n and line_text[i].isspace(): i += 1
        if i >= n: break
        s = i
        while i < n and not line_text[i].isspace(): i += 1
        out.append((line_text[s:i], s, i))
    return out

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def process_chapter(chapter_path, morph, apply_changes):
    with open(chapter_path, encoding="utf-8") as f:
        raw_lines = f.readlines()
    out_edits = []
    i = 0
    new_lines = list(raw_lines)
    cur_ch, cur_vs = None, None
    # Walk and build verse→line-indexes map
    verse_line_idxs = {}
    for idx, raw in enumerate(raw_lines):
        s = raw.strip()
        m = VERSE_RE.match(s)
        if m:
            cur_ch, cur_vs = int(m.group(1)), int(m.group(2))
            verse_line_idxs.setdefault((cur_ch, cur_vs), []).append(idx)  # verse-ref line
        elif s and cur_ch is not None:
            verse_line_idxs.setdefault((cur_ch, cur_vs), []).append(idx)
    for (ch, vs), idxs in verse_line_idxs.items():
        verse_tokens = morph.get((ch, vs), [])
        if not verse_tokens: continue
        # Build a shared pool for the entire verse so positional binding
        # reflects order across lines
        shared_pool = defaultdict(list)
        for t in verse_tokens:
            shared_pool[t[0]].append(t)
        # For each content line in this verse, walk pairs (line_n, line_n+1)
        content_idxs = [k for k in idxs if not VERSE_RE.match(raw_lines[k].strip())]
        # Bind each content line to tokens, consuming the shared pool
        bindings = []
        for k in content_idxs:
            text = raw_lines[k].rstrip("\r\n")
            bound = []
            for raw, _s, _e in word_positions(text):
                c = clean(raw)
                if c in shared_pool and shared_pool[c]:
                    bound.append(shared_pool[c].pop(0))
                else:
                    bound.append(None)
            bindings.append((k, text, bound))
        # Now scan pairs
        for pi in range(len(bindings) - 1):
            idx_n, text_n, bound_n = bindings[pi]
            idx_m, text_m, bound_m = bindings[pi + 1]
            # Line N must contain a gen ptc
            if not any(b is not None and is_gen_ptc(b[1], b[2]) for b in bound_n):
                continue
            # Line N must end with accusative token(s) — find trailing acc run
            trail_count = 0
            for b in reversed(bound_n):
                if b is None: break
                pos, p = b[1], b[2]
                if len(p) >= 5 and p[4] == "A":
                    trail_count += 1
                else:
                    break
            if trail_count == 0:
                continue
            # If the acc trail is PP-governed (preposition immediately before
            # the first acc in the trail, e.g. εἰς Καφαρναοὺμ, διὰ τὸν λόγον),
            # it's a legitimate PP modifier of the gen ptc — NOT the sweep bug.
            # Bug signature is bare acc (ποταποὺς) with no preposition.
            first_trail = len(bound_n) - trail_count
            if first_trail > 0:
                prev = bound_n[first_trail - 1]
                if prev is not None and prev[1] == "P-":
                    continue
            # Line N+1 must start with a finite IMPERSONAL verb (δεῖ, χρή,
            # ἔξεστιν, πρέπει) followed within 3 tokens by an infinitive.
            # This is the specific construction where a bare accusative is
            # predicate-complement of the infinitive, which the gen-abs
            # sweep slurped up. Transitive main verbs (ἐκέλευσα + inf,
            # ἔκρινα + inf) take acc that's actually an object of the gen
            # ptc above, so those don't match.
            IMPERSONAL = {"δέω", "ἔξεστι", "ἔξεστιν", "χρή", "πρέπει"}
            has_imp_inf = False
            for fi, b in enumerate(bound_m[:2]):
                if b is None or not is_finite(b[1], b[2]): continue
                if b[3] not in IMPERSONAL: continue
                for b2 in bound_m[fi+1:fi+4]:
                    if b2 is None: continue
                    pos2, p2 = b2[1], b2[2]
                    if pos2.startswith("V") and len(p2) >= 4 and p2[3] == "N":
                        has_imp_inf = True; break
                break
            if not has_imp_inf:
                continue
            # We have a bug candidate — move trailing acc tokens from line N
            # to start of line N+1
            raw_tokens_n = word_positions(text_n)
            cut_at = raw_tokens_n[-trail_count][1]
            new_n = text_n[:cut_at].rstrip()
            moved = text_n[cut_at:].strip()
            new_m = (moved + " " + text_m).strip()
            eol_n = raw_lines[idx_n][len(raw_lines[idx_n].rstrip("\r\n")):]
            eol_m = raw_lines[idx_m][len(raw_lines[idx_m].rstrip("\r\n")):]
            new_lines[idx_n] = new_n + eol_n
            new_lines[idx_m] = new_m + eol_m
            out_edits.append({
                "ref": f"{ch}:{vs}",
                "before_n": text_n, "after_n": new_n,
                "before_m": text_m, "after_m": new_m,
                "moved": moved,
            })
    if apply_changes and out_edits:
        with open(chapter_path, "w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)
    return out_edits

def main(apply_changes):
    all_edits = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        slug = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(slug)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            edits = process_chapter(os.path.join(bp, fn), morph, apply_changes)
            for e in edits:
                all_edits.append((f"{ent}/{fn}", e))
    mode = "APPLIED" if apply_changes else "DRY-RUN"
    print(f"=== R19 ACC-PREDICATE CORRECTIVE ({mode}) ===\n")
    print(f"{len(all_edits)} corrections:\n")
    for fn, e in all_edits:
        print(f"{fn} {e['ref']}:  moved '{e['moved']}' from line 1 → line 2")
        print(f"  BEFORE 1: {e['before_n']}")
        print(f"  AFTER  1: {e['after_n']}")
        print(f"  BEFORE 2: {e['before_m']}")
        print(f"  AFTER  2: {e['after_m']}")
        print()

if __name__ == "__main__":
    apply_changes = "--apply" in sys.argv
    main(apply_changes)
