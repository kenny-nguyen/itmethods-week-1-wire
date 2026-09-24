"""End-to-end runs of the first-motion playbook on fixtures, including the fail-closed paths."""

import json
import unittest
from pathlib import Path

from agent.feedback import kill_switch
from agent.feedback.decide import DecisionRefused, decide
from agent.governance.audit import validate_record
from agent.input import playbook as pbmod
from agent.processing.brief import ProviderError, TemplateProvider
from agent.run_playbook import RunRefused, run
from tests.helpers import tempdir

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = ROOT / "playbooks/reign-first-motion.jsonc"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []


def variant(tmp: Path, **changes) -> Path:
    pb = pbmod.load(PLAYBOOK)
    for dotted, value in changes.items():
        target, *keys = pb, *dotted.split("__")
        for k in keys[:-1]:
            target = target[int(k)] if isinstance(target, list) else target[k]
        target[keys[-1]] = value
    path = tmp / "playbook.jsonc"
    path.write_text(json.dumps(pb))
    return path


class FailingSink:
    def append(self, record):
        raise OSError("audit store unreachable")


class SloppyProvider(TemplateProvider):
    name = "sloppy"

    def draft(self, ctx):
        return super().draft(ctx).replace("## Why now\n", "## Why now\n- Reign makes you compliant [P-GATEWAY].\n")


class BrokenProvider:
    name = "broken"

    def draft(self, ctx):
        raise ProviderError("simulated outage")


class PipelineTests(unittest.TestCase):
    def test_end_to_end_default_playbook(self):
        with tempdir() as d:
            out = Path(d)
            s = run(PLAYBOOK, out, provider=TemplateProvider())
            self.assertEqual(s["metrics"]["drafted"], 1)
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "brief_pending_approval")
            self.assertEqual(s["accounts"]["hs-1001"]["status"], "preflight_hold")  # A-025 standing reading
            self.assertEqual(s["accounts"]["hs-1006"]["status"], "exclude")          # AI start-up filed as fintech
            self.assertIsNone(s["kill_switch"])
            req = json.loads(Path(s["outputs"][0]["approval_request"]).read_text())
            self.assertEqual((req["status"], req["send"], req["sender"]), ("pending", False, "none"))
            audit = jsonl(out / "audit.jsonl")
            self.assertTrue(audit)
            self.assertEqual([r for r in audit if validate_record(r)], [], "every audit record satisfies R-17")
            enriched = {r["object"] for r in audit if r["action"] == "enrich"}
            self.assertEqual(enriched, {"hubspot:company/hs-1001", "hubspot:company/hs-1002"},
                             "only in-profile accounts with a live play are enriched")
            creates = [r for r in audit if r["action"] == "create"]
            self.assertEqual(len(creates), 1)  # brief and approval request land together (Q-005, C1-a)
            self.assertIn("approval_request", creates[0]["detail"])
            self.assertTrue(all(r["send"] is False for r in audit if r["action"] != "approve"))

    def test_audit_store_down_blocks_everything_and_trips_kill_switch(self):
        with tempdir() as d:
            out = Path(d)
            s = run(PLAYBOOK, out, provider=TemplateProvider(), sink=FailingSink())
            self.assertEqual(s["metrics"]["drafted"], 0)
            self.assertGreater(s["metrics"]["audit_blocked"], 0)
            self.assertFalse((out / "runs" / s["run_id"] / "briefs").exists(), "no brief without an audit record")
            self.assertIsNotNone(s["kill_switch"])
            self.assertTrue(any(e["stage"] == "governance.audit" for e in jsonl(out / "errors.jsonl")))
            with self.assertRaises(RunRefused):
                run(PLAYBOOK, out, provider=TemplateProvider())

    def test_manual_kill_switch_refuses_run(self):
        with tempdir() as d:
            out = Path(d)
            kill_switch.engage(out / "state", "reign-first-motion", by="Kenny Nguyen", reason="drafts read generic")
            with self.assertRaises(RunRefused):
                run(PLAYBOOK, out, provider=TemplateProvider())
            self.assertFalse((out / "audit.jsonl").exists(), "a refused run touches no account")

    def test_sending_channel_without_named_approver_is_refused(self):
        with tempdir() as d:
            tmp = Path(d)
            with self.assertRaises(RunRefused) as cm:
                run(variant(tmp, approval__approvers=["TBD"]), tmp / "out", provider=TemplateProvider())
            self.assertIn("named humans", str(cm.exception))
            self.assertEqual(jsonl(tmp / "out/errors.jsonl")[0]["stage"], "input.playbook")

    def test_caveat_setting_briefs_the_canadian_bank(self):
        with tempdir() as d:
            tmp = Path(d)
            s = run(variant(tmp, plays__0__unconfirmed_applicability="brief_with_caveat"), tmp / "out",
                    provider=TemplateProvider())
            text = Path(s["accounts"]["hs-1001"]["brief"]).read_text()
            self.assertIn("SR 26-2 applicability requires confirmation", text)
            self.assertIn("OSFI Guideline E-23", text)
            self.assertNotIn("Chief Information Security Officer [", text, "CISO is on the do-not-route list")

    def test_sloppy_drafts_fail_the_gate_and_trip_the_kill_switch(self):
        with tempdir() as d:
            out = Path(d)
            s = run(PLAYBOOK, out, provider=SloppyProvider())
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "gate_failed")
            self.assertEqual(s["metrics"]["drafted"], 0)
            self.assertIn("gate-failures", s["kill_switch"]["reason"])

    def test_provider_outage_fails_the_account(self):
        with tempdir() as d:
            s = run(PLAYBOOK, Path(d), provider=BrokenProvider())
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "draft_failed")
            self.assertTrue(any(e["stage"] == "processing.draft" for e in jsonl(Path(d) / "errors.jsonl")))

    def test_no_volume_cap_allowed(self):  # operator decision A-037
        with tempdir() as d:
            tmp = Path(d)
            with self.assertRaises(RunRefused) as cm:
                run(variant(tmp, limits={"max_accounts_per_run": 1}), tmp / "out", provider=TemplateProvider())
            self.assertIn("A-037", str(cm.exception))

    def test_request_write_failure_leaves_no_brief(self):  # QA finding C1-a
        import agent.run_playbook as rp
        original = rp.write_json
        rp.write_json = lambda path, data: (_ for _ in ()).throw(OSError("disk full")) if "approvals" in str(path) else original(path, data)
        try:
            with tempdir() as d:
                out = Path(d)
                s = run(PLAYBOOK, out, provider=TemplateProvider())
                self.assertEqual(s["accounts"]["hs-1002"]["status"], "write_failed")
                self.assertEqual(list((out / "runs" / s["run_id"]).glob("briefs/*.md")), [])
                failed = [r for r in jsonl(out / "audit.jsonl") if r["detail"].get("outcome") == "failed"]
                self.assertEqual(len(failed), 1, "the audit trail says the create did not complete")
        finally:
            rp.write_json = original


class DecisionTests(unittest.TestCase):
    def _run(self, out):
        s = run(PLAYBOOK, out, provider=TemplateProvider())
        return Path(s["outputs"][0]["approval_request"])

    def test_only_a_named_approver_can_approve(self):
        with tempdir() as d:
            out = Path(d)
            req = self._run(out)
            for who in ("Someone Else", "system", ""):
                with self.subTest(who=who), self.assertRaises(DecisionRefused):
                    decide(req, approver=who, approve=True, reason="looks fine to me", out_dir=out)
            r = decide(req, approver="Kenny Nguyen", approve=True, reason="Sources and routing checked.", out_dir=out)
            self.assertEqual(r["status"], "approved_ready_to_send")
            rec = [x for x in jsonl(out / "audit.jsonl") if x["action"] == "approve"][0]
            self.assertEqual((rec["send"], rec["approver"], rec["blockable"]), (True, "Kenny Nguyen", True))
            with self.assertRaises(DecisionRefused):  # already decided
                decide(req, approver="Kenny Nguyen", approve=False, reason="changed my mind now", out_dir=out)

    def test_kill_switch_blocks_approval(self):
        with tempdir() as d:
            out = Path(d)
            req = self._run(out)
            kill_switch.engage(out / "state", "reign-first-motion", by="Kenny Nguyen", reason="stop the motion")
            with self.assertRaises(DecisionRefused):
                decide(req, approver="Kenny Nguyen", approve=True, reason="Sources and routing checked.", out_dir=out)
            self.assertEqual(json.loads(req.read_text())["status"], "pending")

    def test_rejection_trips_rejected_ratio_kill_criterion(self):
        with tempdir() as d:
            out = Path(d)
            req = self._run(out)
            decide(req, approver="Kenny Nguyen", approve=False, reason="Reads too generic for a CAE.", out_dir=out)
            self.assertIsNotNone(kill_switch.engaged(out / "state", "reign-first-motion"))

    def test_audit_failure_blocks_approval(self):
        with tempdir() as d:
            out = Path(d)
            req = self._run(out)
            with self.assertRaises(DecisionRefused):
                decide(req, approver="Kenny Nguyen", approve=True, reason="Sources and routing checked.",
                       out_dir=out, sink=FailingSink())
            self.assertEqual(json.loads(req.read_text())["status"], "pending")


if __name__ == "__main__":
    unittest.main()
