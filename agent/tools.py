"""The governed tools an agent uses to turn a regulatory trigger into an account brief.

The AI decides; the code enforces (operator decision A-046). Each method is one
MCP tool (`agent/mcp_server.py` registers them). The rules live here, inside
the tools, so an agent cannot skip them:

- R-17: every enrich, score, route, hold and create writes its audit record
  first; if the record cannot be written the action does not happen.
- Exclusions and the watch list: an account the ICP drops, holds or watches
  cannot be checked, routed, drafted for or sent to approval.
- The do-not-route list: routing never returns a listed title.
- Claim limits and the brief structure: `request_approval` re-runs the output
  gate itself and refuses a failing brief, whatever the agent was told.
- Approval: the request always goes to the account's named owner; nothing sends.

Every failure raises `ToolFailure`, whose message names the recovery
(operator decision A-033: fail loudly, never silently).

State is kept per server process: the tools must be called in order
(screen -> check applicability -> route -> check claims -> request approval)
for each account and playbook.

FEEDBACK: one server session is one run. After every governed decision the
playbook's quality kill criteria are checked against the session's counts
(audit blocks, drafts, output-gate refusals) and the playbook's reports, and a
tripped criterion engages the kill switch, as the batch runner does per run.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from agent import AGENT_ID, __version__, config
from agent.feedback import kill_criteria, kill_switch, reports, trusted
from agent.governance.audit import AuditBlocked, AuditTrail, JsonlAuditSink, purpose_problems
from agent.governance.error_log import ErrorLog
from agent.input import playbook as pbmod
from agent.input.base import InputError
from agent.input.models import Enrichment
from agent.output.writer import RunPaths, approval_path, brief_path, write_json, write_text
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext
from agent.processing.checks import check_brief
from agent.processing.icp import INCLUDE
from agent.processing.routing import route
from agent.run_playbook import _already_briefed, _load_inputs

ROOT = Path(__file__).resolve().parent.parent
AGENT_DECISIONS = {"hold": "hold", "drop": "score"}  # what an agent may record with write_audit_record


class ToolFailure(Exception):
    """A tool refused or failed. The message always ends with what to do next."""

    def __init__(self, message: str, recovery: str):
        super().__init__(f"{message} Recovery: {recovery}")


class GovernedTools:
    def __init__(self, out_dir: str | Path | None = None, *, root: Path = ROOT, playbooks_dir: Path | None = None,
                 inputs: dict | None = None, sink=None):
        self.run_id = "mcp-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]
        self.paths = RunPaths(Path(out_dir) if out_dir else config.out_dir(), self.run_id)
        self.errors = ErrorLog(self.paths.errors, self.run_id)
        self.playbooks_dir = Path(playbooks_dir) if playbooks_dir else trusted.PLAYBOOKS
        self.io = inputs or _load_inputs(root)
        self.sink = sink or JsonlAuditSink(self.paths.audit)
        self.state: dict[tuple[str, str], dict] = {}
        self.counts: dict[str, dict] = {}

    # ---- helpers ---------------------------------------------------------------------------
    def _fail(self, stage: str, message: str, recovery: str) -> None:
        self.errors.record(f"tool.{stage}", message)
        raise ToolFailure(message, recovery)

    def _playbook(self, playbook_id: str) -> tuple[dict, str]:
        try:
            pb = trusted.load_trusted(playbook_id, self.playbooks_dir)
            sha = trusted.sha256(trusted.playbook_file(playbook_id, self.playbooks_dir))
        except trusted.Untrusted as exc:
            self._fail("playbook", str(exc), "call list_playbooks and use one of the ids it returns.")
        if pb["trigger_status"] != "implemented":
            self._fail("playbook", f"playbook {playbook_id}: trigger not implemented yet: "
                       f"{pb.get('trigger_not_implemented_reason')}",
                       "use the bank-sr26-2 playbook; this trigger cannot produce a brief yet.")
        if pb.get("status", "active") != "active":
            self._fail("playbook", f"playbook {playbook_id} is {pb['status']}.", "ask the playbook owner to reactivate it.")
        killed = kill_switch.engaged(self.paths.state, playbook_id)
        if killed:
            self._fail("playbook", f"playbook {playbook_id} is stopped by its kill switch ({killed['by']}: {killed['reason']}).",
                       "stop; only the playbook owner or an approver can clear it with python3 -m agent.feedback.kill --clear.")
        return pb, sha

    def _trail(self, principal: str, pid: str, version: str, required_for: str) -> AuditTrail:
        return AuditTrail(self.sink, AGENT_ID, __version__, principal, pid, version, self.run_id, self.errors,
                          required_for)

    def _pb_trail(self, pb: dict) -> AuditTrail:
        return self._trail(pb["approval"]["principal"], pb["playbook_id"], pb["version"], pb["audit"]["required_for"])

    def _account(self, account_id: str):
        try:
            for a in self.io["accounts"].list_accounts():
                if a.id == account_id or a.system_id == account_id:
                    return a
        except InputError as exc:
            self._fail("input", f"account source failed: {exc}", "check the HubSpot adapter and retry.")
        self._fail("input", f"no account {account_id!r} in the system of record.",
                   "use a HubSpot company id such as hs-1001.")

    def _step(self, playbook_id: str, account_id: str, needs: str) -> dict:
        st = self.state.get((playbook_id, self._account(account_id).id))
        order = ["screened", "applicable", "routed"]
        if not st or order.index(st["stage"]) < order.index(needs):
            self._fail("order", f"{account_id} has not passed '{needs}' for {playbook_id} in this session.",
                       "call the tools in order: screen_account, check_applicability, route_contact, check_claims, "
                       "request_approval.")
        return st

    def _counts(self, pid: str) -> dict:
        since = kill_switch.last_cleared(self.paths.state, pid)  # a clear means a human reviewed the earlier counts
        if self.counts.get(pid, {}).get("since") != since:
            self.counts[pid] = {"since": since, "audit_blocked": 0, "drafted": 0, "gate_failed": 0}
        return self.counts[pid]

    def _count(self, pb: dict, metric: str) -> None:
        self._counts(pb["playbook_id"])[metric] += 1

    def _check_kill(self, pb: dict) -> None:
        """FEEDBACK: the playbook's quality kill criteria over this session's counts (A-037)."""
        pid = pb["playbook_id"]
        counts = {k: v for k, v in self._counts(pid).items() if k != "since"}
        attempted = counts["drafted"] + counts["gate_failed"]
        metrics = {**counts, "gate_failed_ratio": kill_criteria.ratio(counts["gate_failed"], attempted),
                   **reports.metrics(self.paths.state, pid)}
        hits = kill_criteria.tripped(pb["kill_criteria"], metrics)
        if not hits or kill_switch.engaged(self.paths.state, pid):
            return
        reason = "kill criteria tripped: " + "; ".join(f"{h['id']} ({h['metric']}={h['value']})" for h in hits)
        kill_switch.engage(self.paths.state, pid, by=pb["owner"], reason=reason)  # engage first: the safe direction
        self.errors.record("feedback.kill_criteria", f"{pid}: {reason}", severity="warning")
        try:
            self._pb_trail(pb).perform(action="block", object_id=f"playbook:{pid}", fs=True, commit=lambda: None,
                                       purpose=f"Pause the {pid} playbook because its quality kill criteria tripped.",
                                       sources=[f"run:{self.run_id}"], detail={"tripped": hits, "via": "mcp"})
        except AuditBlocked:
            pass  # the switch is engaged; the failure is in the error log

    def _recovery(self, pb: dict, retry: str) -> str:
        """The retry advice, unless the kill switch is now engaged: then the only next step is the owner's."""
        killed = kill_switch.engaged(self.paths.state, pb["playbook_id"])
        if not killed:
            return retry
        return (f"stop; the {pb['playbook_id']} playbook is now stopped by its kill switch ({killed['reason']}). "
                "Only the playbook owner or an approver can clear it, with python3 -m agent.feedback.kill --clear.")

    def _guard(self, pb: dict, fn, stage: str):
        try:
            result = fn()
        except AuditBlocked as exc:
            self._count(pb, "audit_blocked")
            self._check_kill(pb)
            self._fail(stage, str(exc), "the audit record could not be written, so nothing happened. " + self._recovery(
                pb, "Fix the audit store (see errors.jsonl), then retry. Do not work around it."))
        self._check_kill(pb)
        return result

    # ---- tools -------------------------------------------------------------------------------
    def list_playbooks(self, motion_id: str = "reign-first-motion") -> dict:
        """The motion's playbooks: buyer segment, trigger, channel, and whether the trigger is implemented."""
        try:
            motion = pbmod.load(trusted.motion_file(motion_id, self.playbooks_dir))
        except (trusted.Untrusted, pbmod.PlaybookError) as exc:
            self._fail("playbook", str(exc), "use motion_id 'reign-first-motion'.")
        out = []
        for pid in motion["playbooks"]:
            try:
                pb = pbmod.load(trusted.playbook_file(pid, self.playbooks_dir))
            except (trusted.Untrusted, pbmod.PlaybookError) as exc:
                self._fail("playbook", f"playbook {pid} in motion {motion_id} could not be loaded: {exc}",
                           "ask the playbook owner to fix the file; playbooks/SCHEMA.md explains each field.")
            out.append({"playbook_id": pid, "segment": pb["audience"]["segment"], "trigger": pb["trigger"],
                        "channel": pb["channel"], "trigger_status": pb["trigger_status"],
                        "reason": pb.get("trigger_not_implemented_reason"),
                        "kill_switch": kill_switch.engaged(self.paths.state, pid)})
        try:
            accounts = [{"id": a.id, "name": a.name, "segment": a.segment} for a in self.io["accounts"].list_accounts()]
        except InputError as exc:
            self._fail("input", f"account source failed: {exc}", "check the HubSpot adapter and retry.")
        return {"motion": motion["motion_id"], "playbooks": out, "accounts": accounts}

    def fetch_source(self, trigger_id: str) -> dict:
        """The trigger's verified sources, the facts already extracted from them, and the structural conditions."""
        try:
            t = self.io["feed"].get(trigger_id)
        except InputError as exc:
            self._fail("fetch_source", str(exc), "use a trigger id from list_playbooks, such as SR-26-2.")
        if not t.implemented:
            self._fail("fetch_source", f"trigger {trigger_id} is not implemented: {t.not_implemented_reason}",
                       "use SR-26-2.")
        verified = [asdict(s) for s in t.sources + t.context_sources if s.verified and s.url]
        return {"trigger": {"id": t.id, "title": t.title, "issuer": t.issuer, "published": t.published,
                            "jurisdiction": t.jurisdiction, "regulator": t.regulator},
                "sources": verified,
                "facts": [asdict(f) for f in t.facts],
                "context_by_jurisdiction": {k: [asdict(f) for f in v] for k, v in t.context_by_jurisdiction.items()},
                "structural_conditions": list(t.structural_conditions),
                "note": "Read the source URLs yourself. Cite only these source ids; any other URL fails the gate."}

    def screen_account(self, playbook_id: str, account_id: str) -> dict:
        """Run the ICP for one account. Dropped, held or watched accounts are closed for this session."""
        pb, _ = self._playbook(playbook_id)
        acct = self._account(account_id)
        icp = self.io["icp"]
        if acct.segment != pb["audience"]["segment"]:
            self._fail("screen", f"{acct.name} is in segment '{acct.segment}', not this playbook's "
                       f"'{pb['audience']['segment']}'.", "pick the playbook whose segment matches, or stop.")
        motion_trail = self._trail(pb["approval"]["principal"], pb["playbook_id"], pb["version"], "all_segments")
        fs = icp.is_fs(acct)
        decision = icp.prescreen(acct)
        enrichment = Enrichment.empty(acct.id)
        if decision is None:
            # R-17 order (adversarial QA F1): audit record first, then the enrichment adapter, inside the commit.
            try:
                enrichment = self._guard(pb, lambda: motion_trail.perform(
                    action="enrich", object_id=acct.system_id, fs=fs,
                    commit=lambda: self.io["enrichment"].enrich(acct.id),
                    purpose=f"Attach enrichment to {acct.name} to test the first Reign motion ICP criteria.",
                    sources=[f"clay:company/{acct.id}"]), "screen")
            except InputError as exc:
                self._fail("screen", f"enrichment source failed for {acct.id}: {exc}", "check the Clay adapter and retry.")
            decision = icp.evaluate(acct, enrichment)
        self._guard(pb, lambda: motion_trail.perform(
            action="score", object_id=acct.system_id, fs=fs, commit=lambda: None,
            purpose=f"Record the ICP decision '{decision.decision}' for {acct.name} in the first Reign motion.",
            sources=[acct.system_id] + ([enrichment.source] if enrichment.source else []),
            detail={"decision": decision.decision, "reasons": decision.reasons, "flags": decision.flags,
                    "via": "mcp"}), "screen")
        if decision.decision == INCLUDE:
            self.state[(playbook_id, acct.id)] = {"stage": "screened", "account": acct, "enrichment": enrichment,
                                                  "decision": decision}
        return {"account": {"id": acct.id, "system_id": acct.system_id, "name": acct.name, "segment": acct.segment,
                            "industry": acct.industry, "employees": acct.employees, "hq_country": acct.hq_country,
                            "total_assets_usd": acct.total_assets_usd, "runs_forge": acct.runs_forge,
                            "owner": acct.owner, "description": acct.description},
                "enrichment": asdict(enrichment), "decision": decision.decision, "reasons": decision.reasons,
                "flags": decision.flags, "fs": fs,
                "do_not_contact": decision.decision != INCLUDE,
                "next": "check_applicability" if decision.decision == INCLUDE else
                        "stop: this account is closed for outreach; its decision is in the audit log"}

    def check_applicability(self, playbook_id: str, account_id: str) -> dict:
        """Preflight: may a brief be drafted, and what must it say about applicability?"""
        pb, _ = self._playbook(playbook_id)
        st = self._step(playbook_id, account_id, "screened")
        acct = st["account"]
        try:
            trigger = self.io["feed"].get(pb["trigger"]["id"])
        except InputError as exc:
            self._fail("applicability", f"regulatory feed failed: {exc}", "check the regulator feed adapter and retry.")
        prior = _already_briefed(self.paths, acct.system_id, trigger.id, playbook_id)
        if prior:
            self._fail("applicability", f"{acct.name} already has a brief for {trigger.id}: {prior}.",
                       "do not draft again; the account owner decides on the existing request.")
        result = pf.check(trigger, acct, st["enrichment"], pb)
        if result.status != pf.READY:
            self._guard(pb, lambda: self._pb_trail(pb).perform(
                action="hold", object_id=acct.system_id, fs=st["decision"].fs, commit=lambda: None,
                purpose=f"Record that no {trigger.id} brief is drafted for {acct.name}: preflight {result.status}.",
                sources=[s.url for s in trigger.sources if s.url] + [acct.system_id],
                detail={"preflight": result.status, "reasons": result.reasons, "via": "mcp"}), "applicability")
            del self.state[(playbook_id, acct.id)]
        else:
            st.update(stage="applicable", preflight=result, trigger=trigger)
        return {"status": result.status, "applicability": result.applicability, "reasons": result.reasons,
                "caveats": result.caveats, "must_include_phrase": pf.CAVEAT if pf.CAVEAT in result.caveats else None,
                "certain_context": [asdict(f) for f in result.context],
                "next": "route_contact" if result.status == pf.READY else "stop: held and recorded in the audit log"}

    def route_contact(self, playbook_id: str, account_id: str) -> dict:
        """Suggest contacts by lane from job titles. Do-not-route titles are never returned."""
        pb, _ = self._playbook(playbook_id)
        st = self._step(playbook_id, account_id, "applicable")
        acct = st["account"]
        try:
            contacts = self.io["contacts"].contacts_for(acct.id)
        except InputError as exc:
            self._fail("route", f"contact source failed: {exc}", "check the ZoomInfo adapter and retry.")
        routing = pb.get("routing", {})
        lanes = routing.get("lanes", {})
        routed, skipped = route(contacts, lanes, routing.get("do_not_route", []), list(lanes))
        self._guard(pb, lambda: self._pb_trail(pb).perform(
            action="route", object_id=acct.system_id, fs=st["decision"].fs, commit=lambda: None,
            purpose=f"Record which {acct.name} contacts the brief suggests to the account owner, by lane.",
            sources=[c.system_id for c in contacts] or [acct.system_id],
            detail={"lanes": {l: [c.system_id for c in cs] for l, cs in routed.items()},
                    "not_routed": [{"contact": c.system_id, "why": why} for c, why in skipped], "via": "mcp"}),
            "route")
        st.update(stage="routed", routed=routed, not_routed=[c for c, _ in skipped],
                  flags=list(st["decision"].flags) + [f"A contact was not routed: {why}." for c, why in skipped])
        return {"lanes": {l: [{"id": c.system_id, "name": c.name, "title": c.title} for c in cs]
                          for l, cs in routed.items()},
                "not_routed": [{"id": c.system_id, "title": c.title, "why": why} for c, why in skipped],
                "next": "draft the brief, then check_claims"}

    def _context(self, pb: dict, st: dict) -> BriefContext:
        claims = {c["id"]: c for c in self.io["claims"]}
        return BriefContext(st["trigger"], st["preflight"], st["account"], st["enrichment"], st["routed"],
                            [claims[i] for i in pb.get("claims", [])], st["account"].owner, st["flags"], not_routed=st.get("not_routed", []))

    def check_claims(self, playbook_id: str, account_id: str, brief_markdown: str) -> dict:
        """Run the output gate on a draft. Returns every problem, the allowed sources and the approved claims."""
        pb, _ = self._playbook(playbook_id)
        st = self._step(playbook_id, account_id, "routed")
        ctx = self._context(pb, st)
        problems = check_brief(brief_markdown, **ctx.gate_kwargs())
        return {"passed": not problems, "problems": problems,
                "allowed_sources": [{"id": i, "cite_as": d} for i, d in ctx.sources()],
                "approved_claims": [{"id": c["id"], "text": c["text"]} for c in ctx.claims],
                "open_questions_from_the_record": st["flags"],
                "next": "request_approval" if not problems else "fix every problem and call check_claims again"}

    def write_audit_record(self, playbook_id: str, account_id: str, decision: str, purpose: str,
                           sources: list[str]) -> dict:
        """Record the agent's own decision to hold or drop an account, with its reason. R-17 fields enforced."""
        pb, _ = self._playbook(playbook_id)
        if decision not in AGENT_DECISIONS:
            self._fail("audit", f"decision {decision!r} is not one an agent may record.",
                       f"use one of {sorted(AGENT_DECISIONS)}; drafting goes through request_approval.")
        problems = purpose_problems(purpose)
        if not sources or not all(isinstance(x, str) and x.strip() for x in sources):
            problems.append("sources must be a non-empty list of URLs or system ids")
        if problems:
            self._fail("audit", "; ".join(problems) + ".",
                       "write one specific purpose sentence and cite the sources for this hold or drop, then call again.")
        acct = self._account(account_id)
        rec = self._guard(pb, lambda: self._pb_trail(pb).perform(
            action=AGENT_DECISIONS[decision], object_id=acct.system_id, fs=self.io["icp"].is_fs(acct),
            purpose=purpose, sources=list(sources), commit=lambda: {"recorded": True},
            detail={"agent_decision": decision, "via": "mcp"}), "audit")
        self.state.pop((playbook_id, acct.id), None)
        return {**rec, "decision": decision, "account": acct.system_id,
                "next": "stop for this account; the decision is in the audit log"}

    def request_approval(self, playbook_id: str, account_id: str, brief_markdown: str) -> dict:
        """Write the brief and an approval request routed to the named account owner. Nothing is sent."""
        pb, sha = self._playbook(playbook_id)
        st = self._step(playbook_id, account_id, "routed")
        ctx = self._context(pb, st)
        acct, trigger = st["account"], st["trigger"]
        problems = check_brief(brief_markdown, **ctx.gate_kwargs())
        if problems:  # enforced here, whatever the agent was told
            self.errors.record("tool.request_approval", "brief failed the output gate",
                               context={"account": acct.id, "problems": problems})
            self._count(pb, "gate_failed")
            self._check_kill(pb)
            raise ToolFailure("the brief failed the output gate: " + "; ".join(problems), self._recovery(
                pb, "fix each problem (check_claims lists them) and call request_approval again."))
        prior = _already_briefed(self.paths, acct.system_id, trigger.id, playbook_id)
        if prior:
            self._fail("request_approval", f"{acct.name} already has a brief for {trigger.id}: {prior}.",
                       "do not draft again; the account owner decides on the existing request.")
        bpath, apath = brief_path(self.paths, acct.system_id), approval_path(self.paths, acct.system_id)
        request = {
            "request_id": uuid.uuid4().hex, "run_id": self.run_id, "status": "pending",
            "playbook": {"id": playbook_id, "version": pb["version"]}, "playbook_sha256": sha,
            "account": {"id": acct.system_id, "name": acct.name}, "trigger": trigger.id, "channel": pb["channel"],
            "route_to": {"account_owner": acct.owner}, "brief": str(bpath), "send": False, "blockable": True,
            "sender": pb["approval"].get("sender", "none"), "drafted_by": "agent via MCP",
            "suggested_recipients_in_existing_relationship": {l: [c.system_id for c in cs]
                                                              for l, cs in st["routed"].items()},
            "note": ("Nothing has been sent and the bank has not been contacted. The named account owner decides "
                     "whether to share this brief in the existing relationship, with python3 -m agent.feedback.decide."),
        }

        def commit():
            write_text(bpath, brief_markdown if brief_markdown.endswith("\n") else brief_markdown + "\n")
            try:
                write_json(apath, request)
            except Exception:
                bpath.unlink(missing_ok=True)
                raise
            self._count(pb, "drafted")

        self._guard(pb, lambda: self._pb_trail(pb).perform(
            action="create", object_id=acct.system_id, fs=st["decision"].fs,
            sources=sorted(ctx.allowed_urls() | {acct.system_id}),
            purpose=(f"Draft the {trigger.title.split(':')[0]} brief for {acct.name} and route it to the account "
                     f"owner {acct.owner}, who decides before anything is shared."),
            commit=commit, detail={"brief": str(bpath), "approval_request": str(apath),
                                   "request_id": request["request_id"], "via": "mcp"}), "request_approval")
        del self.state[(playbook_id, acct.id)]
        review_path = None
        try:  # the human review view of this MCP session's run; files stay the source of truth
            from agent.output import review
            from evals.score_run import score as score_run
            self.paths.run_dir.mkdir(parents=True, exist_ok=True)
            review_path = str(review.write(self.paths.run_dir, out_root=self.paths.out, score=score_run(self.paths.out, run_dir=self.paths.run_dir)))
        except Exception as exc:
            self.errors.record("output.review", exc)
        return {"brief": str(bpath), "approval_request": str(apath), "route_to": acct.owner, "sent": False,
                "review": review_path,
                "next": f"stop; {acct.owner} decides with python3 -m agent.feedback.decide --request {apath}"}
