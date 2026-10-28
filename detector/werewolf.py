"""Werewolf: "Find students with spikes in activity throughout the Autumn and Spring Terms."

Deadline rule calibrated on the six corrected HUNT answers. Shortlist students
with repeated 3-9-day activity blocks, then apply the fitted tree's video rhythm
and term-coverage cutoffs. See experiments/werewolf/ for the investigation.
HUNT: six correct, two false positives. Held-out performance is poor; this is a
provisional submission rule, not a validated general classifier.

Run: uv run python -m detector.werewolf [training|test|predict]
Writes out/hunt/werewolf.csv for training, out/<split>/werewolf.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"
# shortcut: HUNT-fitted tree; revisit with more labelled cases after the deadline.
def find(con):
    return [r[0] for r in con.execute("""
        WITH daily AS (
            SELECT P_ID, source, CAST(ts_local AS DATE) AS d, count(*) AS n
            FROM activity
            GROUP BY 1, 2, 3
        ), islands AS (
            SELECT *, d - CAST(row_number() OVER (
                PARTITION BY P_ID, source ORDER BY d
            ) AS INTEGER) AS grp
            FROM daily
        ), bursts AS (
            SELECT P_ID, source, min(d) AS start_d, max(d) AS end_d,
                   count(*) AS n_days, min(n) AS min_n, max(n) AS max_n
            FROM islands GROUP BY P_ID, source, grp
        ), candidates AS (
            SELECT DISTINCT P_ID FROM (
                SELECT P_ID, source FROM bursts
                GROUP BY P_ID, source
                HAVING min(start_d) >= (
                    SELECT min(DATE) FROM calendar_dim WHERE TERM = 'Autumn'
                ) AND max(end_d) <= (
                    SELECT max(DATE) FROM calendar_dim WHERE TERM = 'Spring'
                ) AND count(*) >= 4
                  AND min(min_n) >= 2 AND max(max_n) <= 4
                  AND min(n_days) >= 3 AND max(n_days) <= 9
            )
        ), gaps AS (
            SELECT P_ID, start_d - lag(start_d) OVER (
                       PARTITION BY P_ID ORDER BY start_d
                   ) AS cycle,
                   start_d - lag(end_d) OVER (
                       PARTITION BY P_ID ORDER BY start_d
                   ) AS quiet_gap
            FROM bursts WHERE source = 'video'
        ), rhythm AS (
            SELECT P_ID, stddev_pop(cycle) AS sd_cycle,
                   min(quiet_gap) AS min_quiet
            FROM gaps GROUP BY P_ID
        ), hours AS (
            SELECT P_ID, stddev_pop(extract(hour FROM ts_local)) AS sd_hour
            FROM activity WHERE source = 'video' GROUP BY P_ID
        ), coverage AS (
            SELECT P_ID, count(*) FILTER (WHERE TERM = 'Spring') AS spring_days
            FROM daily JOIN calendar_dim ON d = DATE
            WHERE source = 'video' GROUP BY P_ID
        )
        SELECT P_ID FROM candidates
        JOIN rhythm USING (P_ID)
        JOIN hours USING (P_ID)
        JOIN coverage USING (P_ID)
        JOIN person_dim USING (P_ID)
        WHERE sd_cycle <= 5.38 AND min_quiet <= 11
          AND sd_hour > 3.98 AND spring_days >= 28
        ORDER BY P_ID
    """).fetchall()]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    p_ids = find(connect(split))
    path = OUT / ("hunt" if split == "training" else split) / "werewolf.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(["Werewolf", p] for p in p_ids)
    print(f"{len(p_ids)} Werewolves -> {path}")
