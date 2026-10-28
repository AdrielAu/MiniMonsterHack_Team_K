# Student Guide (official rules)

Converted from `sources/Mini Monster Hack Student Guide.pdf`. Facts only; our plan is in `strategy.md`. If this file and the PDF disagree, the PDF wins.

**Event:** Mini Monster Hack, Data CoLab. Wednesday 28 October 2026, Queens Tower Rooms, South Kensington.
**Flow:** HUNT → BUILD + TEST 1 → PREDICT → SHOWCASE.
**Companion doc:** the separate Monster Guide says *what* to find (`monster-guide.md`, once added). We decide *how*. Organisers may release hints.

## The challenge (p3)

Learning Analytics data contains thousands of normal activity records with monsters (unusual behaviours, anomalies) hidden among them. Work out what gives them away, turn that into a repeatable detector, and test it on unseen data.

| Stage | Task |
|---|---|
| 1 HUNT | Explore the **80% training dataset** manually. Identify as many monsters as possible and explain what gave each away. |
| 2 BUILD | Turn the findings into a repeatable **Monster Detector**: rules, code, workflow or model. |
| 3 TEST 1 | Run the detector on the **unseen 10% test data**. Record the P_IDs and monster types it finds. |
| 4 PREDICT | *Optional ("if you reach this stage").* Using data available only **up to 14 Nov 2023**, spot early warning signs of future behavioural monsters. |
| 5 SHOWCASE | Show the team's clearest, strongest piece of work: a result, visual, model output or interface. |

## Submission process (p4)

1. **Save:** work from team copies in the **private team channel**. Never overwrite the master templates.
2. **Complete the stage:** save the relevant Excel workbook, slides and code/output. **Full P_ID lists go in Excel.**
3. **Post** in the **main Teams checking thread**, e.g. `Team G - HUNT ready for checking`.
4. **Checked in timestamp order.** The Teams post time is the official completion time, so staff being busy doesn't lose us our place.

If something is missing: fix it, then post "Ready for checking" again. **The new post's timestamp becomes the valid one.** An incomplete submission therefore costs time.

## Checkpoint deliverables (p4)

| Checkpoint | Submit / show | Next |
|---|---|---|
| HUNT | HUNT Excel + HUNT slide(s) | Correct HUNT P_IDs released **privately** after checking |
| BUILD / TEST 1 | Working detector (shown running) + code + TEST 1 Excel + TEST slide(s) | Continue once checked |
| PREDICT (if done) | PREDICT Excel + slide(s) + code | Prepare final showcase, then post FINAL ready |

**FINAL ready timestamp:** only this decides 1st and 2nd to Escape. HUNT, TEST 1 and PREDICT timestamps are kept as an audit trail only.

## Awards (p5)

Awards carry **no prize of their own**. They add raffle entries and appear on the certificate. Every participant gets a certificate.

| Award | Raffle entries | Criterion |
|---|---|---|
| 1st to Escape | +10 | Earliest **valid** FINAL Ready-for-checking timestamp |
| 2nd to Escape | +5 | Second valid FINAL timestamp |
| Best Monster Detector | +10 | Highest **official TEST 1 accuracy score** |
| Best Showcase | +10 | Judges' choice |

**Best Showcase judging criteria:** a strong idea or insight; clear evidence and explanation; quality of technical work; creativity and usefulness.

## Raffle entries (p5)

**Only prize:** 4 × £50 vouchers to **one** raffle-winning team.

Checkpoint entries (+1 each):
- HUNT slide(s), HUNT Excel
- Detector shown running, working detector code, TEST 1 slide(s), TEST 1 Excel
- PREDICT slide(s), PREDICT Excel, PREDICT code

Bonuses:
- +1 Most correct monsters (HUNT), +1 All true monsters found (HUNT)
- +1 Most correct monsters (TEST 1), +1 All true monsters found (TEST 1)
- **+1 per spooky / Halloween-dressed team member**
- Award entries as in the table above

## FINAL readiness clarification

The FINAL checklist supplied by the team on 28 October 2026 clarifies that SHOWCASE slides must be complete and the detector/output ready to demonstrate before posting FINAL. PREDICT is optional: save any completed PREDICT work the team wants included. See the full [Before posting FINAL checklist](submission.md#before-posting-final). This clarification supplements the PDF conversion above.

## Open questions (not stated in the guide)

- **The remaining 10% of data.** Training is 80% and TEST 1 is 10%. The name "TEST 1" hints at a hidden holdout (a TEST 2?), but the guide doesn't say.
- **How "TEST 1 accuracy" is scored** (exact P_ID match? does monster type have to be correct? are false positives penalised?). Ask the organisers on the day.
- **Which data PREDICT runs on.** The slide template says "Find early signs in 10%", and the PREDICT workbook says data only up to 14 Nov 2023 and only the 5 behavioural monsters. Is it the TEST 1 10%, or the remaining 10%?
