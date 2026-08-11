#!/usr/bin/env python3
"""Dev scan: every hoti-ground the new BIND_GROUND decision binds backward
(short anaphoric causal ground -> merged into its blessing/main clause). For the
over-merge review before deploy."""
from collections import Counter
import macula_hoti as mh

BOOKS = [f"{i:02d}" for i in range(1, 28)]
fired = []
for nn in BOOKS:
    try:
        dec = mh.decisions(nn)
    except StopIteration:
        continue
    for (c, v, wi), d in dec.items():
        if d == "BIND_GROUND":
            fired.append((nn, c, v))

print(f"BIND_GROUND fires on {len(fired)} hoti-grounds corpus-wide")
print("by book:", dict(Counter(nn for nn, _, _ in fired)))
for nn, c, v in fired:
    print(f"  {nn} {c}:{v}")
