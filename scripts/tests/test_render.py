import unittest
from datetime import date

from claude_code.render import ChartImage, ClaudeCodeSectionRenderer, image_url

CHART = ChartImage("assets/daily.svg", "<svg>v1</svg>", "Lines per day & more")


class SectionRendererTest(unittest.TestCase):
    def test_it_should_point_to_the_raw_file_on_main(self):
        self.assertTrue(image_url(CHART).startswith("https://raw.githubusercontent.com/alex28042/alex28042/main/assets/daily.svg?v="))

    def test_it_should_change_the_url_when_the_chart_changes(self):
        self.assertNotEqual(image_url(CHART), image_url(ChartImage(CHART.path, "<svg>v2</svg>", CHART.description)))

    def test_it_should_escape_the_description_in_the_alt_text(self):
        section = ClaudeCodeSectionRenderer().render([CHART], date(2026, 11, 3))
        self.assertIn('alt="Lines per day &amp; more"', section)

    def test_it_should_stamp_the_refresh_day(self):
        section = ClaudeCodeSectionRenderer().render([CHART], date(2026, 11, 3))
        self.assertIn("refreshed hourly · Nov 3, 2026", section)


if __name__ == "__main__":
    unittest.main()
