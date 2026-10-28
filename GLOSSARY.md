# Mini Monster Hack

Hackathon on Learning Analytics activity data: find the hidden monsters, build a detector, test it on unseen data, and present it.

## Monsters

**Monster**:
A P_ID that matches one of the nine monster types in the Monster Guide.
_Avoid_: outlier, unusual behaviour, "anomaly" on its own

**Monster type**:
One of the nine named kinds of Monster: Phantom, Ghost, Zombie, Vampire, Undead Student, Doppelgänger, Werewolf, Web Crawler, Shape-Shifter.

**Data anomaly**:
The category of monster types caused by faulty or impossible data: Phantom, Undead Student, Doppelgänger, Shape-Shifter.

**Behavioural monster**:
The category of monster types caused by a real student's unusual activity pattern: Ghost, Zombie, Vampire, Werewolf, Web Crawler.

**Doppelgänger pair**:
Two P_IDs with suspiciously identical activity; both are Doppelgängers and each is submitted on its own row.

## Data

**P_ID**:
The identifier of one person (student); the unit that submissions list and get scored on.

**Activity row**:
One row in either the LMS item session fact or the video view fact.
_Avoid_: event, interaction (INTERACTION_COUNT is a separate thing)

**Module instance**:
One running of a module in a given term, which students register on and which owns LMS items and videos.
_Avoid_: course, class

**Night-activity day**:
A UK calendar date with at least one Activity row after midnight and at or before 05:00. A date may be both a Night-activity day and a Day-activity day.

**Day-activity day**:
A UK calendar date with at least one Activity row after 05:00 and before the next midnight.

**Term**:
A teaching period of the academic year: Autumn, Spring, Summer or Late Summer.

**Week number**:
The week of the academic year, where week 1 is the first week of the Autumn term.

**Active week**:
A week number in which a P_ID has at least one activity row.

**Training dataset**:
The 80% of the data given out for HUNT and BUILD.
_Avoid_: train set, full data

**Test dataset**:
The unseen 10% of the data used for TEST 1.
_Avoid_: holdout, validation set

## Competition

**Stage**:
One of HUNT, BUILD, TEST 1, PREDICT, SHOWCASE.

**Monster Detector**:
Our repeatable method (rules, code, workflow or model) that outputs Monster P_IDs and Monster types.
_Avoid_: model, classifier (when meaning the whole detector)

**Checkpoint**:
A stage submission that staff check: HUNT, BUILD/TEST 1, PREDICT, or FINAL.

**Ready-for-checking post**:
A message in the main Teams checking thread announcing a Checkpoint; its post time is the official completion time.

**FINAL ready timestamp**:
The time of the team's valid FINAL Ready-for-checking post; the only timestamp that decides Escape.

**Escape**:
Being 1st or 2nd to post a valid FINAL Ready-for-checking post.

**Raffle entry**:
One chance in the prize raffle, earned from Checkpoints, bonuses and awards.
