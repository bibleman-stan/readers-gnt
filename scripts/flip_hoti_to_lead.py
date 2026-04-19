#!/usr/bin/env python3
"""
flip_hoti_to_lead.py — Flip ὅτι from trailing-end-of-line-1 to leading-line-2.

Current (wrong): `λέγω δὲ ὑμῖν ὅτι / πολλοὶ ἀπὸ ἀνατολῶν ...`
Target: `λέγω δὲ ὑμῖν / ὅτι πολλοὶ ἀπὸ ἀνατολῶν ...`

Per R2/R8 discipline: subordinating conjunctions and framing particles lead
their content; they do not trail the previous line. ὅτι is a complementizer/
subordinator; treat it like καί, γάρ, ἵνα.

Dry-run default; --apply writes changes.

Usage: PYTHONIOENCODING=utf-8 py -3 scripts/flip_hoti_to_lead.py [--apply]
"""
import os, sys, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")

VERSE_RE = re.compile(r"^\d+:\d+\s*$")

# Match line ending with ὅτι (optionally followed by punctuation and whitespace)
HOTI_TRAILING_RE = re.compile(r"^(.+?\s)ὅτι(\s*)$")

def process_file(path, apply_changes):
    """Return list of flips applied."""
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    le = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.replace("\r\n", "\n").split("\n")
    flips = []
    new_lines = list(lines)
    i = 0
    while i < len(new_lines) - 1:
        line = new_lines[i]
        next_line = new_lines[i+1]
        m = HOTI_TRAILING_RE.match(line)
        if m and next_line.strip() and not VERSE_RE.match(next_line.strip()):
            # Don't flip if next line already starts with ὅτι (already flipped)
            if next_line.lstrip().startswith("ὅτι"):
                i += 1; continue
            # Flip: remove ὅτι from end of this line, prepend to next line
            new_prev = m.group(1).rstrip()
            # Preserve any trailing punct that was attached to ὅτι (there shouldn't
            # be any since we matched pure ὅτι + whitespace; but safeguard)
            new_next = "ὅτι " + next_line.lstrip()
            new_lines[i] = new_prev
            new_lines[i+1] = new_next
            flips.append((i, line, next_line, new_prev, new_next))
        i += 1
    if apply_changes and flips:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(le.join(new_lines))
    return flips

def main():
    apply_changes = "--apply" in sys.argv
    all_flips = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            path = os.path.join(bp, fn)
            flips = process_file(path, apply_changes)
            for f in flips:
                all_flips.append((os.path.join(ent, fn), f))
    mode = "APPLIED" if apply_changes else "DRY-RUN"
    print(f"=== ὅτι FLIP ({mode}) ===\n")
    print(f"{len(all_flips)} flips\n")
    for path, (idx, l1, l2, n1, n2) in all_flips[:10]:
        print(f"{path}")
        print(f"  BEFORE L{idx}:   {l1}")
        print(f"  BEFORE L{idx+1}: {l2}")
        print(f"  AFTER  L{idx}:   {n1}")
        print(f"  AFTER  L{idx+1}: {n2}")
        print()
    if len(all_flips) > 10:
        print(f"... and {len(all_flips)-10} more")

if __name__ == "__main__":
    main()
