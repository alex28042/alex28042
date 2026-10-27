from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class LifetimeLines:
    since: date
    lines_added: int


class LineBarHistory:
    def __init__(self, stats_file: Path) -> None:
        self._stats_file = stats_file

    def lifetime_lines(self) -> Optional[LifetimeLines]:
        try:
            days = json.loads(self._stats_file.read_text()).get("days") or {}
        except (OSError, json.JSONDecodeError):
            return None
        if not days:
            return None
        total = sum(int(day.get("linesAdded") or 0) for day in days.values())
        return LifetimeLines(date.fromisoformat(min(days)), total)
