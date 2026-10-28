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
  - **Decided (training, 28 Oct):** LMS and video merged into one timeline of **distinct** UTC `TIMESTAMP`s per P_ID. A run breaks wherever consecutive timestamps are more than 15 minutes apart. A P_ID is a Zombie if any run spans more than 3 hours from its first to its last timestamp. From `detector/zombie.py`. It finds **25** P_IDs, all in person_dim (1 in test: P00018118). Results don't depend on `>` or `>=` at 15 minutes, since no gap sits exactly on the boundary. There's no natural cliff: the longest runs per student tail off smoothly (82 over 2 h, 45 over 2.5 h, 25 over 3 h, 12 over 3.5 h, 5 over 4 h), so the clue's thresholds are applied as written. Most qualifying runs start between 00:00 and 02:00 UTC, which may overlap with Vampire. Only P00009298 is also a Phantom. Variants rejected:
    - Session end (TIMESTAMP + TOTAL_SECONDS_BEFORE_NEXT_INTERACTION or TOTAL_MINUTES_DELIVERED) to the next start: **8,681** P_IDs (7,643 even when the span is measured between start times). Any long lecture video or idle LMS session (LMS p99 is 9,566 s, video p99 is 121 min) bridges gaps, so a third of all students would qualify. That isn't a monster signal.
    - LMS and video as separate timelines: 20 LMS-only, 2 video-only, union of **22**, a strict subset that loses P00004190, P00009298 and P00012772, whose runs only stay unbroken when both sources are combined. The clue says "look at LMS and video activity", so they're merged.
    - Timestamps not deduplicated: an LMS row and a video row at the same instant can take the gap in either order, letting a tied row join the previous run across a long gap (one false "run" spanned 5.7 h with only 2 rows). That bug inflated an early count to 324 (then 33). Deduplicating timestamps fixes it.
    - Sensitivity: a 14-minute gap gives 17, 16 min gives 47, 20 min gives 91, 30 min gives 166. The rule sits on a smooth slope, so it should be checked against the HUNT answers before TEST 1.
  - **Evidence for HUNT:** P00004100 has 97 LMS accesses from 00:00:42 to 04:59:55 UTC on 19 Mar 2024 (4.99 h). The largest gap is 13 min and the median is 2.3 min. It did the same the night before (4.8 h on 18 Mar) and has a third 3.2 h run on 22 Feb. P00020056 has 78 accesses (74 LMS, 4 video) from 23:44 on 3 Jan to 04:52 UTC on 4 Jan 2024 (5.13 h, the longest in training), with a largest gap of 14.2 min. It has three more runs of over 3 h that week (1, 5 and 8 Jan).
- **Vampire (decided against training, 28 Oct 2026):** Merge LMS and video activity and count distinct UK-local calendar dates separately for night (`00:00 < time <= 05:00`) and day (`time > 05:00`). A date with both periods counts once in each. Flag when night dates exceed day dates and night dates >21. Use activity start timestamps, not durations; impose no calendar, registration or copied-row filter. `detector/vampire.py` writes `out/hunt/vampire.csv` with **91 P_IDs**.
  - **Timezone and endpoints:** UTC and UK-local time, each with `(00:00,05:00]`, `[00:00,05:00)` or `(00:00,05:00)`, all select the same **91**. UK time follows the data-model guidance; the chosen endpoints follow the clue's > midnight and >5 am split.
  - **Rejected, no >21-night-date requirement:** **139** UK / **137** UTC. The 48 extra UK candidates have only 1–15 night dates, while the chosen 91 have 163–281 night dates and exceed their day-date totals by 5–37.
  - **Rejected, counting activity rows instead of dates:** **93** with >21 night dates in either timezone (154 UK / 152 UTC without that requirement). The two extra UK candidates fail the date comparison: P00004135 has 24 night / 25 day dates; P00010431 has 22 / 26. The clue asks for days, not row volume.
  - **Source and data-quirk checks:** LMS alone selects the same 91; video alone selects only 74. Keep both sources as activity evidence. Removing `_COPY_` rows or requiring person_dim membership leaves the same 91; duplicate rows cannot inflate distinct-date counts.
  - **Evidence for HUNT:** P00000775 has **167 night / 158 day dates** (UTC: 167 / 157); its first UK night activity is LMS PIT0011516721 at 2023-10-02 02:40:42 UK (01:40:42 UTC). P00013423 has **273 night / 236 day dates** (UTC: 278 / 223); first UK night activity is LMS PIT0009076779 at 2023-10-02 02:24:17 UK (01:24:17 UTC).
  - **Validation limit:** timezone, boundary and counting variants were investigated against training; official HUNT answer P_IDs are not available locally. Score against them when released, before TEST 1; 91 is a rule-based finding, not a verified accuracy score.
- **Undead Student:** Is it activity strictly *after* the deregistration date, or on/after? Persons with a null deregistration date are never Undead.
  - **Decided (training, 28 Oct):** any LMS or video row with `DATE > deregistration_date`, from `detector/undead_student.py`. It finds **92** of the 196 deregistered people (11 in test). The variants all give the same 92 P_IDs: `>` or `>=`, UTC `DATE` or UK-local date, with or without `_COPY_` rows. No one has activity on the deregistration day itself, and the first activity after it falls 1 to 60 days later (median 12), so the boundary choice doesn't matter. 18 people are caught through LMS and 79 through video (some through both), so both sources are needed. P_IDs missing from person_dim have no deregistration date and are excluded. 3 of the 92 deregistered before they registered; they're kept, because the clue only asks about activity after deregistration.
- **Doppelgänger:** What counts as identical: same items/videos at the same timestamps, same counts, or the whole activity profile?
  - **Decided (training, 28 Oct):** a pair is two P_IDs where every distinct activity row of the smaller side (matching on every column except P_ID and PIT_ID/PVT_ID, LMS and video together) also belongs to the other, with at least 2 rows shared. Submit both P_IDs. From `detector/doppelganger.py`. It finds **30 pairs, 60 P_IDs** (5 pairs in test, 5 in predict). Every pair is a real student plus one of the 30 P_IDs missing from person_dim. The missing ID holds only video rows: a copy of the student's **entire** video history (same video, timestamp, minutes and viewing type, new PVT_ID). Every missing ID is in exactly one pair. Copies range from 2 to 375 rows. The cut-off is clean: the best non-pair covers 14% of the smaller side, through 1 shared row. The `_COPY_` rows are unrelated: none of their owners is in a pair. Variants rejected:
    - Full identity both ways: 13 pairs. This drops the 17 students who also have LMS activity, which the copy leaves out (e.g. P00019901, 2,377 rows, whose 375 video views reappear as P00624727).
    - Item/video + timestamp only: the same 30. The stricter whole-row match fits "suspiciously identical".
    - No minimum on shared rows: the same 30. The minimum of 2 guards against a 1-row person matching by chance; the smallest real pairs share 2.
    - Real students only (dropping the missing IDs): 30 rows. The clue says "You must identify both P_IDs". **Risk:** if the organisers' answer only lists person_dim P_IDs, our 30 copy IDs score as false positives.
    - Same item sequence at shifted times: the only real-real matches are 3–18 repeats of one LMS item at unrelated times. That's coincidence, not a copy.
- **Werewolf:** What threshold makes a spike (e.g. a week far above the student's own median)? How many spikes count as "throughout"? Daily or weekly granularity?
- **Web Crawler:** Is the 12 h block a rolling window or fixed blocks? Distinct items/videos, or activity rows? Are LMS and video counted together?
  - **Decided (training, 28 Oct):** more than 200 **distinct** LMS items and videos, counted together, in any rolling 12-hour window that starts at one of the student's rows (UTC `TIMESTAMP`). From `detector/web_crawler.py`. It finds **16** P_IDs, all in person_dim (0 in test, where no variant finds anyone: the busiest window there has 148 rows). There's no natural gap: per-student maxima tail off smoothly past 200 (p99.9 is about 232 rows), so the clue's threshold is applied as written. Most of the 16 open hundreds of distinct items in minutes to a few hours (P00010833: 529 items in 2 minutes). Distinct items follow the clue's wording ("200 lms_items or videos") and favour precision, since false positives cost points. They also make duplicate rows irrelevant. Variants rejected:
    - Activity rows with exact duplicates collapsed: 18 (adds P00002955, 345 rows of 177 items, and P00010487, 232 video views of 148 videos). These two are crawler-like on volume but aren't under the stricter reading, so they're left out. Revisit them first if the HUNT answers show we missed Web Crawlers.
    - Activity rows with duplicates counted: 20 (also adds P00008975 and P00000693, Phantoms whose rows are all doubled: 128 and 101 real rows).
    - Fixed 12 h blocks: 14 in UTC (also drops P00017445, whose window crosses midnight UTC, and P00000016). The result depends on where blocks start, and the clue names no alignment, so rolling it is.
    - Counting LMS and video separately (>200 of either) adds nothing: P00010487 is the only video-led candidate.
- **Shape-Shifter:** There's no programme column. Should we infer it from module registrations or activity shifting between DEPARTMENT_IDs or module levels? Is it registration data or activity data?
  - **Decided (training, 28 Oct):** Activity data. Flag a P_ID with at least one **copied activity row**, an LMS or video row whose PIT_ID/PVT_ID is `<id>_COPY_<P_ID>`. The suffix is always the row's own P_ID. From `detector/shape_shifter.py`. It finds **79** P_IDs (10 in test, 9 in predict), all in person_dim, with no overlap with any other HUNT list. Why it reads as a programme switch: each of the 79 has its copied rows (2–33, median 9) on **exactly one date**. Every one has at least one copied row on a module it isn't registered on (77 have only those), and for 71 the copied rows are in a department missing from the rest of its activity. The original IDs (without the suffix) almost never exist (5 of 839), and the copied content matches no other student's rows, so this isn't Phantom or Doppelgänger. Variants rejected:
    - Copied rows only in a department absent from the rest of the student's activity: **71** (drops P00005827, P00010102, P00010481, P00011971, P00013718, P00017234, P00018141, P00021411). They carry the same marker on the same one-day pattern, and their copied rows are still on unregistered modules, so there's no sign they're false positives.
    - Activity moves cleanly between departments (every department's last date before the next one's first date): 61 P_IDs, only 9 with 10+ rows on each side. Noisy, and no cliff.
    - Registered, but no activity on any registered module: 98 P_IDs, median 4 rows. Mostly low-activity students.
    - Autumn vs Spring Mandatory-module sets that rarely go together (each set held by 3+, 5+ or 10+ students, the pair by at most 2): 7 / 4 / 1. Registration data shows no planted switch.
    - Mandatory modules in 2+ departments: 232. These repeat across cohorts (e.g. D12/L4 + D16/L4), so they look like real joint programmes.
  - **Evidence for HUNT:** P00006918 is registered on D14, D19 and D26 modules. On 17 Nov 2023, 22 copied rows (e.g. `PIT0012675765_COPY_P00006918`, 08:42 UTC) put it on D03 L7 module I2301356, a department it's never otherwise active in. P00009130 is registered on D04 (L5) and D25 (L6). All 26 of its copied rows fall on 3 Dec 2023, on one module outside those registrations.
  - **Validation limit:** the rule keys on the ID marker, not on behaviour. Check it against the released HUNT P_IDs before TEST 1.
- **Overlaps:** Can one P_ID be more than one monster type? The submission format will tell us.
