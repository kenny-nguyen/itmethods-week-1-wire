"""End-to-end runs of the first-motion playbook on fixtures, including the fail-closed paths."""

import json
import unittest
from pathlib import Path

from agent.feedback import kill_switch, trusted
from agent.feedback.decide import DecisionRefused, check_kill_criteria, decide
from agent.governance.error_log import ErrorLog
from agent.governance.audit import validate_record
from agent.input import playbook as pbmod
from agent.processing.brief import ProviderError, TemplateProvider
from agent.run_playbook import RunRefused, run
from tests.helpers import tempdir

ROOT = Path(__file__).resolve().parent.parent
MOTION = ROOT / "playbooks/motions/reign-first-motion.jsonc"
BANK = "bank-sr26-2"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []


def variant(tmp: Path, **changes) -> Path:
    """Copy playbooks/ into tmp, edit the bank playbook, return the copied motion path."""
    import shutil
    shutil.copytree(ROOT / "playbooks", tmp / "playbooks")
    path = tmp / "playbooks" / f"{BANK}.jsonc"
    pb = pbmod.load(path)
    for dotted, value in changes.items():
        target, *keys = pb, *dotted.split("__")
        for k in keys[:-1]:
            target = target[int(k)] if isinstance(target, list) else target[k]
        target[keys[-1]] = value
    path.write_text(json.dumps(pb))
    return tmp / "playbooks/motions/reign-first-motion.jsonc"


class FailingSink:
    def append(self, record):
        raise OSError("audit store unreachable")


class SloppyProvider(TemplateProvider):
    name = "sloppy"

    def draft(self, ctx):
        return super().draft(ctx).replace("## What changed\n", "## What changed\n- Reign makes you compliant [P-GATEWAY].\n")


class BrokenProvider:
    name = "broken"

    def draft(self, ctx):
        raise ProviderError("simulated outage")


class PipelineTests(unittest.TestCase):
    def test_end_to_end_default_playbook(self):
        with tempdir() as d:
            out = Path(d)
            s = run(MOTION, out, provider=TemplateProvider())
            bank = s["playbooks"][BANK]
            self.assertEqual(bank["metrics"]["drafted"], 2)
            self.assertIsNone(bank.get("kill_switch"))
            for aid in ("hs-1001", "hs-1002"):  # A-044: both banks get the structured brief
                self.assertEqual(s["accounts"][aid]["status"], "brief_pending_owner_decision")
            self.assertEqual(s["accounts"]["hs-1006"]["status"], "hold")             # D-040: category unclear, human confirms
            self.assertEqual(s["accounts"]["hs-1007"]["status"], "watch")            # A-040
            self.assertEqual([w["account"] for w in s["watch_list"]], ["hs-1007"])
            for pid in ("biopharma-fda-pccp", "defense-forge-first"):
                self.assertEqual(s["playbooks"][pid]["trigger_status"], "not_implemented")
                self.assertTrue(s["playbooks"][pid]["reason"])
            req = json.loads(Path(s["outputs"][0]["approval_request"]).read_text())
            self.assertEqual((req["status"], req["send"], req["sender"]), ("pending", False, "none"))
            self.assertEqual(req["route_to"], {"account_owner": "Kenny Nguyen"})  # A-043
            audit = jsonl(out / "audit.jsonl")
            self.assertTrue(audit)
            self.assertEqual([r for r in audit if validate_record(r)], [], "every audit record satisfies R-17")
            enriched = {r["object"] for r in audit if r["action"] == "enrich"}
            self.assertEqual(enriched, {"hubspot:company/hs-1001", "hubspot:company/hs-1002"},
                             "only in-profile accounts with a live play are enriched")
            creates = [r for r in audit if r["action"] == "create"]
            self.assertEqual(len(creates), 2)  # one per bank: brief and request land together (Q-005, C1-a)
            self.assertTrue(all("approval_request" in r["detail"] for r in creates))
            self.assertEqual(len([r for r in audit if r["action"] == "route"]), 2)  # A-024
            self.assertEqual({r["playbook"]["id"] for r in audit if r["action"] == "create"}, {BANK})
            self.assertTrue(all(r["send"] is False for r in audit if r["action"] != "approve"))

    def test_audit_store_down_blocks_everything_and_trips_kill_switch(self):
        with tempdir() as d:
            out = Path(d)
            s = run(MOTION, out, provider=TemplateProvider(), sink=FailingSink())
            self.assertEqual(s["playbooks"][BANK]["metrics"]["drafted"], 0)
            self.assertGreater(s["playbooks"][BANK]["metrics"]["audit_blocked"], 0)
            self.assertFalse((out / "runs" / s["run_id"] / "briefs").exists(), "no brief without an audit record")
            self.assertIsNotNone(s["playbooks"][BANK]["kill_switch"])
            self.assertTrue(any(e["stage"] == "governance.audit" for e in jsonl(out / "errors.jsonl")))
            again = run(MOTION, out, provider=TemplateProvider())
            self.assertIn("kill switch", again["playbooks"][BANK]["skipped"])

    def test_scheduled_rerun_does_not_brief_twice(self):  # D-029
        with tempdir() as d:
            out = Path(d)
            first = run(MOTION, out, provider=TemplateProvider())
            second = run(MOTION, out, provider=TemplateProvider())
            self.assertEqual(len(first["outputs"]), 2)
            self.assertEqual(second["outputs"], [])
            self.assertEqual(second["accounts"]["hs-1002"]["status"], "already_briefed")

    def test_manual_kill_switch_skips_the_playbook(self):
        with tempdir() as d:
            out = Path(d)
            kill_switch.engage(out / "state", BANK, by="Kenny Nguyen", reason="drafts read generic")
            s = run(MOTION, out, provider=TemplateProvider())
            self.assertIn("kill switch", s["playbooks"][BANK]["skipped"])
            self.assertEqual(s["outputs"], [])
            self.assertFalse([r for r in jsonl(out / "audit.jsonl") if r["action"] == "enrich"],
                             "no account is enriched for a stopped playbook")

    def test_sending_channel_without_named_approver_is_refused(self):
        with tempdir() as d:
            tmp = Path(d)
            with self.assertRaises(RunRefused) as cm:
                run(variant(tmp, approval__approvers=["TBD"]), tmp / "out", provider=TemplateProvider())
            self.assertIn("named humans", str(cm.exception))
            self.assertEqual(jsonl(tmp / "out/errors.jsonl")[0]["stage"], "input.playbook")

    def test_canadian_bank_gets_the_structured_brief(self):  # A-044
        with tempdir() as d:
            s = run(MOTION, Path(d), provider=TemplateProvider())
            text = Path(s["accounts"]["hs-1001"]["brief"]).read_text()
            self.assertIn("SR 26-2 applicability requires confirmation", text)
            self.assertIn("OSFI Guideline E-23", text)
            self.assertIn("## What depends on structure (confirm)", text)
            self.assertIn("DORA", text)
            self.assertNotIn("Chief Information Security Officer [", text, "CISO is on the do-not-route list")

    def test_hold_setting_holds_the_canadian_bank(self):  # A-025 general case
        with tempdir() as d:
            tmp = Path(d)
            s = run(variant(tmp, unconfirmed_applicability="hold"), tmp / "out", provider=TemplateProvider())
            self.assertEqual(s["accounts"]["hs-1001"]["status"], "preflight_hold")

    def test_account_without_owner_is_held(self):  # A-043
        import agent.run_playbook as rp
        from dataclasses import replace as dc_replace
        io = rp._load_inputs(ROOT)

        class NoOwner:
            def list_accounts(self):
                return [dc_replace(a, owner=None) for a in io["accounts"].list_accounts()]

        with tempdir() as d:
            s = run(MOTION, Path(d), provider=TemplateProvider(), inputs={**io, "accounts": NoOwner()})
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "preflight_hold")
            self.assertEqual(s["outputs"], [])

    def test_sloppy_drafts_fail_the_gate_but_two_are_not_a_sample(self):  # D-041
        with tempdir() as d:
            out = Path(d)
            s = run(MOTION, out, provider=SloppyProvider())
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "gate_failed")
            metrics = s["playbooks"][BANK]["metrics"]
            self.assertEqual((metrics["drafted"], metrics["gate_failed"], metrics["gate_failed_ratio"]), (0, 2, None))
            self.assertIsNone(s["playbooks"][BANK].get("kill_switch"))

    def test_provider_outage_fails_the_account(self):
        with tempdir() as d:
            s = run(MOTION, Path(d), provider=BrokenProvider())
            self.assertEqual(s["accounts"]["hs-1002"]["status"], "draft_failed")
            err = [e for e in jsonl(Path(d) / "errors.jsonl") if e["stage"] == "processing.draft"]
            self.assertTrue(err)
            self.assertIn("Recovery:", err[0]["message"], "A-033: failures name the fix")

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
                s = run(MOTION, out, provider=TemplateProvider())
                self.assertEqual(s["accounts"]["hs-1002"]["status"], "write_failed")
                self.assertEqual(list((out / "runs" / s["run_id"]).glob("briefs/*.md")), [])
                failed = [r for r in jsonl(out / "audit.jsonl") if r["detail"].get("outcome") == "failed"]
                self.assertEqual(len(failed), 2, "the audit trail says each create did not complete")
        finally:
            rp.write_json = original


class DecisionTests(unittest.TestCase):
    def _run(self, out):
        s = run(MOTION, out, provider=TemplateProvider())
        return Path(next(o["approval_request"] for o in s["outputs"] if o["account"] == "hs-1002"))

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
            kill_switch.engage(out / "state", BANK, by="Kenny Nguyen", reason="stop the motion")
            with self.assertRaises(DecisionRefused):
                decide(req, approver="Kenny Nguyen", approve=True, reason="Sources and routing checked.", out_dir=out)
            self.assertEqual(json.loads(req.read_text())["status"], "pending")

    def test_rejection_ratio_needs_minimum_sample(self):  # D-041
        with tempdir() as d:
            out = Path(d)
            req = self._run(out)
            decide(req, approver="Kenny Nguyen", approve=False, reason="Reads too generic for a CAE.", out_dir=out)
            self.assertIsNone(kill_switch.engaged(out / "state", BANK))  # one decision is not a sample
            pb = trusted.load_trusted(BANK)
            trail = trusted.trail_for(pb, out, "test", ErrorLog(out / "errors.jsonl", "test"))
            for i, status in enumerate(["rejected", "rejected", "approved_ready_to_send", "rejected"]):
                (req.parent / f"extra-{i}.json").write_text(json.dumps({"status": status}))
            hits = check_kill_criteria(pb, out, req.parent, trail, by="Kenny Nguyen")
            self.assertEqual([h["id"] for h in hits], ["approver-rejections"])  # 4 of 5 rejected
            self.assertIsNotNone(kill_switch.engaged(out / "state", BANK))

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
