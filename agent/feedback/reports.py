"""Quality feedback on a sent-or-approved brief: complaints and wrong-account reports.

    python3 -m agent.feedback.report --request out/runs/<run>/approvals/<account>.json \
        --by "Kenny Nguyen" --kind wrong_account --detail "Brief names the wrong parent company."

Operator decision A-037: the kill criteria are quality-based, and these reports
feed them. A report is an R-17 "update" on the account (it records feedback
about a prospect touch), written before it is stored.
"""

from __future__ import annotations

import json
from pathlib import Path

KINDS = ("complaint", "wrong_account")


def _path(state_dir: Path, playbook_id: str) -> Path:
    from agent.feedback.kill_switch import _path as kill_path  # reuses the id check
    return kill_path(state_dir, playbook_id).parent.parent / "feedback" / f"{playbook_id}.jsonl"


def append(state_dir: Path, playbook_id: str, report: dict) -> None:
    p = _path(state_dir, playbook_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(report, sort_keys=True) + "\n")


def metrics(state_dir: Path, playbook_id: str) -> dict:
    p = _path(state_dir, playbook_id)
    rows = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    from agent.feedback.kill_switch import last_cleared
    since = last_cleared(state_dir, playbook_id)  # reports before the last clear were reviewed by a human
    rows = [r for r in rows if r.get("at", "") > since]
    return {"complaints": sum(r.get("kind") == "complaint" for r in rows),
            "wrong_account_reports": sum(r.get("kind") == "wrong_account" for r in rows)}
