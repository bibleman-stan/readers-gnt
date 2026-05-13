"""
scan_r18_class3_orphan_vocatives.py
====================================

Surface candidates for R18 Class 3 (object-appositive merge) where a vocative
phrase sits on its own line but the IMMEDIATELY PRECEDING content line carries
a 2p element (pronoun OR 2p finite verb) within the same clause-span.

Motivation: Matt 2:6 case (commit 1023ef23) revealed that some OT-quote
passages preserve Hebrew poetic colon structure against R18 Class 3 + §8
Fronting Paradox. Stan asked for corpus audit (2026-05-13). Per CLAUDE.md,
this surfaces candidates for editorial review; auto-application is Cat A
when the rule fires unambiguously.

Surface signature:
  - Line N: contains a 2p element (σύ-family pronoun OR 2p finite verb)
            AND does NOT end with a speech-boundary (ano teleia · or colon :)
  - Line N+1: is a vocative-only or vocative-dominant phrase (>=1 token in
              vocative case per MorphGNT, no finite verb)

Output: candidate report grouped by book, with verse-ref + line excerpts.
"""

import argparse
import os
import sys
import re
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validators", "_shared"))
import morphgnt_lookup as M

REPO_ROOT = Path(__file__).resolve().parent.parent
GRK_DIR = REPO_ROOT / "data" / "text-files" / "v4" / "grk"

# 2p pronoun surface forms (covers σύ-family, both sg and pl)
TWO_P_PRONOUN_FORMS = {
    "σύ", "σου", "σοῦ", "σοι", "σοί", "σε", "σέ",
    "ὑμεῖς", "ὑμῶν", "ὑμᾶς", "ὑμῖν",
}

# Speech-boundary characters that close the clause-span (per canon §3.5/§3.6)
SPEECH_BOUNDARIES = ("·", ":")

VERSE_REF_RE = re.compile(r"^\d+:\d+\s*$")


def _clean_token(tok):
    """Strip punctuation from a Greek token for lookup matching."""
    return re.sub(r"[,.;:·!?\(\)\[\]\"‘’“”]", "", tok).strip()


def line_has_2p_element(line, book_slug, chapter, verse):
    """Return True if the line contains a 2p pronoun or 2p finite verb."""
    M._load_book(book_slug)
    verse_data = M._verse_cache[book_slug].get((chapter, verse), [])
    if not verse_data:
        return False
    line_tokens = {_clean_token(t) for t in line.split() if _clean_token(t)}
    for word, pos, parsing in verse_data:
        cw = _clean_token(word)
        if cw not in line_tokens:
            continue
        # 2p pronoun by surface form (lemma-encoded — MorphGNT RP doesn't put
        # person in the parsing, but the lemma cluster is small)
        if cw in TWO_P_PRONOUN_FORMS:
            return True
        # 2p finite verb: pos starts 'V', parsing starts with '2'
        if pos.startswith("V") and parsing and parsing[0] == "2":
            return True
    return False


def line_is_vocative_dominant(line, book_slug, chapter, verse):
    """Return True if the line has at least one vocative-case word and no finite verb."""
    M._load_book(book_slug)
    verse_data = M._verse_cache[book_slug].get((chapter, verse), [])
    if not verse_data:
        return False
    line_tokens = {_clean_token(t) for t in line.split() if _clean_token(t)}
    has_vocative = False
    has_finite = False
    for word, pos, parsing in verse_data:
        cw = _clean_token(word)
        if cw not in line_tokens:
            continue
        # Vocative case: parsing position 4 (0-indexed) == 'V'
        if pos.startswith("N") and parsing and len(parsing) > 4 and parsing[4] == "V":
            has_vocative = True
        # Finite verb: pos starts 'V' AND mood is Indicative/Subjunctive/Optative/Imperative
        if pos.startswith("V") and parsing and len(parsing) > 3 and parsing[3] in ("I", "S", "O", "D"):
            has_finite = True
    return has_vocative and not has_finite


def line_ends_with_speech_boundary(line):
    s = line.rstrip()
    return s.endswith(SPEECH_BOUNDARIES)


def scan_book(book_dir):
    """Scan all chapter files in a book directory. Yield candidates."""
    book_slug = book_dir.name.split("-", 1)[1] if "-" in book_dir.name else book_dir.name
    candidates = []
    for chap_file in sorted(book_dir.glob("*.txt")):
        text = chap_file.read_text(encoding="utf-8")
        lines = text.split("\n")
        current_verse = None
        # Build (line_idx, line_text, chapter, verse) tuples for content lines only
        line_meta = []
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                line_meta.append((idx, line, None, None, "blank"))
                continue
            m = VERSE_REF_RE.match(stripped)
            if m:
                current_verse = stripped
                line_meta.append((idx, line, None, None, "verseref"))
                continue
            if current_verse:
                try:
                    chap_s, verse_s = current_verse.split(":")
                    chapter = int(chap_s)
                    verse = int(verse_s)
                    line_meta.append((idx, line, chapter, verse, "content"))
                except ValueError:
                    line_meta.append((idx, line, None, None, "skip"))
                    continue

        # Find content-line pairs where line N has 2p element + no speech boundary
        # AND line N+1 is vocative-dominant
        content_idx = [i for i, m in enumerate(line_meta) if m[4] == "content"]
        for j in range(len(content_idx) - 1):
            a_idx = content_idx[j]
            b_idx = content_idx[j + 1]
            # Lines must be adjacent (or only separated by blanks/verse-refs, not content)
            between = [line_meta[k][4] for k in range(a_idx + 1, b_idx)]
            if any(x == "content" for x in between):
                continue  # not adjacent in content sense

            _, a_line, a_chap, a_verse, _ = line_meta[a_idx]
            _, b_line, b_chap, b_verse, _ = line_meta[b_idx]

            # Speech-boundary filter on line A
            if line_ends_with_speech_boundary(a_line):
                continue

            # Check 2p on A, vocative on B
            if not line_has_2p_element(a_line, book_slug, a_chap, a_verse):
                continue
            if not line_is_vocative_dominant(b_line, book_slug, b_chap, b_verse):
                continue

            candidates.append({
                "book": book_slug,
                "chapter_file": chap_file.name,
                "line_a": a_idx + 1,
                "line_b": b_idx + 1,
                "ref_a": f"{a_chap}:{a_verse}",
                "ref_b": f"{b_chap}:{b_verse}",
                "text_a": a_line.strip(),
                "text_b": b_line.strip(),
            })

    return candidates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", help="single book slug (matt/mark/luke/...)")
    args = parser.parse_args()

    if args.book:
        # find dir
        dirs = [d for d in GRK_DIR.iterdir() if d.is_dir() and d.name.endswith(f"-{args.book}")]
        books = dirs
    else:
        books = sorted([d for d in GRK_DIR.iterdir() if d.is_dir()])

    all_cands = []
    for book_dir in books:
        cands = scan_book(book_dir)
        all_cands.extend(cands)

    if not all_cands:
        print("0 R18 Class 3 orphan-vocative candidates corpus-wide.")
        return 0

    print(f"{len(all_cands)} R18 Class 3 orphan-vocative candidates:\n")
    for c in all_cands:
        print(f"  {c['book']} {c['ref_a']} (lines {c['line_a']}–{c['line_b']} in {c['chapter_file']})")
        print(f"    A: {c['text_a']}")
        print(f"    B: {c['text_b']}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
