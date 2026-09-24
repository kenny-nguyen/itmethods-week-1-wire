# RUNBOOK - Operating Sequence for the Window

The order of operations for this assignment, from first read to submission.

**Read `AGENTS.md` first - it is the contract and it wins over this file.** This runbook is the *sequence*; the contract is the *rules*. Where they disagree, the contract governs and the disagreement is logged as an ambiguity (`AGENTS.md` section 9).

Nothing here assumes a language, framework, build system, or test runner.

---

## Who this is written for

Two readers, and they want different things:

1. **The operator, working under window pressure.** Every step must be executable without re-reading the theory. If a step is too elaborate to actually follow, it is wrong.
2. **An external grader who was not present.** They see only what is submitted. They are explicitly assessing the **process log** and **how ambiguity was resolved** (`AGENTS.md`, "Why this file exists").

The design rule that follows: **produce the evidence as a by-product of working, never as a write-up at the end.** A log reconstructed afterwards reads reconstructed.

---

## Phases

```
P0 INTAKE          → understand the assignment and what is actually being assessed
P1 AMBIGUITY       → register every unknown, decide each one, log the decision
P2 SKELETON        → thinnest end-to-end slice, working, before any depth
P3 DECOMPOSE       → cut parallel units against the now-real interfaces
P4 PARALLEL BUILD  → agents work units, IPOF each, QA every stage
P5 FREEZE          → stop adding, harden what exists
P6 SUBMISSION      → artifact + process log + ambiguity register + QA verdicts + README
```

### Phase transitions are gated by EVENTS, never by the clock

Every transition below names the event that gates it.

This is not a stylistic preference. Under a fixed window, a clock-gated phase invites you to ship a half-built phase because a number was reached. An event-gated phase makes the gate a fact you can point at. It also forces the right response to falling behind: **if the gating event has not happened, cut scope - do not slide the gate.**

`AGENTS.md` section 7 is absolute on this: no durations, no ranges, no "should take", anywhere, ever. Wall-clock `HH:MM` stamps in the process log are a different thing and are required - they **record when something happened** so the reviewer can follow the sequence. A record is not a forecast.

---

## P0 - INTAKE

**Purpose:** know what is actually being asked, and what is actually being graded.

Fill `templates/intake-worksheet.md`. **Do not open an editor before it is complete.** The highest-probability failure on a deliberately ambiguous assignment is solving a more interesting adjacent problem, well.

### The three-column read

Read the assignment once at normal speed. Then read it again, sorting every sentence into exactly one column.

| Column | Definition | Treatment |
|---|---|---|
| **STATED** | Written explicitly. Quote it verbatim. | Non-negotiable. This is the contract with the grader. |
| **IMPLIED** | A reasonable reader infers it, but the text does not say it. | Name it as *your inference* and state your confidence. Weight-bearing inferences get an ambiguity register row. |
| **UNSPECIFIED** | Genuinely absent. The text is silent and no safe inference exists. | Register row. Every one. No exceptions. |

An IMPLIED item is **weight-bearing** if the build changes materially when the inference is wrong. Those, plus every low-confidence inference, go to the register.

Two failure modes this sort exists to prevent:
- Promoting an IMPLIED item to STATED, then building a requirement nobody asked for.
- Silently resolving an UNSPECIFIED item in your head and never telling the grader you decided it.

The second is the expensive one. **An undocumented decision is indistinguishable from an oversight.** This is the section 4 rule of the contract: never silently guess.

### Extract the real evaluation criteria

The stated task is a vehicle. Write down, explicitly, what sits behind it:

- What capability does this assignment *test*?
- Where has it been left deliberately thin - and what would a strong candidate do there that a weak one would not?
- What would **fail** this submission even if the artifact works? (Usually: no reasoning shown, scope sprawl, or a silent wrong assumption.)
- Is a deliverable format stated? Honour it exactly. Format non-compliance is the cheapest possible way to lose points.

Write the conclusion as one sentence:

> I believe this assessment is testing ______, and the deliberate ambiguity is concentrated in ______.

That sentence steers every later phase, and it reappears in the submission README.

### Clarification

If the assignment permits clarifying questions, send them at the top of P0 and **keep working against your assumption while you wait.** Never block - contract section 4, step 4. Ask few, ask high-leverage: only the ones where different answers produce materially different work. Log the question and the assumption you proceeded on.

**Exit event:** intake worksheet complete, including the one-sentence read.

---

## P1 - AMBIGUITY REGISTER

**The core artifact for the capability being graded.** Use `templates/ambiguity-register.md`, which writes to `AMBIGUITY-REGISTER.md`.

Contract section 4 defines the rule; this is how to run it under window pressure.

Every ambiguity carries: the question, the options considered, the assumption taken, the rationale, the **reversal trigger** (the one piece of information that would flip the decision - required by section 4), the reversal cost, and a status. Each one is logged to `PROCESS-LOG.md` as an `A-nnn` entry at the moment it is decided.

### The decision rule

**Order ambiguities by reversal cost, not by how interesting they are.**

- **Low reversal cost** → decide immediately, log it, move on. Do not deliberate. Most ambiguities are here, and they are a trap: deliberating cheap decisions is the classic way to lose a fixed window.
- **High reversal cost** → these deserve real thought, and the grader is most likely watching them. **Prefer the reading that keeps the other reading open** - contract section 4, "choose the reversible reading" - even when it is slightly less elegant, and record that reversibility *is* the reason you chose it.

**Default when genuinely torn:** take the narrower, simpler reading, ship it end to end, and log the wider reading as a documented non-goal. A working narrow answer with the wider one named beats a broad answer that does not run.

**Never resolve an ambiguity by building both readings.** Contract section 4: pick one, say why, note the other as deferred.

### Keep it live

New ambiguities surface mid-build; that is normal and expected. A register holding only P0 entries looks like a form filled in once.

**Append-only, per contract section 5.** To reverse, set the original row's status to `Reversed` and append both a new register row and an `R-nnn` reversal entry in the process log referencing the original ID. Never edit in place. The trail of a reversal is stronger evidence than a run with none.

**Exit event:** every UNSPECIFIED item and every weight-bearing IMPLIED item from the worksheet has a register row whose status is not `Open`, or is explicitly marked `Open - deferred, does not block the skeleton`.

---

## P2 - WALKING SKELETON

**Principle: a thin end-to-end slice, working, before any depth anywhere.**

A walking skeleton is the narrowest path that touches every layer the solution needs and actually runs end to end. Deliberately shallow - one case, minimal handling, no polish - but **real and executable**, not scaffolding.

Why this is first, and non-negotiable:

1. **It converts unknowns into facts.** Much of the register gets cheaper to decide once something runs, because you can observe instead of speculate. This is the contract's Reality node becoming real.
2. **It guarantees a submittable artifact exists.** From skeleton-green onward, every later phase improves something already shippable. The run can never end with nothing.
3. **It makes the interfaces real, which is what P3 parallelism depends on.** Splitting work against imagined interfaces produces merge churn and rework.

**Do not parallelise this phase.** The skeleton is the shared contract that parallelism rests on, so it comes from one head. Build it yourself or with a single agent.

Commit it the moment it is green. That commit is the floor, and per contract section 6 the process log is committed alongside it.

**Exit event: the skeleton runs end to end and produces a correct result for one case.** Not "nearly". Not "once the config is fixed". Green, committed, with the Input QA gate passed on what it consumed.

---

## P3 - DECOMPOSITION

Interfaces now exist. Cut the work into units.

A unit is dispatchable to a separate agent context only if it satisfies **all** of:

- [ ] **Own scope** - an outcome statement with a verb, a subject, and a scope boundary. ("Add retry-with-backoff to the fetch path", not "improve reliability".)
- [ ] **Own files** - minimal overlap with another live unit. Overlapping file sets are the main source of merge pain and the reason to serialise two units rather than parallelise them.
- [ ] **Own verification** - the brief states what "done and correct" means and how it is checked, per `QA-AGENT-SOP.md`, with the verdict in the `templates/qa-verdict.md` format.
- [ ] **Independently mergeable** - it does not need another in-flight unit to land first.

Anything failing these is not a parallel unit; it belongs on the critical path with you.

### Critical path

Identify the chain with no slack - typically: skeleton → the core correctness behaviour → the stated deliverable format.

- Critical-path units are yours, or your most reliable agent's. Never the speculative ones.
- A "parallel" unit that blocks the critical path was mis-cut.
- **Work-in-progress (WIP) limit: cap concurrent units at what you can actually review.** Review is the bottleneck, not generation. Unreviewed agent output is not progress, it is unverified diff. More agents than you can read is strictly worse than fewer.

### Unit brief format (IPOF-shaped)

Every dispatch carries:

- **Input** - the goal, the register rows it must respect, the interface it plugs into, explicit non-goals.
- **Processing** - constraints: stay in scope, no new dependencies without a logged decision, no edits outside the named files.
- **Output** - the deliverable and its format.
- **Feedback** - what will be checked on return, and the required QA verdict.

An ambiguous dispatch is a re-run, and in a fixed window a re-run is the most expensive available mistake. Spend the words in the brief.

**Exit event:** units defined, critical path named, WIP cap set, dispatches sent.

---

## P4 - PARALLEL BUILD

Agents work their units in isolated contexts. You hold the integration seat. **Do not build in parallel with reviewing - your job this phase is Feedback, the last node of IPOF.**

Per returned unit:

1. **Output received** - does it match the brief's stated deliverable?
2. **Output QA** - adversarial, per contract section 2 and `QA-AT-EVERY-IPOF-STAGE.md`. Independent QA is ON by default for this assignment; **the builder does not sign off on their own work.** Run it. Never accept a claim of done without the artifact.
3. **Verdict** - PASS / FAIL / CONDITIONAL with receipts and explicit proof boundaries. Log it as `Q-nnn`. **Every verdict, including every PASS.**
4. **Feedback** - accept, or return with a specific correction. Vague feedback produces a vague second attempt. A dismissed finding is dismissed *in writing, with a reason* - silently dropped findings are the failure mode the Feedback gate exists to prevent.
5. **Integrate** - merge, then confirm the skeleton is still green. A merge that breaks the skeleton is reverted immediately, not debugged in place. Protect the floor.
6. **Log** - the decision, the verdict, anything surprising.

**Posture: refute by default.** Do not accept output because it is plausible. Ask what it would look like if this were wrong, and check *that*. Uncertain means "not verified", never "probably fine". A unit that looks right and was never run is a liability with your name on it.

Anything that contradicts an assumption → register row and `R-nnn` reversal entry immediately, while the reasoning is still fresh.

**Proportionality still applies.** Rigor rises on the specific risk; it does not authorise a full-system audit or duplicate skeptics. A bloated QA programme burns the window and is itself a failure.

---

## P5 - FREEZE

**Trigger: the last Must-tier item is merged and green, OR a checkpoint finds a Must still red.** Either way, freeze. From here: **no new capability - only hardening, verification, and the write-up.**

### MoSCoW (Must / Should / Could / Won't) - set at P0, enforced here

| Tier | Definition | Behaviour under pressure |
|---|---|---|
| **Must** | The submission fails without it. Always includes: the skeleton runs, the stated deliverable in the stated format, `PROCESS-LOG.md`, `AMBIGUITY-REGISTER.md`, the README. | Never cut. If a Must is at risk, cut every Should and Could and put everything on it. |
| **Should** | Clearly raises quality; real intent to ship. | First to go. Cut wholesale, not halfway. |
| **Could** | Polish, extras, depth beyond the assignment. | Cut at the first sign of pressure, without discussion. |
| **Won't (this assignment)** | Explicitly out of scope. | Write them down anyway - a named non-goal is evidence of scope judgment. Goes in the README. |

### The cut rule

Cut in this order, and cut **whole units, never partial ones**:

1. Could-tier, all of it.
2. Depth on Should-tier - keep the shallow working version, drop the enhancement.
3. Should-tier, whole units.
4. **Never** the process log, the ambiguity register, or the README. These are graded directly and they are cheap. A submission that trades the write-up for one more feature has misread the assessment.

**Cut loudly.** Every cut is an `S-nnn` `SCOPE-CUT` entry and a README line: what was cut, why, and what you would do with more room. A documented cut reads as judgment; a silent omission reads as a gap.

---

## CHECKPOINTS - the GRAA loop

At each checkpoint, stop building and write a `G-nnn` `GRAA` entry to `PROCESS-LOG.md`, four stages spelled out:

- **Goal** - the objective in one line, taken from the assignment, not from memory of your plan.
- **Reality** - what exists and is *verified* right now. Observed facts only. "Almost done" is not a Reality, it is a wish.
- **Analysis** - where Reality diverges from Goal, and what that means for scope and sequencing.
- **Action** - one steering decision: continue / re-scope / cut / reverse an assumption.

A checkpoint that produces no decision was not a checkpoint. "Continue - no divergence" is a valid logged outcome; an unwritten checkpoint is not.

Checkpoints are **event-triggered**:

| # | Trigger event | The question that matters most here | Contract requirement satisfied |
|---|---|---|---|
| **CP-1** | Intake worksheet complete, before any code | Am I solving the assignment as stated, or the one I find more interesting? | "once at the start, before any code is written" |
| **CP-2** | Walking skeleton green and committed | Do the running facts contradict any assumption? Which register rows can now be decided from observation instead of guesswork? | material-discovery checkpoint |
| **CP-3** | First parallel unit merged | Is decomposition working - is review keeping up, or is unverified diff accumulating? Adjust the WIP cap now, not later. | material-discovery checkpoint |
| **CP-4** | All Must-tier items merged and green | Freeze. Is there genuinely room for a Should, or does hardening plus the write-up take the remaining room? Default answer is the write-up. | scope-change checkpoint |
| **CP-5** | Write-up drafted, before submission | Grader's-eye read: from the submission alone, can a stranger reconstruct what was decided and why? | "once at the end, to compare what was delivered against the Goal as originally stated" |
| **CP-X** | **Any surprise** - an assumption breaks, a unit returns wrong, or you notice you are stuck | What just changed about Reality, and does the Goal still hold? | material-discovery / scope-change |

Any scope cut or addition also triggers a GRAA entry, per contract section 1.

**CP-X is the one that saves the run.** Deliberate ambiguity produces surprises by design, and the common failure is pushing through one instead of stopping to re-steer. Feeling stuck is itself the trigger. Stop, run GRAA, then continue.

---

## P6 - SUBMISSION

Five things ship. All five.

### 1. The artifact

The working solution. It must run from a clean checkout following its own instructions - **verify this on a clean clone, not in your build directory.** Broken setup instructions are a disproportionate credibility loss.

### 2. `PROCESS-LOG.md`

Append-only, written as you went, in the exact section 5 entry format. Leave the reversals and the dead ends in. A clean log reads authored; a real one reads worked.

### 3. `AMBIGUITY-REGISTER.md`

Including `Reversed` rows and every reversal trigger. This is the headline evidence for the capability being graded. Put it where a grader trips over it.

### 4. The QA verdicts

Per `templates/qa-verdict.md`. What was verified, how, the verdict, and the receipts. Include what is **not** covered - stated gaps are credibility, discovered gaps are damage. Never imply coverage you did not run.

### 5. `README.md` - the framing document

The grader reads this first and may read little else. Short and ordered:

1. **What I understood the assignment to be** - the one sentence from P0, plus the read of what was being assessed.
2. **The key ambiguities and how I resolved them** - the two or three highest-reversal-cost rows, in prose, each with its reversal trigger. Link to the full register.
3. **What I built** - scope delivered, one paragraph.
4. **What I deliberately did not build** - the Won't list and every cut, each with its reason. This section does more work than it looks like it does.
5. **What I would do next** - the first two or three things, in priority order. Shows the work is scoped, not merely unfinished.
6. **How to run it** - exact, and verified from a clean checkout.

### The writer handoff

`PROCESS-LOG.md` and the README both go through the fixed handoff in contract section 3: **Technical Writer first, Human Copywriter second, Technical Writer holds the final accuracy check.** Any fact, caveat, limitation, or number that drifted during the copyedit is restored and the correction is logged. Neither writer signs off on their own pass.

### Final pass - the stranger test

Read only what is being shipped, as someone who was never in the room:

- [ ] Stated deliverable format honoured exactly as written.
- [ ] Every UNSPECIFIED item from intake appears in the register with a decision.
- [ ] Every register row has a rationale and a reversal trigger a stranger can follow without your context.
- [ ] Every cut is named with its reason.
- [ ] Setup instructions verified from a clean checkout.
- [ ] Every QA verdict logged, including passes, with honest proof boundaries.
- [ ] No acronym unexpanded on first use. No internal shorthand, no crew names, no tooling references that mean nothing outside this repository.
- [ ] No duration, estimate, or forecast anywhere in any artifact.
- [ ] The log reads like it was written during, not after.

---

## The five rules, if nothing else survives

1. **Log the decision at the moment it is made.** Reconstruction is visible, and it is fatal.
2. **Walking skeleton before depth.** Always have something shippable.
3. **Decide cheap ambiguities fast; think hard only where reversal is expensive - and record the reversal trigger.**
4. **Cut whole units, loudly, and never cut the write-up.**
5. **Surprise is a checkpoint trigger.** Stop and re-steer rather than pushing through.
