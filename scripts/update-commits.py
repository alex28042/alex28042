#!/usr/bin/env python3
"""Counts commits authored by the user across all repos (private included)
and updates the Activity section in README.md."""

import datetime
import json
import re
import subprocess

GITHUB_USER = "alex28042"
FIRST_YEAR = 2020
CURRENT_YEAR = datetime.date.today().year
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


def build_section(per_year, total, repo_count):
    this_year = per_year.get(CURRENT_YEAR, 0)
    return "\n".join([
        f"![Commits](https://img.shields.io/badge/Commits-{format_count(total)}-6e40c9?style=flat-square&logo=git&logoColor=white)",
        f"![{CURRENT_YEAR}](https://img.shields.io/badge/{CURRENT_YEAR}-{format_count(this_year)}_commits-8957e5?style=flat-square&logo=github&logoColor=white)",
        f"![Repositories](https://img.shields.io/badge/Repositories-{repo_count}-a371f7?style=flat-square&logo=github&logoColor=white)",
    ])


def update_readme(section):
    with open("README.md", "r") as f:
        readme = f.read()

    pattern = r"(<!-- activity:start -->\n).*?(<!-- activity:end -->)"
    readme = re.sub(pattern, lambda m: m.group(1) + section + "\n" + m.group(2), readme, count=1, flags=re.DOTALL)

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
