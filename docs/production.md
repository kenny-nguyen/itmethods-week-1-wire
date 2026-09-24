# Running the agent in production

How to configure the brief agent, run a trigger end to end, operate the approval and kill switch, and connect the real stack (HubSpot, Clay, ZoomInfo, a send path). The last section lists what is not production-ready.

Every command on this page was run from a clean clone on 2026-09-25; the process log records it (entry D-030). One path was **not** run: the live model call. No model API key was available in the build environment, so every run used the deterministic template. The model path is covered by unit tests of provider selection and by the same output gate, but no live model draft has been produced or gated yet.

## 1. Requirements

- Python 3.11 or later, run as `python3`. Standard library only; nothing to install.
- Run commands from the repository root.

## 2. Configuration

Read in one place, `agent/config.py`, plus the provider settings in `agent/processing/brief.py`:

| Variable | Default | Meaning |
|---|---|---|
| `WIRE_OUT_DIR` | `<repo>/out` | Runs, audit trail, error log, kill switches and feedback reports. Set it once per deployment, not per command: every command must see the same directory, or the kill switch and audit trail split in two. |
| `ANTHROPIC_API_KEY` | unset | Claude Messages API key. Unset means the deterministic template drafts every brief. |
| `WIRE_PROVIDER` | auto | `template` forces the template even when a key is set. |
| `WIRE_MODEL` | `claude-opus-5` | Model id for the Claude Messages API. |

Deliberately **not** environment variables:

- **The named principal and approvers** live in the playbook files (`approval.principal`, `approval.approvers`, `owner`). Playbooks are reviewed through git, and the approval step reloads them from `playbooks/` and checks their hash, so changing a shell cannot change who approves.
- **Which playbooks run** is the motion file, `playbooks/motions/<motion>.jsonc`, chosen with `--motion` (default `reign-first-motion`). Playbooks are only ever loaded by id from `playbooks/`.

Field-by-field playbook reference: `playbooks/SCHEMA.md`.

## 3. Run a trigger end to end

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

The agent never contacts a bank. On a regulatory trigger it writes the brief and routes the approval request to the named iTmethods account owner, who decides whether to share it in the existing relationship.

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

Only the playbook owner or a listed approver can report, engage or clear. The kill criteria (quality-based: audit failures, gate failures, rejections, complaints, wrong-account reports) are checked after every run, decision and report, and engage the switch automatically. Engaging never waits on the audit store; clearing is refused if its audit record cannot be written.

## 5. Wire the real stack on day one

The pipeline only talks to the interfaces in `agent/input/base.py` and `agent/governance/audit.py`. Swapping a fixture for a real tool means one class per tool, then constructing it in `_load_inputs()` in `agent/run_playbook.py` (and, for HubSpot, in `account_owner()` in `agent/feedback/decide.py`, which reads the account owner at decision time).

| Tool | Interface to implement | Returns | Notes |
|---|---|---|---|
| HubSpot accounts | `AccountSource.list_accounts() -> list[Account]` | `agent.input.models.Account`, including `owner` (the named account owner) and `system="hubspot"` | Map the company record's industry, headcount, country, total assets, "runs Forge" and "briefing booked" into the fields of `Account`. Unknown values must stay `None`: the ICP holds or flags on unknowns. |
| HubSpot or Reign audit sink | `AuditSink.append(record: dict) -> None` | nothing | Must be durable before returning and must raise on any failure. Raising is what blocks the action (R-17). Keep writes append-only. |
| Clay enrichment | `EnrichmentSource.enrich(account_id) -> Enrichment` | `agent.input.models.Enrichment` with a `source` id for the row | "No data" is `None` fields, not an exception. Only called for in-profile accounts with a live playbook. |
| ZoomInfo contacts | `ContactSource.contacts_for(account_id) -> list[Contact]` | `agent.input.models.Contact` with `system="zoominfo"` | Names and titles are untrusted text; the output gate and the prompt treat them as data. |
| Regulator feed | `TriggerSource.get(trigger_id) -> Trigger`, `implemented_ids() -> set[str]` | `agent.input.models.Trigger` | Every fact must cite a source with a fetched URL (`verified: true`); the preflight blocks unverified sources. A human marks a trigger implemented. |
| Send path | not built | - | Add a sender that only accepts a request whose status is `approved_ready_to_send`, re-checks the kill switch at send time, writes an R-17 `message` record with `send: true`, the approver and `blockable: true` before sending, and records the outcome. Until then `approval.sender` stays `none`. |

## 6. Schedule trigger checks

The motion is safe to run on a schedule: reruns do not re-brief, kill switches skip stopped playbooks, and nothing sends. Example cron entry (hourly):

```
0 * * * * cd /opt/week1-wire && WIRE_OUT_DIR=/var/lib/week1-wire python3 -m agent.run_playbook >> /var/log/week1-wire/run.log 2>&1
```

Alert on exit code `2` (refused) and `3` (kill switch engaged), and on any new line in `errors.jsonl`.

## 7. How failures surface and how to recover

| Symptom | Where it shows | Recovery |
|---|---|---|
| Model call failed | Account status `draft_failed`; `errors.jsonl` stage `processing.draft`, message ends with the recovery options | Retry; or run with no key (unset `ANTHROPIC_API_KEY` or set `WIRE_PROVIDER=template`) for the template; or check the key, `WIRE_MODEL` and network access to `api.anthropic.com`. There is never a silent fallback. |
| Audit store down or record invalid | Account status `audit_blocked`; `errors.jsonl` stage `governance.audit`; kill switch engaged by `audit-write-failure` | Restore the sink, review the error log, then clear the kill switch with a reason. |
| Write failed after the audit record | `errors.jsonl` stage `governance.commit`; a second audit record with `detail.outcome = "failed"` | Fix the file system; rerun. The brief and request are written together or not at all. |
| Draft failed the output gate | Account status `gate_failed` with `gate_problems` in `summary.json`; `errors.jsonl` stage `processing.gate` | Read the problems; fix the prompt, claims or source data. More than one failure in five engages the kill switch. |
| Playbook or motion invalid | Exit code 2, `RUN REFUSED:` with each problem; `errors.jsonl` stage `input.playbook` | Fix the file; `playbooks/SCHEMA.md` explains each field. |
| Adapter failed | `errors.jsonl` stages `input.accounts`, `input.enrichment`, `input.contacts` | Account-level failures skip that account; an account-list failure refuses the run. |

## 8. Not production-ready yet

- **Live model path not exercised.** No API key was available; no model draft has been generated or gated live.
- **Approver identity is a typed name.** It must come from an authenticated identity (single sign-on, HubSpot user) before anything can send.
- **No send path.** By design until the approval flow is wired to a real sender (section 5).
- **Fixtures, not tools.** HubSpot, Clay and ZoomInfo are local fictional files; the audit sink is a local file.
- **Single writer.** The file sinks assume one process at a time; concurrent runs need a real store with append guarantees.
- **Crash window.** A process killed between the audit write and the commit leaves a record with no outcome; production needs an idempotent commit keyed by record id.
- **English word lists in the output gate.** They catch the listed claims and paraphrases, not every false sentence; the account owner's review is the control for plausible falsehoods.
- **One trigger implemented.** SR 26-2. FDA PCCP and the defense trigger are encoded but not implemented.
