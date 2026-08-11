"""Does Macula's clause-level role/rule discriminate complement-ὅτι (bind) from
causal/recitative-ὅτι (stand)? For each case, find the ὅτι word, walk up to the
clause <wg class='cl'> it heads, and print that clause's role + rule, plus the
embedded clause's verb person and any 1st/2nd-person referents."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import xml.etree.ElementTree as ET
from pathlib import Path

BOOKS = {"Matt": "01-matthew", "Mark": "02-mark", "Luke": "03-luke", "John": "04-john",
         "Acts": "05-acts", "Rom": "06-romans", "1Cor": "07-1corinthians",
         "Gal": "09-galatians", "Rev": "27-revelation"}
LF = Path(r"C:\Users\bibleman\repos\readers-gnt\research\macula-greek\SBLGNT\lowfat")

CASES = [("Matt", 5, 36, "CAUSAL->stand"), ("Rev", 10, 6, "COMPLEMENT->bind"),
         ("Rom", 8, 16, "COMPLEMENT->bind"), ("John", 2, 18, "CAUSAL->stand"),
         ("1Cor", 3, 13, "CAUSAL->stand"), ("Rom", 9, 17, "DIRECT-DISC->stand"),
         ("Gal", 3, 8, "1st bind / 2nd stand"), ("Mark", 5, 23, "RECITATIVE->stand")]

for book, chap, verse, note in CASES:
    tree = ET.parse(LF / f"{BOOKS[book]}.xml")
    root = tree.getroot()
    parent = {c: p for p in root.iter() for c in p}
    print(f"\n===== {book} {chap}:{verse} [{note}] =====")
    for w in root.iter("w"):
        ref = w.attrib.get("ref", "")
        if w.attrib.get("lemma") == "ὅτι" and ref.replace(" ", "") .startswith(f"{book.upper() if book!='1Cor' else '1CO'}"):
            pass
        if w.attrib.get("lemma") != "ὅτι":
            continue
        # ref like "MAT 5:36!7"
        try:
            bookref, rest = ref.split(" ", 1)
            cv, _ = rest.split("!")
            c, v = cv.split(":")
            if int(c) != chap or int(v) != verse:
                continue
        except Exception:
            continue
        # walk up printing EVERY ancestor wg (role+rule) to find the discriminator
        node = w
        stack = []
        while node in parent:
            node = parent[node]
            if node.tag == "wg":
                stack.append(f"[cls={node.attrib.get('class','')} "
                             f"role={node.attrib.get('role','')} "
                             f"rule={node.attrib.get('rule', node.attrib.get('Rule',''))}]")
            if node.tag == "sentence":
                break
        print("  ancestors(inner->outer): " + " > ".join(stack))
        clause = w  # for deixis loop, scan from sentence; just use first cl below
        # find nearest ancestor cl for deixis scan
        n2 = w
        while n2 in parent:
            n2 = parent[n2]
            if n2.tag == "wg" and n2.attrib.get("class") == "cl":
                clause = n2
                break
        # embedded clause verb person + 1st/2nd person referents
        persons = []
        for ww in clause.iter("w"):
            if ww.attrib.get("class") == "verb" and ww.attrib.get("mood") in ("indicative", "subjunctive", "imperative", "optative"):
                persons.append(f"{ww.attrib.get('normalized','')}={ww.attrib.get('person','')}")
            if ww.attrib.get("type") == "personal":
                persons.append(f"PRON {ww.attrib.get('normalized','')}={ww.attrib.get('person','')}")
        print(f"    deixis: {persons[:6]}")
