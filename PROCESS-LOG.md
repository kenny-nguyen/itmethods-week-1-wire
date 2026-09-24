# Process log

One page, as the packet asks. Times are KST (Korea Standard Time). Every judgment call: [`AMBIGUITY-REGISTER.md`](AMBIGUITY-REGISTER.md).

## What I tried

Option 3: a Claude skill driving my own MCP (Model Context Protocol) server, with evals. The skill tells the agent how to read SR 26-2 and reason about one bank; the server's tools enforce R-17, the exclusions, routing and claim limits, so the agent cannot skip them. HubSpot, Clay and ZoomInfo are fixtures ([day-one wiring](docs/day-one-wiring.md)); tools used: [README](README.md#how-it-was-built).

## What failed

- **Guessed sources.** Two FDA PCCP URLs an agent guessed returned 404; a research agent found the real guidance.
- **My cross-border lines overstated scope.** The independent fact-check failed my brief: it said SR 26-2 applies to any Federal Reserve-supervised US entity and DORA to any EU financial entity; the sources support neither. Four product claims cited changed pages. Fixed with the regulators' scope words, claims re-quoted from live pages, and new eval cases ([report](docs/qa/factcheck-report.md)).
- **Four defects my tests missed.** With 92 tests green, an adversarial reviewer on a different model found enrichment running before its R-17 audit record, a "C.I.S.O." title routed to engineering, a brief that could re-add an excluded CISO, and paraphrases like "compliance-ready" passing the claim gate. All four fixed, each with a regression test ([report](docs/qa/adversarial-report.md)).
- **Two usage-limit stops.** The review agent hit its session limit at 00:12; a second stop cleared at 00:36 after a plan upgrade.
- **This log** first ran to about 14,700 words.

## What I learned

- Cross-border regulation is where a bank brief is judged ([One thing I did not know](docs/one-thing-i-did-not-know.md)).
- Tests pass on the cases their author imagined. A reviewer on another model, briefed to break things, found the rest.
- Building mode drifts. My note at 00:24: "act against the actual goal and requirements rather than getting lost in building mode".

## With another three hours

1. Build the pharma trigger on the verified FDA PCCP guidance, scored by the same evals.
2. Confirm with the CEO and CRO Rob's intent for defense, and how to classify companies blurring "AI startup" and "uses AI".
3. Wire the real blockable send path and a durable audit sink.
4. Run and score the direct model-API path with a key.
5. A drift check on the quoted product claims.

## Real snippets

<details><summary><code>.mcp.json</code>: how the client starts the governed tools</summary>

```json
{
  "mcpServers": {
    "week1-wire": {
      "command": ".venv/bin/python",
      "args": ["-m", "agent.mcp_server"],
      "env": {}
    }
  }
}
```
</details>

<details><summary><code>SKILL.md</code>: the agent's two core rules</summary>

```markdown
You decide; the tools enforce. The `week1-wire` MCP server (see `.mcp.json`) writes
the R-17 audit record for every step, closes excluded and watch-list accounts, never
returns do-not-route titles, and re-checks your draft before it is written.

- **Never say a rule applies**, governs, binds or must be complied with. Anything that
  depends on the bank's structure goes in "What depends on structure (confirm)", and
  every line there starts with "Confirm:".
```
</details>

<details><summary><code>agent/governance/audit.py</code>: no record, no action</summary>

```python
def perform(self, *, action, object_id, purpose, sources, fs, commit, ...):
    """Write the audit record, then complete the action. No record, no action."""
    try:
        self.sink.append(record)
    except Exception as exc:  # any sink failure blocks the action
        self._fail(record, f"audit record could not be written: {exc}", required, exc)
    try:
        return commit()
```
</details>
