"""PREDICT: flag the 5 behavioural monsters early, from activity up to 14 Nov 2023 only.

Early-warning rules, each backtested on training cut off at 14 Nov 2023 against the HUNT answers (team pick):
- Ghost: active in 3+ of calendar weeks 1-4 with 200+ rows there, then the weekly rate in the later weeks up to
  the cutoff (weeks 5-7) is under 20% of the weeks 1-4 weekly rate.
- Zombie, Vampire, Web Crawler: the full detector rule unchanged, run on the cut-off data.
- Werewolf: 2+ video bursts (runs of consecutive viewing days), and every burst lasts 3-9 days with 2-4 views a day.
Scores are in docs/competition/predict.md.

Run: uv run python -m detector.predict             writes out/predict/<monster>.csv and PREDICT_combined.csv
     uv run python -m detector.predict training    backtests the rules instead
"""

import csv
import runpy
import sys

from detector import vampire, web_crawler, zombie
from detector.backtest import CUTOFF, backtest
from detector.combine import OUT
from detector.load import connect

# shortcut: thresholds picked on one backtest against HUNT answers; no held-out check.
GHOST_MIN_EARLY_ROWS = 200
GHOST_MAX_RATIO = 0.2
WEREWOLF_MIN_BURSTS = 2


def ghost(con):
    return [r[0] for r in con.execute("""
        WITH wk AS (
            SELECT a.P_ID, c.WEEK_NUMBER AS w, count(*) AS n
            FROM activity a JOIN calendar_dim c USING (DATE)
            GROUP BY 1, 2
        ),
        later_weeks AS (
            SELECT count(DISTINCT WEEK_NUMBER) AS k FROM calendar_dim WHERE WEEK_NUMBER > 4 AND DATE <= ?::DATE
        ),
        p AS (
            SELECT P_ID,
                   count(*) FILTER (WHERE w <= 4) AS active_early,
                   sum(n) FILTER (WHERE w <= 4) AS early,
                   coalesce(sum(n) FILTER (WHERE w > 4), 0) AS later
            FROM wk GROUP BY 1
        )
        SELECT P_ID FROM p JOIN person_dim USING (P_ID), later_weeks
        WHERE active_early >= 3 AND early >= ? AND later / k < ? * early / 4
        ORDER BY P_ID
    """, [CUTOFF, GHOST_MIN_EARLY_ROWS, GHOST_MAX_RATIO]).fetchall()]


def werewolf(con):
    return [r[0] for r in con.execute("""
        WITH daily AS (
            SELECT P_ID, CAST(ts_local AS DATE) AS d, count(*) AS n
            FROM activity WHERE source = 'video' GROUP BY 1, 2
        ),
        islands AS (SELECT *, d - CAST(row_number() OVER (PARTITION BY P_ID ORDER BY d) AS INTEGER) AS grp FROM daily),
        bursts AS (
            SELECT P_ID, count(*) AS n_days, min(n) AS min_n, max(n) AS max_n
            FROM islands GROUP BY P_ID, grp
        )
        SELECT P_ID FROM bursts JOIN person_dim USING (P_ID)
        GROUP BY P_ID
        HAVING count(*) >= ? AND min(n_days) >= 3 AND max(n_days) <= 9 AND min(min_n) >= 2 AND max(max_n) <= 4
        ORDER BY P_ID
    """, [WEREWOLF_MIN_BURSTS]).fetchall()]


RULES = {
    "Ghost": ghost,
    "Zombie": zombie.find,
    "Vampire": lambda con: [p for (p,) in vampire.detect(con)],
    "Werewolf": werewolf,
    "Web Crawler": web_crawler.find,
}

if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "predict"
    if split == "training":
        backtest([(m, m, f) for m, f in RULES.items()])
        sys.exit()
    con = connect(split, cutoff=CUTOFF)
    folder = OUT / "predict"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.csv"):  # stale full-year runs would leak into the combine
        old.unlink()
    for monster, find in RULES.items():
        p_ids = find(con)
        with open(folder / f"{monster.lower().replace(' ', '_')}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Monster Type", "P_ID"])
            w.writerows([monster, p] for p in p_ids)
        print(f"{monster:12} {len(p_ids):4}")
    sys.argv = ["combine", "predict"]
    runpy.run_module("detector.combine", run_name="__main__")
