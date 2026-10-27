from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

BOT_NAME = "readme-stats"
BOT_EMAIL = "readme-stats@alex28042.local"


class GitCommandError(Exception):
    pass


class GitPublisher:
    def __init__(self, clone_dir: Path, remote_url: str, branch: str, log: Callable[[str], None]) -> None:
        self._clone_dir = clone_dir
        self._remote_url = remote_url
        self._branch = branch
        self._log = log

    def sync(self) -> bool:
        if not (self._clone_dir / ".git").exists():
            self._clone_dir.parent.mkdir(parents=True, exist_ok=True)
            self._run_outside("clone", "--branch", self._branch, self._remote_url, str(self._clone_dir))
            return True
        scripts_before = self._scripts_tree()
        self._pull_or_reset()
        return self._scripts_tree() != scripts_before

    def _scripts_tree(self) -> str:
        return self._git("rev-parse", "HEAD:scripts", check=False)

    def _pull_or_reset(self) -> None:
        try:
            self._git("pull", "--rebase", "origin", self._branch)
        except GitCommandError as error:
            self._log(f"pull failed, resetting to origin: {error}")
            self._git("rebase", "--abort", check=False)
            self._git("fetch", "origin", self._branch)
            self._git("reset", "--hard", f"origin/{self._branch}")

    def publish(self, file_name: str, message: str) -> None:
        if self._git("status", "--porcelain", "--", file_name):
            self._git("add", "--", file_name)
            self._git("-c", f"user.name={BOT_NAME}", "-c", f"user.email={BOT_EMAIL}", "commit", "-m", message)
        if not self._git("log", f"origin/{self._branch}..HEAD", "--oneline"):
            self._log("nothing to push")
            return
        self._git("pull", "--rebase", "origin", self._branch)
        self._git("push", "origin", f"HEAD:{self._branch}")
        self._log("pushed")

    def _git(self, *args: str, check: bool = True) -> str:
        return run_command(["git", "-C", str(self._clone_dir), *args], check)

    def _run_outside(self, *args: str) -> str:
        return run_command(["git", *args], True)


def run_command(command: list[str], check: bool) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise GitCommandError(f"{' '.join(command)}: {result.stderr.strip()}")
    return result.stdout.strip()
