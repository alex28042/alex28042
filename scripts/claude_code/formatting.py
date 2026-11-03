from __future__ import annotations

from datetime import date

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def compact(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1000:
        return f"{value / 1000:.1f}K"
    return str(value)


def percent(ratio: float) -> str:
    return f"{ratio * 100:.0f}%" if ratio >= 0.01 else "<1%"


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def format_month(day: date) -> str:
    return MONTHS[day.month - 1]


def format_day(day: date) -> str:
    return f"{format_month(day)} {day.day}"


def format_full_day(day: date) -> str:
    return f"{format_day(day)}, {day.year}"
