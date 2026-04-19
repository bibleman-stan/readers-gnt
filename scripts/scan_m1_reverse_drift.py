#!/usr/bin/env python3
"""
scan_m1_reverse_drift.py — Reverse M1 drift detector.

The forward M1 pipeline finds CURRENTLY-SPLIT pairs that should be merged
(hendiadys drift). This scanner does the inverse: find CURRENTLY-MERGED
same-line καί-joined pairs where BOTH halves carry independent finite
predication — i.e., two distinct atomic thoughts that shouldn't be on one
line per R12.

Signature:
  Line contains a καί/καὶ that splits it into two halves.
  Both halves contain a finite verb (mood I/S/D/O).
  Neither half is a subordinate clause (no ὅτι/ὅταν/ἵνα/ὅς/etc. leading
    either half; if present, that half is subordinate to the other).

Output: private/m1-reverse-drift-candidates.md — human-readable list.

This is an ENUMERATOR — no verdict, no agent dispatch. The output is for
human review (or future agent pipeline dispatch if Stan chooses).
"""
import os, re, json
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")

SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

VERSE_RE = re.compile(r"^(\d+):(\d+)$")
SUBORDINATORS = {"ὅτι","ὅταν","ὅτε","ἕως","ὡς","ἵνα","ὥστε","εἰ","ἐάν","καθώς","μήποτε","ὅς","ὅσος","ὅστις","ὅπου","ὅθεν","οὗ"}

def clean(w):
    return re.sub(r"[,.\;\·\s'\u2019\"\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]", "", w)

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

def bind_line(line_text, verse_pool):
    """Bind tokens from a shared verse-pool copy."""
    bound = []
    for raw in line_text.split():
        c = clean(raw)
        lst = verse_pool.get(c)
        if lst:
            bound.append(lst.pop(0))
        else:
            bound.append(None)
    return bound

def find_kai_splits(bound, raw_tokens):
    """Find positions of mid-line καί/καὶ that could split the line into halves.

    Only internal (non-first) positions qualify (first-position καί is the
    line-initial coordinator linking this line to the previous one).
    """
    positions = []
    for i, (raw, _, _) in enumerate(raw_tokens):
        if i == 0: continue
        c = clean(raw)
        if c in ("καί", "καὶ", "Καί", "Καὶ"):
            positions.append(i)
    return positions

def check_candidate(bound, raw_tokens, kai_idx):
    """Given a mid-line καί position, check if BOTH halves have a finite
    verb and neither half leads with a subordinator."""
    left = bound[:kai_idx]
    right = bound[kai_idx+1:]
    if not left or not right: return False, "edge"
    left_finite = any(b is not None and is_finite(b[1], b[2]) for b in left)
    right_finite = any(b is not None and is_finite(b[1], b[2]) for b in right)
    if not (left_finite and right_finite):
        return False, "not both finite"
    # Check for subordinators leading either half
    raw_right = raw_tokens[kai_idx+1:]
    if raw_right:
        first_right = clean(raw_right[0][0])
        if first_right in SUBORDINATORS:
            return False, f"right leads with subordinator {first_right}"
    raw_left_first = clean(raw_tokens[0][0])
    if raw_left_first in SUBORDINATORS:
        return False, f"left leads with subordinator {raw_left_first}"
    return True, None

def split_line_at_kai(text, kai_token_idx):
    """Return (left_text, right_text) based on splitting at the kai_token_idx-th
    whitespace-token position."""
    tokens_with_pos = []
    i, n = 0, len(text)
    while i < n:
        while i < n and text[i].isspace(): i += 1
        if i >= n: break
        s = i
        while i < n and not text[i].isspace(): i += 1
        tokens_with_pos.append((text[s:i], s, i))
    if kai_token_idx >= len(tokens_with_pos): return text, ""
    left = text[:tokens_with_pos[kai_token_idx][1]].rstrip()
    right = text[tokens_with_pos[kai_token_idx][1]:].lstrip()
    return left, right

def word_positions(text):
    out, i, n = [], 0, len(text)
    while i < n:
        while i < n and text[i].isspace(): i += 1
        if i >= n: break
        s = i
        while i < n and not text[i].isspace(): i += 1
        out.append((text[s:i], s, i))
    return out

def main():
    findings = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        book = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(book)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            verses = load_chapter(os.path.join(bp, fn))
            for ref, lines in verses:
                vw = morph.get(ref, [])
                for line in lines:
                    pool = defaultdict(list)
                    for t in vw: pool[t[0]].append(t)
                    bound = bind_line(line, pool)
                    raw_tokens = word_positions(line)
                    if len(raw_tokens) != len(bound):
                        continue
                    for kai_idx in find_kai_splits(bound, raw_tokens):
                        ok, why = check_candidate(bound, raw_tokens, kai_idx)
                        if ok:
                            left, right = split_line_at_kai(line, kai_idx)
                            findings.append({
                                "book": book,
                                "ref": f"{ref[0]}:{ref[1]}",
                                "line": line,
                                "left": left,
                                "right": right,
                            })
                            break  # first kai per line; don't double-flag
    out_md = os.path.join(REPO, "private", "m1-reverse-drift-candidates.md")
    lines = []
    lines.append("# M1 Reverse Drift — Currently-Merged Same-Line καί Pairs with Dual Finite Predication\n")
    lines.append(f"**Scanner:** `scripts/scan_m1_reverse_drift.py`\n")
    lines.append(f"**Count:** {len(findings)} candidates\n")
    lines.append("**Signature:** line contains mid-line καί splitting into two halves; both halves contain a finite verb (ISDO); neither half leads with a subordinator.\n")
    lines.append("**Interpretation:** these pairs may be R12-STACK candidates — two distinct predications currently on one line. Human or agent review needed; some will be legitimate shared-subject compounds or idiomatic verb-pairs.\n")
    by_book = defaultdict(int)
    for f in findings: by_book[f["book"]] += 1
    lines.append("## By book\n")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Full list\n")
    for f in findings:
        lines.append(f"**{f['book']} {f['ref']}** — currently one line:")
        lines.append(f"  `{f['line']}`")
        lines.append(f"  Proposed split:")
        lines.append(f"    `{f['left']}`")
        lines.append(f"    `{f['right']}`")
        lines.append("")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Reverse-drift candidates: {len(findings)}")
    print(f"Written: {out_md}")
    print("\nBy book (top 10):")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k:10s} {v}")

if __name__ == "__main__":
    main()
