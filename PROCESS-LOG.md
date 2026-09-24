# Process log

Times are KST (Korea Standard Time). Decisions: [`AMBIGUITY-REGISTER.md`](AMBIGUITY-REGISTER.md).

## What I tried

Option 3: a Claude skill driving my own MCP (Model Context Protocol) server, with evals. The skill tells the agent how to read SR 26-2 (the Federal Reserve's model risk letter) and reason about one bank. The server's tools enforce R-17 (an audit record before touching a financial-services account), exclusions, routing and claim limits. HubSpot, Clay and ZoomInfo are fixtures ([day-one wiring](docs/day-one-wiring.md)); tools: [README](README.md#how-it-was-built).

## What failed

- **Guessed sources.** Two FDA (Food and Drug Administration) URLs an agent guessed returned 404.
- **My cross-border lines overstated scope.** An independent fact-check failed my brief: it said SR 26-2 applies to any Federal Reserve-supervised US entity and DORA (EU Digital Operational Resilience Act) to any EU financial entity. The sources say neither. Four product claims also overreached. Fixed, with new eval cases ([report](docs/qa/factcheck-report.md)).
- **Four defects my tests missed.** With 92 tests green, an adversarial reviewer found enrichment running before its audit record, a "C.I.S.O." (chief information security officer) title routed to engineering, a brief re-adding an excluded CISO, and "compliance-ready" passing the claim gate. All fixed, each with a regression test ([report](docs/qa/adversarial-report.md)).
- **Two usage-limit stops**, at 00:12 and again before 00:36, when a plan upgrade cleared it.
- **This log** first ran to about 14,700 words. To meet the packet's one-page rule I replaced the contract's append-only log with this page; the full log is in git history at `3dfa5fd:docs/decision-log.md`. The `no-mistakes(...)` commits are the validation pipeline's automatic fixes.

## What I learned

- Cross-border regulation is where a bank brief is judged ([One thing I did not know](docs/one-thing-i-did-not-know.md)).
- Building mode drifts. My note at 00:24: "act against the actual goal and requirements rather than getting lost in building mode".

## With another three hours

1. Build the pharma trigger on the FDA PCCP (Predetermined Change Control Plan) guidance.
2. Confirm Rob's intent on the defense play, and ask the CEO and CRO how to classify companies that blur AI startup and uses AI.
3. Wire the real blockable send path and a durable audit sink.
4. Run and score the direct model-API path with a key.
5. A drift check on product claims.

## Real snippets

<details><summary>The skill's core rules (<code>skills/regulatory-trigger-brief/SKILL.md</code>)</summary>

The agent's instructions.

```markdown
You decide; the tools enforce. ...
   - **Never say a rule applies**, governs, binds or must be complied with. Anything that depends on the bank's structure goes in "What depends on structure (confirm)", and every line there starts with "Confirm:".
```
</details>

<details><summary>The adversarial reviewer's prompt (excerpt)</summary>

Told to break things, not check them, a reviewer on another model found the C.I.S.O. bypass and the audit-ordering defect.

```text
Try to BREAK it, running real commands:
1. Bypass R-17: can any MCP tool or pipeline path create, update, enrich, score, route, exclude, hold, approve or message an account without an audit record first? ...
3. Routing: can a brief be routed to a CISO or any title on the do-not-route list?
4. Claims: can a forbidden claim ... pass check_claims or the evals? Try paraphrases.
```
</details>

<details><summary>The live agent run (transcript: <a href="examples/README.md">examples/</a>)</summary>

Because the agent was not permitted to use Bash, Write or Edit (`--allowedTools` with `--permission-mode dontAsk`), it could only write a brief through the governed `request_approval` tool: structural governance.

```sh
WIRE_OUT_DIR=<empty scratch dir> claude -p 'Run the regulatory-trigger-brief skill for the SR 26-2 trigger against the bank account(s) in the bank playbook.' \
  ... \
  --allowedTools 'mcp__week1-wire__*' Skill WebFetch Read Grep Glob
```
</details>
