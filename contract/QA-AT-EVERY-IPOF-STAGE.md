# QA at Every IPOF Stage

Canonical standard. Single source of truth for how quality is checked during work, not after it.
Portable edition: this copy is written to travel into an unfamiliar repository whose language,
framework, and test runner are unknown.

IPOF means Input, Processing, Output, Feedback - the micro loop that governs the quality of a single
piece of work. (The macro loop, GRAA - Goal, Reality, Analysis, Action - governs direction and is out
of scope here.)

This standard exists because quality assurance placed only at the end is the most expensive place to
put it. Every rule below moves a check earlier.

If brevity and this standard ever conflict, this standard wins.
A fast answer that is confidently wrong about the state of the world is the exact failure this exists
to prevent.

---

## 1. The spine: inspect at the lowest-value-added stage

The organizing principle is Andy Grove's production-line rule from *High Output Management*: inspect
at the lowest-value-added stage, because the cost of scrapping a unit rises with every step of value
added to it.

Translated to knowledge work: **the cost of a defect escalates the later it is caught.** A wrong
assumption caught at Input is a sentence rewritten. The same wrong assumption caught at Output is a
deliverable rebuilt. Caught after delivery, it is credibility.

Two consequences follow, and they are the whole standard:

1. QA is **not** an end-of-cycle gate. It is four gates, one per IPOF stage.
2. Effort is **weighted toward the cheapest catch-point**, which is almost always Input - the
   stage most often skipped.

---

## 2. What this covers, and what it does not

This governs any unit of work that produces a claim or an artifact someone will act on: an analysis,
a change to a system, a deliverable, a recommendation.

It does NOT mandate an audit program. Proportional rigor is a rule of this standard, not an exception
to it: the depth of a check scales with the reversibility and blast radius of the work, never with
how interesting the work feels. A four-gate ritual applied to a trivial, reversible change is waste,
and waste is its own defect. Section 7 sets the floor.

---

## 3. The four stage gates

Each gate below defines five things: what is checked, who checks it, the cheapest catch-point, the
evidence required, and the verdict language used.

### 3.1 INPUT QA - cheapest, most skipped

**What is checked.** That the preconditions, the state of the world, and the assumptions are actually
what you believe them to be, BEFORE any processing starts. Specifically:

- **The ask.** What is being requested, restated in your own words, with the success condition named.
- **The ambiguities.** Every place the request admits more than one reasonable reading. Each is
  listed, the readings named, one chosen, and the reason recorded. An ambiguity resolved silently is
  an untracked risk; an ambiguity resolved *and written down* is a decision.
- **The state.** Facts asserted by the brief are verified against the actual artifact - the file
  exists, the field is populated, the endpoint answers, the dataset has rows. A brief is a claim
  about the world, not the world.
- **The boundary.** What is explicitly out of scope, and what is assumed rather than known.

**Who checks.** The doer, as a required first step. This is self-QA and is not delegable - nobody
else can see the assumptions in your head.

**Cheapest catch-point.** Before the first unit of work is produced. Nothing has been built, so
nothing can be scrapped.

**Evidence required.**
- A written restatement of the ask and the success condition.
- An ambiguity register: ambiguity, readings considered, resolution, rationale. Unresolvable
  ambiguities are listed as open questions with the assumption being run under.
- A precondition check list: each asserted fact, how it was confirmed, confirmed or not confirmed.

**Verdict language.** `INPUT VERIFIED` · `INPUT VERIFIED WITH STATED ASSUMPTIONS` · `INPUT NOT
VERIFIED - proceeding is a gamble on <named unknown>`.

> This gate is where the most damage has actually been prevented, and where its absence has actually
> caused harm: the incident that produced this standard was an operator acting twice on an unverified
> system state.

### 3.2 PROCESSING QA - checkpoints during execution

**What is checked.** That execution is still on the rails, at defined points *inside* the work rather
than at its end. Two distinct triggers:

- **Scheduled checkpoints.** At each natural seam of the work, confirm the intermediate result is
  what the plan predicted before building the next layer on top of it.
- **Risk-triggered independent review.** A second set of eyes BEFORE any irreversible or high-stakes
  step. The triggers are named in advance, not judged in the moment:
  - destructive, irreversible, or hard-to-reverse operations (deletion, overwrite, migration);
  - anything touching production, shared infrastructure, credentials, authentication, tenancy,
    privacy, or money movement;
  - **error clustering** - the operator has already made a mistake in this session. An error cluster
    is a signal about the operator's current state, not about the task. Stop and get eyes.

**Who checks.** The doer owns the scheduled checkpoints. The risk-triggered review is owned by a
*different execution context* - a second person, a separate session, or an independent agent that did
not produce the work. Independence here is structural, not attitudinal.

**Cheapest catch-point.** Immediately before the irreversible step, and at the first seam after a
wrong turn is possible.

**Evidence required.**
- The checkpoint result compared against what the plan predicted, with the delta named.
- For a risk-triggered review: the named trigger, the identity of the independent reviewer, what they
  examined, and their explicit go / no-go.
- For an irreversible step: the reversal path, or an explicit statement that there is none.

**Verdict language.** `CHECKPOINT ON PLAN` · `CHECKPOINT DEVIATION - <delta>, <action taken>` ·
`GO (independent review, trigger: <trigger>)` · `NO-GO - <blocking reason>`.

### 3.3 OUTPUT QA - adversarial verdict on the deliverable

**What is checked.** The claim the deliverable makes, attacked rather than confirmed. Output QA asks
"how would I show this is wrong?", never "does this look right?". The operational discipline is in
`QA-AGENT-SOP.md`; this section defines the gate it satisfies.

The three things that must be established:

- **The claim is true on the real path** - exercised the way it will actually be used, against
  realistic state, not an empty fixture that passes vacuously.
- **The verifier itself verified something.** A green check from a check that examined zero rows,
  zero files, or zero cases is not evidence. Confirm non-empty exercise.
- **The limits are stated.** Everything outside what was actually executed is labelled not verified.

**Who checks.** Ideally an execution context that did not build the artifact. Where no second context
exists, the doer runs the adversarial pass explicitly and in writing, and labels it self-QA - which
is weaker evidence and must be shown as weaker, not presented as independent.

**Cheapest catch-point.** Before the deliverable is handed to anyone who will act on it.

**Evidence required.** A completed verdict record - see `templates/qa-verdict.md`. Minimum: claim
under test, method, evidence with receipts, verdict, explicit limits.

**Verdict language.** `PASS` · `FAIL` · `CONDITIONAL PASS - <condition>` · `NOT VERIFIED`.
See section 5 for what each is allowed to mean.

### 3.4 FEEDBACK QA - ratification and the correction that feeds back

**What is checked.** That an authorized human has actually accepted the work, and that any correction
is captured somewhere durable enough to change the next cycle. Without this stage the same defect is
paid for repeatedly.

- **Ratification.** The human who owns the outcome accepts, rejects, or corrects. Silence is not
  acceptance.
- **Correction capture.** Each correction is recorded as: what was wrong, what the right answer is,
  and - the load-bearing part - **which earlier gate should have caught it**.
- **Gate reassignment.** A defect that reached Output but originated at Input means the Input gate
  was too weak. The fix belongs at the earlier gate, not in a bigger final inspection. This is the
  mechanism by which the loop compounds instead of merely repeating.

**Who checks.** The authorized human owner. Not the doer, and not the reviewer.

**Cheapest catch-point.** At handoff, while the work is still fresh and the context to act on the
correction still exists.

**Evidence required.** The ratification decision and its owner; each correction with its attributed
originating gate; the resulting change to how the next cycle's gates run.

**Verdict language.** `RATIFIED` · `RATIFIED WITH CORRECTIONS - <corrections, attributed gate>` ·
`REJECTED - <reason>` · `AWAITING RATIFICATION` (never silently upgraded to ratified).

---

## 4. The stage-gate table

| Stage | Checks | Checked by | Cheapest catch-point | Evidence | Verdict |
|---|---|---|---|---|---|
| Input | Ask, ambiguities, state, boundary | The doer (required first step) | Before any work is produced | Restated ask, ambiguity register, precondition checks | `INPUT VERIFIED` / `WITH STATED ASSUMPTIONS` / `NOT VERIFIED` |
| Processing | Seam checkpoints; independent review at named risk triggers | Doer; independent context for triggered review | Immediately before the irreversible step | Checkpoint vs. plan delta, reviewer identity, reversal path | `ON PLAN` / `DEVIATION` / `GO` / `NO-GO` |
| Output | The claim, attacked on the real path | Independent context preferred; self-QA labelled as such | Before anyone acts on it | Completed verdict record | `PASS` / `FAIL` / `CONDITIONAL PASS` / `NOT VERIFIED` |
| Feedback | Ratification and correction, attributed to the gate that should have caught it | Authorized human owner | At handoff | Decision, corrections, gate reassignment | `RATIFIED` / `WITH CORRECTIONS` / `REJECTED` / `AWAITING` |

---

## 5. Verdict language, and what it may not mean

Verdict words are load-bearing and are not interchangeable with confidence.

- **PASS** - a specific claim was attacked on the real path with real state and did not break. PASS
  applies only to what was executed. It never generalizes.
- **FAIL** - the claim broke, with a reproducible case. A FAIL must carry the minimal reproduction.
- **CONDITIONAL PASS** - the claim holds only under a stated condition. The condition is part of the
  verdict and travels with it.
- **NOT VERIFIED** - the check was not run, could not be run, or ran without exercising the target.
  This is the correct verdict under uncertainty and is never a failure of the reviewer.

Three prohibitions:

- A green signal from a check that exercised nothing is `NOT VERIFIED`, never `PASS`.
- A PASS on one axis may not conceal a FAIL or NOT VERIFIED on another. Where an artifact is checked
  on more than one axis (for example: does the mechanism work, *and* does it still serve the original
  purpose), the axes report separately and both must pass before the work is called complete.
- Completion language - done, complete, verified, production-ready - is gated on the verdicts. It is
  not available because the work feels finished.

---

## 6. Portability

Nothing above names a language, framework, test runner, or tool. It is stated in terms of gates,
evidence, and verdicts so it survives contact with an unfamiliar repository.

In an unfamiliar codebase the gates bind as follows:

- **Input** - verify the repository's actual state before trusting any description of it: what exists,
  what runs, what the data really contains. The brief's description of the repo is an Input claim to
  be checked like any other.
- **Processing** - the risk triggers are properties of the operation, not of the stack. Deleting,
  overwriting, and migrating are irreversible in every language.
- **Output** - use whatever verification the repository already provides. If it provides none,
  exercise the real path manually and say so; "no automated verification available, exercised
  manually" is an honest and complete evidence statement. Inventing a tool that is not there is a
  fabrication.
- **Feedback** - the correction and its gate attribution are recorded in whatever artifact the
  audience will actually read.

---

## 7. Proportionality - the floor and the ceiling

The floor, always: **Input QA and Feedback QA**. They are the two cheapest gates and the two most
often skipped. Verify your preconditions; get the work ratified and capture the correction.

Processing QA scales with irreversibility. No irreversible step, no triggered review.

Output QA scales with who acts on the result and how hard the consequence is to undo.

The ceiling: high risk increases rigor **on that specific risk**. It does not authorize a second
skeptic, a broadened matrix, a full-system audit, or unrelated regression expansion. The right proof
is the **smallest one that could actually refute the claim**. A proof that could never have returned
FAIL was not a proof.

---

## 8. Why this is a structural standard and not a reminder

The distinguishing commitment: these gates are built into how work is *authored*, not appended as
advice.

1. **Every brief** carries an explicit Input-QA step, a risk assessment that names its
   Processing-QA triggers, and an Output-QA gate. "Done" is defined to include the gates.
2. **Every loop** - human or automated - assigns the gates to roles by design: a QA'd input brief,
   an executing doer, an adversarial output reviewer, a human feedback node.
3. **Catches are recorded**, including which gate caught them and what the later catch would have
   cost. This is how the standard is measured rather than assumed.

The return is two things, and the second is usually left out: **correctness, and calm.** An operator
working behind verified gates does not have to spend attention doubting completed steps. Confidence
under pressure is an output of the process, not a personality trait.

---

## 9. Related documents

- `QA-AGENT-SOP.md` - the operational procedure an adversarial reviewer follows at the Output gate.
- `templates/qa-verdict.md` - the fill-in verdict record required as Output-QA evidence.

Source of the inspection principle: Andy Grove, *High Output Management* - inspect at the
lowest-value-added stage.
