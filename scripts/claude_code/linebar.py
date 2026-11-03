from __future__ import annotations

import json
from datetime import date
from pathlib import Path


class LineBarHistory:
    def __init__(self, stats_file: Path) -> None:
        self._stats_file = stats_file

    def daily_lines(self) -> dict[date, int]:
        try:
            days = json.loads(self._stats_file.read_text()).get("days") or {}
        except (OSError, json.JSONDecodeError):
            return {}
        return {date.fromisoformat(day): int(stats.get("linesAdded") or 0) for day, stats in days.items()}
