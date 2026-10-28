"""Compare training detector output with HUNT answers (exact type + P_ID).

Run: uv run python -m detector.score data/HUNT_P_IDs.csv
Or:  uv run python -m detector.score data/HUNT_P_IDs.csv --predictions out/hunt/HUNT_combined.csv
Synthetic example: see docs/competition/scoring.md.
"""

import argparse
import csv
import re
from pathlib import Path

from detector.__main__ import MONSTERS
from detector.combine import OUT, TYPES


# The organisers' HUNT answers file spells three types differently from our submission.
ANSWER_NAMES = {"Doppleganger": "Doppelgänger", "Shapeshifter": "Shape-shifter", "Undead": "Undead Student"}


def read_csv(path, headers=(["Monster Type", "P_ID"],)):
    pairs = set()
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        if next(reader, None) not in headers:
            raise ValueError(f"{path}: header must be one of {headers}")
        for row in reader:
            if len(row) != 2:
                raise ValueError(f"{path}:{reader.line_num}: expected two columns")
            monster, p_id = row
            monster = ANSWER_NAMES.get(monster, monster)
            if monster not in TYPES:
                raise ValueError(f"{path}:{reader.line_num}: unknown Monster Type {monster!r}")
            if not re.fullmatch(r"P\d+", p_id):
                raise ValueError(f"{path}:{reader.line_num}: bad P_ID {p_id!r}")
            pairs.add((monster, p_id))
    return pairs


def read_answers(path):
    # Real HUNT answers use a Monster column; the synthetic example uses Monster Type.
    return read_csv(path, headers=(["Monster", "P_ID"], ["Monster Type", "P_ID"]))


def read_predictions(path):
    if not path.is_dir():
        return read_csv(path)
    # Read all nine fresh rule outputs, never a potentially stale combined copy.
    pairs = set()
    for name in MONSTERS:
        pairs.update(read_csv(path / f"{name}.csv"))
    return pairs


def score(predictions, answers):
    rows = []
    for monster in TYPES:
        predicted = {p for m, p in predictions if m == monster}
        expected = {p for m, p in answers if m == monster}
        correct = len(predicted & expected)
        rows.append({
            "monster": monster,
            "predicted": len(predicted),
            "answers": len(expected),
            "correct": correct,
            "precision": correct / len(predicted) if predicted else None,
            "recall": correct / len(expected) if expected else None,
            "false_positives": sorted(predicted - expected),
            "missed": sorted(expected - predicted),
        })
    return rows


def percent(value):
    return "N/A" if value is None else f"{value:.2%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answers", type=Path, help="HUNT answers CSV (keep under data/)")
    parser.add_argument("--predictions", type=Path, default=OUT / "hunt",
                        help="combined CSV or directory with all nine rule CSVs (default: out/hunt)")
    args = parser.parse_args()
    try:
        rows = score(read_predictions(args.predictions), read_answers(args.answers))
    except (OSError, ValueError, csv.Error) as exc:
        parser.exit(1, f"Scoring failed: {exc}\n")

    print("Scoring: exact (Monster Type, P_ID) pairs; not the official TEST 1 accuracy score.")
    print(f"{'Monster Type':16} {'Predicted':>9} {'Answers':>7} {'Correct':>7} {'FP':>5} {'Missed':>6} {'Precision':>10} {'Recall':>10}")
    for row in rows:
        print(f"{row['monster']:16} {row['predicted']:9} {row['answers']:7} {row['correct']:7} "
              f"{len(row['false_positives']):5} {len(row['missed']):6} "
              f"{percent(row['precision']):>10} {percent(row['recall']):>10}")
    for row in rows:
        print(f"\n{row['monster']}")
        print("  False positives: " + (", ".join(row['false_positives']) or "none"))
        print("  Missed: " + (", ".join(row['missed']) or "none"))


if __name__ == "__main__":
    main()
