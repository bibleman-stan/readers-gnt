"""
audit_hendiadys_merism_gnt.py
==============================

Survey GNT corpus for N=2 noun-coordinate pairs that are candidate
hendiadys (synonymy/cognate doubling) or merism (polar binary representing
totality). Analogous to bofm's hendiadys/merism survey
(2026-05-13 cross-conversation).

PHASE: framework-codification draft. Surfaces same-line conformance
percentages per candidate lemma-pair; informs future M1 closed-list
extension + canon §1/§5 codification of the hendiadys/merism distinction.

OUTPUT: per-pair same-line vs cross-line counts; cross-line cases listed
for editorial inspection.

NO CORPUS CHANGES — survey only.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
V4_GRK = REPO_ROOT / "data" / "text-files" / "v4" / "grk"

# Candidate pairs. Each pair: (member_a_forms, member_b_forms, category, gloss).
# Forms are inflectional variants (case/number) to match in surface text.
# Category: "hendiadys" (synonymy) or "merism" (polar totality).
CANDIDATE_PAIRS = [
    # === HENDIADYS (synonymy / cognate doubling) ===
    # χάρις + ἔλεος (grace and mercy) — Pastoral Epistles greetings
    (["χάρις", "χάριν", "χάριτος", "χάριτι"],
     ["ἔλεος", "ἐλέους", "ἔλει"],
     "hendiadys", "grace + mercy"),
    # χάρις + εἰρήνη (grace and peace) — Pauline opening formula
    (["χάρις", "χάριν", "χάριτος", "χάριτι"],
     ["εἰρήνη", "εἰρήνην", "εἰρήνης", "εἰρήνῃ"],
     "hendiadys", "grace + peace"),
    # ἔλεος + ἀλήθεια (mercy and truth)
    (["ἔλεος", "ἐλέους", "ἔλει"],
     ["ἀλήθεια", "ἀλήθειαν", "ἀληθείας", "ἀληθείᾳ"],
     "hendiadys", "mercy + truth"),
    # δικαιοσύνη + εἰρήνη (righteousness and peace)
    (["δικαιοσύνη", "δικαιοσύνην", "δικαιοσύνης", "δικαιοσύνῃ"],
     ["εἰρήνη", "εἰρήνην", "εἰρήνης", "εἰρήνῃ"],
     "hendiadys", "righteousness + peace"),
    # ἀγάπη + πίστις (love and faith)
    (["ἀγάπη", "ἀγάπην", "ἀγάπης", "ἀγάπῃ"],
     ["πίστις", "πίστιν", "πίστεως", "πίστει"],
     "hendiadys", "love + faith"),
    # δύναμις + σοφία (power and wisdom)
    (["δύναμις", "δύναμιν", "δυνάμεως", "δυνάμει"],
     ["σοφία", "σοφίαν", "σοφίας", "σοφίᾳ"],
     "hendiadys", "power + wisdom"),
    # δόξα + τιμή (glory and honor)
    (["δόξα", "δόξαν", "δόξης", "δόξῃ"],
     ["τιμή", "τιμήν", "τιμῆς", "τιμῇ"],
     "hendiadys", "glory + honor"),
    # φόβος + τρόμος (fear and trembling)
    (["φόβος", "φόβον", "φόβου", "φόβῳ"],
     ["τρόμος", "τρόμον", "τρόμου", "τρόμῳ"],
     "hendiadys", "fear + trembling"),
    # κόπος + μόχθος (labor and toil — ALREADY in M1)
    (["κόπος", "κόπον", "κόπου", "κόπῳ"],
     ["μόχθος", "μόχθον", "μόχθου", "μόχθῳ"],
     "hendiadys", "labor + toil (already M1)"),

    # === MERISM (polar binary representing totality) ===
    # Ἰουδαῖος + Ἕλλην (Jew and Greek = all humanity)
    (["Ἰουδαῖος", "Ἰουδαῖον", "Ἰουδαίου", "Ἰουδαίῳ", "Ἰουδαίους", "Ἰουδαίοις", "Ἰουδαίων"],
     ["Ἕλλην", "Ἕλληνα", "Ἕλληνος", "Ἕλληνι", "Ἕλληνες", "Ἕλληνας", "Ἕλλησιν", "Ἑλλήνων"],
     "merism", "Jew + Greek (all humanity)"),
    # οὐρανός + γῆ (heaven and earth = all creation)
    (["οὐρανός", "οὐρανόν", "οὐρανοῦ", "οὐρανῷ", "οὐρανοί", "οὐρανούς", "οὐρανῶν", "οὐρανοῖς"],
     ["γῆ", "γῆν", "γῆς", "γῇ"],
     "merism", "heaven + earth (all creation)"),
    # ἄρρην + θῆλυ (male and female = all humans)
    # Audit 2 fix: added neuter ἄρσεν (Gen 1:27 LXX form quoted in Matt 19:4 / Mark 10:6 / Gal 3:28)
    (["ἄρσεν", "ἄρρην", "ἄρσην", "ἄρσενα", "ἄρσενος", "ἄρρενος", "ἄρσενες", "ἄρρενες"],
     ["θῆλυ", "θῆλυν", "θήλεος", "θήλει", "θήλειαι", "θηλειῶν"],
     "merism", "male + female"),
    # Ἄλφα + Ω (Alpha and Omega — totality of time/existence)
    # Audit fix: actual NT form is Ὦ (rough breathing + circumflex), not bare Ω
    (["Ἄλφα"],
     ["Ὦ", "Ω"],
     "merism", "Alpha + Omega"),
    # πρῶτος + ἔσχατος (first and last)
    (["πρῶτος", "πρῶτον", "πρώτου", "πρώτῳ", "πρώτη", "πρώτην", "πρώτης"],
     ["ἔσχατος", "ἔσχατον", "ἐσχάτου", "ἐσχάτῳ", "ἐσχάτη", "ἐσχάτην", "ἐσχάτης"],
     "merism", "first + last"),
    # μικρός + μέγας (small and great = everyone)
    (["μικρός", "μικρόν", "μικροῦ", "μικρῷ", "μικροί", "μικρούς"],
     ["μέγας", "μέγαν", "μεγάλου", "μεγάλῳ", "μεγάλοι", "μεγάλους"],
     "merism", "small + great"),
    # πλούσιος + πτωχός (rich and poor = everyone)
    (["πλούσιος", "πλούσιον", "πλουσίου", "πλουσίῳ", "πλούσιοι"],
     ["πτωχός", "πτωχόν", "πτωχοῦ", "πτωχῷ", "πτωχοί", "πτωχούς"],
     "merism", "rich + poor"),
    # δοῦλος + ἐλεύθερος (slave and free)
    (["δοῦλος", "δοῦλον", "δούλου", "δούλῳ", "δοῦλοι", "δούλους"],
     ["ἐλεύθερος", "ἐλεύθερον", "ἐλευθέρου", "ἐλευθέρῳ", "ἐλεύθεροι", "ἐλευθέρους"],
     "merism", "slave + free"),
    # ζωή + θάνατος (life and death)
    (["ζωή", "ζωήν", "ζωῆς", "ζωῇ"],
     ["θάνατος", "θάνατον", "θανάτου", "θανάτῳ"],
     "merism", "life + death"),
]

GRK_BOOKS = sorted([d for d in V4_GRK.iterdir() if d.is_dir()])


def find_pair_in_corpus(member_a_forms, member_b_forms):
    """Find all occurrences of (member_a + καί + member_b) or (member_b + καί + member_a)
    in v4/grk. Returns list of (book_dir, file_name, line_idx, line_text, status).
    status = 'same_line' or 'cross_line' (members on adjacent lines).

    Audit 2 fix: extended coordinator set from {καί, τε} to include οὐδέ
    (negated coordination, e.g., Gal 3:28 `Ἰουδαῖος οὐδὲ Ἕλλην`) and εἴτε
    (correlative coordination, e.g., 1Cor 12:13 `εἴτε Ἰουδαῖοι εἴτε Ἕλληνες`).
    """
    COORDINATORS = {"καί", "καὶ", "τε", "οὐδέ", "οὐδὲ", "μηδέ", "μηδὲ",
                    "εἴτε", "εἴτʼ", "ἤ"}
    hits = []
    seen = set()  # dedup (book, line) so same hit doesn't count 2x via reverse pair
    pair_re = []
    for a in member_a_forms:
        for b in member_b_forms:
            pair_re.append((a, b))
            pair_re.append((b, a))

    for book_dir in GRK_BOOKS:
        for chap_file in sorted(book_dir.glob("*.txt")):
            text = chap_file.read_text(encoding="utf-8")
            lines = text.split("\n")
            for i, line in enumerate(lines):
                line_clean = re.sub(r"[,.;:·!?\(\)\[\]\"‘’“”ʼ·]", " ", line)
                tokens = line_clean.split()
                # Same-line check: pair separated by coordinator within reasonable span
                matched_same = False
                for j in range(len(tokens) - 2):
                    if matched_same:
                        break
                    for a, b in pair_re:
                        if tokens[j] == a:
                            # Look for any coordinator within next 4 tokens then b within next 3
                            for k in range(j + 1, min(j + 5, len(tokens))):
                                if tokens[k] in COORDINATORS:
                                    for m in range(k + 1, min(k + 4, len(tokens))):
                                        if tokens[m] == b:
                                            key = (chap_file.name, i + 1)
                                            if key not in seen:
                                                hits.append((book_dir.name, chap_file.name,
                                                           i + 1, line.strip(), "same_line"))
                                                seen.add(key)
                                                matched_same = True
                                            break
                                    if matched_same:
                                        break
                            if matched_same:
                                break
                # Cross-line check: line ends with member_a + καί, next line starts with member_b?
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    next_tokens = re.sub(r"[,.;:·!?\(\)\[\]\"‘’“”ʼ·]", " ", next_line).split()
                    for a, b in pair_re:
                        if a in tokens and tokens[-1] in {a, "καί", "καὶ"}:
                            # Check next-line starts with καί+b or b
                            if next_tokens and (next_tokens[0] in {"καί", "καὶ"} and
                                              len(next_tokens) > 1 and next_tokens[1] == b):
                                hits.append((book_dir.name, chap_file.name,
                                           i + 1, line.strip() + " / " + next_line.strip(),
                                           "cross_line"))
                                break
                            elif next_tokens and next_tokens[0] == b:
                                hits.append((book_dir.name, chap_file.name,
                                           i + 1, line.strip() + " / " + next_line.strip(),
                                           "cross_line"))
                                break
    return hits


def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    print(f"GNT Hendiadys + Merism Survey ({len(CANDIDATE_PAIRS)} candidate pairs)\n")
    print(f"{'='*80}\n")

    for member_a, member_b, category, gloss in CANDIDATE_PAIRS:
        hits = find_pair_in_corpus(member_a, member_b)
        same = [h for h in hits if h[4] == "same_line"]
        cross = [h for h in hits if h[4] == "cross_line"]
        total = len(hits)
        if total == 0:
            continue
        same_pct = (len(same) / total * 100) if total else 0
        print(f"[{category:9s}] {gloss}: same={len(same)} cross={len(cross)} total={total} conformance={same_pct:.0f}%")
        if cross:
            for book, fname, lineno, text, status in cross[:5]:
                print(f"    cross-line @ {fname}:{lineno}")
                print(f"        {text}")
        print()


if __name__ == "__main__":
    sys.exit(main())
