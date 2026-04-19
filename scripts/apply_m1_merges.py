#!/usr/bin/env python3
"""
apply_m1_merges.py — Apply M1 merges surviving adversarial Opus review.

Reads the 22 v2 survivors from private/m1-v2-adv/adversarial.json, joins
each candidate's line1 + line2 into a single line in v4-editorial, and
writes the files back. Dry-run by default; --apply writes changes.
"""
import os, sys, json, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
PRIV = os.path.join(REPO, "private")

def find_book_dir(book):
    for ent in sorted(os.listdir(V4)):
        if "-" in ent and ent.split("-", 1)[1] == book:
            return os.path.join(V4, ent)
    return None

def find_chapter_file(bdir, ref):
    """Given 'N:M' ref, find the chapter file (book-NN.txt) in bdir."""
    ch = int(ref.split(":")[0])
    for fn in sorted(os.listdir(bdir)):
        if not fn.endswith(".txt"): continue
        if f"-{ch:02d}.txt" in fn or f"-{ch}.txt" in fn:
            return os.path.join(bdir, fn)
    return None

def apply_merge(path, ref, line1, line2, apply_changes):
    """Find line1 + line2 adjacent in the ref verse; join them."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    # Normalize line endings
    lines = text.split("\n")
    # Find verse-ref line
    verse_header = ref.strip()
    idx = None
    for i, l in enumerate(lines):
        if l.strip() == verse_header:
            idx = i; break
    if idx is None:
        return None, f"verse {ref} not found"
    # Find line1 + line2 adjacent after idx
    for i in range(idx+1, min(idx+50, len(lines)-1)):
        if lines[i].strip() == line1.strip() and lines[i+1].strip() == line2.strip():
            merged = line1.rstrip() + " " + line2.lstrip()
            new_lines = lines[:i] + [merged] + lines[i+2:]
            if apply_changes:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write("\n".join(new_lines))
            return (lines[i], lines[i+1], merged), None
    return None, f"line1/line2 not found adjacent after {ref} in {path}"

def main(apply_changes):
    adv = json.load(open(os.path.join(PRIV, "m1-v2-adv", "adversarial.json"), encoding="utf-8"))
    cands = {c["_id"]: c for c in json.load(open(os.path.join(PRIV, "m1-v2-candidates.json"), encoding="utf-8"))}
    survivors = [a for a in adv if a["outcome"] == "SURVIVES"]
    print(f"=== M1 APPLY {'(APPLIED)' if apply_changes else '(DRY-RUN)'} ===\n")
    print(f"{len(survivors)} survivors to merge:\n")
    applied = 0
    errors = []
    for a in survivors:
        c = cands.get(a["_id"])
        if not c:
            errors.append((a["_id"], "no candidate data")); continue
        bd = find_book_dir(c["book"])
        if not bd:
            errors.append((c["book"], "no book dir")); continue
        cf = find_chapter_file(bd, c["ref"])
        if not cf:
            errors.append((c["ref"], "no chapter file")); continue
        result, err = apply_merge(cf, c["ref"], c["line1"], c["line2"], apply_changes)
        if err:
            errors.append((c["ref"], err)); continue
        applied += 1
        _, _, merged = result
        print(f"  {c['book']:6s} {c['ref']:8s}  -> {merged}")
    print(f"\nApplied: {applied}  Errors: {len(errors)}")
    for e in errors:
        print(f"  ERROR {e}")

if __name__ == "__main__":
    main("--apply" in sys.argv)
