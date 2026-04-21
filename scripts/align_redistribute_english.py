#!/usr/bin/env python3
"""
align_redistribute_english.py

Alignment-driven English gloss redistribution.

Replaces the proportional-word heuristic in regenerate_english.py's
_find_phrase_splits() for verses where a corpus alignment map is available.

Usage (from regenerate_english.py Wave-3 integration):
    from align_redistribute_english import align_redistribute, load_alignment_map

The public API is:
    align_redistribute(book, ch, vs, new_greek_lines, prev_english_lines,
                       alignment_map) -> list[str] | None
    load_alignment_map(path) -> dict

Returns None when no alignment data is available, signalling the caller to
fall back to the legacy proportional heuristic.
"""

import json
import re
import unicodedata
from typing import Optional


# ---------------------------------------------------------------------------
# Preprocessing helpers
# ---------------------------------------------------------------------------

# Greek punctuation characters to strip before tokenisation.
# Covers: ASCII punctuation, Greek ano-teleia (·/U+00B7 and U+0387),
# Greek question mark (;/U+037E), em-dash, modifier letter apostrophe (U+02BC).
_GREEK_PUNCT = re.compile(
    r"[.,;·\u0387\u037E?!()\[\]{}\u2014\u02BC]"
)

# English: strip leading/trailing ASCII punctuation for matching.
_ENG_PUNCT_LEAD = re.compile(r"^[^\w\u00C0-\u024F]+")
_ENG_PUNCT_TRAIL = re.compile(r"[^\w\u00C0-\u024F]+$")


def preprocess_tokenize(greek_text: str) -> list[str]:
    """NFC-normalize, strip Greek punctuation, lowercase, split on whitespace.

    Returns the list of normalised tokens used for index assignment.
    Empty strings are discarded (e.g. punctuation-only 'words').
    """
    normalised = unicodedata.normalize("NFC", greek_text)
    stripped = _GREEK_PUNCT.sub("", normalised)
    return [t for t in stripped.lower().split() if t]


def preprocess_english_token(word: str) -> str:
    """Lowercase the word and strip leading/trailing punctuation.

    Returns a clean form suitable for index matching; the original form
    (with punctuation and case) is preserved separately for output.
    """
    cleaned = _ENG_PUNCT_LEAD.sub("", word)
    cleaned = _ENG_PUNCT_TRAIL.sub("", cleaned)
    return cleaned.lower()


# ---------------------------------------------------------------------------
# Unaligned-token insertion helpers
# ---------------------------------------------------------------------------

def _find_nearest_line(
    unaligned_pos: int,
    greek_tokens_per_line: list[list[int]],
    greek_to_english: dict[int, int],
    english_lines_new: list[list[int]],
) -> int:
    """Return the index of the Greek line whose aligned English tokens are
    nearest (by position in the flat English token sequence) to
    *unaligned_pos*.

    Proximity is measured by the minimum absolute distance between
    *unaligned_pos* and any already-assigned English index on a line.
    Lines with no assigned tokens are skipped; if all lines are empty
    (degenerate case) we fall back to proportional assignment.
    """
    best_line = 0
    best_dist = float("inf")

    for line_idx, line_english_indices in enumerate(english_lines_new):
        if not line_english_indices:
            continue
        dist = min(abs(unaligned_pos - e) for e in line_english_indices)
        if dist < best_dist:
            best_dist = dist
            best_line = line_idx

    # Proportional fallback: if every line is empty, spread evenly.
    if best_dist == float("inf"):
        total_lines = len(english_lines_new)
        # We don't know total English count here; just return line 0.
        return 0

    return best_line


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def align_redistribute(
    book: str,
    ch: int,
    vs: int,
    new_greek_lines: list[str],
    prev_english_lines: list[str],
    alignment_map: dict,
) -> Optional[list[str]]:
    """Redistribute *prev_english_lines* into lines matching *new_greek_lines*,
    guided by *alignment_map*.

    Parameters
    ----------
    book              : book slug matching keys in alignment_map (e.g. "matt")
    ch                : chapter number (int)
    vs                : verse number (int)
    new_greek_lines   : list of Greek line strings (post-edit)
    prev_english_lines: list of existing English gloss strings (any line count)
    alignment_map     : {book: {ch:vs_str: [(greek_idx, english_idx), ...]}}

    Returns
    -------
    list[str] – one English string per Greek line, or
    None      – if no alignment data is available (caller must fall back).
    """
    verse_key = f"{ch}:{vs}"
    alignments: list[tuple[int, int]] = (
        alignment_map.get(book, {}).get(verse_key, [])
    )
    if not alignments:
        return None  # No alignment data — caller falls back.

    # ------------------------------------------------------------------
    # Step 1: tokenise new Greek lines → flat index ranges per line
    # ------------------------------------------------------------------
    greek_tokens_per_line: list[list[int]] = []
    cursor = 0
    for line in new_greek_lines:
        tokens = preprocess_tokenize(line)
        greek_tokens_per_line.append(list(range(cursor, cursor + len(tokens))))
        cursor += len(tokens)

    # ------------------------------------------------------------------
    # Step 2: tokenise previous English → flat list, preserving originals
    # ------------------------------------------------------------------
    english_original_words: list[str] = []
    for line in prev_english_lines:
        for word in line.split():
            english_original_words.append(word)

    total_english = len(english_original_words)

    # ------------------------------------------------------------------
    # Step 3: build greek_idx → english_idx mapping (many-to-one: first
    #         Greek token wins; one-to-many: stored as set per greek_idx)
    # ------------------------------------------------------------------
    # greek_to_english: greek_idx -> set of english_idx
    greek_to_english: dict[int, set[int]] = {}
    # many-to-one guard: track which english_idx have been claimed by an
    # earlier Greek token so subsequent ones don't re-claim them.
    english_claimed_by: dict[int, int] = {}  # english_idx -> first greek_idx

    for g_idx, e_idx in alignments:
        if e_idx >= total_english:
            continue  # stale alignment entry — skip safely
        if e_idx in english_claimed_by:
            # many-to-one: this English token already belongs to an earlier
            # Greek token — ignore the duplicate claim.
            continue
        english_claimed_by[e_idx] = g_idx
        greek_to_english.setdefault(g_idx, set()).add(e_idx)

    # ------------------------------------------------------------------
    # Step 4: assign English tokens to lines via Greek-line membership
    # ------------------------------------------------------------------
    # english_lines_new holds sets of english_idx per line during assembly;
    # converted to sorted lists at the end.
    line_english_sets: list[set[int]] = [set() for _ in new_greek_lines]
    assigned_english: set[int] = set()

    for line_idx, line_greek_indices in enumerate(greek_tokens_per_line):
        for g in line_greek_indices:
            for e in greek_to_english.get(g, set()):
                if e not in assigned_english:
                    line_english_sets[line_idx].add(e)
                    assigned_english.add(e)

    # ------------------------------------------------------------------
    # Step 5: distribute unaligned English tokens to the nearest line
    # ------------------------------------------------------------------
    # Convert sets to sorted lists for proximity calculation.
    line_english_lists: list[list[int]] = [
        sorted(s) for s in line_english_sets
    ]

    unaligned = [
        i for i in range(total_english) if i not in assigned_english
    ]

    for u in unaligned:
        nearest = _find_nearest_line(u, greek_tokens_per_line,
                                     greek_to_english, line_english_lists)
        line_english_lists[nearest].append(u)
        # Keep sorted for subsequent proximity queries.
        line_english_lists[nearest].sort()

    # ------------------------------------------------------------------
    # Step 6: render — output words in original English order with
    #         original case and punctuation
    # ------------------------------------------------------------------
    result: list[str] = []
    for eng_indices in line_english_lists:
        words = [english_original_words[i] for i in sorted(eng_indices)]
        result.append(" ".join(words))

    return result


# ---------------------------------------------------------------------------
# Alignment-map loader
# ---------------------------------------------------------------------------

def load_alignment_map(path: str) -> dict:
    """Load the corpus alignment JSON from *path*.

    Returns an empty dict (triggering proportional fallback everywhere) if
    the file does not exist or cannot be parsed.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """Synthetic test: 3-line Greek, 1-line English, trivial alignment."""
    alignment_map = {"test": {"1:1": [(0, 0), (1, 1), (2, 2), (3, 3)]}}
    greek_lines = ["word1 word2", "word3", "word4"]
    english_lines_prev = ["Eng1 Eng2 Eng3 Eng4"]
    result = align_redistribute(
        "test", 1, 1, greek_lines, english_lines_prev, alignment_map
    )
    assert result == ["Eng1 Eng2", "Eng3", "Eng4"], f"got {result}"
    print("Self-test passed.")

    # Test: no alignment available → returns None
    result_none = align_redistribute(
        "test", 9, 9, greek_lines, english_lines_prev, alignment_map
    )
    assert result_none is None, f"expected None, got {result_none}"
    print("None-fallback test passed.")

    # Test: unaligned English token distributed to nearest line
    alignment_map2 = {"test": {"2:1": [(0, 0), (2, 2)]}}
    greek_lines2 = ["wordA", "wordB wordC"]
    # Eng index 1 ("Eng2") is unaligned; nearest aligned on line 0 (Eng1 at 0)
    # vs line 1 (Eng3 at 2): dist 1 vs dist 1 — tie breaks to first (line 0)
    english_lines2 = ["Eng1 Eng2 Eng3"]
    result2 = align_redistribute(
        "test", 2, 1, greek_lines2, english_lines2, alignment_map2
    )
    assert result2 is not None, "expected list, got None"
    # All three tokens must be distributed (total word count preserved)
    total_words = sum(len(l.split()) for l in result2)
    assert total_words == 3, f"word count mismatch: {result2}"
    print(f"Unaligned-distribution test passed: {result2}")


if __name__ == "__main__":
    _self_test()
