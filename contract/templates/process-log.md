# Process Log - Template and Worked Example

Template for `PROCESS-LOG.md` at the repository root. **This is the primary graded artifact** (`AGENTS.md` section 5).

The format below is copied from the contract and is authoritative. Where this template and `AGENTS.md` section 5 disagree, the contract wins.

## Rules (from `AGENTS.md` section 5)

- **Append-only.** Never edit or delete an existing entry. If something turns out to be wrong, **append** a `REVERSAL` entry referencing the original by ID. The record of having changed your mind is evidence, not embarrassment.
- **Written as you go**, at the moment of the decision. A log reconstructed at the end is a summary, and reads like one.
- **Every agent writes to this same file in this same format.** No per-agent logs.
- **Legible to a stranger.** The reader was not present, does not know this codebase, and will not ask a follow-up question. No internal shorthand. Expand every acronym on first use.
- **One entry per decision.** Do not batch three decisions into one entry.
- Commit the log alongside the work it records. That correspondence is itself evidence the log was written as the work happened (`AGENTS.md` section 6).

## Entry format (exact - all agents use this)

```
### [<ID>] <HH:MM> · <ROLE> · <TYPE>
**What:** <one line: the decision, finding, or checkpoint>
**Why:** <the reasoning, including what was considered and rejected>
**Evidence:** <what was actually observed, run, or read - file paths, commands, outputs>
**Assumption:** <the assumption this rests on, or "none">
**Reversal trigger:** <what would make this wrong, or "n/a">
**Links:** <IDs of related entries, or "-">
```

**`<ID>`** - monotonically increasing, prefixed by type. Never reuse an ID.

| Prefix | Meaning |
|---|---|
| `D-001` | decision |
| `A-001` | ambiguity |
| `Q-001` | QA verdict |
| `G-001` | GRAA checkpoint |
| `R-001` | reversal |
| `S-001` | scope cut |

**`<HH:MM>`** - the wall-clock time the entry was written, 24-hour. This is a **record of when something happened**, so the reviewer can follow the sequence. It is never a forecast or an estimate of how long anything will take.

**`<ROLE>`** - one of: `PM` · `QA` · `BUILDER` · `RESEARCH` · `SECURITY` · `WRITER` · `COPY`

**`<TYPE>`** - one of: `DECISION` · `AMBIGUITY` · `ASSUMPTION` · `INPUT-QA` · `PROCESSING-QA` · `OUTPUT-QA` · `QA-VERDICT` · `GRAA` · `SCOPE-CUT` · `REVERSAL`

**A `GRAA` entry** replaces the `What`/`Why` body with the four stages written out, then `Evidence` and `Links` as normal:

```
### [G-001] <HH:MM> · <ROLE> · GRAA
**Goal:** <what the assignment is actually asking for, in our own words>
**Reality:** <what is observably true right now - never assumed>
**Analysis:** <the gap, and what it means for scope and sequencing>
**Action:** <what to do next, and what to drop>
**Evidence:** <what was observed, run, or read>
**Links:** <related IDs, or "-">
```

## What must be logged (non-negotiable)

- Every GRAA checkpoint.
- Every ambiguity found, and the assumption chosen to resolve it.
- Every QA verdict, **including every PASS**.
- Every scope cut and every scope addition, with the reason.
- Every reversal of an earlier decision.
- Every Researcher and Security finding, **including an explicit null result** ("no external source to verify", "no meaningful attack surface") with its reasoning.
- Any activation of an off-roster role, with the reason it became necessary.
- Every accuracy-drift correction caught at step 3 of the writer handoff.
- Every fallback to a substrate-independent mechanism under `AGENTS.md` section 8, with what failed.

Routine mechanical steps do not need entries. If the log becomes a keystroke diary, the decisions get lost in it.

---

# PROCESS-LOG.md

*(Everything below this line is the starting skeleton. Delete the worked examples once real entries replace them - they are here to show the shape, including the shapes people get wrong.)*

## Log

### [G-001] 09:14 · PM · GRAA
**Goal:** *(The assignment in our own words, including what we have decided it does NOT ask for.)*
**Reality:** *(What is observably true right now: the assignment text, what was supplied, what is unknown. Observed, never assumed.)*
**Analysis:** *(The gap between Goal and Reality, and what it means for scope and sequencing.)*
**Action:** *(The opening scope decision and what is being dropped.)*
**Evidence:** Intake worksheet completed; assignment text read in full from <source>.
**Links:** -

### [A-001] 09:21 · PM · AMBIGUITY
**What:** *(The requirement as written, and the readings it admits.)*
**Why:** *(Which reading was chosen and what evidence supports it - from the assignment, the repository, or ordinary practice.)*
**Evidence:** *(The exact line of the assignment, quoted, with its location.)*
**Assumption:** *(The reading being proceeded on, stated as a falsifiable claim.)*
**Reversal trigger:** *(The one piece of information that would flip this.)*
**Links:** G-001

### [D-001] 09:30 · PM · DECISION
**What:** Must / Should / Could / Won't tiering set for this window.
**Why:** *(The reasoning, including what was considered and rejected.)*
**Evidence:** Intake worksheet, section 5.
**Assumption:** *(or "none")*
**Reversal trigger:** *(or "n/a")*
**Links:** G-001

### [D-002] 09:42 · BUILDER · INPUT-QA
**What:** *(What preconditions were verified before starting this unit of work.)*
**Why:** Input QA is the cheapest catch-point; acting on remembered or inferred state is the failure this gate prevents.
**Evidence:** *(The actual file read, the actual command run, and its real output - not a summary of it.)*
**Assumption:** *(or "none")*
**Reversal trigger:** *(or "n/a")*
**Links:** -

### [Q-001] 10:05 · QA · QA-VERDICT
**What:** PASS / FAIL / CONDITIONAL on *(the specific claim being tested - not "the work")*.
**Why:** *(What was attempted in order to refute the claim, and why it did or did not break.)*
**Evidence:** *(Command run, real output, file paths. A green result from a check that exercised nothing is not evidence - confirm the check ran against the real path with real input.)*
**Assumption:** *(or "none")*
**Reversal trigger:** *(or "n/a")*
**Links:** D-___
**Proof boundary:** *(What was NOT covered. Never imply coverage that was not run.)*

### [R-001] 10:31 · BUILDER · REVERSAL
**What:** Reverses A-001. *(The new position.)*
**Why:** *(What turned up that broke the earlier assumption - ideally, the reversal trigger firing exactly as predicted.)*
**Evidence:** *(What was observed that forced the change.)*
**Assumption:** *(The new assumption now being carried.)*
**Reversal trigger:** *(What would flip the new position.)*
**Links:** A-001

### [S-001] 10:48 · PM · SCOPE-CUT
**What:** Cut *(what)*, tier *(Should / Could)*.
**Why:** *(What the cut protects - usually a Must at risk. Cuts are whole units, never partial.)*
**Evidence:** *(The GRAA checkpoint that triggered it.)*
**Assumption:** *(or "none")*
**Reversal trigger:** n/a
**Links:** G-___

### [D-003] 11:02 · RESEARCH · DECISION
**What:** No external specification, API, protocol, format, or dataset is involved in this assignment.
**Why:** *(The reasoning - what was looked for and where, to establish the null result honestly.)*
**Evidence:** *(What was read to reach that conclusion.)*
**Assumption:** none
**Reversal trigger:** Any requirement turning out to depend on an outside source.
**Links:** G-001

### [D-004] 11:06 · SECURITY · DECISION
**What:** No meaningful attack surface: *(no untrusted input / no credentials / no data at rest / no network boundary - whichever applies)*.
**Why:** *(The reasoning behind the null result.)*
**Evidence:** *(What was inspected.)*
**Assumption:** none
**Reversal trigger:** Introduction of untrusted input, a credential, or a persistence layer.
**Links:** G-001

### [D-005] 11:24 · PM · DECISION
**What:** Activated *(off-roster role)*, which `AGENTS.md` section 3 lists as off for this assignment.
**Why:** *(What turned up that made it necessary - for example, a real user-interface surface appearing.)*
**Evidence:** *(What was observed.)*
**Assumption:** *(or "none")*
**Reversal trigger:** n/a
**Links:** G-___

### [D-006] 11:40 · WRITER · PROCESSING-QA
**What:** Accuracy drift caught at step 3 of the writer handoff and restored: *(what changed)*.
**Why:** The copyedit altered a *(fact / caveat / limitation / number)*. A copyedit that changed a meaning is a defect.
**Evidence:** *(Before and after.)*
**Assumption:** none
**Reversal trigger:** n/a
**Links:** -

### [D-007] 11:55 · BUILDER · DECISION
**What:** Fell back from *(mechanism)* to *(fallback from `AGENTS.md` section 8)*.
**Why:** *(What failed or behaved unexpectedly. One attempt to understand a misbehaving mechanism is reasonable; a second is a trap. Window time spent fighting the substrate produces no evidence of anything.)*
**Evidence:** *(What was attempted and what it did.)*
**Assumption:** The fallback preserves the requirement, only changing how it is done.
**Reversal trigger:** n/a
**Links:** -

### [G-002] 12:10 · PM · GRAA
**Goal:**
**Reality:** *(Verified facts only. "Almost done" is not a Reality.)*
**Analysis:**
**Action:** *(A checkpoint that produces no decision was not a checkpoint. "Continue - no divergence" is a valid logged outcome.)*
**Evidence:** Walking skeleton green and committed at <commit>.
**Links:** G-001

---

## Submission check

- [ ] Every entry uses the exact section 5 format, with `Assumption` and `Reversal trigger` present on every one
- [ ] Every ID is unique, correctly prefixed, and never reused
- [ ] No entry was edited or deleted after being written; every correction is an appended `REVERSAL`
- [ ] Every mandatory-logging item from section 5 is present, including null results and any substrate fallback
- [ ] Every QA verdict is logged, including passes, with its proof boundary
- [ ] Wall-clock stamps record when entries were written; **no durations, estimates, or forecasts anywhere**
- [ ] Every acronym expanded on first use; no internal shorthand a stranger could not follow
- [ ] Worked examples above deleted, leaving only real entries
