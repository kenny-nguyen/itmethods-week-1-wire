"""Rule R-17: prospect-touch audit.

R-17 (from the Reign constraint in the assignment packet): any agent action
that creates, updates, enriches, scores, or messages a person or account in
financial services must write an audit record before the action is considered
complete. If the record cannot be written, the action does not happen.

How that is enforced here: every such action goes through
`AuditTrail.perform(...)`. The caller does the work first (compute a score,
draft a brief), then hands over a `commit` callable that makes the result
real (persist it, attach it, queue it). `perform` validates the record,
writes it durably, and only then calls `commit`. If validation or the write
fails, `commit` is never called and `AuditBlocked` is raised: the action did
not happen, loudly.

Proposed readings this module depends on (AMBIGUITY-REGISTER.md):
- A-007: apply the rule to every segment, not only financial services. Set
  per playbook as `audit.required_for` = "all_segments" | "fs_only".
- A-008: records go to an append-only JSON Lines file behind `AuditSink`.
- A-024: the R-17 verbs are score, enrich, create, update, message.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol, TypeVar

from agent.governance.error_log import ErrorLog

R17_ACTIONS = ("create", "update", "enrich", "score", "message")
# Governance decisions are recorded in the same trail so an auditor sees them in sequence.
DECISION_ACTIONS = ("approve", "reject", "block", "unblock", "hold")
ALLOWED_ACTIONS = R17_ACTIONS + DECISION_ACTIONS

# "purpose - one sentence, specific, not 'engagement'" (R-17).
GENERIC_PURPOSES = {
    "engagement", "outreach", "marketing", "follow up", "follow-up", "nurture",
    "awareness", "prospecting", "sales", "touch", "update", "enrichment",
}
MIN_PURPOSE_WORDS = 6

PLACEHOLDER_NAMES = {
    "", "tbd", "todo", "unknown", "n/a", "na", "none", "null", "system", "agent",
    "bot", "admin", "replace me", "replace-me", "changeme", "someone", "anyone",
}

T = TypeVar("T")


class AuditBlocked(Exception):
    """The audit record could not be validated or written, so the action did not happen."""


def is_named_human(name: object) -> bool:
    """A named human: a real-looking person name, not a role, placeholder or agent id."""
    if not isinstance(name, str):
        return False
    cleaned = name.strip()
    if cleaned.lower() in PLACEHOLDER_NAMES:
        return False
    if re.search(r"\b(agent|bot|system|service)\b", cleaned.lower()):
        return False
    words = [w for w in re.split(r"\s+", cleaned) if re.search(r"[A-Za-z]", w)]
    return len(words) >= 2


def purpose_problems(purpose: object) -> list[str]:
    if not isinstance(purpose, str) or not purpose.strip():
        return ["purpose is empty"]
    text = purpose.strip().lower().rstrip(".")
    if text in GENERIC_PURPOSES:
        return [f"purpose is generic ({purpose!r}); R-17 requires one specific sentence"]
    if len(text.split()) < MIN_PURPOSE_WORDS:
        return [f"purpose is too short to be specific ({purpose!r})"]
    return []


def validate_record(record: dict) -> list[str]:
    problems: list[str] = []
    actor = record.get("actor") or {}
    if not actor.get("agent_id") or not actor.get("version"):
        problems.append("actor must carry agent id and version")
    if not is_named_human(record.get("principal")):
        problems.append(f"principal must be a named human, got {record.get('principal')!r}")
    if record.get("action") not in ALLOWED_ACTIONS:
        problems.append(f"action {record.get('action')!r} is not one of {ALLOWED_ACTIONS}")
    if not record.get("object"):
        problems.append("object (account or contact id) is missing")
    problems.extend(purpose_problems(record.get("purpose")))
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources or not all(isinstance(s, str) and s.strip() for s in sources):
        problems.append("sources must be a non-empty list of URLs or system ids")
    if not isinstance(record.get("send"), bool):
        problems.append("send must be true or false")
    elif record["send"]:
        if not is_named_human(record.get("approver")):
            problems.append(f"send is true, so approver must be a named human, got {record.get('approver')!r}")
        if record.get("blockable") is not True:
            problems.append("send is true, so the send must be blockable")
    return problems


class AuditSink(Protocol):
    def append(self, record: dict) -> None: ...


class JsonlAuditSink:
    """Append-only JSON Lines file. Stands in for a Reign audit store or HubSpot timeline (A-008)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, sort_keys=True) + "\n"
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())


@dataclass
class AuditTrail:
    sink: AuditSink
    agent_id: str
    agent_version: str
    principal: str
    playbook_id: str
    playbook_version: str
    run_id: str
    error_log: ErrorLog
    required_for: str = "all_segments"  # A-007 (proposed): or "fs_only"

    def perform(self, *, action: str, object_id: str, purpose: str, sources: list[str], fs: bool,
                commit: Callable[[], T], send: bool = False, approver: str | None = None,
                detail: dict | None = None) -> T:
        """Write the audit record, then complete the action. No record, no action."""
        record = {
            "record_id": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "rule": "R-17",
            "run_id": self.run_id,
            "playbook": {"id": self.playbook_id, "version": self.playbook_version},
            "actor": {"agent_id": self.agent_id, "version": self.agent_version},
            "principal": self.principal,
            "action": action,
            "object": object_id,
            "purpose": purpose,
            "sources": list(sources),
            "send": send,
            "approver": approver,
            "blockable": True if send else None,
            "fs": fs,
            "detail": detail or {},
        }
        required = fs or self.required_for == "all_segments"
        problems = validate_record(record)
        if problems:
            self._fail(record, "audit record invalid: " + "; ".join(problems), required)
        else:
            try:
                self.sink.append(record)
            except Exception as exc:  # any sink failure blocks the action
                self._fail(record, f"audit record could not be written: {exc}", required, exc)
        try:
            return commit()
        except Exception as exc:
            # The record above says the action happened; it did not. Say so in both logs, then re-raise.
            self.error_log.record("governance.commit", exc, context={"action": action, "object": object_id,
                                                                     "record_id": record["record_id"]})
            try:
                self.sink.append({**record, "record_id": str(uuid.uuid4()), "ts": datetime.now(timezone.utc).isoformat(),
                                  "detail": {"outcome": "failed", "of_record": record["record_id"], "error": str(exc)}})
            except Exception as sink_exc:
                self.error_log.record("governance.audit", sink_exc, context={"note": "failed-outcome record not written"})
            raise

    def _fail(self, record: dict, message: str, required: bool, exc: BaseException | None = None) -> None:
        context = {"action": record["action"], "object": record["object"], "fs": record["fs"],
                   "required": required}
        self.error_log.record("governance.audit", exc or message, context={**context, "reason": message},
                              severity="error" if required else "warning")
        if required:
            raise AuditBlocked(f"R-17 blocked {record['action']} on {record['object']}: {message}")
