"""The agent-run scorer: full marks on a clean run, and it catches a bad brief on disk."""

import unittest
from pathlib import Path

from agent.processing.brief import TemplateProvider
from agent.run_playbook import run
from agent.tools import GovernedTools
from evals.score_run import score
from tests.helpers import tempdir
from tests.test_tools import offline_draft

MOTION = Path(__file__).resolve().parent.parent / "playbooks/motions/reign-first-motion.jsonc"


class ScoreRunTests(unittest.TestCase):
    def test_clean_offline_run_scores_full(self):
        with tempdir() as d:
            run(MOTION, Path(d), provider=TemplateProvider())
            r = score(Path(d))
            self.assertEqual(r["passed"], r["total"])
            self.assertGreater(r["total"], 15)

    def test_tampered_brief_is_caught(self):
        with tempdir() as d:
            s = run(MOTION, Path(d), provider=TemplateProvider())
            brief = Path(s["accounts"]["hs-1001"]["brief"])
            import re
            tampered = re.sub(r"SR 26-2 applicability requires confirmation[^.]*\.\s*", "", brief.read_text())
            brief.write_text(tampered.replace("## What changed\n", "## What changed\n- SR 26-2 applies to the bank.\n"))
            case = next(c for c in score(Path(d))["cases"] if c["account"] == "hs-1001")
            for prop in ("passes_output_gate", "every_line_cited", "no_applicability_claim_without_us_entity"):
                self.assertFalse(case["properties"][prop]["pass"], prop)

    def test_mcp_tool_path_run_is_scored(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            for acct in ("hs-1001", "hs-1002"):
                t.screen_account("bank-sr26-2", acct)
                t.check_applicability("bank-sr26-2", acct)
                t.route_contact("bank-sr26-2", acct)
                t.request_approval("bank-sr26-2", acct, offline_draft(t, acct))
            for acct in ("hs-1009", "hs-1010"):
                t.screen_account("bank-sr26-2", acct)
            r = score(Path(d))
            brief_cases = [c for c in r["cases"] if c["expect"] == "brief"]
            self.assertTrue(all(v["pass"] for c in brief_cases for v in c["properties"].values()))


if __name__ == "__main__":
    unittest.main()
