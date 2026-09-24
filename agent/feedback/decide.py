"""A named human approves or rejects a pending brief.

    python3 -m agent.feedback.decide --request out/runs/<run>/approvals/<account>.json \
        --approver "Kenny Nguyen" --approve --reason "Checked sources and routing."

Refused unless: the request sits under the fixed output root; the playbook,
loaded by id from playbooks/ (never from a path in the request), is unchanged
since the request was created and still validates; the approver is listed in
that playbook; the request is still pending; and the kill switch is off. The
decision is an R-17 record (approve carries send=true, the approver and
blockable=true) written before the request file changes. Approval makes the
brief ready to send; no sender is wired (A-035), so nothing leaves the machine.

Limit (demo): the approver is a typed name. In production it must come from an
authenticated identity, not a command-line string.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import config
from agent.feedback import kill_criteria, kill_switch, reports, trusted
from agent.governance.audit import AuditBlocked, is_named_human
from agent.governance.error_log import ErrorLog
from agent.output.writer import write_json

ROOT = Path(__file__).resolve().parents[2]


class DecisionRefused(Exception):
    pass


def created_record(out: Path, request_id: str | None) -> dict | None:
    """The audited create record that produced this approval request, or None."""
    audit = Path(out) / "audit.jsonl"
    if not request_id or not audit.exists():
        return None
    found = None
    for line in audit.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("action") == "create" and r.get("detail", {}).get("request_id") == request_id:
            found = None if r.get("detail", {}).get("outcome") == "failed" else r
    return found


def account_owner(system_id: str) -> str | None:
    """The account owner from the system of record, never from the request file (A-043, D-018)."""
    from agent.input.local import LocalHubSpotAccounts
    for a in LocalHubSpotAccounts(ROOT / "fixtures/hubspot_companies.json").list_accounts():
        if a.system_id == system_id:
            return a.owner
    return None


def decide(request_path: str | Path, *, approver: str, approve: bool, reason: str, out_dir: str | Path,
           sink=None, playbooks_dir: Path = trusted.PLAYBOOKS) -> dict:
    out = Path(out_dir).resolve()
    request_path = Path(request_path).resolve()
    errors = ErrorLog(out / "errors.jsonl")

    def refuse(msg: str):
        errors.record("feedback.decide", msg, context={"request": str(request_path), "approver": approver})
        raise DecisionRefused(msg)

    if (out / "runs") not in request_path.parents:  # D-020, S-2: no decisions against another output root
        refuse(f"request is not under {out / 'runs'}")
    req = json.loads(request_path.read_text(encoding="utf-8"))
    # Bind the request to the audit trail (QA pass 2, C2): the account and playbook come from the audited
    # create record for this request id, never from the editable request file alone.
    created = created_record(out, req.get("request_id"))
    if created is None:
        refuse("no audited create record for this request id; the request cannot be trusted")
    if (req.get("account", {}).get("id") != created["object"]
            or req.get("playbook", {}).get("id") != created["playbook"]["id"]):
        refuse("the request file does not match its audited create record (account or playbook changed)")
    if not req.get("playbook_sha256"):
        refuse("the request has no playbook hash")
    try:
        pb = trusted.load_trusted(created["playbook"]["id"], playbooks_dir, expected_sha=req["playbook_sha256"])
    except (trusted.Untrusted, KeyError) as exc:
        refuse(f"playbook not trusted: {exc}")
    if req["status"] != "pending":
        refuse(f"request is already {req['status']}")
    if not is_named_human(approver) or approver not in pb["approval"]["approvers"]:
        refuse(f"{approver!r} is not a named approver for {pb['playbook_id']}")
    owner = account_owner(created["object"])
    if pb.get("handoff", {}).get("route_to") == "account_owner" and approver != owner:
        refuse(f"{approver!r} is not the named account owner ({owner!r}) on record in HubSpot (A-043)")
    killed = kill_switch.engaged(out / "state", pb["playbook_id"])
    if approve and killed:
        refuse(f"kill switch engaged by {killed['by']}: {killed['reason']}")
    if not reason or len(reason.split()) < 3:
        refuse("a decision needs a reason of at least three words")

    trail = trusted.trail_for(pb, out, req["run_id"], errors, sink)
    name = req["account"]["name"]
    updated = {**req, "status": "approved_ready_to_send" if approve else "rejected", "decided_by": approver,
               "decided_at": datetime.now(timezone.utc).isoformat(), "reason": reason, "send": approve}
    try:
        trail.perform(
            action="approve" if approve else "reject", object_id=req["account"]["id"],
            fs=True,  # never taken from the request file; required audit either way (D-020)
            purpose=(f"Approve the {req['trigger']} brief for {name} to be sent by its owner; no sender is wired."
                     if approve else f"Reject the {req['trigger']} brief for {name} so it is never sent."),
            sources=[req["brief"], f"approval:{req['request_id']}"], send=approve,
            approver=approver if approve else None, commit=lambda: write_json(request_path, updated),
            detail={"reason": reason})
    except AuditBlocked as exc:
        raise DecisionRefused(str(exc)) from exc
    except OSError as exc:
        raise DecisionRefused(f"decision recorded as failed; request unchanged: {exc}") from exc

    check_kill_criteria(pb, out, request_path.parent, trail, by=approver)
    return updated


def check_kill_criteria(pb: dict, out: Path, approvals_dir: Path | None, trail, *, by: str) -> list[dict]:
    """FEEDBACK: rejections over decided requests, plus complaints and wrong-account reports (A-037)."""
    decided = []
    for p in (approvals_dir.glob("*.json") if approvals_dir else []):
        try:
            status = json.loads(p.read_text(encoding="utf-8")).get("status")
        except (OSError, json.JSONDecodeError):
            continue
        if status in ("approved_ready_to_send", "rejected"):
            decided.append(status)
    metrics = {"rejected_ratio": kill_criteria.ratio(decided.count("rejected"), len(decided)),
               **reports.metrics(out / "state", pb["playbook_id"])}
    hits = kill_criteria.tripped(pb["kill_criteria"], metrics)
    if hits and not kill_switch.engaged(out / "state", pb["playbook_id"]):
        reason = "kill criteria tripped: " + ", ".join(f"{h['id']} ({h['metric']}={h['value']})" for h in hits)
        kill_switch.engage(out / "state", pb["playbook_id"], by=by, reason=reason)  # engage first: the safe direction
        try:
            trail.perform(action="block", object_id=f"playbook:{pb['playbook_id']}", fs=True, commit=lambda: None,
                          purpose=f"Pause the {pb['playbook_id']} motion because its quality kill criteria tripped.",
                          sources=[f"metrics:{json.dumps(metrics, sort_keys=True)}"], detail={"tripped": hits})
        except AuditBlocked:
            pass  # the switch is engaged; the failure is in the error log
    return hits


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Approve or reject a pending brief. Nothing is sent.")
    ap.add_argument("--request", required=True)
    ap.add_argument("--approver", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true")
    g.add_argument("--reject", action="store_true")
    ap.add_argument("--reason", required=True)
    args = ap.parse_args(argv)
    try:
        r = decide(args.request, approver=args.approver, approve=args.approve, reason=args.reason, out_dir=config.out_dir())
    except DecisionRefused as exc:
        print(f"DECISION REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"{r['account']['name']}: {r['status']} by {r['decided_by']}. Nothing has been sent (sender: {r['sender']}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
