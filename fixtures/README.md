# Fixtures

Local stand-ins for the tools this motion runs on, used because there was no HubSpot, Clay or ZoomInfo access in the window (register row A-012, proposed). Each file is read by one input adapter in `agent/input/local.py`; swapping in the real tool means writing one class against the same interface in `agent/input/base.py`.

Every company and person in these files is fictional (register row A-013, proposed). Names end in "(fictional)" so no output can be mistaken for a claim about a real organisation. The one exception is `regulatory_feed.json`, which holds real regulator publications with their fetched URLs.

| File | Stands in for | Read by |
|---|---|---|
| `hubspot_companies.json` | HubSpot companies (system of record) | `LocalHubSpotAccounts` |
| `zoominfo_contacts.json` | ZoomInfo contact search | `LocalZoomInfoContacts` |
| `clay_enrichment.json` | Clay enrichment table | `LocalClayEnrichment` |
| `regulatory_feed.json` | A regulator publication feed | `LocalRegulatoryFeed` |
