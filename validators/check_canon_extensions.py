#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_canon_extensions.py — content-aware canon-diff gate for commit-msg hook.

Detects canon extensions matching §6.5 mandatory-audit triggers in staged
canon diffs and blocks commits that introduce them without audit evidence in
the commit message.

Closes the gap that the regression-baseline pre-commit hook can't catch:
new closed-list additions, new rule sections, new merge-overrides, new audit
triggers, etc., that don't increase any existing rule's candidate count and
would otherwise slip through.

Files watched:
  - private/01-method/colometry-canon.md
  - data/syntax-reference/greek-break-legality.md

This script:
  1. Reads staged diffs of the watched files.
  2. Detects canon-extension patterns in the additions.
  3. Checks the proposed commit message (passed as argv[1]) for audit-evidence
     keywords or skip-safe claims.
  4. Exits 0 if no extension OR extension + audit-evidence/skip-safe present.
  5. Exits 1 if extension detected without audit-evidence or skip-safe.

Override (Stan-only, explicit decision):
    git commit --no-verify -m '...'

Usage (called from commit-msg hook):
    python3 validators/check_canon_extensions.py <commit-msg-file>

Ported from sibling readers-tanakh/validators/check_canon_extensions.py
2026-04-26, with GNT-specific adaptations:
  - Watched files extended to include Layer 1 syntax-reference table.
  - NEW_RULE_RE matches GNT §3.X subsection numbering ("### 3.18 ...").
  - NEW_DATED_PRINCIPLE_RE loosened (Tanakh required literal "(added DATE)";
    GNT detects any new ### heading whose text doesn't look like a §10 dated
    update-log entry, broadening recall at the cost of more false-positives
    that the skip-safe claim can clear).
  - Audit-evidence keywords use GNT §-numbers (§6.5 trigger list, §10 update
    log) instead of BofM/Tanakh §7/§8.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CANON_FILES = [
    "private/01-method/colometry-canon.md",
    "data/syntax-reference/greek-break-legality.md",
]

# ---------------------------------------------------------------------------
# Canon-extension patterns (anchored to lines added by the diff)
# ---------------------------------------------------------------------------

# (a) New rule subsection: "### 3.1 The No-Anchor Rule", "### 3.18 New Rule"
NEW_RULE_RE = re.compile(r"^### \d+\.\d+\b")

# (b) New merge-override: "#### M5. ..." (M1-M4 already settled)
NEW_MERGE_OVERRIDE_RE = re.compile(r"^#### M\d+\.")

# (c) New ### heading that is NOT a §10 dated update-log entry.
#     §10 entries look like "### 2026-04-25 — Title" or
#     "### 2026-04-25 (later⁵) — Title"; those are routine update-log
#     additions and not themselves triggers.
NEW_HEADING_RE = re.compile(r"^### [^0-9].+$")  # any ### heading not starting with a digit

# (d) New §6.5-style trigger entry: numbered bold-titled trigger.
#     Loosened from Tanakh's pattern (which required em-dash after the bold);
#     em-dash placement varies (inside bold vs. after) so we match any
#     numbered bold-titled entry.
NEW_TRIGGER_ENTRY_RE = re.compile(r"^\s*\d+\.\s+\*\*[A-Z]")

# (e) New SCOPE-exclusion / scope bullet under a rule.
#     Same loosening reason as (d).
NEW_SCOPE_EXCLUSION_RE = re.compile(r"^-\s+\*\*[A-Z]")

# (f) New Layer 1 table row in greek-break-legality.md
#     Format: | `signature` | LEGALITY | Grammar ref | Brief note |
LAYER_1_TABLE_ROW_RE = re.compile(
    r"^\|.*REQUIRED-(MERGE|BREAK)|PERMITTED-EITHER"
)

# ---------------------------------------------------------------------------
# Commit-message gate keywords
# ---------------------------------------------------------------------------

# Audit-evidence keywords — at least one must appear if extension detected.
AUDIT_KEYWORDS = [
    "audit",
    "hostile audit",
    "audit dispatched",
    "audit-dispatched",
    "trigger #",
    "§6.5",
    "§10 update log",
    "§10 entry",
    "update log",
    "retract",
    "retracted",
    "post-codification",
    "post-detection",
    "corpus-fit",
    "stan-authorized",
    "stan-direct",
]

# Skip-safe signals — explicit non-extension claims (typo, formatting, ...)
SKIP_SAFE_KEYWORDS = [
    "typo fix",
    "typo",
    "formatting",
    "internal formatting",
    "defensibility-capture",
    "defensibility capture",
    "cross-reference update",
    "cross-ref update",
    "audit-skippable",
    "skip-safe",
]


def get_canon_diff() -> str:
    """Return unified=0 diff of staged changes to any of the watched canon files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"] + CANON_FILES,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout
    except Exception:
        return ""


def detect_extensions(diff: str) -> list[tuple[str, str]]:
    """Return list of (trigger-name, matched-line) tuples found in the
    additions of the diff."""
    indicators: list[tuple[str, str]] = []
    for line in diff.split("\n"):
        if not line.startswith("+") or line.startswith("+++"):
            continue
        body = line[1:].rstrip()
        if not body.strip():
            continue
        if NEW_RULE_RE.match(body):
            indicators.append(("new-rule-subsection", body[:80]))
        if NEW_MERGE_OVERRIDE_RE.match(body):
            indicators.append(("new-merge-override", body[:80]))
        if NEW_HEADING_RE.match(body):
            # Filter out §10 dated update-log entries (those start with a digit
            # so they wouldn't match NEW_HEADING_RE — but the broader-recall
            # NEW_HEADING_RE catches non-§10 new headings)
            indicators.append(("new-heading", body[:80]))
        if NEW_TRIGGER_ENTRY_RE.match(body):
            indicators.append(("new-trigger-entry", body[:80]))
        if NEW_SCOPE_EXCLUSION_RE.match(body):
            indicators.append(("new-scope-exclusion", body[:80]))
        if LAYER_1_TABLE_ROW_RE.search(body):
            indicators.append(("layer-1-table-row", body[:80]))
    return indicators


def has_audit_evidence(message: str) -> bool:
    msg_lower = message.lower()
    return any(k in msg_lower for k in AUDIT_KEYWORDS)


def has_skip_safe_claim(message: str) -> bool:
    msg_lower = message.lower()
    return any(k in msg_lower for k in SKIP_SAFE_KEYWORDS)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check_canon_extensions.py <commit-msg-file>", file=sys.stderr)
        return 0  # don't block on usage errors

    msg_path = Path(sys.argv[1])
    if not msg_path.exists():
        return 0
    message = msg_path.read_text(encoding="utf-8", errors="replace")

    # Skip empty, merge, and squash messages
    if (
        not message.strip()
        or message.startswith("Merge ")
        or message.startswith("Squashed ")
    ):
        return 0

    diff = get_canon_diff()
    if not diff:
        return 0  # no canon changes staged

    indicators = detect_extensions(diff)
    if not indicators:
        return 0  # no extension detected

    if has_audit_evidence(message):
        print(
            f"[canon-extension-check] Detected {len(indicators)} extension "
            f"indicator(s); audit evidence found in commit message. PASS."
        )
        return 0

    if has_skip_safe_claim(message):
        print(
            f"[canon-extension-check] Detected {len(indicators)} extension "
            f"indicator(s); commit claims skip-safe. Allowing — verify the "
            f"claim is accurate."
        )
        return 0

    # Extension detected, no audit evidence, no skip-safe claim → BLOCK
    print()
    print("=" * 72, file=sys.stderr)
    print("CANON EXTENSION DETECTED — AUDIT EVIDENCE REQUIRED", file=sys.stderr)
    print("=" * 72, file=sys.stderr)
    print(file=sys.stderr)
    print(
        "Per canon §6.5 mandatory-audit triggers, this commit introduces canon\n"
        "extensions that require an adversarial audit before landing.",
        file=sys.stderr,
    )
    print(file=sys.stderr)
    print("Detected extension indicators:", file=sys.stderr)
    for trigger, line in indicators[:10]:
        print(f"  [{trigger}] {line}", file=sys.stderr)
    if len(indicators) > 10:
        print(f"  ... and {len(indicators) - 10} more", file=sys.stderr)
    print(file=sys.stderr)
    print("To proceed, the commit message MUST contain ONE of:", file=sys.stderr)
    print(
        "  - An audit-evidence keyword (e.g., 'audit', 'hostile audit',\n"
        "    'audit dispatched', 'trigger #', '§6.5', '§10 update log',\n"
        "    'post-codification', 'post-detection').",
        file=sys.stderr,
    )
    print(
        "  - A skip-safe claim (e.g., 'typo fix', 'cross-reference update',\n"
        "    'defensibility-capture', 'audit-skippable', 'internal formatting')\n"
        "    if the change qualifies under §6.5's audit-skippable categories.",
        file=sys.stderr,
    )
    print(
        "  - 'stan-authorized' or 'stan-direct' if Stan explicitly directed\n"
        "    the change without audit (rare).",
        file=sys.stderr,
    )
    print(file=sys.stderr)
    print("To bypass entirely (Stan-only, explicit decision):", file=sys.stderr)
    print("    git commit --no-verify -m '...'", file=sys.stderr)
    print(file=sys.stderr)
    print(
        "Reformulate the commit message OR run the audit and document its\n"
        "verdict in the message before retrying.",
        file=sys.stderr,
    )
    print("=" * 72, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
