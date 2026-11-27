import unittest
from claude_code.render import ChartImage, ClaudeCodeSectionRenderer, image_url

CHART = ChartImage("assets/daily.svg", "<svg>v1</svg>", "Lines per day & more")


class SectionRendererTest(unittest.TestCase):
    def test_it_should_point_to_the_raw_file_on_main(self):
        self.assertTrue(image_url(CHART).startswith("https://raw.githubusercontent.com/alex28042/alex28042/main/assets/daily.svg?v="))

    def test_it_should_change_the_url_when_the_chart_changes(self):
        self.assertNotEqual(image_url(CHART), image_url(ChartImage(CHART.path, "<svg>v2</svg>", CHART.description)))

    def test_it_should_escape_the_description_in_the_alt_text(self):
        section = ClaudeCodeSectionRenderer().render([CHART])
        self.assertIn('alt="Lines per day &amp; more"', section)


if __name__ == "__main__":
    unittest.main()
