"""Campaign Manager playbook: JSONC parsing and the stub's rules."""

import copy
import unittest
from pathlib import Path

from agent.input import playbook as P

ROOT = Path(__file__).resolve().parent.parent
PB = P.load(ROOT / "playbooks/reign-first-motion.jsonc")
KW = dict(fs_segments={"dsib_capital_markets"}, claim_ids={"P-FORGE", "P-GATEWAY", "P-ASSURANCE", "P-BRIEFING"},
          implemented_triggers={"SR-26-2"})


def problems(**edits):
    pb = copy.deepcopy(PB)
    for path, value in edits.items():
        target, *keys = pb, *path.split("__")
        for k in keys[:-1]:
            target = target[int(k)] if isinstance(target, list) else target[k]
        target[keys[-1]] = value
    return P.validate(pb, **KW)


class PlaybookTests(unittest.TestCase):
    def test_first_motion_playbook_is_valid(self):
        self.assertEqual(P.validate(PB, **KW), [])
        self.assertEqual([p["status"] for p in PB["plays"]], ["implemented", "not_implemented", "not_implemented"])

    def test_jsonc_comments_stripped_but_not_inside_strings(self):
        self.assertEqual(P.strip_jsonc('{"a": "x // y /* z */"} // c\n/* d */'), '{"a": "x // y /* z */"} \n')

    def test_stub_rules(self):
        self.assertTrue(any("named humans" in p for p in problems(approval__approvers=[])))
        self.assertTrue(any("kill_criteria" in p for p in problems(kill_criteria=[])))
        self.assertTrue(any("R-17" in p for p in problems(audit__rule="none")))
        self.assertTrue(any("product" in p for p in problems(product="spray")))
        self.assertTrue(any("channel" in p for p in problems(plays__0__channel="email")))
        self.assertTrue(any("trigger" in p for p in problems(plays__0__trigger={"type": "vibes", "id": "x"})))

    def test_guessed_rules(self):
        self.assertTrue(any("must say why" in p for p in problems(plays__1__not_implemented_reason="")))
        self.assertTrue(any("not an implemented trigger" in p for p in problems(plays__0__trigger={"type": "regulatory", "id": "FDA-PCCP-2025"})))
        self.assertTrue(any("claim ids" in p for p in problems(plays__0__claims=["P-CERTIFIED"])))
        self.assertTrue(any("principal" in p for p in problems(approval__principal="agent")))
        self.assertTrue(any("max_accounts_per_run" in p for p in problems(limits={"max_accounts_per_run": 0})))


if __name__ == "__main__":
    unittest.main()
