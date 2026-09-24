"""Load and validate a Campaign Manager playbook (JSONC: JSON with // and /* */ comments).

Validation is the INPUT gate for the whole run: an invalid playbook stops the
run before any account is touched. The rules marked "stub" come from the
Campaign Manager stub in the assignment packet; the rest are proposed readings
named by register row (see playbooks/SCHEMA.md).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from agent.governance.audit import is_named_human

PRODUCTS = {"reign", "forge"}                                   # stub
TRIGGER_TYPES = {"regulatory", "event", "manual"}               # stub
CHANNELS = {"briefing", "sequence", "slack", "unknown"}         # stub
PLAY_STATUSES = {"implemented", "not_implemented"}  # trigger_status (A-041)
KILL_OPS = {">", ">=", "<", "<=", "=="}


class PlaybookError(Exception):
    pass


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments outside strings."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                raise PlaybookError("unterminated /* comment")
            i = end + 2
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def load(path: str | Path) -> dict:
    try:
        return json.loads(strip_jsonc(Path(path).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlaybookError(f"cannot read playbook {path}: {exc}") from exc


PLAYBOOK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def validate(pb: dict, *, fs_segments: set[str], claim_ids: set[str], implemented_triggers: set[str]) -> list[str]:
    """One playbook: the stub's shape (one audience, one trigger, one channel) plus marked additions (A-041)."""
    p: list[str] = []
    for key in ("playbook_id", "version", "product", "audience", "trigger", "channel", "approval",
                "kill_criteria", "audit", "trigger_status"):
        if key not in pb:
            p.append(f"missing '{key}'")
    if p:
        return p
    if "plays" in pb:
        p.append("one audience, trigger and channel per playbook; list playbooks in a motion file instead (A-041)")
    if not isinstance(pb["playbook_id"], str) or not PLAYBOOK_ID.match(pb["playbook_id"]):
        p.append("playbook_id must be lowercase letters, digits and hyphens")
    if pb["product"] not in PRODUCTS:
        p.append(f"product must be one of {sorted(PRODUCTS)}")
    if pb.get("status", "active") not in {"active", "paused", "retired"}:
        p.append("status must be active, paused or retired")
    if pb["trigger_status"] not in PLAY_STATUSES:
        p.append(f"trigger_status must be one of {sorted(PLAY_STATUSES)}")
    if pb["trigger_status"] == "not_implemented" and not pb.get("trigger_not_implemented_reason"):
        p.append("a trigger that is not implemented must say why")

    seg = (pb.get("audience") or {}).get("segment")
    if not seg:
        p.append("audience.segment is required")
    trig = pb.get("trigger") or {}
    if trig.get("type") not in TRIGGER_TYPES or not trig.get("id"):
        p.append(f"trigger needs type in {sorted(TRIGGER_TYPES)} and an id")
    if pb["channel"] not in CHANNELS:
        p.append(f"channel must be one of {sorted(CHANNELS)}")

    approval = pb["approval"]
    if not is_named_human(approval.get("principal")):
        p.append("approval.principal must be a named human (R-17 principal)")
    if pb["channel"] in set(approval.get("channels_that_send", CHANNELS)):  # stub rule
        approvers = approval.get("approvers") or []
        if not approvers or not all(is_named_human(a) for a in approvers):
            p.append(f"channel '{pb['channel']}' can send, so approval.approvers must list named humans")

    if pb["trigger_status"] == "implemented":
        if trig.get("id") not in implemented_triggers:
            p.append(f"trigger {trig.get('id')} is not an implemented trigger")
        unknown = set(pb.get("claims", [])) - claim_ids
        if unknown:
            p.append(f"unknown claim ids {sorted(unknown)}")
        if pb.get("unconfirmed_applicability", "hold") not in {"hold", "structured_brief"}:
            p.append("unconfirmed_applicability must be hold or structured_brief")

    kc = pb["kill_criteria"]
    if not isinstance(kc, list) or not kc:  # stub: how the CRO stops a sloppy motion
        p.append("kill_criteria must list at least one criterion")
    else:
        for c in kc:
            if not c.get("id") or not c.get("metric") or c.get("op") not in KILL_OPS or "threshold" not in c:
                p.append(f"kill criterion {c.get('id', '?')} needs id, metric, op in {sorted(KILL_OPS)}, threshold")

    audit = pb["audit"]
    if seg in fs_segments and audit.get("rule") != "R-17":  # stub: R-17 when the audience is FS
        p.append("an FS audience requires audit.rule = R-17")
    if audit.get("required_for") not in {"all_segments", "fs_only"}:
        p.append("audit.required_for must be all_segments or fs_only")
    if "limits" in pb:  # operator decision A-037: no volume cap
        p.append("volume limits are not allowed; stop a motion with quality-based kill criteria (A-037)")
    return p


def validate_motion(m: dict) -> list[str]:
    p = [f"motion missing '{k}'" for k in ("motion_id", "version", "owner", "principal", "playbooks") if k not in m]
    if p:
        return p
    if not PLAYBOOK_ID.match(str(m["motion_id"])):
        p.append("motion_id must be lowercase letters, digits and hyphens")
    if not is_named_human(m["principal"]) or not is_named_human(m["owner"]):
        p.append("motion owner and principal must be named humans")
    if not m["playbooks"] or not all(isinstance(x, str) and PLAYBOOK_ID.match(x) for x in m["playbooks"]):
        p.append("motion.playbooks must list playbook ids")
    return p
