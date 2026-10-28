"""Zombie: "Find students with continuous activity (no gaps longer than 15 minutes) for more than 3 hours."

Rule: on one merged LMS + video timeline of distinct TIMESTAMPs (first access / first play, UTC), a run breaks
wherever consecutive timestamps are more than 15 minutes apart; flag a P_ID if any run spans more than 3 hours
from its first to its last timestamp. Timestamps are deduplicated first so an LMS and a video row at the same
instant can't straddle a run boundary. Variant counts on training are in monster-guide.md.

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
        WITH t AS (SELECT DISTINCT P_ID, ts FROM activity),
        g AS (
            SELECT *, CASE WHEN ts - lag(ts) OVER (PARTITION BY P_ID ORDER BY ts) <= INTERVAL 15 minutes
                           THEN 0 ELSE 1 END AS new_run
            FROM t
        ),
        r AS (SELECT *, sum(new_run) OVER (PARTITION BY P_ID ORDER BY ts ROWS UNBOUNDED PRECEDING) AS run FROM g)
        SELECT DISTINCT P_ID FROM (SELECT P_ID, max(ts) - min(ts) AS span FROM r GROUP BY P_ID, run)
        WHERE span > INTERVAL 3 hours ORDER BY P_ID
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
