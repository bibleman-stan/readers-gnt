#!/usr/bin/env python3
"""
apply_vocative_merges.py — Apply the APPOSITION-CANDIDATE merges
identified by scan_vocative_apposition.py.

For each candidate verse:
  1. Locate the vocative-only line (v4-editorial Greek)
  2. Merge it into the preceding line (append with space)
  3. Write back

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/apply_vocative_merges.py
    PYTHONIOENCODING=utf-8 py -3 scripts/apply_vocative_merges.py --dry-run

The script re-invokes scan_vocative_apposition.scan_all() to get a
fresh list of candidates; this avoids stale-list errors when the
scan has drifted since last run.
"""
import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")

sys.path.insert(0, SCRIPT_DIR)
from scan_vocative_apposition import scan_all  # noqa: E402


def apply_merge_in_memory(content, ref, line_idx_in_verse, vocative_text, skip_match=False):
    """Apply a vocative merge to in-memory content string.
    Returns new content on success, None on failure.

    When skip_match=True, don't verify the voc line's first word matches
    vocative_text — useful for merging English gloss lines where the
    content doesn't match the Greek voc_text.
    """
    lines = content.split("\n")

    # Find verse ref
    ref_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == ref:
            ref_idx = i
            break
    if ref_idx is None:
        return None

    # voc absolute index = ref_idx + line_idx_in_verse + 1
    # (ref line at ref_idx, content lines start at ref_idx+1)
    voc_abs = ref_idx + line_idx_in_verse + 1
    if voc_abs >= len(lines):
        return None

    voc_line = lines[voc_abs].strip()
    if not skip_match:
        import re
        def first_word(s):
            m = re.search(r'\S+', s)
            return m.group(0) if m else ""
        if first_word(voc_line) != first_word(vocative_text):
            return None

    prev_abs = voc_abs - 1
    if prev_abs <= ref_idx:
        return None  # voc is at verse's first content line — shouldn't happen

    prev_line = lines[prev_abs]
    merged = prev_line.rstrip() + " " + voc_line.lstrip()
    lines[prev_abs] = merged
    del lines[voc_abs]

    return "\n".join(lines)


def load_verse_block(filepath, ref):
    """Return (lines_before_verse, verse_lines, lines_after_verse).
    verse_lines includes the ref line itself at index 0.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    lines = raw.split("\n")

    # Find the verse ref line
    ref_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == ref:
            ref_idx = i
            break
    if ref_idx is None:
        return None, None, None

    # The verse block runs from ref_idx until the next blank line
    # OR the next verse-ref line
    end_idx = ref_idx + 1
    while end_idx < len(lines):
        stripped = lines[end_idx].strip()
        if stripped == "":
            break
        # Another verse ref starts
        if len(stripped) > 0 and stripped[0].isdigit() and ":" in stripped and \
                all(c.isdigit() or c == ":" for c in stripped):
            break
        end_idx += 1

    return lines[:ref_idx], lines[ref_idx:end_idx], lines[end_idx:]


def apply_merge(filepath, ref, line_idx_in_verse, vocative_text):
    """Merge the vocative line (at line_idx_in_verse within the verse,
    where index 0 is the ref line) into the preceding content line.

    Returns True on success, False if the merge couldn't be applied
    (e.g., line content didn't match).
    """
    before, verse, after = load_verse_block(filepath, ref)
    if verse is None:
        print(f"  FAIL: ref {ref} not found in {filepath}")
        return False

    # Verse structure: [ref_line, content_line_1, content_line_2, ...]
    # scan's line_idx is index of vocative line among content lines (0-based)
    # so vocative absolute index in `verse` is line_idx_in_verse + 1
    voc_abs_idx = line_idx_in_verse + 1
    if voc_abs_idx >= len(verse):
        print(f"  FAIL: voc_abs_idx {voc_abs_idx} >= len(verse) {len(verse)} for {ref}")
        return False

    voc_line = verse[voc_abs_idx].strip()
    # Sanity check: the stripped voc_line should match the scanner's voc_text
    # (or at least start with the vocative word)
    if voc_line != vocative_text.strip():
        # Allow a looser match: scanner's voc_text might have trailing punctuation
        # differences. Check that they share the first non-punct word.
        import re
        def first_word(s):
            m = re.search(r'\w+', s)
            return m.group(0) if m else ""
        if first_word(voc_line) != first_word(vocative_text):
            print(f"  FAIL: voc line mismatch for {ref}")
            print(f"    file has: {voc_line!r}")
            print(f"    scanner:  {vocative_text!r}")
            return False

    prev_abs_idx = voc_abs_idx - 1
    if prev_abs_idx <= 0:
        print(f"  FAIL: voc is at line 1 (verse-initial) for {ref} — shouldn't happen")
        return False

    prev_line = verse[prev_abs_idx]
    # Merge: append voc_line to prev_line with a space
    merged = prev_line.rstrip() + " " + voc_line.lstrip()
    verse[prev_abs_idx] = merged
    # Remove the vocative line
    del verse[voc_abs_idx]

    new_content = "\n".join(before + verse + after)
    return new_content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Show what would be merged without writing")
    ap.add_argument("--english", action="store_true",
                    help="Apply to eng-gloss files instead of v4-editorial")
    ap.add_argument("--save-candidates", type=str, default=None,
                    help="Save the candidate list to a JSON file for later use")
    ap.add_argument("--load-candidates", type=str, default=None,
                    help="Load candidates from JSON instead of re-scanning")
    args = ap.parse_args()

    if args.load_candidates:
        import json
        with open(args.load_candidates, "r", encoding="utf-8") as f:
            candidates = json.load(f)
        print(f"Loaded {len(candidates)} candidates from {args.load_candidates}\n")
    else:
        findings = scan_all()
        candidates = [f for f in findings if f["classification"] == "APPOSITION-CANDIDATE"]
        print(f"Found {len(candidates)} APPOSITION-CANDIDATE merges\n")
        if args.save_candidates:
            import json
            # Strip non-serializable fields
            slim = [{"file": c["file"], "ref": c["ref"],
                     "line_idx": c["line_idx"], "voc_text": c["voc_text"]}
                    for c in candidates]
            with open(args.save_candidates, "w", encoding="utf-8") as f:
                json.dump(slim, f, ensure_ascii=False, indent=2)
            print(f"Saved candidates to {args.save_candidates}\n")

    target_dir = os.path.join(REPO_ROOT, "data", "text-files", "eng-gloss") \
        if args.english else V4_DIR

    # Group by file so we can apply all merges to a given file in reverse order
    # (reverse order prevents line-index invalidation as we delete lines)
    by_file = {}
    for c in candidates:
        by_file.setdefault(c["file"], []).append(c)

    total_applied = 0
    total_failed = 0
    for file_rel, cands in sorted(by_file.items()):
        filepath = os.path.join(target_dir, *file_rel.split("/"))
        # Sort by (ref, line_idx) descending so that deletions within a file
        # don't shift indices of earlier candidates
        # Process within a file in this order:
        #   - Later verses before earlier verses (so deletes don't shift
        #     earlier verses' ref-line positions)
        #   - Within a verse, later line_idx before earlier line_idx (same reason)
        def sort_key(c):
            ch_vs = c["ref"].split(":")
            return (int(ch_vs[0]), int(ch_vs[1]), c["line_idx"])
        cands_sorted = sorted(cands, key=sort_key, reverse=True)
        # Read file once
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        for c in cands_sorted:
            # apply_merge_in_memory operates on `content` directly
            new_content = apply_merge_in_memory(content, c["ref"], c["line_idx"],
                                                 c["voc_text"], skip_match=args.english)
            if new_content is None:
                total_failed += 1
                print(f"  FAIL: {file_rel} {c['ref']} line {c['line_idx']+1}")
                continue
            content = new_content
            total_applied += 1
            print(f"  {file_rel} {c['ref']}: merged '{c['voc_text'].strip()}' into line above")

        # Write final content (only if not dry-run AND content changed)
        if not args.dry_run:
            with open(filepath, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)

    print(f"\nTotal merges applied: {total_applied}")
    print(f"Total failures: {total_failed}")


if __name__ == "__main__":
    main()
