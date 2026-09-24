# iTmethods product facts (public sources)

The only product statements a generated brief may make. They are loaded from `data/claims.json`, which carries the same statements with their source URLs. A brief that states anything about iTmethods outside this list, or breaks one of the content rules below, fails the output gate (`wire/processing/checks.py`).

Source: a researcher report relayed by the supervising agent at 23:20 KST, summarised below. The URLs were re-fetched at 23:22 KST and all returned HTTP 200; the banking, defense and assurance claims were spot-checked against page text (quotes below).

| ID | Statement | Source |
|---|---|---|
| P-FORGE | Forge is iTmethods' managed runtime and infrastructure substrate for DevOps, AI workloads and agent runtimes. Positioning line: "Forge runs; Reign governs". | https://www.itmethods.com/learn/sovereign-ai, https://www.itmethods.com/forge/agent-infrastructure |
| P-SOLD-SEPARATELY | Reign products are sold independently, not as a bundle. | https://www.itmethods.com/ops |
| P-STATUS | Reign Ops is available, Reign Gateway is available, Reign Factory is in beta, Reign Assurance is in co-design. | https://www.itmethods.com, https://www.itmethods.com/assurance |
| P-GATEWAY | Reign Gateway is a governed path for agent and application calls to approved models and tools: identity, policy, spend limits, and records of caller, decision, destination and outcome. | https://www.itmethods.com/gateway |
| P-ASSURANCE | Reign Assurance is being designed to prepare evidence. It does not issue an audit opinion, a certification or independent assurance. | https://www.itmethods.com/assurance |
| P-BRIEFING | The Executive Assurance Briefing is stage 1 of Briefing, Runtime Risk and Governance Assessment, Focused Pilot, Platform Rollout, aimed at boards, audit and risk committees. | https://www.itmethods.com/reign/assurance |
| P-BANKING | The banking page centres on OSFI E-23, SR 26-2 and DORA; iTmethods works as first line, does no independent validation, and makes no compliance or certification claim. | https://www.itmethods.com/sectors/banking |
| P-DEFENSE | iTmethods holds no FedRAMP authorization and no CMMC certification, does not handle CUI (Controlled Unclassified Information), and claims no ITAR compliance. | https://www.itmethods.com/sectors/public-defence |

Not known: what the target bank runs on Forge.

## Content rules (deterministic checks)

1. Never claim compliance, certification, independent assurance or validation.
2. Never state a briefing duration. Pages disagree (25, 45 and 45-60 minutes), so no single number is true.
3. Never imply CMMC, FedRAMP or CUI capability.
4. Product claims only from the table above.

## Spot-check quotes (re-fetched 23:22 KST)

- Assurance page: "iTmethods does not issue an audit opinion or a certification, and nothing here is independent assurance of anyone's controls."
- Banking page: "iTmethods does not validate its own work, independently review it or subject it to effective challenge, and does not certify, attest, issue an audit opinion or provide independent assurance".
- Defense page: "We hold no FedRAMP authorization, no 3PAO-validated package, no Marketplace listing and no readiness designation".
