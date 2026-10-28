"""Shared loader: one DuckDB connection with the 8 tables as views over the CSVs.

Usage:  from detector.load import connect;  con = connect("training")
Run:    uv run python -m detector.load [training|test|predict]   (prints row counts)

Views are named without the la_mmh_ / split prefix: calendar_dim, lms_item_dim,
module_instance_dim, video_dim, person_dim, person_module_instance_fact,
video_activity_by_view_fact, lms_item_activity_by_session_fact, plus `activity`
(LMS sessions and video views merged into one timeline).
"""

import sys
from datetime import date
from pathlib import Path

import duckdb

DATA = Path(__file__).resolve().parent.parent / "data"
SPLITS = {"training": "Training", "test": "Test", "predict": "Predict"}
GENERAL = ["calendar_dim", "lms_item_dim", "module_instance_dim", "video_dim"]
PER_SPLIT = [
    "person_dim",
    "person_module_instance_fact",
    "video_activity_by_view_fact",
    "lms_item_activity_by_session_fact",
]
# Pin LMS_ITEM_ID to text (it's all digits) so dim and fact always join on the same type.
TYPES = "{'LMS_ITEM_ID': 'VARCHAR'}"


def _view(con, name, path, where=""):
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: copy the organisers' data into data/ (see AGENTS.md)")
    # Views can't take bound parameters, so the path is inlined (quotes escaped).
    p = path.as_posix().replace("'", "''")
    types = f", types={TYPES}" if name.startswith("lms_item") else ""
    con.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv('{p}', header=true, nullstr='null'{types}){where}")


def connect(split="training", cutoff=None):
    """cutoff ('YYYY-MM-DD'): keep only activity on or before that UK-local date (PREDICT's 14 Nov 2023 rule)."""
    if split not in SPLITS:
        raise ValueError(f"split must be one of {list(SPLITS)}")
    where = ""
    if cutoff is not None:
        cutoff = date.fromisoformat(cutoff)  # validates before it's inlined into the view
        where = f" WHERE CAST(timezone('Europe/London', TIMESTAMP) AS DATE) <= DATE '{cutoff}'"
    con = duckdb.connect(config={"TimeZone": "UTC"})
    for t in GENERAL:
        _view(con, t, DATA / "General Files" / f"la_mmh_{t}.csv")
    for t in PER_SPLIT:
        _view(con, t, DATA / SPLITS[split] / f"la_mmh_{split}_{t}.csv", where if t.endswith("_fact") and "activity" in t else "")
    # One row per LMS session or video view. TIMESTAMP is UTC; ts_local is UK time.
    con.execute("""
        CREATE VIEW activity AS
        SELECT P_ID, 'lms' AS source, PIT_ID AS event_id, LMS_ITEM_ID AS item_id, DATE,
               TIMESTAMP AS ts, timezone('Europe/London', TIMESTAMP) AS ts_local
        FROM lms_item_activity_by_session_fact
        UNION ALL
        SELECT P_ID, 'video', PVT_ID, VIDEO_ID, DATE,
               TIMESTAMP, timezone('Europe/London', TIMESTAMP)
        FROM video_activity_by_view_fact
    """)
    return con


if __name__ == "__main__":
    con = connect(sys.argv[1] if len(sys.argv) > 1 else "training")
    for t in GENERAL + PER_SPLIT + ["activity"]:
        print(f"{t:36} {con.execute(f'SELECT count(*) FROM {t}').fetchone()[0]:>12,}")
