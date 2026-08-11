"""Full-corpus drift gate for the R10-collapse + is_stranded_neg refinement.
Regenerates every chapter with the in-tree (uncommitted) engine and diffs the
ATU line-structure against the deployed v1.5/grk files. Reports per-chapter the
verses whose line-partition changed. CRLF/blank-line normalized."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import sblgnt_v1_fabric as V1
import sblgnt_generate as G

DEPLOY = G.V4GRK


def norm(lines):
    """Drop blank lines; group cola under their verse marker -> {verse: [cola]}."""
    groups, cur = {}, None
    for ln in lines:
        s = ln.rstrip("\r\n")
        if not s.strip():
            continue
        if s[0].isdigit() and ":" in s.split()[0] and all(
                c.isdigit() or c == ":" for c in s.split()[0]) and len(s.split()) == 1:
            cur = s.strip()
            groups[cur] = []
        elif cur is not None:
            groups[cur].append(s.strip())
    return groups


total_chaps = changed_chaps = 0
changes = []
for book, num in V1.NUM.items():
    lowfat, morph, v0dir, slug, nn = V1.book_paths(num)
    for chap in V1.chapters_of(v0dir, slug):
        total_chaps += 1
        gen = norm(G.emit_v4(lowfat, morph, v0dir, slug, chap))
        dp = DEPLOY / f"{nn}-{slug}" / f"{slug}-{chap:02d}.txt"
        if not dp.exists():
            changes.append(f"{book} {chap}: NO DEPLOYED FILE")
            continue
        dep = norm(dp.read_text(encoding="utf-8").splitlines())
        ch = []
        for v in sorted(set(gen) | set(dep), key=lambda x: tuple(int(n) for n in x.split(":"))):
            if gen.get(v) != dep.get(v):
                ch.append(v)
        if ch:
            changed_chaps += 1
            changes.append(f"{book} {chap}: {', '.join(ch)}")

print(f"=== DRIFT GATE: {total_chaps} chapters, {changed_chaps} changed ===")
for c in changes:
    print(c)
