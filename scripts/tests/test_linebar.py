import tempfile
import unittest
from datetime import date
from pathlib import Path

from claude_code.linebar import LineBarHistory


class LineBarHistoryTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "stats.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_it_should_read_the_lines_added_per_day(self):
        self.path.write_text('{"days": {"2026-09-01": {"linesAdded": 42, "edits": 3}}}')
        self.assertEqual(LineBarHistory(self.path).daily_lines(), {date(2026, 9, 1): 42})

    def test_it_should_return_nothing_when_the_file_is_missing(self):
        self.assertEqual(LineBarHistory(self.path).daily_lines(), {})


if __name__ == "__main__":
    unittest.main()
