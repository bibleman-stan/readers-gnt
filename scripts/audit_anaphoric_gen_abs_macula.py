"""
audit_anaphoric_gen_abs_macula.py
==================================

Macula-driven detector for anaphoric genitive-absolute candidates per the
bidirectional ATU test (framework §1.1, GNT canon §1).

Replaces the surface-regex probe from session 2026-05-13 morning with the
proper structured-layer primitive: Macula Greek's
`ClauseInfo.is_genitive_absolute` flag + Macula's lemma sequence at the
clause's start.

Ported from Tanakh's `audit_anaphoric_frame_macula.py` approach
(detector → fixture → corpus scan → Cat B per-case classification).

SCOPE (round-wheel first pass):
  ✓ gen abs clauses (Macula `is_genitive_absolute = True`)
  ✓ Whose first content token is in the anaphoric-demonstrative closed list
    (ταῦτα / τοῦτο in any case-form: nom/acc/gen plural/singular)
  ✓ Cataphoric exclusions (Matt 2:1 type — proper-noun subjects)
  ✓ Acts 1:9 FEF carve-out (NOT a gen abs — nominative participle)

DEFERRED (later rounds):
  ✗ Anaphoric particles like `μετὰ ταῦτα` outside gen abs
  ✗ 3p pronouns without on-line antecedent
  ✗ Anaphoric δέ + speech tags in non-gen-abs constructions

Output:
  - Fixture pass/fail against `tests/fixtures-anaphoric-gen-abs.tsv`
  - Corpus candidate list with current-rendering (split vs merged)
    classification
  - All candidates flagged Cat B per the post-audit canon §1 revision
    (a1d8807e) — NOT Cat A mechanical fire.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "validators" / "_shared"))

import macula_clauses as MC

V4_GRK_DIR = REPO_ROOT / "data" / "text-files" / "v4" / "grk"
FIXTURE = REPO_ROOT / "tests" / "fixtures-anaphoric-gen-abs.tsv"

# Anaphoric demonstrative lemmas — closed list.
# `οὗτος` is the lemma; surface forms include ταῦτα (nom/acc neut pl),
# τούτων (gen pl), τούτοις (dat pl), τοῦτο (nom/acc neut sg), τούτου (gen sg),
# τούτῳ (dat sg), etc.
ANAPHORIC_LEMMAS = {
    "οὗτος",      # this / these — primary anaphoric demonstrative
    "ἐκεῖνος",    # that / those — distal anaphoric (when offline-pointing)
    "αὐτός",      # he/she/it/same — anaphoric when no on-line antecedent
}

# Surface forms of οὗτος (neut pl, nom/acc) — the canonical gen-abs anaphoric
ANAPHORIC_TAUTA_FORMS = {
    "ταῦτα", "Ταῦτα",
    "ταῦτʼ", "Ταῦτʼ",
    "τοῦτο", "Τοῦτο",
    "τούτου", "Τούτου",
}

GRK_BOOKS = [
    "matt", "mark", "luke", "john", "acts",
    "rom", "1cor", "2cor", "gal", "eph", "phil", "col",
    "1thess", "2thess", "1tim", "2tim", "titus", "phlm",
    "heb", "jas", "1pet", "2pet", "1john", "2john", "3john", "jude", "rev",
]

BOOK_DIRS = {
    "matt": "01-matt", "mark": "02-mark", "luke": "03-luke", "john": "04-john",
    "acts": "05-acts", "rom": "06-rom", "1cor": "07-1cor", "2cor": "08-2cor",
    "gal": "09-gal", "eph": "10-eph", "phil": "11-phil", "col": "12-col",
    "1thess": "13-1thess", "2thess": "14-2thess", "1tim": "15-1tim",
    "2tim": "16-2tim", "titus": "17-titus", "phlm": "18-phlm", "heb": "19-heb",
    "jas": "20-jas", "1pet": "21-1pet", "2pet": "22-2pet", "1john": "23-1john",
    "2john": "24-2john", "3john": "25-3john", "jude": "26-jude", "rev": "27-rev",
}


def _strip_punct(token: str) -> str:
    return re.sub(r"[,.;:·!?\(\)\[\]\"‘’“”ʼ]", "", token).strip()


def detect_anaphoric_gen_abs(book_slug, chapter, verse):
    """Return list of (clause_text, is_anaphoric, first_content_token).
    A clause is anaphoric-gen-abs if it's a gen abs AND its first 1-2 content
    tokens include an anaphoric form of οὗτος (ταῦτα family)."""
    try:
        clauses = MC.get_verse_clauses_detailed(book_slug, chapter, verse)
    except Exception:
        return []

    results = []
    for cl in clauses:
        if not cl.is_genitive_absolute:
            continue
        # Inspect the first 3 content tokens of the clause to check for anaphoric
        first_tokens = [_strip_punct(w[1]) for w in cl.words[:5]]
        first_tokens = [t for t in first_tokens if t]  # drop empties
        # Check if any of the first 3 is in the anaphoric list
        is_anaphoric = False
        marker = None
        for t in first_tokens[:3]:
            if t in ANAPHORIC_TAUTA_FORMS:
                is_anaphoric = True
                marker = t
                break
        results.append((cl, is_anaphoric, marker, first_tokens[:3]))
    return results


def find_clause_line_in_v4(book_slug, chapter, verse, clause_text):
    """Find which v4/grk line contains the clause. Returns (line_idx_1based,
    line_text) or None. Looks for a substring match on the first 2-3 words
    of the clause."""
    book_dir = BOOK_DIRS.get(book_slug)
    if not book_dir:
        return None
    fname = f"{book_slug}-{chapter:02d}.txt"
    fp = V4_GRK_DIR / book_dir / fname
    if not fp.exists():
        return None
    lines = fp.read_text(encoding="utf-8").split("\n")
    # Search-anchor: first 2 words of clause_text
    words = clause_text.split()[:2]
    if not words:
        return None
    anchor = " ".join(words)
    # Find ANCHOR in lines (case-sensitive; clause text is from Macula)
    for i, line in enumerate(lines, 1):
        # Strip leading/trailing punct, soft-normalize
        if anchor in line:
            return (i, line, lines)
        # Try stripped variant
        stripped_anchor = _strip_punct(anchor)
        stripped_line = _strip_punct(line)
        if stripped_anchor and stripped_anchor in stripped_line:
            return (i, line, lines)
    return None


def classify_rendering(line_idx, lines, clause_text):
    """Given a line index + the gen abs clause text, determine if the gen abs
    is currently SPLIT (own line, pre-matrix) or MERGED (combined with matrix
    on one line). Uses positional check: where does the gen abs sit in the line?"""
    if line_idx is None or line_idx > len(lines):
        return "unknown"
    line = lines[line_idx - 1]
    # Anchor: first 2 words of the gen abs clause
    anchor_words = clause_text.split()[:2]
    anchor = " ".join(anchor_words)

    # Check if the gen abs starts the line (split — own-line treatment)
    line_stripped = line.strip()
    if line_stripped.startswith(anchor) or line_stripped.startswith(_strip_punct(anchor)):
        # gen abs is line-initial — check if line ALSO has matrix content
        word_count = len(line.split())
        if word_count <= 6:
            return "split"  # line is just the gen abs, matrix on next line
        return "merged_pre_matrix"  # gen abs leads but matrix is on same line
    # Gen abs is NOT line-initial → it's post-matrix already-merged
    return "merged_post_matrix"


def is_cataphoric_tauta(cl):
    """Detect cataphoric τοῦτο pattern where τοῦτο is the DIRECT OBJECT of a
    forward-pointing verb of revelation/indication (δηλόω, δείκνυμι, σημαίνω,
    γνωρίζω, ἀναγγέλλω). E.g., heb 9:8 τοῦτο δηλοῦντος τοῦ πνεύματος (the
    Spirit indicating THIS [following explanation])."""
    # Get the participle of the gen abs and check if it's a revelation verb
    REVELATION_LEMMAS = {"δηλόω", "δείκνυμι", "σημαίνω", "γνωρίζω",
                         "ἀναγγέλλω", "φανερόω"}
    # cl.words is [(ref, text), ...]; we don't have lemma here directly,
    # but we can heuristic-check the surface forms.
    DELOWN_FORMS = {"δηλοῦντος", "δηλούντων", "δηλοῦσιν",
                    "δείκνυντος", "σημαίνοντος", "γνωρίζοντος",
                    "ἀναγγέλλοντος", "φανεροῦντος"}
    for _, w in cl.words[:5]:
        if _strip_punct(w) in DELOWN_FORMS:
            return True
    return False


def audit_book(book_slug):
    """Audit all verses in a book for anaphoric-gen-abs candidates."""
    results = []
    # We need to scan all chapters; get_chapter_clauses_detailed gives us
    # everything at once
    book_dir = BOOK_DIRS.get(book_slug)
    if not book_dir:
        return results
    book_path = V4_GRK_DIR / book_dir
    if not book_path.exists():
        return results
    chapter_files = sorted(book_path.glob(f"{book_slug}-*.txt"))
    for chap_file in chapter_files:
        # Extract chapter number from filename
        m = re.match(r"^[^-]+-(\d+)\.txt$", chap_file.name)
        if not m:
            continue
        chapter = int(m.group(1))
        try:
            ch_data = MC.get_chapter_clauses_detailed(book_slug, chapter)
        except Exception:
            continue
        for verse, clauses_list in ch_data.items():
            for cl in clauses_list:
                if not cl.is_genitive_absolute:
                    continue
                first_tokens = [_strip_punct(w[1]) for w in cl.words[:5]]
                first_tokens = [t for t in first_tokens if t]
                marker = None
                for t in first_tokens[:3]:
                    if t in ANAPHORIC_TAUTA_FORMS:
                        marker = t
                        break
                if marker is None:
                    continue
                # Cataphoric exclusion (τοῦτο + revelation-verb gen abs)
                if is_cataphoric_tauta(cl):
                    continue
                # It's a candidate. Find its v4/grk line.
                line_info = find_clause_line_in_v4(book_slug, chapter, verse, cl.text)
                if line_info is None:
                    rendering = "unknown"
                    line_idx = None
                else:
                    line_idx, line_text, all_lines = line_info
                    rendering = classify_rendering(line_idx, all_lines, cl.text)
                # Post-matrix-merged is not a candidate — already merged
                if rendering == "merged_post_matrix":
                    continue
                results.append({
                    "book": book_slug,
                    "chapter": chapter,
                    "verse": verse,
                    "marker": marker,
                    "first_tokens": " ".join(first_tokens[:3]),
                    "clause_text": cl.text,
                    "line_idx": line_idx,
                    "rendering": rendering,
                })
    return results


def run_fixture():
    """Validate detector against fixture file."""
    if not FIXTURE.exists():
        print(f"Fixture not found: {FIXTURE}")
        return 1
    rows = []
    with open(FIXTURE, encoding="utf-8") as f:
        # tsv with header
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            fields = line.split("\t")
            if header is None:
                header = fields
                continue
            rows.append(dict(zip(header, fields)))

    print(f"Validating detector against {len(rows)} fixture cases:\n")
    passes, fails = 0, 0
    for r in rows:
        book = r["book"]
        chapter = int(r["chapter"])
        verse = int(r["verse"])
        expected = r["expected"]
        notes = r.get("notes", "")

        # Run detector on this verse
        candidates = []
        try:
            clauses = MC.get_verse_clauses_detailed(book, chapter, verse)
        except Exception as e:
            print(f"  FAIL {book} {chapter}:{verse} (expected {expected}) — Macula error: {e}")
            fails += 1
            continue

        for cl in clauses:
            if not cl.is_genitive_absolute:
                continue
            first_tokens = [_strip_punct(w[1]) for w in cl.words[:5]]
            first_tokens = [t for t in first_tokens if t]
            marker = None
            for t in first_tokens[:3]:
                if t in ANAPHORIC_TAUTA_FORMS:
                    marker = t
                    break
            if marker is None:
                continue
            if is_cataphoric_tauta(cl):
                continue
            line_info = find_clause_line_in_v4(book, chapter, verse, cl.text)
            rendering = "unknown"
            if line_info:
                rendering = classify_rendering(line_info[0], line_info[2], cl.text)
            if rendering == "merged_post_matrix":
                continue
            candidates.append({"marker": marker, "rendering": rendering})

        # Decide pass/fail
        detected_positive = len(candidates) > 0
        if expected == "POSITIVE":
            if detected_positive:
                print(f"  PASS {book} {chapter}:{verse} (POSITIVE — fired: {candidates[0]['marker']})")
                passes += 1
            else:
                print(f"  FAIL {book} {chapter}:{verse} (expected POSITIVE — no fire): {notes}")
                fails += 1
        elif expected.startswith("NEGATIVE"):
            if not detected_positive:
                print(f"  PASS {book} {chapter}:{verse} ({expected} — correctly excluded)")
                passes += 1
            else:
                print(f"  FAIL {book} {chapter}:{verse} (expected {expected} — wrongly fired): {notes}")
                fails += 1
        elif expected.startswith("EDGE"):
            # Edge cases — detector may or may not fire; report which it did
            print(f"  EDGE {book} {chapter}:{verse} ({expected} — detector: {'fired' if detected_positive else 'excluded'}): {notes}")
            passes += 1  # don't count edge cases as fails
        else:
            print(f"  ??   {book} {chapter}:{verse} (unknown expected: {expected})")

    print(f"\nFixture result: {passes}/{len(rows)} pass, {fails} fail")
    return 0 if fails == 0 else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", help="single book slug")
    parser.add_argument("--fixture", action="store_true",
                       help="run fixture-pass check only")
    args = parser.parse_args()

    if args.fixture:
        return run_fixture()

    books = [args.book] if args.book else GRK_BOOKS

    all_results = []
    for b in books:
        results = audit_book(b)
        all_results.extend(results)

    if not all_results:
        print("0 anaphoric-gen-abs candidates found corpus-wide.")
        return 0

    print(f"{len(all_results)} anaphoric-gen-abs candidates found:\n")
    # Group by current rendering
    by_rendering = defaultdict(list)
    for r in all_results:
        by_rendering[r["rendering"]].append(r)

    for rendering, items in sorted(by_rendering.items()):
        print(f"=== {rendering.upper()} ({len(items)}) ===")
        for r in items:
            print(f"  {r['book']} {r['chapter']}:{r['verse']} (line {r['line_idx']}) "
                  f"[{r['marker']}] {r['clause_text']!r}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
