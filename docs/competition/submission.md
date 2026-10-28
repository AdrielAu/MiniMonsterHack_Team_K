# Submission

How to fill the organisers' templates in `/Submissions/`. These are the **master templates**: never edit them. Team copies live in the private Teams channel.

**Team:** K, "Nightmare on Git Street". File prefix: `TEAMK_NightmareOnGitStreet_`

| Stage | Template | Our file |
|---|---|---|
| HUNT | `TEAMLETTER_NAME_HUNT_Submission_Workbook.xlsx` | `TEAMK_NightmareOnGitStreet_HUNT_Submission.xlsx` |
| TEST 1 | `TEAMLETTER_NAME_TEST1_Submission_Workbook.xlsx` | `TEAMK_NightmareOnGitStreet_TEST1_Submission.xlsx` |
| PREDICT | `TEAMLETTER_NAME_PREDICT_Submission_Workbook.xlsx` | `TEAMK_NightmareOnGitStreet_PREDICT_Submission.xlsx` |
| BUILD code | `TEAMLETTER_NAME_Monster_Detector_Code.zip` (empty folder) | `TEAMK_NightmareOnGitStreet_Monster_Detector_Code.zip` |
| PREDICT code | `TEAMLETTER_NAME_PREDICT_Code.zip` (empty folder) | `TEAMK_NightmareOnGitStreet_PREDICT_Code.zip` |
| Slides (all stages) | `Mini_Monster_Hack_Team_Submission_Template.pptx` | `TEAMK_NightmareOnGitStreet_Slides.pptx` |

## Workbooks: we use the MANUAL COMBINED route

Each workbook offers two routes: per-monster tabs feeding AUTO COMBINED, or MANUAL COMBINED. Only one is needed, and **we use MANUAL COMBINED** (sheet `HUNT_MANUAL_COMBINED` / `TEST1_MANUAL_COMBINED` / `PREDICT_MANUAL_COMBINED`; column A = Monster Type, column B = P_ID).

- **Code must never write the `.xlsx` directly.** AUTO COMBINED uses dynamic-array formulas (`FILTER`/`VSTACK`), and saving with openpyxl or similar breaks them.
- Instead, the detector writes a paste-ready CSV per stage: two columns `Monster Type,P_ID`, one row per finding, with no extra columns. A human pastes it into MANUAL COMBINED in Excel and saves.
- Monster Type must match the template's REFERENCE sheet **exactly**: `Phantom`, `Ghost`, `Zombie`, `Vampire`, `Undead Student`, `Doppelgänger`, `Werewolf`, `Web Crawler`, `Shape-shifter`. Note the umlaut, and the lowercase "s" in `Shape-shifter`.
- Doppelgänger: both P_IDs of each pair, each on its own row.
- P_IDs are kept as text with leading characters intact (e.g. `P000005255`). Check that Excel didn't reformat them after pasting.
- PREDICT takes **only the 5 behavioural monsters**: Ghost, Zombie, Vampire, Werewolf, Web Crawler.

## Before posting "ready for checking"

- [ ] **HUNT copy: delete the template's dummy P_IDs** (`09009090`, `0900909` on HUNT_Phantom; `0909090090` on HUNT_Ghost). AUTO COMBINED counts them, so they would be submitted as wrong answers.
- [ ] Team name and members are filled in on START HERE.
- [ ] The per-monster tabs and AUTO COMBINED are left empty (one route only). The TEST1/PREDICT AUTO COMBINED show `#VALUE!` when empty; that's expected.
- [ ] File is saved in the private Teams channel under our file name.

## Before posting FINAL

Readiness checklist supplied by the team on 28 October 2026:

- [ ] Completed and saved the HUNT submission.
- [ ] Built and tested the Monster Detector on TEST 1.
- [ ] Saved the TEST 1 Excel submission and slides.
- [ ] Saved the working detector code.
- [ ] Completed the SHOWCASE slides showing the strongest work the team produced.
- [ ] Made sure the detector/output is ready to demonstrate.
- [ ] Saved any PREDICT work completed and wanted for inclusion (PREDICT is optional).

## Slides (`.pptx`)

- **15 slides maximum.** Each section has core slides plus up to 2 optional evidence slides. Delete the optional ones we don't use.
- Full P_ID lists go in Excel, never on slides. Slides show counts, charts and 1–3 examples.
- Sections and what they ask:
  - **HUNT** (slide 2): our approach; what gave each monster away; what we found (counts/chart).
  - **BUILD** (slide 5): what we built (explained for non-experts); the signals it uses; a screenshot of it running on TEST data.
  - **TEST** (slide 6): result summary; a large evidence visual; 1–2 observations.
  - **PREDICT** (slides 9–10): the monsters we chose; our definition of "starting to transform"; early-warning signals; who we flagged and why; evidence.
  - **SHOWCASE** (slides 13–14): one large best-output screenshot. Optional: what we're proud of, **how we used AI** (and what we checked or built ourselves), and advanced work.
- **The detector must be demoed live** on the TEST data ("call us over"), so keep it to one fast command.
