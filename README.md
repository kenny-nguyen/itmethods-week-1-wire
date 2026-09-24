# Week-1 Wire - regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST.

The chosen artifact is option 3 of the assignment: a small agent that turns a regulatory trigger into a short account brief with sources. It's built so every touch on a financial-services (FS) account leaves an audit record before it counts, and nothing sends without a named human approver.

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

This section is updated as usable pieces land. Requires Python 3.11 or later, run as `python3`; standard library only, nothing to install. Run everything from the repository root.

To see the output without running anything, read `examples/brief-hs-1001.md` (the Canadian bank) and `examples/README.md`.

### 1. Run the motion

```
python3 -m agent.run_playbook
```

This runs the first Reign motion (`playbooks/motions/reign-first-motion.jsonc`) against the fixtures and writes to `out/` (git-ignored). The motion filters the account list once against the ICP (ideal customer profile), then runs each playbook whose trigger is implemented. Only the bank playbook (`playbooks/bank-sr26-2.jsonc`, SR 26-2) is implemented; the biopharma and defense playbooks are reported as "trigger not implemented yet" with the reason.

Without an API key, the brief is drafted from a deterministic template. With `ANTHROPIC_API_KEY` set, it is drafted by Claude (`WIRE_MODEL` picks the model, default `claude-opus-5`; `WIRE_PROVIDER=template` forces the template). Either way every draft passes the same output gate. A failed model call fails that account loudly and names the recovery options; it never falls back silently.

What comes out:

| Path | What it is |
|---|---|
| `out/runs/<run>/briefs/*.md` | Briefs that passed every gate. |
| `out/runs/<run>/approvals/*.json` | One request per brief, routed to the named iTmethods account owner: `status: pending`, `send: false`. |
| `out/runs/<run>/summary.json` | Every account's outcome and reason, the watch list, each playbook's status and metrics. |
| `out/audit.jsonl` | The R-17 audit trail: one record per enrich, score, route, hold, create, approve, reject, update, block or unblock. |
| `out/errors.jsonl` | The error log, kept separate from the audit trail. |
| `out/state/kill/<playbook>.json` | Present only while that playbook's kill switch is engaged. |

On the fixtures: both banks get the structured SR 26-2 brief (what changed, what is certain for the account, what depends on its structure with every line marked "Confirm", and a suggested next step), routed to the account owner. The Canadian bank's brief brings in OSFI E-23 and B-13 and says "SR 26-2 applicability requires confirmation". The AI startups, the mid-market SaaS firm and the small credit union are dropped with their reasons in the audit log. The hospital is on the watch list: noticed and logged, never contacted. The bank with unknown headcount is held for a human. The biopharma, defense and semiconductor accounts are not enriched, because no playbook for them is live.

### 2. The account owner decides

```
python3 -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
  --approver "Kenny Nguyen" --approve --reason "Sources and routing checked."
```

The approver must be listed in the playbook and must be the account's owner in HubSpot; both are read from trusted files, never from the request. The decision is written to the audit trail before the request changes. Approval means ready to send; nothing is wired to send, so nothing leaves the machine.

Limit of the demo: the approver is a typed name. In production it must come from an authenticated identity.

### 3. Report quality problems or stop a playbook

```
python3 -m agent.feedback.report --request out/runs/<run>/approvals/<account>.json \
  --by "Kenny Nguyen" --kind wrong_account --detail "Brief names the wrong parent company."
python3 -m agent.feedback.kill --playbook-id bank-sr26-2 --by "Kenny Nguyen" --reason "Drafts read generic."
python3 -m agent.feedback.kill --playbook-id bank-sr26-2 --by "Kenny Nguyen" --reason "Reviewed the drafts." --clear
```

Only the playbook owner or a listed approver can report, engage or clear, and every one of those actions is audited. While a kill switch is engaged, that playbook is skipped and its approvals are refused. The kill criteria are quality-based (operator decision A-037): any R-17 audit failure, more than one draft in five failing the gate, more than half of decided briefs rejected, one complaint, or one wrong-account report.

Running it for real (configuration, adapters, scheduling, recovery, and what is not production-ready yet): [`docs/production.md`](docs/production.md).

### 4. Check it

```
python3 -m unittest discover -s tests -t . -v
python3 -m evals.run_evals
```

### How the pieces fit

| Stage | Code | Gate |
|---|---|---|
| INPUT | `agent/input/`: adapter interfaces (`base.py`) and local stand-ins for HubSpot, ZoomInfo, Clay and a regulator feed (`local.py`); the playbook and motion loader (`playbook.py`) | The motion and every playbook must validate; a paused playbook or one with its kill switch engaged is skipped. |
| PROCESSING | `agent/processing/`: ICP filter (`icp.py`, rules in `icp/icp.json`), applicability preflight (`preflight.py`), title routing (`routing.py`), brief drafting (`brief.py`, prompt in `prompts/brief_system.md`) | Dropped and watch-list companies are never enriched or contacted. The preflight holds, skips or blocks before drafting. The output gate (`checks.py`) rejects any draft with an unknown source, an invented URL, an unapproved product claim, a compliance or certification claim, a duration, or a CMMC, FedRAMP, CUI or ITAR mention. |
| OUTPUT | `agent/output/writer.py` | Each brief and approval request is written only after its R-17 audit record (`agent/governance/audit.py`). |
| FEEDBACK | `agent/feedback/`: decisions, reports, kill criteria, kill switch | Named account owner only; kill switch blocks approvals; quality kill criteria checked after every run, decision and report. |

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
| `evals/` | Deterministic eval cases for the brief output gate (`python3 -m evals.run_evals`). |
| `playbooks/` | The three Campaign Manager playbooks (one audience, trigger and channel each), the motion file that references them, and `SCHEMA.md` explaining every field. |
| `icp/` | The living ICP, with the source or register row of every field. |
| `fixtures/` | Fictional HubSpot, ZoomInfo and Clay records, plus the real regulator publications with fetched URLs. |
| `tests/` | Unit tests, one file per stage. |
| `.github/workflows/ci.yml` | CI (continuous integration): runs the tests on every push. |
| `examples/` | Real output of one run: both bank briefs, their approval requests, the audit records for one bank, the run summary. |
| `docs/production.md` | Production guide: configuration, end-to-end run, approval and kill switch, wiring each adapter, scheduling, recovery, known gaps. |
| `agent/config.py` | Deployment configuration read from the environment. |
| `docs/research/` | Sourced facts the agent is allowed to use (product claims, regulator pages). |
