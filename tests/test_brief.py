"""Brief generation and the output gate: the template passes, every eval case is caught, provider selection."""

import unittest

from agent.processing.brief import AnthropicProvider, TemplateProvider, get_provider
from agent.processing.checks import check_brief
from evals.golden import golden_brief
from evals.run_evals import run


class BriefTests(unittest.TestCase):
    def test_template_briefs_pass_the_gate(self):
        for caveat in (False, True):
            with self.subTest(caveat=caveat):
                text, ctx, needs = golden_brief(caveat)
                self.assertEqual(needs, caveat)
                self.assertEqual(check_brief(text, allowed_ids=ctx.allowed_ids(), allowed_urls=ctx.allowed_urls(),
                                             claim_texts=ctx.claim_texts(), caveat_required=needs), [])

    def test_canadian_brief_carries_caveat_and_osfi_context(self):
        text, _, _ = golden_brief(caveat=True)
        self.assertIn("so applicability requires confirmation", text)
        self.assertIn("E-23", text)
        self.assertIn("Nothing has been sent and the bank has not been contacted.", text)
        order = [text.index(h) for h in ("## What changed", "## What is certain for this account",
                                         "## What depends on structure (confirm)", "## Suggested next step")]
        self.assertEqual(order, sorted(order), "A-044 structure")

    def test_every_eval_case_behaves(self):
        results = run()
        self.assertGreaterEqual(len(results), 42)
        misses = [(n, p) for n, ok, p in results if not ok]
        self.assertEqual(misses, [])

    def test_provider_selection(self):
        self.assertIsInstance(get_provider({}), TemplateProvider)
        self.assertIsInstance(get_provider({"ANTHROPIC_API_KEY": "k", "WIRE_PROVIDER": "template"}), TemplateProvider)
        p = get_provider({"ANTHROPIC_API_KEY": "k", "WIRE_MODEL": "claude-opus-5"})
        self.assertIsInstance(p, AnthropicProvider)
        self.assertEqual(p.model, "claude-opus-5")


if __name__ == "__main__":
    unittest.main()
