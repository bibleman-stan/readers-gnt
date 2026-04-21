"""
run_all.py — Unified validator runner for the GNT Reader.

Discovers all validator modules in validators/syntax/ and validators/colometry/,
runs each against all 260 chapters, and writes a consolidated markdown report.

Usage:
    PYTHONIOENCODING=utf-8 py -3 validators/run_all.py [options]

Options:
    --books matt mark ...   Restrict to specific book slugs
    --validators R2 R18 ... Restrict to specific rule IDs
    --output PATH           Output file (default: dated session file)
    --verbose               Print progress per chapter
"""

import sys
import importlib
import pkgutil
import argparse
import os

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

def main(output_path=None, books_filter=None, validators_filter=None, verbose=False):
    """Run all validators on all chapters and write a markdown report.

    Args:
        output_path:       Where to write the report (default: DEFAULT_OUTPUT).
        books_filter:      Optional list of book slugs to restrict to.
        validators_filter: Optional list of rule IDs (e.g. ["R2", "R18"]).
        verbose:           If True, print progress per chapter.
    """
    from validators.common import Candidate, write_candidates  # noqa: F401 — built at runtime

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

    if output_path is None:
        print(
            "ERROR: --output PATH is required (no default output path).",
            file=sys.stderr,
        )
        sys.exit(2)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    write_candidates(
        all_candidates,
        output_path,
        title="Layer 2 Validator Suite — Initial Run",
    )
    print(
        f"Wrote {len(all_candidates)} candidates across {len(validators)} validator(s) "
        f"({total_chapters} chapters checked) to {output_path}"
    )


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
        help="Output file path (default: dated session file).",
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
    main(
        output_path=args.output,
        books_filter=args.books,
        validators_filter=args.validators,
        verbose=args.verbose,
    )
