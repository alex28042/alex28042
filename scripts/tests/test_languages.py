import unittest

from claude_code.languages import default_language_classifier


class LanguageClassifierTest(unittest.TestCase):
    def setUp(self):
        self.classifier = default_language_classifier()

    def test_it_should_classify_by_extension(self):
        self.assertEqual(self.classifier.classify("/repo/src/App.tsx"), "TypeScript")

    def test_it_should_classify_known_file_names(self):
        self.assertEqual(self.classifier.classify("/repo/Dockerfile"), "Dockerfile")

    def test_it_should_not_classify_documentation(self):
        self.assertIsNone(self.classifier.classify("/repo/README.md"))


if __name__ == "__main__":
    unittest.main()
