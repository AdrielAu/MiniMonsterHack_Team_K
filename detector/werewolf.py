"""Werewolf: "Find students with spikes in activity throughout the Autumn and Spring Terms."

Merge LMS and video, deduplicating activity content within each source, and count
rows per UK-local date in Autumn and Spring. A spike has at least 40 rows and
5 times the student's median count on active dates across those two terms.
Consecutive spike dates form one burst; require two bursts in each term.
Only P_IDs in person_dim qualify. Thresholds are provisional pending HUNT answers.

Run: uv run python -m detector.werewolf [training|test|predict]
Writes out/hunt/werewolf.csv for training, out/<split>/werewolf.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"
# shortcut: team-selected provisional thresholds; tune against released HUNT answers.
MULTIPLIER = 5
MIN_ROWS = 40
MIN_BURSTS_PER_TERM = 2


def find(con, multiplier=MULTIPLIER, min_rows=MIN_ROWS, min_bursts=MIN_BURSTS_PER_TERM):
    return [r[0] for r in con.execute("""
        WITH lms AS (
            SELECT DISTINCT * EXCLUDE (PIT_ID)
            FROM lms_item_activity_by_session_fact
        ), video AS (
            SELECT DISTINCT * EXCLUDE (PVT_ID)
            FROM video_activity_by_view_fact
        ), merged AS (
            SELECT P_ID, CAST(timezone('Europe/London', TIMESTAMP) AS DATE) AS DATE
            FROM lms
            UNION ALL
            SELECT P_ID, CAST(timezone('Europe/London', TIMESTAMP) AS DATE) AS DATE
            FROM video
        ), daily AS (
            SELECT a.P_ID, a.DATE, c.TERM, count(*) AS n
            FROM merged a
            JOIN calendar_dim c USING (DATE)
            JOIN person_dim p USING (P_ID)
            WHERE c.TERM IN ('Autumn', 'Spring')
            GROUP BY 1, 2, 3
        ), baseline AS (
            SELECT P_ID, median(n) AS med FROM daily GROUP BY P_ID
        ), spikes AS (
            SELECT P_ID, TERM, DATE,
                   DATE - lag(DATE) OVER (PARTITION BY P_ID, TERM ORDER BY DATE) AS gap
            FROM daily JOIN baseline USING (P_ID)
            WHERE n >= ? AND n >= ? * med
        ), bursts AS (
            SELECT P_ID, TERM,
                   count(*) FILTER (WHERE gap IS NULL OR gap > 1) AS n_bursts
            FROM spikes GROUP BY P_ID, TERM
        )
        SELECT P_ID FROM bursts
        GROUP BY P_ID
        HAVING count(*) = 2 AND min(n_bursts) >= ?
        ORDER BY P_ID
    """, [min_rows, multiplier, min_bursts]).fetchall()]


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
