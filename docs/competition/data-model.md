# Data model

Merged from `sources/ERD.pdf` and `sources/Data Dictionary.xlsx` (created 13 Oct 2026). If either source and the **actual data files** disagree, the data files win: check column names and formats on load.

Star schema: 5 dimension tables and 3 fact tables. PK = primary key. "Null" = nullable (all columns are NOT NULL unless marked).

## Relationships (all one-to-many)

```
la_mmh_calendar_dim.DATE ─┬─< la_mmh_video_activity_by_view_fact.DATE
                          └─< la_mmh_lms_item_activity_by_session_fact.DATE
la_mmh_person_dim.P_ID ───┬─< la_mmh_person_module_instance_fact.P_ID
                          ├─< la_mmh_video_activity_by_view_fact.P_ID
                          └─< la_mmh_lms_item_activity_by_session_fact.P_ID
la_mmh_module_instance_dim.MODULE_INSTANCE_ID ─┬─< la_mmh_person_module_instance_fact
                                               ├─< la_mmh_video_dim
                                               └─< la_mmh_lms_item_dim
la_mmh_video_dim.VIDEO_ID ──< la_mmh_video_activity_by_view_fact.VIDEO_ID
la_mmh_lms_item_dim.LMS_ITEM_ID ──< la_mmh_lms_item_activity_by_session_fact.LMS_ITEM_ID
```

The activity facts link to modules only through their item/video dims. There is no programme table.

## Dimensions

### la_mmh_calendar_dim: dates in the relevant academic year

| Column | Type | Format / categories | Notes | e.g. |
|---|---|---|---|---|
| DATE | date | | PK | 2023-10-02 |
| YEAR | integer | YYYY | | 2023 |
| MONTH | integer | 1–12 | | 10 |
| DAY | integer | 1–31 | | 2 |
| WEEK_NUMBER | integer | WW | Week of the academic year; 1 = first week of Autumn term; 52 weeks | 1 |
| ACADEMIC_YEAR | string | YYYY | Year the AY begins (2023 = AY 2023-24) | 2023 |
| TERM | string | Autumn, Spring, Summer, Late Summer | *Dictionary only* | Autumn |
| TERM_CODE | string | ACADEMIC_YEAR + 10/20/30/40 (autumn/spring/summer/late summer) | *Dictionary only* | 202310 |

### la_mmh_person_dim: one row per person

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| P_ID | string | 10-char alphanumeric | PK | P000005255 |
| registration_date | date | | | 2023-09-10 |
| deregistration_date | date | | **Null** allowed (not withdrawn). Withdrawal date | 2024-01-19 |

### la_mmh_module_instance_dim: one row per module instance

| Column | Type | Format / categories | Notes | e.g. |
|---|---|---|---|---|
| MODULE_INSTANCE_ID | string | 8-char alphanumeric | PK | I2300979 |
| MODULE_LEVEL | string | 4, 5, 6, 7 | FHEQ level | 4 |
| ACADEMIC_YEAR_START | integer | YYYY | | 2023 |
| TERM | integer | 6-digit term code (as TERM_CODE above) | | 202320 |
| DEPARTMENT_ID | string | 3-char alphanumeric | Department owning the module | D07 |

### la_mmh_video_dim: learning videos

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| VIDEO_ID | string | 10-char alphanumeric | PK | V000007326 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300384 |
| VIDEO_LENGTH_MINUTES | decimal | | | 59.4 |

### la_mmh_lms_item_dim: LMS learning items

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| LMS_ITEM_ID | string | "8-char" (example is 10 digits) | PK | 2463076854 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300039 |
| TYPE_LABEL | string | categorical, see below | Resource type | Item |
| GROUP_LABEL | string | categorical, see below | Group the type belongs to | Content |

GROUP_LABEL → TYPE_LABEL:
- **Assessment:** Self/peer assessment, Assessment (BB), Assessment (Mobius), Assessment (Turnitin), FeedbackFruits, Test (BB), Turnitin assignment
- **Content:** File, Folder, Item, Learning module, Lesson plan, Page, Scorm content, Syllabus, Textbook, YouTube
- **Learning activity:** Blog, Discussion board (BB), Ed discussion, Journal, Matlab, Wiki
- **Other:** Course info, External weblink, Home page, Link, Survey (BB)

## Facts

### la_mmh_person_module_instance_fact: module registrations

| Column | Type | Format / categories | Notes | e.g. |
|---|---|---|---|---|
| PMI_ID | string | 12-char | PK (one per person × module instance) | PMI230063345 |
| P_ID | string | 10-char | FK → person_dim | P000005255 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300633 |
| MODULE_REGISTRATION_STATUS | string | Elective, Mandatory, Registered for extra credit | | Elective |

### la_mmh_video_activity_by_view_fact: one row per person per video view

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| PVT_ID | string | "9-char" (example is 13) | PK | PVT0000000001 |
| DATE | date | | FK → calendar_dim | 45321 (Excel serial) |
| P_ID | string | 10-char | FK → person_dim | P00015925 |
| TIMESTAMP | timestamp | ISO 8601, UTC (`Z`) | When the video was **first played** in the viewing session | 2024-01-30T17:04:47.000Z |
| VIDEO_ID | string | 10-char | FK → video_dim | V000018648 |
| TOTAL_MINUTES_DELIVERED | decimal | | Playback minutes summed over the session | 21.8851 |
| VIEWING_TYPE | string | categorical, see below | How it was viewed | Interactive Desktop On Demand |

VIEWING_TYPE: Android App On Demand, Downloaded Audio Podcast, Downloaded Tablet Video, Downloaded Video Podcast, Embedded broadcast viewed through the new mobile app, Embedded Live Broadcast, Embedded video viewed through the new mobile app, Embedded Viewer, Interactive Desktop Live Broadcast, Interactive Desktop On Demand, iOS App Live Broadcast, iOS App On Demand, Streamed Audio Podcast, Streamed Video Podcast.

### la_mmh_lms_item_activity_by_session_fact: one row per person per LMS item per session

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| PIT_ID | string | 12-char | PK | PIT038594944 |
| DATE | date | | FK → calendar_dim | 45411 (Excel serial) |
| P_ID | string | 10-char | FK → person_dim | P000014060 |
| LMS_ITEM_ID | string | | FK → lms_item_dim | 2619786778 |
| TIMESTAMP | timestamp | ISO 8601, UTC (`Z`) | When the item was **first accessed** in the session | 2024-04-29T11:34:17.000Z |
| LOGIN_ID | string | | *ERD only*; not in the dictionary | |
| INTERACTION_COUNT | integer | | Interactions with the item in the session | 2 |
| TOTAL_SECONDS_BEFORE_NEXT_INTERACTION | decimal | | Seconds from each interaction to the next recorded one (any item), summed over the session | 49.6167 |

## Known discrepancies (data files win)

- `deregistration_date` is spelled `deregristration_date` in the dictionary.
- Calendar `TERM` / `TERM_CODE` are in the dictionary but not the ERD. `LOGIN_ID` is in the ERD but not the dictionary.
- `TERM` means a name (string) in the calendar but a 6-digit code (integer) in module_instance_dim.
- Formats contradict their examples: `LMS_ITEM_ID` (8-char vs 10 digits), `PVT_ID` (9-char vs 13), video-fact `P_ID` example `P00015925` (9 chars vs 10).
- Fact `DATE` examples are Excel serial numbers (45321 = 2024-01-30), not ISO dates.
- The dictionary's FK descriptions say `la_dataset_*`; the real tables are `la_mmh_*`.
- The lms TIMESTAMP row has no PK or null flag in the dictionary.
- All timestamps are UTC. UK local time was BST (UTC+1) until 29 Oct 2023 and from 31 Mar 2024.
