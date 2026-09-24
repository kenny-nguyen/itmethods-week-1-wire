"""Regression tests for the independent security review findings."""

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
MOTION = ROOT / "playbooks/motions/reign-first-motion.jsonc"
BANK = "bank-sr26-2"
REASON = "Sources and routing checked."


def jsonl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines()] if Path(p).exists() else []


class FailingSink:
    def append(self, record):
        raise OSError("audit store unreachable")


def one_request(out: Path) -> Path:
    s = run(MOTION, out, provider=TemplateProvider())
    return Path(next(o["approval_request"] for o in s["outputs"] if o["account"] == "hs-1002"))


class ApprovalAuthorization(unittest.TestCase):  # S-1
    def test_editing_the_request_cannot_change_the_approver_list(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            evil_dir = Path(d) / "evil"
            evil_dir.mkdir()
            evil = (ROOT / f"playbooks/{BANK}.jsonc").read_text().replace('"approvers": ["Jordan Reyes (fictional)"]', '"approvers": ["Mallory Attacker"]')
            (evil_dir / f"{BANK}.jsonc").write_text(evil)
            req = json.loads(req_path.read_text())
            req["playbook_path"] = str(evil_dir / f"{BANK}.jsonc")  # ignored now
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Mallory Attacker", approve=True, reason=REASON, out_dir=out)
            req["playbook"]["id"] = "bank-sr26-2-evil"
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
            f = pb_dir / f"{BANK}.jsonc"
            f.write_text(f.read_text().replace('"approvers": ["Jordan Reyes (fictional)"]', '"approvers": ["Jordan Reyes (fictional)", "Mallory Attacker"]'))
            with self.assertRaises(DecisionRefused) as cm:
                decide(req_path, approver="Mallory Attacker", approve=True, reason=REASON, out_dir=out, playbooks_dir=pb_dir)
            self.assertIn("changed", str(cm.exception))


class RequestBoundToAuditTrail(unittest.TestCase):  # QA pass 2, C2
    def test_swapped_playbook_without_hash_is_refused_and_kill_switch_holds(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            kill_switch.engage(out / "state", BANK, by="Jordan Reyes (fictional)", reason="stop the motion")
            req = json.loads(req_path.read_text())
            req["playbook"]["id"] = "biopharma-fda-pccp"
            del req["playbook_sha256"]
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Jordan Reyes (fictional)", approve=True, reason=REASON, out_dir=out)

    def test_swapped_account_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            req = json.loads(req_path.read_text())
            req["account"]["id"] = "hubspot:company/hs-1001"
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused) as cm:
                decide(req_path, approver="Jordan Reyes (fictional)", approve=True, reason=REASON, out_dir=out)
            self.assertIn("audited create record", str(cm.exception))

    def test_missing_hash_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            req = json.loads(req_path.read_text())
            del req["playbook_sha256"]
            req_path.write_text(json.dumps(req))
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Jordan Reyes (fictional)", approve=True, reason=REASON, out_dir=out)


class OwnerOnly(unittest.TestCase):  # A-043: the named account owner decides
    def test_listed_approver_who_is_not_the_owner_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            import agent.feedback.decide as dm
            original = dm.account_owner
            dm.account_owner = lambda system_id: "Somebody Else"
            try:
                with self.assertRaises(DecisionRefused) as cm:
                    decide(req_path, approver="Jordan Reyes (fictional)", approve=True, reason=REASON, out_dir=out)
                self.assertIn("account owner", str(cm.exception))
            finally:
                dm.account_owner = original


class OutputRootPinned(unittest.TestCase):  # S-2
    def test_request_outside_output_root_is_refused(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            kill_switch.engage(out / "state", BANK, by="Jordan Reyes (fictional)", reason="stop the motion")
            with self.assertRaises(DecisionRefused):
                decide(req_path, approver="Jordan Reyes (fictional)", approve=True, reason=REASON, out_dir=Path(d) / "elsewhere")


class KillSwitchControl(unittest.TestCase):  # S-3
    def test_only_accountable_people_can_clear_and_both_directions_are_audited(self):
        with tempdir() as d:
            out = Path(d)
            with self.assertRaises(KillRefused):
                kill(BANK, by="Random Person", reason="just because really", clear=False, out_dir=out)
            kill(BANK, by="Jordan Reyes (fictional)", reason="drafts read generic", clear=False, out_dir=out)
            with self.assertRaises(KillRefused):
                kill(BANK, by="Random Person", reason="looks fine now", clear=True, out_dir=out)
            with self.assertRaises(KillRefused):
                kill(BANK, by="Jordan Reyes (fictional)", reason="x", clear=True, out_dir=out)
            self.assertIsNotNone(kill_switch.engaged(out / "state", BANK))
            kill(BANK, by="Jordan Reyes (fictional)", reason="reviewed the drafts", clear=True, out_dir=out)
            self.assertEqual([r["action"] for r in jsonl(out / "audit.jsonl")], ["block", "unblock"])

    def test_clear_refused_when_audit_fails(self):
        with tempdir() as d:
            out = Path(d)
            kill(BANK, by="Jordan Reyes (fictional)", reason="drafts read generic", clear=False, out_dir=out)
            with self.assertRaises(KillRefused):
                kill(BANK, by="Jordan Reyes (fictional)", reason="reviewed the drafts", clear=True,
                     out_dir=out, sink=FailingSink())
            self.assertIsNotNone(kill_switch.engaged(out / "state", BANK))

    def test_path_traversal_ids_rejected(self):
        with tempdir() as d:
            for bad in ("../../runs/x/approvals/y", "a/b", "UPPER", ""):
                with self.subTest(bad=bad):
                    with self.assertRaises(ValueError):
                        kill_switch.clear(Path(d), bad)
                    with self.assertRaises(KillRefused):
                        kill(bad, by="Jordan Reyes (fictional)", reason="reviewed the drafts", clear=True, out_dir=Path(d))


class ClearResetsQualityCounts(unittest.TestCase):  # QA pass 2, C5
    def test_complaint_before_clear_does_not_retrip(self):
        with tempdir() as d:
            out = Path(d) / "out"
            req_path = one_request(out)
            report(req_path, by="Jordan Reyes (fictional)", kind="complaint", detail="Prospect said the brief misread things.", out_dir=out)
            self.assertIsNotNone(kill_switch.engaged(out / "state", BANK))
            kill(BANK, by="Jordan Reyes (fictional)", reason="reviewed the complaint with the prospect", clear=True, out_dir=out)
            s = run(MOTION, out, provider=TemplateProvider())
            self.assertIsNone(s["playbooks"][BANK].get("kill_switch"))
            self.assertEqual(s["playbooks"][BANK]["metrics"]["complaints"], 0)


class AuditOutcome(unittest.TestCase):  # S-4
    def test_failed_commit_is_recorded_as_failed(self):
        with tempdir() as d:
            tmp = Path(d)
            trail = AuditTrail(JsonlAuditSink(tmp / "audit.jsonl"), "a", "1", "Jordan Reyes (fictional)", "pb", "1", "r",
                               ErrorLog(tmp / "errors.jsonl"))

            def boom():
                raise PermissionError("read-only")

            with self.assertRaises(PermissionError):
                trail.perform(action="approve", object_id="acct", fs=True, commit=boom, send=True,
                              approver="Jordan Reyes (fictional)", sources=["x"],
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
            hits = report(req_path, by="Jordan Reyes (fictional)", kind="wrong_account",
                          detail="Brief names the wrong parent company.", out_dir=out)
            self.assertEqual([h["id"] for h in hits], ["wrong-account"])
            self.assertIsNotNone(kill_switch.engaged(out / "state", BANK))
            self.assertEqual([r["action"] for r in jsonl(out / "audit.jsonl")][-2:], ["update", "block"])


if __name__ == "__main__":
    unittest.main()


class SeparationOfDuties(unittest.TestCase):
    def test_principal_cannot_approve_their_own_class_of_action(self):
        import re as _re
        with tempdir() as d:
            pb_dir = Path(d) / "playbooks"
            shutil.copytree(ROOT / "playbooks", pb_dir)
            f = pb_dir / f"{BANK}.jsonc"
            f.write_text(_re.sub(r'"approvers": \[[^\]]*\]', '"approvers": ["Jordan Reyes (fictional)", "Casey Morgan (fictional)"]',
                                 f.read_text()))
            out = Path(d) / "out"
            s = run(pb_dir / "motions/reign-first-motion.jsonc", out, provider=TemplateProvider())
            req = Path(next(o["approval_request"] for o in s["outputs"] if o["account"] == "hs-1002"))
            with self.assertRaises(DecisionRefused) as cm:
                decide(req, approver="Casey Morgan (fictional)", approve=True, reason=REASON, out_dir=out,
                       playbooks_dir=pb_dir)
            self.assertIn("principal", str(cm.exception))
