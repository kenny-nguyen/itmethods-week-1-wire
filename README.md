# Week-1 Wire: regulatory trigger to governed account brief

Take-home for iTmethods (Growth Engineer, AI-Native). Timed window: 2026-09-24 22:50 to 2026-09-25 01:50 KST.

The artifact is option 3 of the assignment: **a Claude skill that drives an MCP (Model Context Protocol) server, with evals.** The agent reads a regulatory trigger (SR 26-2, the Federal Reserve's revised model risk guidance), reasons about a specific bank, and drafts a short brief in which every line is sourced. The server's tools enforce rule R-17 (the audit record comes before any touch on a financial-services account counts), the ICP (ideal customer profile) exclusions, the do-not-route list and the claim limits. The AI decides; the code enforces. Nothing is sent: each brief goes to the bank's named iTmethods account owner, who decides whether to share it.

The assignment packet is private and is not in this repository. Where a decision depends on a line of it, that short line is quoted in `PROCESS-LOG.md` or `AMBIGUITY-REGISTER.md`.

## What is in the box

| Piece | Where | Status |
|---|---|---|
| The agent's instructions (Claude skill) | `skills/regulatory-trigger-brief/SKILL.md` (linked under `.claude/skills/`) | Built. |
| Governed tools (MCP server): `list_playbooks`, `fetch_source`, `screen_account`, `check_applicability`, `route_contact`, `check_claims`, `write_audit_record`, `request_approval` | `agent/mcp_server.py` over `agent/tools.py`; `.mcp.json` | Built, tested over a real MCP client in-process and over stdio. |
| Evals | `evals/agent_cases.json` + `evals/score_run.py` (scores a run's briefs); `evals/brief_cases.json` (63 cases for the output gate) | Built. |
| Human decisions | `python3 -m agent.feedback.decide`, `report`, `kill` | Built. |
| Offline test mode | `python3 -m agent.run_playbook` with no key: a deterministic template drafts the briefs | For CI and tests only. **Not the agent.** |
| Direct model-API path | `AnthropicProvider` in `agent/processing/brief.py` | Documented. **Not exercised live**: no API key in the build environment. |

A live agent run has not happened in this build session. It is run in a Claude Code session for the demo, and its briefs are scored with `python3 -m evals.score_run`.

## How to use

### 1. Set up

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt     # mcp==2.2.0, the one dependency
```

### 2. Run the agent in Claude Code

Open Claude Code in the repository root. It reads `.mcp.json` and starts the `week1-wire` server, and finds the skill under `.claude/skills/`. Then ask, for example:

> Use the regulatory-trigger-brief skill to brief account hs-1001 on SR 26-2.

The agent calls the tools in order, reads the sources, drafts, self-checks with `check_claims`, and calls `request_approval`. Output lands in `out/` (or `WIRE_OUT_DIR`): the brief, an approval request routed to the account owner, the R-17 audit trail (`audit.jsonl`) and the error log (`errors.jsonl`). Other MCP clients (Claude Desktop, any client): see `docs/production.md`.

### 3. Score the run

```
python3 -m evals.score_run --out out
```

### 4. The account owner decides, reports, or stops the playbook

```
python3 -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
  --approver "Kenny Nguyen" --approve --reason "Sources and routing checked."
python3 -m agent.feedback.report --request out/runs/<run>/approvals/<account>.json \
  --by "Kenny Nguyen" --kind wrong_account --detail "Brief names the wrong parent company."
python3 -m agent.feedback.kill --playbook-id bank-sr26-2 --by "Kenny Nguyen" --reason "Drafts read generic."
```

Only the listed approver who is also the account's HubSpot owner can decide; the request is checked against its audited create record. Nothing is wired to send, so approved means ready to send.

### 5. Offline test mode and checks (CI)

```
python3 -m agent.run_playbook          # OFFLINE TEST MODE with no key: template drafts, not the agent
python3 -m unittest discover -s tests -t . -v
python3 -m evals.run_evals
```

To read output without running anything: `examples/20260924T151407Z-5ea5d4/` (an offline-test-mode run, labelled as such), including its generated `review.html`. Production setup, adapters, scheduling and recovery: [`docs/production.md`](docs/production.md).

## Cut, sequenced, refused

**Architecture principle.** The artifact is not coupled to banking. The skill and the MCP tools are buyer-agnostic; everything bank-specific lives in data: the bank playbook (`playbooks/bank-sr26-2.jsonc`), the SR 26-2 trigger record and its regulation mapping (OSFI E-23 and B-13, the US-arm and EU-arm conditions) in `fixtures/regulatory_feed.json`. The packet gives the most detail on the bank (the CEO notes, R-17 being specific to financial services, SR 26-2 and DORA), so the bank is the proving ground, not the limit.

| Cut | Why | With more time |
|---|---|---|
| Pharma trigger not built; its playbook is encoded | The artifact menu says "a regulatory trigger" (singular) and "pick one, go deep, do not spray"; the CEO says the bank is the buyer that matters this month; one deep trigger with sources and evals beats two thin ones; adding it later is a data change. | Build the FDA PCCP trigger on the verified guidance, a Quality / Regulatory Affairs routing lane and GxP-aware claim limits, scored by the same evals. |
| Defense trigger not built; the approach is documented | None of the menu's four triggers fits defense; CMMC appears only with a question mark in the ICP sketch; the CEO is unsure ("I think. Check with Rob."); iTmethods states it holds no CMMC certification, so a CMMC-driven brief risks implying capability it lacks. | Confirm with Rob, then a CMMC scoping questionnaire (not a claim of readiness) feeding a Forge substrate briefing play. |
| No live send | R-17 needs a named approver and a blockable send, which cannot be proven without HubSpot or email access; the CEO says no bank outreach until a briefing is booked. Approved means ready to send. | Wire the real blockable send path (`docs/production.md` section 5). |

| Sequenced | Why |
|---|---|
| Bank first | The CEO's priority; R-17 is mandatory for financial services, so the bank path proves the knockout rule. |
| Governance tools before the agent | The rules had to exist and be tested before anything could draft. |
| Evals before the demo | The live run is judged by criteria fixed in advance. |

| Refused | Why |
|---|---|
| The blog | "Do not write a blog. Build the trigger." |
| Generic CISO sequences | The CEO's explicit kill condition; the CISO is on the do-not-route list and "AI governance" is a gate failure. |
| A volume cap in place of precision | Operator decision A-037. |
| Any compliance, certification or independent-assurance claim | iTmethods' own pages make none; the gate refuses them. |
| Inventing a source or a fact | A missing fact is flagged, never filled; unverified sources cannot be cited. |

## What we went looking for vs what we assumed

**Went looking (read from the source, not recalled):**

| Question | What we found | Log |
|---|---|---|
| Is SR 26-2 real, and whom does it cover? | Federal Reserve letter of April 17, 2026; "most relevant to banking organizations with over $30 billion in total assets regulated by the Federal Reserve"; supersedes SR 11-7 and SR 21-8. | D-003 |
| What binds a Canadian D-SIB (domestic systemically important bank) for sure? | OSFI E-23 (model risk), page shows effective May 1, 2027; OSFI B-13 (technology and cyber risk). | D-003, D-028 |
| DORA's source? | EUR-Lex blocked automated reads; the EIOPA page names Regulation (EU) 2022/2554. | D-028 |
| What do Forge and Reign actually do, and in what state? | itmethods.com: Ops and Gateway available, Factory beta, Assurance in co-design; Gateway is the governed path for agent calls. | D-005 |
| What must iTmethods never claim? | Its own pages: no audit opinion, certification or independent assurance; no FedRAMP; per the researcher, no CMMC certification and no CUI handling. | D-005 |
| FDA PCCP guidance? | My two guessed URLs were wrong; the operator's researcher found the real guidance. | R-012 |
| The MCP SDK's current API? | Read from the installed `mcp==2.2.0`: `FastMCP` became `MCPServer` in 2.x. | R-011 |

**Assumed, then decided by the operator** (full reasoning and reversal triggers in `AMBIGUITY-REGISTER.md`):

| Row | Reading | One-line reason |
|---|---|---|
| A-004 | Unknown headcount is held for a human | Precision, not volume. |
| A-006 | Unknown industry counts as financial services, flagged | An FS account must never escape its audit record. |
| A-007, A-038 | R-17 audit on every segment | A receipt of what our agent did, never a test the prospect must pass. |
| A-011, A-032 | Route risk and engineering by title; never the CISO | "Route them without asking"; the CEO's CISO warning. |
| A-013 | Fictional fixture companies | No invented facts about real banks. |
| A-021 | Rob's risk-committee note is a flag | Unvetted Slack note. |
| A-023 | Defense leads with Forge, Reign as the reason agents can be let in | The CEO's last word; a natural ascension. |
| A-025, A-044 | Hold when applicability is unknown; the SR 26-2 brief separates certain from "Confirm" | Never claim a rule applies. |
| A-029 | Product claims only from the sourced list | A wrong claim to a bank is worse than none. |
| A-031 | Clearly outside the ICP: dropped with the reason audited; unclear: held | No silent drops. |
| A-033 | Fail loudly, never fall back silently | Nothing is worse than a silent failure. |
| A-035 | No send path; "unknown" channel counts as sending | If it cannot be audited and approved, it does not send. |
| A-036 | Agent adoption is a signal, never an exclusion | Nothing in the packet says to exclude on "none". |
| A-037 | No volume cap; quality-based kill criteria | Precision first. |
| A-039, A-040 | Chipmakers without an export-control problem and hospitals go on a watch list | Noticed and logged, never contacted. |
| A-041, A-042, A-043 | Three stub-shaped playbooks; "briefing" is the booked meeting; the brief goes to the account owner | Close reading of the stub and the CEO notes. |
| A-045 | Brief limit of 350 words before the owner-only notes | Still proposed. |

## Reconciling the CEO notes

| Contradiction in the notes | Decision | Why | Row |
|---|---|---|---|
| "Need this live. Not a plan." vs "Everything that sends needs a named human." | A working agent that drafts and routes; nothing sends without a named approver, and no send path is wired yet. | Live and governed are compatible if the send is the gated step. | A-035, A-043 |
| "40 first meetings this quarter" vs "No spray. Precision." | No volume cap; quality-based kill criteria. | A quota invites spray; quality signals stop sloppiness. | A-037 |
| "Do not outbound to the bank until a briefing is on the calendar" vs "we should already be in the thread" on a trigger | No cold outreach; on a trigger the brief goes to the account owner, who shares it in the existing relationship. | The bank already runs Forge, so "the thread" is the existing relationship. | A-043 |
| Risk and engineering "will not sit in the same meeting" | One brief, two lanes by title, never ask. | "Route them without asking." | A-011 |
| Defense: "Forge-first... I think. Check with Rob. Actually lead with the substrate story" | Lead with Forge; Reign is why agents can be let near the estate. | The last word in the notes; not implemented this window. | A-023 |
| ICP sketch lists "AI-native SaaS startups"; notes say remove them | Excluded under any naming variant. | Operator-approved; patterns hardened by two QA passes. | A-003 |
| Pharma "asked about FDA PCCP... build the trigger" vs one deep trigger | Encoded as a playbook, trigger not implemented yet. | One trigger done well beats three done thinly. | A-027, A-041 |
| Website says "banks, hospitals, and defense"; Slack says do not spray hospitals this month | Watch, don't contact. | Explicit instruction; spray is a knockout. | A-040 |

## Day-one wiring

Each tool replaces one fixture class. The pipeline and the MCP tools only talk to these interfaces (`agent/input/base.py`, `agent/governance/audit.py`).

| Tool | Job | Interface to implement |
|---|---|---|
| HubSpot | Accounts, including the named account owner | `AccountSource.list_accounts() -> list[Account]` |
| HubSpot (or the Reign audit store) | R-17 audit records as timeline events | `AuditSink.append(record: dict) -> None`, durable before returning, raises on failure |
| Clay | Enrichment columns: agent adoption, risk committee, export-control exposure, US Federal Reserve entity | `EnrichmentSource.enrich(account_id) -> Enrichment` |
| ZoomInfo | Contact search by the playbook's lane title keywords | `ContactSource.contacts_for(account_id) -> list[Contact]` |
| Regulator feeds | Trigger records with verified sources | `TriggerSource.get(trigger_id) -> Trigger`, `implemented_ids()` |
| Send path | Share an approved brief | Not built. Spec in `docs/production.md` section 5. |

## What I would not ship

| Buyer | Example | Why |
|---|---|---|
| Bank | A brief implying SR 26-2 applies before a US Federal Reserve-supervised entity is confirmed. | A wrong regulatory claim to a bank's audit function destroys trust. The gate refuses it; the brief puts it under "Confirm". |
| Hospital | Any touch this month. | Explicit CEO instruction; spray is a knockout. Hospitals are on the watch list. |
| Defense supplier | Any hint of CMMC, FedRAMP or CUI capability. | iTmethods says it holds none, so the claim would be false. The gate refuses the terms outright. |

## Stuck, and the next experiment

| Stuck on | Next experiment |
|---|---|
| No model API key in the build environment | Run the direct API path with a key and score its briefs with the same evals. |
| No live agent run in this session | Run the skill in Claude Code with the server attached (the demo) and commit the scored result to `examples/`. |
| No HubSpot, Clay or ZoomInfo access | Wire the adapters in the day-one table; the fixtures already exercise every interface. |
| EUR-Lex and fda.gov block automated reads from this environment | Fetch the regulation texts through a browser or the researcher and store verified text snapshots next to the feed. |
| The approver is a typed name | Bind approvals to an authenticated identity (single sign-on or the HubSpot user) before any send path is wired. |

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

## Repo map

| Path | Purpose |
|---|---|
| `README.md` | This file. |
| `AGENTS.md`, `CLAUDE.md`, `contract/`, `.claude/agents/` | The working contract and kit (see above). |
| `PROCESS-LOG.md` | Append-only decision log, written during the window. |
| `AMBIGUITY-REGISTER.md` | Every ambiguity, the reading taken, and what would flip it. |
| `INTAKE-WORKSHEET.md` | First structured read of the assignment. |
| `skills/regulatory-trigger-brief/` | The Claude skill: the agent's instructions. |
| `agent/mcp_server.py`, `agent/tools.py`, `.mcp.json`, `requirements.txt` | The MCP server and the governed tools it exposes. |
| `agent/run_playbook.py` | Batch runner; offline test mode without a key. |
| `agent/output/`, `agent/feedback/` | OUTPUT and FEEDBACK stages: artifacts, approval decisions, kill criteria, kill switch. |
| `agent/governance/` | R-17 audit trail and the error log, used by every stage. |
| `agent/input/` | INPUT stage: adapter interfaces and local fixture adapters. |
| `agent/processing/` | PROCESSING stage: ICP filter, applicability preflight, brief generation, output checks. |
| `prompts/` | The system prompt for the direct model-API path (not exercised live). |
| `evals/` | Agent-run eval cases and scorer (`python3 -m evals.score_run`); output-gate cases (`python3 -m evals.run_evals`). |
| `playbooks/` | The three Campaign Manager playbooks (one audience, trigger and channel each), the motion file that references them, and `SCHEMA.md` explaining every field. |
| `icp/` | The living ICP, with the source or register row of every field. |
| `fixtures/` | Fictional HubSpot, ZoomInfo and Clay records, plus the real regulator publications with fetched URLs. |
| `tests/` | Unit tests, one file per stage. |
| `.github/workflows/ci.yml` | CI (continuous integration): offline tests and evals, plus the MCP server test with the pinned package. |
| `examples/` | One offline-test-mode run (labelled): briefs, approval requests, audit records, summary, scores and the generated `review.html`. |
| `agent/output/review.py` | Generates each run's one-page HTML review view. |
| `docs/production.md` | Production guide: configuration, end-to-end run, approval and kill switch, wiring each adapter, scheduling, recovery, known gaps. |
| `agent/config.py` | Deployment configuration read from the environment. |
| `docs/research/` | Sourced facts the agent is allowed to use (product claims, regulator pages). |
