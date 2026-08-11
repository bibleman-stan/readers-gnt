"""Inspect lowfat clause-role nesting around a ὅτι, to see whether the embedded
clause's wg role discriminates complement (object) from causal (adverbial)."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import xml.etree.ElementTree as ET
import sblgnt_v1_fabric as V1

# (book, chap, verse) -> expected reading
CASES = [
    ("Matt", 5, 36, "CAUSAL stand"),
    ("Rev", 10, 6, "COMPLEMENT bind (oath content)"),
    ("Rom", 8, 16, "COMPLEMENT bind"),
    ("John", 2, 18, "CAUSAL stand (obj σημεῖον filled)"),
    ("1Cor", 3, 13, "CAUSAL stand"),
    ("Rom", 9, 17, "DIRECT-DISCOURSE stand (God->Pharaoh)"),
]

for book, chap, verse, note in CASES:
    num = V1.NUM[book]
    lowfat, *_ = V1.book_paths(num)
    tree = ET.parse(lowfat)
    print(f"\n===== {book} {chap}:{verse}  [{note}] =====")

    def walk(el, depth, rolestack):
        role = el.attrib.get("role", "")
        cls = el.attrib.get("class", "")
        for ch in el:
            if ch.tag == "w":
                osis = ch.attrib.get("osisId", "")
                if not osis or "!" not in osis:
                    continue
                c, v, wi = V1.parse_osis(osis)
                if c == chap and v == verse and ch.attrib.get("lemma") == "ὅτι":
                    print(f"  ὅτι @wi={wi}: enclosing clause role='{role}' class='{cls}' | rolestack={rolestack}")
            else:
                nr = ch.attrib.get("role", "")
                ncls = ch.attrib.get("class", "")
                tag = f"{ncls}:{nr}" if (ncls == "cl" or nr) else ncls
                walk(ch, depth + 1, rolestack + ([tag] if tag else []))

    walk(tree.getroot(), 0, [])
