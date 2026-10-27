import unittest

from claude_code.models import model_display_name


class ModelDisplayNameTest(unittest.TestCase):
    def test_it_should_turn_a_dashed_version_into_a_dotted_one(self):
        self.assertEqual(model_display_name("claude-opus-5-5"), "Opus 5.5")

    def test_it_should_drop_the_snapshot_date(self):
        self.assertEqual(model_display_name("claude-haiku-4-5-20251001"), "Haiku 4.5")

    def test_it_should_keep_a_single_number_version(self):
        self.assertEqual(model_display_name("claude-sonnet-5"), "Sonnet 5")

    def test_it_should_leave_unknown_ids_untouched(self):
        self.assertEqual(model_display_name("gpt-5"), "gpt-5")


if __name__ == "__main__":
    unittest.main()
