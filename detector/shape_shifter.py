"""Shape-shifter: P_IDs carrying copied activity rows (ID `<id>_COPY_<P_ID>`).

Clue: "Find students who appear to switch programme at some point during the year."
Each Shape-shifter has copied rows on one date, on modules it isn't registered on,
usually in a department absent from the rest of its activity.
Run: uv run python -m detector.shape_shifter [training|test|predict]
"""

import csv
import sys
from pathlib import Path

from detector.load import connect


def detect(con):
    """Return sorted P_IDs with at least one LMS or video row whose ID holds `_COPY_`."""
    # shortcut: keys on the ID marker, not behaviour; revisit if the released HUNT answers disagree.
    rows = con.execute("""
        SELECT P_ID FROM lms_item_activity_by_session_fact WHERE PIT_ID LIKE '%\\_COPY\\_%' ESCAPE '\\'
        UNION
        SELECT P_ID FROM video_activity_by_view_fact WHERE PVT_ID LIKE '%\\_COPY\\_%' ESCAPE '\\'
        ORDER BY P_ID
    """).fetchall()
    return [p for (p,) in rows]


if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    with connect(split) as con:
        people = detect(con)
    output = Path("out") / ("hunt" if split == "training" else split) / "shape_shifter.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Monster Type", "P_ID"])
        writer.writerows(("Shape-shifter", p) for p in people)
    print(f"Shape-shifter: {len(people)} P_IDs -> {output}")
