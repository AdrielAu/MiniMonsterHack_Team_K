"""Backtest early-warning rules: run them on training cut off at 14 Nov 2023 and score against the HUNT answers.

Run: uv run python -m detector.backtest   (scores the 5 behavioural detectors unchanged on cut-off training)
"""

from pathlib import Path

from detector import ghost, vampire, web_crawler, werewolf, zombie
from detector.load import connect
from detector.score import percent, read_answers, score

CUTOFF = "2023-11-14"
ANSWERS = Path(__file__).resolve().parent.parent / "data" / "HUNT_P_IDs_corrected.csv"

# Each rule takes a connection and returns P_IDs.
BASELINE = {
    "Ghost": ghost.find,
    "Zombie": zombie.find,
    "Vampire": lambda con: [p for (p,) in vampire.detect(con)],
    "Werewolf": werewolf.find,
    "Web Crawler": web_crawler.find,
}


def backtest(rules, con=None):
    """rules: list of (label, monster, find). Prints one scored row per rule."""
    con = con or connect("training", cutoff=CUTOFF)
    answers = read_answers(ANSWERS)
    print(f"{'Rule':40} {'Pred':>5} {'Ans':>4} {'OK':>4} {'FP':>4} {'Miss':>5} {'Precision':>10} {'Recall':>8}")
    for label, monster, find in rules:
        row = next(r for r in score({(monster, p) for p in find(con)}, answers) if r["monster"] == monster)
        print(f"{label:40} {row['predicted']:5} {row['answers']:4} {row['correct']:4} "
              f"{len(row['false_positives']):4} {len(row['missed']):5} "
              f"{percent(row['precision']):>10} {percent(row['recall']):>8}")


if __name__ == "__main__":
    backtest([(m, m, f) for m, f in BASELINE.items()])
