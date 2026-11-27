from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ..history import DailyHistory

DAYS_PER_WEEK = 7


@dataclass(frozen=True)
class CalendarDay:
    day: date
    week: int
    weekday: int
    lines: int


@dataclass(frozen=True)
class MonthLabel:
    week: int
    month: date


class IntensityScale:
    def __init__(self, values: list[int], levels: int) -> None:
        active = sorted(value for value in values if value > 0)
        self._bounds = [active[len(active) * step // levels] for step in range(1, levels)] if active else []

    def level(self, lines: int) -> int:
        if lines <= 0:
            return 0
        return 1 + sum(1 for bound in self._bounds if lines >= bound)


def calendar_days(history: DailyHistory, weeks: int) -> list[CalendarDay]:
    start = week_start(history.last_day) - timedelta(weeks=weeks - 1)
    lines_by_day = {history.day_at(index): lines for index, lines in enumerate(history.lines_per_day)}
    span = (history.last_day - start).days + 1
    return [
        CalendarDay(day, offset // DAYS_PER_WEEK, offset % DAYS_PER_WEEK, lines_by_day.get(day, 0))
        for offset, day in ((offset, start + timedelta(days=offset)) for offset in range(span))
    ]


def month_labels(days: list[CalendarDay]) -> list[MonthLabel]:
    return [MonthLabel(day.week, day.day) for day in days if day.weekday == 0 and day.day.day <= DAYS_PER_WEEK]


def week_start(day: date) -> date:
    return day - timedelta(days=(day.weekday() + 1) % DAYS_PER_WEEK)
