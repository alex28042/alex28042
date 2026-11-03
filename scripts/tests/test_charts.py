import unittest
import xml.etree.ElementTree as ElementTree
from datetime import date

from claude_code.charts.breakdown_card import BreakdownCard, language_slices
from claude_code.charts.daily_lines import DailyLinesChart
from claude_code.history import DailyHistory
from claude_code.profile_stats import ProfileStats
from claude_code.stats import ClaudeCodeSummary, LanguageShare, ModelShare

LANGUAGES = [LanguageShare(name, lines) for name, lines in [("Zig", 60), ("Elm", 20), ("Nim", 9), ("Lua", 5), ("Ada", 4), ("Hack", 1), ("Odin", 1)]]
SUMMARY = ClaudeCodeSummary(
    first_day=date(2026, 9, 1),
    last_day=date(2026, 9, 3),
    lines_per_day=[0, 40, 60],
    languages=LANGUAGES,
    models=[ModelShare("Opus 9", 80, 1000), ModelShare("Haiku 9", 20, 100)],
    sessions=7,
    output_tokens=1100,
    files_touched=12,
)
STATS = ProfileStats(SUMMARY, DailyHistory(date(2026, 8, 30), [10, 0, 0, 40, 60], 0))


class DailyLinesChartTest(unittest.TestCase):
    def test_it_should_render_well_formed_svg(self):
        root = ElementTree.fromstring(DailyLinesChart().render(STATS))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_it_should_draw_one_bar_per_day_with_lines(self):
        self.assertEqual(DailyLinesChart().render(STATS).count('class="bar"'), 3)

    def test_it_should_label_september_where_the_month_starts(self):
        self.assertIn(">Sep</text>", DailyLinesChart().render(STATS))


class BreakdownCardTest(unittest.TestCase):
    def test_it_should_render_well_formed_svg(self):
        root = ElementTree.fromstring(BreakdownCard().render(STATS))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_it_should_fold_languages_past_the_fifth_into_other(self):
        self.assertEqual(language_slices(STATS)[-1].amount, 2)

    def test_it_should_paint_other_in_the_neutral_color(self):
        self.assertEqual(language_slices(STATS)[-1].css_class, "other")


if __name__ == "__main__":
    unittest.main()
