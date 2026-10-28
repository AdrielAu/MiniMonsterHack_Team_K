"""Vampire: compare distinct night and daytime activity dates.

Clue: "Find students who had more days (24 hours) of activity in the night
(> midnight to 5 am) than in the day (> 5 am to midnight). All had more than
21 days with activity in the night."
Run: uv run python -m detector.vampire [training|test|predict]
"""

import csv
import sys
from pathlib import Path

from detector.load import connect


def detect(con):
    """Return sorted P_IDs with >21 UK night dates and more night than day dates."""
    return con.execute("""
        WITH days AS (
            SELECT P_ID,
                   count(DISTINCT CAST(ts_local AS DATE)) FILTER (
                       WHERE CAST(ts_local AS TIME) > TIME '00:00:00'
                         AND CAST(ts_local AS TIME) <= TIME '05:00:00'
                   ) AS night_days,
                   count(DISTINCT CAST(ts_local AS DATE)) FILTER (
                       WHERE CAST(ts_local AS TIME) > TIME '05:00:00'
                   ) AS day_days
            FROM activity
            GROUP BY P_ID
        )
        SELECT P_ID FROM days
        WHERE night_days > day_days AND night_days > 21
        ORDER BY P_ID
    """).fetchall()


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    with connect(split) as con:
        people = detect(con)
    output = Path("out") / ("hunt" if split == "training" else split) / "vampire.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Monster Type", "P_ID"])
        writer.writerows(("Vampire", person) for (person,) in people)
    print(f"Vampire: {len(people)} P_IDs -> {output}")
