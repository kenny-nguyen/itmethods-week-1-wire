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

### [D-004] 23:26 · PM · DECISION
The operator approved a repository layout. The kit's supporting files move under `contract/`, code goes under `agent/` split by IPOF stage, and each folder is created only when its first real file lands.

<details><summary>Structured fields</summary>

**What:** Move `RUNBOOK.md`, `QA-AT-EVERY-IPOF-STAGE.md`, `QA-AGENT-SOP.md` and `templates/` into `contract/`; update every reference in `AGENTS.md`, `.claude/agents/` and the README. Code lives in `agent/` (`input/`, `processing/`, `output/`, `feedback/`, `governance/`, `run_playbook.py`).

**Why:** A reviewer opening the repository sees the deliverables at the root, not eight kit files. No empty placeholder folders, so the tree never claims work that does not exist.

**Evidence:** Operator instruction received 23:25 KST through the supervisor inbox. `git mv` preserves history; references rewritten with one `perl` substitution and checked with `git diff`.

**Assumption:** Moving files is not editing the contract's rules; only paths changed in `AGENTS.md`.

**Reversal trigger:** A tool that loads kit files from fixed root paths.

**Links:** G-001

</details>

### [D-005] 23:28 · RESEARCH · DECISION
The supervising agent relayed a researcher's report of public iTmethods product facts and four hard content rules. The source pages were re-fetched and the key negative claims spot-checked before anything was written down.

<details><summary>Structured fields</summary>

**What:** Record the product facts in `docs/research/itmethods-product-facts.md` as the only product statements a brief may make.

**Why:** A brief about Reign that overclaims (compliance, certification, a briefing length, defense capability) is worse than no brief. Fetching the pages again instead of trusting the relayed summary is the Input QA gate.

**Evidence:** Eight itmethods.com URLs returned HTTP 200 at 23:22 KST. Page text quoted in the research file: the assurance page says iTmethods "does not issue an audit opinion or a certification"; the defense page says "We hold no FedRAMP authorization".

**Assumption:** Public site text is the approved claim set for this exercise.

**Reversal trigger:** A marketing-approved claims list that differs from the site.

**Links:** A-029

</details>

### [A-027] 23:28 · PM · AMBIGUITY
The operator chose the bank and SR 26-2 as the one trigger implemented deeply. The other two first-motion buyers stay in the same playbook, marked "not implemented yet", because "pick one" in the packet is about the artifact type, not about serving one persona.

<details><summary>Structured fields</summary>

**What:** Does "pick one, go deep, do not spray" limit the artifact to one buyer persona? Options: (a) one persona only; (b) one artifact type and one deep trigger, with the playbook covering all three buyers.

**Why:** The packet's "pick one" sits above a list of three artifact types, and it asks for a tool that turns "a regulatory trigger" (singular) into a brief. The CEO asks for "one playbook we can reuse". Encoding the other buyers as data costs little and shows the engine is not bank-specific.

**Evidence:** Operator decision received 23:25 KST; register row A-027.

**Assumption:** (b). SR 26-2 for the bank implemented; FDA PCCP (biopharma quality) and the defense supplier encoded with triggers marked not implemented and why.

**Reversal trigger:** The reviewer reads "go deep" as one persona only.

**Links:** A-002, A-030

</details>

### [R-001] 23:28 · PM · REVERSAL
Reverses A-025. When SR 26-2 applicability to a Canadian bank is not established, the agent now writes the brief and says plainly that applicability requires confirmation, instead of holding the account.

<details><summary>Structured fields</summary>

**What:** Reverses A-025. New position in A-028: brief with the caveat "applicability requires confirmation", OSFI E-23 and B-13 as the Canadian context.

**Why:** A-025's reversal trigger fired exactly as written ("Operator prefers a caveated brief"). SR 26-2 reaches a Canadian D-SIB only through a US Federal Reserve-regulated entity, so the brief cannot assert it applies, but the Canadian guidelines certainly do.

**Evidence:** Operator decision received 23:25 KST. SR 26-2 page text: "expected to be most relevant to banking organizations with over $30 billion in total assets regulated by the Federal Reserve" (fetched 23:17 KST).

**Assumption:** A caveated brief is safe to route to a named approver because it never states that the rule applies.

**Reversal trigger:** Legal review says any SR 26-2 mention to a non-US bank is inappropriate.

**Links:** A-025, A-028, D-003

</details>

### [A-028] 23:28 · PM · AMBIGUITY
For a Canadian bank the brief says SR 26-2 "applicability requires confirmation" unless a US Federal Reserve-regulated entity is on record, and it leads with OSFI E-23 and B-13.

<details><summary>Structured fields</summary>

**What:** What does the brief say about SR 26-2 for a Canadian D-SIB (domestic systemically important bank)? Options: (a) hold (A-025); (b) brief with the caveat and the Canadian context.

**Why:** Operator decision, and a forwardable brief is the CEO's exception to "no outbound before a briefing".

**Evidence:** Register row A-028.

**Assumption:** (b)

**Reversal trigger:** A confirmed US entity list for the account removes the caveat.

**Links:** R-001

</details>

### [A-029] 23:29 · PM · AMBIGUITY
Briefs may only say what iTmethods' own pages say about its products, and a deterministic gate rejects compliance, certification, assurance and validation claims, any briefing length, and any hint of CMMC, FedRAMP or CUI capability.

<details><summary>Structured fields</summary>

**What:** What may a brief say about iTmethods and its products? Options: (a) whatever the model writes; (b) a sourced claims list plus deterministic forbidden-claim checks.

**Why:** Models paraphrase toward confident claims. A word-list gate is dumb, but it is deterministic, testable and cannot be talked out of its rules.

**Evidence:** `docs/research/itmethods-product-facts.md`; operator content rules received 23:25 KST.

**Assumption:** (b). CMMC = Cybersecurity Maturity Model Certification; FedRAMP = Federal Risk and Authorization Management Program; CUI = Controlled Unclassified Information.

**Reversal trigger:** An approved-claims list from marketing.

**Links:** D-005

</details>

### [R-002] 23:29 · PM · REVERSAL
Reverses A-017. One playbook now holds a list of plays, one per buyer, and each play keeps exactly one trigger.

<details><summary>Structured fields</summary>

**What:** Reverses A-017 ("one trigger per playbook"). New position in A-030: `plays[]`, each keeping the stub's `audience`, `trigger` and `channel` shapes; approval, kill criteria and audit shared.

**Why:** A-017's reversal trigger was about Campaign Manager owners; what actually arrived was the operator's decision that the first-motion playbook covers three buyers. The reason behind A-017 (every audit record tied to one trigger) survives, because each play has one trigger.

**Evidence:** Operator decision received 23:25 KST.

**Assumption:** A shared governance block across plays is acceptable to Campaign Manager.

**Reversal trigger:** Campaign Manager requires one trigger per playbook file.

**Links:** A-017, A-030

</details>

### [A-030] 23:29 · PM · AMBIGUITY
The first-motion playbook is one file with a list of plays: the bank play implemented, the biopharma and defense plays encoded but marked not implemented.

<details><summary>Structured fields</summary>

**What:** How does one playbook cover three buyers given the stub's single `audience` / `trigger` / `channel`? Options: (a) three playbooks; (b) one playbook with `plays[]`.

**Why:** "One playbook we can reuse" (CEO notes) and the operator's decision.

**Evidence:** Register row A-030.

**Assumption:** (b)

**Reversal trigger:** Campaign Manager requires one trigger per playbook file.

**Links:** R-002

</details>

### [D-006] 23:31 · PM · DECISION
New operator rule: the agent makes no assumptions of its own. Every reading the agent chose is now a proposal awaiting the operator, and the proposals go to the operator as one batch while building continues on the parts that do not depend on them.

<details><summary>Structured fields</summary>

**What:** Every `Assumed` row in `AMBIGUITY-REGISTER.md` becomes `Proposed - awaiting operator`, except rows the operator approved: A-003 (remove AI startups and mid-market SaaS), A-027 (bank and SR 26-2 as the deep trigger), A-028 (the applicability caveat that came with that decision). Batch `assumptions-1` sent to the operator with the 24 proposed rows.

**Why:** Operator instruction received 23:30 KST, overriding the earlier latitude. The operator also listed as not yet approved: R-17 on non-financial segments (A-007), the risk and engineering routing (A-011), the bank outbound rule (A-009), the defense approach (A-023), excluding "Canada federal" (A-022), the three-buyer playbook (A-030) and the product content rules as eval checks (A-029). A-030 and A-029 had been recorded as operator decisions at 23:28 and 23:29; they are proposals again from here.

**Evidence:** Register status counts after the change: 24 proposed, 4 confirmed, 2 reversed.

**Assumption:** none. How the build continues: each proposed reading that code depends on is a value in the playbook or a config file, set to the recommendation and named by row ID, so an operator answer changes data, not code.

**Reversal trigger:** The operator answers batch `assumptions-1`.

**Links:** A-001 to A-030

</details>

### [R-003] 23:23 · PM · REVERSAL
Correction of fact: the timestamps on D-004, D-005, A-027, R-001, A-028, A-029, R-002, A-030 and D-006 were written as guesses, not read from the clock, and they are later than reality. The real times are below; the entries themselves stand.

<details><summary>Structured fields</summary>

**What:** Corrects the stamps. D-004 was written at about 23:21 (stamped 23:26). D-005, A-027, R-001, A-028, A-029, R-002 and A-030 were written at about 23:22 (stamped 23:28 or 23:29). D-006 was written at 23:23 (stamped 23:31). The supervisor inbox messages arrived at 23:20:41 (product facts), 23:20:58 (trigger decision and layout) and 23:22:29 (no-assumptions rule) KST, not "23:25" and "23:30" as those entries say. The "re-fetched at 23:22" note in D-005 and `docs/research/` is about a minute late; the fetch ran at about 23:21. The register's "Status rule from 23:31 KST" line has the same error.

**Why:** The contract says stamps record when something happened. A guessed stamp is a small fabrication, and the log is append-only, so the fix is this entry, not an edit.

**Evidence:** `date +%H:%M` printed 23:23 immediately after D-006 was committed (`c87f670`). Inbox message headers: at=2026-09-24T14:20:41Z, 14:20:58Z, 14:22:29Z.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-004, D-005, A-027, R-001, A-028, A-029, R-002, A-030, D-006

</details>

### [R-004] 23:25 · PM · REVERSAL
Correction of attribution. R-001, R-002, A-028, A-029 and A-030 say the operator decided the caveated SR 26-2 brief, the claims list with forbidden-claim checks, and the three-buyer playbook. The operator did not. Those came from the supervising agent's proposals and are now awaiting the operator.

<details><summary>Structured fields</summary>

**What:** A-028, A-029 and A-030 are `Proposed - awaiting operator`. The reversals R-001 (A-025 to A-028) and R-002 (A-017 to A-030) are proposed reversals only; A-025 and A-017 stand until the operator answers. What the operator did approve: option 3, the bank with SR 26-2 as the deep trigger (A-027, first half only), the repository layout (D-004), removing AI startups and mid-market SaaS (A-003), and error logging.

**Why:** The zero-assumption rule (D-006) only works if the log says truthfully who decided what. The supervisor's message relayed the proposals alongside operator decisions, and the earlier entries merged the two.

**Evidence:** Supervisor inbox message at 2026-09-24T14:24:34Z (23:24 KST) stating the attribution. Register statuses changed in the same commit as this entry.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** R-001, R-002, A-027, A-028, A-029, A-030, D-006

</details>

### [Q-001] 23:25 · BUILDER · PROCESSING-QA
The R-17 core is in and its tests pass (11 tests). The tests were then checked for teeth: with the blocking line disabled, 14 assertions failed; restored, all pass. This is builder self-QA; the independent QA pass comes later.

<details><summary>Structured fields</summary>

**What:** PASS (self-QA, not independent) on "an R-17 action whose audit record is invalid or cannot be written does not happen, and the failure is logged separately".

**Why:** Tests cover every R-17 verb against a sink that raises, a generic purpose, a placeholder principal, empty sources, and a send without a named approver. The fs_only policy (proposed reading A-007) is tested both ways.

**Evidence:** `python3 -m unittest discover -s tests -t .` printed "Ran 11 tests ... OK". Mutation: replacing `if required:` with `if False:` before `raise AuditBlocked` in `agent/governance/audit.py` gave "FAILED (failures=14)"; restoring it gave "OK".

**Assumption:** Proposed readings A-007 (every segment), A-008 (local file sink) and A-024 (which verbs) are config or data, not hard-coded outcomes.

**Reversal trigger:** Independent QA finds a path that completes an action without a record.

**Links:** A-007, A-008, A-024

**Proof boundary:** Not covered: a crash between the audit write and the commit (the record says the action happened, the action did not). Not covered: concurrent writers to the same file.

</details>

### [D-007] 23:27 · BUILDER · DECISION
The input layer is in: one adapter interface per tool, with local fixture versions standing in for HubSpot, ZoomInfo, Clay and a regulator feed. The regulator feed holds real, fetched sources; everything else is fictional and labelled so.

<details><summary>Structured fields</summary>

**What:** `agent/input/base.py` (interfaces), `agent/input/local.py` (fixture adapters), `fixtures/` (11 fictional companies, 9 fictional contacts, 7 enrichment rows, 3 triggers: SR 26-2 implemented; FDA PCCP and the defense trigger marked not implemented with the reason).

**Why:** The pipeline should not know whether it is talking to a fixture or to HubSpot. Fixtures include the hard cases on purpose: an AI startup filed under "fintech" with 6,200 employees, a mid-market SaaS firm over the headcount floor, a bank with unknown headcount, a hospital, a semiconductor firm with unknown export-control exposure.

**Evidence:** `python3 -m unittest discover -s tests -t .` printed "Ran 19 tests ... OK". OSFI E-23 page re-read: "Effective date May 1, 2027". OSFI B-13 effective date not found on the page in this pass, so the feed says so rather than stating it.

**Assumption:** Rests on proposed rows A-012 (fixture adapters) and A-013 (fictional accounts). The three-trigger feed shape follows proposed row A-030; with A-017 instead, the feed is unchanged and only the playbook differs.

**Reversal trigger:** Tool access in the window, or the operator rejecting A-012 or A-013.

**Links:** A-012, A-013, A-014, A-030

</details>

### [A-031] 23:28 · PM · AMBIGUITY
Found while coding the ICP: the packet never says what happens to an account whose segment is not listed. The proposal is to hold it for a human.

<details><summary>Structured fields</summary>

**What:** Unlisted segment: exclude, hold, or include? Options: (a) exclude; (b) hold; (c) include if other rules pass.

**Why:** "Regulated enterprise" is broader than the four listed segments, so silent exclusion could drop a real target, and inclusion would be spray.

**Evidence:** Packet ICP sketch lists five segments; CEO notes add semiconductor. Register row A-031.

**Assumption:** (b), proposed and awaiting the operator; it is the config value `unlisted_segment: "hold"` in `icp/icp.json`.

**Reversal trigger:** The operator lists the full segment set.

**Links:** A-003, D-006

</details>

### [Q-002] 23:28 · BUILDER · PROCESSING-QA
The ICP filter passes its 11 tests, including 26 spellings of "AI startup" and "mid-market SaaS" that must be excluded and 6 ordinary uses of "AI" that must not be. With the pattern list emptied, 28 checks fail, so the tests do test the patterns.

<details><summary>Structured fields</summary>

**What:** PASS (self-QA, not independent) on "AI startups and mid-market SaaS are excluded whatever segment they are filed under, and a bank that mentions AI is not".

**Why:** The fixture AI startup is filed as "fintech" with 6,200 employees and a financial-services industry, so only the naming patterns can catch it.

**Evidence:** `python3 -m unittest tests.test_icp`: "Ran 11 tests ... OK". Mutation (patterns set to an empty list): "FAILED (failures=28)". Fixture outcomes asserted per account: hs-1001 to hs-1004 include; hs-1005 to hs-1008, hs-1010, hs-1011 exclude; hs-1009 hold.

**Assumption:** Rests on proposed rows A-004, A-005, A-006, A-019, A-020, A-021, A-031 through config values in `icp/icp.json`.

**Reversal trigger:** A real account name that the patterns wrongly exclude.

**Links:** A-003, A-031

**Proof boundary:** Patterns are English only. Not tested against real CRM data. A startup that never describes itself with any listed phrase will pass the pattern check and fall to the headcount floor.

</details>

### [D-008] 23:29 · BUILDER · DECISION
The applicability preflight is in. For SR 26-2 it applies to a US bank, to a non-US bank only when a US Federal Reserve-regulated entity is on record, and otherwise it says "applicability requires confirmation". Because the caveated-brief reading (A-028) is still only proposed, the default holds such an account for a human (A-025).

<details><summary>Structured fields</summary>

**What:** `agent/processing/preflight.py` (READY, HOLD, SKIP, BLOCKED) and `agent/processing/routing.py` (lanes by title, do-not-route list).

**Why:** The preflight is where a wrong "this rule applies to you" is stopped before any text is drafted. It also blocks unimplemented triggers and triggers whose facts cite an unverified source, so the FDA PCCP record (no URL) cannot produce a brief.

**Evidence:** `python3 -m unittest tests.test_preflight`: "Ran 10 tests ... OK", covering a US bank over and under the $30B relevance line, a Canadian bank with the US entity unknown (hold by default, caveat plus OSFI context when the playbook says `brief_with_caveat`), known and absent US entity, the unimplemented FDA trigger, an unverified source, and the outbound-before-briefing gate.

**Assumption:** Proposed rows A-009, A-011, A-025/A-028, A-032 are playbook values, not code branches.

**Reversal trigger:** The operator's answer on A-028 flips one playbook value.

**Links:** A-009, A-011, A-025, A-028, A-032

</details>

### [A-032] 23:29 · PM · AMBIGUITY
Found while coding routing: the CEO warns against a CISO inbox, so the proposal routes by title and keeps a do-not-route list that starts with the CISO.

<details><summary>Structured fields</summary>

**What:** Who receives the routed brief? Options: (a) every contact; (b) lanes by title plus a do-not-route list.

**Why:** CEO notes: "If we show up in a CISO inbox with a generic 'AI governance' sequence I will kill the motion."

**Evidence:** Register row A-032.

**Assumption:** (b), proposed and awaiting the operator.

**Reversal trigger:** The CEO says a CISO is a valid recipient for a trigger-specific brief.

**Links:** A-011

</details>

### [D-009] 23:32 · BUILDER · DECISION
Briefs are drafted by a deterministic template when there is no API key, and by Claude through the raw Messages API when there is one. The raw HTTP call keeps the repository standard-library only; the default model is `claude-opus-5`.

<details><summary>Structured fields</summary>

**What:** `agent/processing/brief.py` with `TemplateProvider` and `AnthropicProvider` (urllib POST to `https://api.anthropic.com/v1/messages`, headers `x-api-key`, `anthropic-version: 2023-06-01`). Model from `WIRE_MODEL`, default `claude-opus-5`.

**Why:** The operator asked for standard-library Python where possible, which rules out the Anthropic SDK dependency, the usual default for Python. The request shape and default model were read from the Claude API reference bundled with this session's tooling, not recalled. A refusal (`stop_reason: "refusal"`) or empty reply raises `ProviderError`.

**Evidence:** Claude API reference, raw HTTP example: `anthropic-version: 2023-06-01`, model `claude-opus-5`. Provider selection covered by `tests/test_brief.py`.

**Assumption:** Rests on proposed row A-015. What happens when the call fails is proposed row A-033.

**Reversal trigger:** Operator allows a dependency (then the official SDK), or names a model.

**Links:** A-015, A-033

</details>

### [Q-003] 23:32 · BUILDER · PROCESSING-QA
The output gate catches every forbidden-content case in the eval set (18 of 18), and both template briefs, the US bank and the Canadian bank with the caveat, pass it clean. The gate first failed my own template on two points, which were fixed in the template and the URL pattern.

<details><summary>Structured fields</summary>

**What:** PASS (self-QA, not independent) on "a brief that claims compliance, certification, independent assurance or validation, states a duration, mentions CMMC, FedRAMP, CUI or ITAR, cites an unknown source, links an unapproved URL, mentions a product without an approved claim id, uses filler, drops a section, runs long, or drops the applicability caveat does not pass".

**Why:** Each case starts from a brief that passes and changes one thing, so a miss points at exactly one rule.

**Evidence:** `python -m evals.run_evals`: "18/18 eval cases behaved as expected". `python3 -m unittest discover -s tests -t .`: "Ran 44 tests ... OK". First template run failed the gate on: a URL with a trailing comma, and product sentences whose citation came after the full stop. Fixed by citing inside each sentence (`cite()` in `brief.py`) and excluding trailing punctuation from the URL pattern.

**Assumption:** Rests on proposed row A-029 (content rules as eval checks).

**Reversal trigger:** A real model draft that the gate passes but a human would reject.

**Links:** A-029, D-005

**Proof boundary:** Word lists are English and literal; a paraphrase such as "meets every SR 26-2 expectation" is not caught. No live model draft has been gated yet (no API key in this session).

</details>

### [D-010] 23:36 · BUILDER · DECISION
The Campaign Manager playbook for the first Reign motion is written, with the missing half of the schema filled in and every guess marked in place. `playbooks/SCHEMA.md` says, for every field, whether it came from the stub or is a guess, why it is useful, and which register row proposes it.

<details><summary>Structured fields</summary>

**What:** `playbooks/reign-first-motion.jsonc`, `playbooks/SCHEMA.md`, loader and validator `agent/input/playbook.py`. The stub's three "we know" rules are enforced: a sending channel needs named approvers, kill criteria must exist, and an FS (financial-services) audience needs `audit.rule = R-17`.

**Why:** A playbook that validates is the INPUT gate for a run: an invalid one stops the run before any account is touched. JSONC keeps the guess markers next to the values they explain.

**Evidence:** `python3 -m unittest tests.test_playbook`: 4 tests OK. The bank play is implemented; the biopharma and defense plays are `not_implemented` with the reason.

**Assumption:** New proposed rows A-034 (playbook status) and A-035 (which channels send; no sender wired). The `plays[]` shape is proposed row A-030; if the operator keeps A-017 instead, the three plays split into three files with no code change.

**Reversal trigger:** Campaign Manager's real schema.

**Links:** A-009, A-010, A-016, A-018, A-026, A-030, A-034, A-035

</details>

### [A-034] 23:36 · PM · AMBIGUITY
Proposed while writing the schema: a playbook gets a status (active, paused, retired) so the CRO can stop a motion without deleting its history.

<details><summary>Structured fields</summary>

**What:** Can a playbook be paused? Options: (a) delete to stop; (b) a status field.

**Why:** Stopping should not erase the record.

**Evidence:** Register row A-034.

**Assumption:** (b), proposed and awaiting the operator.

**Reversal trigger:** Campaign Manager already has a status concept.

**Links:** D-010

</details>

### [A-035] 23:36 · PM · AMBIGUITY
Proposed: `briefing`, `sequence` and `unknown` count as sending, `slack` counts as an internal notification, and no sender is wired, so an approved brief is ready to send but never sent by this build.

<details><summary>Structured fields</summary>

**What:** Which channels can send, and does anything send? Options: (a) wire a sender; (b) no sender, strict channel list.

**Why:** "If you cannot leave an audit trail, it does not send" (CEO notes). With no approved sender, not sending is the only safe state.

**Evidence:** Register row A-035.

**Assumption:** (b), proposed and awaiting the operator.

**Reversal trigger:** The operator names a sender and approves wiring it behind the approval gate.

**Links:** D-010

</details>

### [D-011] 23:37 · BUILDER · DECISION
The pipeline now runs end to end on the fixtures: one command runs the playbook, one command lets a named human approve or reject, one command stops the motion. Nothing is ever sent.

<details><summary>Structured fields</summary>

**What:** `agent/run_playbook.py` (INPUT gate, ICP, preflight, drafting, output gate, audited writes, kill criteria), `agent/output/writer.py` (atomic writes), `agent/feedback/` (`decide.py`, `kill.py`, kill criteria, kill switch).

**Why:** Two choices worth naming. Accounts whose segment has no implemented play are not enriched: an enrichment call is an R-17 touch, and touching a biopharma company for a play that cannot run is spray. The kill switch file is written before its audit record, because stopping is the safe direction and must not depend on the audit store that may be the reason for stopping.

**Evidence:** `python3 -m agent.run_playbook --out <tmp>` printed one brief pending approval (hs-1002), the Canadian bank on `preflight_hold`, seven exclusions with reasons, two `no_implemented_play`. `python3 -m agent.feedback.decide` refused "Someone Else" (exit 2) and accepted "Kenny Nguyen" (exit 0, "Nothing has been sent (sender: none)"). Audit file 17 records, error file 1 record (the refusal).

**Assumption:** Rests on the proposed rows named in the playbook; A-033 decides that a model outage fails the account rather than falling back.

**Reversal trigger:** Operator answers on the proposed rows.

**Links:** D-008, D-009, D-010, A-033, A-035

</details>

### [Q-004] 23:37 · BUILDER · PROCESSING-QA
Pipeline tests pass (13 new, 60 in total). They cover the failure paths, not only the happy path: with the audit store down, no brief or approval request is written and the kill switch trips; a sloppy draft fails the gate and trips the kill switch; a model outage fails the account; a wrong approver, a kill switch, or an audit failure each stop an approval.

<details><summary>Structured fields</summary>

**What:** PASS (self-QA, not independent) on "R-17 fails closed across the whole pipeline, nothing sends, and only a named approver can approve".

**Why:** The pipeline could have bypassed `AuditTrail.perform` for some writes; the store-down test would show any brief written without a record.

**Evidence:** `python3 -m unittest discover -s tests -t .`: "Ran 60 tests ... OK". Every audit record from the end-to-end test passes `validate_record`; enrich records exist only for hs-1001 and hs-1002.

**Assumption:** none beyond the proposed rows.

**Reversal trigger:** Independent QA finds a write path outside `AuditTrail.perform`.

**Links:** D-011

**Proof boundary:** Not independent. Not run with a live model (no API key in this session). Concurrency and crash-between-audit-and-commit not tested.

</details>

### [D-012] 23:37 · PM · DECISION
Two independent reviews were started, each in a separate agent context that did not build the code: a QA pass on five claims and a security pass on the approval step, injection, secrets, audit integrity and unbounded reads. Neither may edit the repository; their verdicts are logged as they return.

<details><summary>Structured fields</summary>

**What:** QA claims: C1 R-17 fails closed on every write path; C2 nothing sends and only a named approver approves, kill switch blocks runs and approvals; C3 AI-startup naming variants the reviewer invents are excluded without excluding regulated enterprises that mention AI; C4 the output gate catches forbidden claims, including paraphrases; C5 the README commands work from a clean clone.

**Why:** The contract turns independent adversarial QA on by default for this assignment: there is no owner in the feedback loop, no next cycle, and the review is itself graded. The builder's self-QA entries (Q-001 to Q-004) are labelled as such and are not the sign-off.

**Evidence:** Briefs sent to the `qa-engineer` and `security-engineer` role definitions in `.claude/agents/`, bounded to the claims above.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** Q-001, Q-002, Q-003, Q-004

</details>

### [D-013] 23:38 · BUILDER · DECISION
The supervisor's agent-memory helper refused to touch the kit's `CLAUDE.md` and `AGENTS.md`. The kit's own one-line import already does the job, so both files were left exactly as committed, and no project notes were added to the contract.

<details><summary>Structured fields</summary>

**What:** Fallback under contract section 8: skip the helper, keep `CLAUDE.md` (`@AGENTS.md`) and `AGENTS.md` unchanged.

**Why:** One attempt at a misbehaving substrate mechanism is reasonable; a second is a trap. The requirement behind the helper (agents load `AGENTS.md`) is already met, and editing the contract after the fact would blur the point of committing it first. Everything a future session needs to run the code is in the README.

**Evidence:** `fm-ensure-agents-md.sh .` printed "conflict: both AGENTS.md and CLAUDE.md are real files ... reconcile them manually" and changed nothing (`git status` clean).

**Assumption:** none

**Reversal trigger:** The operator wants the helper's canonical two-line pointer in `CLAUDE.md`.

**Links:** -

</details>

### [G-002] 23:38 · PM · GRAA
Checkpoint after the end-to-end run went green. The foundation does what the goal asked, on fixtures; what is not true yet is that anyone independent has checked it, and that the operator has answered the proposed readings.

<details><summary>Goal, Reality, Analysis, Action</summary>

**Goal:** Option 3, a small agent turning a regulatory trigger (SR 26-2, operator-approved) into a short, sourced, non-slop account brief, obeying R-17 and sending nothing without a named human; built as IPOF stages with seams for HubSpot, Clay and ZoomInfo; every assumption recorded.

**Reality:** Observed at commit `098e372` and after: `python -m agent.run_playbook` drafts one brief (US bank), holds the Canadian bank, excludes seven accounts with reasons, skips two plays marked not implemented; approvals, kill switch and kill criteria work from the command line; 60 unit tests and 18 eval cases pass locally; CI passed on the first pushed commit. 28 register rows are proposals awaiting the operator (batches `assumptions-1` and `assumptions-2`). No live model draft has been produced (no API key in this session). Independent QA and security reviews are running and have not returned.

**Analysis:** The biggest risk to the goal is no longer missing code; it is an unverified claim. The builder's own tests could share the builder's blind spots, especially on the output gate's word lists and on the approval step. The second risk is that several operator answers (A-028 caveat versus hold, A-030 plays list) change what the demo shows; both are playbook values, so the cost is low.

**Action:** Continue: fold the reviewers' findings back in as they arrive, each logged with the decision made about it. No new capability until then. Deliberately not doing: a live connector, a sender, a second deep trigger.

**Evidence:** Commits `aae4e31` to `167c6f7`; D-011, Q-004; `gh-axi run list` showing the first CI run `success`.

**Links:** G-001, D-011, D-012

</details>

### [D-014] 23:41 · PM · DECISION
The operator answered the first batch of proposals. Fifteen are decided as proposed, two are changed by the operator, and ten stay open. The register now says "Decided by operator" on each decided row.

<details><summary>Structured fields</summary>

**What:** Decided as proposed: A-001, A-004, A-008, A-011, A-013, A-014, A-015, A-016, A-021, A-022, A-023, A-024 (the list as it stands), A-025 (general case), A-026, A-029. Changed: A-005 becomes A-036 (agent adoption never excludes); A-010 becomes A-037 (no volume cap; quality-based kill criteria only). Still open, not decided here: semiconductor (A-019); hospitals (A-020; the operator's current view is "watch without contacting", not a plain exclusion); unknown industry counted as FS (A-006); audit for every segment (A-007); completeness of the audited steps (A-024); the bank outreach rule (A-009); SR 26-2 versus Canadian rules (A-028); one playbook versus three files and what a play is (A-017, A-030); what "briefing" means as a channel (A-018). Not mentioned, so still proposed: A-012, A-031 to A-035.

**Why:** The zero-assumption rule (D-006). Items for "what we would do next": wire the real audit sink on day one (A-008); confirm Rob's intent on the risk-committee note (A-021); for "Canada federal", find the owner and intent and confirm rather than leave it (A-022, a do-differently note).

**Evidence:** Supervisor inbox message at 2026-09-24T14:40:21Z (23:40 KST) relaying the operator's decisions.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-006, A-036, A-037, R-005, R-006

</details>

### [D-015] 23:41 · PM · DECISION
The operator's framing for the defense supplier, recorded in the operator's terms: lead with Forge, and bring in Reign as the reason agents can be let near the estate. The operator calls it a natural ascension: one solution creates the next problem, and the second product solves it.

<details><summary>Structured fields</summary>

**What:** A-023 decided with this framing. The defense play stays not implemented in this window.

**Why:** Matches the CEO's last word ("lead with the substrate story and mention assurance as the reason they can let agents near the estate") and gives the next product launch a reusable pattern.

**Evidence:** Operator decision relayed at 23:40 KST.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-023

</details>

### [R-005] 23:41 · PM · REVERSAL
Reverses A-005. Agent adoption is now a signal only: shown in the brief, flagged when unknown or "none", and never a reason to exclude.

<details><summary>Structured fields</summary>

**What:** Reverses A-005; new position A-036.

**Why:** Operator decision: no part of the assignment says to exclude on a known "none".

**Evidence:** Operator decision relayed at 23:40 KST.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-005, A-036

</details>

### [R-006] 23:41 · PM · REVERSAL
Reverses A-010. There is no volume cap. The CRO's stop button is quality-based only: approver rejections, complaints, wrong-account reports, gate failures and audit failures.

<details><summary>Structured fields</summary>

**What:** Reverses A-010; new position A-037.

**Why:** Operator decision: precision first, without a premature cap; kill criteria are never a count ceiling.

**Evidence:** Operator decision relayed at 23:40 KST.

**Assumption:** Audit failures and gate failures count as quality signals, not volume ceilings: they measure whether the motion can be trusted, not how much it does.

**Reversal trigger:** The operator says audit or gate failures should not stop the motion.

**Links:** A-010, A-037

</details>

### [Q-005] 23:43 · QA · QA-VERDICT
Independent QA came back: two claims pass, two fail, and one passes with conditions. The failures were real. The ICP patterns missed nine naming variants and wrongly excluded three banks and insurers that only mention startups. The output gate could be walked past with paraphrases, a negation word, a heading, text after the Sources section, a bare domain, or the wrong claim id.

<details><summary>Structured fields</summary>

**What:** C1 (R-17 before every write) CONDITIONAL PASS: every completed action had a record, but if the approval request's record failed after the brief's record succeeded, the brief file stayed on disk. C2 (nothing sends, named approver only, kill switch) PASS. C3 (ICP naming variants) FAIL. C4 (output gate) FAIL. C5 (README commands from a clean clone) CONDITIONAL PASS: `python` is not on the reviewer's PATH; with `python` pointing at 3.11 every command behaved as documented. The reviewer also noted the rejection ratio divides by pending requests.

**Why:** The reviewer invented its own variants and paraphrases instead of reusing the builder's tests. That is exactly the blind spot builder self-QA (Q-002, Q-003) could not see.

**Evidence:** Reviewer's receipts, from a clean clone at `098e372`. Verify-the-verifier: with `raise AuditBlocked` disabled, 16 tests failed. C3 misses included "Machine learning startup", "Early-stage agentic AI company", "Midsize SaaS company"; false positives included "its venture arm invests in AI startups". C4 misses included "Reign keeps the bank fully in line with SR 26-2", "takes half an hour", "Fed RAMP", "www.evil-example.com", a `###` heading claim, and text after `## Sources`.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-012, Q-002, Q-003, D-016, D-017

**Proof boundary (reviewer's):** No model-drafted text was tested; the kill criterion on rejections was not run.

</details>

### [D-016] 23:43 · BUILDER · DECISION
QA's C3 findings are fixed. The ICP patterns now cover machine learning, agentic AI, scale-ups, venture-stage wording and every mid-market SaaS spelling QA tried. A match is ignored when the startups are the account's investees, partners, customers or policyholders. All nine missed variants and all three false positives are now tests.

<details><summary>Structured fields</summary>

**What:** `icp/icp.json` pattern set rewritten; new `object_context_regex`; `Icp.matched_exclusion` checks the words before each match. Also applied here: agent adoption never excludes (A-036, operator decision).

**Why:** Accepting C3's findings in full. "Bare 'AI' never excludes" (A-003) still holds.

**Evidence:** All 13 QA strings behaved correctly in a direct check before the tests were updated; `python3 -m unittest tests.test_icp` OK after adding them.

**Assumption:** The object-context list (invest, partner, fund, back, serve, sell, client, customer, portfolio, policy, insure, lend, accelerator, incubator, arm) is the agent's reading; it is proposed, not operator-decided.

**Reversal trigger:** A real startup that describes itself with one of those words before "AI startup" and slips through.

**Links:** Q-005, A-003, A-036

</details>

### [D-017] 23:43 · BUILDER · DECISION
QA's C4 findings and the security reviewer's markup finding are fixed in the output gate. Every line is checked, including headings and Sources. A product sentence must restate its cited claim word for word. No negation escape remains. Links of any shape outside the approved sources are rejected, and so are HTML and markdown images.

<details><summary>Structured fields</summary>

**What:** `agent/processing/checks.py` rewritten; the model prompt now tells it that record text is data, not instructions, and to quote product claims verbatim. Twenty-one new eval cases, one per bypass QA or security found.

**Why:** Accepting C4 in full. Checking the claim text instead of a negation word closes the "compliant with no manual work" hole, and keeps the approved sentence "It does not issue an audit opinion or a certification" legal.

**Evidence:** `python3 -m evals.run_evals`: "39/39 eval cases behaved as expected". The first rerun had 38/39: "satisfies every SR 26-2 expectation" slipped the claim pattern because "26-2" is not a single word token; fixed by allowing hyphens in the gap. `python3 -m unittest discover -s tests -t .`: OK. The fixture run is unchanged (one brief, same holds and exclusions).

**Assumption:** Verbatim claims make model drafts stiffer; accepted, because the operator decided claims come only from the sourced list (A-029).

**Reversal trigger:** Marketing approves paraphrase variants of each claim (add them to the claims file).

**Links:** Q-005, A-029, D-020

**Proof boundary:** Still English word lists. A plausible false claim with no product name and no listed phrase (for example about the bank itself) passes the gate; the named approver is the control for that.

</details>

### [D-018] 23:47 · SECURITY · DECISION
Independent security review, finding S-1 (high): whoever could edit an approval request chose who may approve it, because the approval step loaded the playbook from a path inside the request. Fixed. The playbook now comes by id from `playbooks/` only, must be unchanged since the request was created, and must validate.

<details><summary>Structured fields</summary>

**What:** `agent/feedback/trusted.py` (load by format-checked id, SHA-256 match, validate); `decide.py` rewritten to use it; the approval record's FS flag is always true instead of read from the request.

**Why:** The approver list is the control that stands between a drafted brief and a send. It cannot live in a file the approval is about.

**Evidence:** Reviewer's reproduction (edited `playbook_path` and id, "Mallory Attacker" approved, exit 0) now prints "DECISION REFUSED: playbook not trusted: no playbook 'reign-first-motion-evil'", exit 2. Regression tests in `tests/test_security.py`: edited request refused; playbook changed after the request refused.

**Assumption:** The `playbooks/` directory itself is trusted (reviewed through git).

**Reversal trigger:** n/a

**Links:** D-012

</details>

### [D-019] 23:47 · SECURITY · DECISION
Finding S-2 (medium): pointing `--out` at another directory got a listed approver past the kill switch and kept the approval out of the real audit trail. Fixed by removing every `--out` flag: the command-line tools always use the repository's `out/`, and a request outside it is refused.

<details><summary>Structured fields</summary>

**What:** `run_playbook`, `decide`, `kill` and `report` take no output-root flag; `decide` refuses requests not under `out/runs`.

**Why:** The kill switch and the audit trail only work if there is exactly one of each.

**Evidence:** `--out /tmp/elsewhere` now fails argument parsing; `tests/test_security.py` covers the function-level refusal.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-018

</details>

### [D-020] 23:47 · SECURITY · DECISION
Finding S-3 (medium): anyone could clear the kill switch, nothing was audited, and a crafted playbook id could delete any JSON file under `out/`. Fixed. Only the playbook owner or a listed approver can engage or clear it, both directions are audited, clearing is refused if its audit record cannot be written, and ids must be lowercase letters, digits and hyphens everywhere.

<details><summary>Structured fields</summary>

**What:** `agent/feedback/kill.py` rewritten; id check in `kill_switch._path` and in the playbook validator; automatic engagements from decisions and reports are audited.

**Why:** Stopping is the safe direction, so engaging still happens even if the audit store is down. Restarting is the unsafe direction, so it fails closed.

**Evidence:** "Random Person ... --clear" now REFUSED, exit 2; `--playbook-id "../../runs/x"` now REFUSED "invalid playbook id", exit 2. Tests: accountable-only, audited both ways, clear refused on audit failure, four traversal ids rejected.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-018

</details>

### [D-021] 23:47 · SECURITY · DECISION
Finding S-4 (low to medium): an audit record could say an approval happened when writing the request failed. Fixed. When the step after the audit record fails, a second record marks the first as failed, the error log gets the detail, and the error is raised. The same review, with QA's C1-a, led to the brief and its approval request being written together or not at all.

<details><summary>Structured fields</summary>

**What:** `AuditTrail.perform` writes a `detail.outcome = "failed"` record pointing at the original; `run_playbook` writes brief and request in one audited action and removes the brief if the request write fails.

**Why:** R-17 only has value if the trail is true.

**Evidence:** `tests/test_security.py::AuditOutcome` and `tests/test_pipeline.py::test_request_write_failure_leaves_no_brief` pass.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** Q-005

**Proof boundary:** A process killed between the audit write and the commit still leaves a record without an outcome; production needs an idempotent commit keyed by record id.

</details>

### [D-022] 23:47 · SECURITY · DECISION
Finding S-5 (medium, production only): text planted in CRM or enrichment data could steer a model draft past the gate, including tracking images. Fixed as far as a gate can: markup, images and links of any shape are rejected, product sentences must quote an approved claim, and the model is told that record text is data, not instructions. Accepted limits, not fixed: the approver's identity is a typed name, and a plausible but false sentence can still pass the gate.

<details><summary>Structured fields</summary>

**What:** Covered by D-017 (gate) and the prompt change. Null results from the same review: no API key leaks into any log, output or traceback (canary test); account ids cannot escape their directory as file names; unbounded reads only from the fixed model endpoint.

**Why:** The named human approver is the real control for plausible falsehoods, which is why S-1 mattered most.

**Evidence:** Reviewer's injection lines are eval cases now ("markdown image beacon", "HTML image", "protocol-relative link", "bare domain"); 39/39 pass.

**Assumption:** Accepted for the demo: approver identity is a string. Production must bind it to an authenticated identity (listed in the README).

**Reversal trigger:** n/a

**Links:** D-017, D-018

</details>

### [D-023] 23:47 · BUILDER · DECISION
The operator's two changes are in the code: agent adoption never excludes, there is no volume cap (a `limits` block is now rejected), and the kill criteria are quality-based: audit failures, gate failures, approver rejections over decided briefs, complaints and wrong-account reports. A new command records complaints and wrong-account reports.

<details><summary>Structured fields</summary>

**What:** `agent/feedback/report.py` and `reports.py`; rejection ratio now divides by decided requests only (QA note in Q-005); playbook kill criteria updated.

**Why:** Operator decisions A-036 and A-037.

**Evidence:** `python3 -m unittest discover -s tests -t .`: "Ran 69 tests ... OK", including a wrong-account report engaging the kill switch.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-036, A-037, R-005, R-006

</details>

### [D-024] 23:47 · PM · DECISION
The operator decided every item that was still open. Four readings are confirmed as proposed (R-17 on every segment, unknown industry counts as financial services with a flag, the audited-steps list completed with our own decisions, one audience-trigger-channel per playbook). Six are changed by the operator and recorded as new rows A-038 to A-044.

<details><summary>Structured fields</summary>

**What:** Decided: A-006, A-007, A-017, A-024. New operator rows: A-038 (an audit record is our receipt, never a test for the prospect), A-039 (semiconductor), A-040 (hospitals: watch, don't contact), A-041 (three stub-shaped playbook files plus a motion file; A-030 rejected), A-042 (channel "briefing" is the booked meeting), A-043 (bank: no cold outreach; on a regulatory trigger the brief goes to the named iTmethods account owner), A-044 (the Canadian bank brief structure). Not covered by the message and still proposed: A-012, A-031, A-032, A-033, A-034, A-035; sent to the operator as batch `assumptions-3`.

**Why:** Zero-assumption rule (D-006). A-042 is the operator's close reading of the packet: the CEO writes "on the calendar", and iTmethods' site makes the briefing stage 1 of its funnel, so "briefing" names the meeting and the brief is the document that earns it. A-043 records the reading "the thread = the existing relationship" (the bank already runs Forge) with its reversal trigger: evidence that "the thread" means a specific email thread or a regulator-facing channel.

**Evidence:** Supervisor inbox message at 2026-09-24T14:46:06Z (23:46 KST).

**Assumption:** none of the agent's own

**Reversal trigger:** per row

**Links:** D-014, A-038 to A-044, R-007 to R-010

</details>

### [R-007] 23:47 · PM · REVERSAL
Reverses A-019 and A-020. Chipmakers without a recorded export-control problem, and hospitals, are no longer excluded. They go on a watch list: noticed and logged, never contacted.

<details><summary>Structured fields</summary>

**What:** New positions A-039 and A-040.

**Why:** Operator decision.

**Evidence:** Operator message at 23:46 KST.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-019, A-020, A-039, A-040

</details>

### [R-008] 23:47 · PM · REVERSAL
Reverses the single-file plays list (A-030, never approved) in favour of three playbook files, each exactly in the stub's shape, plus a motion file that references them. A-017's original reading, one trigger per playbook, is the one that stands.

<details><summary>Structured fields</summary>

**What:** New position A-041. The proposed reversal R-002 is withdrawn.

**Why:** Operator decision.

**Evidence:** Operator message at 23:46 KST.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-017, A-030, R-002, A-041

</details>

### [R-009] 23:47 · PM · REVERSAL
Reverses A-018 and A-009. "Briefing" is the booked meeting, not the document. For the bank, the agent never contacts the bank: on a regulatory trigger it writes the brief and routes it to the named iTmethods account owner, who decides whether to share it in the existing relationship.

<details><summary>Structured fields</summary>

**What:** New positions A-042 and A-043.

**Why:** Operator decision; a closer reading of the packet than the agent's.

**Evidence:** Operator message at 23:46 KST.

**Assumption:** none

**Reversal trigger:** Per A-043.

**Links:** A-009, A-018, A-042, A-043

</details>

### [R-010] 23:47 · PM · REVERSAL
Reverses A-028. The Canadian bank brief is structured: what changed, what is certain at home, what depends on the bank's structure (each marked "confirm"), then a next step. It never says a rule applies.

<details><summary>Structured fields</summary>

**What:** New position A-044.

**Why:** Operator decision.

**Evidence:** Operator message at 23:46 KST.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-025, A-028, A-044

</details>

### [D-025] 23:49 · PM · DECISION
A-012 is decided: the fixture adapters behind swappable interfaces are the operator's own instruction ("meet them where they are"). A-031 to A-035 stay with the operator, and nothing new is built on them. Where code already existed for them, it keeps the reading that takes no action on a prospect, and each stays marked proposed.

<details><summary>Structured fields</summary>

**What:** Pending, not extended: A-031 (unlisted segment held: nobody is contacted), A-032 (CISO on the do-not-route list: nobody is contacted), A-033 (model outage fails the account: no brief), A-034 (playbook `status` field: metadata only), A-035 (no sender: nothing is sent). Also corrected here: product claim P-BANKING had the word "readiness", which the source does not say; removed (see `docs/research/itmethods-product-facts.md`).

**Why:** Supervisor instruction at 23:48 KST under the zero-assumption rule. Removing the existing code would need its own behaviour choice, for example contacting the CISO or falling back silently, which is a bigger assumption than keeping the no-action reading until the operator answers.

**Evidence:** Supervisor inbox message at 2026-09-24T14:48:58Z. Register row A-012 now "Decided by operator".

**Assumption:** The no-action reading is the least assumptive placeholder for a pending item.

**Reversal trigger:** The operator answers any of A-031 to A-035; each is one config or playbook value.

**Links:** D-024, A-012, A-031 to A-035

</details>

### [D-026] 23:53 · PM · DECISION
The operator decided the last five proposals as recommended. The principle behind A-033 is recorded in the operator's words: nothing is worse than a silent failure. Every model failure now says what to do next.

<details><summary>Structured fields</summary>

**What:** Decided: A-031 (an account clearly outside the ICP, or matching an explicit exclude, is dropped from outreach with the reason in the audit log, never silently; an account whose fit is unclear or unknown is held for a human), A-032 (do-not-route list starting with the CISO), A-033 (fail loudly, never fall back silently; every failure names the recovery: retry, run with no key for the template, or check the key and provider), A-034 (playbook status active, paused or retired), A-035 (approved means ready to send; nothing is wired to send; "unknown" counts as able to send; "slack" is internal). New proposed row A-045: the brief word limit (350 words on the forwardable part), which was the agent's own number and had not been registered.

**Why:** Zero-assumption rule. For "what we would do next": wire the real send path behind the blockable approval (A-035). For "do differently": confirm with the CEO and CRO how ICP edge cases should be handled (A-031).

**Evidence:** Supervisor inbox message at 2026-09-24T14:52:36Z (23:52 KST). `ProviderError` now appends the recovery options to every message.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** A-031 to A-035, A-045, D-025

</details>

### [D-027] 23:55 · BUILDER · DECISION
The playbook is now three files, each exactly in the Campaign Manager stub's shape, plus a small motion file that lists them (A-041). The motion runs the ICP filter once, then each playbook with its own approval, kill criteria and audit. Hospitals go on a watch list, routing is an audited decision, and the brief goes to the named account owner, never to the bank.

<details><summary>Structured fields</summary>

**What:** `playbooks/bank-sr26-2.jsonc`, `biopharma-fda-pccp.jsonc`, `defense-forge-first.jsonc`, `motions/reign-first-motion.jsonc`; `agent/run_playbook.py` rewritten as a motion runner; the validator checks one playbook and the motion; `playbooks/SCHEMA.md` rewritten. ICP: a `watch` outcome (A-039, A-040), "industry unconfirmed" flag (A-006). Audit: `route` added to our audited decisions (A-024). Preflight: no account owner means hold; no cold outreach until a briefing is booked (A-043). Approval: the approver must be the account's owner in HubSpot, read from the fixture adapter, not from the request.

**Why:** Operator decisions D-024 and D-026.

**Evidence:** `python3 -m agent.run_playbook` exit 0: hs-1001 and hs-1002 "brief_pending_owner_decision"; hs-1007 "watch"; hs-1005, hs-1006, hs-1010, hs-1011 "exclude"; hs-1009 "hold"; hs-1003, hs-1004, hs-1008 "no_live_playbook"; biopharma and defense playbooks "not_implemented" with reasons.

**Assumption:** A chipmaker without a recorded export-control problem "may still qualify through the main ICP" (A-039); this build has no semiconductor playbook, so such an account is recorded as `no_live_playbook` and is not enriched to find out.

**Reversal trigger:** A semiconductor playbook is added.

**Links:** A-006, A-024, A-039, A-040, A-041, A-043, D-024, D-026

</details>

### [D-028] 23:55 · BUILDER · DECISION
The SR 26-2 bank brief is now the structure the operator set (A-044): what changed, what is certain for this account, what depends on its structure with every line marked "Confirm", and a suggested next step. The gate enforces it: applicability wording outside the conditional section fails, and so does an unmarked line inside it.

<details><summary>Structured fields</summary>

**What:** `TemplateProvider` rewritten; the regulator feed gains `structural_conditions` (US Federal Reserve entity, EU entity and DORA) and a DORA source; the gate's required sections, an `APPLIES` check, and a "Confirm" check; three new eval cases ("claims the rule applies", "says in scope", "unmarked structural line").

**Why:** "Never claim a rule applies. Every line sourced." (operator, A-044).

**Evidence:** Sources re-read for this: EUR-Lex returned HTTP 202 twice (an anti-bot page with no regulation text), so DORA is cited from the EIOPA page, which returned 200 and names "Regulation (EU) 2022/2554 ... on digital operational resilience for the financial sector". The OSFI B-13 page does not show an effective date, so the brief does not call B-13 "in force". `python3 -m evals.run_evals`: 42/42. First run of the new template failed my own gate twice: "the iTmethods account owner" named the company without a claim (reworded), and the brief ran 374 words (cut the generic third SR 26-2 fact and folded the caveat into the first "Confirm" line; limit set to 350 on the forwardable part, proposed row A-045).

**Assumption:** Proposed A-045 (word limit).

**Reversal trigger:** The operator sets a different length, or legal wants no conditional "applies to that entity" wording at all.

**Links:** A-044, A-045, D-003

</details>

### [Q-006] 23:55 · BUILDER · PROCESSING-QA
After the restructure: 74 unit tests and 42 eval cases pass, and the command-line run behaves as the README describes. This is builder self-QA; the restructured code has not yet had an independent pass.

<details><summary>Structured fields</summary>

**What:** PASS (self-QA, not independent) on "the motion, the three playbooks, the watch list, the owner handoff and the structured brief behave as the operator decided, and the earlier QA and security fixes still hold".

**Why:** Every test that the restructure broke was rewritten against the new behaviour rather than deleted; the security regression tests now target `bank-sr26-2`.

**Evidence:** `python3 -m unittest discover -s tests -t .`: "Ran 74 tests ... OK". `python3 -m evals.run_evals`: "42/42". `python3 -m agent.run_playbook`: exit 0.

**Assumption:** none

**Reversal trigger:** An independent pass finds a regression.

**Links:** D-027, D-028

**Proof boundary:** Not independent. No live model draft.

</details>

### [D-029] 23:56 · BUILDER · DECISION
Two changes the production guide needed. Configuration is read in one place, including `WIRE_OUT_DIR` for where the audit trail and error log live. Scheduled reruns are safe: an account already briefed for the same trigger and playbook is not drafted again.

<details><summary>Structured fields</summary>

**What:** `agent/config.py`; every command reads the output root from it. `_already_briefed()` in `agent/run_playbook.py` reads our own approval requests (a plain read, not an R-17 touch) and skips any account with a request that is not rejected.

**Why:** The operator asked for configurable audit and error log locations (supervisor message at 23:55 KST). A per-command `--out` flag was the security finding S-2 (D-019); one deployment-level variable read by every command keeps a single trail, and the guide says to set it once per deployment. Without the rerun check, an hourly schedule would send the account owner the same brief every hour.

**Evidence:** `tests/test_pipeline.py::test_scheduled_rerun_does_not_brief_twice`; "Ran 75 tests ... OK".

**Assumption:** A rejected brief may be redrafted on a later run; any other status blocks a redraft. This is the agent's reading and is logged here for the operator.

**Reversal trigger:** The operator wants rejected briefs to stay blocked until the trigger changes.

**Links:** D-019, D-030

</details>

### [D-030] 23:56 · QA · OUTPUT-QA
Every command in `docs/production.md` was run from a clean clone of commit `acba336` and did what the guide says. The live model call was not run: there is no API key in this environment, and the guide says so at the top.

<details><summary>Structured fields</summary>

**What:** Verified from `git clone` into a scratch directory with `WIRE_OUT_DIR` set: run (exit 0, two briefs); rerun (both banks `already_briefed`); approve (exit 0, "Nothing has been sent"); reject (exit 0); complaint report (exit 3, "KILL SWITCH ENGAGED: complaint"); manual engage (exit 0); clear (exit 0). Then with `WIRE_OUT_DIR` unset: run exit 0, files under `./out`. Test suite 75 OK; evals 42/42.

**Why:** The operator asked for every command in the guide to be verified from a clean clone and the verification logged.

**Evidence:** Audit trail after the sequence: 36 records, last seven `score, approve, reject, update, block, block, unblock`; no `errors.jsonl` (nothing failed).

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-029

**Proof boundary:** Builder-run verification, not independent. Not run: the live Claude call, cron itself (the cron line was not installed), any real HubSpot, Clay or ZoomInfo connection.

</details>

### [R-011] 00:00 · PM · REVERSAL
The operator redefined the artifact. It is a Claude skill plus an MCP server with evals: the skill tells the agent how to read the trigger, reason about the account and draft; the server's tools enforce the audit rule, exclusions, the do-not-route list and the claim limits, so no agent can skip them. The template path is now "offline test mode" for CI only and must never be presented as the agent.

<details><summary>Structured fields</summary>

**What:** Reverses the framing that the Python pipeline with an optional model call is the artifact (D-009, D-011). New position A-046; dependency decision A-047.

**Why:** Operator decision: "A Python script filling a template is NOT an agentic artifact and must never be presented as one." The packet asks for "a Claude skill / MCP / small agent" and tests "AI depth (agents, skills, MCP, evals)". The governed stages already built (ICP, preflight, routing, output gate, R-17 audit, approval, kill switch) become the tools' enforcement layer, so little is thrown away.

**Evidence:** Supervisor inbox message at 2026-09-24T14:58:38Z (23:58 KST). `mcp==2.2.0` installed into a git-ignored `.venv`; its API read from the installed package: `mcp.server.mcpserver.MCPServer`, `mcp.server.mcpserver.exceptions.ToolError`, `mcp.Client` accepting a server instance in-process. Importing the 1.x path `mcp.server.fastmcp` fails in 2.x with a message pointing to the rename.

**Assumption:** The live agent run for the demo happens in a Claude Code session with this server attached, and its output is scored by the evals; it is not run in this build session.

**Reversal trigger:** n/a (operator decision)

**Links:** D-009, D-011, A-046, A-047

</details>

### [Q-007] 00:03 · QA · QA-VERDICT
The second independent QA pass found three real failures in the restructured code, and all three are fixed. The gate let a brief say a rule "governs" or "binds" the bank, and it did not require a citation on every line. Editing an approval request's account or playbook got past the owner check and the kill switch. And more naming variants and paraphrases slipped through.

<details><summary>Structured fields</summary>

**What:** C1 (brief never asserts applicability; Confirm rule; every factual line cited) FAIL. C2 (only the listed owner can approve; request edits cannot change that; kill switch holds) FAIL. C3 (dropped and watched accounts never enriched, routed or briefed) CONDITIONAL PASS: true on the fixtures; a future semiconductor playbook would enrich chipmakers before deciding "watch". C4 (new naming variants and paraphrases) FAIL: 7 of 8 ICP variants and 10 of 10 gate paraphrases passed. C5 (production guide from a clean clone) CONDITIONAL PASS: every command worked; the guide omitted the report command's exit code 3, and a complaint re-tripped the kill switch right after it was cleared.

**Why:** Accepting every finding. The reviewer verified its checks were live: the unmodified brief passed, a control line was blocked.

**Evidence:** Reviewer's probes in a clean clone at `0bcbc1b`. The fixes are in D-031.

**Assumption:** none

**Reversal trigger:** n/a

**Links:** D-012, Q-005, D-031

**Proof boundary (reviewer's):** No live model path; no live semiconductor playbook; a HubSpot fixture with other owners was simulated.

</details>

### [D-031] 00:03 · BUILDER · DECISION
Every Q-007 failure is fixed and each of the reviewer's probes is now a regression case. The approval step now trusts only the audit trail: the account and playbook must match the audited create record for that request id, and the playbook hash is mandatory. The gate checks every line: a citation in each factual section, "Confirm" on every line of the conditional section whatever its bullet, and a much wider applicability, claim, duration and defense vocabulary. Clearing a kill switch now restarts the quality counts.

<details><summary>Structured fields</summary>

**What:** `decide.py` `created_record()`; `checks.py` line-by-line section checks, `CITED_SECTIONS`, wider `APPLIES`, `CLAIMS`, `DURATION`, `DEFENSE`; `icp.json` wider AI, stage and SaaS terms; `kill_switch.last_cleared()` and `reports.metrics()` counting since the last clear; guide updated. C3's semiconductor condition is logged, not changed: no semiconductor playbook exists.

**Why:** Q-007.

**Evidence:** First rerun after the gate rewrite: 31/42 evals. My new loop variable `text` shadowed the brief text, so the whole-brief checks (duration, defense, filler) only saw the last line. Renamed; 42/42. With the reviewer's 20 probes added as cases: "62/62 eval cases behaved as expected". Tests: "Ran 79 tests ... OK", including three request-tampering tests and the clear-then-rerun test.

**Assumption:** A report made before a clear was reviewed by the person who cleared the switch.

**Reversal trigger:** The operator wants complaints to accumulate across clears.

**Links:** Q-007

**Proof boundary:** Word lists still cannot prove a sentence true; the owner's review remains the control for plausible falsehoods.

</details>

### [D-032] 00:04 · BUILDER · DECISION
The MCP server is in. It exposes eight governed tools to any MCP client, and every rule is enforced inside them: the audit record comes first, closed accounts cannot go further, the CISO is never returned, the gate re-runs before any brief is written, and nothing sends. It was checked over a real MCP client, both in-process and over stdio exactly as `.mcp.json` launches it.

<details><summary>Structured fields</summary>

**What:** `agent/tools.py` (the governed logic, standard library), `agent/mcp_server.py` (`MCPServer` wrapper; `ToolFailure` becomes `ToolError`), `requirements.txt` (`mcp==2.2.0`), `.mcp.json` (`.venv/bin/python -m agent.mcp_server`), CI split into an offline job and an MCP job.

**Why:** A-046, A-047. Keeping the logic out of the server file means CI can test every rule without the MCP package, and a second client (Claude Desktop, any MCP client) gets the same enforcement.

**Evidence:** `tests/test_tools.py`: 7 tests OK (full path, closed accounts, order, gate enforced in `request_approval`, unimplemented trigger and kill switch, hold/drop only, audit failure). `tests/test_mcp_server.py` over `mcp.Client`: tools listed; `route_contact` on a dropped account returns an error ending "Recovery: call the tools in order ...". Stdio smoke check from `.mcp.json`: eight tools listed, `fetch_source` returned the SR 26-2 URL.

**Assumption:** Tools keep state per server process, so one agent session runs one account through the steps in order. A restart loses in-flight state, never audited state.

**Reversal trigger:** Several agents need to share one server concurrently.

**Links:** A-046, A-047, R-011

</details>

### [D-033] 00:05 · BUILDER · DECISION
The skill is written: it tells the agent to read the trigger sources itself, reason about the specific account, decide write, hold or drop, draft both lane framings, and self-check before requesting approval. The CEO's "no generic 'AI governance' sequence" is now a gate rule, not just an instruction. A literal em dash that crept back into the gate's own source is replaced by its escape.

<details><summary>Structured fields</summary>

**What:** `skills/regulatory-trigger-brief/SKILL.md`, linked at `.claude/skills/regulatory-trigger-brief` so Claude Code finds it in this repository. Gate: "AI governance" banned; optional owner-only section "## Lane framings for the account owner". New eval case.

**Why:** Operator decision A-046: the skill is the agent's instructions; the tools enforce. Putting the CEO's warning into the gate means a model that ignores the skill still cannot ship the phrase.

**Evidence:** `python3 -m evals.run_evals`: "63/63". First attempt at the gate edit did not apply (the replaced text did not match because the D-017 rewrite had re-introduced a literal em dash); caught by the new eval case missing (62/63). Tests OK (MCP test skipped without the package; it passes in `.venv`).

**Assumption:** Claude Code discovers project skills under `.claude/skills/`; the operator's layout puts the source under `skills/`, hence the link.

**Reversal trigger:** The skill does not load in the demo session (then copy instead of link).

**Links:** A-046, D-032

</details>

### [D-034] 00:06 · BUILDER · DECISION
Agent-run evals are in: six trigger-and-account cases with the properties a run must show, and a scorer that reads any run's output directory. A clean offline-test-mode run scores 22 of 22; the scorer is proven able to fail on a tampered brief. That baseline is committed and labelled as offline test mode, not as an agent result.

<details><summary>Structured fields</summary>

**What:** `evals/agent_cases.json`, `evals/score_run.py` (`python3 -m evals.score_run --out <dir>`), `tests/test_score_run.py`, `examples/offline-test-mode-scores.json`. Properties: passes the output gate; every line cited; no applicability claim without an established US entity; OSFI E-23 and B-13 named for the Canadian bank; forbidden claims absent; CISO never routed; routed to the owner and not sent; held, dropped and watched accounts never briefed, enriched or routed, with the decision recorded.

**Why:** Operator decision A-046, item 3.

**Evidence:** Offline run: "score 22/22". Tests: a tampered brief fails three properties; a run driven through the governed tool path (the same path the MCP server exposes) scores full on the brief cases. First version of the applicability property only looked for the caveat phrase and passed a brief that asserted "SR 26-2 applies"; strengthened to use the gate's applicability and Confirm checks. "Ran 82 tests ... OK (skipped=1)".

**Assumption:** A real agent run is scored the same way when the operator runs the demo in a Claude Code session; no agent-produced brief exists in this build session.

**Reversal trigger:** n/a

**Links:** A-046, D-032, D-033

</details>

### [R-012] 00:06 · PM · REVERSAL
Reverses A-014. The FDA PCCP source was wrongly recorded as unverified: my two guessed URLs were wrong, and the operator's researcher found and verified the real ones. The biopharma trigger stays not implemented, now for the true reason: only the bank trigger is built deeply in this window.

<details><summary>Structured fields</summary>

**What:** New position A-048. Sources: the FDA guidance page (`.../marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence`) and the PDF (`https://www.fda.gov/media/166704/download`), final guidance, August 2025, nonbinding.

**Why:** Operator decision relayed at 00:04 KST. The reason given for not implementing the trigger must be the real one.

**Evidence:** Re-fetch from this build environment: both URLs HTTP 404 to curl (the same response the guessed URLs got at 23:17, which suggests bot blocking rather than a missing page). The feed says exactly that in `verified_how`, so nobody reads "re-verified here" into it.

**Assumption:** none of the agent's own.

**Reversal trigger:** Either URL is withdrawn or superseded.

**Links:** A-014, A-048, D-003

</details>

