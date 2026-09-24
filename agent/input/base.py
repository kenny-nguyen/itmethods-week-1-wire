"""Adapter interfaces for the INPUT stage.

The pipeline only talks to these interfaces. Local fixture implementations
live in `local.py`; a live implementation for each tool is one class against
the same interface (register row A-012, proposed).

Day-one wiring, when access exists:
- AccountSource   -> HubSpot, the system of record (companies object).
- ContactSource   -> ZoomInfo contact search, filtered by company.
- EnrichmentSource -> a Clay table keyed by HubSpot company id.
- TriggerSource   -> regulator publication feeds (for SR letters, the Federal
  Reserve's SR letter listing), reviewed by a human before a trigger is marked
  implemented.
"""

from __future__ import annotations

from typing import Protocol

from agent.input.models import Account, Contact, Enrichment, Trigger


class TriggerSource(Protocol):
    def get(self, trigger_id: str) -> Trigger: ...


class AccountSource(Protocol):
    def list_accounts(self) -> list[Account]: ...


class ContactSource(Protocol):
    def contacts_for(self, account_id: str) -> list[Contact]: ...


class EnrichmentSource(Protocol):
    def enrich(self, account_id: str) -> Enrichment: ...


class InputError(Exception):
    """An adapter could not produce a valid record."""
