"""The governed MCP tools: the agent decides, the code enforces (A-046)."""

import json
import unittest
from pathlib import Path

from agent.feedback import kill_switch
from agent.input.base import InputError
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext, TemplateProvider
from agent.run_playbook import _load_inputs
from agent.tools import ROOT, GovernedTools, ToolFailure
from tests.helpers import tempdir

BANK = "bank-sr26-2"


def jsonl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines()] if Path(p).exists() else []


def offline_draft(tools: GovernedTools, account: str) -> str:
    """Stand-in for the agent's own draft: the offline-test-mode template, built from the tools' session state."""
    pb, _ = tools._playbook(BANK)
    return TemplateProvider().draft(tools._context(pb, tools.state[(BANK, account)]))


class GovernedToolTests(unittest.TestCase):
    def test_full_path_writes_audited_brief_for_owner(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            self.assertIn("SR-26-2", [p["trigger"]["id"] for p in t.list_playbooks()["playbooks"]])
            src = t.fetch_source("SR-26-2")
            self.assertTrue(all(s["verified"] and s["url"] for s in src["sources"]))
            self.assertEqual(t.screen_account(BANK, "hs-1001")["decision"], "include")
            app = t.check_applicability(BANK, "hs-1001")
            self.assertEqual((app["status"], app["must_include_phrase"]), (pf.READY, pf.CAVEAT))
            lanes = t.route_contact(BANK, "hs-1001")
            self.assertNotIn("Chief Information Security Officer",
                             [c["title"] for cs in lanes["lanes"].values() for c in cs])
            draft = offline_draft(t, "hs-1001")
            self.assertTrue(t.check_claims(BANK, "hs-1001", draft)["passed"])
            res = t.request_approval(BANK, "hs-1001", draft)
            self.assertEqual((res["route_to"], res["sent"]), ("Kenny Nguyen", False))
            actions = [r["action"] for r in jsonl(Path(d) / "audit.jsonl")]
            self.assertEqual(actions, ["enrich", "score", "route", "create"])

    def test_excluded_and_watched_accounts_are_closed(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            with self.assertRaises(ToolFailure):  # wrong segment for this playbook
                t.screen_account(BANK, "hs-1007")
            r = t.screen_account(BANK, "hs-1010")  # credit union under the headcount floor
            self.assertTrue(r["do_not_contact"])
            for call in (lambda: t.check_applicability(BANK, "hs-1010"), lambda: t.route_contact(BANK, "hs-1010"),
                         lambda: t.request_approval(BANK, "hs-1010", "x")):
                with self.assertRaises(ToolFailure) as cm:
                    call()
                self.assertIn("Recovery:", str(cm.exception))
            self.assertNotIn("enrich", [r["action"] for r in jsonl(Path(d) / "audit.jsonl")])

    def test_tools_must_run_in_order(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            with self.assertRaises(ToolFailure):
                t.route_contact(BANK, "hs-1002")

    def test_request_approval_enforces_the_gate(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            t.screen_account(BANK, "hs-1002"); t.check_applicability(BANK, "hs-1002"); t.route_contact(BANK, "hs-1002")
            bad = offline_draft(t, "hs-1002").replace("## What changed\n", "## What changed\n- SR 26-2 applies to the bank [src-sr26-2].\n")
            self.assertFalse(t.check_claims(BANK, "hs-1002", bad)["passed"])
            with self.assertRaises(ToolFailure):
                t.request_approval(BANK, "hs-1002", bad)
            self.assertFalse(list(Path(d).glob("runs/*/briefs/*.md")))

    def test_unimplemented_trigger_and_kill_switch_refuse(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            with self.assertRaises(ToolFailure):
                t.fetch_source("FDA-PCCP-2025")
            with self.assertRaises(ToolFailure):
                t.screen_account("biopharma-fda-pccp", "hs-1003")
            kill_switch.engage(Path(d) / "state", BANK, by="Kenny Nguyen", reason="stop the motion now")
            with self.assertRaises(ToolFailure):
                t.screen_account(BANK, "hs-1002")

    def test_agent_can_record_hold_or_drop_but_nothing_else(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            r = t.write_audit_record(BANK, "hs-1002", "hold",
                                     "Hold the Lakeshore brief until the owner confirms the US entity list.",
                                     ["hubspot:company/hs-1002"])
            self.assertEqual(r["decision"], "hold")
            with self.assertRaises(ToolFailure):
                t.write_audit_record(BANK, "hs-1002", "message", "Send the brief to the bank's risk officer now.", ["x"])
            with self.assertRaises(ToolFailure):  # R-17: a generic purpose is refused
                t.write_audit_record(BANK, "hs-1002", "drop", "engagement", ["x"])

    def test_audit_failure_blocks_tool(self):
        class FailingSink:
            def append(self, record):
                raise OSError("audit store unreachable")

        with tempdir() as d:
            t = GovernedTools(Path(d), sink=FailingSink())
            with self.assertRaises(ToolFailure) as cm:
                t.screen_account(BANK, "hs-1002")
            self.assertIn("nothing happened", str(cm.exception))

    def test_audit_failure_engages_kill_switch(self):
        class FailingSink:
            def append(self, record):
                raise OSError("audit store unreachable")

        with tempdir() as d:
            t = GovernedTools(Path(d), sink=FailingSink())
            with self.assertRaises(ToolFailure):
                t.screen_account(BANK, "hs-1002")
            killed = kill_switch.engaged(Path(d) / "state", BANK)
            self.assertIn("audit-write-failure", killed["reason"])
            with self.assertRaises(ToolFailure) as cm:
                t.screen_account(BANK, "hs-1001")
            self.assertIn("kill switch", str(cm.exception))

    def test_gate_refusal_engages_kill_switch(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            t.screen_account(BANK, "hs-1002"); t.check_applicability(BANK, "hs-1002"); t.route_contact(BANK, "hs-1002")
            bad = offline_draft(t, "hs-1002").replace("## What changed\n", "## What changed\n- SR 26-2 applies to the bank [src-sr26-2].\n")
            with self.assertRaises(ToolFailure):
                t.request_approval(BANK, "hs-1002", bad)
            self.assertIn("gate-failures", kill_switch.engaged(Path(d) / "state", BANK)["reason"])
            self.assertIn("block", [r["action"] for r in jsonl(Path(d) / "audit.jsonl")])

    def test_clean_session_leaves_kill_switch_off(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            t.screen_account(BANK, "hs-1001"); t.check_applicability(BANK, "hs-1001"); t.route_contact(BANK, "hs-1001")
            t.request_approval(BANK, "hs-1001", offline_draft(t, "hs-1001"))
            self.assertIsNone(kill_switch.engaged(Path(d) / "state", BANK))

    def test_system_id_works_through_every_step(self):
        with tempdir() as d:
            t = GovernedTools(Path(d))
            sid = "hubspot:company/hs-1001"
            self.assertEqual(t.screen_account(BANK, sid)["decision"], "include")
            self.assertEqual(t.check_applicability(BANK, sid)["status"], pf.READY)
            t.route_contact(BANK, sid)
            draft = offline_draft(t, "hs-1001")
            self.assertTrue(t.check_claims(BANK, sid, draft)["passed"])
            self.assertFalse(t.request_approval(BANK, sid, draft)["sent"])

    def test_adapter_failures_are_logged_with_recovery(self):
        class Broken:
            def enrich(self, account_id):
                raise InputError("Clay timed out")

            def list_accounts(self):
                raise InputError("HubSpot timed out")

            def get(self, trigger_id):
                raise InputError("feed unreachable")

        for key, call in (("enrichment", lambda t: t.screen_account(BANK, "hs-1001")),
                          ("accounts", lambda t: t.list_playbooks()),
                          ("feed", lambda t: (t.screen_account(BANK, "hs-1001"), t.check_applicability(BANK, "hs-1001")))):
            with self.subTest(adapter=key), tempdir() as d:
                t = GovernedTools(Path(d), inputs={**_load_inputs(ROOT), key: Broken()})
                with self.assertRaises(ToolFailure) as cm:
                    call(t)
                self.assertIn("Recovery:", str(cm.exception))
                self.assertTrue(any("timed out" in e["message"] or "unreachable" in e["message"]
                                    for e in jsonl(Path(d) / "errors.jsonl")))


if __name__ == "__main__":
    unittest.main()
