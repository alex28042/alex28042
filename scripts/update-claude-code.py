#!/usr/bin/env python3

from datetime import date
from pathlib import Path

from claude_code.composition import SECTION_NAME, render_claude_code_section
from claude_code.readme import ReadmeFile

README = Path(__file__).resolve().parent.parent / "README.md"


def main():
    changed = ReadmeFile(README).replace_section(SECTION_NAME, render_claude_code_section(date.today()))
    print("README updated" if changed else "README already up to date")


if __name__ == "__main__":
    main()
