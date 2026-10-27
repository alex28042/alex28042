from __future__ import annotations

from collections import Counter


def meaningful_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def line_count(text: str) -> int:
    return len(meaningful_lines(text))


def lines_added(old_text: str, new_text: str) -> int:
    remaining = Counter(meaningful_lines(old_text))
    added = 0
    for line in meaningful_lines(new_text):
        if remaining[line] > 0:
            remaining[line] -= 1
        else:
            added += 1
    return added
