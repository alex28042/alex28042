import unittest
from datetime import date

from claude_code.history import DailyHistory, build_daily_history

RECENT_START = date(2026, 10, 30)


class BuildDailyHistoryTest(unittest.TestCase):
    def test_it_should_start_on_the_first_archived_day_with_lines(self):
        history = build_daily_history({date(2026, 10, 27): 0, date(2026, 10, 28): 7}, RECENT_START, [1, 2], 30)
        self.assertEqual(history.first_day, date(2026, 10, 28))

    def test_it_should_fill_missing_days_with_zero(self):
        history = build_daily_history({date(2026, 10, 28): 7}, RECENT_START, [1, 2], 30)
        self.assertEqual(history.lines_per_day, [7, 0, 1, 2])

    def test_it_should_prefer_the_recent_window_over_the_archive(self):
        history = build_daily_history({RECENT_START: 99}, RECENT_START, [1, 2], 30)
        self.assertEqual(history.lines_per_day, [1, 2])

    def test_it_should_carry_lines_older_than_the_limit_into_the_total(self):
        history = build_daily_history({date(2026, 10, 1): 50}, RECENT_START, [1, 2], 2)
        self.assertEqual(history.total, 53)

    def test_it_should_fall_back_to_the_recent_window_when_nothing_was_written(self):
        history = build_daily_history({}, RECENT_START, [0, 0], 30)
        self.assertEqual(history.first_day, RECENT_START)


class DailyHistoryTest(unittest.TestCase):
    def setUp(self):
        self.history = DailyHistory(date(2026, 10, 1), [3, 0, 5, 4, 0], 10)

    def test_it_should_accumulate_from_the_lines_before_the_chart(self):
        self.assertEqual(self.history.running_totals, [13, 13, 18, 22, 22])

    def test_it_should_find_the_best_day(self):
        self.assertEqual(self.history.peak_day, date(2026, 10, 3))

    def test_it_should_keep_the_streak_alive_when_today_has_no_lines_yet(self):
        self.assertEqual(self.history.current_streak, 2)

    def test_it_should_end_on_the_last_day_of_the_series(self):
        self.assertEqual(self.history.last_day, date(2026, 10, 5))


if __name__ == "__main__":
    unittest.main()
