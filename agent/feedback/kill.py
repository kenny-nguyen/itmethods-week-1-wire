"""Engage or clear a playbook's kill switch by hand.

    python3 -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Drafts read generic."
    python3 -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Reviewed the drafts." --clear

Only the playbook owner or a listed approver may use it (independent
security review). Both directions are audited. Engaging writes the switch first and
the audit record second, because stopping must not depend on the audit store;
clearing is refused unless its audit record is written, because restarting is
the unsafe direction.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent import config
from agent.feedback import kill_switch, trusted
from agent.governance.audit import AuditBlocked
from agent.governance.error_log import ErrorLog

ROOT = Path(__file__).resolve().parents[2]


class KillRefused(Exception):
    pass


def kill(playbook_id: str, *, by: str, reason: str, clear: bool, out_dir: str | Path, sink=None,
         playbooks_dir: Path = trusted.PLAYBOOKS) -> str:
    out = Path(out_dir)
    errors = ErrorLog(out / "errors.jsonl")
    try:
        pb = trusted.load_trusted(playbook_id, playbooks_dir)
    except trusted.Untrusted as exc:
        errors.record("feedback.kill", exc)
        raise KillRefused(str(exc)) from exc
    if not trusted.is_accountable(pb, by) or len(reason.split()) < 3:
        errors.record("feedback.kill", f"refused: {by!r} is not the owner or an approver, or reason too short")
        raise KillRefused(f"{by!r} must be the playbook owner or an approver, with a reason of three words or more")
    trail = trusted.trail_for(pb, out, "manual", errors, sink)
    state = out / "state"
    common = dict(object_id=f"playbook:{playbook_id}", fs=True, sources=[f"operator:{by}"], detail={"reason": reason})
    if clear:
        try:
            trail.perform(action="unblock", purpose=f"Clear the {playbook_id} kill switch after review by {by}.",
                          commit=lambda: kill_switch.clear(state, playbook_id), **common)
        except AuditBlocked as exc:
            raise KillRefused(f"not cleared: {exc}") from exc
        return f"kill switch cleared for {playbook_id} by {by}: {reason}"
    kill_switch.engage(state, playbook_id, by=by, reason=reason)
    try:
        trail.perform(action="block", purpose=f"Stop the {playbook_id} motion by hand at the request of {by}.",
                      commit=lambda: None, **common)
    except AuditBlocked:
        pass  # engaged anyway; the audit failure is in the error log
    return f"kill switch engaged for {playbook_id} by {by}: {reason}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Engage or clear a playbook kill switch.")
    ap.add_argument("--playbook-id", required=True)
    ap.add_argument("--by", required=True, help="the playbook owner or a listed approver")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--clear", action="store_true")
    args = ap.parse_args(argv)
    try:
        print(kill(args.playbook_id, by=args.by, reason=args.reason, clear=args.clear, out_dir=config.out_dir()))
    except KillRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
