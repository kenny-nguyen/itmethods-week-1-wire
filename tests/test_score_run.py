"""The agent-run scorer: full marks on a clean run, and it catches a bad brief on disk."""

import unittest
from pathlib import Path

from agent.processing.brief import TemplateProvider
from agent.run_playbook import run
from agent.tools import GovernedTools, ToolFailure
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

    def test_run_scope_scores_only_that_run(self):
        with tempdir() as d:
            first = run(MOTION, Path(d), provider=TemplateProvider())
            second = run(MOTION, Path(d), provider=TemplateProvider())  # hs-1001 is already briefed
            runs = Path(d) / "runs"
            r1 = score(Path(d), run_dir=runs / first["run_id"])
            self.assertEqual(r1["passed"], r1["total"])
            r2 = score(Path(d), run_dir=runs / second["run_id"])
            rerun = next(c for c in r2["cases"] if c["account"] == "hs-1001")
            # A correctly skipped, already-briefed account is not a failure: it is "not exercised this run".
            self.assertEqual((rerun["exercised"], rerun.get("note")), (False, "already briefed"))
            self.assertTrue(all(c["exercised"] for c in r2["cases"] if c["expect"] != "brief"))

    def test_expected_brief_dropped_by_the_agent_fails(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            t.write_audit_record("bank-sr26-2", "hs-1002", "drop",
                                 "Drop Lakeshore from this motion because the agent judged the fit wrong.",
                                 ["hubspot:company/hs-1002"])
            r = score(Path(d), run_dir=t.paths.run_dir)
            case = next(c for c in r["cases"] if c["account"] == "hs-1002")
            self.assertTrue(case["exercised"])
            self.assertFalse(case["properties"]["passes_output_gate"]["pass"])
            self.assertLess(r["passed"], r["total"])

    def test_mcp_session_scores_only_the_accounts_it_touched(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            t.screen_account("bank-sr26-2", "hs-1001"); t.check_applicability("bank-sr26-2", "hs-1001")
            t.route_contact("bank-sr26-2", "hs-1001")
            t.request_approval("bank-sr26-2", "hs-1001", offline_draft(t, "hs-1001"))
            r = score(Path(d), run_dir=t.paths.run_dir)
            self.assertEqual([c["account"] for c in r["cases"] if c["exercised"]], ["hs-1001"])
            self.assertEqual((r["passed"], r["total"]), (6, 6))

    def test_latest_brief_is_by_run_time_not_directory_name(self):
        with tempdir() as d:
            old, new = Path(d) / "runs/mcp-20260101T000000Z-aaaaaa", Path(d) / "runs/20260601T000000Z-bbbbbb"
            s = run(MOTION, Path(d), provider=TemplateProvider())
            good = Path(s["accounts"]["hs-1001"]["brief"]).read_text()
            for run_dir, text in ((old, "stale brief\n"), (new, good)):
                (run_dir / "briefs").mkdir(parents=True)
                (run_dir / "briefs/hubspot_company_hs-1001.md").write_text(text)
            case = next(c for c in score(Path(d))["cases"] if c["account"] == "hs-1001")
            self.assertTrue(case["properties"]["passes_output_gate"]["pass"], case["properties"]["passes_output_gate"])


if __name__ == "__main__":
    unittest.main()


class RerunScoring(unittest.TestCase):
    def test_already_briefed_accounts_are_not_failures_on_rerun(self):
        with tempdir() as d:
            out = Path(d)
            run(MOTION, out, provider=TemplateProvider())
            second = run(MOTION, out, provider=TemplateProvider())
            r = score(out, run_dir=out / "runs" / second["run_id"])
            case = next(c for c in r["cases"] if c["account"] == "hs-1001")
            self.assertEqual((case["exercised"], case.get("note")), (False, "already briefed"))
            self.assertEqual(r["passed"], r["total"])

    def test_rerun_that_drops_a_previously_briefed_account_fails(self):
        with tempdir() as d:
            out = Path(d)
            run(MOTION, out, provider=TemplateProvider())  # briefs hs-1002
            t = GovernedTools(out)
            t.write_audit_record("bank-sr26-2", "hs-1002", "drop",
                                 "Drop Lakeshore from this motion because the agent judged the fit wrong.",
                                 ["hubspot:company/hs-1002"])
            r = score(out, run_dir=t.paths.run_dir)
            case = next(c for c in r["cases"] if c["account"] == "hs-1002")
            self.assertTrue(case["exercised"])
            self.assertFalse(case["properties"]["passes_output_gate"]["pass"])
            self.assertLess(r["passed"], r["total"])

    def test_mcp_refusal_as_already_briefed_is_not_a_failure(self):
        with tempdir() as d:
            out = Path(d)
            run(MOTION, out, provider=TemplateProvider())  # briefs hs-1001
            t = GovernedTools(out)
            t.screen_account("bank-sr26-2", "hs-1001")
            with self.assertRaises(ToolFailure):
                t.check_applicability("bank-sr26-2", "hs-1001")
            r = score(out, run_dir=t.paths.run_dir)
            case = next(c for c in r["cases"] if c["account"] == "hs-1001")
            self.assertEqual((case["exercised"], case.get("note")), (False, "already briefed"))
