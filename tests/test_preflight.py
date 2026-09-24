"""Applicability preflight (SR 26-2 rules) and title routing."""

import unittest
from dataclasses import replace
from pathlib import Path

from agent.input.local import LocalRegulatoryFeed
from agent.input.models import Account, Contact, Enrichment, Source
from agent.processing import preflight as pf
from agent.processing.routing import route

ROOT = Path(__file__).resolve().parent.parent
FEED = LocalRegulatoryFeed(ROOT / "fixtures/regulatory_feed.json")
SR = FEED.get("SR-26-2")
CA_BANK = Account("b", "Example Bank (fictional)", "dsib_capital_markets", "Banking", "", 38000, "CA",
                  900_000_000_000, True, False, "hubspot")
US_BANK = replace(CA_BANK, hq_country="US", total_assets_usd=85_000_000_000)
UNKNOWN = Enrichment("b", "production", True, None, None, "clay:row/b")
PLAY = {"channel": "briefing", "unconfirmed_applicability": "hold"}


class PreflightTests(unittest.TestCase):
    def test_us_bank_over_threshold_applies(self):
        r = pf.check(SR, US_BANK, UNKNOWN, PLAY)
        self.assertEqual((r.status, r.applicability, r.caveats), (pf.READY, pf.APPLIES, []))

    def test_us_bank_under_threshold_gets_relevance_caveat(self):
        r = pf.check(SR, replace(US_BANK, total_assets_usd=10_000_000_000), UNKNOWN, PLAY)
        self.assertEqual(r.status, pf.READY)
        self.assertTrue(any("below the threshold" in c for c in r.caveats))

    def test_canadian_bank_unknown_us_entity_held_by_default(self):
        r = pf.check(SR, CA_BANK, UNKNOWN, PLAY)
        self.assertEqual((r.status, r.applicability), (pf.HOLD, pf.REQUIRES_CONFIRMATION))

    def test_canadian_bank_with_structured_brief_gets_caveat_and_osfi_context(self):
        r = pf.check(SR, CA_BANK, UNKNOWN, {**PLAY, "unconfirmed_applicability": "structured_brief"})
        self.assertEqual(r.status, pf.READY)
        self.assertIn(pf.CAVEAT, r.caveats)
        self.assertTrue(any("E-23" in f.text for f in r.context))

    def test_canadian_bank_with_us_entity_applies(self):
        r = pf.check(SR, CA_BANK, replace(UNKNOWN, us_fed_regulated_entity=True), PLAY)
        self.assertEqual((r.status, r.applicability), (pf.READY, pf.APPLIES))

    def test_canadian_bank_without_us_entity_skipped(self):
        r = pf.check(SR, CA_BANK, replace(UNKNOWN, us_fed_regulated_entity=False), PLAY)
        self.assertEqual(r.status, pf.SKIP)

    def test_unimplemented_trigger_blocked(self):
        r = pf.check(FEED.get("FDA-PCCP-2025"), US_BANK, UNKNOWN, PLAY)
        self.assertEqual(r.status, pf.BLOCKED)
        self.assertIn("not implemented", r.reasons[0])

    def test_unverified_source_blocked(self):
        bad = replace(SR, sources=(Source("src-sr26-2", "x", None, False),))
        self.assertEqual(pf.check(bad, US_BANK, UNKNOWN, PLAY).status, pf.BLOCKED)

    def test_no_cold_outreach_until_briefing_booked(self):  # A-043
        play = {"channel": "sequence", "handoff": {"cold_outreach_until_briefing_booked": False}}
        self.assertEqual(pf.check(SR, US_BANK, UNKNOWN, play).status, pf.BLOCKED)
        self.assertEqual(pf.check(SR, replace(US_BANK, briefing_scheduled=True), UNKNOWN, play).status, pf.READY)

    def test_brief_needs_a_named_account_owner(self):  # A-043
        play = {**PLAY, "handoff": {"route_to": "account_owner"}}
        self.assertEqual(pf.check(SR, US_BANK, UNKNOWN, play).status, pf.HOLD)
        self.assertEqual(pf.check(SR, replace(US_BANK, owner="Kenny Nguyen"), UNKNOWN, play).status, pf.READY)


class RoutingTests(unittest.TestCase):
    def test_risk_and_engineering_lanes_and_do_not_route(self):
        contacts = [Contact(str(i), "b", f"P{i} (fictional)", t, "zoominfo") for i, t in enumerate([
            "Chief Audit Executive", "Chief Risk Officer", "VP, Platform Engineering",
            "Chief Information Security Officer", "Office Manager"])]
        routed, skipped = route(contacts, {"risk": ["audit", "risk"], "engineering": ["engineering", "platform"]},
                                ["information security"], ["risk", "engineering"])
        self.assertEqual([c.title for c in routed["risk"]], ["Chief Audit Executive", "Chief Risk Officer"])
        self.assertEqual([c.title for c in routed["engineering"]], ["VP, Platform Engineering"])
        self.assertEqual(len(skipped), 2)


if __name__ == "__main__":
    unittest.main()
