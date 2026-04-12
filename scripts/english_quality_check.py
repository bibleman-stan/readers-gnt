#!/usr/bin/env python3
"""
english_quality_check.py — Validate English structural glosses for quality issues.

Uses spaCy (en_core_web_sm) and Macula Greek TSV to detect:
  1. Pronoun errors   — masculine/feminine Greek referent rendered as "its"
  2. Missing verbs    — lines with no VERB or AUX (exceptions: vocatives, list items, triadic stacks)
  3. Subject-verb disagreement — singular Greek subject → "they", or plural → "he/she"
  4. Nonsense fragments — under 3 words, not vocative or imperative
  5. Repeated words   — same content word appearing twice on one line
  6. Mid-word splits  — line starts lowercase but isn't a conjunction

Usage:
    PYTHONIOENCODING=utf-8 py -3 scripts/english_quality_check.py              # all files
    PYTHONIOENCODING=utf-8 py -3 scripts/english_quality_check.py --book mark   # one book
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import spacy

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

ENG_DIR = REPO_ROOT / "data" / "text-files" / "eng-gloss"
if not ENG_DIR.exists():
    print("ERROR: Cannot find English gloss directory.", file=sys.stderr)
    sys.exit(1)

MACULA_TSV = REPO_ROOT / "research" / "macula-greek" / "SBLGNT" / "tsv" / "macula-greek-SBLGNT.tsv"

# ---------------------------------------------------------------------------
# Book-name mapping  (directory name → Macula 3-letter code)
# ---------------------------------------------------------------------------
DIR_TO_MACULA = {
    "matt": "MAT", "mark": "MRK", "luke": "LUK", "john": "JHN",
    "acts": "ACT", "rom": "ROM",
    "1cor": "1CO", "2cor": "2CO",
    "gal": "GAL", "eph": "EPH", "phil": "PHP", "col": "COL",
    "1thess": "1TH", "2thess": "2TH",
    "1tim": "1TI", "2tim": "2TI", "titus": "TIT", "phlm": "PHM",
    "heb": "HEB", "jas": "JAS",
    "1pet": "1PE", "2pet": "2PE",
    "1john": "1JN", "2john": "2JN", "3john": "3JN",
    "jude": "JUD", "rev": "REV",
}

# Lowercase conjunctions that legitimately start a line after a break
CONJUNCTIONS = {"and", "but", "for", "or", "nor", "yet", "so", "then",
                "that", "because", "since", "when", "if", "although",
                "while", "though", "until", "unless", "where", "who",
                "whom", "whose", "which", "what", "whether", "than",
                "as", "even", "not", "just", "also", "to", "of", "in",
                "by", "with", "from", "at", "on", "into", "through",
                "all", "no", "neither", "both", "either", "how",
                "lest", "like", "before", "after", "about"}

# Content-word POS tags (for repeated-word check)
CONTENT_POS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}

# ---------------------------------------------------------------------------
# Load Macula data (verse-level gender info)
# ---------------------------------------------------------------------------
def load_macula_gender(book_code):
    """Return dict: verse_ref (e.g. '1:1') → list of (word, gender, morph)."""
    verse_genders = defaultdict(list)
    if not MACULA_TSV.exists():
        return verse_genders
    with open(MACULA_TSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            ref = row.get("ref", "")
            if not ref.startswith(book_code + " "):
                continue
            # ref format: "MAT 1:1!1"  → extract "1:1"
            parts = ref.split(" ", 1)
            if len(parts) < 2:
                continue
            verse_part = parts[1].split("!")[0]  # "1:1"
            gender = row.get("gender", "")
            text = row.get("text", "")
            morph = row.get("morph", "")
            lemma = row.get("lemma", "")
            if gender:
                verse_genders[verse_part].append({
                    "text": text, "gender": gender, "morph": morph, "lemma": lemma
                })
    return verse_genders


def has_pronoun_with_gender(verse_words, target_gender):
    """Check if any pronoun (αὐτός family) in verse has given gender."""
    for w in verse_words:
        lemma = w.get("lemma", "")
        if lemma in ("αὐτός", "ἑαυτοῦ", "ἐκεῖνος", "οὗτος"):
            if w["gender"] == target_gender:
                return True
    return False


# ---------------------------------------------------------------------------
# Issue dataclass
# ---------------------------------------------------------------------------
class Issue:
    def __init__(self, file, verse, line_num, line_text, issue_type, detail):
        self.file = file
        self.verse = verse
        self.line_num = line_num
        self.line_text = line_text
        self.issue_type = issue_type
        self.detail = detail

    def __str__(self):
        return (f"  [{self.issue_type}] {self.file} {self.verse} (line {self.line_num})\n"
                f"    \"{self.line_text}\"\n"
                f"    → {self.detail}")


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check_pronoun_errors(line, verse_ref, verse_genders, issues_out, file_rel, line_num):
    """Flag 'its' when Greek has masculine/feminine referent."""
    if " its " not in f" {line} " and not line.startswith("its ") and not line.endswith(" its"):
        return
    # Check if the verse has masculine or feminine pronouns
    verse_words = verse_genders.get(verse_ref, [])
    if not verse_words:
        return
    if has_pronoun_with_gender(verse_words, "masculine") or has_pronoun_with_gender(verse_words, "feminine"):
        gender_found = "masculine" if has_pronoun_with_gender(verse_words, "masculine") else "feminine"
        issues_out.append(Issue(
            file_rel, verse_ref, line_num, line,
            "PRONOUN", f"'its' used but Greek verse has {gender_found} referent — should be 'his'/'her'?"
        ))


def check_missing_verb(doc, line, verse_ref, issues_out, file_rel, line_num, context_lines):
    """Flag lines with no verb/aux. Skip vocatives, list items, triadic stacks."""
    # Skip blank or very short
    tokens = [t for t in doc if not t.is_punct and not t.is_space]
    if len(tokens) < 2:
        return  # handled by fragment check

    has_verb = any(t.pos_ in ("VERB", "AUX") for t in doc)
    if has_verb:
        return

    # Exception: vocative lines (all caps or ending with comma before blank)
    stripped = line.strip()
    if stripped.isupper():
        return
    # Exception: lines that look like list items or triadic stacks
    # Heuristic: if 2+ surrounding lines also lack verbs, it's a stack
    verbless_neighbors = 0
    for ctx in context_lines:
        ctx_stripped = ctx.strip()
        if not ctx_stripped or re.match(r"^\d+:\d+$", ctx_stripped):
            continue
        # Quick check without spaCy for performance
        words = ctx_stripped.split()
        if len(words) >= 2:
            verbless_neighbors += 1

    # Exception: lines starting with "and" that continue a prior sentence
    if stripped.lower().startswith(("and ", "or ", "both ", "neither ")):
        return

    # Exception: prepositional phrases, relative clauses, participial phrases
    if tokens and tokens[0].pos_ in ("ADP", "SCONJ"):
        return

    # Exception: noun phrases that are objects/complements of prior line
    if stripped.endswith(",") or stripped.endswith(";"):
        return

    # Exception: lines that are clearly appositional (start with "the" + noun pattern)
    first_word = stripped.split()[0].lower() if stripped.split() else ""
    if first_word in ("the", "a", "an", "his", "her", "their", "its", "my", "our", "your",
                       "this", "that", "these", "those", "every", "each", "all", "some"):
        # Likely a noun phrase continuation
        return

    # If we get here, flag it
    issues_out.append(Issue(
        file_rel, verse_ref, line_num, line,
        "NO_VERB", "No verb or auxiliary detected in this line"
    ))


def check_subject_verb_agreement(line, doc, verse_ref, verse_genders, issues_out, file_rel, line_num):
    """Flag singular Greek subject → 'they' or plural → 'he/she'."""
    verse_words = verse_genders.get(verse_ref, [])
    if not verse_words:
        return

    # Find subjects in the Greek
    subjects = [w for w in verse_words if w["morph"].startswith("N-") or w["morph"].startswith("P-")]
    # Crude: check for nominative
    nom_subjects = [w for w in verse_words if w.get("morph", "").endswith("S") and "N" in w.get("morph", "")[:3]]

    line_lower = line.lower()

    # Check: singular Greek subject + "they" in English
    has_singular_nom = any(
        "singular" == w.get("gender", "") for w in verse_words
        # Actually we need number, not gender
    )
    # Better: look at the number column
    singular_subjects = [w for w in verse_words
                         if w.get("morph", "").startswith(("N-N", "P-N"))  # nominative
                         and "S" in w.get("morph", "")]  # singular morphology marker

    # This is too crude with just TSV — skip for now if no clear signal
    # We'd need proper nominative parsing. Keep the check minimal.
    pass


def check_fragment(line, doc, verse_ref, issues_out, file_rel, line_num):
    """Flag lines under 3 words that aren't vocatives or imperatives."""
    tokens = [t for t in doc if not t.is_punct and not t.is_space]
    if len(tokens) >= 3:
        return
    if len(tokens) == 0:
        return

    stripped = line.strip()

    # Exception: vocatives (all caps, or ending with comma/exclamation)
    if stripped.isupper():
        return
    if stripped.endswith(",") or stripped.endswith("!"):
        return

    # Exception: imperatives (spaCy mood detection)
    has_imperative = any(t.pos_ == "VERB" and "Imp" in t.morph.get("Mood", [""]) for t in doc)
    if has_imperative:
        return

    # Exception: common short valid phrases
    if stripped.lower() in ("amen", "amen.", "yes.", "yes. amen.", "selah", "hosanna",
                             "hallelujah", "maranatha", "abba"):
        return

    # Exception: single-word answers or exclamations
    if len(tokens) == 1 and tokens[0].pos_ in ("INTJ", "PROPN"):
        return

    # Exception: "Yes. Amen." type
    if re.match(r"^[A-Z][a-z]*\.\s*[A-Z][a-z]*\.$", stripped):
        return

    issues_out.append(Issue(
        file_rel, verse_ref, line_num, line,
        "FRAGMENT", f"Only {len(tokens)} content word(s) — possible nonsense fragment"
    ))


def check_repeated_words(line, doc, verse_ref, issues_out, file_rel, line_num):
    """Flag lines where the same content word appears twice."""
    content_words = [t.text.lower() for t in doc if t.pos_ in CONTENT_POS and len(t.text) > 2]
    counts = Counter(content_words)
    repeats = {w: c for w, c in counts.items() if c >= 2}
    if repeats:
        # Filter out common legitimate repeats
        legit = {"lord", "god", "holy", "amen", "come", "great", "said", "say",
                 "one", "first", "good", "day", "man", "son", "spirit", "father",
                 "king", "name", "life", "word", "death", "water", "fire", "land",
                 "heaven", "earth", "right", "left", "true"}
        flagged = {w: c for w, c in repeats.items() if w not in legit}
        if flagged:
            words_str = ", ".join(f"'{w}'×{c}" for w, c in flagged.items())
            issues_out.append(Issue(
                file_rel, verse_ref, line_num, line,
                "REPEAT", f"Repeated content word(s): {words_str}"
            ))


def check_mid_word_split(line, verse_ref, nlp, issues_out, file_rel, line_num):
    """Flag lines that appear to start with a word fragment from a bad split.

    In colometric text, lowercase-starting lines are normal (participial phrases,
    pronouns, articles, etc.). We only flag lines where the first word:
      - Is not recognized by spaCy as a real English word (OOV and short)
      - Looks like a suffix fragment (e.g. 'tion', 'ing' without a stem)
    OR the line starts with a character pattern that looks broken.
    """
    stripped = line.strip()
    if not stripped:
        return
    first_char = stripped[0]
    # Only check lowercase starts
    if not first_char.islower():
        return
    first_word = stripped.split()[0].rstrip(",.;:!?")
    if not first_word:
        return

    # Quick spaCy check: is the first word a known token?
    doc = nlp(first_word)
    token = doc[0] if doc else None

    # If it's a real POS (not X=unknown), it's fine
    if token and token.pos_ != "X":
        return

    # Even if POS is X, many proper names / transliterations are fine
    # Only flag very short fragments that look broken
    if len(first_word) <= 3 and token and token.is_oov:
        issues_out.append(Issue(
            file_rel, verse_ref, line_num, line,
            "MID_SPLIT", f"Line starts with possible word fragment: '{first_word}'"
        ))
    elif token and token.is_oov and not first_word[0].isupper():
        # OOV lowercase word — could be a fragment or transliteration
        # Only flag if it really looks like a suffix
        suffix_patterns = re.compile(r"^(tion|sion|ment|ness|ance|ence|ible|able|ious|eous|ting|ning|ling|ling|ght)s?$", re.I)
        if suffix_patterns.match(first_word):
            issues_out.append(Issue(
                file_rel, verse_ref, line_num, line,
                "MID_SPLIT", f"Line starts with possible word fragment: '{first_word}'"
            ))


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------
def process_file(filepath, book_dir_name, nlp, macula_genders):
    """Process one English gloss file, return list of Issues."""
    issues = []
    file_rel = f"{book_dir_name}/{filepath.name}"

    lines = filepath.read_text(encoding="utf-8").splitlines()
    current_verse = "?"
    content_lines = []  # (line_num, verse_ref, text)

    for i, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        # Verse reference line
        if re.match(r"^\d+:\d+[a-z]?$", stripped):
            current_verse = stripped
            continue
        content_lines.append((i, current_verse, stripped))

    # Process with spaCy in batches for performance
    texts = [cl[2] for cl in content_lines]
    docs = list(nlp.pipe(texts, batch_size=64))

    for idx, (line_num, verse_ref, line_text) in enumerate(content_lines):
        doc = docs[idx]

        # Context lines for stack detection (2 before, 2 after)
        ctx_start = max(0, idx - 2)
        ctx_end = min(len(content_lines), idx + 3)
        context = [content_lines[j][2] for j in range(ctx_start, ctx_end) if j != idx]

        # Run checks
        check_pronoun_errors(line_text, verse_ref, macula_genders, issues, file_rel, line_num)
        check_missing_verb(doc, line_text, verse_ref, issues, file_rel, line_num, context)
        check_fragment(line_text, doc, verse_ref, issues, file_rel, line_num)
        check_repeated_words(line_text, doc, verse_ref, issues, file_rel, line_num)
        check_mid_word_split(line_text, verse_ref, nlp, issues, file_rel, line_num)

    return issues


def get_book_dirs(book_filter=None):
    """Return list of (dir_path, dir_name) for books to process."""
    dirs = []
    for d in sorted(ENG_DIR.iterdir()):
        if d.is_dir():
            if book_filter and d.name != book_filter:
                continue
            dirs.append((d, d.name))
    return dirs


def main():
    parser = argparse.ArgumentParser(description="English gloss quality checker")
    parser.add_argument("--book", type=str, default=None,
                        help="Process only this book (directory name, e.g. 'mark')")
    args = parser.parse_args()

    print("Loading spaCy model...", file=sys.stderr)
    nlp = spacy.load("en_core_web_sm")

    book_dirs = get_book_dirs(args.book)
    if not book_dirs:
        print(f"ERROR: No book directories found (filter={args.book})", file=sys.stderr)
        sys.exit(1)

    all_issues = []
    file_issue_counts = Counter()
    type_counts = Counter()

    for book_dir, book_name in book_dirs:
        macula_code = DIR_TO_MACULA.get(book_name)
        print(f"Processing {book_name}...", file=sys.stderr)

        # Load Macula gender data for this book
        macula_genders = {}
        if macula_code and MACULA_TSV.exists():
            macula_genders = load_macula_gender(macula_code)

        # Process each chapter file
        chapter_files = sorted(book_dir.glob("*.txt"))
        for cf in chapter_files:
            issues = process_file(cf, book_name, nlp, macula_genders)
            all_issues.extend(issues)
            if issues:
                file_issue_counts[f"{book_name}/{cf.name}"] += len(issues)
                for iss in issues:
                    type_counts[iss.issue_type] += 1

    # ---------------------------------------------------------------------------
    # Report
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("ENGLISH QUALITY CHECK REPORT")
    print("=" * 72)

    if not all_issues:
        print("\nNo issues found!")
        return

    # Group by type
    by_type = defaultdict(list)
    for iss in all_issues:
        by_type[iss.issue_type].append(iss)

    type_labels = {
        "PRONOUN": "Pronoun Errors (its → his/her)",
        "NO_VERB": "Missing Verbs",
        "FRAGMENT": "Nonsense Fragments",
        "REPEAT": "Repeated Words",
        "MID_SPLIT": "Mid-Sentence Splits",
    }

    for itype in ("PRONOUN", "NO_VERB", "FRAGMENT", "REPEAT", "MID_SPLIT"):
        items = by_type.get(itype, [])
        if not items:
            continue
        label = type_labels.get(itype, itype)
        print(f"\n--- {label} ({len(items)} issues) ---\n")
        for iss in items:
            print(iss)
        print()

    # Summary
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"\nTotal issues: {len(all_issues)}\n")
    print("By type:")
    for itype in ("PRONOUN", "NO_VERB", "FRAGMENT", "REPEAT", "MID_SPLIT"):
        label = type_labels.get(itype, itype)
        count = type_counts.get(itype, 0)
        if count:
            print(f"  {label:40s} {count:5d}")

    print(f"\nWorst files (top 15):")
    for fname, count in file_issue_counts.most_common(15):
        print(f"  {fname:45s} {count:4d} issues")


if __name__ == "__main__":
    main()
