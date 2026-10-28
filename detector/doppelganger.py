"""Doppelgänger: pairs where one P_ID's whole activity reappears under another.

Clue: "Find pairs of students that had suspiciously identical activity. A
Doppelgänger will always have a matching pair. You must identify both P_IDs
and submit each P_ID on a separate row."
Run: uv run python -m detector.doppelganger [training|test|predict]
"""

import csv
import sys
from pathlib import Path

from detector.load import connect


def detect(con):
    """Return sorted (P_ID, P_ID) pairs: every distinct activity row of the
    smaller side (all columns but P_ID and row ID) also belongs to the other,
    with at least 2 rows shared."""
    return con.execute("""
        WITH rows AS (
            SELECT DISTINCT P_ID, 'L' || md5(concat_ws('|', *COLUMNS(* EXCLUDE (PIT_ID, P_ID)))) AS content
            FROM lms_item_activity_by_session_fact
            UNION
            SELECT DISTINCT P_ID, 'V' || md5(concat_ws('|', *COLUMNS(* EXCLUDE (PVT_ID, P_ID))))
            FROM video_activity_by_view_fact
        ),
        totals AS (SELECT P_ID, count(*) AS n FROM rows GROUP BY P_ID),
        shared AS (
            SELECT a.P_ID AS a, b.P_ID AS b, count(*) AS n
            FROM rows a JOIN rows b ON a.content = b.content AND a.P_ID < b.P_ID
            GROUP BY ALL
        )
        SELECT a, b FROM shared
        JOIN totals ta ON ta.P_ID = a JOIN totals tb ON tb.P_ID = b
        WHERE shared.n >= 2 AND shared.n = least(ta.n, tb.n)
        ORDER BY a, b
    """).fetchall()


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    with connect(split) as con:
        pairs = detect(con)
    output = Path("out") / ("hunt" if split == "training" else split) / "doppelganger.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Monster Type", "P_ID"])
        writer.writerows(("Doppelgänger", person) for pair in pairs for person in pair)
    print(f"Doppelgänger: {len(pairs)} pairs -> {output}")
