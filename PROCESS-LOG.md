# Process Log

Append-only record of decisions, written as they were made. Each entry opens with one or two plain sentences. The structured fields the working contract requires (`AGENTS.md` section 5) sit in the collapsed block under it (see A-001 for why).

IDs: `D` decision, `A` ambiguity, `Q` QA (quality assurance) verdict, `G` GRAA checkpoint (Goal, Reality, Analysis, Action), `R` reversal, `S` scope cut. Times are wall-clock KST (Korea Standard Time) when the entry was written.

## Log

### [D-001] 23:19 · PM · DECISION
Honest timeline first. The operator opened an earlier packet by mistake before the window, said so, and was sent a fresh packet. This window runs 22:50 to 01:50 KST on the fresh packet, and it started at an airport during a layover with the timer already running before any setup.

<details><summary>Structured fields</summary>

**What:** Disclose how the window started, before any other entry.

**Why:** The reviewer should be able to judge the work knowing everything that could have given an advantage or a handicap. The early packet was disclosed at the time; recording it here keeps the log complete.

**Evidence:** Window file in the packet: received 2026-09-24 22:50 KST, clock stops 2026-09-25 01:50 KST. The working contract commit `9f5b8a4` predates this work.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** -

</details>

### [G-001] 23:19 · PM · GRAA
Opening checkpoint. The assignment wants one working, governed agent, not a plan; the foundation is built first and the deep trigger choice comes from the operator.

<details><summary>Structured fields</summary>

**Goal:** Ship option 3: a small agent that turns a regulatory trigger into a short account brief with sources, obeying rule R-17 (audit record before any touch on a financial-services prospect counts, named human approver for anything that sends). Not asked for: a campaign plan, a deck, a blog, real outbound.

**Reality:** Repository holds only the working contract and kit (`9f5b8a4`) and a README. No access to HubSpot, Clay or ZoomInfo. Python 3.11 available. Trigger and buyer choice not yet made (A-002).

**Analysis:** The parts that do not depend on the trigger choice are most of the system: adapters, ICP (ideal customer profile) filter, R-17 audit, approval gate, error log, playbook schema, tests. Building them first means the trigger decision lands on a running pipeline.

**Action:** Build the trigger-agnostic foundation as IPOF (Input, Processing, Output, Feedback) stages with adapter seams, standard-library Python, tests and CI (continuous integration). Do not pick the trigger. Drop anything that needs live tool access.

**Evidence:** `INTAKE-WORKSHEET.md`; all six packet files read.

**Links:** -

</details>

### [A-001] 23:19 · PM · AMBIGUITY
Log entries open with one or two plain sentences and keep the contract's six fields inside a collapsed block, so both the operator's ask and the contract's format hold.

<details><summary>Structured fields</summary>

**What:** The contract asks for an exact process-log entry format; the operator asked for entries a human can read first. Which wins? Options: (a) exact six-field format only; (b) one or two plain sentences, then the six fields verbatim in a collapsed `<details>` block.

**Why:** Both are satisfied: every field is still present in the exact format, and a reader skimming the log gets the decision without expanding anything.

**Evidence:** Packet read in full; register row A-001 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** The reviewer's renderer does not expand `<details>`, or the contract owner rejects the wrapper.

**Links:** G-001

</details>

### [A-002] 23:19 · PM · AMBIGUITY
The trigger and buyer to go deep on is the operator's call and has not arrived yet. The foundation is built so that either choice is a data change.

<details><summary>Structured fields</summary>

**What:** Which trigger and buyer does the artifact go deep on: the bank with SR 26-2 (Federal Reserve model risk guidance) or the biopharma quality org with FDA PCCP (Predetermined Change Control Plan)? Options: (a) bank and SR 26-2; (b) biopharma and FDA PCCP; (c) both.

**Why:** The operator is deciding and the decision arrives separately. Building both would break "pick one, go deep".

**Evidence:** Packet read in full; register row A-002 in `AMBIGUITY-REGISTER.md`.

**Assumption:** Not decided here. The foundation is built trigger-agnostic: triggers, segments and playbooks are data, so either choice is a data change plus one deep brief.

**Reversal trigger:** The operator's decision arrives.

**Links:** G-001

</details>

### [A-003] 23:19 · PM · AMBIGUITY
AI startups and mid-market SaaS are out of the ICP. They are caught by segment and by a list of naming variants, never by the bare word "AI".

<details><summary>Structured fields</summary>

**What:** "Do not include mid-market SaaS" and "Remove [AI startups]" versus an ICP sketch row "AI-native SaaS startups". Include or exclude, and how is "AI startup" detected? Options: (a) keep the row; (b) exclude by segment label only; (c) exclude by segment label plus phrase patterns across naming variations.

**Why:** The CEO notes are explicit and the operator confirmed. Lists get polluted under many labels, so a label-only check would miss "Gen-AI start-up". Bare "AI" is not a pattern because banks and pharma now describe themselves with it.

**Evidence:** Packet read in full; register row A-003 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (c). Excluded by segment and by phrase patterns (AI startup, AI-native, AI-first, GenAI startup, LLM startup, copilot startup, mid-market SaaS and their spelling variants). Bare "AI" never excludes.

**Reversal trigger:** The CEO reinstates the segment, or a regulated enterprise is caught by a pattern (a false positive).

**Links:** G-001

</details>

### [A-004] 23:19 · PM · AMBIGUITY
5,000 employees is a hard floor. Unknown headcount is held for a human, not passed.

<details><summary>Structured fields</summary>

**What:** Is "5k+ employees" a hard floor, and what happens when headcount is unknown? Options: (a) hard floor, unknown passes; (b) hard floor, unknown is held for a human; (c) soft signal.

**Why:** It is in the CEO's own ICP sentence, not only the unvetted Slack notes. Unknown is held rather than passed because the motion is precision, not volume.

**Evidence:** Packet read in full; register row A-004 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** The CRO says headcount is a soft signal, or enrichment coverage of headcount is poor enough that holding starves the motion.

**Links:** G-001

</details>

### [A-005] 23:19 · PM · AMBIGUITY
"Agents in production or about to" is shown as a signal in the brief and flagged when unknown; only an explicit "none" excludes.

<details><summary>Structured fields</summary>

**What:** "Already has agents in production or about to": gate or signal? Options: (a) hard gate; (b) signal shown in the brief, flagged when unknown.

**Why:** This is rarely knowable before a conversation, so a hard gate would drop most real accounts on missing data rather than on evidence.

**Evidence:** Packet read in full; register row A-005 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b). Recorded and flagged, excluded only when enrichment says explicitly "none".

**Reversal trigger:** The CRO says it is a hard gate.

**Links:** G-001

</details>

### [A-006] 23:19 · PM · AMBIGUITY
An account counts as financial services if its segment or industry says so, and unknown counts as financial services.

<details><summary>Structured fields</summary>

**What:** Which accounts count as FS (financial services) for R-17? Options: (a) only the D-SIB / capital markets segment; (b) segment or industry says FS; unknown counts as FS.

**Why:** An FS account misclassified as non-FS would escape a required audit. Treating unknown as FS fails safe.

**Evidence:** Packet read in full; register row A-006 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** A reliable industry code from the system of record.

**Links:** G-001

</details>

### [A-007] 23:19 · PM · AMBIGUITY
The R-17 audit rule is applied to every segment, not only financial services.

<details><summary>Structured fields</summary>

**What:** R-17 says non-FS audit is "recommended, not required". Apply it only to FS or to every segment? Options: (a) FS only; (b) every segment, same fail-closed rule.

**Why:** The operator asked for it. One code path means no classification error can switch the audit off, and the FS flag is still recorded on every record.

**Evidence:** Packet read in full; register row A-007 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** A throughput or storage constraint on non-FS audit.

**Links:** G-001

</details>

### [A-008] 23:19 · PM · AMBIGUITY
Audit records go to a local append-only file behind an interface, standing in for the real Reign or HubSpot store.

<details><summary>Structured fields</summary>

**What:** Where do audit records live? Options: (a) HubSpot timeline events; (b) a Reign audit store; (c) a local append-only JSONL (JSON Lines) file behind an interface.

**Why:** No live access in the window. The interface keeps the write-before-complete rule independent of the store.

**Evidence:** Packet read in full; register row A-008 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (c) now, with (a) or (b) as the production sink behind the same interface

**Reversal trigger:** Access to the real Reign audit store or HubSpot.

**Links:** G-001

</details>

### [A-009] 23:19 · PM · AMBIGUITY
Bank outbound is blocked unless a briefing is booked or the trigger is regulatory. This is a preflight rule, not a note.

<details><summary>Structured fields</summary>

**What:** "Do not outbound to the bank until an Executive Assurance Briefing is on the calendar", with a regulatory-trigger exception. How is this enforced? Options: (a) a note in the brief; (b) a preflight rule: bank-segment outbound is blocked unless a briefing is booked or the trigger type is regulatory.

**Why:** A note can be ignored; a rule cannot. The exception is part of the rule.

**Evidence:** Packet read in full; register row A-009 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** The CEO drops the rule.

**Links:** G-001

</details>

### [A-010] 23:19 · PM · AMBIGUITY
Volume is bounded by a per-run account cap and kill criteria, with a kill switch that blocks every run.

<details><summary>Structured fields</summary>

**What:** "40 first meetings" versus "no spray. Precision." How is volume bounded? Options: (a) no cap; (b) a per-run account cap and kill criteria in the playbook, with a kill switch that blocks every run.

**Why:** Makes "precision" enforceable and gives the CRO the stop button the Campaign Manager stub describes.

**Evidence:** Packet read in full; register row A-010 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** The CRO sets a different mechanism.

**Links:** G-001

</details>

### [A-011] 23:19 · PM · AMBIGUITY
Risk and engineering contacts are routed into two lanes by job title, never asked to pick one.

<details><summary>Structured fields</summary>

**What:** "Route them without asking": how do risk and engineering both get reached? Options: (a) ask the buyer; (b) route by title into a risk lane and an engineering lane, same brief, different cover note.

**Why:** The CEO notes forbid making them declare. Title mapping is deterministic and visible.

**Evidence:** Packet read in full; register row A-011 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Evidence that one lane never engages.

**Links:** G-001

</details>

### [A-012] 23:19 · PM · AMBIGUITY
HubSpot, Clay and ZoomInfo each get an adapter interface with a local fixture behind it, ready to swap for the real tool.

<details><summary>Structured fields</summary>

**What:** HubSpot, Clay and ZoomInfo are the stack, but there is no access in the window. What stands in? Options: (a) mock inside the pipeline; (b) adapter interfaces with local fixture implementations, one per tool.

**Why:** Meets the stack where it is and leaves a named seam to wire on day one.

**Evidence:** Packet read in full; register row A-012 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Access is granted.

**Links:** G-001

</details>

### [A-013] 23:19 · PM · AMBIGUITY
Fixture accounts are fictional so the agent never writes invented facts about a real bank or pharma company.

<details><summary>Structured fields</summary>

**What:** Can fixtures use real company names? Options: (a) real names; (b) clearly fictional accounts.

**Why:** Writing invented facts about a real bank or pharma company is exactly the embarrassment the brief warns about.

**Evidence:** Packet read in full; register row A-013 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Real CRM data becomes available.

**Links:** G-001

</details>

### [A-014] 23:19 · PM · AMBIGUITY
The FDA guidance page was not found at two guessed addresses, so its trigger record carries no URL and is marked unverified.

<details><summary>Structured fields</summary>

**What:** The FDA PCCP guidance page was not found at two guessed URLs (both returned 404). What does the trigger record carry? Options: (a) keep the guessed URL; (b) carry no URL and mark the source unverified.

**Why:** Never invent a source. The preflight refuses to build a brief on an unverified source.

**Evidence:** Packet read in full; register row A-014 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** The real URL is read from fda.gov.

**Links:** G-001

</details>

### [A-015] 23:19 · PM · AMBIGUITY
Briefs use the Anthropic API when a key is set and a deterministic template otherwise, so the repository runs from a clean clone.

<details><summary>Structured fields</summary>

**What:** Which model provider, and what happens with no API key? Options: (a) require a key; (b) Anthropic Messages API over the Python standard library when a key is set, deterministic template otherwise.

**Why:** Anyone can run the repository from a clean clone with no key, and CI needs no secret. The provider is one setting.

**Evidence:** Packet read in full; register row A-015 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** A requirement to use a different provider.

**Links:** G-001

</details>

### [A-016] 23:19 · PM · AMBIGUITY
Playbooks carry a version and the version they supersede, and every audit record names both.

<details><summary>Structured fields</summary>

**What:** How do playbooks version? (stub says unknown) Options: (a) no versioning; (b) a semantic `version` plus `supersedes`, and every audit record carries playbook id and version.

**Why:** An auditor needs to know which rules were in force for a given touch.

**Evidence:** Packet read in full; register row A-016 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Campaign Manager already has a versioning scheme.

**Links:** G-001

</details>

### [A-017] 23:19 · PM · AMBIGUITY
One playbook has one trigger, as the stub's shape already says.

<details><summary>Structured fields</summary>

**What:** Can one playbook have many triggers? (stub says unknown) Options: (a) one; (b) many.

**Why:** Keeps each audit record tied to one reason. Changing a known field's shape is riskier than keeping it.

**Evidence:** Packet read in full; register row A-017 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (a). The stub shape `trigger: {type, id}` is kept. Reuse comes from parameters, not from bundling triggers.

**Reversal trigger:** Campaign Manager owners confirm multi-trigger playbooks.

**Links:** G-001

</details>

### [A-018] 23:19 · PM · AMBIGUITY
"Briefing" means a brief pack handed to a named human who may forward it, so it counts as able to send and needs an approver.

<details><summary>Structured fields</summary>

**What:** What does "briefing" mean as a channel? (stub says unknown) Options: (a) a calendar booking; (b) a Reign-produced brief pack handed to a named human who may forward it; (c) both.

**Why:** Matches "a brief that a CAE (chief audit executive) can forward". Treating it as sending is the stricter reading.

**Evidence:** Packet read in full; register row A-018 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b). Treated as able to send, because the brief is meant to be forwarded, so it needs a named approver. Calendar booking is out of scope.

**Reversal trigger:** Campaign Manager defines briefing differently.

**Links:** G-001

</details>

### [A-019] 23:19 · PM · AMBIGUITY
Semiconductor accounts are in only with recorded US export-control exposure.

<details><summary>Structured fields</summary>

**What:** Semiconductor is in the ICP only "if they have a US export-control problem". Options: (a) include all semiconductor; (b) include only with export-control exposure recorded.

**Why:** Literal reading of the CEO notes.

**Evidence:** Packet read in full; register row A-019 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** CEO widens it.

**Links:** G-001

</details>

### [A-020] 23:19 · PM · AMBIGUITY
Hospitals are excluded this month; biopharma quality orgs stay in.

<details><summary>Structured fields</summary>

**What:** "Do not spray hospitals this month". Options: (a) exclude hospitals; (b) ignore.

**Why:** Plain instruction; low cost.

**Evidence:** Packet read in full; register row A-020 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (a), as an exclusion. Biopharma quality orgs are a different segment and stay in.

**Reversal trigger:** The month rolls over.

**Links:** G-001

</details>

### [A-021] 23:19 · PM · AMBIGUITY
The unvetted "no risk committee, no briefing" rule is a flag in the brief, not a gate.

<details><summary>Structured fields</summary>

**What:** Rob: "if they do not have a risk committee we are wasting the briefing" (unvetted Slack). Options: (a) hard gate; (b) flag in the brief.

**Why:** Unvetted, and it is a signal about briefing value, not eligibility.

**Evidence:** Packet read in full; register row A-021 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Rob or the CEO confirms it as a rule.

**Links:** G-001

</details>

### [A-022] 23:19 · PM · AMBIGUITY
The unvetted "Canada federal" segment is not added.

<details><summary>Structured fields</summary>

**What:** "Also Canada federal" (unvetted Slack). Options: (a) add a Canadian federal government segment; (b) do not add.

**Why:** No owner, no buyer, no trigger. Adding it would be spray.

**Evidence:** Packet read in full; register row A-022 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b), deferred

**Reversal trigger:** An owner and a trigger for it.

**Links:** G-001

</details>

### [A-023] 23:19 · PM · AMBIGUITY
Defense supplier messaging leads with Forge and mentions assurance, per the CEO's last word.

<details><summary>Structured fields</summary>

**What:** Defense supplier: "Forge-first, Reign later ... lead with the substrate story". Options: (a) lead with Reign; (b) segment config says lead with Forge, mention assurance.

**Why:** The CEO's last word on it.

**Evidence:** Packet read in full; register row A-023 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Rob says otherwise.

**Links:** G-001

</details>

### [A-024] 23:19 · PM · AMBIGUITY
R-17 covers scoring, enriching, creating and messaging steps in the pipeline; reading a record is not covered.

<details><summary>Structured fields</summary>

**What:** Which pipeline steps are R-17 actions? Options: (a) sending only; (b) create, update, enrich, score and message, as the rule lists.

**Why:** The rule lists these verbs; the operator's research confirmed the scope is broader than sending.

**Evidence:** Packet read in full; register row A-024 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b). ICP filter = score; attaching enrichment = enrich; brief and approval request = create; send = message (never executed here). Reading a record is not an R-17 action.

**Reversal trigger:** The rule owner says reads count too.

**Links:** G-001

</details>

### [A-025] 23:19 · PM · AMBIGUITY
When the preflight cannot tell whether a trigger applies to an account, the account is held for a human instead of briefed.

<details><summary>Structured fields</summary>

**What:** When the preflight cannot tell whether a trigger applies to an account, what happens? Options: (a) write the brief anyway; (b) hold for a human, with the reason.

**Why:** A wrong "this rule applies to you" brief sent to a bank is the embarrassment case.

**Evidence:** Packet read in full; register row A-025 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** Operator prefers a caveated brief.

**Links:** G-001

</details>

### [A-026] 23:19 · PM · AMBIGUITY
The demo's named principal and approver is the candidate, who is the operator in this exercise, rather than an invented person.

<details><summary>Structured fields</summary>

**What:** Who is the named principal and approver in the runnable demo? Options: (a) a made-up name; (b) the candidate, who is the operator in this exercise.

**Why:** The assignment says "You are the operator". Using a real, accountable person avoids inventing one.

**Evidence:** Packet read in full; register row A-026 in `AMBIGUITY-REGISTER.md`.

**Assumption:** (b)

**Reversal trigger:** A real approver roster.

**Links:** G-001

</details>

### [D-002] 23:19 · PM · DECISION
Scope tiers are set: the runnable governed pipeline, the audit rule, the approval gate and the write-ups are Must; live connectors are Could; any real send is Won't.

<details><summary>Structured fields</summary>

**What:** MoSCoW (Must, Should, Could, Won't) tiering as in `INTAKE-WORKSHEET.md` section 5.

**Why:** The knockouts are "no artifact" and "ignored the Reign constraint", so the runnable pipeline and R-17 are Must. Live connectors need access we do not have.

**Evidence:** `INTAKE-WORKSHEET.md` section 5.

**Assumption:** none

**Reversal trigger:** Tool access granted during the window moves a connector from Could to Should.

**Links:** G-001

</details>

### [D-003] 23:19 · RESEARCH · DECISION
Regulator pages were fetched rather than recalled. SR 26-2 and both OSFI (Office of the Superintendent of Financial Institutions) guideline pages resolve; the FDA PCCP guidance page was not found at two guessed addresses.

<details><summary>Structured fields</summary>

**What:** Source check for the candidate triggers the trigger records will carry.

**Why:** A brief "with sources" is only as good as its URLs. Recalled URLs are not sources.

**Evidence:** `curl` of `https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm` returned 200, title "Supervisory Letter SR 26-2 on Revised Guidance on Model Risk Management -- April 17, 2026"; page text: "expected to be most relevant to banking organizations with over $30 billion in total assets" and "supersedes and replaces SR letter 11-7 ... and SR letter 21-8". OSFI E-23 and B-13 guidance pages returned 200. Two guessed fda.gov PCCP URLs returned 404.

**Assumption:** SR 26-2 applicability is soft ("expected to be most relevant"), so the preflight treats asset size as a relevance signal plus jurisdiction, not a legal test.

**Reversal trigger:** The FDA page is located (A-014), or the letter's attachment defines scope more tightly.

**Links:** A-014, A-025

</details>

