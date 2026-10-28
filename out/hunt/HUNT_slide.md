# HUNT slide content (slide 2 of the team template)

Paste into `TEAMK_NightmareOnGitStreet_Slides.pptx`. Insert the chart as a native PowerPoint bar chart from the counts table so it stays editable. Full P_ID lists go in Excel only.

## Our approach

One small SQL rule per monster, written from the Monster Guide clue and run on the training data (LMS + video activity merged into one timeline, UK local time). For every rule we tested the variants (thresholds, UTC vs UK time, endpoints) and kept the strictest reading the clue supports, because false positives cost points. A P_ID caught by two rules is submitted under both: the organisers allow overlaps.

## What gave each monster away

| Monster | Rule | Example |
|---|---|---|
| Phantom | Two activity rows identical in every field except the row ID | P00000693: the same LMS item, second and login recorded twice |
| Ghost | Active in at least 3 of weeks 1–4, then weekly activity below 10% of that early rate | P00007556: 50 LMS rows in weeks 1–3, then none for weeks 4–52 |
| Zombie | Continuous activity (no gap over 15 min) lasting more than 3 hours | P00020056: 78 accesses from 23:44 to 04:52, largest gap 14 min |
| Vampire | More than 21 night-active dates, and more night dates than day dates | P00013423: 273 night dates against 236 day dates |
| Undead Student | Any activity after the deregistration date | P00019372: 134 rows after deregistering on 15 Nov 2023 |
| Doppelgänger | All of one P_ID's activity reappears, identical, under another P_ID | P00002959 and P00336066: the same 174 video views; the copy isn't in person_dim |
| Werewolf | At least 2 separate bursts in each term, each at least 5x the student's usual day and 40+ rows | P00017160: usually 5 rows a day; 90, 145 and 46 in Autumn, 150 and 167 in Spring |
| Web Crawler | More than 200 distinct LMS items and videos in a rolling 12-hour window | P00010833: 529 distinct pages in under 2 minutes |
| Shape-shifter | Copied activity rows (`_COPY_<P_ID>`) on modules the student isn't registered on | P00006918: 22 copied rows on a D03 module, outside its own departments |

## What we found (chart data)

| Monster | P_IDs |
|---|---|
| Ghost | 148 |
| Undead Student | 92 |
| Vampire | 91 |
| Shape-shifter | 79 |
| Phantom | 77 |
| Doppelgänger | 60 (30 pairs) |
| Werewolf | 32 |
| Zombie | 25 |
| Web Crawler | 16 |

Total: 620 findings across 586 distinct students.

Overlaps, one line on the slide: 23 of the 25 Zombies are also Vampires (their long sessions run through the night); 4 Ghosts are also Undead Students.
