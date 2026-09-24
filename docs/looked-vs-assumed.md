# What I went looking for vs what I assumed

A- rows are in [`AMBIGUITY-REGISTER.md`](../AMBIGUITY-REGISTER.md), with full reasoning and reversal triggers.

Terms used below: SR 26-2 is the Federal Reserve's revised model risk guidance; OSFI is Canada's Office of the Superintendent of Financial Institutions; DORA is the EU's Digital Operational Resilience Act; EIOPA is the European Insurance and Occupational Pensions Authority; FDA PCCP is the US Food and Drug Administration's guidance on a Predetermined Change Control Plan; FedRAMP is the US Federal Risk and Authorization Management Program; CMMC is the Cybersecurity Maturity Model Certification; CUI is controlled unclassified information; ITAR is the US International Traffic in Arms Regulations; MCP is the Model Context Protocol and SDK means software development kit; R-17 is the packet's rule that an agent writes an audit record before it touches a financial-services (FS) person or account; ICP is ideal customer profile; CEO is chief executive officer and CISO chief information security officer.

**Went looking (read from the source, not recalled):**

| Question | What I found |
|---|---|
| Is SR 26-2 real, and whom does it cover? | Federal Reserve letter of April 17, 2026; "most relevant to banking organizations with over $30 billion in total assets regulated by the Federal Reserve"; supersedes SR 11-7 and SR 21-8. |
| What binds a Canadian D-SIB (domestic systemically important bank) for sure? | OSFI E-23 (model risk), page shows effective May 1, 2027; OSFI B-13 (technology and cyber risk). |
| DORA's source? | EUR-Lex blocked automated reads; the EIOPA page names Regulation (EU) 2022/2554. |
| What do Forge and Reign actually do, and in what state? | itmethods.com: Reign Ops and Gateway available, Factory beta, Assurance in co-design; Gateway is the governed path to approved models and tools. The Forge positioning line I first quoted is no longer on the cited pages, so briefs no longer use it (fact-check F-09). |
| What must iTmethods never claim? | Its own pages: no audit opinion, certification or independent assurance; the public-sector page says it is not FedRAMP authorized or CMMC certified, does not handle CUI and does not claim ITAR compliance. |
| FDA PCCP guidance? | Two URLs an agent guessed returned 404 (fda.gov also returns 404 to automated reads here for the real pages, so the 404 alone did not prove them wrong); a research agent found and verified the real guidance. |
| The MCP SDK's current API? | Read from the installed `mcp==2.2.0`: `FastMCP` became `MCPServer` in 2.x. |
| Did my own cross-border lines match those sources? | Not at first. The independent fact-check found my SR 26-2 and DORA "Confirm" lines stated applicability more broadly than the sources do (findings F-02, F-07 in [`qa/factcheck-report.md`](qa/factcheck-report.md)). The lines now keep the regulators' own scope words, and eval cases fail the old wording. See [One thing I did not know](one-thing-i-did-not-know.md). |

**Assumed, then decided by me** (full reasoning and reversal triggers in `AMBIGUITY-REGISTER.md`):

| Row | Reading | One-line reason |
|---|---|---|
| A-004 | Unknown headcount is held for a human | Precision, not volume. |
| A-006 | Unknown industry counts as financial services, flagged | An FS account must never escape its audit record. |
| A-007, A-038 | R-17 audit on every segment | A receipt of what my agent did, never a test the prospect must pass. |
| A-011, A-032 | Route risk and engineering by title; never the CISO | "Route them without asking"; the CEO's CISO warning. |
| A-013 | Fictional fixture companies | No invented facts about real banks. |
| A-021 | Rob's risk-committee note is a flag | Unvetted Slack note. |
| A-023 | Defense leads with Forge, Reign as the reason agents can be let in | The CEO's last word; a natural ascension. |
| A-025, A-044 | Hold when applicability is unknown; the SR 26-2 brief separates certain from "Confirm" | Never claim a rule applies. |
| A-029 | Product claims only from the sourced list | A wrong claim to a bank is worse than none. |
| A-031 | Clearly outside the ICP: dropped with the reason audited; unclear: held | No silent drops. |
| A-033 | Fail loudly, never fall back silently | Nothing is worse than a silent failure. |
| A-035 | No send path; "unknown" channel counts as sending | If it cannot be audited and approved, it does not send. |
| A-036 | Agent adoption is a signal, never an exclusion | Nothing in the packet says to exclude on "none". |
| A-037 | No volume cap; quality-based kill criteria | Precision first. |
| A-039, A-040 | Chipmakers without an export-control problem and hospitals go on a watch list | Noticed and logged, never contacted. |
| A-041, A-042, A-043 | Three stub-shaped playbooks; "briefing" is the booked meeting; the brief goes to the account owner | Close reading of the stub and the CEO notes. |
| A-045 | Brief limit of 350 words before the owner-only notes | Still proposed. |
