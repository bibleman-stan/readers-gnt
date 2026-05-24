"""
ATU segmentation quality audit — John 6
Reads v1.5/grk and v1.5/eng-kjv line-for-line aligned files.
Prints side-by-side with line numbers for manual scoring.
"""
import sys
import re
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

GRK = r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v4\grk\04-john\john-06.txt"
ENG = r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v4\eng-kjv\04-john\john-06.txt"

with open(GRK, encoding="utf-8") as f:
    greek_raw = [l.rstrip("\n") for l in f]

with open(ENG, encoding="utf-8") as f:
    eng_raw = [l.rstrip("\n") for l in f]

# Verify line counts match
if len(greek_raw) != len(eng_raw):
    print(f"LINE COUNT MISMATCH: grk={len(greek_raw)} eng={len(eng_raw)}", file=sys.stderr)

# Use shorter list for zip
min_len = min(len(greek_raw), len(eng_raw))
print(f"Total file lines: grk={len(greek_raw)} eng={len(eng_raw)}")
print()

VERSE_REF = re.compile(r"^\d+:\d+$")

current_verse = ""
for i in range(min_len):
    g = greek_raw[i]
    e = eng_raw[i]
    # Detect verse ref lines
    if VERSE_REF.match(g.strip()):
        current_verse = g.strip()
        print(f"\n=== {current_verse} ===")
        continue
    if g.strip() == "":
        continue
    print(f"  [{i+1:3d}] GRK: {g}")
    print(f"       ENG: {e}")
