# Intake Worksheet

First structured read of the assignment. **Fill this before opening an editor.**

Nothing here assumes a language, framework, build system, or test runner.

This worksheet feeds the opening GRAA (Goal - Reality - Analysis - Action) checkpoint, which is logged as `G-001` per `AGENTS.md` section 5. Its outputs flow into `AMBIGUITY-REGISTER.md` and into the submission README.

**Logging as you fill this in** (`AGENTS.md` section 5 - one entry per decision, never batched):
- Each ambiguity found → an `A-nnn` entry, `ROLE: PM`, `TYPE: AMBIGUITY`.
- Each scope decision → a `D-nnn` entry, `TYPE: DECISION`.
- The closing checkpoint → a `G-nnn` entry, `TYPE: GRAA`.

---

## 1. Input QA on the assignment itself

The cheapest gate in the whole run, and the one most often skipped (`AGENTS.md` section 2). Verify what you actually have before reasoning about it.

- [ ] Read the assignment text in full, from the actual source - not a summary, not a recollection.
- [ ] Located every accompanying file, dataset, link, or repository it references.
- [ ] Confirmed every referenced resource is actually reachable and readable.
- [ ] Noted anything referenced but missing → that is an ambiguity, register it.
- [ ] Confirmed the submission channel and the submission format.

**Referenced but missing or unreachable:**

| # | What is referenced | Where it should be | Status | Register ID |
|---|---|---|---|---|
| | | | Present / Missing / Unreachable | A-___ |

---

## 2. The assignment, sorted

Read once at normal speed. Then re-read, sorting **every sentence into exactly one column.** If a sentence cannot be placed, it is IMPLIED at best - never STATED.

### STATED - written explicitly. Quote verbatim.

| # | Quote from the assignment | What it obliges me to do |
|---|---|---|
| S1 | "" | |
| S2 | "" | |

### IMPLIED - a reasonable reader infers it; the text does not say it.

| # | The inference | What in the text suggests it | Confidence | Weight-bearing? | Register ID |
|---|---|---|---|---|---|
| I1 | | | High / Med / Low | Yes / No | A-___ |

**Weight-bearing** = the build changes materially if the inference is wrong. Every weight-bearing inference, and every Low-confidence inference regardless, gets an ambiguity register row.

### UNSPECIFIED - genuinely absent. **Every row here gets a register row. No exceptions.**

| # | What is missing | What it blocks | Register ID |
|---|---|---|---|
| U1 | | | A-___ |

### Prompts to force UNSPECIFIED items out of hiding

The assignment will rarely flag its own gaps. Walk this list deliberately:

- **Inputs** - source, format, volume, trust level, what a malformed one means.
- **Outputs** - exact format, destination, who consumes it, what "correct" means.
- **Scale** - how much, how often, whether it matters here at all.
- **Edge cases** - empty, duplicate, missing, conflicting, very large, out of order.
- **Errors** - fail loud or degrade? Are partial results acceptable?
- **Persistence** - does state survive a restart? Is that even in scope?
- **Concurrency** - one caller or many? Does ordering matter?
- **Actors** - who uses this, how many, do they differ in permission?
- **External dependencies** - is any outside specification, API, protocol, or dataset involved? (If yes, the Researcher reads it from the actual source. If no, log the null result with reasoning - `AGENTS.md` section 5.)
- **Attack surface** - untrusted input, credentials, secrets, data at rest, injection paths, unbounded reads. (If none, that is a Security null result and it is logged with its reasoning, not skipped silently.)
- **Quality bar** - prototype, production artifact, or demonstration of approach?
- **Deliverable** - what file, what format, what named entry point.

---

## 3. Deliverable contract

Copy the submission requirements **verbatim.** Do not paraphrase - paraphrase is where compliance quietly dies.

> 

| Requirement | Stated? | How I will satisfy it |
|---|---|---|
| Deliverable format | | |
| Named entry point / how it is run | | |
| Documentation expected | | |
| Anything explicitly forbidden | | |
| Anything explicitly out of scope | | |
| Submission channel | | |

**Format non-compliance is the cheapest possible way to lose points. Honour it exactly as written.**

---

## 4. What is actually being assessed

The stated task is a vehicle. Name what sits behind it.

- **The capability this assignment tests:**
- **Where the ambiguity is deliberately concentrated:**
- **What a strong candidate does there that a weak one does not:**
- **What would fail this submission even if the artifact works:**

**One-sentence read** - carries into `G-001` in the process log and into the README:

> I believe this assessment is testing ______________, and the deliberate ambiguity is concentrated in ______________.

---

## 5. MoSCoW - set now, enforced at freeze

Must / Should / Could / Won't. Decided here, while thinking is cheap and no work is sunk.

| Tier | Items |
|---|---|
| **Must** | *(Always includes: walking skeleton runs · stated deliverable in the stated format · `PROCESS-LOG.md` · `AMBIGUITY-REGISTER.md` · README)* |
| **Should** | |
| **Could** | |
| **Won't (this assignment)** | *(Write these down. A named non-goal is evidence of scope judgment, and it goes in the README.)* |

Log the tiering as a `D-nnn` `DECISION` entry with its reasoning.

---

## 6. Walking skeleton definition

The thinnest end-to-end slice that touches every layer and actually runs.

- **The one case it handles:**
- **Layers it must touch:**
- **Explicitly NOT in the skeleton:**
- **"Green" means:** *(the observable result that proves it works - an output you can point at, not a feeling)*

If "green" cannot be stated as something observable, the skeleton is not yet defined.

---

## 7. Clarifications

Only if the assignment permits asking. Ask few, ask high-leverage - only the ones where different answers produce materially different work.

**Send now. Never block on an answer** (`AGENTS.md` section 4, step 4). Record the assumption you proceed on regardless.

| # | Question asked | Assumption I proceed on regardless | Register ID |
|---|---|---|---|
| Q-001 | | | A-___ |

---

## 8. Substrate check

`AGENTS.md` section 8: the operating model must not depend on any distribution-specific feature.

- [ ] Confirmed the contract is loaded in this session (or pasted in directly as the fallback).
- [ ] Confirmed how an independent QA context will be obtained.
- [ ] Noted any tooling mechanism that is unfamiliar, so a fallback is chosen in advance rather than debugged mid-window.

**One attempt to understand a misbehaving mechanism is reasonable. A second is a trap.** Fall back, log the fallback with what failed, and continue.

---

## 9. Exit check

- [ ] Every sentence of the assignment sorted into exactly one column
- [ ] Every UNSPECIFIED row carried into `AMBIGUITY-REGISTER.md` with an ID
- [ ] Every weight-bearing or low-confidence IMPLIED row carried into the register
- [ ] Deliverable contract copied verbatim
- [ ] One-sentence read of what is being assessed, written
- [ ] MoSCoW set, including Won't, and logged as a decision
- [ ] Walking skeleton defined, with an observable "green"
- [ ] Clarifications sent if permitted, with assumptions recorded
- [ ] Researcher and Security null results logged with reasoning, if they apply
- [ ] Substrate fallbacks chosen in advance

→ **Write the `G-001` GRAA checkpoint, then proceed to P1.**
