"""Dump deployed-vs-regenerated ATU partition for the changed verses, so the
R10/neg refinement can be audited verse-by-verse."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import sblgnt_v1_fabric as V1
import sblgnt_generate as G

DEPLOY = G.V4GRK
# (book, [verses]) from the drift gate
TARGETS = {
    "Matt": {5: ["5:23", "5:36"], 26: ["26:54"], 27: ["27:63"]},
    "Mark": {4: ["4:38"], 12: ["12:19"], 14: ["14:14", "14:58"]},
    "Luke": {10: ["10:40"], 16: ["16:25"], 20: ["20:20"], 24: ["24:33", "24:34"]},
    "John": {2: ["2:17", "2:18", "2:22"], 3: ["3:21"], 4: ["4:39"], 7: ["7:42"],
             11: ["11:50"], 12: ["12:16"], 15: ["15:25"], 16: ["16:4", "16:21"],
             17: ["17:7", "17:8"]},
    "Acts": {1: ["1:4", "1:5"], 6: ["6:14"], 14: ["14:9"], 19: ["19:26"], 20: ["20:35"]},
    "Rom": {8: ["8:16", "8:18"], 9: ["9:15", "9:17"], 10: ["10:5"]},
    "1Cor": {3: ["3:13"], 15: ["15:15"]},
    "2Cor": {10: ["10:7", "10:9", "10:10", "10:11"], 12: ["12:3", "12:4"]},
    "Gal": {3: ["3:8"]},
    "Eph": {2: ["2:11"]},
    "2Thess": {2: ["2:5"]},
    "Heb": {8: ["8:11", "8:12"]},
    "1John": {2: ["2:19"], 3: ["3:19", "3:20"], 4: ["4:9"]},
    "Rev": {3: ["3:9", "3:10"], 10: ["10:6"], 17: ["17:8"]},
}


def norm(lines):
    groups, cur = {}, None
    for ln in lines:
        s = ln.rstrip("\r\n")
        if not s.strip():
            continue
        tok0 = s.split()[0]
        if s[0].isdigit() and ":" in tok0 and all(c.isdigit() or c == ":" for c in tok0) and len(s.split()) == 1:
            cur = s.strip(); groups[cur] = []
        elif cur is not None:
            groups[cur].append(s.strip())
    return groups


for book, chaps in TARGETS.items():
    num = V1.NUM[book]
    lowfat, morph, v0dir, slug, nn = V1.book_paths(num)
    for chap, verses in chaps.items():
        gen = norm(G.emit_v4(lowfat, morph, v0dir, slug, chap))
        dep = norm((DEPLOY / f"{nn}-{slug}" / f"{slug}-{chap:02d}.txt").read_text(encoding="utf-8").splitlines())
        for v in verses:
            print(f"\n===== {book} {v} =====")
            print("  DEPLOYED (before):")
            for c in dep.get(v, []):
                print(f"    | {c}")
            print("  REGEN (after):")
            for c in gen.get(v, []):
                print(f"    | {c}")
