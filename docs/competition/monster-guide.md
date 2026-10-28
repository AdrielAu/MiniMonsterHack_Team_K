# Monster Guide (official clue sheet)

From `sources/Mini Monster Hack Monster Guide.pdf`. The clues are **verbatim**, because their thresholds are scored. Don't paraphrase them in code comments or slides; quote them. Table and column names are in `data-model.md`.

## Summary

| Monster | Category | Data | Key threshold |
|---|---|---|---|
| Phantom | Data anomaly | LMS + video | Duplicate activity row |
| Ghost | Behavioural | LMS + video | Active ≥3 of first 4 Autumn weeks; later weekly avg rows <10% of early |
| Zombie | Behavioural | LMS + video | Continuous activity (gaps ≤15 min) for >3 h |
| Vampire | Behavioural | (unspecified) | More night-activity days than day-activity days; all >21 night days |
| Undead Student | Data anomaly | LMS + video | Activity after deregistration date |
| Doppelgänger | Data anomaly | (unspecified) | Pairs with identical activity; submit **both** P_IDs, one per row |
| Werewolf | Behavioural | (unspecified) | Activity spikes throughout Autumn and Spring terms |
| Web Crawler | Behavioural | LMS + video | >200 LMS items or videos within a 12-hour block |
| Shape-Shifter | Data anomaly | (unspecified) | Appears to switch programme during the year |

4 data anomalies, 5 behavioural monsters.

## Clues (verbatim)

**The Phantom** (Data anomaly): "Find students who have been haunted by a phantom that has left them with a duplicate activity row (look at LMS and video activity)."

**The Ghost** (Behavioural monster): "Find students who have been active at least 3 of the first 4 weeks of the Autumn term but then interacted very little for the rest of the academic year (later average weekly count of activity rows is <10% of early weekly average count of activity rows). Look at LMS and video activity."

**The Zombie** (Behavioural monster): "Find students with continuous activity (no gaps longer than 15 minutes) for more than 3 hours. Look at LMS and video activity."

**The Vampire** (Behavioural monster): "Find students who had more days (24 hours) of activity in the night (> midnight to 5 am) than in the day (> 5 am to midnight). All had more than 21 days with activity in the night."

**The Undead Student** (Data anomaly): "Find students with activity after their deregistration date. Look at LMS and video activity."

**The Doppelgänger** (Data anomaly): "Find pairs of students that had suspiciously identical activity. A Doppelgänger will always have a matching pair. You must identify both P_IDs and submit each P_ID on a separate row."

**The Werewolf** (Behavioural monster): "Find students with spikes in activity throughout the Autumn and Spring Terms."

**The Web Crawler** (Behavioural monster): "Find students who in a block of 12 hours had activity with more than 200 lms_items or videos."

**The Shape-Shifter** (Data anomaly): "Find students who appear to switch programme at some point during the year."

## Open questions (settle against the data during HUNT, then record the answer here)

- **Phantom:** Does "duplicate" mean every column except the PK (PIT_ID/PVT_ID) is equal? Or only P_ID + item/video + TIMESTAMP?
- **Ghost:** Is "active" in a week any activity row? Are the "first 4 weeks" WEEK_NUMBER 1–4? Does "rest of the academic year" mean weeks 5–52, or only up to deregistration? Are LMS and video rows counted together?
- **Zombie:** Are gaps measured between consecutive TIMESTAMPs (first-access/first-play times), or from session end (TIMESTAMP + duration)? Are LMS and video merged into one timeline?
- **Vampire:** UTC or UK local time (BST until 29 Oct 2023)? Are boundaries exclusive at 00:00 and 05:00 as written? Is a "day" a calendar date counted once if it has any night (or day) activity? Use ">21 night days" as a sanity check.
- **Undead Student:** Is it activity strictly *after* the deregistration date, or on/after? Persons with a null deregistration date are never Undead.
  - **Decided (training, 28 Oct):** any LMS or video row with `DATE > deregistration_date`, from `detector/undead_student.py`. It finds **92** of the 196 deregistered people (11 in test). The variants all give the same 92 P_IDs: `>` or `>=`, UTC `DATE` or UK-local date, with or without `_COPY_` rows. No one has activity on the deregistration day itself, and the first activity after it falls 1 to 60 days later (median 12), so the boundary choice doesn't matter. 18 people are caught through LMS and 79 through video (some through both), so both sources are needed. P_IDs missing from person_dim have no deregistration date and are excluded. 3 of the 92 deregistered before they registered; they're kept, because the clue only asks about activity after deregistration.
- **Doppelgänger:** What counts as identical: same items/videos at the same timestamps, same counts, or the whole activity profile?
- **Werewolf:** What threshold makes a spike (e.g. a week far above the student's own median)? How many spikes count as "throughout"? Daily or weekly granularity?
- **Web Crawler:** Is the 12 h block a rolling window or fixed blocks? Distinct items/videos, or activity rows? Are LMS and video counted together?
- **Shape-Shifter:** There's no programme column. Should we infer it from module registrations or activity shifting between DEPARTMENT_IDs or module levels? Is it registration data or activity data?
- **Overlaps:** Can one P_ID be more than one monster type? The submission format will tell us.
