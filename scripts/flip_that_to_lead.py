#!/usr/bin/env python3
"""
flip_that_to_lead.py — mirror English flip for the Greek ὅτι-lead flip.

When a Greek line-pair has been flipped from `... ὅτι / content` to `... /
ὅτι content`, the corresponding English line-pair should flip too: move
"that" (or the line-ending equivalent) from end of line N to start of
line N+1, so English alignment continues to mirror Greek structure.

Operates on eng-gloss/ files. Reads corresponding v4-editorial/ to find
which verses have ὅτι-leading-line-N+1, then finds the English line that
ends in "that" / "that," / similar and flips.

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/flip_that_to_lead.py [--apply]
"""
import os, sys, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
ENG = os.path.join(REPO, "data", "text-files", "eng-gloss")

VERSE_RE = re.compile(r"^(\d+):(\d+)\s*$")

# Words that might "trail" at end of English line when they should lead next
# For the ὅτι flip specifically: just "that" in various surface forms.
TRAILING_WORDS_RE = re.compile(r"^(.+?)\s+(that|That)\s*$")

def load_file(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    le = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")
    return lines, le

def parse_verses(lines):
    """Return list of (ref, [(line_idx_in_file, line_content)])."""
    verses = []
    cur_ref, cur = None, []
    for i, l in enumerate(lines):
        m = VERSE_RE.match(l.strip())
        if m:
            if cur_ref is not None:
                verses.append((cur_ref, cur))
            cur_ref = m.group(0).strip()
            cur = []
        elif l.strip() and cur_ref:
            cur.append((i, l))
    if cur_ref is not None:
        verses.append((cur_ref, cur))
    return verses

def process_pair(v4_path, eng_path, apply_changes):
    """For each verse where Greek has ὅτι-leading line at pos K (matching
    the post-flip state), check English: if English line K-1 ends with
    'that', flip 'that' from end of K-1 to start of K."""
    if not os.path.isfile(eng_path): return []
    v4_lines, _ = load_file(v4_path)
    eng_lines, le = load_file(eng_path)
    v4_verses = parse_verses(v4_lines)
    eng_verses = parse_verses(eng_lines)
    # Map ref → eng content lines
    eng_map = {ref: content for ref, content in eng_verses}
    flips = []
    new_eng_lines = list(eng_lines)
    for ref, v4_content in v4_verses:
        eng_content = eng_map.get(ref)
        if not eng_content: continue
        if len(eng_content) != len(v4_content): continue  # mismatched; skip
        # For each Greek line that starts with ὅτι (positions 1..n-1, not line 0)
        for k in range(1, len(v4_content)):
            _, gk = v4_content[k]
            if not gk.lstrip().startswith("ὅτι"): continue
            # Corresponding English line at index k-1: does it end with "that"?
            eng_idx_k_minus_1, eng_k_minus_1 = eng_content[k-1]
            eng_idx_k, eng_k = eng_content[k]
            m = TRAILING_WORDS_RE.match(eng_k_minus_1)
            if not m: continue
            new_prev = m.group(1).rstrip()
            # Preserve case of "that" if starting a new line
            that_word = m.group(2)
            # If next line starts with lowercase, prepend "that" lowercase
            new_next = that_word + " " + eng_k.lstrip()
            new_eng_lines[eng_idx_k_minus_1] = new_prev
            new_eng_lines[eng_idx_k] = new_next
            flips.append((ref, eng_k_minus_1, eng_k, new_prev, new_next))
    if apply_changes and flips:
        with open(eng_path, "w", encoding="utf-8", newline="") as f:
            f.write(le.join(new_eng_lines))
    return flips

def main():
    apply_changes = "--apply" in sys.argv
    all_flips = []
    for ent in sorted(os.listdir(V4)):
        bp_v4 = os.path.join(V4, ent)
        bp_eng = os.path.join(ENG, ent)
        if not os.path.isdir(bp_v4): continue
        for fn in sorted(os.listdir(bp_v4)):
            if not fn.endswith(".txt"): continue
            v4_path = os.path.join(bp_v4, fn)
            eng_path = os.path.join(bp_eng, fn) if os.path.isdir(bp_eng) else ""
            if not eng_path: continue
            flips = process_pair(v4_path, eng_path, apply_changes)
            for f in flips:
                all_flips.append((os.path.join(ent, fn), f))
    mode = "APPLIED" if apply_changes else "DRY-RUN"
    print(f"=== ENGLISH 'that' FLIP ({mode}) ===\n")
    print(f"{len(all_flips)} flips\n")
    for path, (ref, l1, l2, n1, n2) in all_flips[:10]:
        print(f"{path} {ref}")
        print(f"  BEFORE: {l1}")
        print(f"          {l2}")
        print(f"  AFTER:  {n1}")
        print(f"          {n2}")
        print()
    if len(all_flips) > 10:
        print(f"... and {len(all_flips)-10} more")

if __name__ == "__main__":
    main()
