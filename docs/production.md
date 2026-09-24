# Running the agent in production

How to connect the agent (a Claude skill driving the `week1-wire` MCP server), configure it, run a trigger end to end, operate the approval and kill switch, connect the real stack (HubSpot, Clay, ZoomInfo, a send path), and launch the next product. The last section lists what is not production-ready.

Three ways briefs get drafted, and only the first is the agent:

| Path | What drafts | Status |
|---|---|---|
| Agent | Claude, following `skills/regulatory-trigger-brief/SKILL.md`, through the MCP tools | Built; the live run happens in a Claude Code session for the demo. |
| Direct model-API path | `AnthropicProvider` via `python3 -m agent.run_playbook` with `ANTHROPIC_API_KEY` set | Documented, **not exercised live**. |
| Offline test mode | The deterministic template, `python3 -m agent.run_playbook` with no key | CI and tests only; **not the agent**. |

All three pass through the same governed stages and the same output gate.

The batch, approval, report and kill commands on this page were run from a clean clone on 2026-09-25 (process log D-030); the MCP and scoring commands were verified afterwards (D-035). Not run here: a live agent session in Claude Code (that is the demo), and the direct model-API call (no key in the build environment).

## 1. Requirements and the MCP server

- Python 3.11 or later, run as `python3`. Run commands from the repository root.
- The governed tools, the batch runner and all offline tests use the standard library only. The MCP server needs one pinned package:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt     # mcp==2.2.0
```

Connect a client:

| Client | How |
|---|---|
| Claude Code | Open it in the repository root. `.mcp.json` starts `week1-wire` (`.venv/bin/python -m agent.mcp_server`), and the skill is found under `.claude/skills/`. Ask: "Use the regulatory-trigger-brief skill to brief account hs-1001 on SR 26-2." |
| Claude Desktop | Add to `claude_desktop_config.json` under `mcpServers`: `"week1-wire": {"command": "/abs/path/to/repo/.venv/bin/python", "args": ["-m", "agent.mcp_server"], "env": {"WIRE_OUT_DIR": "/abs/path/to/out"}}`, and run it with the repository as the working directory (or set `PYTHONPATH` to the repository). Paste the skill's instructions into the conversation or a project. |
| Any MCP client | Launch `python -m agent.mcp_server` over stdio from the repository root with the venv's Python. |

Every tool failure is an MCP tool error whose text ends with "Recovery: ..." naming what to do.

## 2. Configuration

Read in one place, `agent/config.py`, plus the provider settings in `agent/processing/brief.py`:

| Variable | Default | Meaning |
|---|---|---|
| `WIRE_OUT_DIR` | `<repo>/out` | Runs, audit trail, error log, kill switches and feedback reports. Set it once per deployment, not per command: every command must see the same directory, or the kill switch and audit trail split in two. |
| `ANTHROPIC_API_KEY` | unset | Claude Messages API key. Unset means the deterministic template drafts every brief. |
| `WIRE_PROVIDER` | auto | `offline` (or `template`) forces offline test mode even when a key is set. |
| `WIRE_MODEL` | `claude-opus-5` | Model id for the Claude Messages API. |

Deliberately **not** environment variables:

- **The named principal and approvers** live in the playbook files (`approval.principal`, `approval.approvers`, `owner`). Playbooks are reviewed through git, and the approval step reloads them from `playbooks/` and checks their hash, so changing a shell cannot change who approves.
- **Which playbooks run** is the motion file, `playbooks/motions/<motion>.jsonc`, chosen with `--motion` (default `reign-first-motion`). Playbooks are only ever loaded by id from `playbooks/`.

Field-by-field playbook reference: `playbooks/SCHEMA.md`.

## 3. Run a trigger end to end

With the agent: in Claude Code, "Use the regulatory-trigger-brief skill to brief account hs-1001 on SR 26-2." Then score what it produced:

```
python3 -m evals.score_run --out "${WIRE_OUT_DIR:-out}"
```

As a batch (offline test mode without a key; the direct model-API path with one):

```
export WIRE_OUT_DIR=/var/lib/week1-wire      # optional; default is ./out
python3 -m agent.run_playbook                  # the reign-first-motion motion
```

Exit codes: `0` ran; `2` refused (invalid motion or playbook, unreadable inputs); `3` ran, and a playbook's kill criteria tripped.

Where things land, under `WIRE_OUT_DIR`:

| Path | What it is |
|---|---|
| `runs/<run>/briefs/<account>.md` | Each brief that passed the output gate. |
| `runs/<run>/approvals/<account>.json` | Its approval request: `status: pending`, `send: false`, `route_to.account_owner`. |
| `runs/<run>/summary.json` | Every account's outcome and reason, the watch list, each playbook's status and metrics. |
| `audit.jsonl` | The R-17 audit trail, one JSON record per line. |
| `errors.jsonl` | The error log, separate from the audit trail. |
| `state/kill/<playbook>.json` | Present only while that playbook's kill switch is engaged. |
| `state/feedback/<playbook>.jsonl` | Complaint and wrong-account reports. |

Reruns are safe: an account already briefed for the same trigger and playbook (any status except `rejected`) is reported as `already_briefed` and not drafted again.

## 4. Approval and the kill switch

The agent never contacts a bank. On a regulatory trigger, it writes the brief and routes the approval request to the named iTmethods account owner, who decides whether to share it in the existing relationship.

```
python3 -m agent.feedback.decide --request "$WIRE_OUT_DIR/runs/<run>/approvals/<account>.json" \
  --approver "Kenny Nguyen" --approve --reason "Sources and routing checked."
python3 -m agent.feedback.decide --request "$WIRE_OUT_DIR/runs/<run>/approvals/<account>.json" \
  --approver "Kenny Nguyen" --reject --reason "Reads too generic for a CAE."
```

A decision is refused unless the request is under `WIRE_OUT_DIR/runs`, the playbook (loaded by id from `playbooks/`) is unchanged since the request was created, the approver is listed in it and is the account's owner in HubSpot, the request is still pending, and, for an approval, the playbook's kill switch is off. The decision's audit record is written before the request file changes. Approved means ready to send: no send path is wired.

Quality feedback and the kill switch:

```
python3 -m agent.feedback.report --request "$WIRE_OUT_DIR/runs/<run>/approvals/<account>.json" \
  --by "Kenny Nguyen" --kind complaint --detail "Prospect said the brief misread their structure."
python3 -m agent.feedback.kill --playbook-id bank-sr26-2 --by "Kenny Nguyen" --reason "Drafts read generic."
python3 -m agent.feedback.kill --playbook-id bank-sr26-2 --by "Kenny Nguyen" --reason "Reviewed the drafts." --clear
```

Exit codes for `decide`, `report` and `kill`: `0` done; `2` refused; `report` returns `3` when the report trips a kill criterion and engages the switch. Clearing the switch restarts the complaint and wrong-account counts from that moment, so reports a human has already reviewed do not re-trip it on the next run.

Only the playbook owner or a listed approver can report, engage or clear. The kill criteria (quality-based: audit failures, gate failures, rejections, complaints, wrong-account reports) are checked after every run, decision and report, and after every governed tool call in an agent session (one MCP server session counts as one run), and engage the switch automatically. An audit write failure trips at once. The ratio criteria (gate failures, rejections) count only once there are at least 5 decisions to measure (process log D-041, to confirm with sales leadership). Engaging never waits on the audit store; clearing is refused if its audit record cannot be written.

## 5. Wire the real stack on day one

The batch runner and the MCP tools only talk to the interfaces in `agent/input/base.py` and `agent/governance/audit.py`. Swapping a fixture for a real tool means one class per tool, then constructing it in `_load_inputs()` in `agent/run_playbook.py` (the MCP tools use the same function), and, for HubSpot, in `account_owner()` in `agent/feedback/decide.py`, which reads the account owner at decision time.

| Tool | Job | Interface to implement | Notes |
|---|---|---|---|
| HubSpot | Accounts, with the named account owner | `AccountSource.list_accounts() -> list[Account]` | Map industry, headcount, country, total assets, "runs Forge", "briefing booked" and the owner into `agent.input.models.Account` with `system="hubspot"`. Unknown stays `None`: the ICP holds or flags on unknowns. |
| HubSpot timeline (or the Reign audit store) | R-17 audit records, one timeline event per record | `AuditSink.append(record: dict) -> None` | Durable before returning; raises on any failure, which is what blocks the action. Append-only. |
| Clay | Enrichment columns: `agent_adoption`, `risk_committee`, `export_control_exposure`, `us_fed_regulated_entity`, plus a row id as `source` | `EnrichmentSource.enrich(account_id) -> Enrichment` | "No data" is `None`, not an exception. Only called for in-profile accounts with a live playbook. |
| ZoomInfo | Contact search at the account by the playbook's lane title keywords (risk: audit, risk, compliance; engineering: engineering, platform, technology, architecture) | `ContactSource.contacts_for(account_id) -> list[Contact]` | Names and titles are untrusted text. The do-not-route list is applied by the tools, not the search. |
| Regulator feeds | Trigger records | `TriggerSource.get(trigger_id) -> Trigger`, `implemented_ids() -> set[str]` | Every fact cites a source with `verified: true`; a human marks a trigger implemented. |
| Send path | Share an approved brief | Not built | Add a sender that accepts only a request with status `approved_ready_to_send`, re-checks the kill switch at send time, writes an R-17 `message` record with `send: true`, the approver and `blockable: true` before sending, and records the outcome. Until then `approval.sender` stays `none`. |

## 5a. Launch the next product: one new playbook file, no code

A play is one buyer, one trigger and one channel. To start a new motion, copy a playbook, change the data, and list it in a motion file. Example: a Forge motion for defense suppliers, once a defense trigger is verified.

1. Add the trigger record to the regulator feed (with verified sources) if it is new; that is the only case that needs a new trigger adapter or feed entry.
2. Create `playbooks/defense-forge-launch.jsonc` from `playbooks/defense-forge-first.jsonc`, changing only data:

```
"playbook_id": "defense-forge-launch",
"version": "1.0.0",
"product": "forge",
"audience": { "icp_id": "icp/icp.json@0.3.0", "segment": "defense_supplier" },
"trigger": { "type": "regulatory", "id": "<the verified trigger id>" },
"channel": "briefing",
"trigger_status": "implemented",
"claims": ["P-FORGE", "P-GATEWAY"],
```

3. Create `playbooks/motions/forge-launch.jsonc` listing `"playbooks": ["defense-forge-launch"]`.
4. Check it: `python3 -m unittest discover -s tests -t .` validates every playbook the tests load; the run refuses an invalid playbook with each problem listed.

No Python changes. The approval, kill criteria, audit rule, ICP, routing and output gate apply to the new playbook unchanged.

## 6. Schedule trigger checks

The motion is safe to run on a schedule: reruns do not re-brief, kill switches skip stopped playbooks, and nothing sends. Example cron entry (hourly):

```
0 * * * * cd /opt/week1-wire && WIRE_OUT_DIR=/var/lib/week1-wire python3 -m agent.run_playbook >> /var/log/week1-wire/run.log 2>&1
```

Alert on exit code `2` (refused) and `3` (kill switch engaged), and on any new line in `errors.jsonl`.

## 7. How failures surface and how to recover

| Symptom | Where it shows | Recovery |
|---|---|---|
| Model call failed (direct API path) | Account status `draft_failed`; `errors.jsonl` stage `processing.draft`, message ends with the recovery options | Retry; or run offline test mode (unset `ANTHROPIC_API_KEY` or set `WIRE_PROVIDER=offline`) to check the pipeline; or check the key, `WIRE_MODEL` and network access to `api.anthropic.com`. There is never a silent fallback. |
| MCP tool refused | The tool error text, ending "Recovery: ..."; `errors.jsonl` stage `tool.*` | Follow the recovery text. The tools refuse out-of-order calls, closed accounts, unimplemented triggers, stopped playbooks and drafts that fail the gate. |
| Audit store down or record invalid | Account status `audit_blocked`; `errors.jsonl` stage `governance.audit`; kill switch engaged by `audit-write-failure` | Restore the sink, review the error log, then clear the kill switch with a reason. |
| Write failed after the audit record | `errors.jsonl` stage `governance.commit`; a second audit record with `detail.outcome = "failed"` | Fix the file system; rerun. The brief and request are written together or not at all. |
| Draft failed the output gate | Account status `gate_failed` with `gate_problems` in `summary.json`; `errors.jsonl` stage `processing.gate` | Read the problems; fix the prompt, claims or source data. Once 5 drafts have been attempted, more than one failure in five engages the kill switch. |
| A request file was edited | `decide` refuses: "does not match its audited create record" or "no playbook hash" | Do not edit requests; rerun the motion to get a new request. |
| Playbook or motion invalid | Exit code 2, `RUN REFUSED:` with each problem; `errors.jsonl` stage `input.playbook` | Fix the file; `playbooks/SCHEMA.md` explains each field. |
| Adapter failed | `errors.jsonl` stages `input.accounts`, `input.enrichment`, `input.contacts` | Account-level failures skip that account; an account-list failure refuses the run. |

## 8. Not production-ready yet

- **No live agent run in the build session.** The skill and server are built and tested; the live run is the demo, scored with `python3 -m evals.score_run`.
- **Direct model-API path not exercised.** No API key was available; no model draft has been generated or gated live.
- **Approver identity is a typed name.** It must come from an authenticated identity (single sign-on, HubSpot user) before anything can send.
- **No send path.** By design until the approval flow is wired to a real sender (section 5).
- **Fixtures, not tools.** HubSpot, Clay and ZoomInfo are local fictional files; the audit sink is a local file.
- **Single writer.** The file sinks assume one process at a time; concurrent runs need a real store with append guarantees.
- **Crash window.** A process killed between the audit write and the commit leaves a record with no outcome; production needs an idempotent commit keyed by record id.
- **English word lists in the output gate.** They catch the listed claims and paraphrases, not every false sentence; the account owner's review is the control for plausible falsehoods.
- **One trigger implemented.** SR 26-2. FDA PCCP and the defense trigger are encoded but not implemented.
