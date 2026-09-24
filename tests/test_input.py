"""INPUT stage: fixture adapters load, validate, and fail loudly on bad data."""

import json
import unittest
from pathlib import Path

from agent.input.base import InputError
from agent.input.local import (LocalClayEnrichment, LocalHubSpotAccounts, LocalRegulatoryFeed,
                               LocalZoomInfoContacts)
from tests.helpers import tempdir

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "fixtures"


class InputTests(unittest.TestCase):
    def test_accounts_load_and_are_fictional(self):
        accounts = LocalHubSpotAccounts(FIX / "hubspot_companies.json").list_accounts()
        self.assertGreaterEqual(len(accounts), 10)
        for a in accounts:
            self.assertTrue(a.name.endswith("(fictional)"), a.name)
            self.assertEqual(a.system_id, f"hubspot:company/{a.id}")

    def test_contacts_filtered_by_account(self):
        contacts = LocalZoomInfoContacts(FIX / "zoominfo_contacts.json").contacts_for("hs-1001")
        self.assertEqual(len(contacts), 5)
        self.assertTrue(all(c.account_id == "hs-1001" for c in contacts))

    def test_missing_enrichment_is_unknown_not_error(self):
        e = LocalClayEnrichment(FIX / "clay_enrichment.json").enrich("hs-9999")
        self.assertIsNone(e.agent_adoption)
        self.assertIsNone(e.risk_committee)

    def test_sr26_2_trigger_has_verified_sources(self):
        t = LocalRegulatoryFeed(FIX / "regulatory_feed.json").get("SR-26-2")
        self.assertTrue(t.implemented)
        self.assertTrue(t.facts)
        self.assertTrue(all(s.verified and s.url for s in t.sources + t.context_sources))
        self.assertIn("CA", t.context_by_jurisdiction)

    def test_unimplemented_triggers_carry_a_reason(self):
        feed = LocalRegulatoryFeed(FIX / "regulatory_feed.json")
        for tid in ("FDA-PCCP-2025", "DEFENSE-TBD"):
            t = feed.get(tid)
            self.assertFalse(t.implemented)
            self.assertTrue(t.not_implemented_reason)

    def test_unknown_trigger_raises(self):
        with self.assertRaises(InputError):
            LocalRegulatoryFeed(FIX / "regulatory_feed.json").get("NOPE")

    def test_fact_citing_unknown_source_raises(self):
        with tempdir() as d:
            p = Path(d) / "feed.json"
            p.write_text(json.dumps({"triggers": [{"id": "T", "type": "regulatory", "implemented": True,
                                                   "title": "t", "facts": [{"text": "x", "source": "ghost"}],
                                                   "sources": []}]}))
            with self.assertRaises(InputError):
                LocalRegulatoryFeed(p).get("T")

    def test_corrupt_file_raises_input_error(self):
        with tempdir() as d:
            p = Path(d) / "bad.json"
            p.write_text("{not json")
            with self.assertRaises(InputError):
                LocalHubSpotAccounts(p).list_accounts()


if __name__ == "__main__":
    unittest.main()
