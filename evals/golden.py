"""Build the reference briefs the evals mutate: the two fixture banks, drafted by the template provider."""

from __future__ import annotations

import json
from pathlib import Path

from agent.input.local import LocalClayEnrichment, LocalHubSpotAccounts, LocalRegulatoryFeed, LocalZoomInfoContacts
from agent.input.playbook import load
from agent.processing import preflight as pf
from agent.processing.brief import BriefContext, TemplateProvider
from agent.processing.routing import route

ROOT = Path(__file__).resolve().parent.parent


def golden_brief(caveat: bool):
    """caveat=False: the US bank. caveat=True: the Canadian bank, whose brief must say applicability requires confirmation."""
    fx = ROOT / "fixtures"
    trigger = LocalRegulatoryFeed(fx / "regulatory_feed.json").get("SR-26-2")
    account_id = "hs-1001" if caveat else "hs-1002"
    account = next(a for a in LocalHubSpotAccounts(fx / "hubspot_companies.json").list_accounts() if a.id == account_id)
    enrichment = LocalClayEnrichment(fx / "clay_enrichment.json").enrich(account_id)
    play = load(ROOT / "playbooks/bank-sr26-2.jsonc")
    result = pf.check(trigger, account, enrichment, play)
    lanes = play["routing"]["lanes"]
    routed, _ = route(LocalZoomInfoContacts(fx / "zoominfo_contacts.json").contacts_for(account_id), lanes,
                      play["routing"]["do_not_route"], list(lanes))
    claims = [c for c in json.loads((ROOT / "docs/research/product-claims.json").read_text())["claims"]
              if c["id"] in play["claims"]]
    ctx = BriefContext(trigger, result, account, enrichment, routed, claims, account.owner, [])
    return TemplateProvider().draft(ctx), ctx, pf.CAVEAT in result.caveats
