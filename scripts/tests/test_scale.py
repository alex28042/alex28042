import unittest

from claude_code.charts.scale import LinearScale, nice_ticks


class ScaleTest(unittest.TestCase):
    def test_it_should_round_the_top_tick_up_to_a_nice_step(self):
        self.assertEqual(nice_ticks(151_568), [0, 50_000, 100_000, 150_000, 200_000])

    def test_it_should_use_quarter_steps_when_they_fit_better(self):
        self.assertEqual(nice_ticks(70, 3), [0, 25, 50, 75])

    def test_it_should_never_exceed_the_requested_intervals(self):
        self.assertEqual(nice_ticks(2_290_000), [0, 1_000_000, 2_000_000, 3_000_000])

    def test_it_should_give_an_empty_series_a_unit_axis(self):
        self.assertEqual(nice_ticks(0), [0, 1])

    def test_it_should_map_the_domain_onto_an_inverted_range(self):
        self.assertEqual(LinearScale(100, 200, 100)(25), 175)


if __name__ == "__main__":
    unittest.main()
