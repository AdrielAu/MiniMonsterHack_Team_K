"""Web Crawler: "Find students who in a block of 12 hours had activity with more than 200 lms_items or videos."

Rule: at least 200 distinct LMS items and videos (counted together) in one fixed 12-hour block, 00:00-12:00 or
12:00-24:00 UTC (TIMESTAMP). Distinct items keep repeat visits and Phantom duplicates out. Chosen against the
HUNT answers (15 correct, 0 false positives); rolling windows added P00017445, a false positive.
Variant counts (fixed vs rolling blocks, rows vs distinct items, UTC vs UK, > vs >=) are in monster-guide.md.

Run: uv run python -m detector.web_crawler [training|test|predict]
Writes out/hunt/web_crawler.csv for training, out/<split>/web_crawler.csv otherwise.
"""

import csv
import sys
from pathlib import Path

from detector.load import connect

OUT = Path(__file__).resolve().parent.parent / "out"


def find(con):
    return [r[0] for r in con.execute("""
        WITH b AS (
            SELECT P_ID, count(DISTINCT item_id) AS n
            FROM activity
            GROUP BY P_ID, time_bucket(INTERVAL 12 hours, ts::TIMESTAMP)
        )
        SELECT DISTINCT P_ID FROM b WHERE n >= 200 ORDER BY P_ID
    """).fetchall()]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    p_ids = find(connect(split))
    path = OUT / ("hunt" if split == "training" else split) / "web_crawler.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Monster Type", "P_ID"])
        w.writerows(["Web Crawler", p] for p in p_ids)
    print(f"{len(p_ids)} Web Crawlers -> {path}")
