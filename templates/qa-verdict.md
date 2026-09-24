# QA Verdict Record

Fill-in template. One record per claim under test.
Written for a reader who was not present and has no context: expand every acronym on first use, name
every file and path in full, and never rely on shared background.

Delete the italic guidance lines when filling this in. Do not delete a heading - an empty section is
itself information, and a missing section hides it.

---

## Claim under test

*One falsifiable sentence. "X does Y under condition Z." A topic is not a claim.*

> 

**Disconfirming condition** - *what result would have proven this false. If this is blank, the review
could not have returned FAIL and the verdict below is not evidence.*

> 

---

## Context

- **Artifact / location:** *full path or identifier*
- **Review commissioned by:** *who, and the decision or risk trigger that enabled it*
- **IPOF stage:** *Input / Processing / Output / Feedback (IPOF = Input, Processing, Output, Feedback)*
- **Reviewer independence:** *independent context, or self-QA - state which; self-QA is weaker
  evidence and is labelled, not disguised*

---

## Method

*What you actually did, in the order you did it. Enough that a stranger could repeat it.*

| # | Probe | Target (real path?) | Input state used | Expected if claim FALSE |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |

**Pre-registered before running:** *yes / no. If no, say why - a probe chosen after seeing the result
is weaker evidence.*

---

## Evidence

*Receipts, not assertions. Quote the actual output. Name the number of rows, files, or cases
exercised.*

| # | Signal cited | Exercised non-empty? (count) | Confirmed capable of failing? | Result |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |

**Verify-the-verifier statement:** *for each signal cited - how you confirmed it actually ran, ran
against the target, exercised a non-empty set, and could have returned red. A green signal that
examined zero rows is not verification and must not appear as PASS evidence.*

> 

---

## Verdict

**`PASS` / `FAIL` / `CONDITIONAL PASS` / `NOT VERIFIED`** - *pick exactly one.*

> 

*If CONDITIONAL PASS: the condition, stated so it travels with the verdict.*
*If FAIL: the minimal reproduction, below.*

**Minimal reproduction (FAIL only):**

> 

**Multi-axis note:** *where the work has more than one axis of correctness (the mechanism works, and
it still serves its original purpose), give a separate verdict per axis. A PASS on one axis may not
conceal a FAIL or NOT VERIFIED on another.*

| Axis | Verdict | Basis |
|---|---|---|
| Local mechanics |  |  |
| Purpose fidelity |  |  |

---

## Limits - what is NOT verified

*Mandatory. Everything outside the executed proof. A verdict with unstated limits is unusable.*

- **Exercised:** 
- **Not exercised:** 
- **Assumed rather than confirmed:** 
- **Could not access or could not run:** 
- **This verdict does NOT generalize to:** 

---

## Corrections and gate attribution

*Feedback-stage capture. For each defect found: which earlier gate should have caught it, and what
changes so the next cycle catches it there. A defect that reached Output but originated at Input means
the Input gate was too weak - the fix belongs at the earlier gate, not in a bigger final inspection.*

| Defect | Originating stage | Should have been caught at | Change to that gate |
|---|---|---|---|
|  |  |  |  |

---

## Ratification

- **Decision:** `RATIFIED` / `RATIFIED WITH CORRECTIONS` / `REJECTED` / `AWAITING RATIFICATION`
- **Owner:** 
- **Corrections required:** 

*Silence is not acceptance. `AWAITING RATIFICATION` is never silently upgraded.*
