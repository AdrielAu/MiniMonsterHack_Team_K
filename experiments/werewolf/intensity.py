"""Compare daily time/interaction intensity with the previous behavioral features."""

import csv
import json
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from detector.load import connect

out = Path("data/werewolf-diagnostics")
with (out / "classifier_features.csv").open(newline="") as f:
    reader = csv.reader(f)
    original_names = next(reader)[2:]
    rows = list(reader)
ids = [r[0] for r in rows]
features = {r[0]: dict(zip(original_names, map(float, r[2:]))) for r in rows}
y = np.array([int(r[1]) for r in rows])
c = connect()
c.execute("CREATE TABLE candidates AS SELECT unnest(?) AS P_ID", [ids])
c.execute("""
    CREATE TABLE intensity AS
    SELECT P_ID, 'lms' AS source, CAST(timezone('Europe/London', TIMESTAMP) AS DATE) AS d,
           sum(TOTAL_SECONDS_BEFORE_NEXT_INTERACTION) / 60.0 AS minutes,
           sum(INTERACTION_COUNT) AS interactions
    FROM lms_item_activity_by_session_fact JOIN candidates USING (P_ID)
    GROUP BY 1, 2, 3
    UNION ALL
    SELECT P_ID, 'video', CAST(timezone('Europe/London', TIMESTAMP) AS DATE),
           sum(TOTAL_MINUTES_DELIVERED), NULL
    FROM video_activity_by_view_fact JOIN candidates USING (P_ID)
    GROUP BY 1, 2, 3;
""")
result = c.execute("""
    SELECT P_ID, source, avg(minutes) AS daily_mean_minutes,
           stddev_pop(minutes) / nullif(avg(minutes), 0) AS daily_minutes_cv,
           max(minutes) / nullif(median(minutes), 0) AS daily_minutes_peak_ratio,
           quantile_cont(minutes, 0.9) / nullif(median(minutes), 0) AS daily_minutes_p90_ratio,
           max(minutes) AS daily_peak_minutes,
           avg(interactions) AS daily_mean_interactions,
           max(interactions) / nullif(median(interactions), 0) AS daily_interactions_peak_ratio,
           stddev_pop(interactions) / nullif(avg(interactions), 0) AS daily_interactions_cv
    FROM intensity GROUP BY 1, 2
""")
names = [col[0] for col in result.description][2:]
for row in result.fetchall():
    for name, value in zip(names, row[2:]):
        features[row[0]][row[1] + "_" + name] = float(value) if value is not None else -1
all_names = sorted({name for values in features.values() for name in values})
reports = []
models = {
    "logistic_C0.1": make_pipeline(StandardScaler(), LogisticRegression(C=0.1, class_weight="balanced", max_iter=3000)),
    "tree_depth2": DecisionTreeClassifier(max_depth=2, min_samples_leaf=3, class_weight="balanced", random_state=7),
    "tree_depth3": DecisionTreeClassifier(max_depth=3, min_samples_leaf=3, class_weight="balanced", random_state=7),
}
for family, columns in [("intensity_only", [n for n in all_names if "daily_" in n and n not in original_names]),
                        ("behavior_and_intensity", all_names)]:
    x = np.array([[features[p].get(n, -1) for n in columns] for p in ids])
    for name, model in models.items():
        for seed in [7, 29, 103]:
            cv = StratifiedKFold(n_splits=6, shuffle=True, random_state=seed)
            probs = cross_val_predict(clone(model), x, y, cv=cv, method="predict_proba")[:, 1]
            for threshold in [0.5, 0.8]:
                predicted = probs >= threshold
                row = dict(family=family, model=name, seed=seed, threshold=threshold,
                           correct=int(sum(predicted & (y == 1))),
                           false_positives=int(sum(predicted & (y == 0))))
                reports.append(row)
                print(row, flush=True)
(out / "intensity_results.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
