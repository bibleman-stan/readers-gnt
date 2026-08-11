#!/usr/bin/env python3
"""SBLGNT-native v1 — OUR FABRIC. Reads clause-atoms straight off sblgnt-lowfat
(clauses pre-marked as <wg class="cl">, words carry osisId verse+position + role
+ POS + lemma) and joins MorphGNT for mood (finite vs participle/infinitive).
No PROIEL, no edition gap, no reconciler: this IS the display text (SBLGNT).

Each word -> its INNERMOST containing <wg class="cl"> = its clause-atom. Atoms
are ordered by surface position (osisId word index). Output: document-ordered
clause-atoms with {verse, words(text/role/cls/mood/lemma), head verb + mood}.

Usage: cd /c/tmp && PYTHONIOENCODING=utf-8 python gnt_v1_sblgnt.py Matt 2
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

LOWFAT = Path(r"C:\Users\bibleman\repos\biblical-corpora\greek-new-testament\syntax-trees\sblgnt-lowfat\xml")
MORPH = Path(r"C:\Users\bibleman\repos\readers-gnt\research\morphgnt-sblgnt")
V0_DIR = Path(r"C:\Users\bibleman\repos\readers-gnt\data\text-files\v0-prose")
NUM = {"Matt": 1, "Mark": 2, "Luke": 3, "John": 4, "Acts": 5, "Rom": 6, "1Cor": 7,
       "2Cor": 8, "Gal": 9, "Eph": 10, "Phil": 11, "Col": 12, "1Thess": 13,
       "2Thess": 14, "1Tim": 15, "2Tim": 16, "Titus": 17, "Phlm": 18, "Heb": 19,
       "Jas": 20, "1Pet": 21, "2Pet": 22, "1John": 23, "2John": 24, "3John": 25,
       "Jude": 26, "Rev": 27}  # osisId prefix -> book number


def book_paths(num):
    """Derive all per-book paths from the 2-digit book number (01-27).
    Returns (lowfat_path, morph_path, v0_dir, slug, NN)."""
    nn = f"{num:02d}"
    lowfat = next(LOWFAT.glob(f"{nn}-*.xml"))
    morph = next(MORPH.glob(f"{num + 60}-*morphgnt.txt"))
    v0dir = next(p for p in V0_DIR.glob(f"{nn}-*") if p.is_dir())
    return lowfat, morph, v0dir, v0dir.name.split("-", 1)[1], nn


def chapters_of(v0dir, slug):
    nums = []
    for p in v0dir.glob(f"{slug}-*.txt"):
        m = re.search(r"-(\d+)\.txt$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return sorted(nums)
FINITE = set("IDSO")   # MorphGNT mood codes: Indic/iMperative? -> I D(imper) S(subj) O(opt)
NONFIN = set("NP")     # N=infinitive, P=participle


def load_morph_moods(path):
    """(chapter, verse, word_index_1based) -> (mood, pos, case). Book-agnostic:
    `path` is a single-book MorphGNT file (ref BBCCVV; book part ignored)."""
    moods, counters = {}, {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) < 7:
            continue
        ref, pos, code = p[0], p[1], p[2]
        ch, v = int(ref[2:4]), int(ref[4:6])
        idx = counters.get((ch, v), 0) + 1
        counters[(ch, v)] = idx
        # MorphGNT parse code: person TENSE voice MOOD CASE number gender degree
        tense = code[1] if len(code) > 1 and pos.startswith("V") else ""
        mood = code[3] if len(code) > 3 and pos.startswith("V") else ""
        case = code[4] if len(code) > 4 else ""
        moods[(ch, v, idx)] = (mood, pos, case, tense)
    return moods


def parse_osis(osis):
    # "Matt.2.1!4" -> (chapter, verse, wordidx)
    book_ch_v, w = osis.split("!")
    parts = book_ch_v.split(".")
    return int(parts[1]), int(parts[2]), int(w)


def extract(lowfat_path, morph_path, chap):
    tree = ET.parse(lowfat_path)
    moods = load_morph_moods(morph_path)
    atoms = {}  # innermost-cl id -> list of word dicts

    def is_cl(el):
        return el.tag == "wg" and el.attrib.get("class") == "cl"

    def walk(el, chain):
        if is_cl(el):
            chain = chain + [id(el)]
        for ch in el:
            if ch.tag == "w":
                osis = ch.attrib.get("osisId", "")
                if not osis or "!" not in osis:
                    continue
                c, v, wi = parse_osis(osis)
                if c != chap:
                    continue
                mood, mpos, mcase, mtense = moods.get((c, v, wi), ("", "", "", ""))
                cur_cl = chain[-1] if chain else None
                atoms.setdefault(cur_cl, []).append({
                    "verse": v, "wi": wi, "text": (ch.text or "").strip(),
                    "cls": ch.attrib.get("class", ""), "role": ch.attrib.get("role", ""),
                    "lemma": ch.attrib.get("lemma", ""), "mood": mood, "mpos": mpos,
                    "case": mcase, "tense": mtense, "osis": osis, "chain": chain})
            else:
                walk(ch, chain)

    walk(tree.getroot(), [])
    # order atoms by first surface word, drop empties
    ordered = []
    for cl_id, ws in atoms.items():
        ws = [w for w in ws if w["text"]]
        if ws:
            ws.sort(key=lambda w: (w["verse"], w["wi"]))
            ordered.append(ws)
    ordered.sort(key=lambda ws: (ws[0]["verse"], ws[0]["wi"]))
    return ordered


# Narrative books (Wallace feature 4) — Gospels + Acts. Book numbers per NUM.
NARRATIVE_BOOKS = {1, 2, 3, 4, 5}


def attendant_circ_participles(atom, book_num=None):
    """NODE-FEATURE: the aorist participles in a clause-atom that are PARTICIPLES
    OF ATTENDANT CIRCUMSTANCE per Wallace's 90% rule (Greek Grammar Beyond the
    Basics, 640-45): (1) aorist participle, (2) aorist main verb, (3) participle
    precedes the main verb, (4) narrative genre, (5) imperative/indicative main
    verb. All five are computable from the fabric: tense+mood from MorphGNT,
    precedence from osisId, genre from book_num. Returns the qualifying participle
    word dicts. Such a participle borrows the main verb's mood and is COORDINATE,
    not subordinate ("arise AND take") -> it binds to the finite verb as ONE ATU
    (which cl_features' finite-head selection already enforces structurally).

    Caveat: the 5 features are ~90% PRESENT in attendant circumstance but do not
    PROVE it (ordinary circumstantial participles share them); for ATU BINDING the
    distinction is moot — both bind. The tag is for annotation + binding-confidence."""
    if book_num is not None and book_num not in NARRATIVE_BOOKS:
        return []
    fins = [w for w in atom if w["mood"] in "ID" and w["tense"] == "A"]   # F2,F5
    out = []
    for w in atom:
        if w["mood"] == "P" and w["tense"] == "A":                        # F1
            if any((w["verse"], w["wi"]) < (f["verse"], f["wi"]) for f in fins):  # F3
                out.append(w)
    return out


def main():
    book = sys.argv[1] if len(sys.argv) > 1 else "Matt"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    lowfat, morph, _, _, _ = book_paths(NUM[book])
    atoms = extract(lowfat, morph, chap)
    print(f"=== {book} {chap}: SBLGNT-native clause-atoms (lowfat cl + MorphGNT mood) ===\n")
    for ws in atoms:
        verb = next((w for w in ws if w["mpos"].startswith("V")), None)
        if verb:
            kind = "FIN" if verb["mood"] in FINITE else ("ptcp" if verb["mood"] == "P"
                    else "inf" if verb["mood"] == "N" else verb["mood"])
            tag = f"[{kind} {verb['lemma']}]"
        else:
            tag = "[verbless]"
        vlabel = ws[0]["verse"]
        print(f" v{vlabel} {tag:18} " + " ".join(w["text"] for w in ws))


if __name__ == "__main__":
    main()
