# Week-1 Wire - regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST.

The chosen artifact is option 3 of the assignment: a small agent that turns a regulatory trigger into a short account brief with sources, built so that every touch on a financial-services (FS) account leaves an audit record before it counts, and nothing sends without a named human approver.

The assignment packet itself is private and is not in this repository. Where a decision depends on a line of it, that short line is quoted in `PROCESS-LOG.md` or `AMBIGUITY-REGISTER.md`.

## About the working contract (the first commit)

The first commit in this history (`Install working contract and kit`) contains no product code. It is an operating contract for the AI agents that do the work in this repository, committed before the timer-driven work began so that the rules were fixed before any decision was made. A reviewer can check any later commit against rules that could not have been written to fit it. The supporting kit files were later moved under `contract/` (process log D-004) so the repository root holds what a reviewer reads first; `AGENTS.md` stays at the root because agents load it from there.

What the contract sets out:

- **Two loops.** GRAA (Goal, Reality, Analysis, Action) is the checkpoint loop that asks whether the work is heading the right way. IPOF (Input, Processing, Output, Feedback) is the loop every unit of work runs through, and the code in this repository is structured the same way.
- **QA (quality assurance) at every IPOF stage**, not only at the end, with independent adversarial review switched on for this assignment and every verdict logged.
- **An ambiguity rule.** No silent guesses: every unclear requirement gets a row in `AMBIGUITY-REGISTER.md` with the reading chosen, the reason, and the fact that would flip it.
- **An append-only process log** (`PROCESS-LOG.md`) written as decisions are made, not reconstructed afterwards.
- **A fixed role roster** (PM, QA, Researcher, Security, Technical Writer, Copywriter) and a git standard: branch per unit, conventional commits, no secrets, no agent co-author trailers.

| Kit file | What it is |
|---|---|
| `AGENTS.md` | The contract. Every agent reads it first. `CLAUDE.md` only imports it. |
| `contract/RUNBOOK.md` | The operating sequence for the window (intake, ambiguity, skeleton, build, freeze, submission). |
| `contract/QA-AT-EVERY-IPOF-STAGE.md`, `contract/QA-AGENT-SOP.md` | How QA runs at each stage and how an independent reviewer works. |
| `contract/templates/` | Starting shapes for the intake worksheet, process log, ambiguity register and QA verdicts. |
| `.claude/agents/` | The role roster as dispatchable agent definitions. |

## How to use

This section is updated as usable pieces land.

Requires Python 3.11 or later. Standard library only; nothing to install.

- Run the tests: `python -m unittest discover -s tests -t . -v`
- The R-17 audit trail (`agent/governance/audit.py`): every create, update, enrich, score or message action goes through `AuditTrail.perform(...)`, which writes the audit record first and only then completes the action. If the record is invalid or cannot be written, the action does not happen and `AuditBlocked` is raised.
- Input adapters (`agent/input/`): interfaces in `base.py`, local stand-ins for HubSpot, ZoomInfo, Clay and a regulator feed in `local.py`, reading `fixtures/`. To connect a real tool, write one class against the matching interface.
- The ICP (ideal customer profile) filter (`agent/processing/icp.py`) reads `icp/icp.json`. Each field the packet did not give names the register row that proposes it. AI startups and mid-market SaaS are excluded by segment and by naming-variant patterns; the variants tested are listed in `tests/test_icp.py`.
- The error log (`agent/governance/error_log.py`) is a separate JSON Lines file for anything that goes wrong in any stage.

## Repo map

| Path | Purpose |
|---|---|
| `README.md` | This file. |
| `AGENTS.md`, `CLAUDE.md`, `contract/`, `.claude/agents/` | The working contract and kit (see above). |
| `PROCESS-LOG.md` | Append-only decision log, written during the window. |
| `AMBIGUITY-REGISTER.md` | Every ambiguity, the reading taken, and what would flip it. |
| `INTAKE-WORKSHEET.md` | First structured read of the assignment. |
| `agent/governance/` | R-17 audit trail and the error log, used by every stage. |
| `agent/input/` | INPUT stage: adapter interfaces and local fixture adapters. |
| `agent/processing/` | PROCESSING stage: ICP filter, applicability preflight, brief generation, output checks. |
| `icp/` | The living ICP, with the source or register row of every field. |
| `fixtures/` | Fictional HubSpot, ZoomInfo and Clay records, plus the real regulator publications with fetched URLs. |
| `tests/` | Unit tests, one file per stage. |
| `.github/workflows/ci.yml` | CI (continuous integration): runs the tests on every push. |
| `docs/research/` | Sourced facts the agent is allowed to use (product claims, regulator pages). |
