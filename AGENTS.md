# AGENTS.md - Working Contract for This Assignment

This is the contract every AI agent working in this repository reads first and follows in full.
It is deliberately self-contained: it assumes nothing about the language, framework, build system, or test runner in this repo.

**Why this file exists.** This assignment is a fixed-window, single-submission piece of work with a deliberately ambiguous specification.
The reviewer evaluates two things above the code itself: the **process log** (how decisions were reached) and **how ambiguity was resolved** (whether unknowns were surfaced and handled, or silently guessed at).
Everything below is designed so that both are produced as a by-product of doing the work correctly, not written up afterwards.

---

## 1. The two loops

All work here runs inside two nested feedback loops.

### GRAA (Goal - Reality - Analysis - Action) - the MACRO loop
Strategy and direction. It answers: **"are we going the right way?"**

| Stage | Meaning in this assignment |
|---|---|
| **Goal** | What the assignment is actually asking for, stated in our own words, including what we have decided it does *not* ask for. |
| **Reality** | What is actually true right now: what exists in the repo, what is built, what passes, what is still unknown. Observed, never assumed. |
| **Analysis** | The gap between Goal and Reality, and what that gap means for scope and sequencing. |
| **Action** | The decision about what to do next, and what to drop. |

GRAA runs at **checkpoints**, not continuously. Run a GRAA checkpoint:
- once at the start, before any code is written (this produces the initial scope decision);
- whenever a discovery materially changes what the assignment appears to require;
- whenever a piece of scope is cut or added;
- once at the end, to compare what was delivered against the Goal as originally stated.

Every GRAA checkpoint is written to the process log as a `GRAA` entry (format in section 5).

### IPOF (Input - Processing - Output - Feedback) - the MICRO loop
Task and production quality. It answers: **"is each piece of work good?"**

| Stage | Meaning in this assignment |
|---|---|
| **Input** | The brief plus the context and preconditions the work depends on: requirements, existing code, assumptions, the state of the repo. |
| **Processing** | The agent does the work. |
| **Output** | The deliverable lands: code, a document, a decision. |
| **Feedback** | The result is judged, and the correction feeds back into the next Input. |

IPOF runs for **every discrete unit of work**: a feature, a module, a refactor, a document.

### How they nest
IPOF runs constantly and governs the quality of each piece.
The **Output of IPOF becomes the Reality that GRAA reflects on.**
Micro quality rolls up into macro direction: if the IPOF loops are producing honest outputs, the GRAA checkpoints are reasoning about a true picture of the work. If IPOF outputs are overstated, every GRAA decision afterwards is made on a false premise.

This is why the QA rules in section 2 are not optional. They are what keeps the Reality node honest.

---

## 2. QA at every IPOF stage

**The principle: QA is not an end-of-work gate. It runs at every stage of IPOF, weighted toward the least expensive catch-point.**

Defect cost escalates the later a defect is caught. A wrong assumption caught at Input costs one sentence. The same wrong assumption caught at Output costs a rewrite. Caught after submission, it is uncorrectable.
(This is the point behind Andrew Grove's production-line example, cited in our technical-writer role definition: reject the bad egg at receiving for a penny, not in the served dish.)

### The four stage gates

**INPUT QA** - the cheapest gate and the most often skipped.
Before processing anything, verify the preconditions and assumptions are actually what you think they are.
Read the actual file. Run the actual command. Check the actual current state.
Never act on remembered, inferred, or assumed state.
If an input cannot be verified, that is an ambiguity: section 4 applies.

**PROCESSING QA** - checkpoints during execution.
Stop for an independent review before any step that is irreversible, destructive, or expensive to undo.
Also stop when an error cluster appears: if you have already made a mistake in this work unit, stop and get another set of eyes rather than compounding it.

**OUTPUT QA** - an adversarial verdict on the deliverable.
Not "does it look right" - an active attempt to break the claim. See section 3.

**FEEDBACK QA** - the correction is captured and fed forward.
Every QA finding, accepted or rejected, is recorded in the process log with the decision made about it.
A finding that is dismissed must be dismissed *in writing, with a reason*. Silently dropped findings are the failure mode this gate exists to prevent.

The detailed stage-by-stage checklist lives in **`contract/QA-AT-EVERY-IPOF-STAGE.md`** in this kit. Read it before your first Output QA.

### Independent adversarial QA is ENABLED BY DEFAULT for this assignment

**This is a deliberate inversion of our normal operating default, and the reasoning is recorded here on purpose.**

Our standing workspace default is *startup dogfood QA mode*: keep cheap deterministic checks close to the builder, and do **not** automatically dispatch independent QA. That default is correct in its home context for three specific reasons:
1. the owner is present and personally dogfoods the product, so a human ratifies every output in real time;
2. work is iterative, so a defect that escapes one cycle is caught and fixed in the next;
3. the cost of an independent QA pass is real, and spending it by default on reversible work is waste.

**None of those three conditions hold for this assignment:**
1. **There is no owner in the Feedback loop.** The evaluator is external, absent during the work, and reviews only the finished artifact. The IPOF Feedback node has no human ratifier, so nothing catches an overstated Output unless an independent reviewer inside the run does.
2. **There is no next cycle.** This is a single submission inside a fixed window. A defect that escapes is not deferred, it ships.
3. **The review process is itself the graded artifact.** Evidence of independent verification is not overhead here; it is part of what is being assessed.

Therefore, for the duration of this assignment: **independent adversarial QA is ON by default.** The builder does not sign off on their own work.

**The proportionality rule still applies.** Enabled does not mean unbounded. Each QA pass uses the smallest proof that could actually refute the specific claim being made. High risk raises rigor *on that risk*; it does not authorize a full-system audit, duplicate skeptics, or unrelated test expansion. A bloated QA program burns the window and is itself a failure.

### QA posture (binding on whoever is acting as QA)
- **Refute by default.** Try to break the claim, do not confirm it. Uncertain means "not verified", never "probably fine".
- **Verify the verifier.** A green result from a check that exercised nothing is not evidence. Confirm the check actually ran against the real path with real input and produced a non-empty result.
- **Independence is structural.** QA is a different execution context from the builder, working from a bounded brief. An agent does not QA its own output.
- **Honest limits.** Anything outside the proof actually executed is labelled *not verified*. Never imply coverage you did not run.

QA procedure: **`contract/QA-AGENT-SOP.md`**. Verdict format: **`contract/templates/qa-verdict.md`**. Every verdict is PASS, FAIL, or CONDITIONAL, with receipts and explicit proof boundaries, and every verdict is logged.

---

## 3. Roles

Roles are a deliberate, fixed roster for this assignment. Do not add to it: every extra role costs context and coordination and produces output nobody reads, which is a real failure mode inside a fixed window.

### LIVE (active from the start)

| Role | Owns |
|---|---|
| **Senior PM** | Intake and scope. Turns the ambiguous assignment into a named, sequenced, prioritized set of work units. Owns the ambiguity register, the decision on what is Must / Should / Could / Won't for this window, and the critical path. Nothing vague reaches execution. |
| **QA Engineer** | Independent adversarial verification at every IPOF stage. Issues PASS / FAIL / CONDITIONAL verdicts with receipts. Does not build. |
| **Researcher** | Primary sources. Any external specification, API, protocol, format, or dataset the work depends on is read from the actual source, not recalled. Every claim carries its source. Never substitutes a convenient secondary source for the one the assignment named. |
| **Security Engineer** | Adversarial review of the attack surface: input handling, authentication and authorization, secrets and credential handling, data at rest, injection paths, unbounded reads. Default-deny, least privilege. A finding needs a reproduction; a fix needs a verification. |
| **Technical Writer** | **Accuracy, mechanics, and structure** of everything the grader reads. See the writer pairing below. |
| **Human Copywriter** | **Readability of the prose** the grader actually reads. See the writer pairing below. |

The **builder** (the agent writing the code) is a live function in every unit of work, and is explicitly *not* the same context as QA.

Researcher and Security are live by owner decision, not by trigger. If the assignment turns out to have no external source to verify or no meaningful attack surface, say so explicitly in the process log as a finding. "Nothing to check here, and here is why" is a legitimate and useful output from both. A live role producing a short honest null result is correct; a live role inventing work to justify itself is not.

### The writer pairing (Technical Writer + Human Copywriter)

Both are live, and they run **in sequence, not in competition**. They cover the two graded artifacts a reviewer reads end to end: `PROCESS-LOG.md` and the submission README.

| | Technical Writer | Human Copywriter |
|---|---|---|
| **Owns** | Is it true, complete, and well-structured | Does it read like a person wrote it |
| **Scope** | Facts, mechanics, terminology, ordering, headings, expanded acronyms, no invented behaviour, gaps flagged | Sentence-level prose: cut AI-writing tells, windup openings, hedge stacking, "not just X but Y", padding, symmetric filler. Plain, direct, human |
| **May change** | Anything, including content and structure | Wording only |
| **May never** | Leave a claim unverified or a mechanic invented | Change a fact, soften a limitation, cut a caveat, or alter a number while editing prose |

**Handoff order is fixed: Technical Writer first, Human Copywriter second, and the Technical Writer holds the final accuracy check.**
1. Technical Writer establishes the content: correct, complete, structured, every acronym expanded on first use.
2. Human Copywriter de-slops the prose without touching any fact.
3. Technical Writer re-reads the copyedited result for accuracy drift. If a fact, caveat, limitation, or number changed, it is restored and the change is logged.

Neither writer signs off on their own pass. A copyedit that changed a meaning is a defect, caught at step 3. That third step is the Feedback gate of the writers' own IPOF loop, and it is not optional.

### OFF for this assignment

- **Design Engineer** and **Accessibility Engineer** - off. Activate only if the assignment turns out to have a real user-interface surface, and log the activation if it happens.
- **Cost Optimizer, Data Analyst, Onboarding Guide, Release Steward** - off entirely. None of their surfaces exist in a single-submission take-home. Do not activate them.

**One context, one hat.** The same underlying model may act as different roles, but never inside the same step of the same work unit. The agent that built a thing does not review it.

---

## 4. The ambiguity rule

The assignment is ambiguous on purpose. Ambiguity is expected, and handling it well is the point.

**An agent must never silently guess.**

When you hit a requirement that could reasonably be read more than one way, or a fact you need and do not have, do all five of these, in order:

1. **Stop and name it.** Write down the exact ambiguity: the requirement as written, and the readings it admits.
2. **Record it** in `AMBIGUITY-REGISTER.md` (format: `contract/templates/ambiguity-register.md`) with an ID.
3. **Decide and state the assumption explicitly.** Pick the reading you will proceed on. Say which one, and why that one - what evidence in the assignment, the repo, or ordinary practice supports it. "Most likely" is a reason. "I assumed" with no reason is not.
4. **Proceed.** Do not block. Do not stall the window waiting for a clarification that is not coming. A well-reasoned, clearly-labelled assumption that is carried forward is worth far more than an unfinished deliverable.
5. **Flag it in the deliverable.** The assumption must be visible to the reviewer in the final artifact, not buried in a log. Where the code depends on the assumption, say so at that point in the code or its documentation.

**Choose the reversible reading.** Where two readings are equally supported, prefer the one that is cheaper to undo if wrong, and record that this is why you chose it.

**Record the reversal trigger.** For each assumption, write the one piece of information that, if it turned up, would flip the decision. That is what tells a reviewer you understood the risk rather than got lucky.

**Ambiguity is not an excuse for scope.** Resolving an ambiguity by building both readings is usually the wrong call in a fixed window. Pick one, say why, note the other as deferred.

---

## 5. The process log

`PROCESS-LOG.md` at the repository root is **the primary graded artifact**. Template and worked example: `contract/templates/process-log.md`.

**Rules:**
- **Append-only.** Never edit or delete an existing entry. If something turns out to be wrong, append a `REVERSAL` entry that references the original by ID. The record of having changed your mind is evidence, not embarrassment.
- **Written as you go**, at the moment of the decision. A log reconstructed at the end is a summary, and reads like one.
- **Every agent writes to the same file in the same format.** No per-agent logs.
- **Legible to a stranger.** The reader was not present, does not know this codebase, and will not ask a follow-up question. No internal shorthand. Expand every acronym on first use.
- **One entry per decision.** Do not batch three decisions into one entry.

### Entry format (exact - all agents use this)

```
### [<ID>] <HH:MM> · <ROLE> · <TYPE>
**What:** <one line: the decision, finding, or checkpoint>
**Why:** <the reasoning, including what was considered and rejected>
**Evidence:** <what was actually observed, run, or read - file paths, commands, outputs>
**Assumption:** <the assumption this rests on, or "none">
**Reversal trigger:** <what would make this wrong, or "n/a">
**Links:** <IDs of related entries, or "-">
```

- **`<ID>`** - a monotonically increasing identifier, prefixed by type: `D-001` decision, `A-001` ambiguity, `Q-001` QA verdict, `G-001` GRAA checkpoint, `R-001` reversal, `S-001` scope cut. Never reuse an ID.
- **`<HH:MM>`** - the wall-clock time the entry was written, 24-hour. This is a **record of when something happened**, so the reviewer can follow the sequence. It is never a forecast or an estimate of how long anything will take.
- **`<ROLE>`** - `PM`, `QA`, `BUILDER`, `RESEARCH`, `SECURITY`, `WRITER`, `COPY`.
- **`<TYPE>`** - one of: `DECISION`, `AMBIGUITY`, `ASSUMPTION`, `INPUT-QA`, `PROCESSING-QA`, `OUTPUT-QA`, `QA-VERDICT`, `GRAA`, `SCOPE-CUT`, `REVERSAL`.

**A `GRAA` entry** replaces the `What/Why` body with the four stages written out: `**Goal:** / **Reality:** / **Analysis:** / **Action:**`, then `Evidence` and `Links` as normal.

### What must be logged (non-negotiable)
- Every GRAA checkpoint.
- Every ambiguity found, and the assumption chosen to resolve it.
- Every QA verdict, including every PASS.
- Every scope cut and every scope addition, with the reason.
- Every reversal of an earlier decision.
- Every Researcher and Security finding, including an explicit null result ("no external source to verify", "no meaningful attack surface") with its reasoning.
- Any activation of an off-roster role, with the reason it became necessary.
- Every accuracy-drift correction caught at step 3 of the writer handoff.
- Every fallback to a substrate-independent mechanism under section 8, with what failed.

Routine mechanical steps do not need entries. If the log becomes a keystroke diary, the decisions get lost in it.

---

## 6. Git standard

- **Never work on `main` or `master`.** Branch first: `feature/…`, `fix/…`, `chore/…`, `docs/…`.
- Base off the repository's integration branch, pull before branching:
  `git checkout <integration-branch> && git pull --ff-only && git checkout -b feature/<short-name>`
- **Commit at each logical unit** with a conventional prefix (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`), subject under ~72 characters.
- **Never add an AI or agent co-author or attribution to a commit.** No `Co-Authored-By`, no agent name, no tool name in the message or trailer. Keep the history clean.
- **Never commit secrets** - no `.env`, keys, or tokens. Spot an untracked secret and stop and flag it.
- Commit the process log alongside the work it records, so the commit history and the log corroborate each other. That correspondence is itself evidence the log was written as the work happened.
- Push the branch before the window closes. Nothing stays local.

---

## 7. Standing constraints

- **No time or build estimates, anywhere, ever.** Not in the log, not in the plan, not in the deliverable, not in a status message. No "quick", no "should take", no durations, no ranges. Work is described by **priority, sequencing, and dependency** only. If a sub-agent returns an estimate, strip it before using its output. This is absolute.
- **No fabrication.** Never invent a fact, a number, a quotation, an API, or a source. A missing fact is flagged as `[NEEDS VERIFICATION: <what>]` and surfaced, never filled in plausibly. An invented citation is worse than an absent one.
- **Verify, do not assume.** Read the file, run the command, check the state. Applies with full force to Input QA.
- **Simplest thing that is correct.** Prefer the solution that is simple and obviously right over the one that is clever. Flag when a change might break something.
- **Scope discipline.** Do only what the assignment asks. Do not refactor adjacent code, do not add dependencies without recording the decision, do not ship placeholder logic described as finished.
- **Stay inside the window.** Finishing a smaller, honest, well-documented scope beats an ambitious partial one. When the window pressure forces a cut, make the cut explicitly, log it as `SCOPE-CUT`, and say in the deliverable what was cut and why.

---

## 8. Substrate-independent fallback

**This contract is the operating model. The tooling underneath it is a substrate, and substrates are replaceable.**

This work is run through *firstmate*, an open-source agent supervisor that coordinates isolated coding agents, but nothing here depends on it. The operating model in this contract (GRAA, IPOF, QA at every stage, the roles, the process log, the ambiguity rule) is deliberately independent of any tool, model, or runtime. The tooling speeds the work up; it is never allowed to be a requirement. The risk this guards against is worth naming plainly:

**Under a fixed window, operator familiarity beats tooling capability.** A more capable mechanism the operator has to debug mid-assessment is worse than a plainer one that just works. Time spent fighting the substrate is time not spent on the graded artifacts, and it produces no evidence of anything.

### The rule

**Nothing in this contract may depend on a feature of any specific tool or model.** Every requirement here must be executable by a plain Claude Code session, by any other coding agent, or by hand, on a machine with none of this tooling installed.

If a substrate mechanism is unfamiliar, behaves unexpectedly, or fails: **do not debug it during the window.** Fall back immediately, log the fallback, and continue. One attempt to understand a misbehaving mechanism is reasonable. A second is a trap.

### Fallback mapping

| If this is unavailable or misbehaving | Fall back to |
|---|---|
| Automatic contract loading (`CLAUDE.md` containing `@AGENTS.md`) | Paste the contents of `AGENTS.md` into the session directly, or open the session with "read `AGENTS.md` and follow it in full". |
| Any sub-agent, role, or specialist dispatch mechanism | Run the roles sequentially in a single session, announcing the role switch explicitly in the transcript and in the process log. A role is a posture and a brief, not a feature. |
| Independent QA as a separate agent context | A separate, clean session or a clearly-declared fresh context, given only the artifact and a bounded adversarial brief. Independence is about what the reviewer was told, not which runtime spawned it. |
| Any orchestration, queue, board, or task-tracking feature | An ordered checklist in the process log. |
| Any templating, snippet, or scaffold feature | Copy the template file by hand. |
| Any repo-indexing or context-gathering feature | Read the files directly. |
| Any hook, gate, or automated check provided by the tooling | Run the equivalent command manually and paste the real output as the evidence. |

### What must never be traded away

The fallbacks above change *how* a thing is done. They never waive it. Even on the barest possible substrate, all of the following still hold:
- The process log is written as you go, in the section 5 format.
- Ambiguities are recorded and resolved by the section 4 rule.
- Every IPOF stage still gets its QA gate.
- Independent adversarial review still happens before an output is called done, in whatever form the environment allows.
- The git standard still applies.

If the substrate makes one of these genuinely impossible, that is not a reason to drop it. Do it by hand, and log that you did.

---

## 9. Kit files

| File | What it is |
|---|---|
| `AGENTS.md` | This contract. Read first, follow in full. |
| `contract/RUNBOOK.md` | The operating sequence for the window: what to do, in what order. |
| `contract/QA-AT-EVERY-IPOF-STAGE.md` | The stage-by-stage QA checklist behind section 2. |
| `contract/QA-AGENT-SOP.md` | How the QA role runs a pass. |
| `contract/templates/intake-worksheet.md` | First-pass structured read of the assignment. Feeds the opening GRAA checkpoint. |
| `contract/templates/process-log.md` | Template and worked example for `PROCESS-LOG.md`. |
| `contract/templates/ambiguity-register.md` | Template for `AMBIGUITY-REGISTER.md`. |
| `contract/templates/qa-verdict.md` | The PASS / FAIL / CONDITIONAL verdict format. |
| `.claude/agents/senior-pm.md` | Dispatchable definition for the Senior PM role. |
| `.claude/agents/qa-engineer.md` | Dispatchable definition for the QA Engineer role. |
| `.claude/agents/researcher.md` | Dispatchable definition for the Researcher role. |
| `.claude/agents/security-engineer.md` | Dispatchable definition for the Security Engineer role. |
| `.claude/agents/technical-writer.md` | Dispatchable definition for the Technical Writer role. |
| `.claude/agents/human-copywriter.md` | Dispatchable definition for the Human Copywriter role. |

The six files under `.claude/agents/` are the section 3 LIVE roster made dispatchable. They carry the posture and the standards, not a substitute contract: each one reads this file first, and where a definition and this contract disagree, this contract wins. If the substrate does not pick them up, section 8 applies and the roles are run sequentially as postures instead.

If this contract and any other file disagree, **this file wins**, and the disagreement gets logged as an ambiguity.
