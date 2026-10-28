# Strategy (our plan to win)

Our decisions, not the organisers' rules (those are in `student-guide.md`).

## Goal

Win the raffle, which means collecting the most raffle entries. The big three are **1st to Escape (+10)**, **Best Monster Detector (+10)** and **Best Showcase (+10)**. Every checkpoint +1 adds to that.

## Priorities

1. **Accuracy up to and including TEST 1.** Best Monster Detector goes to the highest TEST 1 accuracy, and the "most correct" / "all true monsters" bonuses come at HUNT and TEST 1.
2. **After TEST 1, speed matters more than anything else.** Sprint to a valid FINAL post for 1st to Escape.
3. **PREDICT:** ask the organisers at the start whether FINAL is valid without it. If another team is close to escaping, skip PREDICT (+3 at most) to protect the +10.
4. **Get every submission right the first time.** A resubmission resets our timestamp. Before posting, check the deliverables against the checklist below.
5. **Showcase:** reuse what we've already built (detector output, a visual) rather than making new material.

## Raffle-entry checklist

- [ ] HUNT Excel (full P_ID list; Doppelgängers as both P_IDs, one per row) + HUNT slide(s)
- [ ] Detector shown running + detector code
- [ ] TEST 1 Excel (P_IDs + monster types) + TEST slide(s)
- [ ] PREDICT Excel + slide(s) + code (if we do PREDICT)
- [ ] Every team member dressed spooky/Halloween (+1 each)
- [ ] FINAL Ready-for-checking post

## Working rules

- Speed over polish. Write the smallest thing that gets a correct answer.
- No CI/CD, no pre-commit hooks and no pytest suite (see the override in `docs/agents/coding-standards.md`).
- The one check we keep is a **scoring script**: once the HUNT P_IDs are released, run the detector on the training data and compare its output against them (precision/recall per monster type). That gives us our accuracy before TEST 1.
