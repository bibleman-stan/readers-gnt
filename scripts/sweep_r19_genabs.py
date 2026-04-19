#!/usr/bin/env python3
"""
sweep_r19_genabs.py — R19 corrective sweep. Splits gen-abs-jammed lines
so the gen abs takes its own line per R19.

Split-point heuristic:
  Start at max(ptc_pos, subj_pos) = the last token of the gen-abs core.
  Extend rightward through:
    - prepositional phrases (skip P- + article(s) + optional adj + noun)
    - further gen-case tokens (gen-of modifiers)
  Stop at:
    - any finite verb (main clause begins)
    - interjections ἰδού / ἴδε
    - any non-gen non-prep content

Dry-run mode (default): prints proposed diffs. Apply mode (--apply): writes
v4-editorial files in place.

Usage:
  dry:   PYTHONIOENCODING=utf-8 py -3 scripts/sweep_r19_genabs.py
  apply: PYTHONIOENCODING=utf-8 py -3 scripts/sweep_r19_genabs.py --apply
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

def is_gen_ptc(pos, p):
    return pos.startswith("V") and len(p) >= 5 and p[3] == "P" and p[4] == "G"

def is_gen_nom(pos, p):
    return pos in ("N-", "RP", "RD", "A-") and len(p) >= 5 and p[4] == "G"

def is_finite(pos, p):
    return pos.startswith("V") and len(p) >= 4 and p[3] in "ISDO"

def is_article(pos):
    return pos == "RA"

def preceded_by_prep(tokens, idx, window=3):
    for k in range(max(0, idx-window), idx):
        if tokens[k][1] == "P-":
            return True
    return False

def bind_line(text, verse_pool):
    """Pop tokens into line order; returns list of (token, pool_idx, orig)."""
    out = []
    for raw in text.split():
        c = clean(raw)
        lst = verse_pool.get(c)
        if lst and lst[0] is not None:
            out.append(lst.pop(0))
    return out

def find_gen_abs(tokens):
    """Return (ptc_idx, subj_idx) or None."""
    for i, (w, pos, p, l) in enumerate(tokens):
        if not is_gen_ptc(pos, p): continue
        if i > 0 and is_article(tokens[i-1][1]) and len(tokens[i-1][2]) >= 5 and tokens[i-1][2][4] == "G":
            continue
        if preceded_by_prep(tokens, i, window=3):
            continue
        ptc_num = p[5] if len(p) >= 6 else ""
        ptc_gen = p[6] if len(p) >= 7 else ""
        for j in range(max(0, i-2), min(len(tokens), i+3)):
            if j == i: continue
            w2, pos2, p2, l2 = tokens[j]
            if not is_gen_nom(pos2, p2): continue
            if preceded_by_prep(tokens, j, window=3):
                continue
            num2 = p2[5] if len(p2) >= 6 else ""
            gen2 = p2[6] if len(p2) >= 7 else ""
            if num2 == ptc_num and gen2 == ptc_gen:
                return (i, j)
    return None

def split_endpoint(tokens, ptc_idx, subj_idx):
    """Compute token index AT WHICH the gen-abs line ends (inclusive).

    Aggressive: extend from the end of the gen-abs core forward, consuming
    all tokens (PPs, datives, accusatives, gen modifiers, additional gen
    participles) until we hit a finite verb or the interjection ἰδού/ἴδε
    — both strong markers of main-clause onset. This over-extends in rare
    cases (main-clause subject before main verb with no ἰδού signal), but
    under-extension errors were far more common in the conservative version
    and produced visibly broken splits (orphaning objects of the gen ptc).
    """
    end = max(ptc_idx, subj_idx)
    i = end + 1
    STOP_LEMMAS = {
        # interjection markers for main-clause onset
        "ἰδού", "ἴδε",
        # subordinators likely introducing next clause
        "ὅτε", "ἐπεί", "ἕως", "ὡς", "ὅταν",
        "εἰ", "ἐάν", "ἵνα", "ὥστε", "καθώς", "μήποτε",
        # relative/interrogative pronouns — introduce own clauses
        "ὅς", "ὅσος", "ὅστις", "τίς", "τί",
        "ὅπου", "ὅθεν", "οὗ",
        # οὐ-class negations (bind to indicative mains)
        "οὐ", "οὐκ", "οὐχ", "οὐχί", "οὐδέ",
        # μή is NOT in this list: it frequently negates a gen ptc
        # inside the absolute (μὴ ἐχόντων, μὴ συνιέντος, μὴ ὄντων).
    }
    while i < len(tokens):
        w, pos, p, l = tokens[i]
        if l in STOP_LEMMAS:
            break
        if is_finite(pos, p):
            break
        # Nominative token signals main-clause subject-before-verb (ὁ Ἰησοῦς ἐποίησεν,
        # μόνος ἦν); gen abs subject is in genitive, so nom here is not the gen abs's.
        if len(p) >= 5 and p[4] == "N":
            break
        end = i
        i += 1
    # Back off if endpoint is a dangling conjunction (R2 violation).
    # Conjunction lemmas never end a line, whether tagged C- (connector)
    # or D- (adverbial — e.g., καί "also" in Acts 28:9 is D-, not C-).
    TRAIL_LEMMAS = {"καί", "δέ", "ἀλλά", "γάρ", "οὖν", "τέ", "μέν"}
    while end > max(ptc_idx, subj_idx) and tokens[end][3] in TRAIL_LEMMAS:
        end -= 1
    # Back off accusative endpoints immediately before the main-clause
    # finite verb: these are typically main-clause predicates of an
    # infinitive (ποταποὺς δεῖ ὑπάρχειν, 2 Pet 3:11), not arguments of
    # the gen ptc. Objects of the gen ptc normally sit next to the ptc,
    # not at the far end of the extension.
    while (end > max(ptc_idx, subj_idx)
           and len(tokens[end][2]) >= 5 and tokens[end][2][4] == "A"
           and end + 1 < len(tokens)
           and is_finite(tokens[end+1][1], tokens[end+1][2])):
        end -= 1
    return end

def word_positions(line_text):
    """Return list of (raw_word, start_index, end_index_exclusive) in original spacing."""
    out = []
    i = 0
    n = len(line_text)
    while i < n:
        while i < n and line_text[i].isspace():
            i += 1
        if i >= n: break
        start = i
        while i < n and not line_text[i].isspace():
            i += 1
        out.append((line_text[start:i], start, i))
    return out

def compute_split(line_text, verse_tokens_view):
    """Return (index_after_split, split_line_1, split_line_2) or None."""
    # Build pool from verse_tokens_view and bind to this line
    pool = defaultdict(list)
    for t in verse_tokens_view:
        pool[t[0]].append(t)
    # Walk the line and bind tokens in order
    raw_positions = word_positions(line_text)
    bound = []  # list of morph tokens in line order
    for raw, s, e in raw_positions:
        c = clean(raw)
        if c in pool and pool[c]:
            bound.append(pool[c].pop(0))
        else:
            bound.append(None)
    # Find gen abs in bound sequence
    tok_seq = [b if b is not None else ("", "", "", "") for b in bound]
    ga = find_gen_abs(tok_seq)
    if ga is None:
        return None
    ptc_idx, subj_idx = ga
    # Adnominal-λέγοντος exclusion: pattern "[gen NP] λέγοντος· Quote"
    # where the gen NP is governed by a main-clause verb of perception
    # (ἤκουσα τοῦ ζῴου λέγοντος· Ἔρχου). Narrow signature: gen ptc's
    # lemma is a speech verb AND the ptc's raw token in the line has an
    # attached ano teleia or colon (the ptc directly precedes the
    # speech-boundary marker, not · somewhere else on the line).
    if tok_seq[ptc_idx][3] in ("λέγω", "φημί"):
        raw_positions = word_positions(line_text)
        if ptc_idx < len(raw_positions):
            raw_ptc = raw_positions[ptc_idx][0]
            if raw_ptc.endswith("·") or raw_ptc.endswith(":"):
                return None
    # Line must have a finite verb that is NOT obviously subordinate.
    # A finite verb preceded within 2 positions by τί/τίς/ὅς/ὅπου/ὅταν/etc.
    # is inside an embedded clause (indirect question, relative), not
    # the main clause — so R19 isn't violated on this line.
    SUB_MARKERS = {"τί", "τίς", "ὅς", "ὅσος", "ὅστις", "ὅπου", "ὅθεν",
                   "οὗ", "ὅτε", "ἕως", "ὅταν", "ὅτι", "ἵνα", "ὥστε",
                   "εἰ", "ἐάν", "καθώς"}
    fin_idx = None
    for i, t in enumerate(tok_seq):
        if i <= max(ptc_idx, subj_idx): continue
        if not is_finite(t[1], t[2]): continue
        sub = False
        for k in range(max(0, i-2), i):
            if tok_seq[k][3] in SUB_MARKERS:
                sub = True; break
        if not sub:
            fin_idx = i; break
    if fin_idx is None:
        return None
    end_idx = split_endpoint(tok_seq, ptc_idx, subj_idx)
    # Split goes between raw_positions[end_idx] and raw_positions[end_idx+1]
    if end_idx + 1 >= len(raw_positions):
        return None
    line1 = line_text[:raw_positions[end_idx][2]]
    line2 = line_text[raw_positions[end_idx+1][1]:]
    return (end_idx, line1.rstrip(), line2.lstrip())

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def process_chapter(chapter_path, morph, apply_changes):
    """Process one chapter file. Return list of (ref, original, new1, new2)."""
    out = []
    with open(chapter_path, encoding="utf-8") as f:
        raw_lines = f.readlines()
    new_lines = []
    cur_ch, cur_vs = None, None
    for raw in raw_lines:
        stripped = raw.rstrip("\r\n")
        s = stripped.strip()
        m = VERSE_RE.match(s)
        if m:
            cur_ch, cur_vs = int(m.group(1)), int(m.group(2))
            new_lines.append(raw)
            continue
        if not s or cur_ch is None:
            new_lines.append(raw)
            continue
        verse_tokens = morph.get((cur_ch, cur_vs), [])
        result = compute_split(stripped, verse_tokens)
        if result is not None:
            end_idx, l1, l2 = result
            out.append((f"{cur_ch}:{cur_vs}", stripped, l1, l2))
            # Preserve line ending
            eol = raw[len(stripped):]
            new_lines.append(l1 + eol)
            new_lines.append(l2 + eol)
        else:
            new_lines.append(raw)
    if apply_changes and out:
        with open(chapter_path, "w", encoding="utf-8", newline="") as f:
            f.writelines(new_lines)
    return out

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
                all_edits.append((f"{ent}/{fn}", *e))
    mode = "APPLIED" if apply_changes else "DRY-RUN"
    print(f"=== R19 SWEEP ({mode}) ===\n")
    print(f"{len(all_edits)} splits proposed:\n")
    for fn, ref, orig, l1, l2 in all_edits:
        print(f"{fn} {ref}:")
        print(f"  BEFORE: {orig}")
        print(f"  AFTER:  {l1}")
        print(f"          {l2}")
        print()

if __name__ == "__main__":
    apply_changes = "--apply" in sys.argv
    main(apply_changes)
