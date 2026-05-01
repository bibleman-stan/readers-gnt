#!/usr/bin/env python3
"""
scan_emdash_midline.py — RETIRED (Canon §1 Step 0 violation).

RETIREMENT RATIONALE
--------------------
The original script framed SBLGNT editorial em-dashes as positive break
warrants ("such boundaries are almost always compositional break points
that our colometric layout should honor"). This violates Canon §1 Step 0
item 1: editorial punctuation is NEVER the warrant for a break decision.
The dash is an editorial overlay from the SBL edition's critical judgment,
not a grammatical signal from the Greek itself.

The script as written would emit split candidates where the punctuation IS
the candidate with no grammatical confirmation required — exactly the
pattern Step 0 closes off.

CORRECT APPROACH (if this scanner is ever revived)
---------------------------------------------------
An em-dash in the SBLGNT corpus is a *locator*, not a signal. If a scan
for parenthetical structures is desired, the warrant must be grammatical:
detect a participial phrase, appositive, or embedded clause bracketed by
the dashes via MorphGNT case/POS analysis, and use the em-dash only to
narrow the search window. The signal is the grammar; the em-dash is the
pointer.

This would require substantial new morphological infrastructure (cf.
validators/_shared/morphgnt_lookup.py). Until that infrastructure is in
place and the locator/warrant distinction is cleanly implemented, this
scanner must remain retired.

Logged: Canon §10 update trail — audit C3 (2026-04-29).

Usage:
    This script intentionally raises NotImplementedError when run.
"""


def main():
    raise NotImplementedError(
        "scan_emdash_midline.py is retired — see module docstring for rationale.\n"
        "Em-dash positions are editorial punctuation (Canon §1 Step 0 item 1) "
        "and may not serve as break warrants without a separate grammatical "
        "confirmation gate."
    )


if __name__ == "__main__":
    main()
