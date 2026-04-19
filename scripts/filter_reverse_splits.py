#!/usr/bin/env python3
"""
filter_reverse_splits.py — Partition the 160 adversarial-approved
reverse-drift SPLITs into "clear legit" and "M2-narrative-beat questionable"
buckets for staged application.

Signature of questionable M2-narrative-beat candidate (SKIP):
  - Both halves are ≤3 content tokens AND
  - Neither half carries a distinct noun-phrase complement (article+noun
    with its own case marking) AND
  - The two verbs are structurally similar (both bare verbs, or one
    intransitive + one transitive-with-short-complement)

Legit SPLIT (APPLY):
  - Distinct named complements / objects (Matt 5:43-class)
  - Distinct subjects in each half
  - Antithetical/contrastive content
  - Long enough that splitting clearly aids readability
"""
import os, sys, json, glob, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIV = os.path.join(REPO, "private")

def tokenize(text):
    return [t for t in re.split(r'\s+', text.strip()) if t]

def has_distinct_np(text):
    """Heuristic: does this half contain a distinct NP with article + noun?"""
    # Article markers
    ART = ("ὁ","ἡ","τό","τοὺς","τὴν","τὸ","τῷ","τῇ","τοῦ","τῆς","τοῖς","ταῖς","τῶν","τὰ","οἱ","αἱ")
    toks = tokenize(text)
    if len(toks) < 3: return False
    for i, t in enumerate(toks):
        # strip trailing punctuation
        clean = re.sub(r'[,.\;·\?!:·\'\"]', '', t)
        if clean in ART and i < len(toks) - 1:
            return True
    # Check for proper noun (capitalized mid-phrase word)
    for t in toks[1:]:
        if len(t) >= 3 and t[0].isupper():
            return True
    return False

def classify(cand):
    left = cand["left"]
    right = cand["right"]
    # Strip leading καί from right
    right_stripped = re.sub(r'^καὶ\s+|^καί\s+', '', right)
    lt = tokenize(left)
    rt = tokenize(right_stripped)
    # Clear legit: long halves or distinct NPs
    if len(lt) >= 4 or len(rt) >= 4:
        return "LEGIT_LONG"
    if has_distinct_np(left) and has_distinct_np(right_stripped):
        return "LEGIT_DISTINCT_NPS"
    # Check for distinct-subject markers (nominative articles, pronouns)
    NOMS = ("ὁ","ἡ","οἱ","αἱ","ἐγώ","σύ","ἡμεῖς","ὑμεῖς","αὐτός","αὐτή")
    both_have_noms = any(tokenize(left)[0] in NOMS for _ in [0]) and any(tokenize(right_stripped)[0] in NOMS for _ in [0] if tokenize(right_stripped))
    # Fallback: short pair without distinct NPs — likely M2 narrative-beat
    return "QUESTIONABLE_M2"

def main():
    # Load cands + verdicts
    cands = {}
    for f in sorted(glob.glob(os.path.join(PRIV, "reverse-adv-batches", "*.json"))):
        for c in json.load(open(f, encoding="utf-8")):
            cands[c["_id"]] = c
    verdicts = {}
    for f in sorted(glob.glob(os.path.join(PRIV, "reverse-adv-verdicts", "*.json"))):
        for v in json.load(open(f, encoding="utf-8")):
            verdicts[v["_id"]] = v
    splits = [{**cands[cid], **v} for cid, v in verdicts.items()
              if v.get("outcome") == "SPLIT" and cid in cands]
    legit = []
    questionable = []
    for c in splits:
        cls = classify(c)
        c["filter_class"] = cls
        if cls.startswith("LEGIT"):
            legit.append(c)
        else:
            questionable.append(c)
    with open(os.path.join(PRIV, "reverse-splits-legit.json"), "w", encoding="utf-8") as f:
        json.dump(legit, f, ensure_ascii=False, indent=1)
    with open(os.path.join(PRIV, "reverse-splits-questionable.json"), "w", encoding="utf-8") as f:
        json.dump(questionable, f, ensure_ascii=False, indent=1)
    print(f"Total SPLITs: {len(splits)}")
    print(f"  LEGIT (apply):        {len(legit)}")
    print(f"  QUESTIONABLE (defer): {len(questionable)}")
    print(f"\nQuestionable M2-narrative-beat candidates deferred for tomorrow:")
    for c in questionable[:30]:
        print(f"  {c['book']:6s} {c['ref']:8s}  {c['line'][:90]}")
    if len(questionable) > 30:
        print(f"  ... and {len(questionable)-30} more")

if __name__ == "__main__":
    main()
