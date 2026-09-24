"""CLI for quality feedback reports; see agent/feedback/reports.py."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from agent import config
from agent.feedback import reports, trusted
from agent.feedback.decide import check_kill_criteria
from agent.governance.audit import AuditBlocked
from agent.governance.error_log import ErrorLog

ROOT = Path(__file__).resolve().parents[2]


class ReportRefused(Exception):
    pass


def report(request_path: str | Path, *, by: str, kind: str, detail: str, out_dir: str | Path, sink=None,
           playbooks_dir: Path = trusted.PLAYBOOKS) -> list[dict]:
    out = Path(out_dir).resolve()
    request_path = Path(request_path).resolve()
    errors = ErrorLog(out / "errors.jsonl")
    if (out / "runs") not in request_path.parents or kind not in reports.KINDS:
        errors.record("feedback.report", "refused: request outside output root or unknown kind")
        raise ReportRefused(f"request must be under {out / 'runs'} and kind one of {reports.KINDS}")
    req = json.loads(request_path.read_text(encoding="utf-8"))
    try:
        pb = trusted.load_trusted(req["playbook"]["id"], playbooks_dir)
    except (trusted.Untrusted, KeyError) as exc:
        raise ReportRefused(f"playbook not trusted: {exc}") from exc
    if not trusted.is_accountable(pb, by) or len(detail.split()) < 3:
        errors.record("feedback.report", f"refused: {by!r} is not the owner or an approver, or detail too short")
        raise ReportRefused(f"{by!r} must be the playbook owner or an approver, with a detail of three words or more")
    trail = trusted.trail_for(pb, out, req["run_id"], errors, sink)
    row = {"kind": kind, "by": by, "detail": detail, "request_id": req["request_id"],
           "account": req["account"]["id"], "at": datetime.now(timezone.utc).isoformat()}
    try:
        trail.perform(action="update", object_id=req["account"]["id"], fs=True,
                      purpose=f"Record a {kind.replace('_', ' ')} report on the {req['trigger']} brief for {req['account']['name']}.",
                      sources=[req["brief"], f"approval:{req['request_id']}"],
                      commit=lambda: reports.append(out / "state", pb["playbook_id"], row), detail=row)
    except AuditBlocked as exc:
        raise ReportRefused(str(exc)) from exc
    return check_kill_criteria(pb, out, request_path.parent, trail, by=by)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report a complaint or a wrong-account brief (feeds the kill criteria).")
    ap.add_argument("--request", required=True)
    ap.add_argument("--by", required=True)
    ap.add_argument("--kind", required=True, choices=reports.KINDS)
    ap.add_argument("--detail", required=True)
    args = ap.parse_args(argv)
    try:
        hits = report(args.request, by=args.by, kind=args.kind, detail=args.detail, out_dir=config.out_dir())
    except ReportRefused as exc:
        print(f"REPORT REFUSED: {exc}", file=sys.stderr)
        return 2
    print("report recorded" + (f"; KILL SWITCH ENGAGED: {', '.join(h['id'] for h in hits)}" if hits else ""))
    return 3 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
