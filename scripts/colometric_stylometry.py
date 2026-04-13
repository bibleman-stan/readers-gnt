#!/usr/bin/env python3
"""
Colometric Stylometry for the Greek New Testament v4-editorial corpus.

Measures per-book and per-chapter line-structure metrics that can serve as
an authorial "voice waveform" for the prospectus. Based on stylometric
analysis protocols developed for parallel colometric work on another
ancient-text corpus; adapted here for Greek.

Outputs:
  research/stylometry/gnt_chapter_metrics.csv      -- per-chapter rows
  research/stylometry/gnt_book_metrics.csv         -- per-book rollup
  research/stylometry/gnt_cluster_metrics.csv      -- traditional author clusters
  research/stylometry/gnt_line_length_histogram.csv  -- line-length buckets per book
  research/stylometry/gnt_stylometry_summary.txt   -- human-readable summary

Run:
  PYTHONIOENCODING=utf-8 py -3 scripts/colometric_stylometry.py
"""

import csv
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
V4_DIR = REPO_ROOT / "data" / "text-files" / "v4-editorial"
OUT_DIR = REPO_ROOT / "research" / "stylometry"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Book ordering and traditional authorial clusters
# ----------------------------------------------------------------------

BOOKS = [
    ("matt",    "01-matt",    "Matthew"),
    ("mark",    "02-mark",    "Mark"),
    ("luke",    "03-luke",    "Luke"),
    ("john",    "04-john",    "John (Gospel)"),
    ("acts",    "05-acts",    "Acts"),
    ("rom",     "06-rom",     "Romans"),
    ("1cor",    "07-1cor",    "1 Corinthians"),
    ("2cor",    "08-2cor",    "2 Corinthians"),
    ("gal",     "09-gal",     "Galatians"),
    ("eph",     "10-eph",     "Ephesians"),
    ("phil",    "11-phil",    "Philippians"),
    ("col",     "12-col",     "Colossians"),
    ("1thess",  "13-1thess",  "1 Thessalonians"),
    ("2thess",  "14-2thess",  "2 Thessalonians"),
    ("1tim",    "15-1tim",    "1 Timothy"),
    ("2tim",    "16-2tim",    "2 Timothy"),
    ("titus",   "17-titus",   "Titus"),
    ("phlm",    "18-phlm",    "Philemon"),
    ("heb",     "19-heb",     "Hebrews"),
    ("jas",     "20-jas",     "James"),
    ("1pet",    "21-1pet",    "1 Peter"),
    ("2pet",    "22-2pet",    "2 Peter"),
    ("1john",   "23-1john",   "1 John"),
    ("2john",   "24-2john",   "2 John"),
    ("3john",   "25-3john",   "3 John"),
    ("jude",    "26-jude",    "Jude"),
    ("rev",     "27-rev",     "Revelation"),
]

# Traditional / prospectus-relevant authorial clusters
CLUSTERS = [
    ("Mark (narrative)",             ["mark"]),
    ("Matthew (narrative)",          ["matt"]),
    ("Luke-Acts (Hellenistic)",      ["luke", "acts"]),
    ("John Gospel",                  ["john"]),
    ("Johannine Epistles",           ["1john", "2john", "3john"]),
    ("Johannine Corpus (w/ Rev)",    ["john", "1john", "2john", "3john", "rev"]),
    ("Johannine Corpus (no Rev)",    ["john", "1john", "2john", "3john"]),
    ("Paul Undisputed Core",         ["rom", "1cor", "2cor", "gal"]),
    ("Paul Undisputed (+ Phil/1Th/Phlm)", ["rom", "1cor", "2cor", "gal", "phil", "1thess", "phlm"]),
    ("Paul Disputed (Deutero)",      ["eph", "col", "2thess"]),
    ("Paul Pastorals",               ["1tim", "2tim", "titus"]),
    ("Hebrews",                      ["heb"]),
    ("General Epistles",             ["jas", "1pet", "2pet", "jude"]),
    ("Revelation",                   ["rev"]),
    ("Synoptics",                    ["matt", "mark", "luke"]),
]

# ----------------------------------------------------------------------
# Greek text handling
# ----------------------------------------------------------------------

# Editorial punctuation to strip before word counting. Per project policy,
# punctuation is not an original feature of the text — we count words by
# whitespace after removing punctuation.
PUNCT_CHARS = ".,;·:!?()[]{}<>\"'\u2018\u2019\u201c\u201d\u00b7\u0387\u037e\u2013\u2014"
PUNCT_TABLE = str.maketrans({c: " " for c in PUNCT_CHARS})

VERSE_RE = re.compile(r"^(\d+):(\d+)\s*$")


def count_words(line: str) -> int:
    if not line:
        return 0
    cleaned = line.translate(PUNCT_TABLE)
    return len([t for t in cleaned.split() if t.strip()])


def parse_chapter_file(path: Path):
    """Return list of (verse_ref, [lines]) tuples in order, plus flat line list."""
    verses = []  # list of (ref, [lines])
    current = None
    lines_flat = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\r\n").strip()
            if not line:
                continue
            m = VERSE_RE.match(line)
            if m:
                ref = f"{m.group(1)}:{m.group(2)}"
                current = (ref, [])
                verses.append(current)
                continue
            if current is None:
                # orphan line before any verse header — skip
                continue
            current[1].append(line)
            lines_flat.append(line)
    return verses, lines_flat


# ----------------------------------------------------------------------
# Greek-specific structural heuristics
# ----------------------------------------------------------------------

def _normalize_initial(word: str) -> str:
    # strip combining marks (accents/breathings) and lowercase for matching
    nfd = unicodedata.normalize("NFD", word)
    stripped = "".join(c for c in nfd if not unicodedata.combining(c))
    return stripped.lower()


# Discourse / subordinator / conjunction markers commonly starting a colon in Greek.
# We count line-initial occurrences as a proxy for "how periodic is this line
# structure" — Paul and Hebrews should show heavier subordination initiation.
SUBORDINATORS = {
    "ινα", "οτι", "οτε", "οταν", "εαν", "ει", "ωστε", "επει", "επειδη",
    "καθως", "καθαπερ", "μηποτε", "ως", "οπως", "διο", "διοτι",
}
DISCOURSE_MARKERS = {
    "γαρ", "δε", "ουν", "αλλα", "μεν", "και", "τοινυν", "αρα",
}
# Rough participle suffix markers (masc/neut nom sg -ων/-ον/-σας/-ως etc.
# are noisy, so we instead flag lines that *start* with a participial form
# by checking against a short whitelist of frequent participles is infeasible.
# We therefore skip morphological participle detection and keep the
# line-length distribution as the primary fingerprint, matching the task brief.


def line_initial_category(line: str) -> str:
    tokens = line.translate(PUNCT_TABLE).split()
    if not tokens:
        return "empty"
    first = _normalize_initial(tokens[0])
    if first in SUBORDINATORS:
        return "subordinator"
    if first in DISCOURSE_MARKERS:
        return "discourse"
    return "other"


# ----------------------------------------------------------------------
# Metric computation
# ----------------------------------------------------------------------

HIST_BUCKETS = [(1, 5), (6, 10), (11, 15), (16, 20), (21, 99)]
HIST_LABELS = ["1-5", "6-10", "11-15", "16-20", "21+"]


def bucket_for(wc: int) -> str:
    for (lo, hi), label in zip(HIST_BUCKETS, HIST_LABELS):
        if lo <= wc <= hi:
            return label
    return "21+"


def analyze_chapter(book_id, chapter_num, verses):
    lines = []
    for _ref, vs_lines in verses:
        lines.extend(vs_lines)
    if not lines:
        return None

    wcs = [count_words(l) for l in lines]
    wcs = [w for w in wcs if w > 0]
    if not wcs:
        return None

    total_lines = len(wcs)
    total_words = sum(wcs)
    total_verses = len(verses)

    mean_wpl = total_words / total_lines
    median_wpl = statistics.median(wcs)
    stdev_wpl = statistics.pstdev(wcs) if total_lines > 1 else 0.0
    lines_per_verse = total_lines / total_verses if total_verses else 0.0

    # line-start category counts (subordinator / discourse / other)
    sub_lines = 0
    disc_lines = 0
    for l in lines:
        cat = line_initial_category(l)
        if cat == "subordinator":
            sub_lines += 1
        elif cat == "discourse":
            disc_lines += 1

    # histogram buckets
    hist = Counter(bucket_for(w) for w in wcs)

    return {
        "book": book_id,
        "chapter": chapter_num,
        "total_verses": total_verses,
        "total_lines": total_lines,
        "total_words": total_words,
        "mean_words_per_line": round(mean_wpl, 3),
        "median_words_per_line": round(float(median_wpl), 2),
        "stdev_words_per_line": round(stdev_wpl, 3),
        "lines_per_verse": round(lines_per_verse, 3),
        "subordinator_initial_lines": sub_lines,
        "subordinator_initial_pct": round(sub_lines / total_lines * 100, 2),
        "discourse_initial_lines": disc_lines,
        "discourse_initial_pct": round(disc_lines / total_lines * 100, 2),
        "hist_1_5": hist.get("1-5", 0),
        "hist_6_10": hist.get("6-10", 0),
        "hist_11_15": hist.get("11-15", 0),
        "hist_16_20": hist.get("16-20", 0),
        "hist_21_plus": hist.get("21+", 0),
    }


def collect():
    chapter_rows = []
    # also keep raw wc lists per book for later aggregation
    book_wcs = defaultdict(list)
    book_verses = defaultdict(int)
    book_lines = defaultdict(int)
    book_words = defaultdict(int)
    book_sub_lines = defaultdict(int)
    book_disc_lines = defaultdict(int)

    for book_id, folder, _display in BOOKS:
        book_dir = V4_DIR / folder
        if not book_dir.is_dir():
            print(f"  [skip] {book_dir} not found")
            continue
        chapter_files = sorted(book_dir.glob(f"{book_id}-*.txt"))
        if not chapter_files:
            print(f"  [skip] no chapter files in {book_dir}")
            continue
        for cf in chapter_files:
            m = re.search(r"-(\d+)\.txt$", cf.name)
            if not m:
                continue
            ch_num = int(m.group(1))
            verses, lines_flat = parse_chapter_file(cf)
            row = analyze_chapter(book_id, ch_num, verses)
            if row is None:
                continue
            chapter_rows.append(row)

            # accumulate per-book raw word counts
            for _ref, vs_lines in verses:
                for l in vs_lines:
                    wc = count_words(l)
                    if wc > 0:
                        book_wcs[book_id].append(wc)
                        cat = line_initial_category(l)
                        if cat == "subordinator":
                            book_sub_lines[book_id] += 1
                        elif cat == "discourse":
                            book_disc_lines[book_id] += 1
            book_verses[book_id] += row["total_verses"]
            book_lines[book_id] += row["total_lines"]
            book_words[book_id] += row["total_words"]

    return chapter_rows, book_wcs, book_verses, book_lines, book_words, book_sub_lines, book_disc_lines


def rollup_book(book_id, display, wcs, verses, lines, words, sub_lines, disc_lines):
    if lines == 0:
        return None
    mean_wpl = words / lines
    median_wpl = statistics.median(wcs)
    stdev_wpl = statistics.pstdev(wcs) if len(wcs) > 1 else 0.0
    hist = Counter(bucket_for(w) for w in wcs)
    return {
        "book": book_id,
        "display": display,
        "chapters": 0,  # filled in by caller
        "total_verses": verses,
        "total_lines": lines,
        "total_words": words,
        "mean_words_per_line": round(mean_wpl, 3),
        "median_words_per_line": round(float(median_wpl), 2),
        "stdev_words_per_line": round(stdev_wpl, 3),
        "lines_per_verse": round(lines / verses, 3) if verses else 0.0,
        "subordinator_initial_pct": round(sub_lines / lines * 100, 2),
        "discourse_initial_pct": round(disc_lines / lines * 100, 2),
        "hist_1_5": hist.get("1-5", 0),
        "hist_6_10": hist.get("6-10", 0),
        "hist_11_15": hist.get("11-15", 0),
        "hist_16_20": hist.get("16-20", 0),
        "hist_21_plus": hist.get("21+", 0),
        "hist_1_5_pct": round(hist.get("1-5", 0) / lines * 100, 2),
        "hist_6_10_pct": round(hist.get("6-10", 0) / lines * 100, 2),
        "hist_11_15_pct": round(hist.get("11-15", 0) / lines * 100, 2),
        "hist_16_20_pct": round(hist.get("16-20", 0) / lines * 100, 2),
        "hist_21_plus_pct": round(hist.get("21+", 0) / lines * 100, 2),
    }


def rollup_cluster(cluster_name, members, book_wcs, book_verses, book_lines, book_words, book_sub_lines, book_disc_lines):
    wcs = []
    verses = lines = words = sub_lines = disc_lines = 0
    for m in members:
        wcs.extend(book_wcs.get(m, []))
        verses += book_verses.get(m, 0)
        lines += book_lines.get(m, 0)
        words += book_words.get(m, 0)
        sub_lines += book_sub_lines.get(m, 0)
        disc_lines += book_disc_lines.get(m, 0)
    if lines == 0:
        return None
    mean_wpl = words / lines
    median_wpl = statistics.median(wcs)
    stdev_wpl = statistics.pstdev(wcs) if len(wcs) > 1 else 0.0
    hist = Counter(bucket_for(w) for w in wcs)
    return {
        "cluster": cluster_name,
        "members": "+".join(members),
        "total_verses": verses,
        "total_lines": lines,
        "total_words": words,
        "mean_words_per_line": round(mean_wpl, 3),
        "median_words_per_line": round(float(median_wpl), 2),
        "stdev_words_per_line": round(stdev_wpl, 3),
        "lines_per_verse": round(lines / verses, 3) if verses else 0.0,
        "subordinator_initial_pct": round(sub_lines / lines * 100, 2),
        "discourse_initial_pct": round(disc_lines / lines * 100, 2),
        "hist_1_5_pct": round(hist.get("1-5", 0) / lines * 100, 2),
        "hist_6_10_pct": round(hist.get("6-10", 0) / lines * 100, 2),
        "hist_11_15_pct": round(hist.get("11-15", 0) / lines * 100, 2),
        "hist_16_20_pct": round(hist.get("16-20", 0) / lines * 100, 2),
        "hist_21_plus_pct": round(hist.get("21+", 0) / lines * 100, 2),
    }


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    print(f"Reading v4-editorial from {V4_DIR}")
    (chapter_rows, book_wcs, book_verses, book_lines,
     book_words, book_sub_lines, book_disc_lines) = collect()

    # --- per-chapter csv ---
    ch_fields = list(chapter_rows[0].keys())
    write_csv(OUT_DIR / "gnt_chapter_metrics.csv", chapter_rows, ch_fields)
    print(f"Wrote {len(chapter_rows)} chapter rows -> gnt_chapter_metrics.csv")

    # --- per-book rollup ---
    book_rows = []
    book_chapters = Counter(r["book"] for r in chapter_rows)
    for book_id, _folder, display in BOOKS:
        if book_id not in book_wcs:
            continue
        row = rollup_book(
            book_id, display,
            book_wcs[book_id], book_verses[book_id],
            book_lines[book_id], book_words[book_id],
            book_sub_lines[book_id], book_disc_lines[book_id],
        )
        if row is None:
            continue
        row["chapters"] = book_chapters[book_id]
        book_rows.append(row)

    bk_fields = list(book_rows[0].keys())
    write_csv(OUT_DIR / "gnt_book_metrics.csv", book_rows, bk_fields)
    print(f"Wrote {len(book_rows)} book rows -> gnt_book_metrics.csv")

    # --- cluster rollup ---
    cluster_rows = []
    for name, members in CLUSTERS:
        row = rollup_cluster(
            name, members, book_wcs, book_verses, book_lines,
            book_words, book_sub_lines, book_disc_lines,
        )
        if row:
            cluster_rows.append(row)
    cl_fields = list(cluster_rows[0].keys())
    write_csv(OUT_DIR / "gnt_cluster_metrics.csv", cluster_rows, cl_fields)
    print(f"Wrote {len(cluster_rows)} cluster rows -> gnt_cluster_metrics.csv")

    # --- line-length histogram (just the pct columns, compact view) ---
    hist_rows = []
    for r in book_rows:
        hist_rows.append({
            "book": r["book"],
            "display": r["display"],
            "total_lines": r["total_lines"],
            "mean_wpl": r["mean_words_per_line"],
            "median_wpl": r["median_words_per_line"],
            "stdev_wpl": r["stdev_words_per_line"],
            "pct_1_5": r["hist_1_5_pct"],
            "pct_6_10": r["hist_6_10_pct"],
            "pct_11_15": r["hist_11_15_pct"],
            "pct_16_20": r["hist_16_20_pct"],
            "pct_21_plus": r["hist_21_plus_pct"],
        })
    hist_fields = list(hist_rows[0].keys())
    write_csv(OUT_DIR / "gnt_line_length_histogram.csv", hist_rows, hist_fields)

    # --- human-readable summary ---
    summary_path = OUT_DIR / "gnt_stylometry_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("GNT COLOMETRIC STYLOMETRY - v4-editorial corpus\n")
        f.write("=" * 72 + "\n\n")
        f.write("Methodology: line-structure metrics over hand-edited sense-lines.\n")
        f.write("Word count = whitespace tokens after stripping editorial punctuation.\n")
        f.write("Based on stylometric analysis protocols developed for parallel\n")
        f.write("colometric work on another ancient-text corpus; adapted for Greek.\n\n")
        f.write("Note on FEF (Front-End Frame): in the sibling corpus, FEFs are\n")
        f.write("mechanically detectable from a single formulaic opener. Greek has no\n")
        f.write("comparable single-phrase marker; narrative KAI EGENETO / EGENETO DE\n")
        f.write("come closest but are not universal. This pass therefore reports\n")
        f.write("line-length distribution as the primary authorial fingerprint and\n")
        f.write("tracks subordinator- and discourse-initial line rates as a proxy\n")
        f.write("for periodic vs. paratactic register.\n\n")

        f.write("-- PER BOOK (sorted by mean words/line) --\n")
        f.write(f"{'book':<20} {'chs':>3} {'lines':>6} {'words':>7} "
                f"{'mean':>5} {'med':>4} {'stdev':>5} {'L/V':>5} "
                f"{'sub%':>5} {'disc%':>5} {'1-5':>5} {'6-10':>5} "
                f"{'11-15':>6} {'16-20':>6} {'21+':>5}\n")
        for r in sorted(book_rows, key=lambda x: x["mean_words_per_line"]):
            f.write(f"{r['display']:<20} {r['chapters']:>3} {r['total_lines']:>6} "
                    f"{r['total_words']:>7} {r['mean_words_per_line']:>5.2f} "
                    f"{r['median_words_per_line']:>4.1f} {r['stdev_words_per_line']:>5.2f} "
                    f"{r['lines_per_verse']:>5.2f} "
                    f"{r['subordinator_initial_pct']:>5.1f} {r['discourse_initial_pct']:>5.1f} "
                    f"{r['hist_1_5_pct']:>5.1f} {r['hist_6_10_pct']:>5.1f} "
                    f"{r['hist_11_15_pct']:>6.1f} {r['hist_16_20_pct']:>6.1f} "
                    f"{r['hist_21_plus_pct']:>5.1f}\n")
        f.write("\n")

        f.write("-- AUTHORIAL CLUSTERS --\n")
        f.write(f"{'cluster':<38} {'lines':>6} {'words':>7} {'mean':>5} "
                f"{'med':>4} {'stdev':>5} {'L/V':>5} {'sub%':>5} {'disc%':>5} "
                f"{'1-5%':>5} {'21+%':>5}\n")
        for r in cluster_rows:
            f.write(f"{r['cluster']:<38} {r['total_lines']:>6} {r['total_words']:>7} "
                    f"{r['mean_words_per_line']:>5.2f} {r['median_words_per_line']:>4.1f} "
                    f"{r['stdev_words_per_line']:>5.2f} {r['lines_per_verse']:>5.2f} "
                    f"{r['subordinator_initial_pct']:>5.1f} {r['discourse_initial_pct']:>5.1f} "
                    f"{r['hist_1_5_pct']:>5.1f} {r['hist_21_plus_pct']:>5.1f}\n")
        f.write("\n")

    print(f"Wrote summary -> {summary_path}")
    print("Done.")


if __name__ == "__main__":
    main()
