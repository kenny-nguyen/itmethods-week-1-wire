"""One regression test per probe in docs/qa/adversarial-report.md (F1 to F3; F4 is covered by evals/brief_cases.json)."""

import json
import unittest
from dataclasses import replace
from pathlib import Path

from agent.processing.routing import route
from agent.input.models import Contact
from agent.run_playbook import _load_inputs
from agent.tools import GovernedTools, ToolFailure
from tests.helpers import tempdir
from tests.test_tools import offline_draft

ROOT = Path(__file__).resolve().parent.parent
BANK = "bank-sr26-2"


def blocked_ciso_playbooks(tmp: Path) -> Path:
    """A copy of playbooks/ whose bank playbook blocks the CISO, so the excluded-contact rules can be tested."""
    import shutil, re as _re
    dst = tmp / "playbooks"
    shutil.copytree(ROOT / "playbooks", dst)
    f = dst / "bank-sr26-2.jsonc"
    f.write_text(_re.sub(r'"do_not_route": \[\]', '"do_not_route": ["information security", "ciso"]', f.read_text()))
    return dst


class OrderedSink:
    def __init__(self, events):
        self.events = events

    def append(self, record):
        self.events.append(("audit", record["action"]))


class RecordingEnrichment:
    def __init__(self, inner, events):
        self.inner, self.events = inner, events

    def enrich(self, account_id):
        self.events.append(("adapter", "enrich"))
        return self.inner.enrich(account_id)


class F1AuditBeforeEnrichment(unittest.TestCase):
    def test_audit_record_precedes_enrichment_call(self):
        events: list = []
        io = _load_inputs(ROOT)
        io = {**io, "enrichment": RecordingEnrichment(io["enrichment"], events)}
        with tempdir() as d:
            GovernedTools(Path(d), inputs=io, sink=OrderedSink(events)).screen_account(BANK, "hs-1001")
        self.assertEqual(events[:2], [("audit", "enrich"), ("adapter", "enrich")])

    def test_failed_audit_means_no_enrichment_call(self):
        events: list = []
        io = _load_inputs(ROOT)
        io = {**io, "enrichment": RecordingEnrichment(io["enrichment"], events)}

        class Failing:
            def append(self, record):
                raise OSError("audit store down")

        with tempdir() as d, self.assertRaises(ToolFailure):
            GovernedTools(Path(d), inputs=io, sink=Failing()).screen_account(BANK, "hs-1001")
        self.assertNotIn(("adapter", "enrich"), events)


class RecordingContacts:
    def __init__(self, inner, events):
        self.inner, self.events = inner, events

    def contacts_for(self, account_id):
        self.events.append(("adapter", "contacts"))
        return self.inner.contacts_for(account_id)


class F7AuditBeforeContacts(unittest.TestCase):
    def test_route_record_precedes_contacts_call(self):
        events: list = []
        io = _load_inputs(ROOT)
        io = {**io, "contacts": RecordingContacts(io["contacts"], events)}
        with tempdir() as d:
            t = GovernedTools(Path(d), inputs=io, sink=OrderedSink(events))
            t.screen_account(BANK, "hs-1001"); t.check_applicability(BANK, "hs-1001")
            events.clear()
            t.route_contact(BANK, "hs-1001")
        self.assertEqual(events[:2], [("audit", "route"), ("adapter", "contacts")])


class F2TitleVariants(unittest.TestCase):
    def test_ciso_variants_never_routed(self):
        variants = ["C.I.S.O., VP Engineering", "CISO", "C I S O", "Chief Information-Security Officer",
                    "chief   information security officer", "CISO/VP Engineering",
                    "\uff23\uff29\uff33\uff2f"]  # full-width CISO (re-test F5)
        cs = [Contact(str(i), "a", f"P{i}", t, "zoominfo") for i, t in enumerate(variants)]
        routed, skipped = route(cs, {"risk": ["risk"], "engineering": ["engineering"]},
                                ["information security", "ciso"], ["risk", "engineering"])
        self.assertEqual(sum(len(v) for v in routed.values()), 0)
        self.assertEqual(len(skipped), len(variants))


class F3RecipientsOnlyFromRouting(unittest.TestCase):
    def _ready(self, t, account="hs-1001"):
        t.screen_account(BANK, account); t.check_applicability(BANK, account); t.route_contact(BANK, account)

    def test_brief_naming_excluded_ciso_is_refused(self):
        with tempdir() as d:
            t = GovernedTools(Path(d) / "out", playbooks_dir=blocked_ciso_playbooks(Path(d)))
            self._ready(t)
            draft = offline_draft(t, "hs-1001").replace(
                "## Open questions for the account owner\n",
                "## Open questions for the account owner\n- Also loop in Sofia Marchetti (fictional).\n")
            self.assertFalse(t.check_claims(BANK, "hs-1001", draft)["passed"])
            with self.assertRaises(ToolFailure):
                t.request_approval(BANK, "hs-1001", draft)

    def test_excluded_ciso_named_the_ordinary_way_is_refused(self):
        with tempdir() as d:
            t = GovernedTools(Path(d) / "out", playbooks_dir=blocked_ciso_playbooks(Path(d)))
            self._ready(t)
            for line in ("- Also loop in Sofia Marchetti.", "- Also loop in the CISO, Sofia Marchetti.",
                         "- Also loop in SOFIA  MARCHETTI."):
                draft = offline_draft(t, "hs-1001").replace(
                    "## Open questions for the account owner\n", f"## Open questions for the account owner\n{line}\n")
                problems = t.check_claims(BANK, "hs-1001", draft)["problems"]
                self.assertTrue(any("routing excluded" in p for p in problems), (line, problems))

    def test_extra_recipient_line_is_refused(self):
        with tempdir() as d:
            t = GovernedTools(Path(d) / "out", playbooks_dir=blocked_ciso_playbooks(Path(d)))
            self._ready(t)
            draft = offline_draft(t, "hs-1001").replace(
                "## Suggested recipients in the existing relationship\n",
                "## Suggested recipients in the existing relationship\n- Security lane: Someone Else, CISO [zoominfo:contact/zi-2005]\n")
            problems = t.check_claims(BANK, "hs-1001", draft)["problems"]
            self.assertTrue(any("routing did not return" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
