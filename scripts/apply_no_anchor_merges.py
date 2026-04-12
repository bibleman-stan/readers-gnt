#!/usr/bin/env python3
"""
apply_no_anchor_merges.py — Apply the unanchored-line merges identified
by scan_no_anchor_lines.py.

Each flagged unanchored line gets merged into the line directly above
it (append with space). When a run of consecutive unanchored lines
follows one anchored line, processing them in REVERSE order cascades
them all into the anchored head naturally:

  [anchored, unanchored_a, unanchored_b, unanchored_c]
  → reverse-merge c into b: [anchored, unanchored_a, unanchored_b+c]
  → reverse-merge b into a: [anchored, unanchored_a+b+c]
  → reverse-merge a into anchored: [anchored+a+b+c]

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/apply_no_anchor_merges.py [--book BOOK] [--english]
                                                                      [--dry-run]
                                                                      [--limit-books BOOK,BOOK,...]

Typical workflow:
  1. Greek pass:    apply_no_anchor_merges.py --book rom
  2. English pass:  apply_no_anchor_merges.py --book rom --english
  3. Rebuild:       build_books.py --book rom
"""
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
ENG_DIR = os.path.join(REPO_ROOT, "data", "text-files", "eng-gloss")

sys.path.insert(0, SCRIPT_DIR)
from scan_no_anchor_lines import scan_all  # noqa: E402


def apply_merge_in_memory(content, ref, line_idx_in_verse, allow_downward=True):
    """Merge the unanchored verse line at line_idx_in_verse.

    Default: upward merge — append the unanchored line's content to the
    preceding line, delete the unanchored line.

    If allow_downward and the unanchored line is the first content line
    of the verse (no upward target), fall back to downward merge —
    prepend the unanchored line's content to the next line, delete the
    unanchored line.

    Returns new content on success, None on failure.
    """
    lines = content.split("\n")
    ref_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == ref:
            ref_idx = i
            break
    if ref_idx is None:
        return None

    target_line_abs = ref_idx + line_idx_in_verse + 1
    if target_line_abs >= len(lines):
        return None

    can_upward = (target_line_abs - 1 > ref_idx)
    if can_upward:
        merged = lines[target_line_abs - 1].rstrip() + " " + lines[target_line_abs].lstrip()
        lines[target_line_abs - 1] = merged
        del lines[target_line_abs]
        return "\n".join(lines)

    # Upward not possible — try downward
    if not allow_downward:
        return None
    # Need a next line within the same verse
    next_abs = target_line_abs + 1
    if next_abs >= len(lines):
        return None
    next_stripped = lines[next_abs].strip()
    if not next_stripped:
        return None  # blank line — verse ended
    import re
    # Don't merge into another verse ref
    if re.match(r'^\d+:\d+$', next_stripped):
        return None
    merged = lines[target_line_abs].rstrip() + " " + lines[next_abs].lstrip()
    lines[target_line_abs] = merged
    del lines[next_abs]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--english", action="store_true",
                    help="Apply to eng-gloss files instead of v4-editorial")
    ap.add_argument("--book", default=None, help="Limit to one book slug (e.g., rom)")
    ap.add_argument("--limit-books", default=None,
                    help="Comma-separated list of book slugs to apply to")
    ap.add_argument("--save-candidates", default=None,
                    help="Save candidate list to a JSON file (run before any merges)")
    ap.add_argument("--load-candidates", default=None,
                    help="Load candidates from JSON instead of fresh scanning")
    args = ap.parse_args()

    target_dir = ENG_DIR if args.english else V4_DIR

    if args.load_candidates:
        import json
        with open(args.load_candidates, "r", encoding="utf-8") as f:
            findings = json.load(f)
    else:
        findings = scan_all(book_filter=args.book)
        if args.save_candidates:
            import json
            slim = [{"file": f["file"], "ref": f["ref"],
                     "line_idx": f["line_idx"]} for f in findings]
            with open(args.save_candidates, "w", encoding="utf-8") as out:
                json.dump(slim, out, ensure_ascii=False, indent=2)
            print(f"Saved {len(slim)} candidates to {args.save_candidates}")
            return

    # Optional additional book filter
    if args.limit_books:
        allowed = set(args.limit_books.split(","))
        findings = [f for f in findings
                    if f["file"].split("/")[0].split("-", 1)[-1] in allowed]

    print(f"Found {len(findings)} unanchored lines\n")

    # Group by file
    by_file = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    total_applied = 0
    total_failed = 0
    for file_rel, cands in sorted(by_file.items()):
        filepath = os.path.join(target_dir, *file_rel.split("/"))
        # Sort descending by (chapter, verse, line_idx) so we delete higher
        # indices first and don't invalidate earlier indices in the same file.
        def sort_key(c):
            ch_vs = c["ref"].split(":")
            return (int(ch_vs[0]), int(ch_vs[1]), c["line_idx"])
        cands_sorted = sorted(cands, key=sort_key, reverse=True)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        file_applied = 0
        file_failed = 0
        for c in cands_sorted:
            new_content = apply_merge_in_memory(content, c["ref"], c["line_idx"])
            if new_content is None:
                file_failed += 1
                continue
            content = new_content
            file_applied += 1

        if not args.dry_run:
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)

        total_applied += file_applied
        total_failed += file_failed
        if file_applied or file_failed:
            print(f"  {file_rel}: {file_applied} merged, {file_failed} failed")

    print(f"\nTotal merges applied: {total_applied}")
    print(f"Total failures: {total_failed}")
    if args.dry_run:
        print("(dry-run — no files written)")


if __name__ == "__main__":
    main()
