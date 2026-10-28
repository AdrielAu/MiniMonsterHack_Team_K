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

- **Phantom (decided against training, 28 Oct 2026):** Within each activity fact separately, flag a P_ID if at least two rows match on **every column except PIT_ID/PVT_ID**. Take the union across LMS and video; output each P_ID once. Do not use the reduced `activity` view: it omits fields needed to distinguish sessions and viewing types. No date, registration, or `_COPY_` filter is imposed by the clue. `detector/phantom.py` writes `out/hunt/phantom.csv`.
  - **Chosen:** 63,317 duplicate LMS groups (58 P_IDs), 6,969 duplicate video groups (70 P_IDs); 51 P_IDs overlap, giving **77 unique P_IDs**. Every group has exactly two rows. All 77 occur in person_dim.
  - **Including the PK:** the identical groups and P_ID sets, also **77**. Ignoring a technical row ID permits a duplicate to have a new ID without weakening equality of the activity content; this choice does not change the training result.
  - **Rejected, P_ID + item/video + TIMESTAMP only:** 63,319 LMS groups (60 P_IDs) and 7,398 video groups (91 P_IDs), **100** unique P_IDs. This adds rows whose other activity fields differ. For example, P00012772 has the same LMS item/time but different LOGIN_ID, interaction count (2 vs 1), and duration (567 vs 4 seconds); P00000061 has matching video/time but different VIEWING_TYPE.
  - **Rejected, repeated row ID within a P_ID:** **98** unique P_IDs (58 LMS, 91 video, 51 overlap); reused video IDs can have different VIEWING_TYPE and do not prove duplicate activity content.
  - **Evidence for HUNT:** P00000693 has two identical LMS rows for PIT0014193262, item 2120762263, 2023-09-28 16:54:43.143 UTC, LOGIN_ID L00035058, interaction count 1 and duration 40 seconds. P00000097 has two identical video rows for PVT0001278917, video V000002334, 2023-11-12 22:31:25 UTC, 7.1179 minutes, Interactive Desktop On Demand.
  - **Validation limit:** this is a literal activity-content rule, not a tuned count threshold. The organisers' scoring answer and released HUNT P_IDs are still unavailable; validate against them before TEST 1.
- **Ghost:** Is "active" in a week any activity row? Are the "first 4 weeks" WEEK_NUMBER 1–4? Does "rest of the academic year" mean weeks 5–52, or only up to deregistration? Are LMS and video rows counted together?
  - **Decided (training, 28 Oct):** LMS and video rows counted together, placed in weeks by calendar `WEEK_NUMBER` (rows dated outside the calendar dropped). Active in at least 3 of weeks 1–4 (any row), and (rows in weeks 5–52 ÷ 48) < 0.1 × (rows in weeks 1–4 ÷ 4). P_IDs missing from person_dim dropped. From `detector/ghost.py`. It finds **148** P_IDs (14 in test). The ratio rises smoothly through 0.1 with no natural gap, so the clue's threshold is applied as written. Only 6 of the 148 are deregistered, so the rule isn't just catching dropouts. Rows vs distinct event IDs give the same result, so Phantom duplicates don't matter. Variants rejected:
    - Early average ÷ active early weeks instead of ÷4: 188 (adds 39). This loosens the rule for anyone with a blank early week.
    - Later window ending at the deregistration week: 143 (drops P00004182, P00005594, P00007911, P00009295, P00015883, P00017094). The clue says "rest of the academic year" with no withdrawal carve-out.
    - Keeping P_IDs missing from person_dim: 149 (adds P00649204, 23 video rows in total, ratio 0.054). No clue covers orphan IDs, and false positives cost points.
  - **Overlaps:** P00014866 is also a Phantom. P00005594, P00007911, P00009295 and P00015883 are also Undead Students.
- **Zombie:** Are gaps measured between consecutive TIMESTAMPs (first-access/first-play times), or from session end (TIMESTAMP + duration)? Are LMS and video merged into one timeline?
- **Vampire:** UTC or UK local time (BST until 29 Oct 2023)? Are boundaries exclusive at 00:00 and 05:00 as written? Is a "day" a calendar date counted once if it has any night (or day) activity? Use ">21 night days" as a sanity check.
- **Undead Student:** Is it activity strictly *after* the deregistration date, or on/after? Persons with a null deregistration date are never Undead.
  - **Decided (training, 28 Oct):** any LMS or video row with `DATE > deregistration_date`, from `detector/undead_student.py`. It finds **92** of the 196 deregistered people (11 in test). The variants all give the same 92 P_IDs: `>` or `>=`, UTC `DATE` or UK-local date, with or without `_COPY_` rows. No one has activity on the deregistration day itself, and the first activity after it falls 1 to 60 days later (median 12), so the boundary choice doesn't matter. 18 people are caught through LMS and 79 through video (some through both), so both sources are needed. P_IDs missing from person_dim have no deregistration date and are excluded. 3 of the 92 deregistered before they registered; they're kept, because the clue only asks about activity after deregistration.
- **Doppelgänger:** What counts as identical: same items/videos at the same timestamps, same counts, or the whole activity profile?
- **Werewolf:** What threshold makes a spike (e.g. a week far above the student's own median)? How many spikes count as "throughout"? Daily or weekly granularity?
- **Web Crawler:** Is the 12 h block a rolling window or fixed blocks? Distinct items/videos, or activity rows? Are LMS and video counted together?
  - **Decided (training, 28 Oct):** more than 200 **distinct** LMS items and videos, counted together, in any rolling 12-hour window that starts at one of the student's rows (UTC `TIMESTAMP`). From `detector/web_crawler.py`. It finds **16** P_IDs, all in person_dim (0 in test, where no variant finds anyone: the busiest window there has 148 rows). There's no natural gap: per-student maxima tail off smoothly past 200 (p99.9 is about 232 rows), so the clue's threshold is applied as written. Most of the 16 open hundreds of distinct items in minutes to a few hours (P00010833: 529 items in 2 minutes). Distinct items follow the clue's wording ("200 lms_items or videos") and favour precision, since false positives cost points. They also make duplicate rows irrelevant. Variants rejected:
    - Activity rows with exact duplicates collapsed: 18 (adds P00002955, 345 rows of 177 items, and P00010487, 232 video views of 148 videos). These two are crawler-like on volume but aren't under the stricter reading, so they're left out. Revisit them first if the HUNT answers show we missed Web Crawlers.
    - Activity rows with duplicates counted: 20 (also adds P00008975 and P00000693, Phantoms whose rows are all doubled: 128 and 101 real rows).
    - Fixed 12 h blocks: 14 in UTC (also drops P00017445, whose window crosses midnight UTC, and P00000016). The result depends on where blocks start, and the clue names no alignment, so rolling it is.
    - Counting LMS and video separately (>200 of either) adds nothing: P00010487 is the only video-led candidate.
- **Shape-Shifter:** There's no programme column. Should we infer it from module registrations or activity shifting between DEPARTMENT_IDs or module levels? Is it registration data or activity data?
- **Overlaps:** Can one P_ID be more than one monster type? The submission format will tell us.
