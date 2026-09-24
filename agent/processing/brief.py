"""Brief context and the two non-agent drafting paths.

The agent is the Claude skill driving the MCP tools (skills/, agent/mcp_server.py;
operator decision A-046). This module holds what those tools share (BriefContext)
and two drafting paths that are NOT the agent:

- TemplateProvider, "offline test mode": deterministic, no key, for CI and tests
  only. It must never be presented as the agent.
- AnthropicProvider, the direct model-API path: the Claude Messages API over the
  standard library. Documented, and NOT exercised live (no key in the build
  environment).

Every draft, from any path, goes through the same output gate (`checks.py`).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from agent.input.models import Account, Contact, Enrichment, Trigger
from agent.processing.preflight import CAVEAT, Preflight

ROOT = Path(__file__).resolve().parents[2]
SYSTEM_PROMPT = ROOT / "prompts" / "brief_system.md"
DEFAULT_MODEL = "claude-opus-5"


RECOVERY = ("Recovery: retry the run; or run in offline test mode (unset ANTHROPIC_API_KEY, or set WIRE_PROVIDER=offline) "
            "to check the pipeline with the deterministic template; or check ANTHROPIC_API_KEY, WIRE_MODEL and network access to "
            "api.anthropic.com.")


class ProviderError(Exception):
    """A model call failed. Operator decision A-033: fail loudly and name the fix; never fall back silently."""

    def __init__(self, message: str):
        super().__init__(f"{message}. {RECOVERY}")


@dataclass
class BriefContext:
    trigger: Trigger
    preflight: Preflight
    account: Account
    enrichment: Enrichment
    routed: dict[str, list[Contact]]
    claims: list[dict]  # approved product claims for this play
    approver: str
    flags: list[str] = field(default_factory=list)

    def sources(self) -> list[tuple[str, str]]:
        """(id, 'title - url' or system record) for every id the brief may cite."""
        out = [(s.id, f"{s.title} - {s.url}") for s in self.trigger.sources + self.trigger.context_sources
               if s.verified and s.url]
        out += [(c["id"], f"iTmethods - {' ; '.join(c['urls'])}") for c in self.claims]
        out.append((self.account.system_id, "HubSpot company record"))
        if self.enrichment.source:
            out.append((self.enrichment.source, "Clay enrichment row"))
        out += [(c.system_id, "ZoomInfo contact record") for lane in self.routed.values() for c in lane]
        return out

    def allowed_ids(self) -> set[str]:
        return {i for i, _ in self.sources()}

    def allowed_urls(self) -> set[str]:
        urls = {s.url for s in self.trigger.sources + self.trigger.context_sources if s.verified and s.url}
        return urls | {u for c in self.claims for u in c["urls"]}

    def claim_texts(self) -> dict[str, str]:
        return {c["id"]: c["text"] for c in self.claims}

    def to_json(self) -> dict:
        t, p, a, e = self.trigger, self.preflight, self.account, self.enrichment
        return {
            "trigger": {"id": t.id, "title": t.title, "issuer": t.issuer, "published": t.published,
                        "facts": [{"text": f.text, "source": f.source} for f in t.facts]},
            "preflight": {"applicability": p.applicability, "reasons": p.reasons, "caveats": p.caveats,
                          "context": [{"text": f.text, "source": f.source} for f in p.context]},
            "account": {"id": a.system_id, "name": a.name, "segment": a.segment, "hq_country": a.hq_country,
                        "runs_forge": a.runs_forge, "description": a.description},
            "enrichment": {"source": e.source, "agent_adoption": e.agent_adoption,
                           "risk_committee": e.risk_committee},
            "routed_contacts": {lane: [{"id": c.system_id, "name": c.name, "title": c.title} for c in cs]
                                for lane, cs in self.routed.items()},
            "approved_product_claims": self.claims,
            "open_questions": self.flags,
            "approver": self.approver,
            "sources": [{"id": i, "cite_as": d} for i, d in self.sources()],
        }


def cite(text: str, *ids: str) -> str:
    """Put the citation inside every sentence, before its full stop, so no sentence is left unsourced."""
    tag = " " + " ".join(f"[{i}]" for i in ids)
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(p[:-1] + tag + p[-1] if p[-1] in ".!?" else p + tag for p in parts)


class TemplateProvider:
    """OFFLINE TEST MODE, for CI only; not the agent. A deterministic brief in the structure the operator
    decided for SR 26-2 (A-044):
    what changed -> what is certain for this account -> what depends on its structure
    (each line "Confirm") -> a suggested next step. It never says a rule applies."""

    name = "offline-test-mode"

    def draft(self, ctx: BriefContext) -> str:
        t, p, a, e = ctx.trigger, ctx.preflight, ctx.account, ctx.enrichment
        short = t.title.split(":")[0]
        lines = [f"# {a.name}: {short} brief for the account owner", "",
                 f"Prepared for {ctx.approver}, the account owner, to decide whether to share it in the "
                 "existing relationship. Nothing has been sent and the bank has not been contacted.", "",
                 "## What changed"]
        lines += ["- " + cite(f.text, f.source) for f in t.facts]

        lines += ["", "## What is certain for this account"]
        certain = ["- " + cite(f.text, f.source) for f in p.context]
        if a.hq_country:
            certain.append("- " + cite(f"Our record shows headquarters in {a.hq_country}.", a.system_id))
        lines += certain

        lines += ["", "## What depends on structure (confirm)"]
        in_jurisdiction = a.hq_country == t.jurisdiction
        for c in t.structural_conditions:
            if c["when"] == "always" or (c["when"] == "in_jurisdiction") == in_jurisdiction:
                if t.source(c["source"]) and t.source(c["source"]).verified:
                    lines.append("- " + cite(c["text"].format(account=a.name), c["source"]))
        if CAVEAT in p.caveats and not any(CAVEAT in l for l in lines):
            lines.append("- " + cite(f"Confirm: {short} {CAVEAT}; {'; '.join(p.reasons)}.", t.facts[0].source))
        lines += ["- " + cite(f"Confirm: {c}.", t.facts[0].source, a.system_id) for c in p.caveats if c != CAVEAT]

        lines += ["", "## What we know about the account"]
        if a.runs_forge and any(c["id"] == "P-FORGE" for c in ctx.claims):
            lines.append("- " + cite("Existing Forge customer.", a.system_id, "P-FORGE"))
        if e.agent_adoption in ("production", "planned"):
            lines.append("- " + cite(f"Agents: {e.agent_adoption}.", e.source))
        if e.risk_committee:
            lines.append("- " + cite("Risk committee on record.", e.source))

        lines += ["", "## Where Reign fits"]
        lines += ["- " + cite(c["text"], c["id"]) for c in ctx.claims if c["id"] not in ("P-FORGE", "P-BRIEFING")]

        lines += ["", "## Suggested next step"]
        lines.append("- The account owner offers the audit and risk committee an Executive Assurance Briefing.")
        brief = next((c for c in ctx.claims if c["id"] == "P-BRIEFING"), None)
        if brief:
            lines.append("- " + cite(brief["text"], brief["id"]))

        lines += ["", "## Suggested recipients in the existing relationship"]
        for lane, contacts in ctx.routed.items():
            who = "; ".join(f"{c.name}, {c.title} [{c.system_id}]" for c in contacts) or "no contact on record"
            lines.append(f"- {lane.capitalize()} lane: {who}")

        lines += ["", "## Open questions for the account owner"]
        lines += [f"- {q}" for q in ctx.flags] or ["- None from the record."]
        cited = set(re.findall(r"\[([A-Za-z0-9][A-Za-z0-9:_/.\-]*)\]", "\n".join(lines)))
        lines += ["", "## Sources"] + [f"- [{i}] {d}" for i, d in ctx.sources() if i in cited]
        return "\n".join(lines) + "\n"


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, timeout: float = 120.0):
        self.api_key, self.model, self.timeout = api_key, model, timeout

    def draft(self, ctx: BriefContext) -> str:
        body = {
            "model": self.model,
            "max_tokens": 16000,
            "system": SYSTEM_PROMPT.read_text(encoding="utf-8"),
            "messages": [{"role": "user", "content": json.dumps(ctx.to_json(), indent=2)}],
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"content-type": "application/json", "x-api-key": self.api_key,
                     "anthropic-version": "2023-06-01"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"Anthropic API HTTP {exc.code}: {exc.read()[:300]!r}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderError(f"Anthropic API call failed: {exc}") from exc
        if data.get("stop_reason") == "refusal":
            raise ProviderError(f"model refused: {data.get('stop_details')}")
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        if not text.strip():
            raise ProviderError(f"empty response, stop_reason={data.get('stop_reason')}")
        return text


def get_provider(env: dict | None = None):
    env = os.environ if env is None else env
    key = env.get("ANTHROPIC_API_KEY", "")
    if env.get("WIRE_PROVIDER", "").lower() in ("offline", "template") or not key:  # offline test mode
        return TemplateProvider()
    return AnthropicProvider(key, env.get("WIRE_MODEL", DEFAULT_MODEL))
