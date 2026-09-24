"""Build the reference briefs the evals mutate: the two fixture banks, drafted by the template provider."""

from __future__ import annotations

import json
from pathlib import Path

from agent.input.local import LocalClayEnrichment, LocalHubSpotAccounts, LocalRegulatoryFeed, LocalZoomInfoContacts
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext, TemplateProvider
from agent.processing.routing import route

ROOT = Path(__file__).resolve().parent.parent
LANES = {"risk": ["audit", "risk"], "engineering": ["engineering", "platform"]}


def golden_brief(caveat: bool):
    """caveat=False: the US bank (rule applies). caveat=True: the Canadian bank with the caveat setting."""
    fx = ROOT / "fixtures"
    trigger = LocalRegulatoryFeed(fx / "regulatory_feed.json").get("SR-26-2")
    account_id = "hs-1001" if caveat else "hs-1002"
    account = next(a for a in LocalHubSpotAccounts(fx / "hubspot_companies.json").list_accounts() if a.id == account_id)
    enrichment = LocalClayEnrichment(fx / "clay_enrichment.json").enrich(account_id)
    play = {"channel": "briefing", "unconfirmed_applicability": "brief_with_caveat"}
    result = pf.check(trigger, account, enrichment, play)
    routed, _ = route(LocalZoomInfoContacts(fx / "zoominfo_contacts.json").contacts_for(account_id), LANES,
                      ["information security"], list(LANES))
    claims = [c for c in json.loads((ROOT / "docs/research/product-claims.json").read_text())["claims"]
              if c["id"] in ("P-FORGE", "P-GATEWAY", "P-ASSURANCE", "P-BRIEFING")]
    ctx = BriefContext(trigger, result, account, enrichment, routed, claims, "Kenny Nguyen", [])
    return TemplateProvider().draft(ctx), ctx, pf.CAVEAT in result.caveats
