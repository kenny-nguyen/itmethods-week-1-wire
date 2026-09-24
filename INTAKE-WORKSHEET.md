# Intake Worksheet

First structured read of the assignment, filled from `templates/intake-worksheet.md` before any code was written. It feeds the opening GRAA (Goal, Reality, Analysis, Action) checkpoint `G-001` in `PROCESS-LOG.md` and the rows of `AMBIGUITY-REGISTER.md`.

The assignment packet is private and is not copied here. Only the short lines a decision depends on are quoted.

## 1. Input QA on the assignment itself

- [x] Read in full from the source files: the assignment brief, CEO (chief executive officer) notes, ICP (ideal customer profile) sketch, the Reign constraint (rule R-17), the Campaign Manager stub, and the window file. Six files, all readable.
- [x] Every referenced input is present. The brief names four packet items; all four are there.
- [x] Submission channel and format confirmed: a public GitHub repository containing four things (artifact, one-page process log, one thing learned, what we would not ship).

| # | What is referenced | Where it should be | Status | Register ID |
|---|---|---|---|---|
| 1 | Real HubSpot, Clay, ZoomInfo access | Operator accounts | Missing (no access in the window) | A-012 |
| 2 | The "Canadian bank on Forge" as a named account | ICP sketch | Not named, on purpose | A-013 |
| 3 | FDA PCCP (Predetermined Change Control Plan) guidance page | fda.gov | Two guessed URLs returned 404; not yet located | A-014 |

## 2. The assignment, sorted

### STATED (short quotes)

| # | Quote | What it obliges |
|---|---|---|
| S1 | "pick one, go deep, do not spray" | One artifact. Chosen: option 3, a small agent that turns a regulatory trigger into a short account brief with sources. |
| S2 | "must write an audit record before the action is considered complete" (R-17) | Audit write is a precondition of completion, not a log line afterwards. |
| S3 | "If the record cannot be written, the action does not happen." (R-17) | Fail closed. |
| S4 | "`approval` must name a human if `channel` can send" (Campaign Manager) | Playbook validation rejects a sending channel without a named approver. |
| S5 | "Encode a playbook JSON for the first Reign motion. Leave comments for guesses." | A JSONC (JSON with comments) playbook with every guess marked. |
| S6 | "You must touch at least two tool classes" | HubSpot, Clay and ZoomInfo seams plus a Claude model call. |
| S7 | "You must use an agent to do part of the work, and you must show the scaffolding" | Prompts, adapters, gates and tests are in the repository. |
| S8 | "Do not include mid-market SaaS." / "Someone put 'AI startups' on a list. Remove them." (CEO notes) | Deterministic ICP exclusions. |
| S9 | "Everything that sends needs a named human." (CEO notes) | Approval request with a named approver; nothing auto-sends. |

### IMPLIED

| # | Inference | Source | Confidence | Weight-bearing? | Register ID |
|---|---|---|---|---|---|
| I1 | "Precision, no spray" means a small, gated volume per run and a kill switch the CRO (chief revenue officer) controls. | CEO notes, Campaign Manager `kill_criteria` | High | Yes | A-010 |
| I2 | Risk and engineering buyers at the bank get one brief routed to both lanes by title, never asked to pick. | CEO notes "Route them without asking" | High | Yes | A-011 |
| I3 | Bank outbound is blocked unless a briefing is booked or a regulatory trigger fired. | CEO notes | High | Yes | A-009 |
| I4 | The product must not invent facts about real companies; fixtures use fictional accounts. | "no-slop", bank/hospital/defense embarrassment test | High | Yes | A-013 |

### UNSPECIFIED

| # | What is missing | What it blocks | Register ID |
|---|---|---|---|
| U1 | Which trigger and buyer to go deep on | The deep brief and the real playbook | A-002 |
| U2 | Playbook versioning | Playbook schema | A-016 |
| U3 | One trigger or many per playbook | Playbook schema | A-017 |
| U4 | What "briefing" means as a channel | Channel semantics, approval rule | A-018 |
| U5 | Which accounts count as FS (financial services) | R-17 scope | A-006 |
| U6 | Where audit records live | R-17 module | A-008 |
| U7 | Which model provider, and behaviour with no key | Brief generation | A-015 |

## 3. Deliverable contract

Four things in a public GitHub repository: a working artifact, a one-page process log with two or three actual prompts or configs, one thing learned, and what we would not ship. Forbidden: a deck, a long strategy memo, a private repo or PDF as the submission. Knockouts include "high-volume slop outbound" and "ignored the Reign constraint".

## 4. What is actually being assessed

> I believe this assessment is testing whether I can turn a messy, self-contradicting brief into a governed agent that actually runs, and the deliberate ambiguity is concentrated in the ICP, the Campaign Manager schema and the reach of rule R-17.

## 5. MoSCoW (Must, Should, Could, Won't)

| Tier | Items |
|---|---|
| Must | Runnable pipeline end to end on fixtures; R-17 fail-closed audit; named-approver gate with no send path; ICP exclusions; process log; ambiguity register; README; tests and CI |
| Should | Real model call behind a provider switch; playbook schema with marked guesses; structured error log |
| Could | Live HubSpot, Clay or ZoomInfo connectors; MCP (Model Context Protocol) server wrapper |
| Won't | Any real send; a blog; a sequence to hospitals this month; scraping; a UI |

## 6. Walking skeleton

- **One case:** one fictional FS account, one trigger, one brief.
- **Layers:** input adapters, ICP filter, applicability preflight, brief generator, audit, approval request.
- **Not in it:** live connectors, a real send.
- **Green means:** `python -m wire run` writes a brief, an approval request marked pending, and audit records for every action, and exits 0; the test suite passes.

## 8. Substrate check

- Contract loaded through `CLAUDE.md` importing `AGENTS.md`.
- Independent QA runs as a separate reviewer context with a bounded brief.
