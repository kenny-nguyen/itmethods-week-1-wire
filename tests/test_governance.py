"""R-17 fail-closed behaviour and the separate error log."""

import json
import unittest
from pathlib import Path

from agent.governance.audit import AuditBlocked, is_named_human, validate_record
from tests.helpers import make_trail, tempdir

PURPOSE = "Score this account against the first Reign motion ICP before any brief is drafted."


class FailingSink:
    def append(self, record):
        raise OSError("disk full")


def read_jsonl(path: Path):
    return [json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []


class R17Tests(unittest.TestCase):
    def test_record_written_before_commit_runs(self):
        with tempdir() as d:
            tmp = Path(d)
            trail, _ = make_trail(tmp)
            seen = []

            def commit():
                seen.append(len(read_jsonl(tmp / "audit.jsonl")))
                return "done"

            result = trail.perform(action="score", object_id="acct-1", purpose=PURPOSE,
                                   sources=["hubspot:company/acct-1"], fs=True, commit=commit)
            self.assertEqual(result, "done")
            self.assertEqual(seen, [1], "commit must run only after the record is on disk")
            rec = read_jsonl(tmp / "audit.jsonl")[0]
            for field in ("actor", "principal", "action", "object", "purpose", "sources", "send"):
                self.assertIn(field, rec)
            self.assertEqual(rec["actor"], {"agent_id": "test-agent", "version": "0.0.1"})

    def test_unwritable_sink_blocks_action_for_fs(self):
        with tempdir() as d:
            tmp = Path(d)
            trail, _ = make_trail(tmp, sink=FailingSink())
            called = []
            with self.assertRaises(AuditBlocked):
                trail.perform(action="enrich", object_id="acct-1", purpose=PURPOSE,
                              sources=["clay:row/1"], fs=True, commit=lambda: called.append(1))
            self.assertEqual(called, [], "the action must not happen when the record cannot be written")
            errors = read_jsonl(tmp / "errors.jsonl")
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["stage"], "governance.audit")
            self.assertIn("disk full", errors[0]["message"])

    def test_every_r17_verb_is_blocked_on_failure(self):
        for verb in ("create", "update", "enrich", "score", "message"):
            with self.subTest(verb=verb), tempdir() as d:
                trail, _ = make_trail(Path(d), sink=FailingSink())
                with self.assertRaises(AuditBlocked):
                    trail.perform(action=verb, object_id="acct-1", purpose=PURPOSE,
                                  sources=["x"], fs=True, commit=lambda: None)

    def test_all_segments_policy_blocks_non_fs_too(self):
        with tempdir() as d:
            trail, _ = make_trail(Path(d), sink=FailingSink(), required_for="all_segments")
            with self.assertRaises(AuditBlocked):
                trail.perform(action="score", object_id="acct-2", purpose=PURPOSE,
                              sources=["x"], fs=False, commit=lambda: None)

    def test_fs_only_policy_lets_non_fs_proceed_but_logs_warning(self):
        with tempdir() as d:
            tmp = Path(d)
            trail, _ = make_trail(tmp, sink=FailingSink(), required_for="fs_only")
            self.assertEqual(trail.perform(action="score", object_id="acct-2", purpose=PURPOSE,
                                           sources=["x"], fs=False, commit=lambda: "ok"), "ok")
            self.assertEqual(read_jsonl(tmp / "errors.jsonl")[0]["severity"], "warning")
            with self.assertRaises(AuditBlocked):  # FS stays required under fs_only
                trail.perform(action="score", object_id="acct-1", purpose=PURPOSE,
                              sources=["x"], fs=True, commit=lambda: None)

    def test_generic_purpose_blocks(self):
        with tempdir() as d:
            trail, _ = make_trail(Path(d))
            for purpose in ("engagement", "Outreach.", "follow up with them"):
                with self.subTest(purpose=purpose), self.assertRaises(AuditBlocked):
                    trail.perform(action="message", object_id="c-1", purpose=purpose,
                                  sources=["x"], fs=True, commit=lambda: None)

    def test_placeholder_principal_blocks(self):
        with tempdir() as d:
            trail, _ = make_trail(Path(d), principal="TBD")
            with self.assertRaises(AuditBlocked):
                trail.perform(action="score", object_id="acct-1", purpose=PURPOSE,
                              sources=["x"], fs=True, commit=lambda: None)

    def test_missing_sources_blocks(self):
        with tempdir() as d:
            trail, _ = make_trail(Path(d))
            with self.assertRaises(AuditBlocked):
                trail.perform(action="score", object_id="acct-1", purpose=PURPOSE,
                              sources=[], fs=True, commit=lambda: None)

    def test_send_requires_named_approver(self):
        with tempdir() as d:
            trail, _ = make_trail(Path(d))
            with self.assertRaises(AuditBlocked):
                trail.perform(action="message", object_id="c-1", purpose=PURPOSE, sources=["x"],
                              fs=True, send=True, approver="system", commit=lambda: None)
            self.assertEqual(
                trail.perform(action="message", object_id="c-1", purpose=PURPOSE, sources=["x"],
                              fs=True, send=True, approver="Kenny Nguyen", commit=lambda: "queued"),
                "queued")

    def test_named_human(self):
        self.assertTrue(is_named_human("Kenny Nguyen"))
        self.assertTrue(is_named_human("Abbot Smith"))
        for bad in ("", "TBD", "agent", "Kenny", "brief-agent service", None, 42):
            with self.subTest(bad=bad):
                self.assertFalse(is_named_human(bad))

    def test_validate_record_rejects_unknown_action(self):
        problems = validate_record({"action": "delete"})
        self.assertTrue(any("action" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
