# Week-1 Wire: regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST (Korea Standard Time).

A Claude skill drives an MCP (Model Context Protocol) server to turn a regulatory trigger, SR 26-2 (the Federal Reserve's revised model risk guidance), into a short brief on a specific bank, with a source on every line. The agent decides what to write; the server's tools enforce R-17 (an audit record before any touch on a financial-services account), the ICP (ideal customer profile) exclusions, the do-not-route list and the claim limits. Nothing is sent: each brief goes to the bank's named iTmethods account owner, who decides whether to share it.

The assignment packet is private and not in this repository; short lines are quoted where a decision depends on them.

## The four deliverables

1. **The artifact:** the [skill](skills/regulatory-trigger-brief/SKILL.md), the [MCP server](agent/mcp_server.py) over its [governed tools](agent/tools.py), and the [evals](evals/). Sample output: [`examples/README.md`](examples/README.md).
2. **The process log:** [`PROCESS-LOG.md`](PROCESS-LOG.md), one page.
3. **[One thing I did not know](#one-thing-i-did-not-know)**, below.
4. **[What I would not ship](#what-i-would-not-ship)**, below.

Also asked for in the packet: the Campaign Manager playbook (`playbooks/`, guesses marked) and the living ICP (`icp/icp.json`, invented fields marked).

## One thing I did not know

How rules from three jurisdictions reach a Canadian bank. As I read it, SR 26-2 reaches it only through US operations the Federal Reserve regulates; guidelines E-23 and B-13 from OSFI (Canada's Office of the Superintendent of Financial Institutions) certainly apply; DORA (the EU's Digital Operational Resilience Act) applies only if an EU entity is one of its listed financial-entity types. That became the brief's structure: what changed, what is certain, what depends on structure (marked "Confirm"). My first draft still overstated the SR 26-2 and DORA lines. The independent fact-check caught it, and those lines now keep the regulators' own scope words. [Full story](docs/one-thing-i-did-not-know.md).

## What I would not ship

| Buyer | Example | Why |
|---|---|---|
| Bank | A brief saying SR 26-2 "applies" to the bank's US entity, or DORA to "an EU financial entity". My first draft did this. | Audit and risk readers know regulatory scope. One overstated line and nothing else in the brief is trusted. Scope questions go under "Confirm". |
| Hospital | Any touch this month. | The packet's Slack notes say "do not spray hospitals this month", and "high-volume slop outbound" is a knockout. Hospitals go on a watch list: noticed, never contacted. |
| Defense supplier | Any hint of CMMC (Cybersecurity Maturity Model Certification), FedRAMP (Federal Risk and Authorization Management Program) or CUI (controlled unclassified information) capability. | iTmethods' public-sector page says it is not FedRAMP authorized or CMMC certified and does not handle CUI. The claim would be false; the gate refuses those terms. |

## How to run

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt     # mcp==2.2.0, the one dependency
```

**Run the agent.** Open Claude Code in the repository root. It reads [`.mcp.json`](.mcp.json), starts the `week1-wire` server and finds the skill under `.claude/skills/`. Then ask:

> Use the regulatory-trigger-brief skill to brief account hs-1001 on SR 26-2.

The brief, the approval request, the R-17 audit trail (`audit.jsonl`), the error log and a one-page `review.html` land in `out/` (or `WIRE_OUT_DIR`).

**Score the run.** `python3 -m evals.score_run --out out`

**The account owner decides.** Only the account's HubSpot owner can approve. Approved means ready to send; nothing is wired to send.

```
python3 -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
  --approver "Kenny Nguyen" --approve --reason "Sources and routing checked."
```

**Offline test mode and CI (continuous integration).** With no model key, a deterministic template drafts the briefs. For tests only; it is not the agent.

```
python3 -m agent.run_playbook
python3 -m unittest discover -s tests -t . -v
python3 -m evals.run_evals
```

The direct model-API (application programming interface) path was not run (no key). The live agent run in Claude Code is in `examples/` (see [`examples/README.md`](examples/README.md), transcript included). Production setup, kill switch and recovery: [`docs/production.md`](docs/production.md).

## How it was built

I made the calls; AI agents did most of the building under the working contract below. Claude Code (Claude Opus 5.5) built the skill, server and evals. Codex, OpenAI's coding agent and so a different model, ran the independent fact-check and adversarial review. A research agent on another model checked the primary sources blind.

## How I decided

- [Cut, sequenced, refused](docs/cut-sequenced-refused.md): why only the bank trigger is built.
- [What I went looking for vs what I assumed](docs/looked-vs-assumed.md).
- [Reconciling the CEO notes](docs/ceo-notes-reconciled.md).
- [Day-one wiring](docs/day-one-wiring.md): HubSpot, Clay and ZoomInfo are fixtures behind interfaces.
- [Stuck, and the next experiment](docs/stuck.md).
- [`AMBIGUITY-REGISTER.md`](AMBIGUITY-REGISTER.md): every ambiguity, the reading taken, what would flip it.

## About the working contract

The kit is part of the agentic system I use for my own work: the method layer of my DBK Agentic OS, reapplied here as I would on any task. It contains nothing specific to this assignment. I committed it first (`Install working contract and kit`) so its rules were in place before any work began, and I used it throughout: goal and reality checkpoints, QA (quality assurance) at every stage, the ambiguity register and the writer handoff. The contract is [`AGENTS.md`](AGENTS.md); the rest is in [`contract/`](contract/) and [`.claude/agents/`](.claude/agents/). The repo runs without the rest of that system; the tools that ran the method are named under [How it was built](#how-it-was-built).

## Repo map

| Path | Purpose |
|---|---|
| `README.md`, `PROCESS-LOG.md` | This file; the process log. |
| `docs/` | Write-ups, intake worksheet, production guide, `research/` (sourced facts), `qa/` (independent QA reports). |
| `AMBIGUITY-REGISTER.md` | Every judgment call, its reason and what would flip it. |
| `AGENTS.md`, `CLAUDE.md`, `contract/`, `.claude/agents/` | The working contract and kit. |
| `skills/regulatory-trigger-brief/`, `.claude/skills/` | The Claude skill, and the link Claude Code finds it through. |
| `agent/`, `.mcp.json`, `requirements.txt` | The MCP server (`mcp_server.py`, `tools.py`), the IPOF (Input, Processing, Output, Feedback) stages, R-17 audit trail, batch runner. |
| `prompts/` | Direct model-API system prompt (not exercised live). |
| `evals/` | Agent-run cases and scorer; output-gate cases. |
| `playbooks/`, `icp/` | Campaign Manager playbooks and schema; the living ICP. |
| `fixtures/` | Fictional CRM (customer relationship management) and enrichment records; records of real regulator publications. |
| `tests/`, `.github/workflows/ci.yml`, `.gitignore` | Unit tests, CI, and the paths git ignores (`out/`, `.venv/`, `.env`). |
| `examples/` | Labelled sample runs, indexed in `examples/README.md`. |
