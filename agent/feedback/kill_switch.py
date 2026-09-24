"""The kill switch: a state file per playbook. While it exists, no run starts and no approval is accepted.

Engaging never depends on the audit trail succeeding: stopping is the safe
direction, so the file is written first and the audit record second.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _path(state_dir: Path, playbook_id: str) -> Path:
    return Path(state_dir) / "kill" / f"{playbook_id}.json"


def engaged(state_dir: Path, playbook_id: str) -> dict | None:
    p = _path(state_dir, playbook_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def engage(state_dir: Path, playbook_id: str, *, by: str, reason: str) -> dict:
    p = _path(state_dir, playbook_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    record = {"playbook_id": playbook_id, "by": by, "reason": reason,
              "at": datetime.now(timezone.utc).isoformat()}
    p.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def clear(state_dir: Path, playbook_id: str) -> bool:
    p = _path(state_dir, playbook_id)
    if p.exists():
        p.unlink()
        return True
    return False
