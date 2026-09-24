# Campaign Manager playbook schema

The Campaign Manager stub gave eight fields and said "Infer the rest. Mark guesses." This page lists every field: where it came from, why it is useful, and the register row that proposes it when it is a guess. Guessed rows are `Proposed - awaiting operator` in `AMBIGUITY-REGISTER.md`. The loader and validator are in `agent/input/playbook.py`; the first-motion playbook is `reign-first-motion.jsonc`.

Files are JSONC (JSON with `//` comments) so each guess can be marked where it sits.

## Top level

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| `playbook_id` | stub | Names the motion in every audit record. | - |
| `version`, `supersedes` | guess | The stub says versioning is unknown. An auditor needs to know which rules were in force for a given touch, so every audit record carries id and version. | A-016 |
| `status` | guess | `active`, `paused` or `retired`. Lets the CRO (chief revenue officer) stop a motion without deleting its history. | A-034 |
| `owner` | guess | One accountable human for the motion. | A-026 |
| `product` | stub | `reign` or `forge`. | - |
| `plays[]` | guess | The stub has one `audience`, `trigger`, `channel`. One playbook covering several buyers needs a list; each play keeps the stub's shapes unchanged, so one trigger per play and every audit record is tied to one reason. A playbook with one play is the stub's shape. | A-030 (A-017 stands until answered) |
| `approval` | stub (empty object) | See below. | - |
| `kill_criteria[]` | stub (empty list) | See below. | - |
| `limits.max_accounts_per_run` | guess | Makes "precision, no spray" enforceable: a run drafts at most this many briefs. | A-010 |
| `audit` | stub (empty object) | See below. | - |

## Each play

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| `play_id` | guess | Names the play in run summaries and approval requests. | A-030 |
| `status`, `not_implemented_reason` | guess | Buyers can be encoded before their trigger is ready, with the reason visible, instead of silently missing. | A-030 |
| `audience.icp_id`, `audience.segment` | stub | Which ICP version and segment the play targets. | - |
| `trigger.type`, `trigger.id` | stub | `regulatory`, `event` or `manual`, and the trigger record in the feed. | - |
| `channel` | stub | `briefing`, `sequence`, `slack` or `unknown`. | A-018 (briefing) |
| `lead_product` | guess | Lets the defense play lead with Forge while the motion is Reign. | A-023 |
| `unconfirmed_applicability` | guess | `hold` or `brief_with_caveat`: what happens when the preflight cannot confirm the rule applies. | A-025, A-028 |
| `outbound_requires_briefing` | guess | Enforces the CEO's "no bank outbound until a briefing is booked, except on a regulatory trigger". | A-009 |
| `claims[]` | guess | The approved product claim ids this play may use (`docs/research/product-claims.json`). | A-029 |
| `routing.lanes`, `routing.do_not_route` | guess | Routes one brief to risk and engineering by title without asking the buyer to pick; keeps it out of a CISO inbox. | A-011, A-032 |

## `approval`

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| (rule) | stub | "`approval` must name a human if `channel` can send." The validator enforces it. | - |
| `principal` | guess | R-17's "named human who authorized this class of action". Goes on every audit record. | A-026 |
| `approvers[]` | guess | Who may approve a send. A decision by anyone else is refused. | A-026 |
| `channels_that_send[]` | guess | Which channels count as sending. `unknown` counts as sending (the strict reading); `slack` is treated as an internal notification. | A-018, A-035 |
| `sender` | guess | `none`: no transport is wired, so an approved request is ready to send, not sent. | A-035 |

## `kill_criteria[]`

The stub: "how CRO stops a motion that goes sloppy". Each entry has `id`, `metric`, `op`, `threshold` and `why`. After every run the metrics are computed from the run summary; if any criterion trips, the kill switch engages and every later run is refused until a named human clears it (`python -m agent.feedback.kill --clear`). Proposed row A-010.

Metrics available: `audit_blocked`, `gate_failed_ratio`, `rejected_ratio`, `held_ratio`, `drafted`.

## `audit`

| Field | Origin | Why it is useful | Row |
|---|---|---|---|
| `rule` | stub | "`audit` should satisfy Reign rule R-17 when the audience is FS". Must be `R-17` when any play targets a financial-services segment. | - |
| `required_for` | guess | `all_segments` (a failed audit write blocks the action everywhere) or `fs_only` (outside financial services a failure is logged as a warning and the action proceeds). | A-007 |
| `sink` | guess | `jsonl`: an append-only local file standing in for a Reign or HubSpot audit store. | A-008 |

## Still unknown

- How Campaign Manager itself stores and serves playbooks.
- Whether "briefing" also means a calendar booking (A-018 leaves booking out).
