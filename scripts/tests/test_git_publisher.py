import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from claude_code.git_publisher import GitCommandError, GitPublisher


def git_that_conflicts_on_rebase(command, check):
    arguments = command[3:]
    if arguments[:2] == ["pull", "--rebase"]:
        raise GitCommandError("conflict in README.md")
    if arguments[0] == "log":
        return "abc123 chore: update Claude Code stats"
    return ""


class GitPublisherTest(unittest.TestCase):
    def setUp(self):
        self.publisher = GitPublisher(Path("/repo"), "https://example.test/repo.git", "main", Mock())

    def published_commands(self):
        with patch("claude_code.git_publisher.run_command", side_effect=git_that_conflicts_on_rebase) as run_command:
            self.publisher.publish(["README.md"], "chore: stats")
        return [call.args[0][3:] for call in run_command.call_args_list]

    def test_it_should_reset_to_origin_when_the_rebase_conflicts(self):
        self.assertIn(["reset", "--hard", "origin/main"], self.published_commands())

    def test_it_should_not_push_when_the_rebase_conflicts(self):
        self.assertFalse(any(command[0] == "push" for command in self.published_commands()))


if __name__ == "__main__":
    unittest.main()
