#!/usr/bin/env python3
"""
apply_line_splits.py — Generic line-split applier.

Reads adversarial-verdict files and applies SPLIT outcomes to v4-editorial.
For each candidate with an approved split, finds the current single line
matching `line` under the verse ref and replaces it with two lines (`left`
and `right`).

Usage:
  # Pilot: 10 of each class
  PYTHONIOENCODING=utf-8 py -3 scripts/apply_line_splits.py --class hoti --limit 10 [--apply]
  PYTHONIOENCODING=utf-8 py -3 scripts/apply_line_splits.py --class reverse --limit 10 [--apply]
  # Full
  PYTHONIOENCODING=utf-8 py -3 scripts/apply_line_splits.py --class hoti [--apply]
  PYTHONIOENCODING=utf-8 py -3 scripts/apply_line_splits.py --class reverse [--apply]

--class hoti:    reads hoti-adv-batches/*.json + hoti-adv-verdicts/*.json,
                 applies where outcome == SPLIT_CORRECT.
--class reverse: reads reverse-adv-batches/*.json + reverse-adv-verdicts/*.json,
                 applies where outcome == SPLIT.
"""
import os, sys, json, glob, re
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
PRIV = os.path.join(REPO, "private")

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def find_book_dir(book):
    for ent in sorted(os.listdir(V4)):
        if "-" in ent and ent.split("-", 1)[1] == book:
            return os.path.join(V4, ent)
    return None

def find_chapter_file(bdir, ref):
    ch = int(ref.split(":")[0])
    for fn in sorted(os.listdir(bdir)):
        if not fn.endswith(".txt"): continue
        if f"-{ch:02d}.txt" in fn or f"-{ch}.txt" in fn:
            return os.path.join(bdir, fn)
    return None

def apply_split(path, ref, current_line, left, right, apply_changes):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    # Find verse-ref line
    idx = None
    for i, l in enumerate(lines):
        if l.strip() == ref.strip():
            idx = i; break
    if idx is None:
        return None, f"verse {ref} not found"
    # Find matching line after idx
    for i in range(idx+1, min(idx+50, len(lines))):
        if lines[i].strip() == current_line.strip():
            new_lines = lines[:i] + [left, right] + lines[i+1:]
            if apply_changes:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write("\n".join(new_lines))
            return (lines[i], left, right), None
    return None, f"line not found: {current_line[:60]}..."

def load_pool(cls):
    if cls == "hoti":
        batches_glob = os.path.join(PRIV, "hoti-adv-batches", "*.json")
        verdicts_glob = os.path.join(PRIV, "hoti-adv-verdicts", "*.json")
        approved_outcome = "SPLIT_CORRECT"
    elif cls == "reverse":
        batches_glob = os.path.join(PRIV, "reverse-adv-batches", "*.json")
        verdicts_glob = os.path.join(PRIV, "reverse-adv-verdicts", "*.json")
        approved_outcome = "SPLIT"
    else:
        raise ValueError(f"unknown class {cls}")
    cands = {}
    for f in sorted(glob.glob(batches_glob)):
        for c in json.load(open(f, encoding="utf-8")):
            cands[c["_id"]] = c
    verdicts = {}
    for f in sorted(glob.glob(verdicts_glob)):
        for v in json.load(open(f, encoding="utf-8")):
            verdicts[v["_id"]] = v
    approved = []
    for cid, v in verdicts.items():
        if v.get("outcome") == approved_outcome:
            c = cands.get(cid)
            if c:
                approved.append({**c, **v})
    approved.sort(key=lambda x: x["_id"])
    return approved

def main():
    args = sys.argv[1:]
    cls = None; limit = None; apply_changes = False
    for i, a in enumerate(args):
        if a == "--class": cls = args[i+1]
        if a == "--limit": limit = int(args[i+1])
        if a == "--apply": apply_changes = True
    if cls not in ("hoti", "reverse"):
        print("Usage: --class hoti|reverse [--limit N] [--apply]")
        sys.exit(1)
    pool = load_pool(cls)
    if limit: pool = pool[:limit]
    mode = "APPLIED" if apply_changes else "DRY-RUN"
    print(f"=== {cls.upper()} SPLIT APPLY ({mode}) ===\n")
    print(f"{len(pool)} candidates to apply:\n")
    ok, errs = 0, []
    for c in pool:
        bd = find_book_dir(c["book"])
        if not bd: errs.append((c["_id"], "no book dir")); continue
        cf = find_chapter_file(bd, c["ref"])
        if not cf: errs.append((c["_id"], "no chapter file")); continue
        result, err = apply_split(cf, c["ref"], c["line"], c["left"], c["right"], apply_changes)
        if err: errs.append((c["_id"], err)); continue
        ok += 1
        _, l1, l2 = result
        print(f"  {c['book']:6s} {c['ref']:8s}")
        print(f"    → {l1}")
        print(f"      {l2}")
    print(f"\nApplied: {ok}  Errors: {len(errs)}")
    for e in errs[:10]:
        print(f"  ERROR {e}")

if __name__ == "__main__":
    main()
