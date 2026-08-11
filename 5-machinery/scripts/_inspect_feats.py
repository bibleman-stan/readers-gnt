"""What discriminating features ARE present: dump word-level role + full morph
parse code (incl. person = code[0]) for the governor+ὅτι region of each case."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import sblgnt_v1_fabric as V1

CASES = [("Matt", 5, 36), ("Rev", 10, 6), ("Rom", 8, 16),
         ("John", 2, 18), ("1Cor", 3, 13), ("Rom", 9, 17), ("Gal", 3, 8)]

# all distinct lowfat word-level role values in Matthew, for vocabulary
import xml.etree.ElementTree as ET
roles = {}
tree = ET.parse(V1.book_paths(1)[0])
for w in tree.iter("w"):
    r = w.attrib.get("role", "")
    roles[r] = roles.get(r, 0) + 1
print("Matthew word-level role vocabulary:", roles)

for book, chap, verse in CASES:
    num = V1.NUM[book]
    lowfat, morph, *_ = V1.book_paths(num)
    moods_raw = {}
    for line in Path(morph).read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) < 7:
            continue
        ref = p[0]
        ch, v = int(ref[2:4]), int(ref[4:6])
        cnt = moods_raw.get(("c", ch, v), 0) + 1
        moods_raw[("c", ch, v)] = cnt
        moods_raw[(ch, v, cnt)] = (p[1], p[2])  # (pos, parsecode)
    tree = ET.parse(lowfat)
    print(f"\n===== {book} {chap}:{verse} =====")
    for w in tree.iter("w"):
        osis = w.attrib.get("osisId", "")
        if not osis or "!" not in osis:
            continue
        c, v, wi = V1.parse_osis(osis)
        if c == chap and v == verse:
            pos, code = moods_raw.get((chap, verse, wi), ("", ""))
            person = code[0] if code and pos.startswith("V") else "-"
            print(f"  wi={wi:2} {w.text or '':12} lem={w.attrib.get('lemma',''):14} "
                  f"role={w.attrib.get('role',''):6} pos={pos:4} code={code:10} person={person}")
