# iTmethods product facts (public sources)

The only product statements a brief may make are in `docs/research/product-claims.json`. Each one is a single sentence quoted exactly from the cited page as fetched live on 2026-09-24 at 15:28 UTC (00:28 KST). The output gate (`agent/processing/checks.py`) accepts a product sentence only when it restates one of these word for word.

| ID | Usable in a brief | Exact quote | Page |
|---|---|---|---|
| P-GATEWAY | yes | "Reign Gateway gives applications and agents a governed path to approved models and tools." | https://itmethods.com/gateway |
| P-ASSURANCE-STATUS | yes | "Reign Assurance is in co-design development." | https://itmethods.com/assurance |
| P-ASSURANCE-BOUNDARY | yes | "iTmethods does not issue an audit opinion or a certification, and nothing here is independent assurance of anyone’s controls." | https://itmethods.com/assurance |
| P-EVIDENCE | yes | "Reign prepares the evidence; the people who own the risk decide." | https://itmethods.com/assurance |
| P-RELIANCE | yes | "The assurance and reliance judgments stay with your business, risk, compliance and audit experts, and any audit opinion or certification stays with their auditors." | https://itmethods.com/assurance |
| P-BANKING | yes | "iTmethods does not validate its own work, independently review it or subject it to effective challenge, and does not certify, attest, issue an audit opinion or provide independent assurance, so where any of those functions is required, we would work with a firm that holds that mandate." | https://itmethods.com/sectors/banking |
| P-STATUS | yes | "Reign Ops and Reign Gateway are available today." | https://itmethods.com/status |
| P-DEFENSE | no (research only) | "iTmethods is not FedRAMP authorized or CMMC certified, does not handle controlled unclassified information and does not claim ITAR compliance, so we confirm the supplier path before scoping begins." | https://itmethods.com/sectors/public-defence |

## What changed after the independent fact-check

The fact-check (`docs/qa/factcheck-report.md`, rows F-09, F-10, F-13, F-14, F-17) found claims whose cited pages had changed. Fixed by fetching every page live and keeping only sentences that are on today's page:

- **Removed:** Forge positioning ("Forge runs; Reign governs"), "sold independently, not as a bundle", and the Executive Assurance Briefing four-stage funnel. Their wording is not on the current pages.
- **Replaced:** "iTmethods works as first line" was our interpretation, not a quote. P-BANKING now quotes the banking page's own boundary, and P-RELIANCE quotes the assurance page: reliance judgments stay with the customer's business, risk, compliance and audit experts.
- **Kept, re-quoted:** Gateway, Assurance status and boundary, the evidence sentence, product status, and the defense statement (research only).

"Existing Forge customer" in a brief is an account fact from the system of record, cited to the HubSpot record, not a product claim.

## Content rules (deterministic checks)

1. Never claim or imply compliance, certification, attestation, validation or independent assurance. The gate blocks those word families anywhere outside the quoted claims above.
2. Never state a briefing or meeting duration. The earlier research relayed durations that disagreed across pages (25, 45 and 45-60 minutes), but this repository has no reproducible source note for them (fact-check F-17). The rule stands as a precaution, not a sourced fact: the gate blocks any duration.
3. Never imply CMMC, FedRAMP, CUI or ITAR capability. The defense page says iTmethods holds none (P-DEFENSE); the gate refuses the terms outright.
4. Product claims only from the table above, word for word.
