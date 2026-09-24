# Live agent run: SR 26-2 against the bank playbook

**This is agent output.** Claude Code ran headless and drove the `regulatory-trigger-brief` skill and the `week1-wire` MCP server's governed tools. No file in this directory was written or edited by hand. The only change after the run was replacing absolute paths: the output directory became `$WIRE_OUT_DIR` (or a path relative to the run), the repository became `$REPO` and the home directory became `~`. Every company and person is fictional.

## How it was run

```
WIRE_OUT_DIR=<empty scratch dir> claude -p 'Run the regulatory-trigger-brief skill for the SR 26-2 trigger against the bank account(s) in the bank playbook.' \
  --mcp-config .mcp.json --strict-mcp-config --setting-sources project \
  --output-format stream-json --verbose --permission-mode dontAsk \
  --allowedTools 'mcp__week1-wire__*' Skill WebFetch Read Grep Glob
```

- Claude Code 2.1.280, model `claude-opus-5-5`, run on 2026-09-24 (UTC). The MCP server ran from a local `.venv` built from `requirements.txt`.
- The prompt is the whole user input. The agent was not permitted to use Bash, Write or Edit (`--allowedTools` with `--permission-mode dontAsk`), so the only way to write a brief was through `request_approval`.
- This was the first and only attempt. It was not re-run.
- Full event stream: [`transcript.jsonl`](transcript.jsonl) (Claude Code `stream-json`: every tool call and result, including the web-fetch sub-agent's).

## Result

| Account | Outcome | Decided by |
|---|---|---|
| hs-1001 Northbridge Financial Group | Brief written, approval request routed to the account owner, `send: false` | agent, gate passed |
| hs-1002 Lakeshore Bancorp | Brief written, approval request routed to the account owner, `send: false` | agent, gate passed |
| hs-1009 Harbourline Trust | Held at screening: headcount unknown | `screen_account` (ICP) |
| hs-1010 Riverbend Credit Union | Excluded at screening: 800 employees, under the 5,000 floor | `screen_account` (ICP) |

## Score

`python3 -m evals.score_run --out $WIRE_OUT_DIR --write scores.json` printed **20/22** and exited 1:

```
PASS  hs-1001  Canadian D-SIB on Forge; US entity not established
PASS  hs-1002  US bank holding company
PASS  hs-1009  bank with unknown headcount: fit unknown
PASS  hs-1010  credit union under the 5,000-employee floor
FAIL  hs-1006  Gen-AI start-up filed as fintech: category unclear, held for a human  failed: ['decision_recorded']
FAIL  hs-1007  hospital: watch list this month, do not contact  failed: ['decision_recorded']
score 20/22
```

The two failures are eval cases for hs-1006 (segment `fintech`) and hs-1007 (segment `hospital`). Neither is in the bank playbook's segment (`dsib_capital_markets`), and the prompt asked only for the bank accounts, so the agent never touched them. The CLI scores the whole output directory, so it counts an untouched case as a failed `decision_recorded`. The offline example gets 22/22 because the batch runner screens every account in the motion.

Scoped to this run (`evals.score_run.score(out, run_dir=...)`, the score the review page shows), the result is **16/16** on the four exercised cases, with hs-1006 and hs-1007 marked "not exercised": [`scores-run.json`](scores-run.json). Both numbers are kept. Neither is edited.

## Tool calls in order

1. `Skill regulatory-trigger-brief`: loaded the skill.
2. `ToolSearch`: loaded the eight `week1-wire` tool schemas.
3. `list_playbooks`: three playbooks, of which only `bank-sr26-2` is implemented, plus eleven accounts. The agent picked the four in segment `dsib_capital_markets`.
4. `fetch_source {"trigger_id": "sr-26-2"}`: **refused**: `trigger 'sr-26-2' not found ... Recovery: use a trigger id from list_playbooks, such as SR-26-2.` Logged to `errors.jsonl`.
5. `fetch_source {"trigger_id": "SR-26-2"}`: trigger record, four verified sources (SR 26-2, OSFI E-23, OSFI B-13, DORA), context by jurisdiction and structural conditions.
6. `screen_account hs-1001`: include. Canadian D-SIB (domestic systemically important bank), Forge customer, agents in production. Audited `enrich` then `score`.
7. `screen_account hs-1002`: include. US bank holding company, agents planned, enrichment flags a Federal Reserve-regulated entity.
8. `screen_account hs-1009`: hold (headcount unknown). `do_not_contact: true`, so the agent stopped there.
9. `screen_account hs-1010`: exclude (800 employees). `do_not_contact: true`, so the agent stopped there.
10. `check_applicability hs-1001`: `ready`, applicability `requires_confirmation` (no US Federal Reserve-regulated entity established). The brief must include "applicability requires confirmation". Certain context: OSFI E-23 and B-13.
11. `check_applicability hs-1002`: `ready`, applicability `applies` (US-headquartered).
12. `Agent (web-fetch)`: the agent sent a sub-agent to read the source URLs, as the skill tells it to:
    - `WebFetch` SR 26-2 cover letter (HTTP 200)
    - `WebFetch` OSFI E-23 (HTTP 200)
    - `WebFetch` OSFI B-13 (HTTP 200)
    - `WebFetch` EIOPA DORA page (HTTP 200)
    - `WebFetch` SR 26-2 attachment PDF (HTTP 200, but the text came back unreadable). The sub-agent reported that it could not read the attachment and did not answer those questions from memory. As a result the briefs use only what the cover letter says about SR 26-2.
13. `route_contact hs-1001`: risk lane: Chief Audit Executive, Chief Risk Officer, Head of Model Risk Management. Engineering lane: VP Platform Engineering. One contact was not routed (a do-not-route information security title).
14. `route_contact hs-1002`: risk lane: Chief Risk Officer. Engineering lane: Head of AI Engineering.
15. `check_claims hs-1001` with a placeholder draft, to get the allowed sources and approved claims. Failed as expected.
16. `check_claims hs-1002` with a placeholder draft, for the same reason.
17. `check_claims hs-1001`, first real draft: **failed** with 13 problems. It was 411 words (limit 350). Seven product sentences failed the word-for-word claim check, because the approved claims were wrapped in quotation marks and two product lines were the agent's own wording. That also made the P-BANKING disclaimer ("does not validate ...") trip the compliance check. The four recipient lines were not in the format routing produces.
18. `Grep` and `Read` of `agent/processing/checks.py` and `agent/processing/brief.py`: the agent read the gate's rules and the exact recipient-line format.
19. `check_claims hs-1001`, second draft: **failed**, 405 words.
20. `check_claims hs-1001`, third draft: **passed**.
21. `check_claims hs-1002`, first real draft: **passed**.
22. `request_approval hs-1001`: the gate re-ran, then wrote `briefs/hubspot_company_hs-1001.md` and `approvals/hubspot_company_hs-1001.json`, routed to the account owner, `sent: false`.
23. `request_approval hs-1002`: same, for hs-1002.

The agent then stopped and reported. It did not run the eval scorer (scoring was done afterwards, as above).

## Files

| File | What it is |
|---|---|
| `briefs/` | The two briefs, exactly as `request_approval` wrote them. |
| `approvals/` | The approval requests: `status: pending`, `send: false`, routed to the account owner. |
| `audit.jsonl` | Every R-17 audit record the tools wrote during the run. |
| `errors.jsonl` | The one refused call (step 4). |
| `review.html` | The one-page review view, regenerated after the run with `python3 -m agent.output.review` so it carries the run-scoped score. Download and open it locally. |
| `scores.json` | `evals.score_run` CLI output (20/22). |
| `scores-run.json` | The same scorer scoped to this run (16/16, two cases not exercised). |
| `transcript.jsonl` | The full Claude Code event stream. |
| [`blocked-attempt/`](blocked-attempt/TRANSCRIPT.md) | A second live run asking the same agent to brief the do-not-contact hospital account. The tool refused it. |

## Things a reviewer should know

- The agent wrote "Confirm:" lines for SR 26-2 for both banks. For hs-1002, `check_applicability` returned `applies`, but the skill never lets a brief state that a rule applies, and the Federal Reserve-regulated flag comes only from the enrichment row. The agent listed that as an open question for the account owner.
- Lakeshore's brief does not mention Forge. The gate allows product sentences only as approved claims quoted word for word, so the agent left out "not a Forge customer" instead of paraphrasing.
- `Agent` was not in `--allowedTools`, but Claude Code still let the agent hand the web reading to its built-in `web-fetch` sub-agent. That sub-agent's `WebFetch` calls are in the transcript.
