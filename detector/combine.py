"""Combine one stage's per-monster CSVs into the paste-ready MANUAL COMBINED CSV.

Overlaps are allowed (organisers' answer), so a P_ID caught by two rules stays in under both types.
Only exact repeats of the same (Monster Type, P_ID) row are dropped.

Run: uv run python -m detector.combine [hunt|test|predict]
Reads out/<stage>/*.csv, writes out/<stage>/<STAGE>_combined.csv (UTF-8 with BOM so Excel keeps the umlaut).
"""

import csv
import re
import sys
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "out"

# Spelled exactly as on the template's REFERENCE sheet.
TYPES = ["Phantom", "Ghost", "Zombie", "Vampire", "Undead Student",
         "Doppelgänger", "Werewolf", "Web Crawler", "Shape-shifter"]

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "hunt"
    folder = OUT / stage
    target = folder / f"{stage.upper()}_combined.csv"
    rows = set()
    for path in sorted(folder.glob("*.csv")):
        if path == target:
            continue
        with open(path, newline="", encoding="utf-8-sig") as f:
            r = csv.reader(f)
            if next(r) != ["Monster Type", "P_ID"]:
                sys.exit(f"{path.name}: header must be exactly Monster Type,P_ID")
            for monster, p_id in r:
                if monster not in TYPES:
                    sys.exit(f"{path.name}: unknown Monster Type {monster!r}")
                if not re.fullmatch(r"P\d+", p_id):
                    sys.exit(f"{path.name}: bad P_ID {p_id!r}")
                rows.add((monster, p_id))
    rows = sorted(rows, key=lambda r: (TYPES.index(r[0]), r[1]))
    with open(target, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(rows)
    counts = Counter(m for m, _ in rows)
    for m in TYPES:
        print(f"{m:15} {counts[m]:4}" + ("" if counts[m] else "   <- MISSING"))
    multi = Counter(p for _, p in rows)
    print(f"{len(rows)} rows, {len(multi)} distinct P_IDs, {sum(c > 1 for c in multi.values())} under 2+ types -> {target}")
