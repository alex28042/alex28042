from __future__ import annotations

from datetime import date
from math import sqrt
from urllib.parse import quote

from .stats import ClaudeCodeSummary

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SPARK_BLOCKS = "▁▂▃▄▅▆▇█"
BAR_WIDTH = 12
ROWS = 5
LANGUAGE_COLUMN = 11
MODEL_COLUMN = 11
CELL_EXTRA = 6
PALETTE = ["6e40c9", "8957e5", "a371f7", "d2a8ff"]


class ClaudeCodeSectionRenderer:
    def render(self, summary: ClaudeCodeSummary) -> str:
        return "\n".join([
            "<div align=\"center\">",
            "",
            self._badges(summary),
            "",
            "```text",
            self._sparkline(summary),
            "",
            self._breakdown(summary),
            "```",
            "",
            f"<sub>Every line Claude Code writes on my laptop · rolling 30 days · refreshed hourly · "
            f"{format_full_day(summary.last_day)}</sub>",
            "",
            "</div>",
        ])

    def _badges(self, summary: ClaudeCodeSummary) -> str:
        badges = [badge("Lines · 30 days", compact(summary.lines_total), PALETTE[0], "claude")]
        if summary.lifetime is not None:
            since = f"{MONTHS[summary.lifetime.since.month - 1]} {summary.lifetime.since.year}"
            badges.append(badge(f"Since {since}", compact(summary.lifetime.lines_added), PALETTE[1]))
        badges.append(badge("Streak", plural(summary.current_streak, "day"), PALETTE[2]))
        top_model = summary.models[0].model if summary.models else "—"
        badges.append(badge("Main model", top_model, PALETTE[3], "anthropic", dark_text=True))
        return "\n".join(badges)

    def _sparkline(self, summary: ClaudeCodeSummary) -> str:
        values = summary.lines_per_day
        peak = max(values) or 1
        cells = "".join(
            " " if value == 0 else SPARK_BLOCKS[min(int(sqrt(value / peak) * len(SPARK_BLOCKS)), len(SPARK_BLOCKS) - 1)]
            for value in values
        )
        return (
            f"{format_day(summary.first_day)} {cells} {format_day(summary.last_day)}   "
            f"peak {compact(peak)}/day · {summary.active_days} of {len(values)} days active"
        )

    def _breakdown(self, summary: ClaudeCodeSummary) -> str:
        language_total = sum(share.lines for share in summary.languages) or 1
        model_total = sum(model.requests for model in summary.models) or 1
        languages = shares([(share.language, share.lines) for share in summary.languages[:ROWS]], language_total)
        models = shares([(model.model, model.requests) for model in summary.models[:ROWS]], model_total)

        rows = [f"{'LANGUAGES':<{LANGUAGE_COLUMN + BAR_WIDTH + CELL_EXTRA}}   MODELS"]
        for index in range(max(len(languages), len(models))):
            left = share_cell(languages, index, LANGUAGE_COLUMN)
            right = share_cell(models, index, MODEL_COLUMN)
            rows.append(f"{left}   {right}".rstrip())
        return "\n".join(rows)


def shares(counts: list[tuple[str, int]], total: int) -> list[tuple[str, float, float]]:
    peak = max((count for _, count in counts), default=0) or 1
    return [(name, count / total, count / peak) for name, count in counts]


def share_cell(rows: list[tuple[str, float, float]], index: int, name_width: int) -> str:
    if index >= len(rows):
        return " " * (name_width + BAR_WIDTH + CELL_EXTRA)
    name, share, ratio_to_peak = rows[index]
    return f"{name:<{name_width}}{bar(ratio_to_peak)} {percent(share).rjust(5)}"


def badge(label: str, message: str, color: str, logo: str = "", dark_text: bool = False) -> str:
    url = f"https://img.shields.io/badge/{badge_text(label)}-{badge_text(message)}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={logo}&logoColor={'black' if dark_text else 'white'}"
    return f"![{label}]({url})"


def badge_text(text: str) -> str:
    escaped = text.replace("-", "--").replace("_", "__").replace(" ", "_")
    return quote(escaped, safe="_-.")


def bar(ratio: float) -> str:
    filled = round(ratio * BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


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


def format_day(day: date) -> str:
    return f"{MONTHS[day.month - 1]} {day.day}"


def format_full_day(day: date) -> str:
    return f"{format_day(day)}, {day.year}"
