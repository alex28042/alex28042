import unittest
from datetime import date

from claude_code.formatting import compact, format_full_day, percent, plural


class FormattingTest(unittest.TestCase):
    def test_it_should_show_tiny_shares_as_less_than_one_percent(self):
        self.assertEqual(percent(0.002), "<1%")

    def test_it_should_compact_millions_with_two_decimals(self):
        self.assertEqual(compact(2_142_419), "2.14M")

    def test_it_should_compact_thousands_with_one_decimal(self):
        self.assertEqual(compact(14_430), "14.4K")

    def test_it_should_keep_the_noun_singular_for_one(self):
        self.assertEqual(plural(1, "day"), "1 day")

    def test_it_should_write_the_month_day_and_year(self):
        self.assertEqual(format_full_day(date(2026, 8, 12)), "Aug 12, 2026")


if __name__ == "__main__":
    unittest.main()
