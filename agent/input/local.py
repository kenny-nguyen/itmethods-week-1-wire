"""Local fixture adapters standing in for HubSpot, ZoomInfo, Clay and a regulator feed."""

from __future__ import annotations

import json
from pathlib import Path

from agent.input.base import InputError
from agent.input.models import Account, Contact, Enrichment, Fact, Source, Trigger


def _load(path: Path, key: str) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    rows = data.get(key)
    if not isinstance(rows, list):
        raise InputError(f"{path} has no '{key}' list")
    return rows


def _require(row: dict, fields: tuple[str, ...], where: str) -> None:
    missing = [f for f in fields if f not in row]
    if missing:
        raise InputError(f"{where}: missing fields {missing}")


class LocalHubSpotAccounts:
    """Stands in for HubSpot companies."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def list_accounts(self) -> list[Account]:
        accounts = []
        for row in _load(self.path, "companies"):
            _require(row, ("id", "name", "segment"), f"{self.path.name} row {row.get('id')}")
            accounts.append(Account(
                id=row["id"], name=row["name"], segment=row["segment"], industry=row.get("industry"),
                description=row.get("description", ""), employees=row.get("employees"),
                hq_country=row.get("hq_country"), total_assets_usd=row.get("total_assets_usd"),
                runs_forge=row.get("runs_forge"), briefing_scheduled=bool(row.get("briefing_scheduled")),
                system="hubspot",
            ))
        return accounts


class LocalZoomInfoContacts:
    """Stands in for ZoomInfo contact search."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def contacts_for(self, account_id: str) -> list[Contact]:
        out = []
        for row in _load(self.path, "contacts"):
            _require(row, ("id", "company_id", "name", "title"), f"{self.path.name} row {row.get('id')}")
            if row["company_id"] == account_id:
                out.append(Contact(row["id"], row["company_id"], row["name"], row["title"], system="zoominfo"))
        return out


class LocalClayEnrichment:
    """Stands in for a Clay enrichment table. Missing rows mean 'no data', not an error."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def enrich(self, account_id: str) -> Enrichment:
        for row in _load(self.path, "rows"):
            if row.get("company_id") == account_id:
                return Enrichment(
                    account_id=account_id, agent_adoption=row.get("agent_adoption"),
                    risk_committee=row.get("risk_committee"),
                    export_control_exposure=row.get("export_control_exposure"),
                    us_fed_regulated_entity=row.get("us_fed_regulated_entity"),
                    source=row.get("source") or f"clay:row/{account_id}",
                )
        return Enrichment.empty(account_id)


def _sources(rows: list[dict]) -> tuple[Source, ...]:
    return tuple(Source(r["id"], r.get("title", r["id"]), r.get("url"), bool(r.get("verified"))) for r in rows)


def _facts(rows: list[dict]) -> tuple[Fact, ...]:
    return tuple(Fact(r["text"], r["source"]) for r in rows)


class LocalRegulatoryFeed:
    """Stands in for a regulator publication feed."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def get(self, trigger_id: str) -> Trigger:
        for row in _load(self.path, "triggers"):
            if row.get("id") != trigger_id:
                continue
            _require(row, ("id", "type", "implemented", "title"), f"trigger {trigger_id}")
            trigger = Trigger(
                id=row["id"], type=row["type"], implemented=bool(row["implemented"]), title=row["title"],
                issuer=row.get("issuer"), published=row.get("published"), jurisdiction=row.get("jurisdiction"),
                facts=_facts(row.get("facts", [])), sources=_sources(row.get("sources", [])),
                not_implemented_reason=row.get("not_implemented_reason"), regulator=row.get("regulator"),
                relevance_threshold_total_assets_usd=row.get("relevance_threshold_total_assets_usd"),
                context_by_jurisdiction={k: _facts(v) for k, v in row.get("context_by_jurisdiction", {}).items()},
                context_sources=_sources(row.get("context_sources", [])),
            )
            for fact in trigger.facts + tuple(f for fs in trigger.context_by_jurisdiction.values() for f in fs):
                if trigger.source(fact.source) is None:
                    raise InputError(f"trigger {trigger_id}: fact cites unknown source {fact.source!r}")
            return trigger
        raise InputError(f"trigger {trigger_id!r} not found in {self.path}")
