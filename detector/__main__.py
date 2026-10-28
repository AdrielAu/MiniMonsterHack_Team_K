"""Run all nine detectors on one split, then combine them: the one command for the live demo.

Run: uv run python -m detector [training|test|predict]
Writes out/<stage>/<monster>.csv for each detector, then out/<stage>/<STAGE>_combined.csv with a count per type.
"""

import runpy
import sys
import time

from detector.load import SPLITS

MONSTERS = ["phantom", "ghost", "zombie", "vampire", "undead_student",
            "doppelganger", "werewolf", "web_crawler", "shape_shifter"]

if __name__ == "__main__":
    split = sys.argv[1] if len(sys.argv) > 1 else "training"
    if split not in SPLITS:
        sys.exit(f"split must be one of {list(SPLITS)}")
    start = time.perf_counter()
    # Each detector's own __main__ block does the writing, so this stays in step with running them one by one.
    for m in MONSTERS:
        sys.argv = [m, split]
        runpy.run_module(f"detector.{m}", run_name="__main__")
    sys.argv = ["combine", "hunt" if split == "training" else split]
    runpy.run_module("detector.combine", run_name="__main__")
    print(f"done in {time.perf_counter() - start:.1f}s")
