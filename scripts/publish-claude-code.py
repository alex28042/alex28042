#!/usr/bin/env python3

import os
import sys
from datetime import date, datetime

from claude_code.composition import BRANCH, CLONE_DIR, REMOTE_URL, SECTION_NAME, render_claude_code_section
from claude_code.git_publisher import GitPublisher
from claude_code.readme import ReadmeFile

RELAUNCHED = "PROFILE_README_RELAUNCHED"


def log(message):
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}", flush=True)


def main():
    publisher = GitPublisher(CLONE_DIR, REMOTE_URL, BRANCH, log)
    if publisher.sync() and os.environ.get(RELAUNCHED) != "1":
        log("scripts changed, relaunching with the new version")
        os.environ[RELAUNCHED] = "1"
        os.execv(sys.executable, [sys.executable, *sys.argv])
    changed = ReadmeFile(CLONE_DIR / "README.md").replace_section(SECTION_NAME, render_claude_code_section(date.today()))
    log("section changed" if changed else "section unchanged")
    publisher.publish("README.md", "chore: update Claude Code stats")


if __name__ == "__main__":
    main()
