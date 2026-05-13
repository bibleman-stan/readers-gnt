"""
scan_eng_kjv_coverage.py — verify eng-kjv has English content for every
Greek content line in v4/grk.

Closes a coverage-gap blind spot that the two-check cascade
(verify_word_order + scan_english_drift) misses: `verify_word_order`
compares v4/grk against sblgnt-source (Greek-only), and
`scan_english_drift` checks for translation quality on English lines
that EXIST — neither flags the case where eng-kjv has a blank line
where v4/grk has Greek content.

This blind spot caused the bracket-pericope bug (commit 7f3c361c): the
SBL-only TAGNT filter dropped every token of Mark 16:9-20 and John
7:53-8:11, leaving entire pericopes blank in eng-kjv — and the cascade
discipline said "verify clean" because it never read eng-kjv.

Run as:
  py -3 scripts/scan_eng_kjv_coverage.py
  py -3 scripts/scan_eng_kjv_coverage.py --baseline-check
  py -3 scripts/scan_eng_kjv_coverage.py --update-baseline

Baseline lives at data/eng-kjv-coverage.baseline.json — a sorted list
of [book_slug, verse_ref, line_idx] tuples that are KNOWN to be blank
(typically because SBLGNT-vs-KJV verse-boundary differences leave some
Greek lines with no KJV counterpart). --baseline-check fails if any
NEW blank lines have appeared that aren't in the baseline.
"""

import argparse
import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
V4_GRK = REPO_ROOT / "data" / "text-files" / "v4" / "grk"
V4_ENG = REPO_ROOT / "data" / "text-files" / "v4" / "eng-kjv"
BASELINE_PATH = REPO_ROOT / "data" / "eng-kjv-coverage.baseline.json"

_RE_VERSE = re.compile(r"^(\d+):(\d+)\s*$")


def parse_chapter(path: Path) -> list[tuple[str, list[str]]]:
    """Return [(verse_ref, [raw_lines]), ...] preserving order.

    Trailing blank lines within each verse block are KEPT (not stripped).
    A subsequent v4-grk vs eng-kjv line-index comparison expects them to
    align positionally.
    """
    out: list[tuple[str, list[str]]] = []
    cur_ref: str | None = None
    cur_lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _RE_VERSE.match(line)
        if m:
            if cur_ref is not None:
                out.append((cur_ref, cur_lines))
            cur_ref = f"{m.group(1)}:{m.group(2)}"
            cur_lines = []
        else:
            if cur_ref is not None:
                cur_lines.append(line)
    if cur_ref is not None:
        out.append((cur_ref, cur_lines))
    # Strip trailing blanks from each verse's line list (the eng-kjv format
    # uses blank line as separator between verses; trailing blanks within
    # a verse are just separator artifacts).
    return [(ref, _rstrip_blanks(lines)) for ref, lines in out]


def _rstrip_blanks(lines: list[str]) -> list[str]:
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    return out


def scan_corpus() -> list[tuple[str, str, int, str]]:
    """Walk v4/grk + v4/eng-kjv, return list of coverage misses.

    Each tuple: (book_slug, verse_ref, line_idx, grk_excerpt).
    A "miss" is a v4/grk line with non-blank Greek content where the
    eng-kjv counterpart line is blank or missing.
    """
    misses: list[tuple[str, str, int, str]] = []
    for grk_dir in sorted(V4_GRK.iterdir()):
        if not grk_dir.is_dir():
            continue
        eng_dir = V4_ENG / grk_dir.name
        for grk_file in sorted(grk_dir.glob("*.txt")):
            book_slug = grk_file.stem  # e.g. "matt-21"
            eng_file = eng_dir / grk_file.name
            if not eng_file.exists():
                continue
            grk_verses = dict(parse_chapter(grk_file))
            eng_verses = dict(parse_chapter(eng_file))
            for ref, grk_lines in grk_verses.items():
                eng_lines = eng_verses.get(ref, [])
                for i, gl in enumerate(grk_lines):
                    if not gl.strip():
                        continue
                    eng_line = eng_lines[i] if i < len(eng_lines) else ""
                    if not eng_line.strip():
                        misses.append((book_slug, ref, i, gl[:60]))
    return sorted(misses)


def load_baseline() -> set[tuple[str, str, int]]:
    if not BASELINE_PATH.exists():
        return set()
    raw = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {(e["book"], e["ref"], e["line_idx"]) for e in raw.get("misses", [])}


def write_baseline(misses: list[tuple[str, str, int, str]]) -> None:
    payload = {
        "_note": (
            "Known coverage misses: v4/grk lines with Greek content "
            "whose eng-kjv counterpart is blank. Each represents an "
            "SBLGNT-vs-KJV verse-boundary mismatch or other structural "
            "case the alignment cannot resolve. Run "
            "scripts/scan_eng_kjv_coverage.py --update-baseline after "
            "intentional structural changes."
        ),
        "misses": [
            {"book": b, "ref": r, "line_idx": i, "grk_excerpt": g}
            for b, r, i, g in misses
        ],
    }
    BASELINE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument(
        "--baseline-check", action="store_true",
        help="Fail with exit code 1 if any NEW coverage misses have "
             "appeared that aren't in the baseline.",
    )
    p.add_argument(
        "--update-baseline", action="store_true",
        help="Overwrite the baseline file with current coverage misses.",
    )
    args = p.parse_args(argv)

    misses = scan_corpus()
    print(f"Coverage misses: {len(misses)} v4/grk content lines have "
          f"blank eng-kjv counterparts")

    if args.update_baseline:
        write_baseline(misses)
        print(f"Wrote baseline: {BASELINE_PATH.relative_to(REPO_ROOT)}")
        return 0

    if args.baseline_check:
        baseline = load_baseline()
        current = {(b, r, i) for b, r, i, _ in misses}
        new = sorted(current - baseline)
        resolved = sorted(baseline - current)
        if new:
            print(f"\nFAIL: {len(new)} new coverage miss(es) vs baseline:")
            for b, r, i in new[:20]:
                print(f"  {b}.txt {r} line {i}")
            if len(new) > 20:
                print(f"  ... and {len(new) - 20} more")
            print(
                "\nEither (a) fix the alignment so these v4/grk lines "
                "produce English, or (b) update the baseline if the "
                "increase is intentional:\n"
                "      PYTHONIOENCODING=utf-8 py -3 "
                "scripts/scan_eng_kjv_coverage.py --update-baseline"
            )
            return 1
        if resolved:
            print(f"\nNote: {len(resolved)} baseline entry now resolved "
                  f"(consider --update-baseline to shrink baseline).")
        print("OK: no new coverage misses vs baseline.")
        return 0

    # Default: print summary + first 30
    for b, r, i, g in misses[:30]:
        print(f"  {b}.txt {r} line {i}: {g}")
    if len(misses) > 30:
        print(f"  ... and {len(misses) - 30} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
