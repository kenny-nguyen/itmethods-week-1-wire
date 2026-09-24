# Day-one wiring

We had no HubSpot, Clay or ZoomInfo access in the window, so each is a local fixture behind an interface. This is what we would wire on day one. Moved from the README.

Each tool replaces one fixture class. The pipeline and the MCP tools only talk to these interfaces (`agent/input/base.py`, `agent/governance/audit.py`).

| Tool | Job | Interface to implement |
|---|---|---|
| HubSpot | Accounts, including the named account owner | `AccountSource.list_accounts() -> list[Account]` |
| HubSpot (or the Reign audit store) | R-17 audit records as timeline events | `AuditSink.append(record: dict) -> None`, durable before returning, raises on failure |
| Clay | Enrichment columns: agent adoption, risk committee, export-control exposure, US Federal Reserve entity | `EnrichmentSource.enrich(account_id) -> Enrichment` |
| ZoomInfo | Contact search by the playbook's lane title keywords | `ContactSource.contacts_for(account_id) -> list[Contact]` |
| Regulator feeds | Trigger records with verified sources | `TriggerSource.get(trigger_id) -> Trigger`, `implemented_ids()` |
| Send path | Share an approved brief | Not built. Spec in [`docs/production.md`](production.md) section 5. |
