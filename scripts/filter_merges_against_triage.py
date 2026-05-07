#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filter_merges_against_triage.py — Filter the Phase 1 MERGES table down to
entries that are confirmed in some triage file's ## MERGE-MECHANICAL
section. Keeps Phase 1's table structure intact for the survivors;
drops fabrications.

For each entry (file_path, ref) in the Phase 1 MERGES table:
1. Build a list of search keys: full path, basename without dir, book-abbrev + ref
2. For each triage file, extract its ## MERGE-MECHANICAL section
3. If any search key appears in that section → KEEP
4. Else → DROP (logged)

Also pulls additional MERGE-MECHANICAL entries from
private/r1-review-demoted.md.

Output: scripts/apply_r1_merges_v2.py with verified MERGES.
"""
import glob
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v4-editorial")
RESULTS_DIR = os.path.join(REPO_ROOT, "private", "r1-sweep-results")
DEMOTED_FILE = os.path.join(REPO_ROOT, "private", "r1-review-demoted.md")
PHASE1 = os.path.join(REPO_ROOT, "scripts", "apply_r1_merges.py")
OUT = os.path.join(REPO_ROOT, "scripts", "apply_r1_merges_v2.py")


# Folder → Book abbreviations for searching
FOLDER_TO_BOOK = {
    "01-matt": "Matt",  "02-mark": "Mark",  "03-luke": "Luke",
    "04-john": "John",  "05-acts": "Acts",  "06-rom": "Rom",
    "07-1cor": "1Cor",  "08-2cor": "2Cor",  "09-gal": "Gal",
    "10-eph": "Eph",    "11-phil": "Phil",  "12-col": "Col",
    "13-1thess": "1Thess", "14-2thess": "2Thess",
    "15-1tim": "1Tim", "16-2tim": "2Tim",
    "17-titus": "Titus", "18-phlm": "Phlm",
    "19-heb": "Heb",   "20-jas": "Jas",
    "21-1pet": "1Pet", "22-2pet": "2Pet",
    "23-1john": "1John", "24-2john": "2John",
    "25-3john": "3John", "26-jude": "Jude",
    "27-rev": "Rev",
}


def extract_phase1_merges():
    """Extract the (file, ref, src, tgt) tuples from the Phase 1 script."""
    with open(PHASE1, "r", encoding="utf-8") as f:
        content = f.read()
    # Match: ("path", "ref", "src", tgt)
    pat = re.compile(
        r'\("([^"]+\.txt)",\s*"(\d+:\d+)",\s*"([^"]+)",\s*("([^"]+)"|None)\),',
        re.DOTALL,
    )
    out = []
    for m in pat.finditer(content):
        out.append({
            "file": m.group(1),
            "ref": m.group(2),
            "src": m.group(3),
            "tgt": m.group(5),  # None if matched 'None'
        })
    return out


def extract_section(content, header):
    pattern = re.compile(
        rf"^## {re.escape(header)}\s*$(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(content)
    return m.group(1) if m else ""


def load_triage_merge_sections():
    """Return dict {file_basename: merge_section_text} for each triage file."""
    out = {}
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        out[os.path.basename(path)] = extract_section(content, "MERGE-MECHANICAL")
    return out


def is_in_merge_section(entry, sections):
    """Return True if entry's (file, ref) appears in any MERGE-MECHANICAL
    section. Uses multiple search keys to handle the 5+ format variations."""
    file_path = entry["file"]
    ref = entry["ref"]
    folder = file_path.split("/")[0]
    fname = file_path.split("/")[-1]  # e.g., "mark-01.txt"
    book_abbrev = FOLDER_TO_BOOK.get(folder, "")

    # Search keys (regex patterns):
    # 1. Full path + ref:    "01-matt/matt-01.txt 1:5"
    # 2. Path components:    "matt-01.txt 1:5"  (acts.md uses this)
    # 3. Book abbrev + ref:  "Matt 1:5" or "Mark 1:5 L2" (pauline-b style)
    # 4. Book + ref dash:    "Matt 1:5 —" or "Rom 1:1 — line"
    # 5. Bare ref in rev.md: "1:9 (line 3/3)" — file context implied by triage filename

    chapter = ref.split(":")[0]
    keys = [
        re.compile(rf"\b{re.escape(file_path)}\s+{re.escape(ref)}\b"),
        re.compile(rf"\b{re.escape(fname)}\s+{re.escape(ref)}\b"),
    ]
    if book_abbrev:
        keys.append(re.compile(rf"\b{re.escape(book_abbrev)}\s+{re.escape(ref)}\b"))
        # Book abbrev case-insensitive (e.g., "ROM" in some agents)
        keys.append(re.compile(rf"\b{book_abbrev.upper()}\s+{re.escape(ref)}\b", re.IGNORECASE))

    # For rev.md and similar: the file is implied — check if section is from
    # the corresponding triage file
    relevant_files = []
    for tf_name in sections:
        # acts.md → 05-acts entries
        # mark.md → 02-mark entries
        # luke-john.md → 03-luke + 04-john
        # heb-catholic.md → 19-heb + 20-jas + 21-1pet + 22-2pet + 23-1john + 24-2john + 25-3john + 26-jude
        # pauline-a.md → 06-rom + 07-1cor + 08-2cor
        # pauline-b.md → 09-gal through 18-phlm
        # rev.md → 27-rev
        # matt.md → 01-matt
        slug = tf_name.replace(".md", "")
        scope_match = False
        if slug == "mark" and folder == "02-mark":
            scope_match = True
        elif slug == "matt" and folder == "01-matt":
            scope_match = True
        elif slug == "luke-john" and folder in ("03-luke", "04-john"):
            scope_match = True
        elif slug == "acts" and folder == "05-acts":
            scope_match = True
        elif slug == "pauline-a" and folder in ("06-rom", "07-1cor", "08-2cor"):
            scope_match = True
        elif slug == "pauline-b" and folder in (
            "09-gal", "10-eph", "11-phil", "12-col", "13-1thess",
            "14-2thess", "15-1tim", "16-2tim", "17-titus", "18-phlm",
        ):
            scope_match = True
        elif slug == "heb-catholic" and folder in (
            "19-heb", "20-jas", "21-1pet", "22-2pet",
            "23-1john", "24-2john", "25-3john", "26-jude",
        ):
            scope_match = True
        elif slug == "rev" and folder == "27-rev":
            scope_match = True
        if scope_match:
            relevant_files.append(tf_name)

    for tf_name in relevant_files:
        section = sections[tf_name]
        for k in keys:
            if k.search(section):
                return True, tf_name
        # rev.md special: bare ref pattern with line indicator
        if tf_name == "rev.md":
            bare_pat = re.compile(rf"^### {re.escape(ref)}\s*\(", re.MULTILINE)
            if bare_pat.search(section):
                return True, tf_name
    return False, None


def parse_demoted():
    """Parse private/r1-review-demoted.md ## DEMOTED → MERGE-MECHANICAL section.
    Returns list of {file, ref, src, tgt}."""
    if not os.path.exists(DEMOTED_FILE):
        return []
    with open(DEMOTED_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    section = extract_section(content, "DEMOTED → MERGE-MECHANICAL")
    if not section:
        return []
    # Format: ### book/book-NN.txt X:Y (line N/M)
    #         Line: `text`
    #         Original recommendation: ...
    #         New classification: MERGE-MECHANICAL
    #         Canon citation: ...
    out = []
    blocks = re.split(r"^### ", section, flags=re.MULTILINE)
    for block in blocks[1:]:
        lines = block.split("\n")
        header = lines[0].strip()
        # Header: "book/book-NN.txt X:Y (line N/M)"
        m = re.match(r"(\S+\.txt)\s+(\d+:\d+)\s+\(line", header)
        if not m:
            continue
        bare_path = m.group(1)
        ref = m.group(2)
        # Add NN- prefix
        if "/" in bare_path:
            folder, fname = bare_path.split("/", 1)
            if not re.match(r"^\d{2}-", folder):
                # Map book → folder
                inv_map = {v.lower(): k for k, v in FOLDER_TO_BOOK.items()}
                key = folder.lower()
                if key in inv_map:
                    folder = inv_map[key]
            full_path = f"{folder}/{fname}"
        else:
            continue
        # Find Line: `text`
        src = None
        for ln in lines[1:8]:
            mm = re.match(r"Line:\s*`(.+?)`", ln)
            if mm:
                src = mm.group(1)
                break
        if src:
            out.append({
                "file": full_path,
                "ref": ref,
                "src": src,
                "tgt": None,  # demoted file doesn't always specify target text
            })
    return out


VERSE_RE = re.compile(r"^\d+:\d+\s*$")


def normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def verify_in_corpus(entry):
    filepath = os.path.join(V4_DIR, entry["file"])
    if not os.path.exists(filepath):
        return False, "file not found"
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # Find verse range
    in_verse = False
    verse_lines = []
    for ln in lines:
        s = ln.strip()
        if s == entry["ref"]:
            in_verse = True
            continue
        if in_verse and VERSE_RE.match(s):
            break
        if in_verse and s:
            verse_lines.append(s)
    if not verse_lines:
        return False, f"verse {entry['ref']} not found"
    src_n = normalize(entry["src"])
    src_match = any(normalize(ln) == src_n or normalize(ln).startswith(src_n) for ln in verse_lines)
    if not src_match:
        return False, f"src not found"
    if entry["tgt"]:
        tgt_n = normalize(entry["tgt"])
        tgt_match = any(normalize(ln) == tgt_n or normalize(ln).startswith(tgt_n) for ln in verse_lines)
        if not tgt_match:
            return False, "tgt not found"
    return True, "ok"


def main():
    p1 = extract_phase1_merges()
    sections = load_triage_merge_sections()
    print(f"Phase 1 MERGES entries: {len(p1)}")

    confirmed = []
    rejected = []
    for e in p1:
        in_merge, source = is_in_merge_section(e, sections)
        if in_merge:
            e["source"] = source
            confirmed.append(e)
        else:
            rejected.append(e)

    print(f"Confirmed in some MERGE-MECHANICAL section: {len(confirmed)}")
    print(f"Rejected (not in any MERGE section): {len(rejected)}")

    # Add demoted entries
    demoted = parse_demoted()
    print(f"Demoted MERGE entries (from r1-review-demoted.md): {len(demoted)}")

    # De-dupe
    seen = set()
    final = []
    for e in confirmed + demoted:
        key = (e["file"], e["ref"], e["src"][:40])
        if key in seen:
            continue
        seen.add(key)
        final.append(e)
    print(f"Combined unique candidates: {len(final)}")

    # Verify against corpus
    verified = []
    failed_verify = []
    for e in final:
        ok, reason = verify_in_corpus(e)
        if ok:
            verified.append(e)
        else:
            failed_verify.append((e, reason))

    print(f"\nVerified in corpus: {len(verified)}")
    print(f"Failed corpus verification: {len(failed_verify)}")

    if failed_verify:
        print("\nFirst 15 verification failures:")
        for e, r in failed_verify[:15]:
            src_repr = e.get("src", "")[:50]
            print(f"  {e['file']} {e['ref']}: {r}  (src: {src_repr})")

    # Emit clean apply script
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("# -*- coding: utf-8 -*-\n")
        f.write('"""apply_r1_merges_v2.py — verified clean MERGES list."""\n')
        f.write("import os, re, sys\n\n")
        f.write("REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n")
        f.write('V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")\n\n')
        f.write("MERGES = [\n")
        for e in verified:
            tgt_repr = repr(e["tgt"]) if e["tgt"] else "None"
            f.write(f"    ({e['file']!r}, {e['ref']!r}, {e['src']!r}, {tgt_repr}),\n")
        f.write("]\n\n")
        f.write(_APPLY_LOGIC)
    print(f"\nWrote: {OUT}")


_APPLY_LOGIC = '''
VERSE_RE = re.compile(r"^\\d+:\\d+\\s*$")


def normalize(s):
    return re.sub(r"\\s+", " ", s).strip()


def find_verse(lines, ref):
    start = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == ref:
            start = i + 1
        elif start is not None and VERSE_RE.match(s):
            return start, i
    if start is not None:
        return start, len(lines)
    return None, None


def find_line(lines, lo, hi, target):
    tn = normalize(target)
    for i in range(lo, hi):
        ln = normalize(lines[i])
        if ln == tn or ln.startswith(tn):
            return i
    return -1


def apply_one(lines, ref, src, tgt):
    lo, hi = find_verse(lines, ref)
    if lo is None:
        return False, f"verse {ref} not found"
    src_idx = find_line(lines, lo, hi, src)
    if src_idx == -1:
        return False, f"src not found: {src[:40]}"
    if tgt:
        tgt_idx = find_line(lines, lo, hi, tgt)
        if tgt_idx == -1:
            return False, f"tgt not found: {tgt[:40]}"
        if tgt_idx == src_idx:
            return False, "tgt == src"
    else:
        tgt_idx = -1
        for k in range(src_idx - 1, lo - 1, -1):
            n = normalize(lines[k])
            if n and not VERSE_RE.match(n):
                tgt_idx = k
                break
        if tgt_idx == -1:
            return False, "no preceding line"
    earlier = min(src_idx, tgt_idx)
    later = max(src_idx, tgt_idx)
    lines[earlier] = lines[earlier].rstrip("\\n").rstrip() + " " + lines[later].rstrip("\\n").lstrip() + "\\n"
    del lines[later]
    return True, "ok"


def main():
    dry = "--dry-run" in sys.argv
    by_file = {}
    for f, r, s, t in MERGES:
        by_file.setdefault(f, []).append((r, s, t))
    applied = 0
    failed = []
    for fp, entries in sorted(by_file.items()):
        full = os.path.join(V4, fp)
        if not os.path.exists(full):
            for r, s, t in entries:
                failed.append((fp, r, "file not found"))
            continue
        with open(full, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        applied_in_file = 0
        for r, s, t in entries:
            ok, reason = apply_one(lines, r, s, t)
            if ok:
                applied += 1
                applied_in_file += 1
            else:
                failed.append((fp, r, reason))
        if applied_in_file and not dry:
            with open(full, "w", encoding="utf-8") as fh:
                fh.writelines(lines)
        if applied_in_file:
            print(f"  {'[dry] ' if dry else ''}{fp}: {applied_in_file}")
    print(f"\\n=== {applied} applied / {len(failed)} failed ===")
    for fp, r, rsn in failed[:30]:
        print(f"  FAIL {fp} {r}: {rsn}")


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    main()
