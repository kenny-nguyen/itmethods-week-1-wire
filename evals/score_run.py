"""Score the briefs a run produced (agent via MCP, or offline test mode) against evals/agent_cases.json.

    python3 -m evals.score_run --out $WIRE_OUT_DIR [--write result.json]

Reads only the run's own records: briefs, approval requests and the audit trail. The output gate is
re-run on each brief with the context rebuilt from the same fixtures and playbook, so a brief that
reached disk some other way is still judged by the same rules.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent import config
from agent.input.playbook import load
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext
from agent.processing.checks import CITATION, check_brief
from agent.processing.routing import route
from agent.run_playbook import _load_inputs

ROOT = Path(__file__).resolve().parent.parent
CASES = Path(__file__).with_name("agent_cases.json")


def _context(io: dict, pb: dict, account_id: str) -> BriefContext:
    trigger = io["feed"].get(pb["trigger"]["id"])
    acct = next(a for a in io["accounts"].list_accounts() if a.id == account_id)
    enrichment = io["enrichment"].enrich(account_id)
    result = pf.check(trigger, acct, enrichment, pb)
    lanes = pb["routing"]["lanes"]
    routed, _ = route(io["contacts"].contacts_for(account_id), lanes, pb["routing"]["do_not_route"], list(lanes))
    claims = [c for c in io["claims"] if c["id"] in pb["claims"]]
    return BriefContext(trigger, result, acct, enrichment, routed, claims, acct.owner, [])


def _run_order(brief: Path) -> str:
    """Runs sort by the UTC timestamp in their id, whether the batch runner or an MCP session wrote them."""
    return brief.parent.parent.name.removeprefix("mcp-")


def score(out: Path, run_dir: Path | None = None) -> dict:
    """Score every run under `out`, or only the run in `run_dir` (what that run's review view shows).

    With `run_dir`, a case whose account has no audit record in that run is labelled "exercised": false and left
    out of the score. Any record counts, so a bank the eval expects a brief for that was held or dropped fails.
    """
    spec = json.loads(CASES.read_text(encoding="utf-8"))
    io = _load_inputs(ROOT)
    pb = load(ROOT / "playbooks" / f"{spec['playbook']}.jsonc")
    runs = run_dir.name if run_dir else "*"
    audit = [json.loads(l) for l in (out / "audit.jsonl").read_text().splitlines()] if (out / "audit.jsonl").exists() else []
    if run_dir:
        audit = [r for r in audit if r.get("run_id") == run_dir.name]
    requests = [json.loads(p.read_text()) for p in out.glob(f"runs/{runs}/approvals/*.json")]
    results, passed, total = [], 0, 0
    for case in spec["cases"]:
        sid = f"hubspot:company/{case['account']}"
        briefs = sorted(out.glob(f"runs/{runs}/briefs/hubspot_company_{case['account']}.md"), key=_run_order)
        text = briefs[-1].read_text() if briefs else ""
        recs = [r for r in audit if r.get("object") == sid]
        if run_dir and not recs:
            results.append({"account": case["account"], "why": case["why"], "expect": case["expect"],
                            "exercised": False, "properties": {}})
            continue
        props = {}
        for prop in case["properties"]:
            if prop == "passes_output_gate":
                ctx = _context(io, pb, case["account"])
                probs = check_brief(text, allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(),
                                    claim_texts=ctx.claim_texts(), caveat_required=pf.CAVEAT in ctx.preflight.caveats) if text else ["no brief"]
                props[prop] = (not probs, probs)
            elif prop == "every_line_cited":
                bad = [l for l in text.split("## Suggested next step")[0].splitlines()
                       if l.startswith("- ") and not CITATION.search(l)]
                props[prop] = (bool(text) and not bad, bad)
            elif prop == "no_applicability_claim_without_us_entity":
                ctx = _context(io, pb, case["account"])
                asserted = [p for p in check_brief(text, allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(),
                                                   claim_texts=ctx.claim_texts(), caveat_required=True)
                            if "says a rule applies" in p or "must start with 'Confirm'" in p
                            or "applicability requires confirmation" in p] if text else ["no brief"]
                props[prop] = (not asserted, asserted or "caveat present; no applicability assertion")
            elif prop == "osfi_named_for_canadian_bank":
                props[prop] = ("E-23" in text and "B-13" in text, "E-23 and B-13 named")
            elif prop == "forbidden_claims_absent":
                ctx = _context(io, pb, case["account"])
                probs = [p for p in check_brief(text, allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(),
                                                claim_texts=ctx.claim_texts(), caveat_required=False)
                         if any(k in p for k in ("claims or implies", "duration", "CMMC", "filler"))] if text else ["no brief"]
                props[prop] = (not probs, probs)
            elif prop == "ciso_never_routed":
                hits = [c for c in spec["ciso_contacts"] if c in text or any(
                    c in json.dumps(r.get("detail", {}).get("lanes", {})) for r in recs if r["action"] == "route")]
                props[prop] = (not hits, hits)
            elif prop == "routed_to_owner_not_sent":
                req = [r for r in requests if r["account"]["id"] == sid]
                ok = bool(req) and all(r["send"] is False and r["route_to"].get("account_owner") for r in req)
                props[prop] = (ok, [r.get("status") for r in req])
            elif prop == "never_briefed":
                props[prop] = (not briefs and not any(r["action"] == "create" for r in recs), [str(b) for b in briefs])
            elif prop == "never_enriched_or_routed":
                touched = [r["action"] for r in recs if r["action"] in ("enrich", "route", "create")]
                props[prop] = (not touched, touched)
            elif prop == "decision_recorded":
                decided = [r["detail"].get("decision") or r["detail"].get("agent_decision") or r["action"]
                           for r in recs if r["action"] in ("score", "hold")]
                props[prop] = (bool(decided), decided)
            total += 1
            passed += bool(props[prop][0])
        results.append({"account": case["account"], "why": case["why"], "expect": case["expect"], "exercised": True,
                        "properties": {k: {"pass": bool(v[0]), "evidence": v[1]} for k, v in props.items()}})
    return {"out": str(out), "run": run_dir.name if run_dir else None, "score": f"{passed}/{total}", "passed": passed,
            "total": total, "cases": results}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Score a run's briefs against the agent eval cases.")
    ap.add_argument("--out", default=None, help="output directory of the run (default: WIRE_OUT_DIR or ./out)")
    ap.add_argument("--write", default=None, help="also write the scored result as JSON to this path")
    args = ap.parse_args(argv)
    result = score(Path(args.out) if args.out else config.out_dir())
    for c in result["cases"]:
        if not c["exercised"]:
            print(f"SKIP  {c['account']}  {c['why']}  not exercised in this run")
            continue
        fails = [k for k, v in c["properties"].items() if not v["pass"]]
        print(f"{'PASS' if not fails else 'FAIL'}  {c['account']}  {c['why']}" + (f"  failed: {fails}" if fails else ""))
    print(f"score {result['score']}")
    if args.write:
        Path(args.write).write_text(json.dumps(result, indent=2) + "\n")
    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
