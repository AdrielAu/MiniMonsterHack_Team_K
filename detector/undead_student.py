"""Undead Student: "Find students with activity after their deregistration date. Look at LMS and video activity."

Rule: any LMS or video row whose DATE is strictly after the person's deregistration_date.
People with a null deregistration_date, and activity P_IDs missing from person_dim, are never Undead.
Variant counts on training (UTC vs UK-local date, > vs >=, with or without _COPY_ rows) are in monster-guide.md.

Run: uv run python -m detector.undead_student [training|test|predict]
Writes out/hunt/undead_student.csv for training, out/<split>/undead_student.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"


def find(con):
    return [r[0] for r in con.execute("""
        SELECT DISTINCT a.P_ID
        FROM activity a JOIN person_dim p USING (P_ID)
        WHERE a.DATE > p.deregistration_date
        ORDER BY a.P_ID
    """).fetchall()]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    p_ids = find(connect(split))
    path = OUT / ("hunt" if split == "training" else split) / "undead_student.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(["Undead Student", p] for p in p_ids)
    print(f"{len(p_ids)} Undead Students -> {path}")
