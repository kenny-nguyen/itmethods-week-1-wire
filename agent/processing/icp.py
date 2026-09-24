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

INCLUDE, EXCLUDE, HOLD = "include", "exclude", "hold"


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

    @classmethod
    def load(cls, path: str | Path) -> "Icp":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        patterns = [(p["id"], re.compile(p["regex"], re.IGNORECASE)) for p in raw["exclusion_patterns"]]
        return cls(raw, patterns)

    def is_fs(self, account: Account) -> bool:
        seg = self.raw["segments"].get(account.segment, {})
        if seg.get("fs"):
            return True
        if account.industry is None:  # unknown counts as FS so R-17 cannot be skipped by missing data (A-006)
            return True
        return account.industry.strip().lower() in self.raw["fs_industries"]

    def matched_exclusion(self, account: Account) -> str | None:
        text = " . ".join(filter(None, [account.name, account.description, account.segment.replace("_", " "),
                                        account.industry or ""]))
        for pid, pattern in self.patterns:
            if pattern.search(text):
                return pid
        return None

    def prescreen(self, account: Account) -> IcpDecision | None:
        """Decide what can be decided without enrichment, so excluded companies are never enriched."""
        fs = self.is_fs(account)
        seg = self.raw["segments"].get(account.segment)

        hit = self.matched_exclusion(account)
        if hit:
            return IcpDecision(EXCLUDE, fs, [f"matches exclusion pattern '{hit}' (AI startups and mid-market SaaS are out, A-003)"])
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
                return IcpDecision(EXCLUDE, fs, [f"segment requires {key}={required}, enrichment has {actual} (A-019)"], segment=seg)

        flags = []
        adoption = enrichment.agent_adoption
        if adoption in self.raw["agent_adoption"]["exclude_values"]:
            return IcpDecision(EXCLUDE, fs, [f"enrichment says agent adoption is '{adoption}' (A-005)"], segment=seg)
        if adoption is None:
            flags.append("agent adoption unknown: confirm agents are in production or planned (A-005)")
        if enrichment.risk_committee is not True:
            flags.append("no risk committee on record: the briefing may not land (A-021, unvetted)")

        return IcpDecision(INCLUDE, fs, [f"segment '{account.segment}' in ICP"], flags, segment=seg)
