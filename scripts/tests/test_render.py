import unittest

from claude_code.render import badge_text, bar, compact, percent, shares


class RenderHelpersTest(unittest.TestCase):
    def test_it_should_escape_dashes_underscores_and_spaces_for_shields(self):
        self.assertEqual(badge_text("Lines - my_repo"), "Lines_--_my__repo")

    def test_it_should_fill_the_whole_bar_for_the_peak(self):
        self.assertEqual(bar(1.0), "████████████")

    def test_it_should_show_tiny_shares_as_less_than_one_percent(self):
        self.assertEqual(percent(0.002), "<1%")

    def test_it_should_compact_millions_with_two_decimals(self):
        self.assertEqual(compact(2_142_419), "2.14M")

    def test_it_should_scale_bars_against_the_largest_entry(self):
        self.assertEqual(shares([("a", 50), ("b", 25)], 100)[1], ("b", 0.25, 0.5))


if __name__ == "__main__":
    unittest.main()
