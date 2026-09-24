"""Run a Campaign Manager playbook end to end: INPUT -> PROCESSING -> OUTPUT -> FEEDBACK.

    python -m agent.run_playbook --playbook playbooks/reign-first-motion.jsonc

Every stage has a gate:
- INPUT: the playbook must validate, the motion must be active, the kill switch
  must be off. Adapter failures stop the run and go to the error log.
- PROCESSING: ICP filter (excluded companies are never enriched), then the
  applicability preflight, then the output gate on every draft.
- OUTPUT: each brief and approval request is written only after its R-17 audit
  record (`AuditTrail.perform`). Nothing is sent; an approval request waits for
  a named human (`python -m agent.feedback.decide`).
- FEEDBACK: kill criteria are checked against the run's metrics; tripping one
  engages the kill switch.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from agent import AGENT_ID, __version__
from agent.feedback import kill_criteria, kill_switch
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
from agent.processing.icp import HOLD, INCLUDE, Icp, IcpDecision
from agent.processing.routing import route

ROOT = Path(__file__).resolve().parent.parent


class RunRefused(Exception):
    """The run did not start: invalid playbook, inactive motion, or kill switch engaged."""


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


def run(playbook_path: str | Path, out_dir: str | Path, *, root: Path = ROOT, provider=None,
        inputs: dict | None = None, sink=None) -> dict:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
    paths = RunPaths(Path(out_dir), run_id)
    errors = ErrorLog(paths.errors, run_id)

    # ---- INPUT gate -------------------------------------------------------
    try:
        io = inputs or _load_inputs(root)
        pb = pbmod.load(playbook_path)
        icp: Icp = io["icp"]
        problems = pbmod.validate(
            pb, fs_segments={k for k, v in icp.raw["segments"].items() if v.get("fs")},
            claim_ids={c["id"] for c in io["claims"]}, implemented_triggers=io["feed"].implemented_ids())
    except (InputError, pbmod.PlaybookError, OSError, KeyError, json.JSONDecodeError) as exc:
        errors.record("input", exc, context={"playbook": str(playbook_path)})
        raise RunRefused(f"inputs could not be loaded: {exc}") from exc
    if problems:
        errors.record("input.playbook", "playbook invalid: " + "; ".join(problems), context={"playbook": str(playbook_path)})
        raise RunRefused("playbook invalid:\n  - " + "\n  - ".join(problems))
    if pb.get("status", "active") != "active":
        raise RunRefused(f"playbook {pb['playbook_id']} is {pb['status']}, not active")
    killed = kill_switch.engaged(paths.state, pb["playbook_id"])
    if killed:
        errors.record("input.kill_switch", f"run refused: kill switch engaged by {killed['by']}: {killed['reason']}")
        raise RunRefused(f"kill switch engaged by {killed['by']} at {killed['at']}: {killed['reason']}")

    principal = pb["approval"]["principal"]
    approver = pb["approval"]["approvers"][0]
    trail = AuditTrail(sink or JsonlAuditSink(paths.audit), AGENT_ID, __version__, principal, pb["playbook_id"],
                       pb["version"], run_id, errors, pb["audit"]["required_for"])
    provider = provider or get_provider()
    summary = {"run_id": run_id, "playbook": {"id": pb["playbook_id"], "version": pb["version"]},
               "playbook_path": str(Path(playbook_path).resolve()),
               "provider": provider.name, "accounts": {}, "plays": [], "outputs": [], "kill_switch": None}
    counts = {"audit_blocked": 0, "drafted": 0, "gate_failed": 0, "draft_failed": 0, "held": 0}

    # ---- PROCESSING 1: ICP filter over the motion's account list ------------------------------
    try:
        accounts = io["accounts"].list_accounts()
    except InputError as exc:
        errors.record("input.accounts", exc)
        raise RunRefused(f"account source failed: {exc}") from exc
    live_segments = {p["audience"]["segment"] for p in pb["plays"] if p["status"] == "implemented"}
    included: list[tuple] = []
    for acct in accounts:
        fs = icp.is_fs(acct)
        entry = summary["accounts"].setdefault(acct.id, {"name": acct.name, "segment": acct.segment, "fs": fs})
        try:
            decision = icp.prescreen(acct)
            enrichment = Enrichment.empty(acct.id)
            if decision is None and acct.segment not in live_segments:
                # In profile on firmographics, but its play is not implemented: no enrichment, no brief.
                decision = IcpDecision("no_implemented_play", fs, [f"no implemented play for segment '{acct.segment}'"])
            if decision is None:  # only in-profile companies with a live play are enriched
                fetched = io["enrichment"].enrich(acct.id)
                enrichment = trail.perform(
                    action="enrich", object_id=acct.system_id, fs=fs, commit=lambda f=fetched: f,
                    purpose=f"Attach enrichment to {acct.name} to test the first Reign motion ICP criteria.",
                    sources=[fetched.source or f"clay:row/{acct.id}"])
                decision = icp.evaluate(acct, enrichment)
            trail.perform(action="score", object_id=acct.system_id, fs=fs, commit=lambda: None,
                          purpose=f"Record the ICP decision '{decision.decision}' for {acct.name} in the first Reign motion.",
                          sources=[acct.system_id] + ([enrichment.source] if enrichment.source else []),
                          detail={"decision": decision.decision, "reasons": decision.reasons, "flags": decision.flags})
        except AuditBlocked as exc:
            counts["audit_blocked"] += 1
            entry.update(status="audit_blocked", reasons=[str(exc)])
            continue
        except InputError as exc:
            errors.record("input.enrichment", exc, context={"account": acct.id})
            entry.update(status="input_error", reasons=[str(exc)])
            continue
        entry.update(status=decision.decision, reasons=decision.reasons, flags=decision.flags)
        if decision.decision == INCLUDE:
            included.append((acct, enrichment, decision))
        elif decision.decision == HOLD:
            counts["held"] += 1

    # ---- PROCESSING 2 + OUTPUT: each play ------------------------------------------------------
    cap = (pb.get("limits") or {}).get("max_accounts_per_run")
    claims_by_id = {c["id"]: c for c in io["claims"]}
    for play in pb["plays"]:
        record = {"play_id": play["play_id"], "status": play["status"], "trigger": play["trigger"]["id"]}
        summary["plays"].append(record)
        if play["status"] != "implemented":
            record["reason"] = play.get("not_implemented_reason")
            continue
        trigger = io["feed"].get(play["trigger"]["id"])
        targets = [t for t in included if t[0].segment == play["audience"]["segment"]]
        if cap is not None and len(targets) > cap:
            for acct, _, _ in targets[cap:]:
                summary["accounts"][acct.id].update(status="deferred", reasons=[f"volume cap of {cap} per run (A-010)"])
            targets = targets[:cap]
        record["targets"] = [a.id for a, _, _ in targets]
        for acct, enrichment, decision in targets:
            _brief_one(acct, enrichment, decision, play, trigger, pb, io, claims_by_id, provider, trail,
                       errors, paths, approver, summary, counts)

    # ---- FEEDBACK: kill criteria ---------------------------------------------------------------
    attempted = counts["drafted"] + counts["gate_failed"]
    metrics = {"audit_blocked": counts["audit_blocked"], "drafted": counts["drafted"],
               "gate_failed_ratio": counts["gate_failed"] / attempted if attempted else 0.0,
               "held_ratio": counts["held"] / len(accounts) if accounts else 0.0, "rejected_ratio": 0.0}
    summary["metrics"] = {**counts, **metrics}
    hits = kill_criteria.tripped(pb["kill_criteria"], metrics)
    if hits:
        reason = "; ".join(f"{h['id']} ({h['metric']}={h['value']} {h['op']} {h['threshold']})" for h in hits)
        summary["kill_switch"] = kill_switch.engage(paths.state, pb["playbook_id"], by=pb["owner"],
                                                    reason=f"kill criteria tripped: {reason}")
        errors.record("feedback.kill_criteria", f"kill switch engaged: {reason}", severity="warning")
        try:
            trail.perform(action="block", object_id=f"playbook:{pb['playbook_id']}", fs=True, commit=lambda: None,
                          purpose=f"Pause the {pb['playbook_id']} motion because its kill criteria tripped.",
                          sources=[f"run:{run_id}"], detail={"tripped": hits})
        except AuditBlocked:
            pass  # the switch is already engaged; the failure is in the error log

    write_json(paths.run_dir / "summary.json", summary)
    return summary


def _brief_one(acct, enrichment, decision, play, trigger, pb, io, claims_by_id, provider, trail, errors, paths,
               approver, summary, counts) -> None:
    entry = summary["accounts"][acct.id]
    result = pf.check(trigger, acct, enrichment, play)
    entry.update(preflight=result.status, applicability=result.applicability, preflight_reasons=result.reasons)
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

    try:
        contacts = io["contacts"].contacts_for(acct.id)
    except InputError as exc:
        errors.record("input.contacts", exc, context={"account": acct.id})
        entry["status"] = "input_error"
        return
    routing = play.get("routing", {})
    lanes = routing.get("lanes", {})
    routed, skipped = route(contacts, lanes, routing.get("do_not_route", []), list(lanes))
    flags = list(decision.flags) + [f"{c.name} ({c.title}) not routed: {why}" for c, why in skipped]
    claims = [claims_by_id[cid] for cid in play.get("claims", [])]
    ctx = BriefContext(trigger, result, acct, enrichment, routed, claims, approver, flags)

    try:
        text = provider.draft(ctx)
    except ProviderError as exc:  # A-033 (proposed): fail the account, do not fall back silently
        errors.record("processing.draft", exc, context={"account": acct.id, "provider": provider.name})
        counts["draft_failed"] += 1
        entry["status"] = "draft_failed"
        return
    problems = check_brief(text, allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(),
                           claim_texts=ctx.claim_texts(), caveat_required=pf.CAVEAT in result.caveats)
    if problems:
        errors.record("processing.gate", "brief failed the output gate", context={"account": acct.id, "problems": problems})
        counts["gate_failed"] += 1
        entry.update(status="gate_failed", gate_problems=problems)
        return

    sources = sorted(ctx.allowed_urls() | {acct.system_id})
    bpath, apath = brief_path(paths, acct.system_id), approval_path(paths, acct.system_id)
    try:
        trail.perform(action="create", object_id=acct.system_id, fs=decision.fs, sources=sources,
                      purpose=f"Draft the {trigger.title.split(':')[0]} account brief for {acct.name} for {approver} to review before any send.",
                      commit=lambda: write_text(bpath, text), detail={"brief": str(bpath), "provider": provider.name})
        request = {
            "request_id": uuid.uuid4().hex, "run_id": summary["run_id"], "status": "pending",
            "playbook": summary["playbook"], "playbook_path": summary["playbook_path"], "play_id": play["play_id"],
            "account": {"id": acct.system_id, "name": acct.name, "fs": decision.fs},
            "trigger": trigger.id, "channel": play["channel"], "brief": str(bpath),
            "approvers": pb["approval"]["approvers"], "send": False, "blockable": True,
            "sender": pb["approval"].get("sender", "none"),
            "recipients": {lane: [c.system_id for c in cs] for lane, cs in routed.items()},
            "note": "Nothing has been sent. A named approver decides with python -m agent.feedback.decide.",
        }
        trail.perform(action="create", object_id=acct.system_id, fs=decision.fs, sources=[str(bpath)],
                      purpose=f"Open an approval request so {approver} decides whether the {acct.name} brief may be sent.",
                      commit=lambda: write_json(apath, request), detail={"request_id": request["request_id"]})
    except AuditBlocked as exc:
        counts["audit_blocked"] += 1
        entry.update(status="audit_blocked", reasons=[str(exc)])
        return
    counts["drafted"] += 1
    entry.update(status="brief_pending_approval", brief=str(bpath), approval_request=str(apath))
    summary["outputs"].append({"account": acct.id, "brief": str(bpath), "approval_request": str(apath)})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a Campaign Manager playbook (nothing is ever sent).")
    ap.add_argument("--playbook", default=str(ROOT / "playbooks/reign-first-motion.jsonc"))
    ap.add_argument("--out", default=str(ROOT / "out"))
    args = ap.parse_args(argv)
    try:
        s = run(args.playbook, args.out)
    except RunRefused as exc:
        print(f"RUN REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"run {s['run_id']}  playbook {s['playbook']['id']}@{s['playbook']['version']}  provider {s['provider']}")
    for aid, a in s["accounts"].items():
        why = "; ".join(a.get("preflight_reasons") or a.get("reasons") or [])
        print(f"  {aid}  {a.get('status', '?'):<24} {a['name']}  {why}")
    for p in s["plays"]:
        print(f"  play {p['play_id']}: {p['status']}" + (f" ({p['reason']})" if p.get("reason") else ""))
    for o in s["outputs"]:
        print(f"  brief {o['brief']}\n  approval request {o['approval_request']}")
    print(f"  metrics {json.dumps(s['metrics'])}")
    if s["kill_switch"]:
        print(f"  KILL SWITCH ENGAGED: {s['kill_switch']['reason']}")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
