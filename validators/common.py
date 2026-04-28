"""
validators/common.py — Shared infrastructure for Layer 2 validators.

All validators in validators/syntax/ and validators/colometry/ import from here.
Provides: Candidate dataclass, data loaders, v4-editorial parser, token mapper,
  punctuation stripper, and markdown report writer.

Macula data shape:
  get_chapter_clauses_detailed(book, chapter) ->
      dict[verse_num: int, list[ClauseInfo]]
  ClauseInfo.words = [(ref_str, normalized_text), ...]
  ClauseInfo.rule may come back as "Rule" attribute in some XML nodes —
      use get_rule_attr(node) to guard against the inconsistency.

MorphGNT data shape (_load_book):
  dict[(chapter: int, verse: int), list[tuple[word, pos, parsing]]]
  word = surface form (may include punctuation)
  pos  = 2-char POS code (e.g. "V-", "N-", "RA")
  parsing = 8-char morphology string (person/tense/voice/mood/case/number/gender/degree)
"""

from __future__ import annotations

import os
import re
import sys
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional

# ─── Path constants + _shared importable ─────────────────────────────────────

_VALIDATORS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_VALIDATORS_DIR)

if _VALIDATORS_DIR not in sys.path:
    sys.path.insert(0, _VALIDATORS_DIR)

from _shared import macula_clauses, morphgnt_lookup  # noqa: E402

# ─── Paths ───────────────────────────────────────────────────────────────────

_V4_ROOT = os.path.join(_REPO_ROOT, "data", "text-files", "v4-editorial")
_MORPHGNT_DIR = os.path.join(_REPO_ROOT, "research", "morphgnt-sblgnt")

# ─── Book slug utilities (factored from validate_r18/r19/r11 boilerplate) ────
# v4-editorial dirs use the form "NN-slug" (e.g. "01-matt", "05-acts").
# This map is the same SLUGS dict that every validator duplicates inline.

BOOK_SLUGS: dict[str, str] = {
    "61": "matt",  "62": "mark",  "63": "luke",  "64": "john",
    "65": "acts",  "66": "rom",   "67": "1cor",  "68": "2cor",
    "69": "gal",   "70": "eph",   "71": "phil",  "72": "col",
    "73": "1thess","74": "2thess","75": "1tim",  "76": "2tim",
    "77": "titus", "78": "phlm",  "79": "heb",   "80": "jas",
    "81": "1pet",  "82": "2pet",  "83": "1john", "84": "2john",
    "85": "3john", "86": "jude",  "87": "rev",
}
SLUG_TO_FILE_NUM: dict[str, str] = {v: k for k, v in BOOK_SLUGS.items()}

# Map from v4 directory base name ("01-matt") to book slug ("matt")
def _dir_to_slug(dirname: str) -> str:
    """Strip optional leading "NN-" prefix from a v4-editorial directory name."""
    parts = dirname.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1]
    return dirname


# ─── Rule attribute double-get guard ─────────────────────────────────────────

def get_rule_attr(node) -> str:
    """Double-get guard for the rule/Rule attribute inconsistency in Macula XML.

    Some Macula wg elements store the attribute as "rule", others as "Rule".
    Always use this helper rather than .get("rule") directly.
    """
    return node.get("rule") or node.get("Rule") or ""


# ─── Candidate output type ───────────────────────────────────────────────────

@dataclass
class Candidate:
    verse_ref: str       # "Matt 4:1"
    line_index: int      # 0-based index within chapter
    line_text: str       # raw line content for context
    rule: str            # "R2", "R18", "M1", etc.
    tag: str             # "STRONG-MERGE" | "STRONG-SPLIT" | "REVIEW-REQUIRED" | "AMBIG"
    error_class: str     # "MALFORMED" (Layer 1) | "DEVIATION" (Layer 3)
    rationale: str       # short description of why this is flagged
    context: str = ""    # 2-3 lines surrounding (optional)


def emit_candidate(
    verse_ref: str,
    line_index: int,
    line_text: str,
    rule: str,
    tag: str,
    error_class: str,
    rationale: str,
    context: str = "",
) -> Candidate:
    """Constructor helper — same fields as Candidate dataclass."""
    return Candidate(verse_ref, line_index, line_text, rule, tag, error_class, rationale, context)


# ─── Data loaders (thin wrappers around scripts/) ────────────────────────────

def load_macula_chapter(book: str, chapter: int) -> dict:
    """Load Macula-Greek parse for a chapter.

    Wraps validators/_shared/macula_clauses.get_chapter_clauses_detailed.
    Returns dict[verse_num: int, list[ClauseInfo]].
    Each ClauseInfo has:
      .text           — space-joined surface text of the clause
      .words          — [(ref_str, normalized_text), ...]  in surface order
      .has_participle — bool
      .is_genitive_absolute — bool
      .clause_type    — str (Macula clauseType attribute)
      .rule           — str (Macula rule attribute; use get_rule_attr for raw nodes)
    Apply the rule/Rule double-get guard on any raw XML node dict access.
    """
    return macula_clauses.get_chapter_clauses_detailed(book, chapter)


def load_morphgnt_book(book_slug: str) -> dict:
    """Load MorphGNT data for a book.

    Wraps validators/_shared/morphgnt_lookup._load_book.
    Returns dict[(chapter: int, verse: int), list[tuple[word, pos, parsing]]].
      word    — surface form (may include punctuation)
      pos     — 2-char POS code ("V-", "N-", "RA", etc.)
      parsing — 8-char morphology string
    Returns {} if book file is not found.
    """
    return morphgnt_lookup._load_book(book_slug)


# Cache for the 4-tuple (lemma-aware) MorphGNT loader below.
_morphgnt_with_lemma_cache: dict = {}


def load_morphgnt_book_with_lemma(book_slug: str) -> dict:
    """Load MorphGNT data including lemma (4-tuples).

    morphgnt_lookup._load_book drops the lemma field; this helper reads the
    MorphGNT text file directly and preserves it.

    Returns dict[(chapter: int, verse: int), list[tuple[word, pos, parsing, lemma]]].
      word    — surface form, punctuation-stripped
      pos     — 2-char POS code ("V-", "N-", "RA", etc.)
      parsing — 8-char morphology string
      lemma   — dictionary form
    Returns {} if book file is not found.
    """
    if book_slug in _morphgnt_with_lemma_cache:
        return _morphgnt_with_lemma_cache[book_slug]
    file_num = SLUG_TO_FILE_NUM.get(book_slug)
    if not file_num or not os.path.isdir(_MORPHGNT_DIR):
        _morphgnt_with_lemma_cache[book_slug] = {}
        return {}
    path = next(
        (os.path.join(_MORPHGNT_DIR, f) for f in os.listdir(_MORPHGNT_DIR)
         if f.startswith(file_num + "-") and f.endswith(".txt")),
        None,
    )
    if not path:
        _morphgnt_with_lemma_cache[book_slug] = {}
        return {}
    verses: dict = defaultdict(list)
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.strip().split(" ", 6)
            if len(parts) < 7:
                continue
            ref, pos, parsing, _text, word, _norm, lemma = parts
            cleaned = strip_punctuation(word)
            if cleaned:
                verses[(int(ref[2:4]), int(ref[4:6]))].append(
                    (cleaned, pos, parsing, lemma)
                )
    result = dict(verses)
    _morphgnt_with_lemma_cache[book_slug] = result
    return result


# ─── Punctuation stripping ───────────────────────────────────────────────────

# Characters to strip when comparing Greek tokens.
# Includes standard punctuation, Greek-specific marks, and Unicode variants.
_PUNCT_RE = re.compile(
    r"[,.\;\·\s"
    r"\u037E"   # Greek question mark
    r"\u0387"   # Greek ano teleia
    r"\u00B7"   # middle dot
    r"\u02BC"   # modifier letter apostrophe
    r"'`\(\)\[\]\{\}⟦⟧—–"
    r"⸀⸁⸂⸃⸄⸅"   # critical apparatus sigla
    r"]",
    re.UNICODE,
)


def strip_punctuation(text: str) -> str:
    """Strip Greek punctuation from a word and apply NFC normalization.

    Strips: . , ; : · ? ! ( ) [ ] { } — – U+02BC U+00B7 U+037E U+0387
    and Macula/MorphGNT apparatus sigla ⸀⸁⸂⸃⸄⸅.
    Also normalizes to Unicode NFC so combining diacritics compare correctly.
    """
    normalized = unicodedata.normalize("NFC", text)
    return _PUNCT_RE.sub("", normalized)


# Combining accent marks that are prosody-determined (not lexically distinctive).
# U+0301 acute, U+0300 grave, U+0342 perispomeni/circumflex.
# Breathing marks (U+0313 smooth, U+0314 rough) are intentionally kept —
# they carry lexical weight (e.g. ἄγω vs ἅγιος).
_ACCENT_MARKS = frozenset(["\u0301", "\u0300", "\u0342"])


def _compare_normalize(text: str) -> str:
    """Return a form suitable for token-identity comparison across accent variants.

    NFD-decomposes the input, strips combining acute/grave/circumflex (which
    Macula may add or rearrange due to enclitic sandhi), then NFC-recomposes.
    Breathing marks are preserved.  Used only for matching; original surface
    forms are stored in Token.word unchanged.
    """
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(ch for ch in decomposed if ch not in _ACCENT_MARKS)
    return unicodedata.normalize("NFC", stripped)


# ─── v4-editorial loader ──────────────────────────────────────────────────────

_VERSE_RE = re.compile(r"^(\d+):(\d+)$")


@dataclass
class V4Line:
    line_index: int      # 0-based within chapter
    text: str            # raw Greek text of this line (leading/trailing ws stripped)
    verse_ref: str       # "Matt 4:1" style — which verse this line belongs to
    tokens: list         # list of punctuation-stripped Greek words in order


@dataclass
class V4Chapter:
    book: str
    chapter: int
    lines: list          # list of V4Line


def _find_v4_file(book: str, chapter: int) -> str:
    """Locate the v4-editorial file for a book/chapter.

    Handles both bare slug directories ("matt") and prefixed directories
    ("01-matt"). Returns the full path or raises FileNotFoundError.
    """
    # Try both forms: plain slug and numbered prefix
    candidates = []
    if os.path.isdir(_V4_ROOT):
        for entry in os.listdir(_V4_ROOT):
            slug = _dir_to_slug(entry)
            if slug == book:
                candidates.append(os.path.join(_V4_ROOT, entry))

    for dirpath in candidates:
        fname = f"{book}-{chapter:02d}.txt"
        fpath = os.path.join(dirpath, fname)
        if os.path.exists(fpath):
            return fpath

    raise FileNotFoundError(
        f"v4-editorial file not found for book={book!r} chapter={chapter}. "
        f"Searched in {_V4_ROOT!r}."
    )


def load_v4_editorial(book: str, chapter: int) -> V4Chapter:
    """Load a v4-editorial chapter file and parse it into V4Chapter.

    File format (UTF-8, plain text):
      - Lines matching "^\\d+:\\d+$" are verse-ref markers (e.g. "4:1").
      - All other non-empty lines are sense-lines belonging to the current verse.
      - Blank lines are ignored.

    Each sense-line becomes one V4Line. line_index is 0-based across the
    whole chapter (not per-verse). verse_ref is formatted as "Book CH:VS"
    (e.g., "Matt 4:1") using the capitalized book name.

    V4Line.tokens = punctuation-stripped NFC words in order of appearance.
    """
    fpath = _find_v4_file(book, chapter)

    # Capitalize first letter of book for display (matt -> Matt, 1cor -> 1Cor)
    display_book = book[0].upper() + book[1:] if book else book

    lines: list[V4Line] = []
    current_verse_ref = f"{display_book} {chapter}:?"  # fallback before first marker
    line_index = 0

    with open(fpath, encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if not stripped:
                continue
            m = _VERSE_RE.match(stripped)
            if m:
                current_verse_ref = f"{display_book} {m.group(1)}:{m.group(2)}"
            else:
                tokens = [strip_punctuation(w) for w in stripped.split()]
                tokens = [t for t in tokens if t]  # drop empty strings
                lines.append(V4Line(
                    line_index=line_index,
                    text=stripped,
                    verse_ref=current_verse_ref,
                    tokens=tokens,
                ))
                line_index += 1

    return V4Chapter(book=book, chapter=chapter, lines=lines)


# ─── Token mapping ────────────────────────────────────────────────────────────

@dataclass
class Token:
    word: str              # surface form from Macula (normalized attribute)
    pos: str               # class attribute from Macula (or empty if unavailable)
    lemma: str             # lemma from Macula
    morph: str             # full morph string (tense+voice+mood+case+number+gender)
    role: str              # syntactic role from Macula (s, o, v, adv, ...)
    line_index: int        # v4-editorial line this token lives on (-1 = unmapped)
    position_in_line: int  # 0-based position within that line (-1 = unmapped)
    verse_ref: str         # "Matt 4:1"
    macula_raw: dict = field(default_factory=dict)  # raw Macula word element attributes


def _flatten_macula_tokens(macula_chapter: dict) -> list[dict]:
    """Flatten macula chapter dict into a list of word dicts in document order.

    macula_chapter: dict[verse_num, list[ClauseInfo]]
    ClauseInfo.words: list of (ref_str, normalized_text)
    We need the full word element attributes, so we reconstruct from ClauseInfo.

    Note: ClauseInfo.words only carries (ref, text) tuples — the raw element
    attributes (pos/class, lemma, morph, role) are not directly exposed by
    ClauseInfo. We emit synthetic dicts with what's available and fill the rest
    with empty strings. Validators needing full Macula token attributes should
    use macula_clauses._parse_book() directly for raw element access.

    Tokens are sorted by (verse, word_position) using the ref string.
    """
    tokens = []
    for verse_num in sorted(macula_chapter.keys()):
        for clause_info in macula_chapter[verse_num]:
            for ref, text in clause_info.words:
                tokens.append({
                    "ref": ref,
                    "word": text,
                    "pos": "",      # not carried by ClauseInfo.words
                    "lemma": "",    # not carried by ClauseInfo.words
                    "morph": "",    # not carried by ClauseInfo.words
                    "role": "",     # not carried by ClauseInfo.words
                    "clause_type": clause_info.clause_type,
                    "rule": clause_info.rule,
                })
    # Sort by (chapter, verse, word_position) using macula_clauses._parse_ref
    def _sort_key(t):
        _, ch, vs, pos = macula_clauses._parse_ref(t["ref"])
        return (ch or 0, vs or 0, pos or 0)

    tokens.sort(key=_sort_key)
    # Deduplicate: same ref can appear in multiple clauses; keep first occurrence
    seen_refs: set[str] = set()
    deduped = []
    for t in tokens:
        if t["ref"] not in seen_refs:
            seen_refs.add(t["ref"])
            deduped.append(t)
    return deduped


def map_tokens_to_lines(v4_chapter: V4Chapter, macula_chapter: dict) -> list[Token]:
    """Map each Macula token to its v4-editorial line_index.

    Algorithm: sequential-consume queue.
    1. Build a flat queue of (line_index, position_in_line, stripped_word) from
       all V4Line.tokens in order.
    2. Flatten and sort Macula tokens into document order.
    3. Walk both queues, matching on NFC-stripped surface form.
       - On match: consume from both queues; record line_index + position.
       - Macula token no match after scanning ahead V4_LOOKAHEAD positions:
         log a warning and emit Token with line_index=-1 (unmapped).
       - V4 word no match: advance the v4 queue (Macula may have skipped it).

    Returns list of Token in Macula document order. Unmapped tokens have
    line_index=-1 and position_in_line=-1.

    Note: Because ClauseInfo.words does not expose per-word POS/lemma/morph,
    those fields will be empty strings in the returned Tokens. For full
    morphological data, validators should also call load_morphgnt_book() and
    correlate by (chapter, verse, word_position) via the verse_ref.
    """
    V4_LOOKAHEAD = 5  # how many v4 positions to scan before declaring mismatch

    # Build v4 queue: list of (line_index, position_in_line, stripped_word)
    v4_queue: list[tuple[int, int, str]] = []
    v4_verse_refs: dict[tuple[int, int], str] = {}  # (line_idx, pos) -> verse_ref
    for vline in v4_chapter.lines:
        for pos, tok in enumerate(vline.tokens):
            v4_queue.append((vline.line_index, pos, tok))
            v4_verse_refs[(vline.line_index, pos)] = vline.verse_ref

    # Flatten Macula tokens
    macula_tokens = _flatten_macula_tokens(macula_chapter)

    result: list[Token] = []
    v4_ptr = 0  # current position in v4_queue

    for mtok in macula_tokens:
        m_word = strip_punctuation(unicodedata.normalize("NFC", mtok["word"]))
        if not m_word:
            continue  # skip punctuation-only macula entries

        matched = False
        # Scan ahead in v4 queue to find a match
        for lookahead in range(V4_LOOKAHEAD):
            v4_pos = v4_ptr + lookahead
            if v4_pos >= len(v4_queue):
                break
            v4_line_idx, v4_word_pos, v4_word = v4_queue[v4_pos]
            if _compare_normalize(m_word) == _compare_normalize(v4_word):
                # Consume everything up to and including this match
                v4_ptr = v4_pos + 1
                vref = v4_verse_refs.get((v4_line_idx, v4_word_pos), "")
                result.append(Token(
                    word=mtok["word"],
                    pos=mtok.get("pos", ""),
                    lemma=mtok.get("lemma", ""),
                    morph=mtok.get("morph", ""),
                    role=mtok.get("role", ""),
                    line_index=v4_line_idx,
                    position_in_line=v4_word_pos,
                    verse_ref=vref,
                    macula_raw=mtok,
                ))
                matched = True
                break

        if not matched:
            # Could not find this Macula word in the v4 queue within lookahead
            # Determine verse_ref from Macula ref string
            _, ch, vs, _ = macula_clauses._parse_ref(mtok["ref"])
            vref = f"{v4_chapter.book[0].upper()}{v4_chapter.book[1:]} {ch}:{vs}" if ch else ""
            result.append(Token(
                word=mtok["word"],
                pos=mtok.get("pos", ""),
                lemma=mtok.get("lemma", ""),
                morph=mtok.get("morph", ""),
                role=mtok.get("role", ""),
                line_index=-1,
                position_in_line=-1,
                verse_ref=vref,
                macula_raw=mtok,
            ))

    return result


# ─── v4-editorial corpus iterator (factored from validate_* boilerplate) ─────

def iter_v4_chapters():
    """Yield (slug, chapter_num, filepath) for every v4-editorial chapter.

    Replaces the duplicated os.listdir(V4) + parse_chapter() pattern in
    validate_r18_vocative.py, validate_r19_genabs.py, validate_r11_speech_intro.py.
    Yields tuples in sorted book/chapter order.
    """
    if not os.path.isdir(_V4_ROOT):
        return
    for entry in sorted(os.listdir(_V4_ROOT)):
        dirpath = os.path.join(_V4_ROOT, entry)
        if not os.path.isdir(dirpath):
            continue
        slug = _dir_to_slug(entry)
        for fname in sorted(os.listdir(dirpath)):
            if not fname.endswith(".txt"):
                continue
            # Parse chapter number from filename: "matt-04.txt" -> 4
            m = re.search(r"-(\d+)\.txt$", fname)
            if not m:
                continue
            chapter_num = int(m.group(1))
            yield slug, chapter_num, os.path.join(dirpath, fname)


def parse_chapter_file(filepath: str) -> list[dict]:
    """Parse a v4-editorial chapter file into verse dicts.

    Factored from the identical parse_chapter() in validate_r18, r19, r11.
    Returns list of dicts:
      {"ref": "4:1", "ch": 4, "vs": 1, "lines": [raw_line_str, ...]}
    lines preserve original whitespace (trailing newline stripped).
    """
    verses: list[dict] = []
    cur: Optional[dict] = None
    for raw in open(filepath, encoding="utf-8"):
        s = raw.strip()
        if not s:
            continue
        m = _VERSE_RE.match(s)
        if m:
            if cur:
                verses.append(cur)
            cur = {
                "ref": s,
                "ch": int(m.group(1)),
                "vs": int(m.group(2)),
                "lines": [],
            }
        elif cur:
            cur["lines"].append(raw.rstrip("\r\n"))
    if cur:
        verses.append(cur)
    return verses


# ─── MorphGNT word-level helpers (factored from validate_* boilerplate) ──────
# These replicate inline helper functions defined in each validator.
# Validators can import these rather than defining their own.

def is_finite_verb(pos: str, parsing: str) -> bool:
    """True if POS starts with V and mood is indicative/subjunctive/imperative/optative."""
    return pos.startswith("V") and len(parsing) >= 4 and parsing[3] in "ISDO"


def is_2p_verb(pos: str, parsing: str) -> bool:
    """True if finite verb with person=2."""
    return is_finite_verb(pos, parsing) and len(parsing) >= 1 and parsing[0] == "2"


def is_vocative(pos: str, parsing: str) -> bool:
    """True if noun/adj/pronoun in vocative case (MorphGNT parsing[4]=='V')."""
    return pos in ("N-", "A-", "RP", "RD") and len(parsing) >= 5 and parsing[4] == "V"


_SECOND_PERSON_PRONOUN_SURFACES: frozenset = frozenset({
    # 2p singular
    "σύ", "σοῦ", "σου", "σοί", "σοι", "σέ", "σε",
    # 2p plural
    "ὑμεῖς", "ὑμῶν", "ὑμῖν", "ὑμᾶς",
})


def is_2p_pronoun(pos: str, parsing: str, lemma: str, surface: str = "") -> bool:
    """True if personal pronoun referencing second person (σύ and case forms).

    Uses lemma == "σύ" as the primary check (requires load_morphgnt_book_with_lemma).
    Falls back to surface-form matching for robustness when lemma is absent.
    Canon §3.9: object-appositive merge fires on any explicit 2p pronoun.
    """
    if pos == "RP" and lemma == "σύ":
        return True
    # Surface-form fallback: catches cases where lemma field is empty or mismatched.
    if surface and strip_punctuation(surface) in _SECOND_PERSON_PRONOUN_SURFACES:
        return True
    return False


def is_genitive_participle(pos: str, parsing: str) -> bool:
    """True if participle in genitive case."""
    return pos.startswith("V") and len(parsing) >= 5 and parsing[3] == "P" and parsing[4] == "G"


def is_genitive_noun_or_pronoun(pos: str, parsing: str) -> bool:
    """True if noun, adjective, or pronoun in genitive case."""
    return pos in ("N-", "RP", "RD", "A-") and len(parsing) >= 5 and parsing[4] == "G"


# ─── Report writer ────────────────────────────────────────────────────────────

# Human-readable names for known rule codes
_RULE_NAMES: dict[str, str] = {
    "R2":  "subordinate clause break",
    "R11": "direct-speech introduction",
    "R18": "vocative own line",
    "R19": "genitive absolute own line",
    "R25": "speech-frame absorption",
    "M1":  "merge override (bonded pair)",
    "M2":  "merge override (coordinate pair)",
    "M3":  "merge override (FEF)",
    "M4":  "merge override (judgment)",
}


def _rule_display(rule: str) -> str:
    name = _RULE_NAMES.get(rule, "")
    return f"{rule} — {name}" if name else rule


def write_candidates(
    candidates: list,
    output_path: str,
    title: str = "Validator Report",
) -> None:
    """Write candidates as a grouped markdown report.

    Structure:
        # {title}

        ## MALFORMED (Layer 1 violations) — N total

        ### R18 (N) — vocative own line
        - verse_ref — line N — "text" — rationale

        ## DEVIATION (Layer 3 violations) — N total

        ### R19 (N) — genitive absolute own line
        - ...

    Groups: first by error_class (MALFORMED then DEVIATION then others),
    then by rule code within each class.
    """
    # Group by error_class, then by rule
    by_class: dict[str, dict[str, list[Candidate]]] = defaultdict(lambda: defaultdict(list))
    for c in candidates:
        by_class[c.error_class][c.rule].append(c)

    # Desired error_class order
    class_order = ["MALFORMED", "DEVIATION"]
    remaining_classes = [k for k in sorted(by_class) if k not in class_order]
    all_classes = class_order + remaining_classes

    lines_out: list[str] = [f"# {title}", ""]

    for ec in all_classes:
        if ec not in by_class:
            continue
        ec_rules = by_class[ec]
        ec_total = sum(len(v) for v in ec_rules.values())
        lines_out.append(f"## {ec} — {ec_total} total")
        lines_out.append("")

        for rule in sorted(ec_rules.keys()):
            rule_candidates = ec_rules[rule]
            display = _rule_display(rule)
            lines_out.append(f"### {display} ({len(rule_candidates)})")
            for c in rule_candidates:
                tag_str = f"[{c.tag}] " if c.tag else ""
                line_str = f'"{c.line_text}"' if c.line_text else "(empty)"
                lines_out.append(
                    f"- {c.verse_ref} — line {c.line_index} — {line_str} — "
                    f"{tag_str}{c.rationale}"
                )
                if c.context:
                    lines_out.append(f"  - context: {c.context}")
            lines_out.append("")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines_out) + "\n")
