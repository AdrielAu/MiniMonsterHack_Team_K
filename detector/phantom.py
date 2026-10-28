"""Phantom: duplicate activity content within either LMS or video.

Clue: "Find students who have been haunted by a phantom that has left them
with a duplicate activity row (look at LMS and video activity)."
Run: uv run python -m detector.phantom [training|test|predict]
"""

import csv
import sys
from pathlib import Path

from detector.load import connect


def detect(con):
    """Return sorted P_IDs with repeated rows (ignoring only PIT_ID/PVT_ID) on at least 2 dates.

    Duplicates confined to one date are a Zombie's replayed viewing block, not a Phantom (see monster-guide.md).
    """
    return con.execute("""
        SELECT P_ID FROM (
            SELECT P_ID, DATE FROM (
                SELECT * EXCLUDE (PIT_ID)
                FROM lms_item_activity_by_session_fact
                GROUP BY ALL HAVING count(*) > 1
            )
            UNION ALL
            SELECT P_ID, DATE FROM (
                SELECT * EXCLUDE (PVT_ID)
                FROM video_activity_by_view_fact
                GROUP BY ALL HAVING count(*) > 1
            )
        )
        GROUP BY P_ID HAVING count(DISTINCT DATE) >= 2
        ORDER BY P_ID
    """).fetchall()


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    with connect(split) as con:
        people = detect(con)
    output = Path("out") / ("hunt" if split == "training" else split) / "phantom.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Monster Type", "P_ID"])
        writer.writerows(("Phantom", person) for (person,) in people)
    print(f"Phantom: {len(people)} P_IDs -> {output}")
