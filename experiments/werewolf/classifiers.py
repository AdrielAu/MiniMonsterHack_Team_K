"""Private classifier investigation; does not alter detector or submission outputs.

Run: uv run --with scikit-learn python -m experiments.werewolf.classifiers
"""

import csv
import json
import runpy
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from detector.score import read_answers

previous = runpy.run_module("experiments.werewolf.candidate")
con = previous["con"]
out = previous["OUT"]
ids = sorted(previous["predicted"])
answers = {p for m, p in read_answers(Path("data/HUNT_P_IDs_corrected.csv"))
           if m == "Werewolf"}
features = {p: {} for p in ids}


def add(query, source_column=False):
    result = con.execute(query)
    names = [column[0] for column in result.description]
    for row in result.fetchall():
        prefix = row[1] + "_" if source_column else ""
        start = 2 if source_column else 1
        for name, value in zip(names[start:], row[start:]):
            features[row[0]][prefix + name] = float(value) if value is not None else -1.0


add("""
    WITH gaps AS (
        SELECT *, start_d - lag(end_d) OVER (
            PARTITION BY P_ID, source ORDER BY start_d
        ) AS quiet_gap, start_d - lag(start_d) OVER (
            PARTITION BY P_ID, source ORDER BY start_d
        ) AS cycle
        FROM bursts WHERE P_ID IN (SELECT P_ID FROM candidate_sources)
    )
    SELECT P_ID, source, count(*) AS n_bursts, min(n_days) AS min_burst,
           max(n_days) AS max_burst, avg(n_days) AS mean_burst,
           stddev_pop(n_days) AS sd_burst, avg(quiet_gap) AS mean_quiet,
           min(quiet_gap) AS min_quiet, max(quiet_gap) AS max_quiet,
           avg(cycle) AS mean_cycle, stddev_pop(cycle) AS sd_cycle,
           sum(n_days) AS active_days, sum(n_rows) AS n_rows,
           min(min_n) AS min_daily_rows, max(max_n) AS max_daily_rows
    FROM gaps GROUP BY P_ID, source
""", True)
add("""
    WITH events AS (
        SELECT a.P_ID, 'lms' AS source, TIMESTAMP AS ts, LMS_ITEM_ID AS item,
               TOTAL_SECONDS_BEFORE_NEXT_INTERACTION / 60.0 AS duration,
               INTERACTION_COUNT AS interactions, d.MODULE_INSTANCE_ID AS module,
               pm.P_ID IS NOT NULL AS registered
        FROM lms_item_activity_by_session_fact a
        LEFT JOIN lms_item_dim d USING (LMS_ITEM_ID)
        LEFT JOIN (SELECT DISTINCT P_ID, MODULE_INSTANCE_ID
                   FROM person_module_instance_fact) pm
          ON a.P_ID = pm.P_ID AND d.MODULE_INSTANCE_ID = pm.MODULE_INSTANCE_ID
        WHERE a.P_ID IN (SELECT P_ID FROM candidate_sources)
        UNION ALL
        SELECT a.P_ID, 'video', TIMESTAMP, VIDEO_ID,
               TOTAL_MINUTES_DELIVERED, NULL, d.MODULE_INSTANCE_ID,
               pm.P_ID IS NOT NULL
        FROM video_activity_by_view_fact a
        LEFT JOIN video_dim d USING (VIDEO_ID)
        LEFT JOIN (SELECT DISTINCT P_ID, MODULE_INSTANCE_ID
                   FROM person_module_instance_fact) pm
          ON a.P_ID = pm.P_ID AND d.MODULE_INSTANCE_ID = pm.MODULE_INSTANCE_ID
        WHERE a.P_ID IN (SELECT P_ID FROM candidate_sources)
    )
    SELECT P_ID, source, count(DISTINCT item) AS n_items,
           count(DISTINCT module) AS n_modules,
           avg(duration) AS mean_duration, median(duration) AS median_duration,
           stddev_pop(duration) AS sd_duration, max(duration) AS max_duration,
           quantile_cont(duration, 0.9) AS p90_duration,
           avg(interactions) AS mean_interactions, max(interactions) AS max_interactions,
           avg(registered::INTEGER) AS registered_fraction,
           avg(extract(hour FROM timezone('Europe/London', ts))) AS mean_hour,
           stddev_pop(extract(hour FROM timezone('Europe/London', ts))) AS sd_hour,
           avg((extract(second FROM ts) = 0)::INTEGER) AS whole_minute_fraction
    FROM events GROUP BY P_ID, source
""", True)
add("""
    SELECT P_ID, source, count(*) FILTER (WHERE c.TERM = 'Autumn') AS autumn_days,
           count(*) FILTER (WHERE c.TERM = 'Spring') AS spring_days,
           sum(n) FILTER (WHERE c.TERM = 'Autumn') AS autumn_rows,
           sum(n) FILTER (WHERE c.TERM = 'Spring') AS spring_rows,
           count(DISTINCT date_trunc('week', d)) AS active_weeks
    FROM daily LEFT JOIN calendar_dim c ON daily.d = c.DATE
    WHERE P_ID IN (SELECT P_ID FROM candidate_sources) GROUP BY P_ID, source
""", True)

names = sorted({name for person in features.values() for name in person})
x = np.array([[features[p].get(name, -1.0) for name in names] for p in ids])
y = np.array([p in answers for p in ids], dtype=int)
assert set(ids) & answers == answers, "Candidate gate must retain all six corrected answers"
with (out / "classifier_features.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["P_ID", "Werewolf_answer", *names])
    writer.writerows([p, int(label), *row] for p, label, row in zip(ids, y, x))

models = {
    "tree_depth1": DecisionTreeClassifier(max_depth=1, class_weight="balanced", random_state=7),
    "tree_depth2": DecisionTreeClassifier(max_depth=2, min_samples_leaf=3, class_weight="balanced", random_state=7),
    "tree_depth3": DecisionTreeClassifier(max_depth=3, min_samples_leaf=3, class_weight="balanced", random_state=7),
    "logistic_C0.1": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced", max_iter=3000)),
    "logistic_C1": make_pipeline(StandardScaler(), LogisticRegression(C=1, class_weight="balanced", max_iter=3000)),
    "forest_depth3": RandomForestClassifier(n_estimators=200, max_depth=3, min_samples_leaf=3, class_weight="balanced", random_state=7),
    "neighbours3": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3)),
    "naive_bayes": make_pipeline(StandardScaler(), GaussianNB()),
}
report = []
for name, model in models.items():
    for seed in [7, 29, 103]:
        cv = StratifiedKFold(n_splits=6, shuffle=True, random_state=seed)
        probs = cross_val_predict(clone(model), x, y, cv=cv, method="predict_proba")[:, 1]
        for threshold in [0.5, 0.8]:
            predicted = probs >= threshold
            row = dict(model=name, seed=seed, threshold=threshold,
                       correct=int(sum(predicted & (y == 1))),
                       false_positives=int(sum(predicted & (y == 0))),
                       average_precision=float(average_precision_score(y, probs)))
            report.append(row)
            print(row, flush=True)
        with (out / f"classifier_{name}_{seed}_scores.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["P_ID", "Werewolf_answer", "out_of_fold_score"])
            writer.writerows(zip(ids, y.tolist(), probs.tolist()))
tree = clone(models["tree_depth3"]).fit(x, y)
print("Full-data fitted tree (training fit, not validation):")
print(export_text(tree, feature_names=names))
(out / "classifier_results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
