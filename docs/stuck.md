# Stuck, and the next experiment

Where I got stuck in the window, and the experiment I would run next.

| Stuck on | Next experiment |
|---|---|
| No model API (application programming interface) key in the build environment | Run the direct API path with a key and score its briefs with the same evals. |
| No live agent run in the build environment | Run the skill in Claude Code with the MCP (Model Context Protocol) server attached (the demo) and commit the scored result to `examples/`. |
| No HubSpot, Clay or ZoomInfo access | Wire the adapters in the [day-one table](day-one-wiring.md); the fixtures already exercise every interface. |
| Automated reads failed from this environment: EUR-Lex (the EU law database) returned an anti-bot page, and fda.gov returned HTTP 404 even for the real guidance | Fetch the regulation texts through a browser or a research agent and store verified text snapshots next to the feed. |
| Companies that blur the line between a bank or insurer and an AI startup (the category fields, segment and industry, are the only thing that excludes; an unclear category is held) | Agree with sales leadership how those companies are categorised, then update the classification rule in `icp/icp.json`. |
| The approver is a typed name | Bind approvals to an authenticated identity (single sign-on or the HubSpot user) before any send path is wired. |
