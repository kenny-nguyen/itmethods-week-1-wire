"""Engage or clear a playbook's kill switch by hand.

    python -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Drafts read generic."
    python -m agent.feedback.kill --playbook-id reign-first-motion --by "Kenny Nguyen" --reason "Reviewed." --clear
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from agent.feedback import kill_switch
from agent.governance.audit import is_named_human
from agent.governance.error_log import ErrorLog

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Engage or clear a playbook kill switch.")
    ap.add_argument("--playbook-id", required=True)
    ap.add_argument("--by", required=True, help="named human")
    ap.add_argument("--reason", required=True)
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "out"))
    args = ap.parse_args(argv)
    out = Path(args.out)
    if not is_named_human(args.by):
        ErrorLog(out / "errors.jsonl").record("feedback.kill", f"refused: {args.by!r} is not a named human")
        print(f"REFUSED: {args.by!r} is not a named human", file=sys.stderr)
        return 2
    if args.clear:
        cleared = kill_switch.clear(out / "state", args.playbook_id)
        print(f"kill switch {'cleared' if cleared else 'was not engaged'} for {args.playbook_id} by {args.by}: {args.reason}")
    else:
        kill_switch.engage(out / "state", args.playbook_id, by=args.by, reason=args.reason)
        print(f"kill switch engaged for {args.playbook_id} by {args.by}: {args.reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
