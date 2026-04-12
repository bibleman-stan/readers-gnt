#!/usr/bin/env python3
"""
scan_english_straddles.py

Detection-only audit. Walks every eng-gloss chapter file and flags pairs of
consecutive content lines (within the same verse) where the line break appears
to straddle a phrase. Typical cause: regenerate_english.py split by proportional
word count rather than by meaning, leaving a function word stranded at the end
of one line and its semantic completion at the start of the next.

Output: c:/Users/bibleman/repos/readers-gnt/private/english-straddle-audit.txt

This script does NOT modify any files.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

REPO = Path("c:/Users/bibleman/repos/readers-gnt")
ENG_DIR = REPO / "data" / "text-files" / "eng-gloss"
OUT_PATH = REPO / "private" / "english-straddle-audit.txt"

VERSE_RE = re.compile(r"^\s*(\d+):(\d+)\s*$")

# ---------------------------------------------------------------------------
# Trigger lists
# ---------------------------------------------------------------------------

HIGH_DANGLERS = {
    # articles & determiners
    "the", "a", "an",
    # prepositions
    "of", "in", "to", "from", "by", "with", "at", "on", "for",
    # universal quantifiers / determiners
    "every", "all", "each", "some", "no",
    # demonstratives
    "that", "this", "these", "those",
    # possessives
    "my", "your", "his", "her", "their", "our", "its",
}

MEDIUM_DANGLERS = {
    # auxiliaries / copulas
    "is", "was", "are", "were", "has", "had", "have",
    "will", "would", "may", "might", "can", "could", "shall", "should",
    "be", "been", "being", "do", "does", "did",
    # conjunctions
    "and", "but", "or", "nor", "yet", "so",
}

# Words that almost always start a real new clause / phrase, so even a dangling
# function word followed by them is suspicious-but-not-certain. We tone these
# down by NOT auto-flagging when line N+1 starts with one of these clause
# starters AFTER a medium dangler. (Articles/preps remain high-confidence.)
CLAUSE_STARTERS = {
    "for", "but", "and", "so", "therefore", "thus", "now", "then",
    "if", "when", "while", "because", "since", "as", "though", "although",
    "lest", "until", "before", "after", "that", "who", "which", "whom",
    "whose", "whoever", "whatever", "whenever", "where", "whither",
}

# Pronouns that, when they appear as the LAST word of line A, are usually the
# OBJECT of a preceding verb rather than a dangling possessive — provided
# line B begins with a clause starter (which is the typical "object pronoun
# at end of clause, then subordinate clause begins" shape).
OBJECT_PRONOUN_FORMS = {"her", "him", "them", "us", "me", "you", "it"}

# Common subordinating words that, when they start line B, signal that line A
# ended at a real clause boundary even if its last word looks like a function
# word.
HARD_CLAUSE_STARTERS = {
    "until", "lest", "because", "so", "if", "when", "while", "though",
    "although", "since", "before", "after", "unless", "whereas",
    "whenever", "wherever",
}

# A small set of "completion idioms" — when line N ends with KEY and line N+1
# starts with one of VALUES, flag with extra confidence.
COMPLETION_IDIOMS = {
    "every": {"kind", "one", "man", "woman", "person", "thing", "place",
              "time", "day", "way", "good", "evil", "tribe", "nation",
              "tongue", "name", "knee", "tongue", "spirit", "soul"},
    "all": {"things", "men", "people", "nations", "the"},
    "no": {"one", "man", "longer", "more", "means"},
    "the": set(),  # too broad to enumerate; handled by general rule
    "of": set(),
}

# Words that are likely the head of a noun phrase if they appear at start of
# line N+1 after a dangling article/prep on line N.
LIKELY_NP_HEADS_HINT = re.compile(
    r"^[A-Za-z][A-Za-z'\-]*$"  # any single word token (loose)
)

# Punctuation that, if present at the end of line N, almost always means the
# break is intentional and we should NOT flag it.
TERMINAL_PUNCT = set(".!?;:")
# A trailing comma is weaker — many real straddles end with a comma when the
# proportional splitter cut mid-phrase. We'll treat comma as "weakly terminal":
# we still flag it if the dangling-word test fires, but downgrade confidence
# one tier (high -> medium, medium -> low).

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def tokenize(line: str) -> List[str]:
    return WORD_RE.findall(line)


def last_word(line: str) -> str:
    toks = tokenize(line)
    return toks[-1].lower() if toks else ""


def first_word(line: str) -> str:
    toks = tokenize(line)
    return toks[0].lower() if toks else ""


def first_two_words(line: str) -> Tuple[str, str]:
    toks = tokenize(line)
    a = toks[0].lower() if toks else ""
    b = toks[1].lower() if len(toks) > 1 else ""
    return a, b


def stripped_terminal_char(line: str) -> str:
    """Return the last non-space character of the line, or '' if empty."""
    s = line.rstrip()
    return s[-1] if s else ""


# ---------------------------------------------------------------------------
# Verse parsing
# ---------------------------------------------------------------------------

def parse_chapter(path: Path):
    """
    Yield (chapter, verse, [content_lines]) tuples.
    A 'content line' is the raw text line (preserving spacing within the line)
    after a verse marker, until the next blank line or verse marker.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  WARN: could not read {path.name}: {e}")
        return

    lines = text.split("\n")
    cur_ch = None
    cur_vs = None
    bucket: List[str] = []

    def flush():
        nonlocal bucket
        if cur_ch is not None and cur_vs is not None and bucket:
            yield_buf.append((cur_ch, cur_vs, bucket))
        bucket = []

    yield_buf: List[Tuple[int, int, List[str]]] = []

    for raw in lines:
        m = VERSE_RE.match(raw)
        if m:
            # flush previous verse
            if cur_ch is not None and cur_vs is not None and bucket:
                yield_buf.append((cur_ch, cur_vs, bucket))
                bucket = []
            cur_ch = int(m.group(1))
            cur_vs = int(m.group(2))
            continue
        if raw.strip() == "":
            if cur_ch is not None and cur_vs is not None and bucket:
                yield_buf.append((cur_ch, cur_vs, bucket))
                bucket = []
            continue
        bucket.append(raw)

    if cur_ch is not None and cur_vs is not None and bucket:
        yield_buf.append((cur_ch, cur_vs, bucket))

    return yield_buf


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def classify_pair(line_a: str, line_b: str) -> Tuple[str, str] | None:
    """
    Return (confidence, issue_label) if pair is flagged, else None.
    confidence in {"HIGH", "MEDIUM", "LOW"}.
    """
    last = last_word(line_a)
    if not last:
        return None

    fw = first_word(line_b)
    fw1, fw2 = first_two_words(line_b)
    if not fw:
        return None

    term = stripped_terminal_char(line_a)

    # Hard stop: if line A ends with terminal punctuation, the break is real.
    if term in TERMINAL_PUNCT:
        return None

    # Strong "completion idiom" hits — flag at HIGH regardless of comma.
    if last in COMPLETION_IDIOMS:
        targets = COMPLETION_IDIOMS[last]
        if targets and fw in targets:
            return ("HIGH", f"idiom split: '{last} {fw}...'")

    is_high = last in HIGH_DANGLERS
    is_med = last in MEDIUM_DANGLERS

    if not (is_high or is_med):
        return None

    # Special-case: medium danglers followed by a clause starter are usually
    # legitimate (e.g. "...is // for he..." — both clause boundaries). Skip.
    if is_med and fw in CLAUSE_STARTERS:
        return None

    # Special-case: object pronouns ("her", "him", "them", ...) at end of
    # line A are usually the object of a verb earlier in line A. They only
    # look like a dangling possessive when line B begins with a noun phrase.
    # If line B begins with a hard clause starter or an obvious verb-y word,
    # treat the pronoun as an object and skip.
    if last in OBJECT_PRONOUN_FORMS and fw in HARD_CLAUSE_STARTERS:
        return None

    # Special-case: "for" / "but" / "and" / "so" / "or" at end of line A are
    # ambiguous between preposition/conjunction and discourse marker. If
    # line B starts with a finite-clause shape (subject pronoun + verb, or a
    # clause starter), treat the dangler as a real conjunction and skip.
    if last in {"for", "but", "and", "so", "or", "yet"}:
        # Subject-pronoun-led clause => discourse-marker reading
        if fw in {"he", "she", "they", "we", "i", "you", "it",
                   "there", "this", "that", "these", "those"}:
            return None
        if fw in HARD_CLAUSE_STARTERS:
            return None

    # Special-case: a "to" at end of line A followed by a hard clause starter
    # is rare but possible — treat as legit.
    if last == "to" and fw in HARD_CLAUSE_STARTERS:
        return None

    # Special-case: "to" at end of line followed by a verb is "to <verb>"
    # infinitive, definitely a straddle.
    # We can't POS-tag, but we can boost confidence on common short verbs.
    # Just keep "to" as HIGH dangler — already covered.

    # Determine confidence
    if is_high:
        conf = "HIGH"
    else:
        conf = "MEDIUM"

    # Comma at end of line A weakens the signal one tier.
    if term == ",":
        if conf == "HIGH":
            conf = "MEDIUM"
        else:
            conf = "LOW"

    # Build issue label
    if last in {"the", "a", "an"}:
        label = f"dangling article '{last}'"
    elif last in {"of", "in", "to", "from", "by", "with", "at", "on", "for"}:
        label = f"dangling preposition '{last}'"
    elif last in {"every", "all", "each", "some", "no"}:
        label = f"dangling quantifier '{last}'"
    elif last in {"that", "this", "these", "those"}:
        label = f"dangling demonstrative '{last}'"
    elif last in {"my", "your", "his", "her", "their", "our", "its"}:
        label = f"dangling possessive '{last}'"
    elif last in {"and", "but", "or", "nor", "yet", "so"}:
        label = f"dangling conjunction '{last}'"
    else:
        label = f"dangling auxiliary '{last}'"

    return (conf, label)


# ---------------------------------------------------------------------------
# Main scan
# ---------------------------------------------------------------------------

def scan() -> List[dict]:
    findings: List[dict] = []

    book_dirs = sorted(p for p in ENG_DIR.iterdir() if p.is_dir())
    for book_dir in book_dirs:
        chapter_files = sorted(book_dir.glob("*.txt"))
        for ch_file in chapter_files:
            verses = parse_chapter(ch_file)
            if not verses:
                continue
            for ch, vs, content in verses:
                if len(content) < 2:
                    continue
                for i in range(len(content) - 1):
                    a = content[i]
                    b = content[i + 1]
                    result = classify_pair(a, b)
                    if result is None:
                        continue
                    conf, label = result
                    findings.append({
                        "file": ch_file.name,
                        "book_dir": book_dir.name,
                        "ch": ch,
                        "vs": vs,
                        "line_a": a.strip(),
                        "line_b": b.strip(),
                        "confidence": conf,
                        "issue": label,
                    })
    return findings


def render(findings: List[dict]) -> str:
    out: List[str] = []
    out.append("=== ENGLISH LINE-STRADDLE AUDIT ===")
    out.append("")
    out.append(f"Total candidates: {len(findings)}")
    out.append("")
    out.append("Detection-only. No files modified.")
    out.append("Source: data/text-files/eng-gloss/**/*.txt")
    out.append("")

    by_conf = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for f in findings:
        by_conf[f["confidence"]].append(f)

    for conf in ("HIGH", "MEDIUM", "LOW"):
        bucket = by_conf[conf]
        if conf == "HIGH":
            header = f"HIGH CONFIDENCE (likely bugs) — {len(bucket)}"
        elif conf == "MEDIUM":
            header = f"MEDIUM CONFIDENCE — {len(bucket)}"
        else:
            header = f"LOW CONFIDENCE — {len(bucket)}"
        out.append("")
        out.append("=" * len(header))
        out.append(header)
        out.append("=" * len(header))
        out.append("")

        for f in bucket:
            out.append(f"{f['book_dir']}/{f['file']} {f['ch']}:{f['vs']}")
            out.append(f"  Line A: {f['line_a']}")
            out.append(f"  Line B: {f['line_b']}")
            out.append(f"  issue: {f['issue']}")
            out.append("")

    return "\n".join(out)


def main() -> int:
    if not ENG_DIR.exists():
        print(f"ERROR: {ENG_DIR} does not exist")
        return 2

    print(f"Scanning {ENG_DIR} ...")
    findings = scan()
    print(f"  found {len(findings)} candidates")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = render(findings)
    OUT_PATH.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT_PATH}")

    # Per-confidence summary to stdout
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        counts[f["confidence"]] += 1
    print(f"  HIGH:   {counts['HIGH']}")
    print(f"  MEDIUM: {counts['MEDIUM']}")
    print(f"  LOW:    {counts['LOW']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
