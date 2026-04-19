#!/usr/bin/env python3
"""
scan_hoti_jammed_speech_intro.py — Find lines that jam a speech-intro
frame with its content via mid-line ὅτι.

Class instance: Matt 8:11 `λέγω δὲ ὑμῖν ὅτι πολλοὶ ἀπὸ ἀνατολῶν καὶ
δυσμῶν ἥξουσιν` — speech verb + ὅτι + quote content all on ONE line.

R11 says speech-intros own their line; content follows on next line.
The ὅτι is the natural split point (stays on the intro line, NEVER
dropped — it's Greek text, not punctuation).

Signature:
  A single line contains:
    - a speech/declaration verb lemma (narrow list)
    - ὅτι (mid-line, not last token)
    - content past the ὅτι (at least 2 more tokens)

Dry-run enumeration for a sweep. Output: candidates + proposed split.
"""
import os, re, json, sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4-editorial")
MORPH = os.path.join(REPO, "research", "morphgnt-sblgnt")

SLUGS = {"61":"matt","62":"mark","63":"luke","64":"john","65":"acts","66":"rom","67":"1cor","68":"2cor","69":"gal","70":"eph","71":"phil","72":"col","73":"1thess","74":"2thess","75":"1tim","76":"2tim","77":"titus","78":"phlm","79":"heb","80":"jas","81":"1pet","82":"2pet","83":"1john","84":"2john","85":"3john","86":"jude","87":"rev"}
SLUG_TO_FN = {v:k for k,v in SLUGS.items()}
_cache = {}

# Verbs that license recitative/declaration ὅτι
SPEECH_DECL_LEMMAS = {
    "λέγω", "φημί", "εἶπον",  # εἶπον lemmatized λέγω in MorphGNT
    "γράφω",
    "μαρτυρέω", "ὁμολογέω",
    "διδάσκω", "κηρύσσω",
    "ἀπαγγέλλω", "ἀναγγέλλω", "καταγγέλλω",
    "προφητεύω",
    "ἀποκρίνομαι",
    "κράζω", "κραυγάζω", "βοάω",
    "ἀκούω",  # "hear that..."
    "γινώσκω", "οἶδα", "ὁράω", "βλέπω", "πιστεύω",  # cognition (R10 merge side)
    "γέγραπται",  # perfect passive "it is written"
    "γράφω",
}
# These cognition lemmas merge per R10 — flag separately
COGNITION_LEMMAS = {"γινώσκω", "οἶδα", "ὁράω", "βλέπω", "πιστεύω", "ἀκούω"}

HOTI_FORMS = {"ὅτι"}

def clean(w):
    return re.sub(r"[,.\;\·\s'\u2019\"\(\)\[\]⟦⟧—–\u037E\u0387\u00B7]", "", w)

def load_morph(slug):
    if slug in _cache: return _cache[slug]
    fn = SLUG_TO_FN.get(slug)
    if not os.path.isdir(MORPH):
        _cache[slug] = {}; return {}
    path = next((os.path.join(MORPH, f) for f in os.listdir(MORPH)
                 if fn and f.startswith(fn+"-") and f.endswith(".txt")), None)
    if not path:
        _cache[slug] = {}; return {}
    verses = defaultdict(list)
    for line in open(path, encoding="utf-8"):
        parts = line.strip().split(" ", 6)
        if len(parts) < 7: continue
        ref, pos, parsing, _, word, _n, lemma = parts
        c = clean(word)
        if c:
            verses[(int(ref[2:4]), int(ref[4:6]))].append((c, pos, parsing, lemma))
    _cache[slug] = dict(verses); return _cache[slug]

def word_positions(text):
    out, i, n = [], 0, len(text)
    while i < n:
        while i < n and text[i].isspace(): i += 1
        if i >= n: break
        s = i
        while i < n and not text[i].isspace(): i += 1
        out.append((text[s:i], s, i))
    return out

def bind_line(text, verse_pool):
    bound = []
    for raw, _, _ in word_positions(text):
        c = clean(raw)
        lst = verse_pool.get(c)
        if lst:
            bound.append(lst.pop(0))
        else:
            bound.append(None)
    return bound

VERSE_RE = re.compile(r"^(\d+):(\d+)$")

def load_chapter(path):
    verses = []
    cur_ref, cur_lines = None, []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            m = VERSE_RE.match(s)
            if m:
                if cur_ref is not None:
                    verses.append((cur_ref, cur_lines))
                cur_ref = (int(m.group(1)), int(m.group(2)))
                cur_lines = []
            elif s:
                cur_lines.append(s)
        if cur_ref is not None:
            verses.append((cur_ref, cur_lines))
    return verses

def find_jammed(line_text, bound):
    """Return (split_idx, speech_lemma, cognition?) if line is jammed, else None.

    split_idx = index of the token AFTER ὅτι where we'd split.
    """
    raw_tokens = word_positions(line_text)
    if len(raw_tokens) != len(bound): return None
    # Find ὅτι positions (mid-line, not last, not first)
    hoti_idx = None
    for i, (raw, _, _) in enumerate(raw_tokens):
        if clean(raw) in HOTI_FORMS:
            if 0 < i < len(raw_tokens) - 1:
                hoti_idx = i; break
    if hoti_idx is None: return None
    # Need at least 2 tokens of content after ὅτι
    if len(raw_tokens) - (hoti_idx + 1) < 2: return None
    # Find a speech/declaration/cognition lemma BEFORE ὅτι
    speech_lemma = None
    cognition = False
    for i in range(hoti_idx):
        b = bound[i]
        if b is None: continue
        _, pos, p, lemma = b
        if lemma in SPEECH_DECL_LEMMAS:
            speech_lemma = lemma
            if lemma in COGNITION_LEMMAS: cognition = True
            break
    if speech_lemma is None: return None
    return hoti_idx, speech_lemma, cognition

def main():
    findings = []
    for ent in sorted(os.listdir(V4)):
        bp = os.path.join(V4, ent)
        if not os.path.isdir(bp): continue
        parts = ent.split("-", 1)
        book = parts[1] if len(parts) == 2 and parts[0].isdigit() else ent
        morph = load_morph(book)
        for fn in sorted(os.listdir(bp)):
            if not fn.endswith(".txt"): continue
            for ref, lines in load_chapter(os.path.join(bp, fn)):
                vw = morph.get(ref, [])
                for line in lines:
                    pool = defaultdict(list)
                    for t in vw: pool[t[0]].append(t)
                    bound = bind_line(line, pool)
                    r = find_jammed(line, bound)
                    if r:
                        hoti_idx, lemma, cognition = r
                        # Split AFTER the ὅτι token
                        raw_tokens = word_positions(line)
                        split_char = raw_tokens[hoti_idx][2]
                        left = line[:split_char].rstrip()
                        right = line[split_char:].lstrip()
                        findings.append({
                            "book": book, "ref": f"{ref[0]}:{ref[1]}",
                            "line": line, "left": left, "right": right,
                            "speech_verb_lemma": lemma,
                            "is_cognition": cognition,
                        })
    # Report
    out_md = os.path.join(REPO, "private", "hoti-jammed-speech-intro.md")
    by_book = defaultdict(int)
    by_cog = {"speech_decl": 0, "cognition": 0}
    for f in findings:
        by_book[f["book"]] += 1
        by_cog["cognition" if f["is_cognition"] else "speech_decl"] += 1
    lines = []
    lines.append("# ὅτι-jammed speech-intro lines\n")
    lines.append(f"**Scanner:** `scripts/scan_hoti_jammed_speech_intro.py`\n")
    lines.append(f"**Count:** {len(findings)} candidates\n")
    lines.append("**Signature:** single line contains speech/declaration/cognition verb + mid-line ὅτι + ≥2 tokens of content past ὅτι. Class instance: Matt 8:11 `λέγω δὲ ὑμῖν ὅτι πολλοὶ ἀπὸ ἀνατολῶν καὶ δυσμῶν ἥξουσιν`.\n")
    lines.append("**Proposed split:** after ὅτι. ὅτι stays on the intro line (never dropped).\n")
    lines.append(f"- Speech/declaration: {by_cog['speech_decl']}  → split (R11)")
    lines.append(f"- Cognition: {by_cog['cognition']}  → MERGE per R10 (already correct as-is; listed for audit only)")
    lines.append("")
    lines.append("## By book")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1]):
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## Full list (speech/declaration = SPLIT candidates)")
    for f in findings:
        if f["is_cognition"]: continue
        lines.append(f"**{f['book']} {f['ref']}** ({f['speech_verb_lemma']})")
        lines.append(f"  BEFORE: `{f['line']}`")
        lines.append(f"  AFTER:  `{f['left']}`")
        lines.append(f"          `{f['right']}`")
        lines.append("")
    if by_cog["cognition"]:
        lines.append("## Cognition verbs (MERGE per R10 — no action needed)")
        for f in findings:
            if not f["is_cognition"]: continue
            lines.append(f"- {f['book']} {f['ref']} ({f['speech_verb_lemma']}): `{f['line']}`")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"{len(findings)} total candidates")
    print(f"  Speech/declaration (SPLIT): {by_cog['speech_decl']}")
    print(f"  Cognition (no action, R10 merge): {by_cog['cognition']}")
    print(f"\nBy book:")
    for k, v in sorted(by_book.items(), key=lambda x: -x[1]):
        print(f"  {k:10s} {v}")
    print(f"\nWritten: {out_md}")

if __name__ == "__main__":
    main()
