"""Records passed between stages. Plain dataclasses, built from adapter output."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str | None
    verified: bool


@dataclass(frozen=True)
class Fact:
    text: str
    source: str  # Source.id


@dataclass(frozen=True)
class Trigger:
    id: str
    type: str
    implemented: bool
    title: str
    issuer: str | None
    published: str | None
    jurisdiction: str | None
    facts: tuple[Fact, ...]
    sources: tuple[Source, ...]
    not_implemented_reason: str | None = None
    regulator: str | None = None
    relevance_threshold_total_assets_usd: int | None = None
    context_by_jurisdiction: dict = field(default_factory=dict)  # jurisdiction -> tuple[Fact, ...]
    context_sources: tuple[Source, ...] = ()
    structural_conditions: tuple[dict, ...] = ()  # {"when", "text", "source"}: lines marked "Confirm" (A-044)

    def source(self, source_id: str) -> Source | None:
        return next((s for s in self.sources + self.context_sources if s.id == source_id), None)


@dataclass(frozen=True)
class Account:
    id: str
    name: str
    segment: str
    industry: str | None
    description: str
    employees: int | None
    hq_country: str | None
    total_assets_usd: int | None
    runs_forge: bool | None
    briefing_scheduled: bool
    system: str  # where the record came from, e.g. "hubspot"
    owner: str | None = None  # the named iTmethods account owner (A-043)

    @property
    def system_id(self) -> str:
        return f"{self.system}:company/{self.id}"


@dataclass(frozen=True)
class Contact:
    id: str
    account_id: str
    name: str
    title: str
    system: str

    @property
    def system_id(self) -> str:
        return f"{self.system}:contact/{self.id}"


@dataclass(frozen=True)
class Enrichment:
    account_id: str
    agent_adoption: str | None  # "production" | "planned" | "none" | None (unknown)
    risk_committee: bool | None
    export_control_exposure: bool | None
    us_fed_regulated_entity: bool | None
    source: str

    @classmethod
    def empty(cls, account_id: str) -> "Enrichment":
        return cls(account_id, None, None, None, None, source="")
