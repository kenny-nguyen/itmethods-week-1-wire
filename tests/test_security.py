"""Regression tests for the independent security review findings (process log D-020 onwards)."""

import json
import shutil
import unittest
from pathlib import Path

from agent.feedback import kill_switch
from agent.feedback.decide import DecisionRefused, decide
from agent.feedback.kill import KillRefused, kill
from agent.feedback.report import report
from agent.governance.audit import AuditTrail, JsonlAuditSink
from agent.governance.error_log import ErrorLog
from agent.processing.brief import TemplateProvider
from agent.run_playbook import run
from tests.helpers import tempdir

ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = ROOT / "playbooks/reign-first-motion.jsonc"
REASON = "Sources and routing checked."


def jsonl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines()] if Path(p).exists() else []


class FailingSink:
    def append(self, record):
        raise OSError("audit store unreachable")


def one_request(out: Path) -> Path:
    s = run(PLAYBOOK, out, provider=TemplateProvider())
    return Path(s["outputs"][0]["approval_request"])


class ApprovalAuthorization(unittest.TestCase):  # S-1
    def test_editing_the_request_cannot_change_the_approver_list(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            evil_dir = Path(d) / "evil"
            evil_dir.mkdir()
            evil = PLAYBOOK.read_text().replace('"approvers": ["Kenny Nguyen"]', '"approvers": ["Mallory Attacker"]')
            (evil_dir / "reign-first-motion.jsonc").write_text(evil)
            req = json.loads(req_path.read_text())
            req["playbook_path"] = str(evil_dir / "reign-first-motion.jsonc")  # ignored now
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Mallory Attacker", approve=True, reason=REASON, out_dir=out)
            req["playbook"]["id"] = "reign-first-motion-evil"
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Mallory Attacker", approve=True, reason=REASON, out_dir=out)
            self.assertFalse([r for r in jsonl(out / "audit.jsonl") if r["action"] == "approve"])

    def test_changed_playbook_since_request_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            pb_dir = Path(d) / "playbooks"
            shutil.copytree(ROOT / "playbooks", pb_dir)
            req_path = one_request(out)
            f = pb_dir / "reign-first-motion.jsonc"
            f.write_text(f.read_text().replace('"approvers": ["Kenny Nguyen"]', '"approvers": ["Kenny Nguyen", "Mallory Attacker"]'))
            with self.assertRaises(DecisionRefused) as cm:
                decide(req_path, approver="Mallory Attacker", approve=True, reason=REASON, out_dir=out, playbooks_dir=pb_dir)
            self.assertIn("changed", str(cm.exception))


class OutputRootPinned(unittest.TestCase):  # S-2
    def test_request_outside_output_root_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            kill_switch.engage(out / "state", "reign-first-motion", by="Kenny Nguyen", reason="stop the motion")
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Kenny Nguyen", approve=True, reason=REASON, out_dir=Path(d) / "elsewhere")


class KillSwitchControl(unittest.TestCase):  # S-3
    def test_only_accountable_people_can_clear_and_both_directions_are_audited(self):
        with tempdir() as d:
            out = Path(d)
            with self.assertRaises(KillRefused):
                kill("reign-first-motion", by="Random Person", reason="just because really", clear=False, out_dir=out)
            kill("reign-first-motion", by="Kenny Nguyen", reason="drafts read generic", clear=False, out_dir=out)
            with self.assertRaises(KillRefused):
                kill("reign-first-motion", by="Random Person", reason="looks fine now", clear=True, out_dir=out)
            with self.assertRaises(KillRefused):
                kill("reign-first-motion", by="Kenny Nguyen", reason="x", clear=True, out_dir=out)
            self.assertIsNotNone(kill_switch.engaged(out / "state", "reign-first-motion"))
            kill("reign-first-motion", by="Kenny Nguyen", reason="reviewed the drafts", clear=True, out_dir=out)
            self.assertEqual([r["action"] for r in jsonl(out / "audit.jsonl")], ["block", "unblock"])

    def test_clear_refused_when_audit_fails(self):
        with tempdir() as d:
            out = Path(d)
            kill("reign-first-motion", by="Kenny Nguyen", reason="drafts read generic", clear=False, out_dir=out)
            with self.assertRaises(KillRefused):
                kill("reign-first-motion", by="Kenny Nguyen", reason="reviewed the drafts", clear=True,
                     out_dir=out, sink=FailingSink())
            self.assertIsNotNone(kill_switch.engaged(out / "state", "reign-first-motion"))

    def test_path_traversal_ids_rejected(self):
        with tempdir() as d:
            for bad in ("../../runs/x/approvals/y", "a/b", "UPPER", ""):
                with self.subTest(bad=bad):
                    with self.assertRaises(ValueError):
                        kill_switch.clear(Path(d), bad)
                    with self.assertRaises(KillRefused):
                        kill(bad, by="Kenny Nguyen", reason="reviewed the drafts", clear=True, out_dir=Path(d))


class AuditOutcome(unittest.TestCase):  # S-4
    def test_failed_commit_is_recorded_as_failed(self):
        with tempdir() as d:
            tmp = Path(d)
            trail = AuditTrail(JsonlAuditSink(tmp / "audit.jsonl"), "a", "1", "Kenny Nguyen", "pb", "1", "r",
                               ErrorLog(tmp / "errors.jsonl"))

            def boom():
                raise PermissionError("read-only")

            with self.assertRaises(PermissionError):
                trail.perform(action="approve", object_id="acct", fs=True, commit=boom, send=True,
                              approver="Kenny Nguyen", sources=["x"],
                              purpose="Approve the brief for the account to be sent by its owner.")
            recs = jsonl(tmp / "audit.jsonl")
            self.assertEqual(len(recs), 2)
            self.assertEqual(recs[1]["detail"]["outcome"], "failed")
            self.assertEqual(recs[1]["detail"]["of_record"], recs[0]["record_id"])
            self.assertEqual(jsonl(tmp / "errors.jsonl")[0]["stage"], "governance.commit")


class QualityKillCriteria(unittest.TestCase):  # operator decision A-037
    def test_wrong_account_report_engages_kill_switch(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            hits = report(req_path, by="Kenny Nguyen", kind="wrong_account",
                          detail="Brief names the wrong parent company.", out_dir=out)
            self.assertEqual([h["id"] for h in hits], ["wrong-account"])
            self.assertIsNotNone(kill_switch.engaged(out / "state", "reign-first-motion"))
            self.assertEqual([r["action"] for r in jsonl(out / "audit.jsonl")][-2:], ["update", "block"])


if __name__ == "__main__":
    unittest.main()
