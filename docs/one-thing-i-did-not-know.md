# One thing I did not know: which rules reach a Canadian bank, and through what

When the window opened, I did not know how a US Federal Reserve letter relates to a Canadian bank. The trigger in the packet is SR 26-2. The buyer is a Canadian D-SIB (domestic systemically important bank). The obvious brief, "SR 26-2 is out, here is what it means for you", would have been wrong, and wrong in front of the one reader who would notice: the bank's audit and risk function.

## What I learned

Three layers, with a different level of certainty for each.

| Rule | What it is | How it reaches a Canadian D-SIB | Certainty |
|---|---|---|---|
| **SR 26-2** | Federal Reserve supervisory letter of April 17, 2026: revised model risk guidance that supersedes SR 11-7 and SR 21-8. The letter says it is "expected to be most relevant to banking organizations with over $30 billion in total assets regulated by the Federal Reserve". | My reading: only through US operations the Federal Reserve regulates. Whether the bank has them, and whether they fall in the scope the letter describes, depends on its structure. | Depends. Marked "Confirm". |
| **OSFI E-23** | Model risk management guideline from OSFI (Office of the Superintendent of Financial Institutions), covering AI and machine learning models. Effective May 1, 2027. | Applies to federally regulated financial institutions, which a Canadian D-SIB is. | Certain. |
| **OSFI B-13** | Technology and cyber risk management guideline. | Same: it sets expectations for all federally regulated financial institutions. The page did not show an effective date, so the brief does not give one. | Certain. |
| **DORA** | Regulation (EU) 2022/2554, the Digital Operational Resilience Act for the EU financial sector. | EIOPA (European Insurance and Occupational Pensions Authority) says it applies to 20 types of financial entities and to ICT (information and communication technology) third-party service providers. It reaches the bank only if an EU entity of the bank falls into one of those types. | Depends. Marked "Confirm". |

Sources, all read during the window: [SR 26-2](https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm), [OSFI E-23](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027), [OSFI B-13](https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/technology-cyber-risk-management), [EIOPA on DORA](https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en). EUR-Lex blocked automated reads, so the DORA regulation text itself was not read; the EIOPA page was.

The practical lesson: for a cross-border bank, the news is the US letter, but the rules that certainly apply to it are its home regulator's. A brief that leads with the foreign rule and states it as binding is the embarrassment case.

## How it became the brief's structure

The brief follows the three layers, in this order (decision A-044 in [AMBIGUITY-REGISTER.md](../AMBIGUITY-REGISTER.md)):

1. **What changed** - SR 26-2, in the letter's own scope language.
2. **What is certain for this account** - OSFI E-23 and B-13.
3. **What depends on structure (confirm)** - every line starts with "Confirm:": a Federal Reserve-regulated US entity for SR 26-2, an in-scope EU entity for DORA.

The skill tells the agent to "never say a rule applies". The output gate refuses applicability wording ("applies", "in scope", "subject to" and similar) anywhere outside the "Confirm" section, and any unmarked line inside it. The account owner gets a brief that is useful without a legal opinion, and its open questions are ones the bank can answer.

## How I got dangerous in three hours

- **22:50** Packet opened. SR 26-2 was a name I could not place.
- **23:03** An independent research agent (a different AI model, working blind) confirmed SR 26-2 is a real Federal Reserve letter dated April 17, 2026, and confirmed OSFI E-23 and B-13 for Canadian banks.
- **23:17** The building agent fetched the SR 26-2 page directly and quoted its scope sentence, so the brief did not rest on memory or on the research agent alone.
- **23:39** My note at the time: cross-border regulation is "probably where they'll look hardest, because it matters for governance". I asked for a deeper pass on SR 26-2 for a Canadian bank.
- **23:47** I set the three-layer structure (A-044). **23:55** It was in the template, the gate and three new eval cases.
- **00:22** The independent fact-check returned FAIL on my own lines. The first draft said that if the bank operates "a US banking entity supervised by the Federal Reserve, SR 26-2 applies to that entity", and that if it has "an EU financial entity, DORA ... applies to that entity". The sources support neither: SR 26-2 describes where it is "expected to be most relevant", and DORA covers listed entity types only ([report](qa/factcheck-report.md), findings F-02 and F-07).

That last step is the real learning. The structure was right, and the conditional was still written too strongly, in exactly the place the structure was meant to protect. The gate allowed "applies" inside the "Confirm" section because a conditional looked safe; that is where the overstatement lived. The fix: the "Confirm" lines now keep the regulator's own scope words. The SR 26-2 line says the letter "addresses Federal Reserve-regulated banking organizations and is expected to be most relevant above $30 billion in total assets" and asks the account owner to confirm whether the bank has one. The DORA line asks whether the bank has EU entities of the types DORA covers. Two new eval cases in `evals/brief_cases.json` fail a brief that says SR 26-2 "applies to that entity" or that DORA applies to any EU financial entity.

## What I still do not know

- Whether a Federal Reserve-regulated US arm of a Canadian bank falls inside SR 26-2's expected relevance in practice. The letter says "expected to be most relevant"; how supervisors use that is not on the page I read.
- The DORA text itself, which I only read through EIOPA's summary.
- The real bank's legal structure. The fixture accounts are fictional on purpose.
