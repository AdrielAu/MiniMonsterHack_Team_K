# Scoring

Compare training detector output with the organisers' HUNT answers. This reports our precision and recall per Monster type, not the official TEST 1 accuracy score or an assumed points formula.

Keep the private answers under gitignored `data/`. The real answers are `data/HUNT_P_IDs.csv`: UTF-8 with BOM, header `Monster,P_ID`. `read_answers` in `detector/score.py` maps their spellings Doppleganger, Shapeshifter and Undead to Doppelgänger, Shape-shifter and Undead Student. It also accepts the `Monster Type,P_ID` header used by the synthetic example. Every ID stays text.

Run from the repo root:

```powershell
.venv\Scripts\python.exe -m detector.score data/HUNT_P_IDs.csv
```

The default reads all nine `out/hunt/<monster>.csv` files, including header-only files for rules finding nobody, and fails if any is missing. It ignores the combined file so an older combined copy cannot override fresh rule output. To score a saved combined file instead:

```powershell
.venv\Scripts\python.exe -m detector.score data/HUNT_P_IDs.csv --predictions out/hunt/HUNT_combined.csv
```

Each exact `(Monster Type, P_ID)` pair counts once. Overlaps remain separate findings; a correct ID under the wrong type is a false positive for the predicted type and a miss for the answer type. Precision is correct / predicted; recall is correct / answers. A zero denominator displays `N/A`. The report prints all nine types and full false-positive and missed-ID lists. It only reads inputs and prints to the terminal.

## Synthetic stand-in

These example IDs are invented, not organisers' answers:

```powershell
.venv\Scripts\python.exe -m detector.score docs/competition/scoring-example/answers.csv --predictions docs/competition/scoring-example/predictions.csv
```

Expected: Phantom has 50% precision and recall, false positive `P00000009`, and miss `P00000002`. Ghost has 100% for both despite sharing an ID with Phantom. Zombie has no predictions, `N/A` precision and 0% recall, missing `P00000003`; that same ID is a Vampire false positive (0% precision, `N/A` recall). Both Doppelgänger IDs match at 100%. The other four types have `N/A` for both. The duplicate Phantom row counts once.
