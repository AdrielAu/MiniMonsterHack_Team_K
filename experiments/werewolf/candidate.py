"""Exploratory candidate only; run python -m experiments.werewolf.candidate.

Writes private diagnostics under data/, never submission outputs.
"""

import csv
from detector.load import DATA, connect
from detector.score import read_answers

OUT = DATA / "werewolf-diagnostics"
OUT.mkdir(exist_ok=True)
con = connect("training")
con.execute("""
    CREATE TABLE daily AS
    SELECT P_ID, source, CAST(ts_local AS DATE) AS d, count(*) AS n
    FROM activity GROUP BY 1, 2, 3;

    CREATE TABLE bursts AS
    WITH islands AS (
        SELECT *, d - CAST(row_number() OVER (
            PARTITION BY P_ID, source ORDER BY d
        ) AS INTEGER) AS grp
        FROM daily
    )
    SELECT P_ID, source, min(d) AS start_d, max(d) AS end_d,
           count(*) AS n_days, sum(n) AS n_rows, min(n) AS min_n, max(n) AS max_n
    FROM islands GROUP BY P_ID, source, grp;

    CREATE TABLE candidate_sources AS
    SELECT P_ID, source FROM bursts
    GROUP BY P_ID, source
    HAVING min(start_d) >= (SELECT min(DATE) FROM calendar_dim WHERE TERM = 'Autumn')
       AND max(end_d) <= (SELECT max(DATE) FROM calendar_dim WHERE TERM = 'Spring')
       AND count(*) >= 4
       AND min(min_n) >= 2 AND max(max_n) <= 4
       AND min(n_days) >= 3 AND max(n_days) <= 9;

    CREATE TABLE metrics AS
    WITH gaps AS (
        SELECT *, start_d - lag(end_d) OVER (
            PARTITION BY P_ID, source ORDER BY start_d
        ) AS quiet_gap, start_d - lag(start_d) OVER (
            PARTITION BY P_ID, source ORDER BY start_d
        ) AS cycle
        FROM bursts JOIN candidate_sources USING (P_ID, source)
    )
    SELECT P_ID, source, count(*) AS n_bursts, avg(n_days) AS burst_days,
           avg(n_rows) AS burst_rows, avg(quiet_gap) AS quiet_gap,
           avg(cycle) AS cycle_days, stddev_pop(cycle) / avg(cycle) AS cycle_cv
    FROM gaps GROUP BY P_ID, source;
""")
answers = {p for m, p in read_answers(DATA / "HUNT_P_IDs_corrected.csv")
           if m == "Werewolf"}
predicted = {p for p, in con.execute("SELECT DISTINCT P_ID FROM candidate_sources").fetchall()}
active = {p for p, in con.execute("SELECT DISTINCT P_ID FROM daily").fetchall()}
observable = answers & active
with (OUT / "training_candidate.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Monster Type", "P_ID"])
    writer.writerows(("Werewolf", p) for p in sorted(predicted))
result = con.execute("SELECT * FROM metrics ORDER BY P_ID, source")
with (OUT / "training_candidate_metrics.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([column[0] for column in result.description] + ["HUNT_answer"])
    writer.writerows((*row, row[0] in answers) for row in result.fetchall())
print(f"Candidate: {len(predicted)}; correct: {len(predicted & answers)}; "
      f"FP: {len(predicted - answers)}; observable recall: "
      f"{len(predicted & observable)}/{len(observable)}")
print("Zero-activity answers remaining: " + (", ".join(sorted(answers - active)) or "none"))
