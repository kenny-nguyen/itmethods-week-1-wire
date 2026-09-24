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

This section is updated as usable pieces land. Requires Python 3.11 or later; standard library only, nothing to install. Run everything from the repository root.

### 1. Run the playbook

```
python -m agent.run_playbook
```

This runs `playbooks/reign-first-motion.jsonc` against the fixtures and writes to `out/` (git-ignored). Without an API key it drafts with a deterministic template. With `ANTHROPIC_API_KEY` set it drafts with Claude (`WIRE_MODEL` picks the model, default `claude-opus-5`; `WIRE_PROVIDER=template` forces the template). Either way every draft goes through the same output gate.

What comes out:

| Path | What it is |
|---|---|
| `out/runs/<run>/briefs/*.md` | Briefs that passed every gate. |
| `out/runs/<run>/approvals/*.json` | One approval request per brief, `status: pending`, `send: false`. |
| `out/runs/<run>/summary.json` | Every account's outcome and reason, every play's status, the run metrics. |
| `out/audit.jsonl` | The R-17 audit trail: one record per enrich, score, create, hold, approve, reject or block. |
| `out/errors.jsonl` | The error log, kept separate from the audit trail. |
| `out/state/kill/<playbook>.json` | Present only while the kill switch is engaged. |

On the fixtures, with the playbook as committed: the US bank gets a brief pending approval; the Canadian bank is held because a US Federal Reserve-regulated entity is not established (set `unconfirmed_applicability` to `brief_with_caveat` in the playbook to brief it with "applicability requires confirmation" and the OSFI context instead; register rows A-025 and A-028); the AI startups, the mid-market SaaS firm, the hospital, the small credit union and the semiconductor firm without export-control exposure are excluded; the biopharma and defense accounts are not enriched because their plays are not implemented.

### 2. Approve or reject a brief

```
python -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
  --approver "Kenny Nguyen" --approve --reason "Sources and routing checked."
```

Only a named approver listed in the playbook can decide. The decision is written to the audit trail before the request changes. Approval marks the brief ready to send; no sender is wired (register row A-035), so nothing leaves the machine.

### 3. Stop the motion

```
python -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Drafts read generic."
python -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Reviewed." --clear
```

While engaged, runs are refused and approvals are refused. The playbook's kill criteria engage it automatically: any R-17 audit failure, more than one draft in five failing the gate, or more than half of decided briefs rejected.

### 4. Check it

```
python -m unittest discover -s tests -t . -v
python -m evals.run_evals
```

### How the pieces fit

| Stage | Code | Gate |
|---|---|---|
| INPUT | `agent/input/`: adapter interfaces (`base.py`) and local stand-ins for HubSpot, ZoomInfo, Clay and a regulator feed (`local.py`); the playbook loader (`playbook.py`) | The playbook must validate, the motion must be active, the kill switch must be off. |
| PROCESSING | `agent/processing/`: ICP filter (`icp.py`, rules in `icp/icp.json`), applicability preflight (`preflight.py`), title routing (`routing.py`), brief drafting (`brief.py`, prompt in `prompts/brief_system.md`) | Excluded companies are never enriched. The preflight holds, skips or blocks before drafting. The output gate (`checks.py`) rejects any draft with an unknown source, an invented URL, an unapproved product claim, a compliance or certification claim, a duration, or a CMMC, FedRAMP, CUI or ITAR mention. |
| OUTPUT | `agent/output/writer.py` | Each brief and approval request is written only after its R-17 audit record (`agent/governance/audit.py`). |
| FEEDBACK | `agent/feedback/`: decisions, kill criteria, kill switch | Named approver only; kill switch blocks approvals; kill criteria checked after every run and decision. |

To connect a real tool, write one class against the matching interface in `agent/input/base.py`. The rest of the pipeline does not change.

## Repo map

| Path | Purpose |
|---|---|
| `README.md` | This file. |
| `AGENTS.md`, `CLAUDE.md`, `contract/`, `.claude/agents/` | The working contract and kit (see above). |
| `PROCESS-LOG.md` | Append-only decision log, written during the window. |
| `AMBIGUITY-REGISTER.md` | Every ambiguity, the reading taken, and what would flip it. |
| `INTAKE-WORKSHEET.md` | First structured read of the assignment. |
| `agent/run_playbook.py` | The pipeline entry point. |
| `agent/output/`, `agent/feedback/` | OUTPUT and FEEDBACK stages: artifacts, approval decisions, kill criteria, kill switch. |
| `agent/governance/` | R-17 audit trail and the error log, used by every stage. |
| `agent/input/` | INPUT stage: adapter interfaces and local fixture adapters. |
| `agent/processing/` | PROCESSING stage: ICP filter, applicability preflight, brief generation, output checks. |
| `prompts/` | The system prompt the model drafts briefs with. |
| `evals/` | Deterministic eval cases for the brief output gate (`python -m evals.run_evals`). |
| `playbooks/` | The Campaign Manager playbook for the first Reign motion, and `SCHEMA.md` explaining every field. |
| `icp/` | The living ICP, with the source or register row of every field. |
| `fixtures/` | Fictional HubSpot, ZoomInfo and Clay records, plus the real regulator publications with fetched URLs. |
| `tests/` | Unit tests, one file per stage. |
| `.github/workflows/ci.yml` | CI (continuous integration): runs the tests on every push. |
| `docs/research/` | Sourced facts the agent is allowed to use (product claims, regulator pages). |
