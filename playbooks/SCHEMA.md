# Campaign Manager playbook schema

The Campaign Manager stub gave eight fields and said "Infer the rest. Mark guesses." Operator decision A-041: each playbook file keeps the stub's shape exactly, with one audience, one trigger and one channel. A play is one buyer, one trigger and one channel. A small motion file lists the playbooks that make up a motion.

Every field below says where it came from (the stub, an operator decision, or a proposal still awaiting the operator), why it is useful, and its register row in `AMBIGUITY-REGISTER.md`. Files are JSONC (JSON with `//` comments), so each guess is marked where it sits. The loader and validator are in `agent/input/playbook.py`.

| File | What it is |
|---|---|
| `motions/reign-first-motion.jsonc` | The first Reign motion: owner, principal, and the three playbooks below. |
| `bank-sr26-2.jsonc` | Bank buyer, SR 26-2 trigger, channel `briefing`. Implemented. |
| `biopharma-fda-pccp.jsonc` | Biopharma quality buyer, FDA PCCP trigger. Trigger not implemented yet, with the reason. |
| `defense-forge-first.jsonc` | Defense supplier, Forge first. Trigger not implemented yet, with the reason. |

## Playbook fields

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| `playbook_id` | stub | Names the playbook in every audit record and kill switch. Lowercase letters, digits and hyphens only. | security review |
| `product` | stub | `reign` or `forge`. | - |
| `audience.icp_id`, `audience.segment` | stub | Which ICP version and segment the playbook targets. | - |
| `trigger.type`, `trigger.id` | stub | `regulatory`, `event` or `manual`, and the trigger record in the regulator feed. | - |
| `channel` | stub | `briefing`, `sequence`, `slack` or `unknown`. `briefing` is the booked Executive Assurance Briefing meeting (the meeting the CEO's notes propose, not a public iTmethods product); the forwardable brief is the document that earns it. | A-042 (operator) |
| `approval` | stub (empty object) | See below. | - |
| `kill_criteria[]` | stub (empty list) | See below. | - |
| `audit` | stub (empty object) | See below. | - |
| `version`, `supersedes` | operator | Which rules were in force for a given touch; every audit record carries id and version. | A-016 |
| `status` | operator | `active`, `paused` or `retired`, so the CRO (chief revenue officer) can stop a playbook without deleting its history. | A-034 |
| `owner` | operator | The accountable human; in the demo, the candidate. | A-026 |
| `trigger_status`, `trigger_not_implemented_reason` | operator | A buyer can be encoded before its trigger is ready, with the reason visible. | A-041 |
| `lead_product` | operator | Lets the defense playbook lead with Forge while the motion is Reign. Lead with Forge; Reign's assurance is what makes letting agents into the estate possible. | A-023 |
| `handoff.route_to` | operator | `account_owner`: on a regulatory trigger the brief goes to the named iTmethods account owner, never to the bank. | A-043 |
| `handoff.cold_outreach_until_briefing_booked` | operator | `false`: no new cold outreach to the buyer until a briefing is booked. | A-043 |
| `unconfirmed_applicability` | operator | `hold` (general case) or `structured_brief` (the SR 26-2 brief: what changed, what is certain, what depends on structure marked "Confirm", next step; never says a rule applies). | A-025, A-044 |
| `claims[]` | operator | Approved product claim ids (`docs/research/product-claims.json`); sentences about products must quote them word for word. | A-029 |
| `routing.lanes` | operator | Suggests risk and engineering contacts by title, without asking the buyer to pick. | A-011 |
| `routing.do_not_route` | operator | Titles never suggested, starting with the CISO. | A-032 |

## `approval`

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| (rule) | stub | "`approval` must name a human if `channel` can send." Enforced by the validator. | - |
| `principal` | operator | R-17's "named human who authorized this class of action". On every audit record. | A-026 |
| `approvers[]` | operator | Who may approve. For a playbook routed to the account owner, the approver must also be that account's owner in HubSpot. | A-026, A-043 |
| `channels_that_send[]` | operator | `briefing` (booking reaches a person), `sequence` and `unknown` count as sending; `slack` is internal. | A-035, A-042 |
| `sender` | operator | `none`: nothing is wired to send; approved means ready to send. | A-035 |

## `kill_criteria[]`

The stub: "how CRO stops a motion that goes sloppy". Operator decision A-037: quality-based only, never a count ceiling, and no volume cap (a `limits` block is rejected). Each entry has `id`, `metric`, `op`, `threshold` and `why`. Metrics are computed after every run, approval decision and feedback report; if any criterion trips, that playbook's kill switch engages until its owner or an approver clears it.

Metrics: `audit_blocked`, `gate_failed_ratio`, `rejected_ratio` (over decided requests; both ratios are not measured, and cannot trip, until there are 5 attempts or decisions, A-049), `complaints`, `wrong_account_reports` (from `python3 -m agent.feedback.report`).

## `audit`

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| `rule` | stub | Must be `R-17` when the audience is financial services. | - |
| `required_for` | operator | `all_segments`. An audit record is a receipt of what our agent did, not a test the prospect must pass: it never disqualifies a prospect; only our own action stops when the receipt cannot be written. | A-007, A-038 |
| `sink` | operator | `jsonl`: a local append-only file behind a swappable interface; wiring the real audit store is day-one work. | A-008 |

## Motion file

| Field | Why it is useful |
|---|---|
| `motion_id`, `version` | Stamped on the audit records of the motion-level ICP pass. |
| `owner`, `principal` | Named humans for the ICP pass. |
| `icp` | The ICP file the motion filters with. |
| `playbooks[]` | Playbook ids, loaded only from this directory. |
