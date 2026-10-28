# Data model

Merged from `sources/ERD.pdf` and `sources/Data Dictionary.xlsx` (created 13 Oct 2026). If either source and the **actual data files** disagree, the data files win: check column names and formats on load.

**Files** (checked 28 Oct 2026): `data/General Files/la_mmh_<table>.csv` holds the 4 shared dims (calendar, lms_item, module_instance, video). `data/{Training,Test,Predict}/la_mmh_<split>_<table>.csv` holds person_dim and the 3 facts for each split. Load them with `detector/load.py` (see `AGENTS.md`). CSVs have a header row; nulls are the literal `null`.

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
| DATE | date | | PK. 363 days, 2023-10-02 to 2024-09-28 | 2023-10-02 |
| YEAR | integer | YYYY | | 2023 |
| MONTH | integer | 1–12 | | 10 |
| DAY | integer | 1–31 | | 2 |
| WEEK_NUMBER | integer | WW | Week of the academic year; 1 = first week of Autumn term; 52 weeks. Boundary weeks span two terms (Autumn 1–14, Spring 14–30, Summer 30–39, Late Summer 39–52) | 1 |
| ACADEMIC_YEAR | string | YYYY | Year the AY begins (2023 = AY 2023-24) | 2023 |
| TERM | string | Autumn, Spring, Summer, Late Summer | | Autumn |
| TERM_CODE | integer | ACADEMIC_YEAR + 10/20/30/40 (autumn/spring/summer/late summer) | | 202310 |

### la_mmh_person_dim: one row per person

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| P_ID | string | 9-char: `P` + 8 digits | PK | P00005255 |
| registration_date | date | | | 2023-09-10 |
| deregistration_date | date | | **Null** allowed (not withdrawn; written `null`). Withdrawal date | 2024-01-19 |

### la_mmh_module_instance_dim: one row per module instance

| Column | Type | Format / categories | Notes | e.g. |
|---|---|---|---|---|
| MODULE_INSTANCE_ID | string | 8-char alphanumeric | PK | I2300979 |
| MODULE_LEVEL | string | L4, L5, L6, L7 | FHEQ level | L4 |
| ACADEMIC_YEAR_START | integer | YYYY | | 2023 |
| TERM | integer | 6-digit term code (as TERM_CODE above) | | 202320 |
| DEPARTMENT_ID | string | 3-char alphanumeric | Department owning the module | D07 |

### la_mmh_video_dim: learning videos

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| VIDEO_ID | string | 9–10 chars: `V` + 8–9 digits | PK | V000007326 |
| VIDEO_LENGTH_MINUTES | integer | whole minutes, 1–959 | | 59 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300384 |

### la_mmh_lms_item_dim: LMS learning items

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| LMS_ITEM_ID | string | 10 digits (the loader reads it as text) | PK | 2463076854 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300039 |
| TYPE_LABEL | string | categorical, see below | Resource type | Item |
| GROUP_LABEL | string | categorical, see below | Group the type belongs to | Content |

GROUP_LABEL → TYPE_LABEL:
- **Assessment:** Assessment (BB), Assessment (Mobius), FeedbackFruits, Test (BB), Turnitin assignment
- **Content:** File, Folder, Item, Learning module, Lesson plan, Page, Scorm content, Syllabus, YouTube
- **Learning activity:** Blog, Discussion board (BB), Ed discussion, Journal, Matlab, Wiki
- **Other:** Course info, External weblink, Home page, Link, Survey (BB)

## Facts

### la_mmh_person_module_instance_fact: module registrations

| Column | Type | Format / categories | Notes | e.g. |
|---|---|---|---|---|
| PMI_ID | string | 10-char: `PMI` + 7 digits | PK (one per person × module instance) | PMI0063345 |
| P_ID | string | 9-char | FK → person_dim | P00005255 |
| MODULE_INSTANCE_ID | string | 8-char | FK → module_instance_dim | I2300633 |
| MODULE_REGISTRATION_STATUS | string | Elective, Mandatory, Registered for extra credit | | Elective |

### la_mmh_video_activity_by_view_fact: one row per person per video view

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| PVT_ID | string | 13-char: `PVT` + 10 digits | PK (but see Data quirks) | PVT0000000001 |
| P_ID | string | 9-char | FK → person_dim | P00015925 |
| VIDEO_ID | string | 9–10 chars | FK → video_dim | V000018648 |
| DATE | date | ISO `YYYY-MM-DD` | FK → calendar_dim. The **UTC** date of TIMESTAMP | 2024-01-30 |
| TIMESTAMP | timestamp | ISO 8601, UTC (`Z`), always `.000` ms | When the video was **first played** in the viewing session | 2024-01-30T17:04:47.000Z |
| TOTAL_MINUTES_DELIVERED | decimal | | Playback minutes summed over the session | 21.8851 |
| VIEWING_TYPE | string | categorical, see below | How it was viewed | Interactive Desktop On Demand |

VIEWING_TYPE: Android App On Demand, Downloaded Audio Podcast, Downloaded Tablet Video, Downloaded Video Podcast, Embedded broadcast viewed through the new mobile app, Embedded Live Broadcast, Embedded video viewed through the new mobile app, Embedded Viewer, Interactive Desktop Live Broadcast, Interactive Desktop On Demand, iOS App Live Broadcast, iOS App On Demand, Streamed Audio Podcast, Streamed Video Podcast.

### la_mmh_lms_item_activity_by_session_fact: one row per person per LMS item per session

| Column | Type | Format | Notes | e.g. |
|---|---|---|---|---|
| PIT_ID | string | 13-char: `PIT` + 10 digits | PK (but see Data quirks) | PIT0038594944 |
| DATE | date | ISO `YYYY-MM-DD` | FK → calendar_dim. The **UTC** date of TIMESTAMP | 2024-04-29 |
| P_ID | string | 9-char | FK → person_dim | P00014060 |
| LMS_ITEM_ID | string | 10 digits | FK → lms_item_dim | 2619786778 |
| TIMESTAMP | timestamp | ISO 8601, UTC (`Z`), 0–3 ms digits | When the item was **first accessed** in the session | 2024-04-29T11:34:17.183Z |
| LOGIN_ID | string | `L` + 8 digits | In the files (ERD only, not the dictionary). Close to one per LMS session: 1.54M distinct in training | L00537558 |
| INTERACTION_COUNT | integer | | Interactions with the item in the session | 2 |
| TOTAL_SECONDS_BEFORE_NEXT_INTERACTION | integer | whole seconds | Seconds from each interaction to the next recorded one (any item), summed over the session | 49 |

## Known discrepancies (data files win)

The tables above already follow the files. What the sources got wrong: ID lengths (P_ID is 9 chars, PMI_ID 10, PIT_ID and PVT_ID 13), MODULE_LEVEL has an `L` prefix, fact DATEs are ISO dates not Excel serials, VIDEO_LENGTH_MINUTES and TOTAL_SECONDS_BEFORE_NEXT_INTERACTION are integers, and three dictionary TYPE_LABELs (Self/peer assessment, Assessment (Turnitin), Textbook) never occur. Remaining source notes:

- `deregistration_date` is spelled `deregristration_date` in the dictionary.
- Calendar `TERM` / `TERM_CODE` are in the dictionary but not the ERD. `LOGIN_ID` is in the ERD but not the dictionary.
- `TERM` means a name (string) in the calendar but a 6-digit code (integer) in module_instance_dim.
- Formats contradict their examples: `LMS_ITEM_ID` (8-char vs 10 digits), `PVT_ID` (9-char vs 13), video-fact `P_ID` example `P00015925` (9 chars vs 10).
- Fact `DATE` examples are Excel serial numbers (45321 = 2024-01-30), not ISO dates.
- The dictionary's FK descriptions say `la_dataset_*`; the real tables are `la_mmh_*`.
- The lms TIMESTAMP row has no PK or null flag in the dictionary.
- All timestamps are UTC. UK local time was BST (UTC+1) until 29 Oct 2023 and from 31 Mar 2024. Fact `DATE` is the UTC date, so for "night" or "day" logic use the loader's `ts_local` (Europe/London), not `DATE`.

## Data quirks (training / test / predict)

Found while profiling. Several look planted (monster evidence), so the loader keeps them and each detector decides what to do with them.

| Quirk | Training | Test | Predict |
|---|---|---|---|
| person_dim rows | 14,951 | 1,874 | 1,874 |
| person_module_instance_fact rows | 100,611 | 12,345 | 12,814 |
| video_activity_by_view_fact rows | 1,145,358 | 144,735 | 152,482 |
| lms_item_activity_by_session_fact rows | 7,857,424 | 960,024 | 1,011,759 |
| Rows with 28-char `<id>_COPY_<P_ID>` IDs (e.g. `PIT0000000548_COPY_P00009130`), LMS / video | 615 / 224 | 99 / 20 | 83 / 19 |
| LMS PIT_IDs appearing more than once (all exact duplicate rows) | 63,317 | 0 | 0 |
| Video PVT_IDs appearing more than once | 7,399 | 510 | 877 |
| Activity rows dated outside the calendar (training LMS spans 2023-05-06 to 2025-08-27) | 10,749 | 1,199 | 691 |
| Activity P_IDs missing from person_dim (e.g. `P00922502`), rows / people | 2,773 / 30 | 318 / 5 | 200 / 5 |
| LMS rows whose LMS_ITEM_ID is not in lms_item_dim | 32,836 | 0 | 0 |

Also in training: 3 people deregistered before they registered, 1,767 people have no activity, 79 have no module registration, and one LOGIN_ID is used by two P_IDs. Most repeated PVT_IDs are exact duplicate rows, but 430 reuse an ID for a different row.
