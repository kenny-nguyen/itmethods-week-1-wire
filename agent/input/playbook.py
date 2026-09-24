"""Load and validate a Campaign Manager playbook (JSONC: JSON with // and /* */ comments).

Validation is the INPUT gate for the whole run: an invalid playbook stops the
run before any account is touched. The rules marked "stub" come from the
Campaign Manager stub in the assignment packet; the rest are proposed readings
named by register row (see playbooks/SCHEMA.md).
"""

from __future__ import annotations

import json
from pathlib import Path

from agent.governance.audit import is_named_human

PRODUCTS = {"reign", "forge"}                                   # stub
TRIGGER_TYPES = {"regulatory", "event", "manual"}               # stub
CHANNELS = {"briefing", "sequence", "slack", "unknown"}         # stub
PLAY_STATUSES = {"implemented", "not_implemented"}
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


def validate(pb: dict, *, fs_segments: set[str], claim_ids: set[str], implemented_triggers: set[str]) -> list[str]:
    p: list[str] = []
    for key in ("playbook_id", "version", "product", "plays", "approval", "kill_criteria", "audit"):
        if key not in pb:
            p.append(f"missing '{key}'")
    if p:
        return p
    if pb["product"] not in PRODUCTS:
        p.append(f"product must be one of {sorted(PRODUCTS)}")
    if pb.get("status", "active") not in {"active", "paused", "retired"}:
        p.append("status must be active, paused or retired")

    approval = pb["approval"]
    sending = set(approval.get("channels_that_send", CHANNELS))
    if not is_named_human(approval.get("principal")):
        p.append("approval.principal must be a named human (R-17 principal)")

    if not isinstance(pb["plays"], list) or not pb["plays"]:
        p.append("plays must be a non-empty list")
        return p
    any_fs = False
    for play in pb["plays"]:
        where = f"play {play.get('play_id', '?')}"
        if play.get("status") not in PLAY_STATUSES:
            p.append(f"{where}: status must be one of {sorted(PLAY_STATUSES)}")
        if play.get("status") == "not_implemented" and not play.get("not_implemented_reason"):
            p.append(f"{where}: a not-implemented play must say why")
        seg = (play.get("audience") or {}).get("segment")
        if not seg:
            p.append(f"{where}: audience.segment is required")
        any_fs = any_fs or seg in fs_segments
        trig = play.get("trigger") or {}
        if trig.get("type") not in TRIGGER_TYPES or not trig.get("id"):
            p.append(f"{where}: trigger needs type in {sorted(TRIGGER_TYPES)} and an id")
        if play.get("channel") not in CHANNELS:
            p.append(f"{where}: channel must be one of {sorted(CHANNELS)}")
        if play.get("channel") in sending:  # stub: approval must name a human if channel can send
            approvers = approval.get("approvers") or []
            if not approvers or not all(is_named_human(a) for a in approvers):
                p.append(f"{where}: channel '{play.get('channel')}' can send, so approval.approvers must list named humans")
        if play.get("status") == "implemented":
            if trig.get("id") not in implemented_triggers:
                p.append(f"{where}: trigger {trig.get('id')} is not an implemented trigger")
            unknown = set(play.get("claims", [])) - claim_ids
            if unknown:
                p.append(f"{where}: unknown claim ids {sorted(unknown)}")
            if play.get("unconfirmed_applicability", "hold") not in {"hold", "brief_with_caveat"}:
                p.append(f"{where}: unconfirmed_applicability must be hold or brief_with_caveat")

    kc = pb["kill_criteria"]
    if not isinstance(kc, list) or not kc:  # stub: how the CRO stops a sloppy motion
        p.append("kill_criteria must list at least one criterion")
    else:
        for c in kc:
            if not c.get("id") or not c.get("metric") or c.get("op") not in KILL_OPS or "threshold" not in c:
                p.append(f"kill criterion {c.get('id', '?')} needs id, metric, op in {sorted(KILL_OPS)}, threshold")

    audit = pb["audit"]
    if any_fs and audit.get("rule") != "R-17":  # stub: audit satisfies R-17 when the audience is FS
        p.append("an FS audience requires audit.rule = R-17")
    if audit.get("required_for") not in {"all_segments", "fs_only"}:
        p.append("audit.required_for must be all_segments or fs_only")
    cap = (pb.get("limits") or {}).get("max_accounts_per_run")
    if cap is not None and (not isinstance(cap, int) or cap < 1):
        p.append("limits.max_accounts_per_run must be a positive integer")
    return p
