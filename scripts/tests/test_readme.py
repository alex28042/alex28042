import tempfile
import unittest
from pathlib import Path

from claude_code.readme import MissingSectionError, ReadmeFile


class ReadmeFileTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "README.md"
        self.path.write_text("intro\n<!-- stats:start -->\nold\n<!-- stats:end -->\noutro\n")

    def tearDown(self):
        self.directory.cleanup()

    def test_it_should_replace_only_the_marked_section(self):
        ReadmeFile(self.path).replace_section("stats", "new")
        self.assertEqual(self.path.read_text(), "intro\n<!-- stats:start -->\nnew\n<!-- stats:end -->\noutro\n")

    def test_it_should_report_no_change_when_the_content_is_the_same(self):
        self.assertFalse(ReadmeFile(self.path).replace_section("stats", "old"))

    def test_it_should_fail_when_the_markers_are_missing(self):
        with self.assertRaises(MissingSectionError):
            ReadmeFile(self.path).replace_section("languages", "new")


if __name__ == "__main__":
    unittest.main()
