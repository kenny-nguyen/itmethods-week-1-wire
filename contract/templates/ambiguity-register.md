# Ambiguity Register

Template for `AMBIGUITY-REGISTER.md` at the repository root.

Every ambiguity found in the assignment, and what was decided about it. This is one of the two artifacts the reviewer weighs above the code itself.

**Governed by `AGENTS.md` section 4 (the ambiguity rule) and section 5 (append-only).** Where this template and the contract disagree, the contract wins.

## How to use this file

- **Append-only.** Never edit or delete a row once written.
- **To reverse a decision:** set the original row's Status to `Reversed`, then **append** a new row that names the original by ID. Do not rewrite the original. Add the matching `R-nnn` `REVERSAL` entry to `PROCESS-LOG.md`.
- **Every row is mirrored in the process log** as an `A-nnn` entry at the moment it is decided, with `ROLE: PM` and `TYPE: AMBIGUITY`. The IDs are the same on both sides so the two files can be read against each other.
- **Never silently guess.** An ambiguity that was resolved in your head and never written here is indistinguishable from an oversight.
- **Never block.** Decide, state the assumption, proceed (section 4, step 4).
- **Legible to a stranger.** The reviewer was not present and will not ask a follow-up question. No internal shorthand; expand every acronym on first use.

**Source of the initial rows:** every UNSPECIFIED item from the intake worksheet, plus every weight-bearing or low-confidence IMPLIED item. New ambiguities surface throughout the work - that is expected, and a register holding only opening-phase rows looks like a form filled in once.

---

## Register

| ID | Question | Options considered | Assumption taken | Rationale | Reversal trigger | Reversal cost | Status |
|----|----------|--------------------|------------------|-----------|------------------|---------------|--------|
| A-001 | *The ambiguity as a neutral question - the requirement as written, and the readings it admits* | *(a) … (b) … - at least two real candidates* | *The reading chosen, stated as a falsifiable claim* | *Why this one, in terms of the assignment's apparent goal - evidence from the text, the repository, or ordinary practice. "Most likely, because X" is a reason; "I assumed" is not* | *The one piece of information that, if it turned up, would flip this decision* | Low / Med / High - *plus one concrete line on what is lost if wrong* | Assumed |
| A-002 | | | | | | | Open |

### Field rules

| Field | Requirement |
|---|---|
| **Question** | Neutral, not a complaint. Shows the ambiguity was *detected*. |
| **Options considered** | At least two genuine candidates. A single "option" is a decision written backwards. |
| **Assumption taken** | One reading, stated so it could be shown wrong. |
| **Rationale** | Why this reading, grounded in evidence - not in preference. This is the actual evidence of judgment, and it is what the reviewer reads most closely. |
| **Reversal trigger** | Required by `AGENTS.md` section 4. This is what shows the risk was understood rather than survived by luck. |
| **Reversal cost** | Drives the decision order. Low-cost items are decided immediately without deliberation; high-cost items get the real thinking. |
| **Status** | `Open` · `Assumed` · `Confirmed` · `Reversed` |

**Status values:**
- `Open` - not yet decided. Must state what it blocks. An `Open` row at submission needs a reason.
- `Assumed` - decided, work is proceeding on it.
- `Confirmed` - validated by something that actually ran, or by an answer received.
- `Reversed` - superseded. Names the successor row.

### The decision rule

**Order by reversal cost, not by how interesting the question is.** Deliberating cheap decisions is the standard way to lose a fixed window.

**Where two readings are equally supported, choose the reversible one** (`AGENTS.md` section 4) - and record that its reversibility is *why* it was chosen.

**Never resolve an ambiguity by building both readings.** Pick one, say why, note the other as deferred.

---

## Reversals

Appended, never edited in place. A documented reversal is stronger evidence of judgment than a run with none.

| Original ID | Superseded by | What triggered the reversal | Log entry | Cost actually incurred |
|-------------|---------------|-----------------------------|-----------|------------------------|
| A-___ | A-___ | *The fact that broke the assumption - ideally the reversal trigger firing as predicted* | R-___ | *Work discarded / rework required* |

---

## Clarifications requested

Only if the assignment permits asking. Never block on an answer - proceed on the assumption and record both.

| # | Question asked | Assumption proceeded on | Answer received | Effect |
|---|----------------|-------------------------|-----------------|--------|
| Q-001 | | | *(or: no answer before submission)* | |

---

## Deferred readings

Alternatives that were considered, rejected for this window, and deliberately not built. Naming them is evidence of scope judgment; these carry into the README.

| From ID | The reading not taken | Why deferred rather than dropped |
|---------|----------------------|----------------------------------|
| A-___ | | |

---

## Highest-reversal-cost decisions

The two or three that most shaped the solution. These are written out in prose in the submission README, each with its reversal trigger.

1. **A-___ - ** *one line on the decision and what it foreclosed*
2. **A-___ - **
3. **A-___ - **

---

## Submission check

- [ ] Every UNSPECIFIED item from the intake worksheet has a row
- [ ] Every weight-bearing IMPLIED item has a row
- [ ] No row is left at `Open` without a stated reason
- [ ] Every row has a rationale a stranger can follow without context
- [ ] Every `Assumed` row has a reversal trigger
- [ ] Every reversal is appended, with its original row marked `Reversed` and a matching `R-nnn` log entry
- [ ] Every assumption the code depends on is also visible at that point in the code or its documentation (`AGENTS.md` section 4, step 5) - not buried here
- [ ] No duration, estimate, or forecast anywhere in this file
