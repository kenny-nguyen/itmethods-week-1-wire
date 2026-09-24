# Cut, sequenced, refused

What I cut from the window, what I did first, and what I refused to do, each with the reason. A- rows are in [`AMBIGUITY-REGISTER.md`](../AMBIGUITY-REGISTER.md).

Terms used below: SR 26-2 is the Federal Reserve's revised model risk guidance; OSFI is Canada's Office of the Superintendent of Financial Institutions; DORA is the EU's Digital Operational Resilience Act; R-17 is the packet's rule that an agent writes an audit record before it touches a financial-services person or account; FDA PCCP is the US Food and Drug Administration's guidance on a Predetermined Change Control Plan for AI-enabled device software functions; GxP is the family of "good practice" quality regulations, such as good manufacturing practice; CMMC is the US defense Cybersecurity Maturity Model Certification; CEO is chief executive officer, CISO chief information security officer, and ICP ideal customer profile.

**Architecture principle.** The artifact is meant not to be coupled to banking. The skill and the MCP (Model Context Protocol) tool interfaces are buyer-agnostic, and most of what is bank-specific lives in data: the bank playbook (`playbooks/bank-sr26-2.jsonc`), the SR 26-2 trigger record and its regulation mapping (OSFI E-23 and B-13, the US-arm and EU-arm conditions) in `fixtures/regulatory_feed.json`. Some bank specifics are still in code: the applicability check has a Federal Reserve rule (`agent/processing/preflight.py`), the output gate has SR 26-2 and DORA patterns (`agent/processing/checks.py`), and the brief template and approval requests say "the bank has not been contacted" for every account. A second buyer would need those generalised. The packet gives the most detail on the bank (the CEO notes, R-17 being specific to financial services, SR 26-2 and DORA), so the bank is the proving ground, not the limit.

| Cut | Why | With more time |
|---|---|---|
| Pharma trigger not built; its playbook is encoded | The artifact menu says "a regulatory trigger" (singular) and "pick one, go deep, do not spray"; the CEO says the bank is the buyer that matters this month; one deep trigger with sources and evals beats two thin ones; adding it later is mostly a data change (see the code caveats above). | Build the FDA PCCP trigger on the verified guidance, a Quality / Regulatory Affairs routing lane and GxP-aware claim limits, scored by the same evals. |
| Defense trigger not built; the approach is documented | None of the menu's four triggers fits defense; CMMC appears only with a question mark in the ICP sketch; the CEO is unsure ("I think. Check with Rob."); iTmethods states it holds no CMMC certification, so a CMMC-driven brief risks implying capability it lacks. | Confirm with Rob, then a CMMC scoping questionnaire (not a claim of readiness) feeding a Forge substrate briefing play. |
| No live send | R-17 needs a named approver and a blockable send, which cannot be proven without HubSpot or email access; the CEO says no bank outreach until a briefing is booked. Approved means ready to send. | Wire the real blockable send path ([`docs/production.md`](production.md) section 5). |

| Sequenced | Why |
|---|---|
| Bank first | The CEO's priority; R-17 is mandatory for financial services, so the bank path proves the knockout rule. |
| Governance tools before the agent | The rules had to exist and be tested before anything could draft. |
| Evals before the demo | The live run is judged by criteria fixed in advance. |

| Refused | Why |
|---|---|
| The blog | "Do not write a blog. Build the trigger." |
| Generic CISO sequences | The CEO's explicit kill condition; the CISO is on the do-not-route list and "AI governance" is a gate failure. |
| A volume cap in place of precision | Precision first; quality-based kill criteria instead (A-037). |
| Any compliance, certification or independent-assurance claim | iTmethods' own pages disclaim them; the gate refuses them. |
| Inventing a source or a fact | A missing fact is flagged, never filled; unverified sources cannot be cited. |
