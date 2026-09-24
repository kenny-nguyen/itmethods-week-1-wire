"""The MCP server over a real MCP client, in-process. Skipped when the pinned `mcp` package is not installed
(the offline CI job); the `mcp` CI job installs requirements.txt and runs it."""

import asyncio
import json
import unittest
from pathlib import Path

from tests.helpers import tempdir

try:
    import mcp  # noqa: F401
    HAVE_MCP = True
except ImportError:
    HAVE_MCP = False

EXPECTED = {"list_playbooks", "fetch_source", "screen_account", "check_applicability", "route_contact",
            "check_claims", "write_audit_record", "request_approval"}


@unittest.skipUnless(HAVE_MCP, "mcp==2.2.0 not installed (pip install -r requirements.txt)")
class McpServerTests(unittest.TestCase):
    def test_tools_listed_and_enforcement_reaches_the_client(self):
        from mcp import Client
        from agent.mcp_server import build_server
        from agent.tools import GovernedTools

        async def scenario(out: Path):
            async with Client(build_server(GovernedTools(out))) as client:
                names = {t.name for t in (await client.list_tools()).tools}
                screened = await client.call_tool("screen_account", {"playbook_id": "bank-sr26-2", "account_id": "hs-1010"})
                refused = await client.call_tool("route_contact", {"playbook_id": "bank-sr26-2", "account_id": "hs-1010"})
                return names, screened, refused

        with tempdir() as d:
            names, screened, refused = asyncio.run(scenario(Path(d)))
            self.assertEqual(names, EXPECTED)
            self.assertFalse(screened.is_error)
            self.assertTrue(json.loads(screened.content[0].text)["do_not_contact"])
            self.assertTrue(refused.is_error)
            self.assertIn("Recovery:", refused.content[0].text)
            audit = [json.loads(l) for l in (Path(d) / "audit.jsonl").read_text().splitlines()]
            self.assertEqual([r["action"] for r in audit], ["score"])


if __name__ == "__main__":
    unittest.main()
