#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_hoti_complement.py

Detects ὅτι lines that may be complementizer ὅτι (indirect discourse)
erroneously broken off from their governing verb onto a separate line.

GRAMMATICAL BASIS:
  Verbs of cognition, communication, perception, and belief (γράφω, οἶδα,
  γινώσκω, λέγω, ἀκούω, ὁράω, πιστεύω, μαρτυρέω, etc.) govern a ὅτι
  complement clause that functions as their direct object / argument. The
  verb + ὅτι + complement clause form ONE propositional unit — one atomic
  thought. There is no thought boundary between them, so there should be
  no line break between them.

  This is distinct from causal ὅτι ("because X") or result ὅτι, which
  introduce genuinely separate clauses and warrant their own lines.

DETECTION METHOD:
  For each text line starting with ὅτι, check whether the immediately
  preceding text line in the same verse ends with a token whose
  accent-stripped form appears in the GOVERNING_VERBS set. If so, flag
  as a HIGH CONFIDENCE candidate — the preceding verb governs this ὅτι
  clause and they should likely be on one line.

  A second pass flags REVIEW candidates: lines starting with ὅτι where
  the preceding line contains a governing verb anywhere (not just at end)
  but does not end with one. Lower confidence; causal ὅτι more likely.

Usage:
  py -3 scripts/scan_hoti_complement.py

Output:
  Console summary + private/scan-hoti-complement-findings.md
"""

import unicodedata
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

# ─── paths ────────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).parent.parent
V4_DIR      = REPO_ROOT / "data" / "text-files" / "v4-editorial"
PRIVATE_DIR = REPO_ROOT / "private"
OUT_FILE    = PRIVATE_DIR / "scan-hoti-complement-findings.md"

# ─── accent stripping ─────────────────────────────────────────────────────────

def strip_accents(s: str) -> str:
    """Return lowercase Greek string with all diacriticals removed."""
    nfd = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def tokens(line: str) -> List[str]:
    """Split a line into word tokens, stripping punctuation."""
    import re
    words = re.findall(r"[\w\u0300-\u036f\u1f00-\u1fff\u0370-\u03ff]+", line, re.UNICODE)
    return words


# ─── governing verbs (accent-stripped forms) ──────────────────────────────────
# Verbs that take a complementizer ὅτι clause as their argument.
# Forms are accent-stripped (no diacriticals) and lowercase.
# Organized by verb family for maintainability.

GOVERNING_VERBS: set = {
    # γράφω — write
    "γραφω", "γραφεις", "γραφει", "γραφομεν", "γραφετε", "γραφουσιν",
    "εγραψα", "εγραψας", "εγραψεν", "εγραψαμεν", "εγραψατε", "εγραψαν",
    "γεγραφα", "γεγραφας", "γεγραφεν", "γεγραμμαι",

    # οἶδα — know
    "οιδα", "οιδας", "οιδεν", "οιδαμεν", "οιδατε", "οιδασιν",
    "ηδειν", "ηδεις", "ηδει", "ηδειμεν", "ηδειτε", "ηδεισαν",

    # γινώσκω — know, come to know
    "γινωσκω", "γινωσκεις", "γινωσκει", "γινωσκομεν", "γινωσκετε", "γινωσκουσιν",
    "εγνων", "εγνως", "εγνω", "εγνωμεν", "εγνωτε", "εγνωσαν",
    "εγνωκα", "εγνωκας", "εγνωκεν", "εγνωκαμεν", "εγνωκατε", "εγνωκασιν",

    # λέγω / εἶπον — say, tell
    "λεγω", "λεγεις", "λεγει", "λεγομεν", "λεγετε", "λεγουσιν",
    "ειπον", "ειπας", "ειπεν", "ειπαμεν", "ειπατε", "ειπαν",
    "ειρηκα", "ειρηκας", "ειρηκεν", "ειρηκαμεν", "ειρηκατε", "ειρηκασιν",
    "ελεγον", "ελεγες", "ελεγεν", "ελεγομεν", "ελεγετε", "ελεγον",

    # ἀκούω — hear
    "ακουω", "ακουεις", "ακουει", "ακουομεν", "ακουετε", "ακουουσιν",
    "ηκουσα", "ηκουσας", "ηκουσεν", "ηκουσαμεν", "ηκουσατε", "ηκουσαν",
    "ακηκοα", "ακηκοας", "ακηκοεν", "ακηκοαμεν", "ακηκοατε", "ακηκοασιν",

    # ὁράω / εἶδον / βλέπω / θεωρέω — see
    "ορω", "ορας", "ορα", "ορωμεν", "ορατε", "ορωσιν",
    "ειδον", "ειδες", "ειδεν", "ειδομεν", "ειδετε", "ειδαν",
    "εωρακα", "εωρακας", "εωρακεν", "εωρακαμεν", "εωρακατε", "εωρακασιν",
    "βλεπω", "βλεπεις", "βλεπει", "βλεπομεν", "βλεπετε", "βλεπουσιν",
    "θεωρω", "θεωρεις", "θεωρει", "θεωρουμεν", "θεωρειτε", "θεωρουσιν",
    "εθεωρουν", "εθεωρεις", "εθεωρει", "εθεωρουμεν", "εθεωρειτε", "εθεωρουν",

    # πιστεύω — believe
    "πιστευω", "πιστευεις", "πιστευει", "πιστευομεν", "πιστευετε", "πιστευουσιν",
    "επιστευσα", "επιστευσας", "επιστευσεν", "επιστευσαμεν", "επιστευσατε", "επιστευσαν",
    "πεπιστευκα", "πεπιστευκας", "πεπιστευκεν", "πεπιστευκαμεν", "πεπιστευκατε",

    # μαρτυρέω — testify, bear witness
    "μαρτυρω", "μαρτυρεις", "μαρτυρει", "μαρτυρουμεν", "μαρτυρειτε", "μαρτυρουσιν",
    "εμαρτυρησα", "εμαρτυρησας", "εμαρτυρησεν", "εμαρτυρησαμεν", "εμαρτυρησατε", "εμαρτυρησαν",
    "μεμαρτυρηκα", "μεμαρτυρηκας", "μεμαρτυρηκεν",

    # ὁμολογέω — confess, acknowledge
    "ομολογω", "ομολογεις", "ομολογει", "ομολογουμεν", "ομολογειτε", "ομολογουσιν",
    "ωμολογησα", "ωμολογησας", "ωμολογησεν", "ωμολογησαμεν", "ωμολογησατε", "ωμολογησαν",

    # νομίζω / δοκέω — think, suppose
    "νομιζω", "νομιζεις", "νομιζει", "νομιζομεν", "νομιζετε", "νομιζουσιν",
    "ενομιζον", "ενομιζες", "ενομιζεν",
    "δοκω", "δοκεις", "δοκει", "δοκουμεν", "δοκειτε", "δοκουσιν",
    "εδοκουν", "εδοκεις", "εδοκει",

    # ἐπίσταμαι — know, understand
    "επισταμαι", "επιστασαι", "επισταται", "επιστεμεθα", "επιστασθε", "επιστανται",
    "ηπιστατο",

    # εὑρίσκω — find (sometimes takes ὅτι)
    "ευρισκω", "ευρισκεις", "ευρισκει", "ευρισκομεν", "ευρισκετε", "ευρισκουσιν",
    "ευρον", "ευρες", "ευρεν", "ευρομεν", "ευρετε", "ευροσαν",
    "ευρηκα", "ευρηκας", "ευρηκεν",

    # φανερόω / δηλόω — reveal, show, make clear
    "φανερω", "φανερεις", "φανερει", "φανερουμεν", "φανερειτε", "φανερουσιν",
    "εφανερωσα", "εφανερωσας", "εφανερωσεν", "εφανερωσαμεν", "εφανερωσατε", "εφανερωσαν",
    "πεφανερωκα", "πεφανερωται", "πεφανερωνται",
    "δηλω", "δηλοις", "δηλοι", "εδηλωσα", "εδηλωσας", "εδηλωσεν",

    # ἀναγγέλλω / ἀπαγγέλλω / καταγγέλλω — announce, report, proclaim
    "αναγγελλω", "αναγγελεις", "αναγγελει",
    "ανηγγειλα", "ανηγγειλας", "ανηγγειλεν",
    "απαγγελλω", "απαγγελεις", "απαγγελει",
    "απηγγειλα", "απηγγειλας", "απηγγειλεν",
    "καταγγελλω", "καταγγελεις", "καταγγελει",
    "κατηγγειλα", "κατηγγειλας", "κατηγγειλεν",

    # κηρύσσω / εὐαγγελίζω — proclaim, preach
    "κηρυσσω", "κηρυσσεις", "κηρυσσει", "κηρυσσομεν", "κηρυσσετε", "κηρυσσουσιν",
    "εκηρυξα", "εκηρυξας", "εκηρυξεν",
    "ευαγγελιζω", "ευαγγελιζεις", "ευαγγελιζει", "ευαγγελιζομαι",
    "ευηγγελισαμην", "ευηγγελισατο",

    # γνωρίζω — make known
    "γνωριζω", "γνωριζεις", "γνωριζει", "γνωριζομεν", "γνωριζετε", "γνωριζουσιν",
    "εγνωρισα", "εγνωρισας", "εγνωρισεν",

    # ἐλπίζω — hope (takes ὅτι occasionally)
    "ελπιζω", "ελπιζεις", "ελπιζει", "ελπιζομεν", "ελπιζετε", "ελπιζουσιν",
    "ηλπισα", "ηλπισας", "ηλπισεν",

    # φοβέομαι — fear (μή often, but sometimes ὅτι)
    "φοβουμαι", "φοβη", "φοβειται", "φοβουμεθα", "φοβεισθε", "φοβουνται",
    "εφοβηθην", "εφοβηθης", "εφοβηθη",
}


# ─── corpus parsing ────────────────────────────────────────────────────────────

def parse_file(path: Path):
    """
    Yields (verse_ref, line_number, line_text) for each text line.
    Blank lines serve as verse boundaries.
    """
    current_verse = None
    with open(path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                continue
            # verse reference lines: contain ':' and no spaces (e.g. '1:1', '12:34')
            import re
            if re.match(r"^\d+:\d+$", stripped):
                current_verse = stripped
                continue
            if current_verse:
                yield current_verse, lineno, line


def parse_file_with_blanks(path: Path):
    """
    Yields (verse_ref, lineno, line_text, is_blank) — preserving blank lines
    so we can detect verse boundaries.
    """
    import re
    current_verse = None
    with open(path, encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if re.match(r"^\d+:\d+$", stripped):
                current_verse = stripped
                continue
            yield current_verse, lineno, line, (stripped == "")


# ─── detection ────────────────────────────────────────────────────────────────

def is_hoti_line(line: str) -> bool:
    """True if line starts with ὅτι (case-insensitive, accent-stripped)."""
    toks = tokens(line)
    if not toks:
        return False
    return strip_accents(toks[0]) == "οτι"


def last_token_stripped(line: str) -> Optional[str]:
    """Return the accent-stripped last meaningful token of a line."""
    toks = tokens(line)
    if not toks:
        return None
    return strip_accents(toks[-1])


def any_governing_verb(line: str) -> bool:
    """True if any token in the line is a governing verb (accent-stripped)."""
    return any(strip_accents(t) in GOVERNING_VERBS for t in tokens(line))


def scan_file(path: Path) -> List[Dict]:
    """
    Scan one file for complementizer ὅτι candidates.
    Returns list of candidate dicts.
    """
    # Build list of (verse_ref, lineno, text) grouped by verse
    verses: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
    verse_order = []

    import re
    current_verse = None
    with open(path, encoding="utf-8") as f:
        lines_by_verse: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if re.match(r"^\d+:\d+$", stripped):
                if current_verse is None or current_verse != stripped:
                    current_verse = stripped
                    if current_verse not in verse_order:
                        verse_order.append(current_verse)
                continue
            if stripped and current_verse:
                lines_by_verse[current_verse].append((lineno, line))

    candidates = []
    for verse_ref in verse_order:
        verse_lines = lines_by_verse[verse_ref]
        for i, (lineno, line) in enumerate(verse_lines):
            if not is_hoti_line(line):
                continue
            if i == 0:
                # First line of verse starts with ὅτι — could be continuation
                # from previous verse; not our target pattern
                continue

            prev_lineno, prev_line = verse_lines[i - 1]
            last_tok = last_token_stripped(prev_line)
            prev_has_gov = last_tok in GOVERNING_VERBS

            # Also check if any token in preceding line is a governing verb
            prev_any_gov = any_governing_verb(prev_line)

            if prev_has_gov:
                confidence = "HIGH"
            elif prev_any_gov:
                confidence = "REVIEW"
            else:
                continue  # no governing verb nearby — skip

            candidates.append({
                "file": str(path.relative_to(REPO_ROOT)),
                "book": path.parent.name,
                "chapter": path.stem,
                "verse": verse_ref,
                "lineno": lineno,
                "line": line.strip(),
                "prev_lineno": prev_lineno,
                "prev_line": prev_line.strip(),
                "confidence": confidence,
                "governing_verb": last_tok if prev_has_gov else "(mid-line)",
            })

    return candidates


def scan_corpus() -> List[Dict]:
    candidates = []
    book_dirs = sorted(V4_DIR.iterdir())
    for book_dir in book_dirs:
        if not book_dir.is_dir():
            continue
        for txt_file in sorted(book_dir.glob("*.txt")):
            candidates.extend(scan_file(txt_file))
    return candidates


# ─── report ───────────────────────────────────────────────────────────────────

def write_report(candidates: List[Dict]):
    high = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]

    book_counts: Dict[str, int] = defaultdict(int)
    for c in candidates:
        book_counts[c["book"]] += 1

    lines = []
    lines.append("# ὅτι Complement Clause Scan — Findings Report\n")
    lines.append(f"**Generated:** 2026-04-15")
    lines.append(f"**Scanner:** scan_hoti_complement.py v1")
    lines.append(f"**Corpus:** data/text-files/v4-editorial/ — all 260 chapters\n")
    lines.append("## Grammatical basis\n")
    lines.append(
        "Verbs of cognition, communication, perception, and belief govern a ὅτι\n"
        "complement clause as their direct argument. The verb + ὅτι + complement\n"
        "form one propositional unit — one atomic thought. No line break belongs\n"
        "between them. This differs from causal ὅτι ('because X') or result ὅτι,\n"
        "which introduce separate clauses and warrant their own lines.\n"
    )
    lines.append("---\n")
    lines.append("## Summary\n")
    lines.append(f"- **Total candidates:** {len(candidates)}")
    lines.append(f"- **HIGH confidence** (preceding line ends with governing verb): {len(high)}")
    lines.append(f"- **REVIEW** (governing verb mid-line in preceding): {len(review)}\n")
    lines.append("### By book\n")
    for book, count in sorted(book_counts.items(), key=lambda x: -x[1])[:12]:
        lines.append(f"- {book}: {count}")
    lines.append("\n---\n")

    for label, group in [("HIGH CONFIDENCE", high), ("REVIEW", review)]:
        lines.append(f"## {label} candidates ({len(group)})\n")
        for i, c in enumerate(group, 1):
            lines.append(f"### {label} {i}: `{c['book']}` — {c['chapter']} — {c['verse']}\n")
            lines.append(f"- **File:** `{c['file']}` (line {c['lineno']})")
            lines.append(f"- **Confidence:** {c['confidence']}")
            if c['confidence'] == 'HIGH':
                lines.append(f"- **Governing verb (line-final):** `{c['governing_verb']}`")
            lines.append(f"\n**Preceding line (line {c['prev_lineno']}):**")
            lines.append(f"```\n  {c['prev_line']}\n```")
            lines.append(f"**ὅτι line (line {c['lineno']}):**")
            lines.append(f"```\n  {c['line']}\n```\n")

    lines.append("---\n")
    lines.append("## Adversarial audit notes\n")
    lines.append("*(To be filled in after parallel sub-agent review.)*\n")
    lines.append("---\n")
    lines.append("## False positive patterns\n")
    lines.append(
        "Expected FP sources:\n"
        "1. Causal ὅτι after a governing verb that happens to be sentence-final\n"
        "   (e.g. 'I rejoiced, because...' where the ὅτι is causal not complementizer)\n"
        "2. REVIEW candidates where the governing verb governs a different clause,\n"
        "   not the following ὅτι line\n"
        "3. Quotation formulas (εἶπεν / ἔγραψεν γέγραπται) followed by a ὅτι\n"
        "   introducing direct discourse — these may be correct splits if the\n"
        "   speech frame is long enough to warrant its own line\n"
    )

    PRIVATE_DIR.mkdir(exist_ok=True)
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {OUT_FILE}")


# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Scanning corpus for complementizer ὅτι candidates...")
    candidates = scan_corpus()
    high = [c for c in candidates if c["confidence"] == "HIGH"]
    review = [c for c in candidates if c["confidence"] == "REVIEW"]
    print(f"  Total candidates: {len(candidates)}")
    print(f"  HIGH confidence:  {len(high)}")
    print(f"  REVIEW:           {len(review)}")

    book_counts: Dict[str, int] = defaultdict(int)
    for c in candidates:
        book_counts[c["book"]] += 1
    print("\nTop books:")
    for book, count in sorted(book_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {book}: {count}")

    write_report(candidates)


if __name__ == "__main__":
    main()
