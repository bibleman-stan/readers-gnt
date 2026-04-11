#!/usr/bin/env python3
"""
v4 Editorial Review for Pauline Epistles
Applies the four criteria + sub-principles from 02-colometry-method.md
to all 87 Pauline epistle chapters.

Only writes v4 files for chapters that actually change.
"""

import os
import re
import sys
import copy

V3_DIR = r"c:\Users\bibleman\repos\readers-gnt\data\text-files\v3-colometric"
V4_DIR = r"c:\Users\bibleman\repos\readers-gnt\data\text-files\v4-editorial"

# All Pauline epistle files
PAULINE_FILES = []
BOOKS = {
    "rom": 16, "1cor": 16, "2cor": 13, "gal": 6, "eph": 6, "phil": 4,
    "col": 4, "1thess": 5, "2thess": 3, "1tim": 6, "2tim": 4, "titus": 3, "phlm": 1
}
for book, chapters in BOOKS.items():
    for ch in range(1, chapters + 1):
        PAULINE_FILES.append(f"{book}-{ch:02d}.txt")


def parse_file(filepath):
    """Parse a v3 file into a list of verse blocks.
    Each block is (verse_ref, [lines]).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = []
    current_ref = None
    current_lines = []

    for line in content.split("\n"):
        line = line.rstrip()
        # Verse reference line (e.g., "8:1")
        if re.match(r'^\d+:\d+$', line.strip()):
            if current_ref is not None:
                blocks.append((current_ref, current_lines))
            current_ref = line.strip()
            current_lines = []
        elif line.strip() == "":
            continue
        else:
            current_lines.append(line)

    if current_ref is not None:
        blocks.append((current_ref, current_lines))

    return blocks


def blocks_to_text(blocks):
    """Convert blocks back to file text."""
    lines = []
    for ref, content_lines in blocks:
        lines.append(ref)
        for cl in content_lines:
            lines.append(cl)
        lines.append("")
    return "\n".join(lines) + "\n"


def apply_v4_fixes(blocks, filename):
    """Apply all v4 editorial fixes to a list of blocks.
    Returns (new_blocks, changes_list).
    """
    changes = []
    new_blocks = []

    for ref, orig_lines in blocks:
        fixed_lines = list(orig_lines)

        # === FIX 1: Dangling fragments — merge lines that are just 1-2 words
        # and not imperatives/vocatives onto neighbors ===
        fixed_lines = fix_dangling_fragments(ref, fixed_lines, changes)

        # === FIX 2: Split overly long lines that contain multiple clauses ===
        fixed_lines = fix_long_lines(ref, fixed_lines, changes)

        # === FIX 3: Parallel stacking for catalog lists ===
        fixed_lines = fix_parallel_stacking(ref, fixed_lines, changes)

        # === FIX 4: μέν/δέ contrast stacking ===
        fixed_lines = fix_men_de_stacking(ref, fixed_lines, changes)

        # === FIX 5: Dangling conjunctions at line end ===
        fixed_lines = fix_dangling_conjunctions(ref, fixed_lines, changes)

        # === FIX 6: Dangling articles at line end ===
        fixed_lines = fix_dangling_articles(ref, fixed_lines, changes)

        # === FIX 7: εἰ μή restriction merges ===
        fixed_lines = fix_ei_me_restriction(ref, fixed_lines, changes)

        # === FIX 8: Stranded temporal/discourse adverbs ===
        fixed_lines = fix_stranded_adverbs(ref, fixed_lines, changes)

        # === FIX 9: Speech intro separation ===
        fixed_lines = fix_speech_intros(ref, fixed_lines, changes)

        # === FIX 10: πολλῷ μᾶλλον escalation ===
        fixed_lines = fix_escalation(ref, fixed_lines, changes)

        new_blocks.append((ref, fixed_lines))

    return new_blocks, changes


def fix_dangling_fragments(ref, lines, changes):
    """Merge fragment lines (1-3 short words, no verb) into neighbors."""
    if len(lines) <= 1:
        return lines

    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        words = line.split()

        # Check if this is a stranded fragment that should merge
        # But preserve legitimate short lines: imperatives, vocatives, etc.
        if (len(words) <= 2 and len(line) < 20 and
            not is_imperative_or_vocative(line) and
            not re.match(r'^\d+:\d+$', line) and
            not is_standalone_predication(line) and
            not is_parallel_element(line)):

            # Check specific patterns that are legitimately short
            # e.g., "θανάτου δὲ σταυροῦ" - escalation, keep separate
            if is_escalation_phrase(line):
                result.append(lines[i])
                i += 1
                continue

            # Merge with previous line if possible
            if result and not line.startswith(('ἀλλ', 'ἵνα', 'ὅτι', 'ὥστε', 'ὅταν', 'ὅτε', 'εἰ ', 'ἐάν', 'γάρ', 'οὖν', 'διό')):
                old_prev = result[-1]
                result[-1] = result[-1].rstrip() + " " + line
                changes.append(f"  {ref}: merged fragment '{line}' into previous line")
            elif i + 1 < len(lines):
                # Merge forward
                old_next = lines[i + 1]
                lines[i + 1] = line + " " + lines[i + 1].lstrip()
                changes.append(f"  {ref}: merged fragment '{line}' into next line")
            else:
                result.append(lines[i])
            i += 1
        else:
            result.append(lines[i])
            i += 1

    return result


def fix_long_lines(ref, lines, changes):
    """Split lines >100 chars that contain natural break points."""
    result = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 100:
            split = try_split_long_line(stripped)
            if split and len(split) > 1:
                changes.append(f"  {ref}: split long line ({len(stripped)} chars) into {len(split)} lines")
                result.extend(split)
            else:
                result.append(line)
        else:
            result.append(line)
    return result


def try_split_long_line(line):
    """Try to find a good split point in a long line."""
    # Priority split points (in order)
    split_patterns = [
        # Subordinating conjunctions
        r'(?<=\S)\s+(ἵνα\s)',
        r'(?<=\S)\s+(ὥστε\s)',
        r'(?<=\S)\s+(ὅτι\s)',
        r'(?<=\S)\s+(ὅταν\s)',
        r'(?<=\S)\s+(ὅτε\s)',
        r'(?<=\S)\s+(ἐάν\s)',
        r'(?<=\S)\s+(μήποτε\s)',
        r'(?<=\S)\s+(καθὼς\s)',
        r'(?<=\S)\s+(διότι\s)',
        r'(?<=\S)\s+(ἐπειδὴ\s)',
        # Discourse markers
        r'(?<=\S)\s+(ἀλλὰ\s)',
        r'(?<=\S)\s+(ἀλλʼ\s)',
        # καί + new clause (after comma or semicolon context)
        r'(?<=,)\s+(καὶ\s)',
        r'(?<=·)\s+(καὶ\s)',
        # Relative clauses
        r'(?<=,)\s+(ὃ[ςνἥ]\s)',
        r'(?<=,)\s+(ἥτις\s)',
        # Participial phrases (common Pauline)
        r'(?<=,)\s+(\w+(?:μενο[ςιν]|σαντ[εο]ς|θε[ίὶ]ς|ων)\s)',
    ]

    for pattern in split_patterns:
        m = re.search(pattern, line)
        if m:
            pos = m.start(1)
            first = line[:pos].rstrip()
            second = line[pos:].lstrip()
            if len(first) > 15 and len(second) > 15:
                return [first, second]

    # Try splitting at a comma near the middle
    mid = len(line) // 2
    best_comma = -1
    best_dist = len(line)
    for m in re.finditer(r',\s', line):
        dist = abs(m.start() - mid)
        if dist < best_dist and m.start() > 20 and m.start() < len(line) - 20:
            best_dist = dist
            best_comma = m.end()

    if best_comma > 0:
        first = line[:best_comma].rstrip()
        second = line[best_comma:].lstrip()
        if len(first) > 15 and len(second) > 15:
            return [first, second]

    return None


def fix_parallel_stacking(ref, lines, changes):
    """Stack parallel structures vertically (οὔτε...οὔτε, εἴτε...εἴτε, etc.)."""
    result = []
    for line in lines:
        stripped = line.strip()

        # οὔτε catalog lists (e.g., Rom 8:38-39)
        oute_count = stripped.count('οὔτε')
        if oute_count >= 3:
            parts = split_parallel_list(stripped, 'οὔτε')
            if parts:
                changes.append(f"  {ref}: stacked {oute_count} οὔτε parallel elements")
                result.extend(parts)
                continue

        # εἴτε lists (e.g., 1 Cor 13:8, Col 1:16)
        eite_count = stripped.count('εἴτε')
        if eite_count >= 3:
            parts = split_parallel_list(stripped, 'εἴτε')
            if parts:
                changes.append(f"  {ref}: stacked {eite_count} εἴτε parallel elements")
                result.extend(parts)
                continue

        # ἤ catalog lists (e.g., Rom 8:35 — θλῖψις ἢ στενοχωρία ἢ ...)
        e_count = len(re.findall(r'\bἢ\b', stripped))
        if e_count >= 4:
            parts = split_e_list(stripped)
            if parts:
                changes.append(f"  {ref}: stacked {e_count + 1} ἤ catalog elements")
                result.extend(parts)
                continue

        # πάντα parallel (1 Cor 13:7)
        panta_count = stripped.count('πάντα ')
        if panta_count >= 3 and len(stripped) > 50:
            parts = split_panta_parallel(stripped)
            if parts:
                changes.append(f"  {ref}: stacked {panta_count} πάντα parallel elements")
                result.extend(parts)
                continue

        # Triple καί + noun lists (stacking subject/object lists)
        # Only for clearly parallel noun phrases

        result.append(line)

    return result


def split_parallel_list(line, marker):
    """Split a parallel list at marker boundaries."""
    # Find all occurrences of the marker
    parts = []
    # Split the line keeping the marker with its content
    segments = re.split(f'(?={marker})', line)

    # The first segment might be a frame (e.g., "πέπεισμαι γὰρ ὅτι")
    result = []
    for seg in segments:
        seg = seg.strip()
        if seg:
            result.append(seg)

    if len(result) >= 3:
        return result
    return None


def split_e_list(line):
    """Split an ἤ catalog list, keeping the question frame separate."""
    # Pattern: "question? item1 ἢ item2 ἢ item3..."
    # Or just: "item1 ἢ item2 ἢ item3..."

    # Check if there's a question before the list
    q_match = re.match(r'^(.+;\s*)', line)
    frame = ""
    rest = line
    if q_match:
        # Check if the question mark is a Greek semicolon (;)
        frame = q_match.group(1).strip()
        rest = line[q_match.end():].strip()
    elif '?' in line:
        q_pos = line.index('?')
        frame = line[:q_pos+1].strip()
        rest = line[q_pos+1:].strip()

    if not rest:
        rest = line
        frame = ""

    items = re.split(r'\s+ἢ\s+', rest)
    if len(items) < 3:
        return None

    result = []
    if frame:
        result.append(frame)

    for i, item in enumerate(items):
        if i == 0:
            result.append(item.strip())
        else:
            result.append("ἢ " + item.strip())

    return result if len(result) >= 3 else None


def split_panta_parallel(line):
    """Split πάντα parallel structure."""
    parts = re.split(r'(?=πάντα\s)', line)
    result = [p.strip().rstrip(',') for p in parts if p.strip()]
    return result if len(result) >= 3 else None


def fix_men_de_stacking(ref, lines, changes):
    """Ensure μέν/δέ contrasts are on separate lines."""
    result = []
    for line in lines:
        stripped = line.strip()

        # Pattern: "X μέν Y, Z δέ W" on one line
        men_match = re.search(r'^(.+\bμὲν\b.+),\s+(.+\bδὲ\b.+)$', stripped)
        if men_match:
            first = men_match.group(1).strip()
            second = men_match.group(2).strip()
            if len(first) > 10 and len(second) > 10:
                changes.append(f"  {ref}: split μέν/δέ contrast onto separate lines")
                result.append(first + ",")
                result.append(second)
                continue

        # Pattern: "κληρονόμοι μὲν θεοῦ, συγκληρονόμοι δὲ Χριστοῦ"
        men_de_match = re.search(r'^(.+\bμὲν\b[^,]+),\s+(.+\bδὲ\b.+)$', stripped)
        if men_de_match and 'μὲν' in stripped and 'δὲ' in stripped:
            first = men_de_match.group(1).strip()
            second = men_de_match.group(2).strip()
            if len(first) > 8 and len(second) > 8:
                changes.append(f"  {ref}: split μέν/δέ contrast onto separate lines")
                result.append(first + ",")
                result.append(second)
                continue

        result.append(line)

    return result


def fix_dangling_conjunctions(ref, lines, changes):
    """Fix conjunctions dangling at line end — they should lead their clause."""
    if len(lines) <= 1:
        return lines

    result = list(lines)
    i = 0
    while i < len(result) - 1:
        stripped = result[i].rstrip()
        # Check if line ends with a conjunction
        for conj in ['καὶ', 'δὲ', 'ἀλλὰ', 'ἀλλʼ', 'γὰρ', 'οὖν', 'τε', 'ἤ']:
            if stripped.endswith(' ' + conj):
                # Move conjunction to next line
                result[i] = stripped[:-len(conj)].rstrip()
                result[i + 1] = conj + ' ' + result[i + 1].lstrip()
                changes.append(f"  {ref}: moved dangling '{conj}' to lead next line")
                break
        i += 1

    # Remove any empty lines created
    result = [l for l in result if l.strip()]
    return result


def fix_dangling_articles(ref, lines, changes):
    """Fix articles dangling at line end."""
    if len(lines) <= 1:
        return lines

    result = list(lines)
    articles = ['τόν', 'τήν', 'τό', 'τοῦ', 'τῆς', 'τῷ', 'τῇ', 'τοὺς', 'τὰς', 'τά',
                 'τῶν', 'τοῖς', 'ταῖς', 'ὁ', 'ἡ', 'τὸ', 'οἱ', 'αἱ', 'τὰ']

    i = 0
    while i < len(result) - 1:
        stripped = result[i].rstrip()
        words = stripped.split()
        if words and words[-1] in articles:
            # Move article to next line
            art = words[-1]
            result[i] = ' '.join(words[:-1])
            result[i + 1] = art + ' ' + result[i + 1].lstrip()
            changes.append(f"  {ref}: moved dangling article '{art}' to next line")
        i += 1

    result = [l for l in result if l.strip()]
    return result


def fix_ei_me_restriction(ref, lines, changes):
    """Merge εἰ μή restriction phrases with preceding clause."""
    if len(lines) <= 1:
        return lines

    result = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('εἰ μὴ') and result and len(stripped) < 40:
            # Check if this is a restriction (not a conditional)
            # Short εἰ μή phrases are typically restrictions
            old_prev = result[-1]
            result[-1] = result[-1].rstrip() + " " + stripped
            changes.append(f"  {ref}: merged εἰ μή restriction into preceding line")
        else:
            result.append(lines[i])
        i += 1

    return result


def fix_stranded_adverbs(ref, lines, changes):
    """Fix stranded temporal adverbs (ἄρτι, τότε, νῦν) that need their clause."""
    if len(lines) <= 1:
        return lines

    result = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        # Check for standalone ἄρτι, τότε that should merge with next line
        if stripped in ('ἄρτι', 'τότε', 'νῦν', 'τότε δέ', 'νῦν δέ') and i + 1 < len(lines):
            # Merge with next line
            lines[i + 1] = stripped + " " + lines[i + 1].lstrip()
            changes.append(f"  {ref}: merged stranded '{stripped}' into next line")
        else:
            result.append(lines[i])
        i += 1

    return result


def fix_speech_intros(ref, lines, changes):
    """Ensure speech introductions are on their own line."""
    result = []
    speech_patterns = [
        r'^(.*(?:εἶπεν|ἔλεγεν|λέγει|ἔφη|λέγουσιν|εἶπαν|φησίν)\s+(?:αὐτ[οῷ]ῖς|πρὸς\s+αὐτ[οό]ν|πρὸς\s+αὐτ[οό]ύς)·)\s+(.+)',
        r'^(.*(?:εἶπεν|ἔλεγεν|λέγει|ἔφη|λέγουσιν|εἶπαν|φησίν)·)\s+(.+)',
    ]

    for line in lines:
        stripped = line.strip()
        split_done = False
        for pat in speech_patterns:
            m = re.match(pat, stripped)
            if m:
                intro = m.group(1).strip()
                speech = m.group(2).strip()
                if len(intro) > 5 and len(speech) > 5:
                    result.append(intro)
                    result.append(speech)
                    changes.append(f"  {ref}: separated speech intro from speech content")
                    split_done = True
                    break
        if not split_done:
            result.append(line)

    return result


def fix_escalation(ref, lines, changes):
    """Ensure πολλῷ μᾶλλον and μᾶλλον δέ get their own line when embedded."""
    result = []
    for line in lines:
        stripped = line.strip()

        # πολλῷ μᾶλλον embedded in a longer line
        match = re.search(r'(.{20,})\s+(πολλῷ μᾶλλον\s.+)', stripped)
        if match:
            result.append(match.group(1).rstrip())
            result.append(match.group(2).lstrip())
            changes.append(f"  {ref}: gave πολλῷ μᾶλλον its own line")
            continue

        result.append(line)

    return result


def is_imperative_or_vocative(line):
    """Check if a short line is a valid standalone imperative or vocative."""
    imperatives = ['Ἀκούετε', 'Σιώπα', 'πεφίμωσο', 'Μετανοεῖτε', 'Χαίρετε',
                   'Ἀμήν', 'Μαρανα θα', 'Ἀσπάσασθε']
    vocatives = ['ἀδελφοί', 'Ἄνδρες ἀδελφοί', 'ἀγαπητοί']

    stripped = line.strip().rstrip(',·;.')
    return stripped in imperatives or stripped in vocatives


def is_standalone_predication(line):
    """Check if a short line is a valid standalone predication."""
    stripped = line.strip()
    # Short lines that are valid: μᾶλλον δὲ ἐγερθείς, θανάτου δὲ σταυροῦ, etc.
    if 'δὲ' in stripped or 'δέ' in stripped:
        return True
    # Answers to rhetorical questions
    if stripped.endswith(';') or stripped.endswith('·'):
        return True
    return False


def is_escalation_phrase(line):
    """Check if a line is an escalation phrase that should stay separate."""
    stripped = line.strip()
    escalation_markers = ['θανάτου δὲ', 'πολλῷ μᾶλλον', 'μᾶλλον δὲ', 'ὑπὲρ ἐκ περισσοῦ']
    return any(m in stripped for m in escalation_markers)


def is_parallel_element(line):
    """Check if a line is a parallel list element that should stay separate."""
    stripped = line.strip()
    # Lines starting with parallel markers
    parallel_starts = ['ἢ ', 'οὔτε ', 'εἴτε ', 'μήτε ', 'πάντα ', 'καὶ ἐπ', 'ἐπ']
    for start in parallel_starts:
        if stripped.startswith(start):
            return True
    # Single-word cosmic realm terms
    if stripped.rstrip(',;·.') in ('ἐπουρανίων', 'ἐπιγείων', 'καταχθονίων'):
        return True
    # οὐ + verb patterns (love chapter parallel attributes)
    if re.match(r'^οὐ[κχ]?\s+\w+', stripped) and len(stripped) < 35:
        return True
    return False


# ============================================================
# SPECIAL CHAPTER HANDLERS for known important passages
# ============================================================

def handle_rom_08(blocks):
    """Special handling for Romans 8 — key theological chapter."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)

        # 8:9 — Fix the broken line split "εἰ δέ τις / πνεῦμα Χριστοῦ οὐκ ἔχει, οὗτος / οὐκ ἔστιν αὐτοῦ."
        if ref == "8:9":
            new_lines = [
                "Ὑμεῖς δὲ οὐκ ἐστὲ ἐν σαρκὶ ἀλλὰ ἐν πνεύματι,",
                "εἴπερ πνεῦμα θεοῦ οἰκεῖ ἐν ὑμῖν.",
                "εἰ δέ τις πνεῦμα Χριστοῦ οὐκ ἔχει,",
                "οὗτος οὐκ ἔστιν αὐτοῦ."
            ]
            changes.append("  8:9: restructured conditional — protasis/apodosis on proper lines")

        # 8:11 — Break long periodic sentence
        if ref == "8:11":
            new_lines = [
                "εἰ δὲ τὸ πνεῦμα τοῦ ἐγείραντος τὸν Ἰησοῦν ἐκ νεκρῶν οἰκεῖ ἐν ὑμῖν,",
                "ὁ ἐγείρας ἐκ νεκρῶν Χριστὸν Ἰησοῦν",
                "ζῳοποιήσει καὶ τὰ θνητὰ σώματα ὑμῶν",
                "διὰ τὸ ἐνοικοῦν αὐτοῦ πνεῦμα ἐν ὑμῖν."
            ]
            changes.append("  8:11: restructured protasis/apodosis with proper clause breaks")

        # 8:17 — Fix μέν/δέ stacking
        if ref == "8:17":
            new_lines = [
                "εἰ δὲ τέκνα, καὶ κληρονόμοι·",
                "κληρονόμοι μὲν θεοῦ,",
                "συγκληρονόμοι δὲ Χριστοῦ,",
                "εἴπερ συμπάσχομεν",
                "ἵνα καὶ συνδοξασθῶμεν."
            ]
            changes.append("  8:17: stacked μέν/δέ contrast (κληρονόμοι μὲν θεοῦ / συγκληρονόμοι δὲ Χριστοῦ)")

        # 8:26 — Split long line
        if ref == "8:26":
            new_lines = [
                "Ὡσαύτως δὲ καὶ τὸ πνεῦμα συναντιλαμβάνεται τῇ ἀσθενείᾳ ἡμῶν·",
                "τὸ γὰρ τί προσευξώμεθα καθὸ δεῖ οὐκ οἴδαμεν,",
                "ἀλλὰ αὐτὸ τὸ πνεῦμα ὑπερεντυγχάνει στεναγμοῖς ἀλαλήτοις,"
            ]
            changes.append("  8:26: split long line at ἀλλά discourse marker")

        # 8:30 — Full chain stacking (golden chain of salvation)
        if ref == "8:30":
            new_lines = [
                "οὓς δὲ προώρισεν, τούτους καὶ ἐκάλεσεν·",
                "καὶ οὓς ἐκάλεσεν, τούτους καὶ ἐδικαίωσεν·",
                "οὓς δὲ ἐδικαίωσεν, τούτους καὶ ἐδόξασεν."
            ]
            changes.append("  8:30: stacked golden chain links as parallel lines")

        # 8:33-34 — Rhetorical question stacking
        if ref == "8:34":
            new_lines = [
                "τίς ὁ κατακρινῶν;",
                "Χριστὸς ὁ ἀποθανών,",
                "μᾶλλον δὲ ἐγερθείς,",
                "ὅς καί ἐστιν ἐν δεξιᾷ τοῦ θεοῦ,",
                "ὃς καὶ ἐντυγχάνει ὑπὲρ ἡμῶν·"
            ]
            # Already well structured, just confirm

        # 8:35 — Catalog list stacking
        if ref == "8:35":
            new_lines = [
                "τίς ἡμᾶς χωρίσει ἀπὸ τῆς ἀγάπης τοῦ Χριστοῦ;",
                "θλῖψις",
                "ἢ στενοχωρία",
                "ἢ διωγμὸς",
                "ἢ λιμὸς",
                "ἢ γυμνότης",
                "ἢ κίνδυνος",
                "ἢ μάχαιρα;"
            ]
            changes.append("  8:35: stacked sevenfold catalog list vertically")

        # 8:38-39 — οὔτε catalog stacking (nothing can separate)
        if ref == "8:38":
            new_lines = [
                "πέπεισμαι γὰρ ὅτι",
                "οὔτε θάνατος",
                "οὔτε ζωὴ",
                "οὔτε ἄγγελοι",
                "οὔτε ἀρχαὶ",
                "οὔτε ἐνεστῶτα",
                "οὔτε μέλλοντα",
                "οὔτε δυνάμεις"
            ]
            changes.append("  8:38: stacked οὔτε catalog — nothing can separate list")

        if ref == "8:39":
            new_lines = [
                "οὔτε ὕψωμα",
                "οὔτε βάθος",
                "οὔτε τις κτίσις ἑτέρα",
                "δυνήσεται ἡμᾶς χωρίσαι",
                "ἀπὸ τῆς ἀγάπης τοῦ θεοῦ",
                "τῆς ἐν Χριστῷ Ἰησοῦ τῷ κυρίῳ ἡμῶν."
            ]
            changes.append("  8:39: completed catalog stacking with resolution")

        # 8:20 — Fix "ἐφʼ ἑλπίδι" dangling
        if ref == "8:20":
            new_lines = [
                "τῇ γὰρ ματαιότητι ἡ κτίσις ὑπετάγη,",
                "οὐχ ἑκοῦσα ἀλλὰ διὰ τὸν ὑποτάξαντα,",
                "ἐφʼ ἑλπίδι"
            ]
            changes.append("  8:20: gave ἐφʼ ἑλπίδι its own line as framing device")

        # 8:36 — Split speech intro from content
        if ref == "8:36":
            new_lines = [
                "καθὼς γέγραπται ὅτι",
                "Ἕνεκεν σοῦ θανατούμεθα ὅλην τὴν ἡμέραν,",
                "ἐλογίσθημεν ὡς πρόβατα σφαγῆς."
            ]
            changes.append("  8:36: separated scripture intro from quotation")

        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_phil_02(blocks):
    """Special handling for Philippians 2 — Christ hymn."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)

        # 2:1 — Stack the fourfold εἴ τις parallel
        if ref == "2:1":
            new_lines = [
                "Εἴ τις οὖν παράκλησις ἐν Χριστῷ,",
                "εἴ τι παραμύθιον ἀγάπης,",
                "εἴ τις κοινωνία πνεύματος,",
                "εἴ τις σπλάγχνα καὶ οἰκτιρμοί,"
            ]
            changes.append("  2:1: stacked fourfold εἴ τις parallel structure")

        # 2:2 — Split at ἵνα
        if ref == "2:2":
            new_lines = [
                "πληρώσατέ μου τὴν χαράν,",
                "ἵνα τὸ αὐτὸ φρονῆτε,",
                "τὴν αὐτὴν ἀγάπην ἔχοντες,",
                "σύμψυχοι, τὸ ἓν φρονοῦντες,"
            ]
            changes.append("  2:2: split at ἵνα, stacked parallel participial phrases")

        # 2:6-8 — Christ hymn descent — already mostly good, minor refinements
        if ref == "2:6":
            new_lines = [
                "ὃς ἐν μορφῇ θεοῦ ὑπάρχων",
                "οὐχ ἁρπαγμὸν ἡγήσατο τὸ εἶναι ἴσα θεῷ,"
            ]
            changes.append("  2:6: separated participial frame from main clause in hymn")

        if ref == "2:8":
            new_lines = [
                "ἐταπείνωσεν ἑαυτὸν",
                "γενόμενος ὑπήκοος μέχρι θανάτου,",
                "θανάτου δὲ σταυροῦ."
            ]
            changes.append("  2:8: isolated ἐταπείνωσεν and θανάτου δὲ σταυροῦ escalation")

        # 2:10 — Stack the triple cosmic realm
        if ref == "2:10":
            new_lines = [
                "ἵνα ἐν τῷ ὀνόματι Ἰησοῦ πᾶν γόνυ κάμψῃ",
                "ἐπουρανίων",
                "καὶ ἐπιγείων",
                "καὶ καταχθονίων,"
            ]
            changes.append("  2:10: stacked triple cosmic realm (ἐπουρανίων/ἐπιγείων/καταχθονίων)")

        # 2:11 — Fix ὅτι split
        if ref == "2:11":
            new_lines = [
                "καὶ πᾶσα γλῶσσα ἐξομολογήσηται",
                "ὅτι κύριος Ἰησοῦς Χριστὸς εἰς δόξαν θεοῦ πατρός."
            ]
            changes.append("  2:11: merged ὅτι content clause properly")

        # 2:25 — Split very long line
        if ref == "2:25":
            new_lines = [
                "Ἀναγκαῖον δὲ ἡγησάμην Ἐπαφρόδιτον",
                "τὸν ἀδελφὸν καὶ συνεργὸν καὶ συστρατιώτην μου,",
                "ὑμῶν δὲ ἀπόστολον καὶ λειτουργὸν τῆς χρείας μου,",
                "πέμψαι πρὸς ὑμᾶς,"
            ]
            changes.append("  2:25: split long apposition list, stacked titles")

        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_1cor_13(blocks):
    """Special handling for 1 Corinthians 13 — love chapter."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)

        # 13:2 — Split long conditional
        if ref == "13:2":
            new_lines = [
                "καὶ ἐὰν ἔχω προφητείαν",
                "καὶ εἰδῶ τὰ μυστήρια πάντα καὶ πᾶσαν τὴν γνῶσιν,",
                "καὶ ἐὰν ἔχω πᾶσαν τὴν πίστιν",
                "ὥστε ὄρη μεθιστάναι,",
                "ἀγάπην δὲ μὴ ἔχω,",
                "οὐθέν εἰμι."
            ]
            changes.append("  13:2: split long conditional into proper protasis/apodosis lines")

        # 13:3 — Fix dangling μου
        if ref == "13:3":
            new_lines = [
                "καὶ ἐὰν ψωμίσω πάντα τὰ ὑπάρχοντά μου,",
                "καὶ ἐὰν παραδῶ τὸ σῶμά μου,",
                "ἵνα καυθήσομαι,",
                "ἀγάπην δὲ μὴ ἔχω,",
                "οὐδὲν ὠφελοῦμαι."
            ]
            changes.append("  13:3: fixed dangling μου, proper conditional structure")

        # 13:4 — Stack love's attributes
        if ref == "13:4":
            new_lines = [
                "Ἡ ἀγάπη μακροθυμεῖ,",
                "χρηστεύεται ἡ ἀγάπη,",
                "οὐ ζηλοῖ ἡ ἀγάπη,",
                "οὐ περπερεύεται,",
                "οὐ φυσιοῦται,"
            ]
            changes.append("  13:4: stacked love's attributes as parallel lines")

        # 13:7 — Stack πάντα parallel
        if ref == "13:7":
            new_lines = [
                "πάντα στέγει,",
                "πάντα πιστεύει,",
                "πάντα ἐλπίζει,",
                "πάντα ὑπομένει."
            ]
            changes.append("  13:7: stacked fourfold πάντα parallel")

        # 13:12 — Fix stranded ἄρτι and τότε
        if ref == "13:12":
            new_lines = [
                "βλέπομεν γὰρ ἄρτι διʼ ἐσόπτρου ἐν αἰνίγματι,",
                "τότε δὲ πρόσωπον πρὸς πρόσωπον·",
                "ἄρτι γινώσκω ἐκ μέρους,",
                "τότε δὲ ἐπιγνώσομαι,",
                "καθὼς καὶ ἐπεγνώσθην."
            ]
            changes.append("  13:12: fixed stranded ἄρτι/τότε, proper temporal contrast")

        # 13:13 — Stack the triad
        if ref == "13:13":
            new_lines = [
                "νυνὶ δὲ μένει",
                "πίστις, ἐλπίς, ἀγάπη·",
                "τὰ τρία ταῦτα,",
                "μείζων δὲ τούτων ἡ ἀγάπη."
            ]
            changes.append("  13:13: restructured triad with climactic μείζων line")

        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_eph_01(blocks):
    """Special handling for Ephesians 1 — berakah prayer (1:3-14 one sentence)."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)

        # 1:1 — Fix order (lines appear out of order in v3)
        if ref == "1:1":
            new_lines = [
                "Παῦλος ἀπόστολος Χριστοῦ Ἰησοῦ διὰ θελήματος θεοῦ",
                "τοῖς ἁγίοις τοῖς οὖσιν [ἐν Ἐφέσῳ]",
                "καὶ πιστοῖς ἐν Χριστῷ Ἰησοῦ·"
            ]
            changes.append("  1:1: fixed salutation line order")

        # 1:7 — Split apposition
        if ref == "1:7":
            new_lines = [
                "ἐν ᾧ ἔχομεν τὴν ἀπολύτρωσιν διὰ τοῦ αἵματος αὐτοῦ,",
                "τὴν ἄφεσιν τῶν παραπτωμάτων,",
                "κατὰ τὸ πλοῦτος τῆς χάριτος αὐτοῦ"
            ]
            changes.append("  1:7: separated apposition (τὴν ἄφεσιν) onto its own line")

        # 1:10 — Fix ἐν αὐτῷ dangling
        if ref == "1:10":
            new_lines = [
                "εἰς οἰκονομίαν τοῦ πληρώματος τῶν καιρῶν,",
                "ἀνακεφαλαιώσασθαι τὰ πάντα ἐν τῷ Χριστῷ,",
                "τὰ ἐπὶ τοῖς οὐρανοῖς καὶ τὰ ἐπὶ τῆς γῆς·",
                "ἐν αὐτῷ,"
            ]
            changes.append("  1:10: separated cosmic scope list, gave ἐν αὐτῷ its own line")

        # 1:18 — Stack the triple τίς questions
        if ref == "1:18":
            new_lines = [
                "πεφωτισμένους τοὺς ὀφθαλμοὺς τῆς καρδίας ὑμῶν εἰς τὸ εἰδέναι ὑμᾶς",
                "τίς ἐστιν ἡ ἐλπὶς τῆς κλήσεως αὐτοῦ,",
                "τίς ὁ πλοῦτος τῆς δόξης τῆς κληρονομίας αὐτοῦ ἐν τοῖς ἁγίοις,"
            ]
            changes.append("  1:18: stacked τίς questions as parallel lines")

        # 1:21 — Fix order and parallel stacking
        if ref == "1:21":
            new_lines = [
                "ὑπεράνω πάσης ἀρχῆς",
                "καὶ ἐξουσίας",
                "καὶ δυνάμεως",
                "καὶ κυριότητος",
                "καὶ παντὸς ὀνόματος ὀνομαζομένου",
                "οὐ μόνον ἐν τῷ αἰῶνι τούτῳ ἀλλὰ καὶ ἐν τῷ μέλλοντι·"
            ]
            changes.append("  1:21: stacked fourfold cosmic powers + temporal scope")

        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_col_01(blocks):
    """Special handling for Colossians 1 — cosmic hymn."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)

        # 1:2 — Fix χάρις ὑμῖν fragment
        if ref == "1:2":
            new_lines = [
                "τοῖς ἐν Κολοσσαῖς ἁγίοις καὶ πιστοῖς ἀδελφοῖς ἐν Χριστῷ·",
                "χάρις ὑμῖν καὶ εἰρήνη ἀπὸ θεοῦ πατρὸς ἡμῶν."
            ]
            changes.append("  1:2: merged grace formula into one line")

        # 1:16 — Stack εἴτε quadruple list
        if ref == "1:16":
            new_lines = [
                "ὅτι ἐν αὐτῷ ἐκτίσθη τὰ πάντα ἐν τοῖς οὐρανοῖς καὶ ἐπὶ τῆς γῆς,",
                "τὰ ὁρατὰ καὶ τὰ ἀόρατα,",
                "εἴτε θρόνοι",
                "εἴτε κυριότητες",
                "εἴτε ἀρχαὶ",
                "εἴτε ἐξουσίαι·",
                "τὰ πάντα διʼ αὐτοῦ καὶ εἰς αὐτὸν ἔκτισται·"
            ]
            changes.append("  1:16: stacked εἴτε quadruple cosmic powers list")

        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_rom_05(blocks):
    """Special handling for Romans 5 — Adam/Christ typology."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)
        new_blocks.append((ref, new_lines))

    return new_blocks, changes


def handle_1tim_03(blocks):
    """Special handling for 1 Timothy 3:16 — hymn fragment."""
    changes = []
    new_blocks = []

    for ref, lines in blocks:
        new_lines = list(lines)
        new_blocks.append((ref, new_lines))

    return new_blocks, changes


# ============================================================
# MAIN PROCESSING
# ============================================================

def process_all():
    os.makedirs(V4_DIR, exist_ok=True)

    total_changed = 0
    total_line_changes = 0
    all_changes = []
    changed_files = []
    unchanged_files = []
    fix_type_counts = {}

    for filename in PAULINE_FILES:
        v3_path = os.path.join(V3_DIR, filename)
        v4_path = os.path.join(V4_DIR, filename)

        if not os.path.exists(v3_path):
            print(f"WARNING: {filename} not found in v3")
            continue

        blocks = parse_file(v3_path)
        original_text = blocks_to_text(blocks)

        # Apply general fixes FIRST
        blocks, general_changes = apply_v4_fixes(blocks, filename)

        # Apply special handlers LAST — they override general fixes for key passages
        special_changes = []
        if filename == "rom-08.txt":
            blocks, special_changes = handle_rom_08(blocks)
        elif filename == "phil-02.txt":
            blocks, special_changes = handle_phil_02(blocks)
        elif filename == "1cor-13.txt":
            blocks, special_changes = handle_1cor_13(blocks)
        elif filename == "eph-01.txt":
            blocks, special_changes = handle_eph_01(blocks)
        elif filename == "col-01.txt":
            blocks, special_changes = handle_col_01(blocks)

        changes = general_changes + special_changes
        new_text = blocks_to_text(blocks)

        if new_text != original_text:
            total_changed += 1
            total_line_changes += len(changes)
            all_changes.append((filename, changes))
            changed_files.append(filename)

            with open(v4_path, "w", encoding="utf-8") as f:
                f.write(new_text)

            # Count fix types
            for change in changes:
                if "stacked" in change:
                    fix_type_counts["parallel stacking"] = fix_type_counts.get("parallel stacking", 0) + 1
                elif "μέν/δέ" in change:
                    fix_type_counts["μέν/δέ contrast"] = fix_type_counts.get("μέν/δέ contrast", 0) + 1
                elif "split long" in change or "split" in change.lower():
                    fix_type_counts["long line split"] = fix_type_counts.get("long line split", 0) + 1
                elif "merged" in change:
                    fix_type_counts["fragment merge"] = fix_type_counts.get("fragment merge", 0) + 1
                elif "dangling" in change:
                    fix_type_counts["dangling fix"] = fix_type_counts.get("dangling fix", 0) + 1
                elif "speech" in change:
                    fix_type_counts["speech intro"] = fix_type_counts.get("speech intro", 0) + 1
                elif "escalation" in change or "μᾶλλον" in change:
                    fix_type_counts["escalation"] = fix_type_counts.get("escalation", 0) + 1
                elif "εἰ μή" in change:
                    fix_type_counts["restriction merge"] = fix_type_counts.get("restriction merge", 0) + 1
                else:
                    fix_type_counts["other"] = fix_type_counts.get("other", 0) + 1
        else:
            unchanged_files.append(filename)

    # Report
    print(f"\n{'='*60}")
    print(f"V4 PAULINE EDITORIAL REVIEW — SUMMARY")
    print(f"{'='*60}")
    print(f"Total chapters reviewed: {len(PAULINE_FILES)}")
    print(f"Chapters changed: {total_changed}")
    print(f"Chapters unchanged: {len(unchanged_files)}")
    print(f"Total line-level changes: {total_line_changes}")
    print()

    print("FIX TYPE BREAKDOWN:")
    for ftype, count in sorted(fix_type_counts.items(), key=lambda x: -x[1]):
        print(f"  {ftype}: {count}")
    print()

    print("CHANGED FILES:")
    for filename, changes in all_changes:
        print(f"\n  {filename} ({len(changes)} changes):")
        for c in changes:
            print(f"    {c}")

    print(f"\n{'='*60}")
    print(f"Files written to: {V4_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    process_all()
