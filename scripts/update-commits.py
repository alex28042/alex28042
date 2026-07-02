#!/usr/bin/env python3
"""Counts commits authored by the user across all repos (private included)
and updates the Activity section in README.md."""

import json
import re
import subprocess

GITHUB_USER = "alex28042"
FIRST_YEAR = 2020
CURRENT_YEAR = 2026
BAR_WIDTH = 40
REPOS_PER_QUERY = 10


def run_gh(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result.stdout


def get_user_id():
    output = run_gh(["api", f"users/{GITHUB_USER}", "-q", ".node_id"])
    return output.strip()


def get_all_repos():
    """All non-fork repos the token can access: own + collaborator + org."""
    output = run_gh([
        "api", "user/repos", "--paginate",
        "-q", "[.[] | select(.fork == false)] | .[].full_name",
    ])
    return [r for r in output.strip().split("\n") if r]


def build_history_fields(user_id):
    """One aliased totalCount field per year, plus the all-time total."""
    fields = [f'total: history(author: {{id: "{user_id}"}}) {{ totalCount }}']
    for year in range(FIRST_YEAR, CURRENT_YEAR + 1):
        fields.append(
            f'y{year}: history(author: {{id: "{user_id}"}}, '
            f'since: "{year}-01-01T00:00:00Z", until: "{year}-12-31T23:59:59Z") '
            f'{{ totalCount }}'
        )
    return " ".join(fields)


def count_commits(repos, user_id):
    """Query default-branch history per repo in batches. Returns
    (per-year dict, all-time total)."""
    history_fields = build_history_fields(user_id)
    per_year = {year: 0 for year in range(FIRST_YEAR, CURRENT_YEAR + 1)}
    total = 0

    for start in range(0, len(repos), REPOS_PER_QUERY):
        batch = repos[start:start + REPOS_PER_QUERY]
        aliases = []
        for i, full_name in enumerate(batch):
            owner, name = full_name.split("/")
            aliases.append(
                f'r{i}: repository(owner: "{owner}", name: "{name}") '
                f'{{ defaultBranchRef {{ target {{ ... on Commit {{ {history_fields} }} }} }} }}'
            )
        query = "query { " + " ".join(aliases) + " }"
        output = run_gh(["api", "graphql", "-f", f"query={query}"])
        try:
            data = json.loads(output).get("data") or {}
        except json.JSONDecodeError:
            continue
        for repo_data in data.values():
            if not repo_data or not repo_data.get("defaultBranchRef"):
                continue
            commit = repo_data["defaultBranchRef"]["target"]
            total += commit["total"]["totalCount"]
            for year in per_year:
                per_year[year] += commit[f"y{year}"]["totalCount"]

    return per_year, total


def format_count(count):
    if count >= 1000:
        return f"{count / 1000:.1f}K"
    return str(count)


def build_bar(ratio, width):
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def build_chart(per_year, total):
    max_commits = max(per_year.values()) or 1
    lines = []
    for year, count in sorted(per_year.items()):
        bar = build_bar(count / max_commits, BAR_WIDTH)
        count_str = format_count(count).rjust(6)
        lines.append(f" {year}         {bar} {count_str} commits")
    separator = " " + "─" * 65
    lines.append(separator)
    lines.append(f" Total{' ' * 49}{format_count(total).rjust(6)} commits")
    return "```\n" + "\n".join(lines) + "\n```"


def build_section(per_year, total, repo_count):
    chart = build_chart(per_year, total)
    badges = "\n".join([
        f"![Commits](https://img.shields.io/badge/Commits-{format_count(total)}-6e40c9?style=for-the-badge&logo=git&logoColor=white)",
        f"![Repositories](https://img.shields.io/badge/Repositories-{repo_count}-8957e5?style=for-the-badge&logo=github&logoColor=white)",
    ])
    return f"""### Activity

<div align="center">

{chart}

{badges}

</div>"""


def update_readme(section):
    with open("README.md", "r") as f:
        readme = f.read()

    pattern = r"### Activity.*?</div>"
    if re.search(pattern, readme, flags=re.DOTALL):
        readme = re.sub(pattern, section, readme, count=1, flags=re.DOTALL)
    else:
        # First run: insert right after the Languages section.
        languages_pattern = r"(### Languages.*?</div>\n)"
        readme = re.sub(
            languages_pattern, r"\1\n---\n\n" + section + "\n",
            readme, count=1, flags=re.DOTALL,
        )

    with open("README.md", "w") as f:
        f.write(readme)


def main():
    user_id = get_user_id()
    repos = get_all_repos()
    per_year, total = count_commits(repos, user_id)
    own_repo_count = len([r for r in repos if r.startswith(f"{GITHUB_USER}/")])

    update_readme(build_section(per_year, total, own_repo_count))
    print(f"Updated activity section: {total} commits across {len(repos)} repos")


if __name__ == "__main__":
    main()
