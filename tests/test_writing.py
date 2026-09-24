"""The write-ups a reviewer reads: no em or en dashes and none of the stock AI-writing words."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DASHES = re.compile("[–—]")
BANNED = re.compile(
    r"\b(delve\w*|robust\w*|seamless\w*|leverag\w*|comprehensive\w*|cutting-edge|game-changer\w*|unlock\w*|empower\w*)\b"
    r"|in today's landscape|it's worth noting",
    re.IGNORECASE,
)


def write_ups() -> list[Path]:
    return [ROOT / "README.md", ROOT / "PROCESS-LOG.md", *sorted((ROOT / "docs").rglob("*.md"))]


class WritingTests(unittest.TestCase):
    def test_files_exist(self):
        files = write_ups()
        self.assertGreater(len(files), 2)
        for f in files:
            self.assertTrue(f.is_file(), f)

    def test_no_em_or_en_dashes(self):
        for f in write_ups():
            for n, line in enumerate(f.read_text().splitlines(), 1):
                self.assertIsNone(DASHES.search(line), f"{f.relative_to(ROOT)}:{n}: {line[:80]!r}")

    def test_no_banned_words(self):
        for f in write_ups():
            for n, line in enumerate(f.read_text().splitlines(), 1):
                m = BANNED.search(line)
                self.assertIsNone(m, f"{f.relative_to(ROOT)}:{n}: {m and m.group(0)!r}")


if __name__ == "__main__":
    unittest.main()
