# Week-1 Wire - regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST.

The chosen artifact is option 3 of the assignment: a small agent that turns a regulatory trigger into a short account brief with sources, built so that every touch on a financial-services (FS) account leaves an audit record before it counts, and nothing sends without a named human approver.

The assignment packet itself is private and is not in this repository. Where a decision depends on a line of it, that short line is quoted in `PROCESS-LOG.md` or `AMBIGUITY-REGISTER.md`.

## About the working contract (the first commit)

The first commit in this history (`Install working contract and kit`) contains no product code. It is an operating contract for the AI agents that do the work in this repository, committed before the timer-driven work began so that the rules were fixed before any decision was made. A reviewer can check any later commit against rules that could not have been written to fit it.

What the contract sets out:

- **Two loops.** GRAA (Goal, Reality, Analysis, Action) is the checkpoint loop that asks whether the work is heading the right way. IPOF (Input, Processing, Output, Feedback) is the loop every unit of work runs through, and the code in this repository is structured the same way.
- **QA (quality assurance) at every IPOF stage**, not only at the end, with independent adversarial review switched on for this assignment and every verdict logged.
- **An ambiguity rule.** No silent guesses: every unclear requirement gets a row in `AMBIGUITY-REGISTER.md` with the reading chosen, the reason, and the fact that would flip it.
- **An append-only process log** (`PROCESS-LOG.md`) written as decisions are made, not reconstructed afterwards.
- **A fixed role roster** (PM, QA, Researcher, Security, Technical Writer, Copywriter) and a git standard: branch per unit, conventional commits, no secrets, no agent co-author trailers.

| Kit file | What it is |
|---|---|
| `AGENTS.md` | The contract. Every agent reads it first. `CLAUDE.md` only imports it. |
| `RUNBOOK.md` | The operating sequence for the window (intake, ambiguity, skeleton, build, freeze, submission). |
| `QA-AT-EVERY-IPOF-STAGE.md`, `QA-AGENT-SOP.md` | How QA runs at each stage and how an independent reviewer works. |
| `templates/` | Starting shapes for the intake worksheet, process log, ambiguity register and QA verdicts. |
| `.claude/agents/` | The role roster as dispatchable agent definitions. |

## How to use

This section is updated as usable pieces land.

- Nothing is runnable yet. Read `PROCESS-LOG.md` for what has been decided so far.

## Repo map

| Path | Purpose |
|---|---|
| `README.md` | This file. |
| `AGENTS.md`, `RUNBOOK.md`, `QA-*.md`, `templates/`, `.claude/agents/` | The working contract and kit (see above). |
