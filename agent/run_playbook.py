"""Batch runner for the first Reign motion: INPUT -> PROCESSING -> OUTPUT -> FEEDBACK.

This is OFFLINE TEST MODE unless a model key is set: without one, briefs come from the deterministic
template, which exists for CI and tests and is not the agent. The agent is the Claude skill
(skills/regulatory-trigger-brief) driving the MCP server (agent/mcp_server.py). Both paths share
the same governed stages and gates.

    python3 -m agent.run_playbook                          # motion playbooks/motions/reign-first-motion.jsonc

A motion references playbooks, each exactly in the Campaign Manager stub's
shape: one audience, one trigger, one channel (A-041). The motion runs the ICP
filter once over the account list, then each playbook whose trigger is
implemented, with that playbook's own approval, kill criteria and audit.

Every stage has a gate:
- INPUT: the motion and every playbook must validate; a playbook that is not
  active, or whose kill switch is engaged, is skipped. Adapter failures go to
  the error log.
- PROCESSING: ICP filter (excluded and watch-list companies are never
  enriched or contacted), the applicability preflight, title routing (an
  audited decision), then the output gate on every draft.
- OUTPUT: the brief and its approval request are written together, only after
  their R-17 record. The request goes to the named iTmethods account owner,
  never to the prospect (A-043). Nothing is sent.
- FEEDBACK: each playbook's quality kill criteria are checked after the run.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agent import AGENT_ID, __version__
from agent import config
from agent.feedback import kill_criteria, kill_switch, reports, trusted
from agent.governance.audit import AuditBlocked, AuditTrail, JsonlAuditSink
from agent.governance.error_log import ErrorLog
from agent.input import playbook as pbmod
from agent.input.base import InputError
from agent.input.local import LocalClayEnrichment, LocalHubSpotAccounts, LocalRegulatoryFeed, LocalZoomInfoContacts
from agent.input.models import Enrichment
from agent.output.writer import RunPaths, approval_path, brief_path, write_json, write_text
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext, ProviderError, get_provider
from agent.processing.checks import check_brief
from agent.processing.icp import HOLD, INCLUDE, WATCH, Icp, IcpDecision
from agent.processing.routing import route

ROOT = Path(__file__).resolve().parent.parent


class RunRefused(Exception):
    """The run did not start: invalid motion or playbook, or unreadable inputs."""


def _load_inputs(root: Path) -> dict:
    fx = root / "fixtures"
    return {
        "accounts": LocalHubSpotAccounts(fx / "hubspot_companies.json"),
        "contacts": LocalZoomInfoContacts(fx / "zoominfo_contacts.json"),
        "enrichment": LocalClayEnrichment(fx / "clay_enrichment.json"),
        "feed": LocalRegulatoryFeed(fx / "regulatory_feed.json"),
        "icp": Icp.load(root / "icp" / "icp.json"),
        "claims": json.loads((root / "docs/research/product-claims.json").read_text(encoding="utf-8"))["claims"],
    }


def _trail(sink, gov: dict, run_id: str, errors: ErrorLog, *, pid: str, version: str) -> AuditTrail:
    return AuditTrail(sink, AGENT_ID, __version__, gov["principal"], pid, version, run_id, errors,
                      gov.get("required_for", "all_segments"))


def run(motion_path: str | Path, out_dir: str | Path, *, playbooks_dir: Path | None = None, root: Path = ROOT,
        provider=None, inputs: dict | None = None, sink=None) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    paths = RunPaths(Path(out_dir), run_id)
    errors = ErrorLog(paths.errors, run_id)
    playbooks_dir = Path(playbooks_dir) if playbooks_dir else Path(motion_path).resolve().parent.parent

    # ---- INPUT gate -------------------------------------------------------
    try:
        io = inputs or _load_inputs(root)
        icp: Icp = io["icp"]
        motion = pbmod.load(motion_path)
        problems = pbmod.validate_motion(motion)
        playbooks = []
        if not problems:
            kw = dict(fs_segments={k for k, v in icp.raw["segments"].items() if v.get("fs")},
                      claim_ids={c["id"] for c in io["claims"] if c.get("usable_in_briefs", True)}, implemented_triggers=io["feed"].implemented_ids())
            for pid in motion["playbooks"]:
                path = trusted.playbook_file(pid, playbooks_dir)
                pb = pbmod.load(path)
                problems += [f"{pid}: {p}" for p in pbmod.validate(pb, **kw)]
                if pb.get("playbook_id") != pid:
                    problems.append(f"{path.name} declares playbook_id {pb.get('playbook_id')!r}")
                playbooks.append((pb, trusted.sha256(path)))
    except (InputError, pbmod.PlaybookError, trusted.Untrusted, OSError, KeyError, json.JSONDecodeError) as exc:
        errors.record("input", exc, context={"motion": str(motion_path)})
        raise RunRefused(f"inputs could not be loaded: {exc}") from exc
    if problems:
        errors.record("input.playbook", "invalid: " + "; ".join(problems), context={"motion": str(motion_path)})
        raise RunRefused("motion or playbook invalid:\n  - " + "\n  - ".join(problems))

    sink = sink or JsonlAuditSink(paths.audit)
    motion_trail = _trail(sink, motion, run_id, errors, pid=motion["motion_id"], version=motion["version"])
    provider = provider or get_provider()
    summary = {"run_id": run_id, "motion": {"id": motion["motion_id"], "version": motion["version"]},
               "provider": provider.name, "accounts": {}, "playbooks": {}, "outputs": [], "watch_list": []}
    live = {pb["audience"]["segment"]: (pb, sha) for pb, sha in playbooks
            if pb["trigger_status"] == "implemented" and pb.get("status", "active") == "active"
            and not kill_switch.engaged(paths.state, pb["playbook_id"])}

    # ---- PROCESSING 1: ICP filter over the motion's account list --------------------------------
    try:
        accounts = io["accounts"].list_accounts()
    except InputError as exc:
        errors.record("input.accounts", exc)
        raise RunRefused(f"account source failed: {exc}") from exc
    included: list[tuple] = []
    motion_blocked = 0
    for acct in accounts:
        fs = icp.is_fs(acct)
        entry = summary["accounts"].setdefault(acct.id, {"name": acct.name, "segment": acct.segment, "fs": fs})
        try:
            decision = icp.prescreen(acct)
            enrichment = Enrichment.empty(acct.id)
            if decision is None and acct.segment not in live:
                # In profile on firmographics, but no live playbook for it: no enrichment, no brief.
                decision = IcpDecision("no_live_playbook", fs, [f"no active playbook with an implemented trigger for '{acct.segment}'"])
            if decision is None:  # only in-profile companies with a live playbook are enriched
                # R-17 order (adversarial QA F1): the audit record is written first, and only then is the
                # enrichment adapter called, inside the commit.
                enrichment = motion_trail.perform(
                    action="enrich", object_id=acct.system_id, fs=fs,
                    commit=lambda a=acct: io["enrichment"].enrich(a.id),
                    purpose=f"Attach enrichment to {acct.name} to test the first Reign motion ICP criteria.",
                    sources=[f"clay:company/{acct.id}"])
                decision = icp.evaluate(acct, enrichment)
            # Exclusion, hold and watch are our decisions about the account: audited as a score (A-024).
            motion_trail.perform(action="score", object_id=acct.system_id, fs=fs, commit=lambda: None,
                                 purpose=f"Record the ICP decision '{decision.decision}' for {acct.name} in the first Reign motion.",
                                 sources=[acct.system_id] + ([enrichment.source] if enrichment.source else []),
                                 detail={"decision": decision.decision, "reasons": decision.reasons, "flags": decision.flags})
        except AuditBlocked as exc:
            motion_blocked += 1
            entry.update(status="audit_blocked", reasons=[str(exc)])
            continue
        except InputError as exc:
            errors.record("input.enrichment", exc, context={"account": acct.id})
            entry.update(status="input_error", reasons=[str(exc)])
            continue
        entry.update(status=decision.decision, reasons=decision.reasons, flags=decision.flags)
        if decision.decision == INCLUDE:
            included.append((acct, enrichment, decision))
        elif decision.decision == WATCH:  # noticed and logged, never contacted (A-039, A-040)
            summary["watch_list"].append({"account": acct.id, "name": acct.name, "reasons": decision.reasons})

    # ---- PROCESSING 2 + OUTPUT: each playbook -----------------------------------------------------
    claims_by_id = {c["id"]: c for c in io["claims"]}
    for pb, sha in playbooks:
        pid = pb["playbook_id"]
        rec = summary["playbooks"][pid] = {"version": pb["version"], "trigger": pb["trigger"]["id"],
                                           "channel": pb["channel"], "trigger_status": pb["trigger_status"]}
        if pb["trigger_status"] != "implemented":
            rec["reason"] = pb.get("trigger_not_implemented_reason")
            continue
        killed = kill_switch.engaged(paths.state, pid)
        if killed or pb.get("status", "active") != "active":
            rec["skipped"] = f"kill switch engaged by {killed['by']}: {killed['reason']}" if killed else f"status {pb['status']}"
            errors.record("input.kill_switch", f"{pid} skipped: {rec['skipped']}", severity="warning")
            continue
        trail = _trail(sink, {**pb["approval"], **pb["audit"]}, run_id, errors, pid=pid, version=pb["version"])
        counts = {"audit_blocked": 0, "drafted": 0, "gate_failed": 0, "draft_failed": 0, "held": 0}
        trigger = io["feed"].get(pb["trigger"]["id"])
        for acct, enrichment, decision in [t for t in included if t[0].segment == pb["audience"]["segment"]]:
            _brief_one(acct, enrichment, decision, pb, sha, trigger, io, claims_by_id, provider, trail,
                       errors, paths, summary, counts)

        # ---- FEEDBACK: quality kill criteria (A-037) --------------------------------------------
        attempted = counts["drafted"] + counts["gate_failed"]
        metrics = {**counts, "audit_blocked": counts["audit_blocked"] + motion_blocked,
                   "gate_failed_ratio": kill_criteria.ratio(counts["gate_failed"], attempted),
                   **reports.metrics(paths.state, pid)}
        rec["metrics"] = metrics
        hits = kill_criteria.tripped(pb["kill_criteria"], metrics)
        if hits:
            reason = "kill criteria tripped: " + "; ".join(f"{h['id']} ({h['metric']}={h['value']})" for h in hits)
            rec["kill_switch"] = kill_switch.engage(paths.state, pid, by=pb["owner"], reason=reason)
            errors.record("feedback.kill_criteria", f"{pid}: {reason}", severity="warning")
            try:
                trail.perform(action="block", object_id=f"playbook:{pid}", fs=True, commit=lambda: None,
                              purpose=f"Pause the {pid} playbook because its quality kill criteria tripped.",
                              sources=[f"run:{run_id}"], detail={"tripped": hits})
            except AuditBlocked:
                pass  # the switch is engaged; the failure is in the error log

    write_json(paths.run_dir / "summary.json", summary)
    try:  # the review view is a convenience for humans; the JSON and Markdown files stay the source of truth
        from agent.output import review
        from evals.score_run import score as score_run
        summary["review"] = str(review.write(paths.run_dir, out_root=paths.out, score=score_run(paths.out, run_dir=paths.run_dir)))
    except Exception as exc:  # never hide it, never let it block the run's real outputs
        errors.record("output.review", exc)
    return summary


def _already_briefed(paths: RunPaths, account_id: str, trigger_id: str, playbook_id: str) -> str | None:
    """A scheduled rerun must not brief the same account on the same trigger twice (A-055)."""
    for p in sorted(paths.out.glob("runs/*/approvals/*.json")):
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if (r.get("account", {}).get("id") == account_id and r.get("trigger") == trigger_id
                and r.get("playbook", {}).get("id") == playbook_id and r.get("status") != "rejected"):
            return f"{r.get('status')} in run {r.get('run_id')}"
    return None


def _brief_one(acct, enrichment, decision, pb, sha, trigger, io, claims_by_id, provider, trail, errors, paths,
               summary, counts) -> None:
    entry = summary["accounts"][acct.id]
    prior = _already_briefed(paths, acct.system_id, trigger.id, pb["playbook_id"])
    if prior:  # plain read of our own records: no new touch, nothing to audit
        entry.update(playbook=pb["playbook_id"], status="already_briefed", reasons=[prior])
        return
    result = pf.check(trigger, acct, enrichment, pb)
    entry.update(playbook=pb["playbook_id"], preflight=result.status, applicability=result.applicability,
                 preflight_reasons=result.reasons)
    if result.status != pf.READY:
        try:
            trail.perform(action="hold", object_id=acct.system_id, fs=decision.fs, commit=lambda: None,
                          purpose=f"Record that no {trigger.id} brief is drafted for {acct.name}: preflight {result.status}.",
                          sources=[s.url for s in trigger.sources if s.url] + [acct.system_id],
                          detail={"preflight": result.status, "reasons": result.reasons})
        except AuditBlocked as exc:
            counts["audit_blocked"] += 1
            entry.update(status="audit_blocked", reasons=[str(exc)])
            return
        counts["held"] += result.status == pf.HOLD
        entry["status"] = f"preflight_{result.status}"
        return

    routing = pb.get("routing", {})
    lanes = routing.get("lanes", {})
    # R-17 order (adversarial re-test F7): the route record first, then the contacts adapter inside the commit.
    try:  # routing into lanes is our decision about people at the account (A-024)
        contacts = trail.perform(
            action="route", object_id=acct.system_id, fs=decision.fs,
            commit=lambda: io["contacts"].contacts_for(acct.id),
            purpose=f"Record which {acct.name} contacts the brief suggests to the account owner, by lane.",
            sources=[acct.system_id], detail={"lanes_rule": lanes, "do_not_route": routing.get("do_not_route", [])})
    except AuditBlocked as exc:
        counts["audit_blocked"] += 1
        entry.update(status="audit_blocked", reasons=[str(exc)])
        return
    except InputError as exc:
        errors.record("input.contacts", exc, context={"account": acct.id})
        entry["status"] = "input_error"
        return
    routed, skipped = route(contacts, lanes, routing.get("do_not_route", []), list(lanes))
    flags = list(decision.flags) + [f"A contact was not routed: {why}." for c, why in skipped]
    claims = [claims_by_id[cid] for cid in pb.get("claims", [])]
    ctx = BriefContext(trigger, result, acct, enrichment, routed, claims, acct.owner, flags,
                       not_routed=[c for c, _ in skipped])

    try:
        text = provider.draft(ctx)
    except ProviderError as exc:  # A-033 (proposed): the account fails; no silent fallback
        errors.record("processing.draft", exc, context={"account": acct.id, "provider": provider.name})
        counts["draft_failed"] += 1
        entry["status"] = "draft_failed"
        return
    problems = check_brief(text, **ctx.gate_kwargs())
    if problems:
        errors.record("processing.gate", "brief failed the output gate", context={"account": acct.id, "problems": problems})
        counts["gate_failed"] += 1
        entry.update(status="gate_failed", gate_problems=problems)
        return

    bpath, apath = brief_path(paths, acct.system_id), approval_path(paths, acct.system_id)
    request = {
        "request_id": uuid.uuid4().hex, "run_id": summary["run_id"], "status": "pending",
        "playbook": {"id": pb["playbook_id"], "version": pb["version"]}, "playbook_sha256": sha,
        "account": {"id": acct.system_id, "name": acct.name}, "trigger": trigger.id, "channel": pb["channel"],
        "route_to": {"account_owner": acct.owner},
        "brief": str(bpath), "send": False, "blockable": True, "sender": pb["approval"].get("sender", "none"),
        "suggested_recipients_in_existing_relationship": {l: [c.system_id for c in cs] for l, cs in routed.items()},
        "note": ("Nothing has been sent and the bank has not been contacted. The named account owner decides "
                 "whether to share this brief in the existing relationship (A-043), with "
                 "python3 -m agent.feedback.decide. Approvers come from the playbook and HubSpot, never from this file."),
    }

    def commit():
        # Brief and approval request land together or not at all (independent QA).
        write_text(bpath, text)
        try:
            write_json(apath, request)
        except Exception:
            bpath.unlink(missing_ok=True)
            raise

    try:
        trail.perform(action="create", object_id=acct.system_id, fs=decision.fs,
                      sources=sorted(ctx.allowed_urls() | {acct.system_id}),
                      purpose=(f"Draft the {trigger.title.split(':')[0]} brief for {acct.name} and route it to the "
                               f"account owner {acct.owner}, who decides before anything is shared."),
                      commit=commit, detail={"brief": str(bpath), "approval_request": str(apath),
                                             "request_id": request["request_id"], "provider": provider.name})
    except AuditBlocked as exc:
        counts["audit_blocked"] += 1
        entry.update(status="audit_blocked", reasons=[str(exc)])
        return
    except OSError as exc:
        counts["draft_failed"] += 1
        entry.update(status="write_failed", reasons=[str(exc)])
        return
    counts["drafted"] += 1
    entry.update(status="brief_pending_owner_decision", brief=str(bpath), approval_request=str(apath))
    summary["outputs"].append({"account": acct.id, "brief": str(bpath), "approval_request": str(apath)})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a motion of Campaign Manager playbooks (nothing is ever sent).")
    ap.add_argument("--motion", default="reign-first-motion", help="a motion in playbooks/motions/")
    args = ap.parse_args(argv)
    try:
        # Output root is fixed so the audit trail and kill switches cannot be redirected (security review).
        s = run(trusted.motion_file(args.motion), config.out_dir())
    except (RunRefused, trusted.Untrusted) as exc:
        print(f"RUN REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"run {s['run_id']}  motion {s['motion']['id']}@{s['motion']['version']}  provider {s['provider']}")
    if s["provider"] == "offline-test-mode":
        print("  OFFLINE TEST MODE: template drafts for CI, not the agent. The agent path is the skill + MCP server.")
    for aid, a in s["accounts"].items():
        why = "; ".join(a.get("preflight_reasons") or a.get("reasons") or [])
        print(f"  {aid}  {a.get('status', '?'):<30} {a['name']}  {why}")
    for pid, p in s["playbooks"].items():
        extra = p.get("reason") or p.get("skipped") or json.dumps(p.get("metrics", {}))
        print(f"  playbook {pid}: trigger {p['trigger']} {p['trigger_status']}  {extra}")
    for o in s["outputs"]:
        print(f"  brief {o['brief']}\n  approval request {o['approval_request']}")
    if s.get("review"):
        print(f"  review view {s['review']}")
    engaged = [pid for pid, p in s["playbooks"].items() if p.get("kill_switch")]
    if engaged:
        print(f"  KILL SWITCH ENGAGED: {', '.join(engaged)}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
