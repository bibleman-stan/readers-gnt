"""Deploy regen: regenerate ALL v1.5/grk chapters from the current engine into the
DEPLOYED path (V4GRK). autocrlf=true normalizes line endings; only content-changed
chapters surface in git diff."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import sblgnt_v1_fabric as V1
import sblgnt_generate as G

n = 0
for book, num in V1.NUM.items():
    lowfat, morph, v0dir, slug, nn = V1.book_paths(num)
    for chap in V1.chapters_of(v0dir, slug):
        lines = G.emit_v4(lowfat, morph, v0dir, slug, chap)
        d = G.V4GRK / f"{nn}-{slug}"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}-{chap:02d}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        n += 1
print(f"regenerated {n} chapters into v1.5/grk")
