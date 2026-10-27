import unittest

from claude_code.line_counting import line_count, lines_added


class LineCountingTest(unittest.TestCase):
    def test_it_should_ignore_blank_lines(self):
        self.assertEqual(line_count("a\n\n   \nb\n"), 2)

    def test_it_should_count_only_lines_missing_from_the_old_block(self):
        self.assertEqual(lines_added("a\nb\n", "a\nb\nc\nd\n"), 2)

    def test_it_should_count_a_repeated_line_once_per_extra_occurrence(self):
        self.assertEqual(lines_added("x\n", "x\nx\n"), 1)


if __name__ == "__main__":
    unittest.main()
