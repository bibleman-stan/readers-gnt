"""
run_all.py — Unified validator runner for the GNT Reader.

Discovers all validator modules in validators/syntax/ and validators/colometry/,
runs each against all 260 chapters, and reports per-rule candidate counts.

Modes:
    --output PATH         Write a consolidated markdown report (default mode if
                          --output is given). Required if no other mode flag.
    --summary             Print a per-rule candidate-count dashboard to stdout;
                          do not write a report. Exit 0 regardless of counts.
    --baseline-check      Compare current per-rule counts to validators/.baseline.json.
                          Exit 1 if any rule's count INCREASED vs baseline.
                          Used by validators/hooks/pre-commit.
    --update-baseline     Capture current per-rule counts as the new baseline at
                          validators/.baseline.json. Used after intentional changes.

Filters (apply to any mode):
    --books matt mark ...   Restrict to specific book slugs
    --validators R2 R18 ... Restrict to specific rule IDs
    --verbose               Print progress per chapter

Exit codes:
    0  All clean OR (default/summary) report only.
    1  Regressions detected (--baseline-check).
    2  Setup error.

Usage:
    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --summary
    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --baseline-check
    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --update-baseline
    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --output report.md
"""

import sys
import importlib
import pkgutil
import argparse
import json
import os
from collections import Counter
from pathlib import Path

BASELINE_PATH = Path(__file__).resolve().parent / ".baseline.json"

# ---------------------------------------------------------------------------
# Book/chapter table — 27 NT books, canonical project slugs
# ---------------------------------------------------------------------------
BOOKS = [
    ("matt", 28), ("mark", 16), ("luke", 24), ("john", 21), ("acts", 28),
    ("rom", 16), ("1cor", 16), ("2cor", 13), ("gal", 6), ("eph", 6),
    ("phil", 4), ("col", 4), ("1thess", 5), ("2thess", 3),
    ("1tim", 6), ("2tim", 4), ("titus", 3), ("phlm", 1),
    ("heb", 13), ("jas", 5), ("1pet", 5), ("2pet", 3),
    ("1john", 5), ("2john", 1), ("3john", 1), ("jude", 1), ("rev", 22),
]

# No default output path — callers must pass --output explicitly.
# Prior versions hardcoded a session-specific folder which went stale.

# ---------------------------------------------------------------------------
# Dynamic validator discovery
# ---------------------------------------------------------------------------

def discover_validators():
    """Import all check_* modules from validators/syntax/ and validators/colometry/.

    Each module must expose:
        RULE_ID     : str   (e.g. "R2")
        ERROR_CLASS : str   (e.g. "MALFORMED" | "DEVIATION")
        check_book_chapter(book: str, chapter: int) -> list[Candidate]

    Modules that fail to import are logged to stderr; the runner continues.
    """
    import validators.syntax
    import validators.colometry

    modules = []
    for pkg in [validators.syntax, validators.colometry]:
        for _loader, name, _ispkg in pkgutil.iter_modules(pkg.__path__):
            if not name.startswith("check_"):
                continue
            full_name = f"{pkg.__name__}.{name}"
            try:
                mod = importlib.import_module(full_name)
                modules.append(mod)
            except Exception as exc:
                print(f"  ! Could not import {full_name}: {exc}", file=sys.stderr)
    return modules


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def collect_candidates(books_filter=None, validators_filter=None, verbose=False):
    """Run all validators on all chapters and return (candidates, validators, total_chapters)."""
    from validators.common import Candidate  # noqa: F401 — built at runtime

    validators = discover_validators()
    if not validators:
        print("No validator modules found in validators/syntax/ or validators/colometry/.",
              file=sys.stderr)

    if validators_filter:
        validators = [v for v in validators if getattr(v, "RULE_ID", None) in validators_filter]

    all_candidates = []
    total_chapters = 0

    for book, nchapters in BOOKS:
        if books_filter and book not in books_filter:
            continue
        for chapter in range(1, nchapters + 1):
            total_chapters += 1
            if verbose:
                print(f"  checking {book} {chapter} …", file=sys.stderr)
            for v in validators:
                try:
                    cands = v.check_book_chapter(book, chapter)
                    all_candidates.extend(cands)
                except Exception as exc:
                    rule = getattr(v, "RULE_ID", repr(v))
                    print(f"  ! {rule} on {book} {chapter} raised: {exc}", file=sys.stderr)

    return all_candidates, validators, total_chapters


def counts_by_rule(candidates):
    """Return Counter mapping RULE_ID -> candidate count."""
    return Counter(c.rule for c in candidates)


def load_baseline():
    if not BASELINE_PATH.exists():
        return None
    try:
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[run_all] WARNING: {BASELINE_PATH} is invalid JSON; treating as missing.",
              file=sys.stderr)
        return None


def save_baseline(rule_counts):
    """Write rule_counts dict to baseline file."""
    data = dict(sorted(rule_counts.items()))
    BASELINE_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def diff_against_baseline(rule_counts, baseline):
    """Return [(rule, baseline_count, current_count)] for any rule whose count
    INCREASED vs baseline. Rules absent from baseline are treated as 0."""
    regressions = []
    for rule, cur in rule_counts.items():
        base = int(baseline.get(rule, 0))
        if cur > base:
            regressions.append((rule, base, cur))
    return regressions


def print_summary(rule_counts, validators, total_chapters):
    """Print per-rule dashboard to stdout."""
    print("=" * 60)
    print(f"GNT Validator Suite — {len(validators)} validators, {total_chapters} chapters")
    print("=" * 60)
    if not rule_counts:
        print("  (all clean — no candidates)")
        print()
        return
    by_layer = {"MALFORMED": 0, "DEVIATION": 0}
    for v in validators:
        rule = getattr(v, "RULE_ID", None)
        ec = getattr(v, "ERROR_CLASS", "DEVIATION")
        by_layer[ec] = by_layer.get(ec, 0) + rule_counts.get(rule, 0)
    name_width = max((len(r) for r in rule_counts), default=4) + 2
    print(f"  {'RULE':<{name_width}} CANDIDATES  ERROR_CLASS")
    print("  " + "-" * (name_width + 25))
    for v in sorted(validators, key=lambda v: getattr(v, "RULE_ID", "")):
        rule = getattr(v, "RULE_ID", None)
        ec = getattr(v, "ERROR_CLASS", "DEVIATION")
        if rule is None:
            continue
        n = rule_counts.get(rule, 0)
        marker = "" if n == 0 else "  *"
        print(f"  {rule:<{name_width}} {n:>10}  [{ec}]{marker}")
    print()
    print(f"  Layer 1 [MALFORMED] total: {by_layer.get('MALFORMED', 0)}")
    print(f"  Layer 3 [DEVIATION] total: {by_layer.get('DEVIATION', 0)}")
    print(f"  GRAND TOTAL candidates   : {sum(rule_counts.values())}")
    print()


def main(output_path=None, books_filter=None, validators_filter=None, verbose=False,
         baseline_check=False, update_baseline=False, summary=False):
    """Run all validators on all chapters and act per the chosen mode."""
    all_candidates, validators, total_chapters = collect_candidates(
        books_filter=books_filter,
        validators_filter=validators_filter,
        verbose=verbose,
    )
    rule_counts = counts_by_rule(all_candidates)

    # Mode dispatch
    if update_baseline:
        # Ensure every discovered validator's RULE_ID is recorded (zero count if no candidates)
        for v in validators:
            rule = getattr(v, "RULE_ID", None)
            if rule is not None:
                rule_counts.setdefault(rule, 0)
        save_baseline(rule_counts)
        print_summary(rule_counts, validators, total_chapters)
        print(f"  Baseline updated at {BASELINE_PATH}")
        print(f"  Captured counts for {len(rule_counts)} rules.")
        return 0

    if baseline_check:
        baseline = load_baseline()
        if baseline is None:
            print(
                "  No baseline at validators/.baseline.json. Run with --update-baseline\n"
                "  to create one. Treating absence as PASS.",
                file=sys.stderr,
            )
            return 0
        regressions = diff_against_baseline(rule_counts, baseline)
        if regressions:
            print_summary(rule_counts, validators, total_chapters)
            print("=" * 60, file=sys.stderr)
            print("REGRESSIONS DETECTED — candidate count INCREASED vs baseline:",
                  file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            for rule, base, cur in regressions:
                print(f"  {rule}: baseline={base} → current={cur}  (+{cur - base})",
                      file=sys.stderr)
            print(file=sys.stderr)
            print("Either fix the new violations or update the baseline:", file=sys.stderr)
            print("    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py --update-baseline",
                  file=sys.stderr)
            return 1
        print("  No regressions vs baseline.")
        return 0

    if summary:
        print_summary(rule_counts, validators, total_chapters)
        return 0

    # Default: write markdown report (requires --output)
    from validators.common import write_candidates

    if output_path is None:
        print("ERROR: --output PATH is required when no mode flag is given.\n"
              "       Use --summary, --baseline-check, --update-baseline, or pass --output.",
              file=sys.stderr)
        return 2

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    write_candidates(
        all_candidates,
        output_path,
        title="Layer 2 Validator Suite — Initial Run",
    )
    print(f"Wrote {len(all_candidates)} candidates across {len(validators)} validator(s) "
          f"({total_chapters} chapters checked) to {output_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser():
    p = argparse.ArgumentParser(
        description="Run all GNT validators and write a markdown report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--books",
        nargs="+",
        metavar="SLUG",
        help="Restrict to these book slugs (e.g. matt mark luke).",
    )
    p.add_argument(
        "--validators",
        nargs="+",
        metavar="RULE_ID",
        help="Restrict to these rule IDs (e.g. R2 R18).",
    )
    p.add_argument(
        "--output",
        metavar="PATH",
        help="Output file path. Required when no mode flag is given.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print per-rule candidate-count dashboard to stdout. Exit 0.",
    )
    p.add_argument(
        "--baseline-check",
        action="store_true",
        help="Compare current counts to validators/.baseline.json; exit 1 on regression.",
    )
    p.add_argument(
        "--update-baseline",
        action="store_true",
        help="Capture current counts as the new baseline.",
    )
    p.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress per chapter.",
    )
    return p


if __name__ == "__main__":
    # Ensure the repo root is on sys.path so `validators.*` imports resolve
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)

    args = _build_parser().parse_args()
    sys.exit(main(
        output_path=args.output,
        books_filter=args.books,
        validators_filter=args.validators,
        verbose=args.verbose,
        baseline_check=args.baseline_check,
        update_baseline=args.update_baseline,
        summary=args.summary,
    ) or 0)
