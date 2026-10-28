# Werewolf investigations

These are alternative candidates and analysis scripts. The submission detector in
`detector/werewolf.py` now applies the deadline fitted tree as DuckDB SQL, without
requiring scikit-learn at runtime.

Run these commands from the repository root, in this order:

| Script | Purpose | Command |
|---|---|---|
| `candidate.py` | Build and score the broad burst shortlist | `uv run python -m experiments.werewolf.candidate` |
| `classifiers.py` | Extract features and compare classifiers with student-level validation | `uv run --with scikit-learn python -m experiments.werewolf.classifiers` |
| `intensity.py` | Compare daily duration and interaction features | `uv run --with scikit-learn python -m experiments.werewolf.intensity` |
| `training_fit.py` | Compare fitted tree depths on HUNT | `uv run --with scikit-learn python -m experiments.werewolf.training_fit` |
| `fitted_tree.py` | Save the eight-student fitted shortlist and check held-out performance | `uv run --with scikit-learn python -m experiments.werewolf.fitted_tree` |

Inputs remain under ignored `data/`. The organiser-corrected scoring copy is
`data/HUNT_P_IDs_corrected.csv`. Generated tables, candidate CSVs, and model results
remain under `data/werewolf-diagnostics/`; no script writes submission outputs.

The broad candidate finds all six corrected answers with 64 false positives.
The fitted tree finds all six with two false positives on HUNT, but performs poorly
when students are held out. It was selected as a provisional deadline rule and
predicts two TEST students; TEST correctness is unknown.

Place future investigations for another monster under `experiments/<monster>/`.
