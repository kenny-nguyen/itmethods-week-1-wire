"""Requirements tests: CI fails if the submission stops meeting the assignment brief.

These read submission documents and example artifacts as owned contracts: the one-page process log,
the required sections, the example audit trail and briefs. They do not grep implementation code.
"""

import json
import re
import unittest
from pathlib import Path

from agent.governance.audit import validate_record
from agent.processing import preflight as pf
from agent.processing.checks import check_brief
from evals.score_run import _context
from agent.input.playbook import load
from agent.run_playbook import _load_inputs

ROOT = Path(__file__).resolve().parent.parent
MAX_LOG_WORDS = 600  # "a process log (one page)"; the target is 550
FINGERPRINTS = ROOT / "tests/packet_fingerprints.json"


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


class SubmissionRequirements(unittest.TestCase):
    def test_process_log_is_one_page(self):
        text = (ROOT / "PROCESS-LOG.md").read_text()
        prose = re.sub(r"(?s)```.*?```", "", text)  # the required snippets do not count against the page
        self.assertLessEqual(words(prose), MAX_LOG_WORDS)

    def test_process_log_has_real_prompts_or_configs(self):
        text = (ROOT / "PROCESS-LOG.md").read_text()
        self.assertGreaterEqual(len(re.findall(r"```", text)) // 2, 2)

    def test_required_sections_exist(self):
        readme = (ROOT / "README.md").read_text()
        for title in ("## One thing I did not know", "## What I would not ship"):
            self.assertIn(title, readme)

    def test_no_em_or_en_dashes_in_written_docs(self):
        """The kit (AGENTS.md, contract/, .claude/agents/) is committed as received and is not checked."""
        files = [ROOT / "README.md", ROOT / "PROCESS-LOG.md", ROOT / "AMBIGUITY-REGISTER.md"]
        for folder in ("docs", "examples", "skills", "playbooks", "prompts", "evals", "agent", "tests"):
            files += [p for p in (ROOT / folder).rglob("*") if p.is_file()
                      and p.suffix in {".md", ".json", ".jsonc", ".py", ".html", ".txt"}]
        hits = [f"{p.relative_to(ROOT)}:{i}" for p in files for i, line in enumerate(p.read_text().splitlines(), 1)
                if "\u2014" in line or "\u2013" in line]
        self.assertEqual(hits, [])

    def test_example_audit_records_carry_every_r17_field(self):
        records = [json.loads(l) for p in ROOT.glob("examples/*/audit.jsonl") for l in p.read_text().splitlines() if l]
        self.assertTrue(records)
        self.assertEqual([r["record_id"] for r in records if validate_record(r)], [])

    def test_example_briefs_pass_the_gate(self):
        io = _load_inputs(ROOT)
        pb = load(ROOT / "playbooks/bank-sr26-2.jsonc")
        briefs = [b for b in ROOT.glob("examples/*/briefs/*.md")
                  if not b.name.endswith((".brief-forwardable.md", ".owner-notes.md"))]
        self.assertTrue(briefs)
        for b in briefs:
            account = b.stem.rsplit("_", 1)[-1]
            ctx = _context(io, pb, account)
            with self.subTest(brief=b.name):
                kwargs = {**ctx.gate_kwargs(), "recipient_lines": None, "excluded_names": ()}
                self.assertEqual(check_brief(b.read_text(), **kwargs), [])

    def test_forwardable_briefs_carry_no_internal_data(self):
        leaks = [f"{p.relative_to(ROOT)}: {l[:60]}" for p in ROOT.glob("examples/*/briefs/*.brief-forwardable.md")
                 for l in p.read_text().splitlines()
                 if re.search(r"hubspot:|clay:|zoominfo:|do-not-route|\blanes?\b", l, re.IGNORECASE)]
        self.assertEqual(leaks, [])

    def test_no_packet_text_in_repo(self):
        """No 80+ character packet sentence appears in any repository text file (hash match, no packet text stored)."""
        import hashlib
        banned = set(json.loads(FINGERPRINTS.read_text())["sha256"])
        self.assertTrue(banned)
        hits = []
        for p in ROOT.rglob("*"):
            if not p.is_file() or p.suffix not in {".md", ".json", ".jsonc", ".py", ".txt", ".html"} \
                    or {".venv", ".git"} & set(p.parts) or p == FINGERPRINTS:
                continue
            for s in re.split(r"(?<=[.!?])\s+|\n", p.read_text(errors="ignore")):
                s = re.sub(r"\s+", " ", s).strip().lstrip("-*> ").strip()
                if len(s) >= 80 and hashlib.sha256(s.lower().encode()).hexdigest() in banned:
                    hits.append(f"{p.relative_to(ROOT)}: {s[:60]}")
        self.assertEqual(hits, [], "long packet sentences copied into the repository")


if __name__ == "__main__":
    unittest.main()
