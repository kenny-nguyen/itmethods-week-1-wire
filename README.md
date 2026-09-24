# Week-1 Wire: regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST (Korea Standard Time).

A Claude skill drives an MCP (Model Context Protocol) server to turn a regulatory trigger, SR 26-2 (the Federal Reserve's revised model risk guidance), into a short brief on a specific bank, with a source on every line. The agent decides what to write; the server's tools enforce R-17 (an audit record before any touch on a financial-services account), the ICP (ideal customer profile) exclusions, the do-not-route list and the claim limits. Nothing is sent: each brief goes to the bank's named iTmethods account owner, who decides whether to share it.

The assignment packet is private and not in this repository; short lines are quoted where a decision depends on them.

## The four deliverables

1. **The artifact:** the [skill](skills/regulatory-trigger-brief/SKILL.md), the [MCP server](agent/mcp_server.py) over its [governed tools](agent/tools.py), and the [evals](evals/). A labelled example run is in [`examples/`](examples/).
2. **The process log:** [`PROCESS-LOG.md`](PROCESS-LOG.md), one page.
3. **[One thing I did not know](#one-thing-i-did-not-know)**, below.
4. **[What I would not ship](#what-i-would-not-ship)**, below.

## One thing I did not know

How rules from three jurisdictions reach a Canadian bank. As I read it, SR 26-2 reaches it only through US operations the Federal Reserve regulates; OSFI E-23 and B-13 certainly apply; DORA applies only if an EU entity is one of its listed financial-entity types. That became the brief's structure: what changed, what is certain, what depends on structure (marked "Confirm"). My first draft still overstated the SR 26-2 and DORA lines; the independent fact-check caught it. [Full story](docs/one-thing-i-did-not-know.md).

## What I would not ship

| Buyer | Example | Why |
|---|---|---|
| Bank | A brief saying SR 26-2 "applies" to the bank's US entity, or DORA to "an EU financial entity". My first draft did this. | Audit and risk readers know regulatory scope. One overstated line and nothing else in the brief is trusted. Scope questions go under "Confirm". |
| Hospital | Any touch this month. | The packet's Slack notes say "do not spray hospitals this month", and spray is a knockout. Hospitals go on a watch list: noticed, never contacted. |
| Defense supplier | Any hint of CMMC, FedRAMP or CUI capability. | iTmethods' public-sector page says it is not FedRAMP authorized or CMMC certified and does not handle CUI. The claim would be false; the gate refuses those terms. |

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

No live agent or direct model-API run happened in the build environment. Production setup, kill switch and recovery: [`docs/production.md`](docs/production.md).

## How it was built

I made the calls; AI agents did most of the building under the working contract below. Claude Code (Claude Opus 5.5) built the skill, server and evals. Codex, a different model, ran the independent fact-check and adversarial review. A research agent on another model checked the primary sources blind.

## How I decided

- [Cut, sequenced, refused](docs/cut-sequenced-refused.md): why only the bank trigger is built.
- [What I went looking for vs what I assumed](docs/looked-vs-assumed.md).
- [Reconciling the CEO notes](docs/ceo-notes-reconciled.md).
- [Day-one wiring](docs/day-one-wiring.md): HubSpot, Clay and ZoomInfo are fixtures behind interfaces.
- [Stuck, and the next experiment](docs/stuck.md).
- [`AMBIGUITY-REGISTER.md`](AMBIGUITY-REGISTER.md): every ambiguity, the reading taken, what would flip it.

## About the working contract

The first commit (`Install working contract and kit`) has no product code. It is the contract I set for the agents, committed first so every later commit can be checked against rules written before it. [`AGENTS.md`](AGENTS.md) sets two loops (GRAA: Goal, Reality, Analysis, Action; IPOF: Input, Processing, Output, Feedback), QA (quality assurance) at every stage with independent adversarial review, and a no-silent-guess ambiguity rule. The rest of the kit is in [`contract/`](contract/) and [`.claude/agents/`](.claude/agents/).

## Repo map

| Path | Purpose |
|---|---|
| `README.md`, `PROCESS-LOG.md` | This file; the process log. |
| `docs/` | Write-ups, intake worksheet, production guide, `research/` (sourced facts), `qa/` (independent QA reports). |
| `AMBIGUITY-REGISTER.md` | Every judgment call, its reason and what would flip it. |
| `AGENTS.md`, `CLAUDE.md`, `contract/`, `.claude/agents/` | The working contract and kit. |
| `skills/regulatory-trigger-brief/` | The Claude skill. |
| `agent/`, `.mcp.json`, `requirements.txt` | The MCP server (`mcp_server.py`, `tools.py`), IPOF stages, R-17 audit trail, batch runner. |
| `prompts/` | Direct model-API system prompt (not exercised live). |
| `evals/` | Agent-run cases and scorer; output-gate cases. |
| `playbooks/`, `icp/` | Campaign Manager playbooks and schema; the living ICP. |
| `fixtures/` | Fictional CRM and enrichment records; real regulator publications. |
| `tests/`, `.github/workflows/ci.yml` | Unit tests and CI. |
| `examples/` | One labelled offline-test-mode run. |
