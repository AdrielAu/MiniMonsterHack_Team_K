"""Zombie: "Find students with continuous activity (no gaps longer than 15 minutes) for more than 3 hours."

Rule (retuned against the HUNT answers): flag a P_ID if either
- its video views replay: some views are logged more than once under the same PVT_ID, and every such
  repeated view falls within 24 hours, at 2+ distinct timestamps (one stretch of viewing, recorded twice), or
- its video views alone form a run of distinct TIMESTAMPs (UTC) with no gap over 15 minutes lasting more than 3 hours.
The old merged LMS + video run rule caught night-time Vampires, not Zombies; see monster-guide.md.

Run: uv run python -m detector.zombie [training|test|predict]
Writes out/hunt/zombie.csv for training, out/<split>/zombie.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"


def find(con):
    return [r[0] for r in con.execute("""
        WITH repeated AS (
            SELECT DISTINCT v.P_ID, v.TIMESTAMP AS ts
            FROM video_activity_by_view_fact v
            JOIN (SELECT P_ID, PVT_ID FROM video_activity_by_view_fact GROUP BY ALL HAVING count(*) > 1)
                USING (P_ID, PVT_ID)
        ),
        replay AS (
            SELECT P_ID FROM repeated GROUP BY P_ID HAVING max(ts) - min(ts) <= INTERVAL 24 hours AND count(*) >= 2
        ),
        t AS (SELECT DISTINCT P_ID, TIMESTAMP AS ts FROM video_activity_by_view_fact),
        g AS (
            SELECT *, CASE WHEN ts - lag(ts) OVER (PARTITION BY P_ID ORDER BY ts) <= INTERVAL 15 minutes
                           THEN 0 ELSE 1 END AS new_run
            FROM t
        ),
        r AS (SELECT *, sum(new_run) OVER (PARTITION BY P_ID ORDER BY ts ROWS UNBOUNDED PRECEDING) AS run FROM g),
        long_run AS (
            SELECT DISTINCT P_ID FROM (SELECT P_ID, max(ts) - min(ts) AS span FROM r GROUP BY P_ID, run)
            WHERE span > INTERVAL 3 hours
        )
        SELECT P_ID FROM replay UNION SELECT P_ID FROM long_run ORDER BY P_ID
    """).fetchall()]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    p_ids = find(connect(split))
    path = OUT / ("hunt" if split == "training" else split) / "zombie.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(["Zombie", p] for p in p_ids)
    print(f"{len(p_ids)} Zombies -> {path}")
