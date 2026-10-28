"""Ghost: "Find students who have been active at least 3 of the first 4 weeks of the Autumn term but then interacted
very little for the rest of the academic year (later average weekly count of activity rows is <10% of early weekly
average count of activity rows). Look at LMS and video activity."

Rule: LMS and video rows together, placed in weeks by calendar WEEK_NUMBER (rows outside the calendar dropped).
At least 3 of weeks 1-4 have a row, and (rows in weeks 5-52 / 48) < 0.1 * (rows in weeks 1-4 / 4).
P_IDs missing from person_dim are dropped. Variant counts on training are in monster-guide.md.

Run: uv run python -m detector.ghost [training|test|predict]
Writes out/hunt/ghost.csv for training, out/<split>/ghost.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"


def find(con):
    return [r[0] for r in con.execute("""
        WITH wk AS (
            SELECT a.P_ID, c.WEEK_NUMBER AS w, count(*) AS n
            FROM activity a JOIN calendar_dim c USING (DATE)
            GROUP BY 1, 2
        ),
        p AS (
            SELECT P_ID,
                   count(*) FILTER (WHERE w <= 4) AS active_early,
                   sum(n) FILTER (WHERE w <= 4) AS early,
                   coalesce(sum(n) FILTER (WHERE w > 4), 0) AS later
            FROM wk GROUP BY 1
        )
        SELECT P_ID FROM p JOIN person_dim USING (P_ID)
        WHERE active_early >= 3 AND later / 48 < 0.1 * early / 4
        ORDER BY P_ID
    """).fetchall()]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    p_ids = find(connect(split))
    path = OUT / ("hunt" if split == "training" else split) / "ghost.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(["Ghost", p] for p in p_ids)
    print(f"{len(p_ids)} Ghosts -> {path}")
