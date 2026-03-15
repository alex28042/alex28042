#!/usr/bin/env python3
"""Fetches language stats from all GitHub repos and updates README.md."""

import json
import subprocess
import re
import math

GITHUB_USER = "alex28042"
BYTES_PER_LINE = 40
LANGUAGES = ["TypeScript", "Java", "Python", "JavaScript", "Kotlin", "Dart", "Swift", "Rust", "Solidity"]
BAR_WIDTH = 40

BADGE_COLORS = {
    "TypeScript": "6e40c9",
    "Java": "6e40c9",
    "Python": "8957e5",
    "JavaScript": "8957e5",
    "Kotlin": "a371f7",
    "Dart": "a371f7",
    "Swift": "d2a8ff",
    "Rust": "d2a8ff",
    "Solidity": "d2a8ff",
}

BADGE_LOGO = {
    "TypeScript": "typescript",
    "Java": "openjdk",
    "Python": "python",
    "JavaScript": "javascript",
    "Kotlin": "kotlin",
    "Dart": "dart",
    "Swift": "swift",
    "Rust": "rust",
    "Solidity": "solidity",
}

DARK_TEXT = {"Swift", "Dart", "Solidity"}


def get_all_repos():
    """Get all repos: owned + collaborator/org member."""
    own_repos = set()
    contrib_repos = set()

    # Own repos (public + private)
    result = subprocess.run(
        ["gh", "api", "user/repos", "--paginate",
         "-q", '[.[] | select(.fork == false and .owner.login == "' + GITHUB_USER + '")] | .[].full_name'],
        capture_output=True, text=True
    )
    for r in result.stdout.strip().split("\n"):
        if r:
            own_repos.add(r)

    # Repos where user is collaborator or org member
    result = subprocess.run(
        ["gh", "api", f"users/{GITHUB_USER}/repos?type=all&affiliation=collaborator,organization_member",
         "--paginate", "-q", '[.[] | select(.fork == false)] | .[].full_name'],
        capture_output=True, text=True
    )
    for r in result.stdout.strip().split("\n"):
        if r and r not in own_repos:
            contrib_repos.add(r)

    return own_repos, contrib_repos


def get_repo_languages(repo_full_name):
    result = subprocess.run(
        ["gh", "api", f"repos/{repo_full_name}/languages"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}


def get_contribution_ratio(repo_full_name):
    """Get the ratio of lines contributed by GITHUB_USER in a repo."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo_full_name}/stats/contributors"],
        capture_output=True, text=True
    )
    try:
        contributors = json.loads(result.stdout)
        if not isinstance(contributors, list):
            return 0.0
        total_additions = 0
        user_additions = 0
        for c in contributors:
            additions = sum(w.get("a", 0) for w in c.get("weeks", []))
            total_additions += additions
            if c.get("author", {}).get("login", "").lower() == GITHUB_USER.lower():
                user_additions = additions
        if total_additions == 0:
            return 0.0
        return user_additions / total_additions
    except (json.JSONDecodeError, TypeError):
        return 0.0


def build_bar(ratio, width):
    filled = round(ratio * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def format_lines(lines):
    if lines >= 1000:
        return f"{lines / 1000:.1f}K"
    return str(lines)


def build_level(lines):
    if lines >= 50000:
        return "\u2588\u2588"
    elif lines >= 3000:
        return "\u2588\u2591"
    else:
        return "\u2591\u2591"


def main():
    own_repos, contrib_repos = get_all_repos()
    totals = {}

    # Own repos: count everything
    for repo in own_repos:
        langs = get_repo_languages(repo)
        for lang, bytes_count in langs.items():
            if lang in LANGUAGES:
                totals[lang] = totals.get(lang, 0) + bytes_count

    # Contributor repos: count only user's contribution ratio
    for repo in contrib_repos:
        ratio = get_contribution_ratio(repo)
        if ratio <= 0:
            continue
        langs = get_repo_languages(repo)
        for lang, bytes_count in langs.items():
            if lang in LANGUAGES:
                totals[lang] = totals.get(lang, 0) + int(bytes_count * ratio)

    repos = own_repos | contrib_repos

    sorted_langs = sorted(
        [(lang, totals.get(lang, 0)) for lang in LANGUAGES],
        key=lambda x: -x[1]
    )

    max_bytes = sorted_langs[0][1] if sorted_langs else 1
    total_lines = sum(b // BYTES_PER_LINE for _, b in sorted_langs)

    # Build ASCII chart
    lines = []
    for lang, bytes_count in sorted_langs:
        loc = bytes_count // BYTES_PER_LINE
        if loc == 0:
            continue
        ratio = bytes_count / max_bytes
        bar = build_bar(ratio, BAR_WIDTH)
        level = build_level(loc)
        loc_str = format_lines(loc).rjust(6)
        lines.append(f" {lang:<13}{bar} {loc_str} lines   {level}")

    separator = " " + "\u2500" * 65
    total_str = format_lines(total_lines)
    lines.append(separator)
    lines.append(f" Total{' ' * 48}{total_str.rjust(6)} lines")

    chart = "```\n" + "\n".join(lines) + "\n```"

    # Build badges
    badges = []
    for lang, _ in sorted_langs:
        if totals.get(lang, 0) == 0:
            continue
        color = BADGE_COLORS[lang]
        logo = BADGE_LOGO[lang]
        text_color = "black" if lang in DARK_TEXT else "white"
        badges.append(
            f"![{lang}](https://img.shields.io/badge/{lang}-{color}?style=for-the-badge&logo={logo}&logoColor={text_color})"
        )

    badge_line = "\n".join(badges)

    new_section = f"""### Languages

<div align="center">

{chart}

{badge_line}

</div>"""

    # Read and replace in README
    with open("README.md", "r") as f:
        readme = f.read()

    pattern = r"### Languages.*?</div>"
    readme = re.sub(pattern, new_section, readme, flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(readme)

    print(f"Updated languages section with {len(repos)} repos, {total_str} total lines")


if __name__ == "__main__":
    main()
