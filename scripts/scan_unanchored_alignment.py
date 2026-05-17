"""scan_unanchored_alignment.py — diagnostic scan for unanchored English alignment.

Per directive 2026-05-16-2300-unanchored-alignment-scan.md. Bounds the
"supplement-attachment" problem surfaced by the Mark 4:6 case (KJV pronoun
"it" stranded on the temporal-clause line when its grammatical subject-of-
verb anchor is on the next line).

NO FIXES. NO v4 EDITS. Diagnostic only.

Approach
--------
For each v4 verse:
  1. Load TAGNT tokens (existing regenerate_english.py infrastructure).
  2. Build source_atu_lines_with_tokens and call align_verse → per-line strings.
  3. Load KjvIndex separately → identify which KJV words are anchored
     (have Strong's) vs unanchored (no Strong's, "translator supplied").
  4. Map each KJV word to the v4/eng-kjv line it landed on (by walking
     output lines in KJV-vpos order, since align_verse preserves order).
  5. For each UNANCHORED token: classify POS via closed list (pronoun /
     auxiliary / article / conjunction / particle / other).
  6. Parse the verse with spaCy en_core_web_sm. Find each unanchored
     token's UD head. Determine the head's line. Compare:
        - OK: head on same line as token
        - MIS-ATTACHED: head on different line
        - AMBIGUOUS: token is root, or head not findable in token map
  7. Record per-category counts + representative samples.

Output
------
Per-category counts table (OK / MIS / AMBIG).
Top mis-attachment shapes.
Representative MIS samples (5-10 per category).
Markdown report to stdout or --output path.

Usage
-----
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_unanchored_alignment.py
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_unanchored_alignment.py --book mark
  PYTHONIOENCODING=utf-8 py -3 scripts/scan_unanchored_alignment.py --output report.md
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
ATU_METHOD = REPO_ROOT.parent / "atu-method"
sys.path.insert(0, str(ATU_METHOD))
sys.path.insert(0, str(REPO_ROOT))

from atu_method.kjv_alignment import (  # noqa: E402
    SourceToken,
    align_verse,
    extract_strongs_from_tagnt_col,
    load_kjv_strongs_index,
)
from atu_method.kjv_alignment.metav_loader import book_id_for_osis  # noqa: E402

# Reuse regenerate_english's TAGNT loader + v4 parser
from scripts.regenerate_english import (  # noqa: E402
    BOOK_META,
    BOOK_BY_SLUG,
    load_tagnt_book,
    parse_v4_file,
    normalise_greek,
    V4_EDITORIAL,
    METAV_DIR,
)

# ---------------------------------------------------------------------------
# POS / function classification (closed lists per directive item 2)
# ---------------------------------------------------------------------------

PRONOUNS = {
    "i", "me", "my", "mine", "myself",
    "we", "us", "our", "ours", "ourselves",
    "you", "your", "yours", "yourself", "yourselves",
    "thou", "thee", "thy", "thine", "thyself",
    "ye",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",
    "who", "whom", "whose", "which", "what",
}

AUXILIARIES = {
    "am", "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "having",
    "do", "does", "did", "doing", "done",
    "shall", "should", "will", "would",
    "may", "might", "must", "can", "could",
    "ought",
}

ARTICLES = {"the", "a", "an"}

CONJUNCTIONS = {
    "and", "but", "or", "nor", "for", "so", "yet",
    "if", "though", "although", "while", "when", "as", "because",
    "since", "unless", "until", "till", "whether",
}

PARTICLES = {"behold", "lo", "verily", "truly", "now", "then"}

PREPOSITIONS = {
    "of", "in", "on", "at", "to", "from", "with", "by", "for",
    "into", "unto", "upon", "before", "after", "above", "below",
    "between", "among", "through", "against", "without", "within",
    "about", "under", "over", "out", "off", "up", "down",
}


def classify_pos(token: str) -> str:
    """Closed-list POS classification for an unanchored English token."""
    norm = token.lower().strip(".,;:!?\"'()[]")
    if norm in PRONOUNS:
        return "pronoun"
    if norm in AUXILIARIES:
        return "auxiliary"
    if norm in ARTICLES:
        return "article"
    if norm in CONJUNCTIONS:
        return "conjunction"
    if norm in PARTICLES:
        return "particle"
    if norm in PREPOSITIONS:
        return "preposition"
    return "other"


# ---------------------------------------------------------------------------
# Per-verse alignment introspection
# ---------------------------------------------------------------------------


@dataclass
class UnanchoredToken:
    """An unanchored KJV English token in a v4 verse."""

    book_slug: str
    chapter: int
    verse: int
    line_idx: int           # which v4 line the token landed on
    word_idx_in_line: int   # position within the line
    surface: str            # KJV surface form (no punctuation stripping)
    pos_category: str       # closed-list category
    head_line_idx: Optional[int] = None   # filled in by UD attachment phase
    head_surface: Optional[str] = None
    attachment_verdict: str = "PENDING"   # OK / MIS_ATTACHED / AMBIGUOUS


def build_source_lines(
    grk_lines: list[str],
    tagnt_tokens: list[tuple[str, str, str, str]],
) -> list[list[SourceToken]]:
    """Convert v4 grk lines + TAGNT tokens to SourceToken lines.

    Walks v4 grk tokens in textual order; for each, finds the matching
    TAGNT row by surface match (with NFC + casefold). Returns one list
    of SourceTokens per v4 line.
    """
    # Flatten v4 grk tokens with line indices
    v4_words: list[tuple[int, str]] = []  # (line_idx, raw_word)
    for line_idx, line in enumerate(grk_lines):
        for w in line.split():
            v4_words.append((line_idx, w))

    # Walk TAGNT tokens in order; surface-match against v4 words
    result: list[list[SourceToken]] = [[] for _ in grk_lines]
    tagnt_ptr = 0
    for line_idx, raw_word in v4_words:
        norm_v4 = normalise_greek(raw_word)
        if not norm_v4:
            continue
        # Find next TAGNT row whose surface matches (window=5 lookahead)
        matched = None
        for k in range(tagnt_ptr, min(tagnt_ptr + 5, len(tagnt_tokens))):
            t_surface, _, _, _ = tagnt_tokens[k]
            if normalise_greek(t_surface) == norm_v4:
                matched = k
                break
        if matched is None:
            # Add a no-Strong's source token (preserves word count)
            result[line_idx].append(SourceToken(text=raw_word, strongs_list=()))
            continue
        # Move pointer past matched (allow gaps)
        _, col3, col11, col12 = tagnt_tokens[matched]
        strongs = tuple(extract_strongs_from_tagnt_col(col3, col11, col12))
        result[line_idx].append(SourceToken(text=raw_word, strongs_list=strongs))
        tagnt_ptr = matched + 1
    return result


def identify_unanchored(
    book_osis: str,
    chapter: int,
    verse: int,
    source_lines: list[list[SourceToken]],
    kjv_index,
    book_slug: str,
) -> list[UnanchoredToken]:
    """For one verse: align, then identify unanchored output tokens.

    Returns list of UnanchoredToken with line + word-in-line position
    populated. Head/verdict fields left to UD pass.
    """
    try:
        per_line_strings = align_verse(book_osis, chapter, verse, source_lines, METAV_DIR)
    except KeyError:
        return []  # verse not in MetaV
    except Exception:
        return []

    # Lookup KJV-side data for this verse
    book_id = book_id_for_osis(book_osis)
    key = (book_id, chapter, verse)
    kjv_words = kjv_index.get(key)
    if not kjv_words:
        return []
    kjv_sorted = sorted(kjv_words, key=lambda w: w.vpos)

    # Walk per_line_strings → flat token list with (line_idx, word_idx_in_line)
    flat_output: list[tuple[int, int, str]] = []
    for line_idx, line_str in enumerate(per_line_strings):
        if not line_str.strip():
            continue
        for word_idx, w in enumerate(line_str.split()):
            flat_output.append((line_idx, word_idx, w))

    # The flat_output tokens correspond positionally to kjv_sorted IF the
    # word counts agree. align_verse preserves KJV-vpos order within each
    # line and emits lines in order, so position-N in flat_output = the
    # N-th KJV word in vpos order.
    if len(flat_output) != len(kjv_sorted):
        # Count mismatch — defensive skip. Diagnostic only; we don't fix.
        return []

    unanchored: list[UnanchoredToken] = []
    for i, (line_idx, word_idx, surface) in enumerate(flat_output):
        kjv_word = kjv_sorted[i]
        if not kjv_word.strongs_list:
            # No Strong's anchor → translator-supplied / unanchored
            unanchored.append(
                UnanchoredToken(
                    book_slug=book_slug,
                    chapter=chapter,
                    verse=verse,
                    line_idx=line_idx,
                    word_idx_in_line=word_idx,
                    surface=surface,
                    pos_category=classify_pos(surface),
                )
            )
    return unanchored


# ---------------------------------------------------------------------------
# UD attachment classification (spaCy en_core_web_sm)
# ---------------------------------------------------------------------------


def classify_attachments(
    verse_unanchored: list[UnanchoredToken],
    per_line_strings: list[str],
    nlp,
) -> None:
    """For each unanchored token, run spaCy on the verse and determine
    the line index of the UD head. Mutates token.attachment_verdict +
    token.head_line_idx + token.head_surface.

    Strategy: parse the concatenated verse. Build a mapping from
    spaCy-token-index to (line_idx, word_idx_in_line) by walking spaCy
    tokens in parallel with the flat KJV output and matching surfaces.
    """
    if not verse_unanchored:
        return
    # Concatenate lines with single spaces (preserves word-order across lines).
    flat_output: list[tuple[int, int, str]] = []
    for line_idx, line_str in enumerate(per_line_strings):
        if not line_str.strip():
            continue
        for word_idx, w in enumerate(line_str.split()):
            flat_output.append((line_idx, word_idx, w))
    verse_text = " ".join(w for _, _, w in flat_output)
    doc = nlp(verse_text)

    # Map spaCy tokens to (line_idx, word_idx). Walk in parallel; spaCy
    # may produce extra tokens for punctuation. We match surface forms.
    spacy_to_line: dict[int, tuple[int, int]] = {}
    kjv_ptr = 0
    for spacy_idx, spacy_tok in enumerate(doc):
        if kjv_ptr >= len(flat_output):
            break
        line_idx, word_idx, kjv_surface = flat_output[kjv_ptr]
        # Strip kjv trailing punc
        kjv_norm = kjv_surface.strip(".,;:!?\"'()[]").lower()
        sp_norm = spacy_tok.text.strip(".,;:!?\"'()[]").lower()
        if sp_norm == kjv_norm and sp_norm:
            spacy_to_line[spacy_idx] = (line_idx, word_idx)
            kjv_ptr += 1
        elif sp_norm.startswith(kjv_norm) and kjv_norm:
            # Defensive: prefix match (rare)
            spacy_to_line[spacy_idx] = (line_idx, word_idx)
            kjv_ptr += 1
        # else spaCy emitted punctuation; skip without advancing kjv_ptr

    # For each unanchored token, find its spaCy index by matching position.
    for unanchored in verse_unanchored:
        target = (unanchored.line_idx, unanchored.word_idx_in_line)
        spacy_idx = None
        for sidx, line_pos in spacy_to_line.items():
            if line_pos == target:
                spacy_idx = sidx
                break
        if spacy_idx is None:
            unanchored.attachment_verdict = "AMBIGUOUS"
            continue
        spacy_tok = doc[spacy_idx]
        head = spacy_tok.head
        if head.i == spacy_tok.i:
            # Token is the parse root
            unanchored.attachment_verdict = "AMBIGUOUS"
            continue
        head_line_pos = spacy_to_line.get(head.i)
        if head_line_pos is None:
            unanchored.attachment_verdict = "AMBIGUOUS"
            continue
        head_line, _ = head_line_pos
        unanchored.head_line_idx = head_line
        unanchored.head_surface = head.text
        if head_line == unanchored.line_idx:
            unanchored.attachment_verdict = "OK"
        else:
            unanchored.attachment_verdict = "MIS_ATTACHED"


# ---------------------------------------------------------------------------
# Top-shape detection
# ---------------------------------------------------------------------------


def shape_of(tok: UnanchoredToken) -> str:
    """One of: SUBJECT_PRONOUN_BEFORE_VERB, AUX_AFTER_SUBJECT,
    CONJUNCTION_TRAILING, OTHER_FORWARD_MIS, OTHER_BACKWARD_MIS.

    Distinguishes the most-common mis-attachment shapes per directive item 5.
    """
    if tok.attachment_verdict != "MIS_ATTACHED":
        return "N/A"
    forward = tok.head_line_idx is not None and tok.head_line_idx > tok.line_idx
    if tok.pos_category == "pronoun" and forward:
        return "PRONOUN_STRANDED_BEFORE_VERB"
    if tok.pos_category == "auxiliary" and forward:
        return "AUX_STRANDED_AFTER_SUBJECT"
    if tok.pos_category == "conjunction":
        return "CONJUNCTION_STRANDED_AT_PRIOR_CLAUSE"
    if forward:
        return "OTHER_FORWARD_MIS"
    return "OTHER_BACKWARD_MIS"


# ---------------------------------------------------------------------------
# Main scan loop
# ---------------------------------------------------------------------------


def scan_book(
    book_meta: tuple[str, str, str, Path],
    kjv_index,
    nlp,
) -> tuple[list[UnanchoredToken], int]:
    """Scan one book. Returns (all_unanchored_tokens, verse_count_processed)."""
    dir_name, slug, tagnt_prefix, tagnt_path = book_meta
    book_dir = V4_EDITORIAL / dir_name
    if not book_dir.exists():
        return [], 0
    tagnt_verses = load_tagnt_book(tagnt_path, tagnt_prefix)

    all_unanchored: list[UnanchoredToken] = []
    verse_count = 0
    for ch_file in sorted(book_dir.glob("*.txt")):
        # Parse chapter number from filename: e.g. matt-01.txt -> 1
        m = re.search(r"-(\d+)\.txt$", ch_file.name)
        if not m:
            continue
        chapter = int(m.group(1))
        verses = parse_v4_file(ch_file)
        for verse_ref, grk_lines in verses:
            try:
                _ch_str, vs_str = verse_ref.split(":")
                verse = int(vs_str)
            except ValueError:
                continue
            verse_count += 1
            tagnt_ref = f"{tagnt_prefix}.{chapter}.{verse}"
            tagnt_tokens = tagnt_verses.get(tagnt_ref, [])
            if not tagnt_tokens or not grk_lines:
                continue
            source_lines = build_source_lines(grk_lines, tagnt_tokens)
            try:
                per_line_strings = align_verse(
                    tagnt_prefix, chapter, verse, source_lines, METAV_DIR
                )
            except (KeyError, Exception):
                continue
            verse_unanchored = identify_unanchored(
                tagnt_prefix, chapter, verse, source_lines, kjv_index, slug
            )
            if not verse_unanchored:
                continue
            classify_attachments(verse_unanchored, per_line_strings, nlp)
            all_unanchored.extend(verse_unanchored)
    return all_unanchored, verse_count


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


CATEGORIES = ["pronoun", "auxiliary", "article", "conjunction", "particle", "preposition", "other"]
VERDICTS = ["OK", "MIS_ATTACHED", "AMBIGUOUS"]


def format_report(tokens: list[UnanchoredToken], verse_count: int) -> str:
    out: list[str] = []
    out.append("# Unanchored English-Alignment Diagnostic Scan — GNT")
    out.append("")
    out.append(
        f"Per directive 2026-05-16-2300-unanchored-alignment-scan. "
        f"Scanned {verse_count} verses across {len({t.book_slug for t in tokens})} "
        f"books with unanchored tokens."
    )
    out.append("")

    # Per-category × verdict counts
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for t in tokens:
        counts[(t.pos_category, t.attachment_verdict)] += 1

    out.append("## Per-category counts")
    out.append("")
    out.append("| Category | Total | OK | MIS_ATTACHED | AMBIGUOUS |")
    out.append("|---|---:|---:|---:|---:|")
    for cat in CATEGORIES:
        total = sum(counts[(cat, v)] for v in VERDICTS)
        if total == 0:
            continue
        ok = counts[(cat, "OK")]
        mis = counts[(cat, "MIS_ATTACHED")]
        amb = counts[(cat, "AMBIGUOUS")]
        out.append(f"| **{cat}** | {total} | {ok} | {mis} | {amb} |")
    total_all = len(tokens)
    ok_all = sum(counts[(c, "OK")] for c in CATEGORIES)
    mis_all = sum(counts[(c, "MIS_ATTACHED")] for c in CATEGORIES)
    amb_all = sum(counts[(c, "AMBIGUOUS")] for c in CATEGORIES)
    out.append(f"| **TOTAL** | {total_all} | {ok_all} | {mis_all} | {amb_all} |")
    out.append("")

    # Top mis-attachment shapes
    shape_counts: dict[str, int] = defaultdict(int)
    for t in tokens:
        if t.attachment_verdict == "MIS_ATTACHED":
            shape_counts[shape_of(t)] += 1
    out.append("## Top mis-attachment shapes")
    out.append("")
    out.append("| Shape | Count |")
    out.append("|---|---:|")
    for shape, count in sorted(shape_counts.items(), key=lambda kv: -kv[1]):
        out.append(f"| {shape} | {count} |")
    out.append("")

    # Representative samples per category (MIS_ATTACHED only, up to 10 each)
    out.append("## Representative MIS-ATTACHED samples")
    out.append("")
    by_cat: dict[str, list[UnanchoredToken]] = defaultdict(list)
    for t in tokens:
        if t.attachment_verdict == "MIS_ATTACHED":
            by_cat[t.pos_category].append(t)
    for cat in CATEGORIES:
        samples = by_cat[cat][:10]
        if not samples:
            continue
        out.append(f"### {cat}")
        out.append("")
        for t in samples:
            direction = "→ later line" if (t.head_line_idx or 0) > t.line_idx else "← earlier line"
            out.append(
                f"- **{t.book_slug} {t.chapter}:{t.verse}** "
                f"line {t.line_idx} → line {t.head_line_idx} ({direction}) "
                f"token `{t.surface}` → head `{t.head_surface}`"
            )
        out.append("")

    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--book", help="Restrict to one book slug (e.g. mark)")
    parser.add_argument("--output", help="Write report to this path; otherwise stdout")
    args = parser.parse_args()

    # Lazy imports for heavy deps
    print("[scan] loading KjvIndex...", file=sys.stderr)
    kjv_index = load_kjv_strongs_index(METAV_DIR)
    print(f"[scan] KjvIndex: {len(kjv_index)} verses", file=sys.stderr)

    print("[scan] loading spaCy en_core_web_sm...", file=sys.stderr)
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    print("[scan] spaCy loaded", file=sys.stderr)

    if args.book:
        if args.book not in BOOK_BY_SLUG:
            print(f"Unknown book: {args.book}", file=sys.stderr)
            return 2
        books = [BOOK_BY_SLUG[args.book]]
    else:
        books = BOOK_META

    all_tokens: list[UnanchoredToken] = []
    total_verses = 0
    for book_meta in books:
        slug = book_meta[1]
        print(f"[scan] processing {slug}...", file=sys.stderr)
        tokens, verses = scan_book(book_meta, kjv_index, nlp)
        all_tokens.extend(tokens)
        total_verses += verses
        print(
            f"[scan]   {slug}: {verses} verses, "
            f"{len(tokens)} unanchored tokens",
            file=sys.stderr,
        )

    report = format_report(all_tokens, total_verses)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"[scan] report written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
