import tempfile
from pathlib import Path

from agent.governance.audit import AuditTrail, JsonlAuditSink
from agent.governance.error_log import ErrorLog


def make_trail(tmp: Path, *, sink=None, principal="Casey Morgan (fictional)", required_for="all_segments"):
    errors = ErrorLog(tmp / "errors.jsonl", run_id="test-run")
    trail = AuditTrail(
        sink=sink or JsonlAuditSink(tmp / "audit.jsonl"),
        agent_id="test-agent", agent_version="0.0.1", principal=principal,
        playbook_id="pb-test", playbook_version="1.0.0", run_id="test-run",
        error_log=errors, required_for=required_for,
    )
    return trail, errors


def tempdir():
    return tempfile.TemporaryDirectory()
