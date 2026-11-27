import unittest
import xml.etree.ElementTree as ElementTree
from datetime import date

from claude_code.charts.calendar import IntensityScale, calendar_days, month_labels, week_start
from claude_code.charts.claude_code_card import ClaudeCodeCard, language_slices
from claude_code.charts.language_colors import language_color
from claude_code.history import DailyHistory
from claude_code.profile_stats import ProfileStats
from claude_code.stats import ClaudeCodeSummary, LanguageShare, ModelShare

LANGUAGES = [LanguageShare(name, lines) for name, lines in [("Zig", 60), ("Elm", 20), ("Nim", 9), ("Lua", 5), ("Ada", 4), ("Hack", 1), ("Odin", 1)]]
SUMMARY = ClaudeCodeSummary(
    first_day=date(2026, 9, 1),
    last_day=date(2026, 9, 3),
    lines_per_day=[0, 40, 60],
    languages=LANGUAGES,
    models=[ModelShare("Opus 9", 80, 1000)],
    sessions=7,
    output_tokens=1000,
    files_touched=12,
)
HISTORY = DailyHistory(date(2026, 8, 30), [10, 0, 0, 40, 60], 0, date(2026, 8, 30))
STATS = ProfileStats(SUMMARY, HISTORY)
LEGEND_SWATCHES = 5
CALENDAR_CELLS = 52 * 7 + 5


class ClaudeCodeCardTest(unittest.TestCase):
    def test_it_should_render_well_formed_svg(self):
        root = ElementTree.fromstring(ClaudeCodeCard().render(STATS))
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")

    def test_it_should_draw_a_cell_for_every_day_up_to_today(self):
        self.assertEqual(ClaudeCodeCard().render(STATS).count('class="cell heat-'), CALENDAR_CELLS + LEGEND_SWATCHES)

    def test_it_should_state_the_total_and_the_first_day(self):
        self.assertIn("110 lines written since Aug 30, 2026", ClaudeCodeCard().describe(STATS))

    def test_it_should_mention_a_streak_of_several_days(self):
        self.assertIn("2-day streak", ClaudeCodeCard().describe(STATS))

    def test_it_should_fold_languages_past_the_fifth_into_other(self):
        self.assertEqual(language_slices(STATS)[-1].lines, 2)

    def test_it_should_paint_other_in_the_neutral_colour(self):
        self.assertIsNone(language_slices(STATS)[-1].color)


class CalendarTest(unittest.TestCase):
    def test_it_should_start_weeks_on_sunday(self):
        self.assertEqual(week_start(date(2026, 9, 3)), date(2026, 8, 30))

    def test_it_should_put_today_in_the_last_week(self):
        self.assertEqual(calendar_days(HISTORY, 53)[-1].week, 52)

    def test_it_should_label_the_first_week_of_august(self):
        labels = month_labels(calendar_days(HISTORY, 53))
        self.assertIn(date(2026, 8, 2), [label.month for label in labels])

    def test_it_should_leave_days_without_lines_empty(self):
        self.assertEqual(IntensityScale([1, 2, 3, 4], 4).level(0), 0)

    def test_it_should_put_the_busiest_days_in_the_top_level(self):
        self.assertEqual(IntensityScale([1, 2, 3, 4], 4).level(4), 4)

    def test_it_should_put_the_quietest_days_in_the_first_level(self):
        self.assertEqual(IntensityScale([1, 2, 3, 4], 4).level(1), 1)


class LanguageColorTest(unittest.TestCase):
    def test_it_should_use_the_github_colour_of_a_known_language(self):
        self.assertEqual(language_color("TypeScript"), "#3178c6")


if __name__ == "__main__":
    unittest.main()
