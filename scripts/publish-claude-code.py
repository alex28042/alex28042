#!/usr/bin/env python3

import os
import sys
from datetime import date, datetime

from claude_code.composition import BRANCH, CLONE_DIR, REMOTE_URL, SECTION_NAME, build_claude_code_section
from claude_code.git_publisher import GitPublisher
from claude_code.readme import ReadmeFile

RELAUNCHED = "PROFILE_README_RELAUNCHED"
README = "README.md"


def log(message):
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}", flush=True)


def main():
    publisher = GitPublisher(CLONE_DIR, REMOTE_URL, BRANCH, log)
    if publisher.sync() and os.environ.get(RELAUNCHED) != "1":
        log("scripts changed, relaunching with the new version")
        os.environ[RELAUNCHED] = "1"
        os.execv(sys.executable, [sys.executable, *sys.argv])
    section = build_claude_code_section(date.today())
    for chart in section.charts:
        target = CLONE_DIR / chart.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(chart.content)
    changed = ReadmeFile(CLONE_DIR / README).replace_section(SECTION_NAME, section.markdown)
    log("section changed" if changed else "section unchanged")
    publisher.publish([README, *[chart.path for chart in section.charts]], "chore: update Claude Code stats")


if __name__ == "__main__":
    main()
