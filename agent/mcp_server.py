"""MCP (Model Context Protocol) server exposing the governed tools to an agent.

    pip install -r requirements.txt
    python3 -m agent.mcp_server            # stdio transport; Claude Code starts it from .mcp.json

The agent (the skill in skills/regulatory-trigger-brief/) decides what to do;
every rule is enforced inside the tools in agent/tools.py, so no agent can
skip the audit record, an exclusion, the do-not-route list or the claim
limits. A refused or failed tool call returns an error whose message ends
with "Recovery: ..." (operator decision A-033).
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from agent.tools import GovernedTools, ToolFailure

INSTRUCTIONS = (
    "Governed tools for turning a regulatory trigger into an account brief for iTmethods' first Reign motion. "
    "Call them in order for each account: list_playbooks, fetch_source, screen_account, check_applicability, "
    "route_contact, check_claims, request_approval. Nothing is ever sent; approval goes to the named account owner. "
    "Follow the regulatory-trigger-brief skill."
)


def build_server(tools: GovernedTools | None = None) -> MCPServer:
    t = tools or GovernedTools()
    server = MCPServer(name="week1-wire", instructions=INSTRUCTIONS, version="0.2.0")

    def call(fn, *args):
        try:
            return fn(*args)
        except ToolFailure as exc:
            raise ToolError(str(exc)) from exc

    @server.tool()
    def list_playbooks(motion_id: str = "reign-first-motion") -> dict:
        """List the motion's playbooks (buyer segment, trigger, channel, implemented or not) and the accounts."""
        return call(t.list_playbooks, motion_id)

    @server.tool()
    def fetch_source(trigger_id: str) -> dict:
        """Return the trigger's verified source URLs, extracted facts, home-regulator context and structural
        conditions. Read the URLs yourself; cite only these source ids."""
        return call(t.fetch_source, trigger_id)

    @server.tool()
    def screen_account(playbook_id: str, account_id: str) -> dict:
        """Run the ICP for one account (audited). If do_not_contact is true, stop: the account is closed."""
        return call(t.screen_account, playbook_id, account_id)

    @server.tool()
    def check_applicability(playbook_id: str, account_id: str) -> dict:
        """Preflight whether a brief may be drafted and what it must say about applicability (audited hold if not)."""
        return call(t.check_applicability, playbook_id, account_id)

    @server.tool()
    def route_contact(playbook_id: str, account_id: str) -> dict:
        """Suggest contacts by lane (risk, engineering) from job titles; do-not-route titles are never returned."""
        return call(t.route_contact, playbook_id, account_id)

    @server.tool()
    def check_claims(playbook_id: str, account_id: str, brief_markdown: str) -> dict:
        """Run the output gate on a draft brief. Returns every problem, the allowed sources and approved claims."""
        return call(t.check_claims, playbook_id, account_id, brief_markdown)

    @server.tool()
    def write_audit_record(playbook_id: str, account_id: str, decision: str, purpose: str,
                           sources: list[str]) -> dict:
        """Record your own decision to 'hold' or 'drop' an account, with a specific one-sentence purpose."""
        return call(t.write_audit_record, playbook_id, account_id, decision, purpose, sources)

    @server.tool()
    def request_approval(playbook_id: str, account_id: str, brief_markdown: str) -> dict:
        """Re-run the gate, then write the brief and an approval request routed to the account owner. Never sends."""
        return call(t.request_approval, playbook_id, account_id, brief_markdown)

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
