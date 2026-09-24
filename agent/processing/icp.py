"""Deterministic ICP (ideal customer profile) filter.

Pure function: account and enrichment in, decision out. The pipeline records
the decision as an R-17 "score" action; this module never writes anything.

The rules come from `icp/icp.json`, where every field the packet did not give
names the register row that proposes it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from agent.input.models import Account, Enrichment

INCLUDE, EXCLUDE, HOLD, WATCH = "include", "exclude", "hold", "watch"  # watch: noticed and logged, never contacted


@dataclass
class IcpDecision:
    decision: str
    fs: bool
    reasons: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    segment: dict = field(default_factory=dict)


@dataclass
class Icp:
    raw: dict
    patterns: list[tuple[str, re.Pattern]]
    object_context: re.Pattern

    @classmethod
    def load(cls, path: str | Path) -> "Icp":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        patterns = [(p["id"], re.compile(p["regex"], re.IGNORECASE)) for p in raw["exclusion_patterns"]]
        return cls(raw, patterns, re.compile(raw["object_context_regex"], re.IGNORECASE))

    def is_fs(self, account: Account) -> bool:
        seg = self.raw["segments"].get(account.segment, {})
        if seg.get("fs"):
            return True
        if account.industry is None:  # unknown counts as FS so R-17 cannot be skipped by missing data (A-006)
            return True
        return account.industry.strip().lower() in self.raw["fs_industries"]

    def matched_exclusion(self, account: Account) -> str | None:
        """First exclusion pattern that describes the account itself.

        A match is ignored when the startups are someone the account deals with
        ("invests in AI startups", "partners with fintech startups"): the
        `object_context` pattern, which needs a relational phrase rather than an
        adjective such as "well-funded", is checked on the words just before the match.
        """
        text = " . ".join(filter(None, [account.name, account.description, account.segment.replace("_", " "),
                                        account.industry or ""]))
        for pid, pattern in self.patterns:
            for m in pattern.finditer(text):
                before = text[max(0, m.start() - 40):m.start()]
                if not self.object_context.search(before):
                    return pid
        return None

    def prescreen(self, account: Account) -> IcpDecision | None:
        """Decide what can be decided without enrichment, so excluded companies are never enriched."""
        fs = self.is_fs(account)
        seg = self.raw["segments"].get(account.segment)

        hit = self.matched_exclusion(account)
        if hit:
            return IcpDecision(EXCLUDE, fs, [f"matches exclusion pattern '{hit}' (AI startups and mid-market SaaS are out, A-003)"])
        if seg is not None and seg.get("watch"):
            return IcpDecision(WATCH, fs, [f"segment '{account.segment}' is on the watch list: {seg.get('reason', '')}".strip()])
        if seg is not None and not seg.get("include", False):
            return IcpDecision(EXCLUDE, fs, [f"segment '{account.segment}' is excluded: {seg.get('reason', '')}".strip()])
        if seg is None:
            decision = HOLD if self.raw["unlisted_segment"] == "hold" else EXCLUDE
            return IcpDecision(decision, fs, [f"segment '{account.segment}' is not in the ICP (A-031)"])

        if account.employees is None:
            if self.raw["unknown_employees"] == "hold":
                return IcpDecision(HOLD, fs, ["headcount unknown; the ICP floor is 5,000 employees (A-004)"], segment=seg)
        elif account.employees < self.raw["min_employees"]:
            return IcpDecision(EXCLUDE, fs, [f"{account.employees} employees is under the {self.raw['min_employees']} floor"], segment=seg)
        return None

    def evaluate(self, account: Account, enrichment: Enrichment) -> IcpDecision:
        early = self.prescreen(account)
        if early is not None:
            return early
        fs = self.is_fs(account)
        seg = self.raw["segments"][account.segment]

        for key, required in seg.get("requires", {}).items():
            actual = getattr(enrichment, key, None)
            if actual != required:
                decision = WATCH if seg.get("otherwise") == "watch" else EXCLUDE
                return IcpDecision(decision, fs, [f"segment target needs {key}={required}, enrichment has {actual}; "
                                                  f"{'on the watch list, no outreach' if decision == WATCH else 'excluded'} (A-039)"],
                                   segment=seg)

        flags = []
        if account.industry is None:  # counted as FS so the audit is always written (A-006, operator decision)
            flags.append("industry unconfirmed: treated as financial services until a human confirms (A-006)")
        adoption = enrichment.agent_adoption  # a signal only, never a reason to exclude (A-036, operator decision)
        if adoption is None:
            flags.append("agent adoption unknown: confirm whether agents are in production or planned (A-036)")
        elif adoption == "none":
            flags.append("enrichment says no agents in production or planned: confirm before the briefing (A-036)")
        if enrichment.risk_committee is not True:
            flags.append("no risk committee on record: the briefing may not land (A-021, unvetted)")

        return IcpDecision(INCLUDE, fs, [f"segment '{account.segment}' in ICP"], flags, segment=seg)
