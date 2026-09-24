"""One-page HTML review view of a run, for the demo (operator decision, log D-036).

    python3 -m agent.output.review --run out/runs/<run-id>

Generated from the run's own files, never hand-written. The Markdown and JSON files stay the source
of truth; every section links to the file it came from (relative links, so they also work on GitHub).
Self-contained: inline CSS, no scripts, no external requests. All record text is HTML-escaped.
"""

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

CSS = """
body{font:15px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0;background:#f6f7f9;color:#1d2330}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid #d9dde5;padding-bottom:4px}
.meta{color:#5b6475;font-size:13px}.banner{background:#fff4d6;border:1px solid #e8c766;padding:8px 12px;border-radius:6px;margin:12px 0}
.card{background:#fff;border:1px solid #d9dde5;border-radius:8px;padding:12px 16px;margin:10px 0}
pre{white-space:pre-wrap;word-wrap:break-word;font:13px/1.45 ui-monospace,Menlo,Consolas,monospace;margin:0}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;border-bottom:1px solid #e6e9ef;padding:5px 6px;vertical-align:top}
.ok{color:#146c2e;font-weight:600}.bad{color:#a1261b;font-weight:600}a{color:#1f56c2}
"""


def _rel(path: Path, base: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(base.resolve()))
    except ValueError:
        import os
        return os.path.relpath(Path(path).resolve(), base.resolve())


def _jsonl(path: Path) -> list[dict]:
    rows = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def render(run_dir: Path, *, audit_path: Path, errors_path: Path, score: dict | None = None) -> str:
    run_dir = Path(run_dir)
    run_id = run_dir.name
    audit = [r for r in _jsonl(audit_path) if r.get("run_id") == run_id]
    errors = [e for e in _jsonl(errors_path) if e.get("run_id") == run_id]
    summary_path = run_dir / "summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    requests = sorted(run_dir.glob("approvals/*.json"))
    briefs = sorted(run_dir.glob("briefs/*.md"))
    provider = summary.get("provider") or ("agent via MCP" if run_id.startswith("mcp-") else "unknown")
    link = lambda p: f'<a href="{escape(_rel(p, run_dir))}">{escape(_rel(p, run_dir))}</a>'  # noqa: E731

    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><title>Run review {escape(run_id)}</title>"
           f"<style>{CSS}</style></head><body><main>",
           f"<h1>Run review</h1><div class=meta>run {escape(run_id)} &middot; drafted by {escape(provider)}"
           f" &middot; generated from the run's files; those files are the source of truth</div>"]
    if provider == "offline-test-mode":
        out.append("<div class=banner><b>OFFLINE TEST MODE.</b> These briefs were drafted by the deterministic CI "
                   "template, not by the agent.</div>")

    out.append("<h2>Briefs (with the risk and engineering framings)</h2>")
    for b in briefs:
        out.append(f"<div class=card><div class=meta>{link(b)}</div><pre>{escape(b.read_text())}</pre></div>")
    if not briefs:
        out.append("<p>No brief was written in this run.</p>")

    out.append("<h2>Approval requests</h2><table><tr><th>Account</th><th>Status</th><th>Routed to</th>"
               "<th>Sent</th><th>File</th></tr>")
    for p in requests:
        r = json.loads(p.read_text())
        out.append(f"<tr><td>{escape(r['account']['name'])}</td><td>{escape(r['status'])}</td>"
                   f"<td>{escape(str(r.get('route_to', {}).get('account_owner')))}</td>"
                   f"<td>{'yes' if r.get('send') else 'no'}</td><td>{link(p)}</td></tr>")
    out.append("</table>")

    if score:
        cls = "ok" if score["passed"] == score["total"] else "bad"
        out.append(f"<h2>Eval score</h2><p class={cls}>{escape(score['score'])}</p><table>"
                   "<tr><th>Account</th><th>Expect</th><th>Failed properties</th></tr>")
        for c in score["cases"]:
            fails = [k for k, v in c["properties"].items() if not v["pass"]]
            out.append(f"<tr><td>{escape(c['account'])}</td><td>{escape(c['expect'])}</td>"
                       f"<td class={'bad' if fails else 'ok'}>{escape(', '.join(fails) or 'none')}</td></tr>")
        out.append("</table><p class=meta>Cases: evals/agent_cases.json; scorer: evals/score_run.py</p>")

    out.append("<h2>Held, dropped, watched or blocked</h2><table><tr><th>Object</th><th>Decision</th><th>Reason</th></tr>")
    for r in audit:
        d = r.get("detail", {})
        decision = d.get("decision") or d.get("agent_decision") or (r["action"] if r["action"] in ("hold", "block") else None)
        if decision and decision not in ("include",):
            reasons = d.get("reasons") or [r.get("purpose")]
            out.append(f"<tr><td>{escape(r['object'])}</td><td>{escape(str(decision))}</td>"
                       f"<td>{escape('; '.join(map(str, reasons)))}</td></tr>")
    out.append(f"</table><p class=meta>Source: {link(audit_path)}</p>")

    out.append(f"<h2>Audit trail for this run ({len(audit)} records)</h2><table>"
               "<tr><th>Action</th><th>Object</th><th>Principal</th><th>Send</th><th>Purpose</th></tr>")
    for r in audit:
        out.append(f"<tr><td>{escape(r['action'])}</td><td>{escape(r['object'])}</td><td>{escape(r['principal'])}</td>"
                   f"<td>{escape(str(r['send']))}</td><td>{escape(r['purpose'])}</td></tr>")
    out.append(f"</table><p class=meta>Source: {link(audit_path)}</p>")

    out.append(f"<h2>Errors ({len(errors)})</h2>")
    out.append("<table><tr><th>Stage</th><th>Message</th></tr>" + "".join(
        f"<tr><td>{escape(e['stage'])}</td><td>{escape(e['message'])}</td></tr>" for e in errors) + "</table>"
        if errors else "<p>None.</p>")
    source = link(errors_path) if Path(errors_path).exists() else "no error log written (nothing failed)"
    out.append(f"<p class=meta>Source: {source}</p></main></body></html>")
    return "\n".join(out)


def write(run_dir: Path, *, out_root: Path, score: dict | None = None) -> Path:
    html = render(run_dir, audit_path=Path(out_root) / "audit.jsonl", errors_path=Path(out_root) / "errors.jsonl",
                  score=score)
    target = Path(run_dir) / "review.html"
    target.write_text(html, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write the one-page HTML review view for a run.")
    ap.add_argument("--run", required=True, help="the run directory, e.g. out/runs/<run-id>")
    args = ap.parse_args(argv)
    from evals.score_run import score as score_run
    run_dir = Path(args.run)
    out_root = run_dir.parent.parent
    print(write(run_dir, out_root=out_root, score=score_run(out_root, run_dir=run_dir)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
