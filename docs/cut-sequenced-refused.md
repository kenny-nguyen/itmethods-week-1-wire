# Cut, sequenced, refused

What we cut from the window, what we did first, and what we refused to do, each with the reason. Moved from the README so it stays short. Entry IDs (A-, D-, R-) are in [`AMBIGUITY-REGISTER.md`](../AMBIGUITY-REGISTER.md) and [`decision-log.md`](decision-log.md).

**Architecture principle.** The artifact is not coupled to banking. The skill and the MCP tools are buyer-agnostic; everything bank-specific lives in data: the bank playbook (`playbooks/bank-sr26-2.jsonc`), the SR 26-2 trigger record and its regulation mapping (OSFI E-23 and B-13, the US-arm and EU-arm conditions) in `fixtures/regulatory_feed.json`. The packet gives the most detail on the bank (the CEO notes, R-17 being specific to financial services, SR 26-2 and DORA), so the bank is the proving ground, not the limit.

| Cut | Why | With more time |
|---|---|---|
| Pharma trigger not built; its playbook is encoded | The artifact menu says "a regulatory trigger" (singular) and "pick one, go deep, do not spray"; the CEO says the bank is the buyer that matters this month; one deep trigger with sources and evals beats two thin ones; adding it later is a data change. | Build the FDA PCCP trigger on the verified guidance, a Quality / Regulatory Affairs routing lane and GxP-aware claim limits, scored by the same evals. |
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
| A volume cap in place of precision | Operator decision A-037. |
| Any compliance, certification or independent-assurance claim | iTmethods' own pages make none; the gate refuses them. |
| Inventing a source or a fact | A missing fact is flagged, never filled; unverified sources cannot be cited. |
