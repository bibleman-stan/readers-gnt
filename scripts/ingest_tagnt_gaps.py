#!/usr/bin/env python3
"""
ingest_tagnt_gaps.py — Extract TR/Byzantine-only gap-fill passages from STEPBible TAGNT.

Reads TAGNT Mat-Jhn and Act-Rev TSV files. Filters for rows where:
  1. The reference matches one of the 17 KJV gap passages
  2. The word-type field indicates presence in TR/Byzantine tradition but
     NOT in the standard NA/SBL editions (type codes beginning with K or
     containing K but not N as the leading character)

Outputs gap-fill.json mapping "Book CH:VS" → "Greek text (reconstructed)"

Does NOT modify v4/grc. Hand-editorial ATU line-breaking is a
separate step.

Usage:
    python3 scripts/ingest_tagnt_gaps.py [--dry-run]

Output:
    data/text-files/tagnt-source/gap-fill.json
"""

import re
import sys
import json
import pathlib
import argparse

# ---------------------------------------------------------------------------
# Gap passages: (TAGNT_book_prefix, chapter, verse, label, whole_verse)
#
# whole_verse=True  → every word in the verse is a gap (verse entirely absent
#                     from SBL/NA; include all K-type AND NKO words alike)
# whole_verse=False → verse exists in SBL/NA but has TR-only additions;
#                     include only K-type words (plus NKO words that are
#                     already present, stitched in word-order)
#
# For Matt 6:13b the base verse (#01-#12 = NKO) exists; the doxology
# (#13-#27 = K) is the gap.  We want doxology words only, appended.
# For all wholly-absent verses, we take the full reconstructed text.
# ---------------------------------------------------------------------------

GAP_PASSAGES = [
    # (tagnt_ref_prefix, human_label, doxology_only)
    ("Mat.6.13",   "Matt 6:13b",   True),   # doxology only (#13+)
    ("Mat.17.21",  "Matt 17:21",   False),
    ("Mat.18.11",  "Matt 18:11",   False),
    ("Mat.23.14",  "Matt 23:14",   False),
    ("Mrk.7.16",   "Mark 7:16",    False),
    ("Mrk.9.44",   "Mark 9:44",    False),
    ("Mrk.9.46",   "Mark 9:46",    False),
    ("Mrk.11.26",  "Mark 11:26",   False),
    ("Mrk.15.28",  "Mark 15:28",   False),
    ("Luk.17.36",  "Luke 17:36",   False),
    ("Luk.23.17",  "Luke 23:17",   False),
    ("Jhn.5.4",    "John 5:4",     False),
    ("Act.8.37",   "Acts 8:37",    False),
    ("Act.15.34",  "Acts 15:34",   False),
    ("Act.24.7",   "Acts 24:7",    False),
    ("Act.28.29",  "Acts 28:29",   False),
    # Rom 16:24 is present in v4/grc (SBL includes it via KO type).
    # Excluded here — not a gap.
    # 1John 5:7 Comma Johanneum — insert the TR-only words (K type)
    ("1Jn.5.7",    "1 John 5:7",   True),   # TR-only insertion words only
]

# Build lookup: tagnt_ref_prefix -> (label, doxology_only)
GAP_LOOKUP = {ref: (label, dox) for ref, label, dox in GAP_PASSAGES}

# Source files
BASE = pathlib.Path(__file__).parent.parent
TAGNT_DIR = BASE / "data" / "text-files" / "tagnt-source"
MAT_JHN = TAGNT_DIR / "TAGNT_Mat-Jhn.txt"
ACT_REV = TAGNT_DIR / "TAGNT_Act-Rev.txt"
OUTPUT = TAGNT_DIR / "gap-fill.json"

# Regex to parse data rows (non-comment lines with a reference field)
# Format: Book.Ch.Vs#NN=TypeCode\tGreek(translit)\t...
REF_RE = re.compile(r"^([A-Za-z0-9]+\.\d+\.\d+)#(\d+)=([A-Z()/a-z]+)\t(.+)$")


def is_tr_only_type(type_code: str) -> bool:
    """Return True if this word is TR/Byzantine-only (not in NA/SBL).

    Type codes:
      NKO / N(K)O / NKo etc. → present in NA editions → NOT a gap word
      KO / K(O) / K           → in TR/Byz but NOT NA   → IS a gap word
      K(N)                    → variant; treat as gap
      N(K)                    → in NA with TR variant; NOT a gap word

    Rule: if code starts with 'N' (case-insensitive) and N is the
    primary/unparenthesised prefix, it's in NA → not a gap.
    If the code starts with 'K' as the primary edition indicator, it
    is TR/Byz-only → gap word.
    """
    # Strip surrounding whitespace
    code = type_code.strip()
    # Primary character (outside parentheses) is what the TAGNT header
    # defines as the primary edition. A leading 'N' means NA-present.
    if not code:
        return False
    # NKO, NKo, N(K)O, N(K)(O) etc. → NA present → not a gap
    if code[0].upper() == 'N':
        return False
    # KO, K(O), K(N)(O), KO etc. → not in NA → gap
    if code[0].upper() == 'K':
        return True
    # O-only or other → not a standard gap
    return False


def extract_greek_word(greek_field: str) -> str:
    """Extract bare Greek text from the Greek(translit) field.
    Format examples:
        ὅτι (hoti)
        νηστείᾳ.¶ (nēsteia)
        ἀμήν.
    Strip the parenthesised transliteration and ¶ markers.
    """
    # Remove paragraph marker
    text = greek_field.replace("¶", "")
    # Remove (translit) portion if present
    text = re.sub(r"\s*\([^)]*\)", "", text)
    return text.strip()


def parse_tagnt_file(filepath: pathlib.Path, results: dict) -> None:
    """Parse one TAGNT file, accumulating words for gap passages."""
    with open(filepath, encoding="utf-8-sig") as fh:
        for line in fh:
            line = line.rstrip("\n")
            # Skip comment/header lines (start with # or space-tab-blank)
            if not line or line.startswith("#") or line.startswith("\t"):
                continue
            m = REF_RE.match(line)
            if not m:
                continue
            ref_prefix, word_idx, type_code, rest = (
                m.group(1), int(m.group(2)), m.group(3), m.group(4)
            )
            if ref_prefix not in GAP_LOOKUP:
                continue

            label, doxology_only = GAP_LOOKUP[ref_prefix]

            # Split rest on tabs to get Greek field (first tab-field)
            parts = rest.split("\t")
            greek_word = extract_greek_word(parts[0]) if parts else ""
            if not greek_word:
                continue

            # For doxology_only passages (Matt 6:13b, 1Jn 5:7):
            # include only TR-only words (the insertion block)
            # For wholly-absent verses: include ALL words in word order
            if doxology_only:
                if not is_tr_only_type(type_code):
                    continue  # skip NKO base words; doxology = K-only block
            # else: include every word (the whole verse is absent from SBL)

            if label not in results:
                results[label] = []
            results[label].append((word_idx, greek_word))


def assemble_texts(results: dict) -> dict:
    """Sort words by index and join into reconstructed Greek text strings."""
    assembled = {}
    for label, words in results.items():
        words.sort(key=lambda x: x[0])
        assembled[label] = " ".join(w for _, w in words)
    return assembled


def main():
    parser = argparse.ArgumentParser(description="Extract TAGNT gap-fill passages.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results to stdout; do not write gap-fill.json")
    args = parser.parse_args()

    for path in (MAT_JHN, ACT_REV):
        if not path.exists():
            print(f"ERROR: Required file not found: {path}", file=sys.stderr)
            sys.exit(1)

    raw: dict = {}
    print(f"Parsing {MAT_JHN.name} ...", file=sys.stderr)
    parse_tagnt_file(MAT_JHN, raw)
    print(f"Parsing {ACT_REV.name} ...", file=sys.stderr)
    parse_tagnt_file(ACT_REV, raw)

    assembled = assemble_texts(raw)

    # Report
    expected_labels = {label for _, label, _ in GAP_PASSAGES}
    found = set(assembled.keys())
    missing = expected_labels - found
    print(f"\nPassages found:  {len(found)}", file=sys.stderr)
    if missing:
        print(f"MISSING passages: {sorted(missing)}", file=sys.stderr)
    else:
        print("All expected passages extracted.", file=sys.stderr)

    print("\nExtracted texts:", file=sys.stderr)
    for label in sorted(assembled, key=lambda x: GAP_PASSAGES.index(
            next(t for t in GAP_PASSAGES if t[1] == x))):
        text = assembled[label]
        preview = text[:80] + ("..." if len(text) > 80 else "")
        print(f"  {label:20s}: {preview}", file=sys.stderr)

    if args.dry_run:
        print("\n[dry-run] gap-fill.json not written.", file=sys.stderr)
        # Write dry-run output as UTF-8 to stdout (safe on all platforms)
        out = json.dumps(assembled, ensure_ascii=False, indent=2)
        sys.stdout.buffer.write(out.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        return

    OUTPUT.write_text(
        json.dumps(assembled, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nWrote {OUTPUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
