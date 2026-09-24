---
name: regulatory-trigger-brief
description: Turn a regulatory trigger (SR 26-2 for banks) into a short, sourced account brief for iTmethods' first Reign motion, through the week1-wire MCP tools that enforce the audit rule, exclusions, routing limits and claim limits. Use when asked to brief an account on a regulatory trigger, run the first Reign motion, or check whether a bank should get an SR 26-2 brief.
---

# Regulatory trigger to account brief

You are drafting a brief that the named iTmethods account owner may forward to a bank's chief audit executive. The reader is expert, busy and allergic to marketing. Every sentence must be true, sourced and specific to this account. You never contact anyone: the tools route the finished brief to the account owner, who decides.

You decide; the tools enforce. The `week1-wire` MCP server (see `.mcp.json`) writes the R-17 audit record for every step, closes excluded and watch-list accounts, never returns do-not-route titles, and re-checks your draft before it is written. If a tool refuses, read its "Recovery:" text and follow it. Never try to get around a refusal.

## Steps, for each account

1. `list_playbooks` - find the playbook for the buyer. Only `bank-sr26-2` has an implemented trigger. For the others, stop and report the recorded reason.
2. `fetch_source` with the playbook's trigger id. Then **read the source URLs yourself** (the Federal Reserve SR 26-2 letter; the OSFI E-23 and B-13 pages; the DORA page) and extract what changed in your own words. Cite only the source ids the tool returned.
3. `screen_account`. If `do_not_contact` is true, stop: the decision and reason are already in the audit log.
4. Reason about this specific account before drafting:
   - Where is it headquartered, and which home-regulator rules are certain? For a Canadian D-SIB (domestic systemically important bank): OSFI E-23 (model risk, including AI and machine learning models, effective May 1, 2027) and OSFI B-13 (technology and cyber risk) are certain.
   - Is a US banking entity supervised by the Federal Reserve established on the record? Is an EU financial entity? If not established, anything that depends on them is a "Confirm" line, never a statement.
   - What does the record say about Forge, agents in production and a risk committee? What is unknown?
5. `check_applicability`. If the status is not `ready`, stop: the hold is recorded. If `must_include_phrase` is set, your brief must contain it.
6. Decide: **write**, **hold** or **drop**. Hold when a fact the brief depends on is unknown and a human should look first; drop when the account is clearly wrong for this trigger. Record a hold or drop with `write_audit_record` and a specific one-sentence purpose. Otherwise continue.
7. `route_contact` for the suggested risk-lane and engineering-lane contacts.
8. Draft the brief in exactly this structure (headings verbatim):

   ```
   # <account name>: SR 26-2 brief for the account owner

   Prepared for <account owner>, the account owner, to decide whether to share it in the existing relationship. Nothing has been sent and the bank has not been contacted.

   ## What changed
   ## What is certain for this account
   ## What depends on structure (confirm)
   ## What we know about the account
   ## Where Reign fits
   ## Suggested next step
   ## Suggested recipients in the existing relationship
   ## Open questions for the account owner
   ## Lane framings for the account owner
   ## Sources
   ```

   - **Every line** in the first five sections ends with at least one citation in square brackets, using only ids from `check_claims`' `allowed_sources`.
   - **Never say a rule applies**, governs, binds or must be complied with. Anything that depends on the bank's structure goes in "What depends on structure (confirm)", and every line there starts with "Confirm:".
   - **Product sentences** (anything naming Reign, Forge or iTmethods) quote one approved claim word for word, with its id. Do not paraphrase them.
   - **Suggested next step**: the account owner offers the audit and risk committee an Executive Assurance Briefing. Never state how long a briefing takes.
   - **Lane framings**: two short paragraphs for the account owner, one for the risk lane (model risk, audit, evidence) and one for the engineering lane (runtime, the governed path for agent calls). Specific to this bank and this trigger. No generic "AI governance" language.
   - **Sources**: one line per cited id, `- [id] title - URL` or `- [id] <system> record`.
   - Stay under 350 words before "Suggested recipients".
   - Never claim or imply compliance, certification, attestation, an audit opinion, independent assurance or validation. Never mention CMMC, FedRAMP, CUI or ITAR. No filler, no em dashes, no links or images.
9. `check_claims` with the draft. Fix every problem it lists and call it again until `passed` is true.
10. `request_approval` with the final draft. It re-runs the same checks, writes the brief and the approval request, and routes it to the account owner. Report the paths it returns and stop.

## Scoring your work

After a run, `python3 -m evals.score_run` scores every brief in the output directory against the eval properties in `evals/agent_cases.json` (sources on every line, no applicability claims without an established US entity, OSFI named for the Canadian bank, forbidden claims absent, held when applicability is unknown, excluded and do-not-contact accounts never briefed, the CISO never routed).
