"""Every brief is also written as a forwardable part (public sources only) and the owner's notes."""

import re
import unittest
from pathlib import Path

from agent.processing.brief import TemplateProvider
from agent.run_playbook import run
from tests.helpers import tempdir

MOTION = Path(__file__).resolve().parent.parent / "playbooks/motions/reign-first-motion.jsonc"
INTERNAL = re.compile(r"hubspot:|clay:|zoominfo:|do-not-route|\blanes?\b", re.IGNORECASE)


class SplitTests(unittest.TestCase):
    def test_forwardable_part_has_no_internal_data(self):
        with tempdir() as d:
            s = run(MOTION, Path(d), provider=TemplateProvider())
            for aid in ("hs-1001", "hs-1002"):
                b = Path(s["accounts"][aid]["brief"])
                fwd = b.with_name(b.stem + ".brief-forwardable.md").read_text()
                notes = b.with_name(b.stem + ".owner-notes.md").read_text()
                self.assertFalse(INTERNAL.search(fwd), fwd)
                self.assertIn("## What changed", fwd)
                self.assertIn("## Sources", fwd)
                self.assertIn("Suggested recipients", notes)
                self.assertIn("hubspot:company/", notes)


if __name__ == "__main__":
    unittest.main()
