from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from itertools import accumulate


@dataclass(frozen=True)
class DailyHistory:
    first_day: date
    lines_per_day: list[int]
    lines_before: int

    @property
    def last_day(self) -> date:
        return self.first_day + timedelta(days=len(self.lines_per_day) - 1)

    @property
    def total(self) -> int:
        return self.lines_before + sum(self.lines_per_day)

    @property
    def running_totals(self) -> list[int]:
        return list(accumulate(self.lines_per_day, initial=self.lines_before))[1:]

    @property
    def peak_index(self) -> int:
        return max(range(len(self.lines_per_day)), key=lambda index: self.lines_per_day[index])

    @property
    def peak_day(self) -> date:
        return self.day_at(self.peak_index)

    @property
    def current_streak(self) -> int:
        days = list(self.lines_per_day)
        if days and days[-1] == 0:
            days.pop()
        streak = 0
        for lines in reversed(days):
            if lines == 0:
                break
            streak += 1
        return streak

    def day_at(self, index: int) -> date:
        return self.first_day + timedelta(days=index)


def build_daily_history(
    archived: dict[date, int],
    recent_first_day: date,
    recent_lines: list[int],
    max_days: int,
) -> DailyHistory:
    lines_by_day = dict(archived)
    for offset, lines in enumerate(recent_lines):
        lines_by_day[recent_first_day + timedelta(days=offset)] = lines
    last_day = recent_first_day + timedelta(days=len(recent_lines) - 1)
    earliest_active = min((day for day, lines in lines_by_day.items() if lines > 0), default=recent_first_day)
    first_day = max(earliest_active, last_day - timedelta(days=max_days - 1))
    span = (last_day - first_day).days + 1
    return DailyHistory(
        first_day=first_day,
        lines_per_day=[lines_by_day.get(first_day + timedelta(days=offset), 0) for offset in range(span)],
        lines_before=sum(lines for day, lines in lines_by_day.items() if day < first_day),
    )
