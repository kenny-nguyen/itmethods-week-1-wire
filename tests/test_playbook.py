import json
"""Campaign Manager playbook: JSONC parsing and the stub's rules."""

import copy
import unittest
from pathlib import Path

from agent.input import playbook as P

ROOT = Path(__file__).resolve().parent.parent
PB = P.load(ROOT / "playbooks/bank-sr26-2.jsonc")
KW = dict(fs_segments={"dsib_capital_markets"},
          claim_ids={c["id"] for c in json.loads((ROOT / "docs/research/product-claims.json").read_text())["claims"]
                     if c["usable_in_briefs"]},
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
    def test_first_motion_playbooks_are_valid_and_stub_shaped(self):  # A-041
        motion = P.load(ROOT / "playbooks/motions/reign-first-motion.jsonc")
        self.assertEqual(P.validate_motion(motion), [])
        statuses = []
        for pid in motion["playbooks"]:
            pb = P.load(ROOT / f"playbooks/{pid}.jsonc")
            self.assertEqual(P.validate(pb, **KW), [], pid)
            for field in ("playbook_id", "product", "audience", "trigger", "channel", "approval", "kill_criteria", "audit"):
                self.assertIn(field, pb)
            self.assertIsInstance(pb["trigger"], dict)  # one trigger, one audience, one channel
            statuses.append(pb["trigger_status"])
        self.assertEqual(statuses, ["implemented", "not_implemented", "not_implemented"])

    def test_jsonc_comments_stripped_but_not_inside_strings(self):
        self.assertEqual(P.strip_jsonc('{"a": "x // y /* z */"} // c\n/* d */'), '{"a": "x // y /* z */"} \n')

    def test_stub_rules(self):
        self.assertTrue(any("named humans" in p for p in problems(approval__approvers=[])))
        self.assertTrue(any("kill_criteria" in p for p in problems(kill_criteria=[])))
        self.assertTrue(any("R-17" in p for p in problems(audit__rule="none")))
        self.assertTrue(any("product" in p for p in problems(product="spray")))
        self.assertTrue(any("channel" in p for p in problems(channel="email")))
        self.assertTrue(any("trigger" in p for p in problems(trigger={"type": "vibes", "id": "x"})))
        self.assertTrue(any("A-041" in p for p in problems(plays=[])))

    def test_guessed_rules(self):
        self.assertTrue(any("must say why" in p for p in problems(trigger_status="not_implemented")))
        self.assertTrue(any("not an implemented trigger" in p for p in problems(trigger={"type": "regulatory", "id": "FDA-PCCP-2025"})))
        self.assertTrue(any("claim ids" in p for p in problems(claims=["P-CERTIFIED"])))
        self.assertTrue(any("principal" in p for p in problems(approval__principal="agent")))
        self.assertTrue(any("A-037" in p for p in problems(limits={"max_accounts_per_run": 5})))
        self.assertTrue(any("playbook_id" in p for p in problems(playbook_id="../../evil")))


if __name__ == "__main__":
    unittest.main()
