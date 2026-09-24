"""A named human approves or rejects a pending brief.

    python -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
        --approver "Kenny Nguyen" --approve --reason "Checked sources and routing."

Refused unless: the approver is a named human listed in the playbook's
`approval.approvers`, the request is still pending, and the kill switch is off.
The decision is an R-17 record (approve carries send=true, the approver and
blockable=true) written before the request file changes. Approval makes the
brief ready to send; no sender is wired (proposed reading A-035), so nothing
leaves the building.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import AGENT_ID, __version__
from agent.feedback import kill_criteria, kill_switch
from agent.governance.audit import AuditBlocked, AuditTrail, JsonlAuditSink, is_named_human
from agent.governance.error_log import ErrorLog
from agent.input import playbook as pbmod
from agent.output.writer import write_json


class DecisionRefused(Exception):
    pass


def decide(request_path: str | Path, *, approver: str, approve: bool, reason: str, out_dir: str | Path,
           sink=None) -> dict:
    request_path = Path(request_path)
    out = Path(out_dir)
    req = json.loads(request_path.read_text(encoding="utf-8"))
    errors = ErrorLog(out / "errors.jsonl", req["run_id"])
    pb = pbmod.load(req["playbook_path"])

    def refuse(msg: str):
        errors.record("feedback.decide", msg, context={"request": str(request_path), "approver": approver})
        raise DecisionRefused(msg)

    if req["status"] != "pending":
        refuse(f"request is already {req['status']}")
    if not is_named_human(approver) or approver not in pb["approval"]["approvers"]:
        refuse(f"{approver!r} is not a named approver for {pb['playbook_id']}")
    killed = kill_switch.engaged(out / "state", pb["playbook_id"])
    if approve and killed:
        refuse(f"kill switch engaged by {killed['by']}: {killed['reason']}")
    if not reason or len(reason.split()) < 3:
        refuse("a decision needs a reason of at least three words")

    trail = AuditTrail(sink or JsonlAuditSink(out / "audit.jsonl"), AGENT_ID, __version__,
                       pb["approval"]["principal"], pb["playbook_id"], pb["version"], req["run_id"], errors,
                       pb["audit"]["required_for"])
    name = req["account"]["name"]
    updated = {**req, "status": "approved_ready_to_send" if approve else "rejected", "decided_by": approver,
               "decided_at": datetime.now(timezone.utc).isoformat(), "reason": reason, "send": approve}
    try:
        trail.perform(
            action="approve" if approve else "reject", object_id=req["account"]["id"], fs=req["account"]["fs"],
            purpose=(f"Approve the {req['trigger']} brief for {name} to be sent by its owner; no sender is wired."
                     if approve else f"Reject the {req['trigger']} brief for {name} so it is never sent."),
            sources=[req["brief"], f"approval:{req['request_id']}"], send=approve,
            approver=approver if approve else None, commit=lambda: write_json(request_path, updated),
            detail={"reason": reason})
    except AuditBlocked as exc:
        raise DecisionRefused(str(exc)) from exc

    # FEEDBACK: the rejection ratio across this run feeds the kill criteria.
    decided = [json.loads(p.read_text()) for p in request_path.parent.glob("*.json")]
    rejected = sum(r["status"] == "rejected" for r in decided)
    metrics = {"rejected_ratio": rejected / len(decided)}
    hits = kill_criteria.tripped(pb["kill_criteria"], metrics)
    if hits:
        kill_switch.engage(out / "state", pb["playbook_id"], by=approver,
                           reason="kill criteria tripped: " + ", ".join(h["id"] for h in hits))
    return updated


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Approve or reject a pending brief. Nothing is sent.")
    ap.add_argument("--request", required=True)
    ap.add_argument("--approver", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true")
    g.add_argument("--reject", action="store_true")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--out", default=None, help="run output root (default: two levels above the request's run)")
    args = ap.parse_args(argv)
    out = args.out or str(Path(args.request).resolve().parents[3])
    try:
        r = decide(args.request, approver=args.approver, approve=args.approve, reason=args.reason, out_dir=out)
    except DecisionRefused as exc:
        print(f"DECISION REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"{r['account']['name']}: {r['status']} by {r['decided_by']}. Nothing has been sent (sender: {r['sender']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
