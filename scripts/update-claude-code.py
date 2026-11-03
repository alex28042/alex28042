#!/usr/bin/env python3

from datetime import date
from pathlib import Path

from claude_code.composition import SECTION_NAME, build_claude_code_section
from claude_code.readme import ReadmeFile

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def main():
    section = build_claude_code_section(date.today())
    for chart in section.charts:
        target = REPOSITORY_ROOT / chart.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(chart.content)
    changed = ReadmeFile(REPOSITORY_ROOT / "README.md").replace_section(SECTION_NAME, section.markdown)
    print("README updated" if changed else "README already up to date")


if __name__ == "__main__":
    main()
