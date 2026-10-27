import unittest

from claude_code.extractors import default_extractor_registry

TIMESTAMP = "2026-10-27T10:00:00.000Z"


def tool_use(name, **tool_input):
    return {"type": "tool_use", "id": f"toolu_{name}", "name": name, "input": tool_input}


class ExtractorsTest(unittest.TestCase):
    def setUp(self):
        self.registry = default_extractor_registry()

    def test_it_should_count_every_line_of_a_written_file(self):
        contribution = self.registry.extract(tool_use("Write", file_path="a.ts", content="a\nb\nc\n"), TIMESTAMP)
        self.assertEqual(contribution.lines_added, 3)

    def test_it_should_count_only_new_lines_of_an_edit(self):
        contribution = self.registry.extract(
            tool_use("Edit", file_path="a.ts", old_string="a\n", new_string="a\nb\n"), TIMESTAMP
        )
        self.assertEqual(contribution.lines_added, 1)

    def test_it_should_sum_the_edits_of_a_multi_edit(self):
        edits = [{"old_string": "", "new_string": "a\n"}, {"old_string": "b", "new_string": "b\nc\nd"}]
        contribution = self.registry.extract(tool_use("MultiEdit", file_path="a.ts", edits=edits), TIMESTAMP)
        self.assertEqual(contribution.lines_added, 3)

    def test_it_should_ignore_a_deleted_notebook_cell(self):
        contribution = self.registry.extract(
            tool_use("NotebookEdit", notebook_path="n.ipynb", new_source="x", edit_mode="delete"), TIMESTAMP
        )
        self.assertIsNone(contribution)

    def test_it_should_take_the_target_of_a_heredoc_redirect(self):
        command = "cat > src/main.rs <<'EOF'\nfn main() {}\nEOF"
        contribution = self.registry.extract(tool_use("Bash", command=command), TIMESTAMP)
        self.assertEqual(contribution.file_path, "src/main.rs")

    def test_it_should_ignore_a_heredoc_that_writes_no_file(self):
        command = "python3 - <<'EOF'\nprint(1)\nEOF"
        self.assertIsNone(self.registry.extract(tool_use("Bash", command=command), TIMESTAMP))

    def test_it_should_ignore_tools_that_do_not_write_code(self):
        self.assertIsNone(self.registry.extract(tool_use("Read", file_path="a.ts"), TIMESTAMP))


if __name__ == "__main__":
    unittest.main()
