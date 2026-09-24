"""ICP filter: exclusions (including AI-startup naming variants), floor, holds, flags."""

import unittest
from dataclasses import replace
from pathlib import Path

from agent.input.local import LocalClayEnrichment, LocalHubSpotAccounts
from agent.input.models import Account, Enrichment
from agent.processing.icp import EXCLUDE, HOLD, INCLUDE, WATCH, Icp

ROOT = Path(__file__).resolve().parent.parent
ICP = Icp.load(ROOT / "icp" / "icp.json")

BANK = Account(id="x", name="Example Bank (fictional)", segment="dsib_capital_markets", industry="Banking",
               description="Large bank.", employees=20000, hq_country="CA", total_assets_usd=None,
               runs_forge=True, briefing_scheduled=False, system="hubspot")
ENRICHED = Enrichment("x", "production", True, None, None, "clay:row/x")

AI_STARTUP_VARIANTS = [
    "AI startup", "AI start-up", "AI start up", "A.I. startup", "AI-native startup", "AI native SaaS",
    "AI-first startup", "AI-powered startup", "GenAI startup", "Gen-AI start-up", "Gen AI startups",
    "Generative AI startup", "LLM startup", "LLM-based start-up", "GPT startup",
    "startup building AI agents", "start-up shipping LLM copilots", "Series B copilot company",
    "Series B AI platform", "seed-stage AI tooling", "YC-backed agents platform", "copilot startup",
    "AI-first company", "mid-market SaaS", "Mid market SaaS vendor", "SMB SaaS",
    # Found by independent QA, missed by the first pattern set:
    "Machine learning startup, founded 2023.", "Venture-backed AI company, 40 employees, founded 2024.",
    "Early-stage agentic AI company.", "Generative-AI scale-up selling copilots to banks.",
    "Mid-market B2B SaaS platform for finance teams.", "SaaS for mid-sized companies.",
    "Software-as-a-service vendor for the mid-market.", "Midsize SaaS company.",
    "Artificial intelligence start-up.",
    # Found by independent QA pass 2:
    "Fintech startup using large language models.", "YC W24 company building LLM agents.",
    "Venture-funded autonomous agent company.", "Deep-learning startup.", "Seed-funded foundation model lab.",
    "Cloud software vendor for mid-sized manufacturers.", "B2B subscription software for midmarket lenders.",
    # Adjectives about the company itself (review F2):
    "Well-funded AI startup building copilots for banks.", "VC-funded AI startup.",
    "Backed by a16z, Acme is an AI startup.", "Insurtech AI startup.", "Customer-obsessed GenAI startup.",
]

# Descriptions of companies that use AI or deal with AI startups; free text never excludes (A-050).
MUST_NOT_EXCLUDE = [
    "Bank with AI models in production.", "Runs an AI governance programme across capital markets.",
    "Started a model risk programme for AI in 2025.", "Uses generative AI for document review.",
    "US bank holding company; its venture arm invests in AI startups.",
    "Bank that partners with fintech startups and is piloting AI agents in lending.",
    "Large bank with a venture arm backing AI startups.", "Large bank funding AI startups across Canada.",
    "Large bank financing AI startups.", "Large insurer insuring AI startups.", "Bank with a fund for AI startups.",
]


class IcpTests(unittest.TestCase):
    def test_in_icp_bank_included(self):
        d = ICP.evaluate(BANK, ENRICHED)
        self.assertEqual(d.decision, INCLUDE, d.reasons)
        self.assertTrue(d.fs)

    def test_ai_startup_category_variants_excluded(self):
        for text in AI_STARTUP_VARIANTS:
            with self.subTest(text=text):
                acct = replace(BANK, segment="fintech", industry=text, description="Lending software.")
                d = ICP.evaluate(acct, ENRICHED)
                self.assertEqual(d.decision, EXCLUDE, f"{text!r} -> {d.decision} {d.reasons}")

    def test_free_text_never_excludes(self):  # A-050: only the category says what a company is
        for text in AI_STARTUP_VARIANTS + MUST_NOT_EXCLUDE:
            with self.subTest(text=text):
                d = ICP.evaluate(replace(BANK, name=f"{text} (fictional)", description=text), ENRICHED)
                self.assertEqual(d.decision, INCLUDE, f"{text!r} wrongly -> {d.reasons}")

    def test_unclear_category_is_held_and_flagged(self):  # A-050
        d = ICP.evaluate(replace(BANK, segment="fintech", industry="Financial Services",
                                 description="Gen-AI start-up building LLM agents for lenders."), ENRICHED)
        self.assertEqual(d.decision, HOLD)
        self.assertTrue(any("a human confirms the company category" in f for f in d.flags), d.flags)
        d = ICP.evaluate(replace(BANK, segment="fintech", industry="Financial Services", description="Lender."), ENRICHED)
        self.assertEqual((d.decision, d.flags), (HOLD, []))

    def test_excluded_segment_labels(self):
        for seg in ("ai_native_saas", "ai_startup", "mid_market_saas"):
            with self.subTest(seg=seg):
                self.assertEqual(ICP.evaluate(replace(BANK, segment=seg, description="x"), ENRICHED).decision, EXCLUDE)

    def test_hospitals_are_watched_not_contacted(self):  # A-040
        self.assertEqual(ICP.evaluate(replace(BANK, segment="hospital", description="x"), ENRICHED).decision, WATCH)

    def test_headcount_floor_and_unknown(self):
        self.assertEqual(ICP.evaluate(replace(BANK, employees=4999), ENRICHED).decision, EXCLUDE)
        self.assertEqual(ICP.evaluate(replace(BANK, employees=5000), ENRICHED).decision, INCLUDE)
        self.assertEqual(ICP.evaluate(replace(BANK, employees=None), ENRICHED).decision, HOLD)

    def test_unlisted_segment_held(self):
        self.assertEqual(ICP.evaluate(replace(BANK, segment="retail"), ENRICHED).decision, HOLD)

    def test_semiconductor_needs_export_control_exposure(self):
        semi = replace(BANK, segment="semiconductor", industry="Semiconductors", description="Foundry.")
        self.assertEqual(ICP.evaluate(semi, replace(ENRICHED, export_control_exposure=True)).decision, INCLUDE)
        self.assertEqual(ICP.evaluate(semi, replace(ENRICHED, export_control_exposure=None)).decision, WATCH)  # A-039

    def test_agent_adoption_never_excludes(self):  # A-036, operator decision
        d = ICP.evaluate(BANK, replace(ENRICHED, agent_adoption="none"))
        self.assertEqual(d.decision, INCLUDE)
        self.assertTrue(any("no agents" in f for f in d.flags))
        d = ICP.evaluate(BANK, replace(ENRICHED, agent_adoption=None, risk_committee=None))
        self.assertEqual(d.decision, INCLUDE)
        self.assertEqual(len(d.flags), 2)
        d = ICP.evaluate(replace(BANK, industry=None), ENRICHED)
        self.assertTrue(d.fs and any("industry unconfirmed" in f for f in d.flags))  # A-006

    def test_unknown_industry_counts_as_fs(self):
        acct = replace(BANK, segment="biopharma_quality", industry=None)
        self.assertTrue(ICP.is_fs(acct))
        self.assertFalse(ICP.is_fs(replace(acct, industry="Pharmaceuticals")))

    def test_fixture_outcomes(self):
        accounts = {a.id: a for a in LocalHubSpotAccounts(ROOT / "fixtures/hubspot_companies.json").list_accounts()}
        clay = LocalClayEnrichment(ROOT / "fixtures/clay_enrichment.json")
        got = {aid: ICP.evaluate(a, clay.enrich(aid)).decision for aid, a in accounts.items()}
        self.assertEqual(got, {
            "hs-1001": INCLUDE, "hs-1002": INCLUDE, "hs-1003": INCLUDE, "hs-1004": INCLUDE,
            "hs-1005": EXCLUDE, "hs-1006": HOLD, "hs-1007": WATCH, "hs-1008": WATCH,
            "hs-1009": HOLD, "hs-1010": EXCLUDE, "hs-1011": HOLD,
        })


if __name__ == "__main__":
    unittest.main()
