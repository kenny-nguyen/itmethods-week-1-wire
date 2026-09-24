"""Load a playbook by its id from the trusted playbooks directory, never from a path a caller supplies.

Security review finding S-1 (log D-020): the approval step used to load the
playbook named inside the approval request, so whoever could edit the request
chose the approver list. Now the id is format-checked, the file comes from
`playbooks/`, its hash must match the hash recorded when the request was
created, and it must validate.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from agent import AGENT_ID, __version__
from agent.governance.audit import AuditTrail, JsonlAuditSink
from agent.governance.error_log import ErrorLog
from agent.input import playbook as pbmod

ROOT = Path(__file__).resolve().parents[2]
PLAYBOOKS = ROOT / "playbooks"
PLAYBOOK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


class Untrusted(Exception):
    pass


def playbook_file(playbook_id: str, playbooks_dir: Path = PLAYBOOKS) -> Path:
    if not isinstance(playbook_id, str) or not PLAYBOOK_ID.match(playbook_id):
        raise Untrusted(f"invalid playbook id {playbook_id!r}")
    path = Path(playbooks_dir) / f"{playbook_id}.jsonc"
    if not path.is_file():
        raise Untrusted(f"no playbook {playbook_id!r} in {playbooks_dir}")
    return path


def motion_file(motion_id: str, playbooks_dir: Path = PLAYBOOKS) -> Path:
    if not isinstance(motion_id, str) or not PLAYBOOK_ID.match(motion_id):
        raise Untrusted(f"invalid motion id {motion_id!r}")
    path = Path(playbooks_dir) / "motions" / f"{motion_id}.jsonc"
    if not path.is_file():
        raise Untrusted(f"no motion {motion_id!r} in {Path(playbooks_dir) / 'motions'}")
    return path


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_trusted(playbook_id: str, playbooks_dir: Path = PLAYBOOKS, expected_sha: str | None = None) -> dict:
    path = playbook_file(playbook_id, playbooks_dir)
    if expected_sha is not None and sha256(path) != expected_sha:
        raise Untrusted(f"playbook {playbook_id} changed since the request was created")
    pb = pbmod.load(path)
    if pb.get("playbook_id") != playbook_id:
        raise Untrusted(f"{path.name} declares playbook_id {pb.get('playbook_id')!r}")
    problems = pbmod.validate(pb, **_validation_inputs())
    if problems:
        raise Untrusted("playbook invalid: " + "; ".join(problems))
    return pb


def _validation_inputs() -> dict:
    from agent.input.local import LocalRegulatoryFeed
    icp = json.loads((ROOT / "icp/icp.json").read_text(encoding="utf-8"))
    claims = json.loads((ROOT / "docs/research/product-claims.json").read_text(encoding="utf-8"))["claims"]
    return {"fs_segments": {k for k, v in icp["segments"].items() if v.get("fs")},
            "claim_ids": {c["id"] for c in claims},
            "implemented_triggers": LocalRegulatoryFeed(ROOT / "fixtures/regulatory_feed.json").implemented_ids()}


def is_accountable(pb: dict, name: str) -> bool:
    """The playbook owner or a listed approver."""
    return name == pb.get("owner") or name in pb["approval"]["approvers"]


def trail_for(pb: dict, out: Path, run_id: str, errors: ErrorLog, sink=None) -> AuditTrail:
    return AuditTrail(sink or JsonlAuditSink(Path(out) / "audit.jsonl"), AGENT_ID, __version__,
                      pb["approval"]["principal"], pb["playbook_id"], pb["version"], run_id, errors,
                      pb["audit"]["required_for"])
