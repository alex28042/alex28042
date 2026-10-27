import unittest
from datetime import date
from unittest.mock import Mock

from claude_code.records import Contribution, ModelRequest, TranscriptRecords
from claude_code.stats import ClaudeCodeStatsCalculator

TODAY = date(2026, 10, 27)


def contribution(day, lines, path="a.ts"):
    return Contribution(f"toolu_{day}_{lines}_{path}", f"2026-10-{day:02d}T12:00:00Z", path, lines)


def request(day, model, session="s1"):
    return ModelRequest(f"req_{day}_{model}_{session}", f"2026-10-{day:02d}T12:00:00Z", model, 100, session)


class ClaudeCodeStatsCalculatorTest(unittest.TestCase):
    def setUp(self):
        classifier = Mock()
        classifier.classify.side_effect = lambda path: "TypeScript" if path.endswith(".ts") else None
        self.calculator = ClaudeCodeStatsCalculator(classifier, 7)

    def summarize(self, contributions=(), requests=()):
        return self.calculator.summarize(TranscriptRecords(list(contributions), list(requests)), TODAY, None)

    def test_it_should_leave_out_lines_older_than_the_window(self):
        summary = self.summarize([contribution(27, 5), contribution(1, 100)])
        self.assertEqual(summary.lines_total, 5)

    def test_it_should_place_each_day_at_its_offset_in_the_window(self):
        summary = self.summarize([contribution(21, 4), contribution(27, 6)])
        self.assertEqual(summary.lines_per_day, [4, 0, 0, 0, 0, 0, 6])

    def test_it_should_keep_the_streak_alive_when_today_has_no_lines_yet(self):
        summary = self.summarize([contribution(25, 1), contribution(26, 1)])
        self.assertEqual(summary.current_streak, 2)

    def test_it_should_only_group_lines_of_classified_files(self):
        summary = self.summarize([contribution(27, 3, "a.ts"), contribution(27, 9, "notes.md")])
        self.assertEqual([(share.language, share.lines) for share in summary.languages], [("TypeScript", 3)])

    def test_it_should_rank_models_by_number_of_calls(self):
        requests = [request(27, "claude-sonnet-5-5"), request(26, "claude-opus-5-5"), request(27, "claude-opus-5-5")]
        summary = self.summarize(requests=requests)
        self.assertEqual([model.model for model in summary.models], ["Opus 5.5", "Sonnet 5.5"])

    def test_it_should_count_distinct_sessions(self):
        requests = [request(27, "claude-opus-5-5", "a"), request(26, "claude-opus-5-5", "a"), request(27, "claude-opus-5-5", "b")]
        self.assertEqual(self.summarize(requests=requests).sessions, 2)


if __name__ == "__main__":
    unittest.main()
