# PREDICT early-warning rules

Only activity up to **14 Nov 2023** (UK-local date, inclusive) is used: `connect(split, cutoff="2023-11-14")`.
"Starting to transform" means the monster's pattern is already visible in that early slice of the year.

Run: `uv run python -m detector.predict` (writes `out/predict/`), `uv run python -m detector.predict training` (backtest).

## Chosen rules and backtest

Training cut off at 14 Nov 2023, scored against `data/HUNT_P_IDs_corrected.csv`. 11,276 training students are active by the cutoff.

| Monster | Early-warning rule | Flagged | Correct | Precision | Recall | Base rate |
|---|---|---|---|---|---|---|
| Ghost | Active 3+ of weeks 1–4 with 200+ rows, then weeks 5–7 weekly rate < 20% of weeks 1–4 | 21 | 5 | 23.8% | 8.6% | 0.5% |
| Zombie | Full detector: same-day replayed video views, or a 3h+ video run with no gap over 15 min | 4 | 3 | 75.0% | 5.1% | 0.5% |
| Vampire | Full detector: more night than day dates, 21+ night dates | 68 | 67 | 98.5% | 67.7% | 0.9% |
| Werewolf | 2+ video bursts, each 3–9 days at 2–4 views a day | 57 | 5 | 8.8% | 83.3% | 0.05% |
| Web Crawler | Full detector: 200+ distinct items in one 12h block | 2 | 2 | 100% | 4.3% | 0.4% |

## Candidates rejected

- Ghost: lower floors (0/100 rows) or looser ratios (30%) raise recall but drop precision to 2–17%.
- Zombie: replay alone 5.8%; video run > 90 min 40%, > 60 min 5.9%.
- Vampire: lowering the 21-night floor adds only false positives (recall stays 67.7%).
- Werewolf: 3+ bursts gives 20% precision but 1 of 6; the full detector flags nobody, as it needs Spring term.
- Web Crawler: 150/100/75/50 items add false positives (67%/33%/6%/4%). 5 of the 47 aren't active by the cutoff.
