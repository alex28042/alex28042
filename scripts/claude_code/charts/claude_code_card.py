from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby
from typing import Optional

from ..formatting import compact, format_full_day, format_month, percent
from ..profile_stats import ProfileStats
from . import svg
from .calendar import DAYS_PER_WEEK, IntensityScale, calendar_days, month_labels
from .language_colors import language_color
from .theme import HEAT_LEVELS, heat_class

WIDTH = 880
PADDING = 24
WEEKS = 53
CALENDAR_DAYS = WEEKS * DAYS_PER_WEEK
CELL = 12
CELL_GAP = 3
CELL_RADIUS = 2.5
PITCH = CELL + CELL_GAP
GRID_RIGHT = WIDTH - PADDING
GRID_LEFT = GRID_RIGHT - (WEEKS * PITCH - CELL_GAP)
GRID_TOP = 112
GRID_BOTTOM = GRID_TOP + DAYS_PER_WEEK * PITCH - CELL_GAP
WEEKDAY_LABELS = ((1, "Mon"), (3, "Wed"), (5, "Fri"))
LEGEND_BASELINE = GRID_BOTTOM + 26
LEGEND_WORD_ROOM = 36
LANGUAGES_BASELINE = LEGEND_BASELINE + 48
TOP_LANGUAGES = 5
BAR_TOP = LANGUAGES_BASELINE + 14
BAR_WIDTH = WIDTH - 2 * PADDING
BAR_HEIGHT = 8
BAR_CLIP_ID = "language-bar"
SEGMENT_GAP = 2
LANGUAGE_COLUMN = BAR_WIDTH / (TOP_LANGUAGES + 1)
LANGUAGE_ROW_BASELINE = BAR_TOP + BAR_HEIGHT + 26
HEIGHT = LANGUAGE_ROW_BASELINE + 22
WEEK_DELAY_MS = 14
SEGMENT_DELAY_MS = 90


@dataclass(frozen=True)
class LanguageSlice:
    name: str
    lines: int
    color: Optional[str]


class ClaudeCodeCard:
    file_name = "claude-code.svg"

    def render(self, stats: ProfileStats) -> str:
        body = [*self._header(stats), *self._calendar(stats), *self._legend(), *self._languages(stats)]
        return svg.document(WIDTH, HEIGHT, self.describe(stats), body)

    def describe(self, stats: ProfileStats) -> str:
        headline = "".join(content for content, _ in summary_parts(stats))
        shares = ", ".join(f"{piece.name} {percent(share)}" for piece, share in shares_of(language_slices(stats)))
        return f"Claude Code: {headline}. Languages, last 30 days: {shares}" if shares else f"Claude Code: {headline}"

    def _header(self, stats: ProfileStats) -> list[str]:
        return [
            svg.text(PADDING, 44, "Claude Code", "title"),
            svg.rich_text(PADDING, 68, summary_parts(stats), "summary"),
        ]

    def _calendar(self, stats: ProfileStats) -> list[str]:
        days = calendar_days(stats.history, WEEKS)
        scale = IntensityScale([day.lines for day in days], HEAT_LEVELS)
        elements = [svg.text(PADDING, cell_y(weekday) + CELL - 2, label, "axis") for weekday, label in WEEKDAY_LABELS]
        elements += [svg.text(cell_x(label.week), GRID_TOP - 8, format_month(label.month), "axis")
                     for label in month_labels(days)]
        for week, week_days in groupby(days, key=lambda day: day.week):
            cells = [svg.rect(cell_x(day.week), cell_y(day.weekday), CELL, CELL,
                              f"cell {heat_class(scale.level(day.lines))}", CELL_RADIUS) for day in week_days]
            elements.append(svg.group(cells, "week", f"animation-delay:{week * WEEK_DELAY_MS}ms"))
        return elements

    def _legend(self) -> list[str]:
        swatches_end = GRID_RIGHT - LEGEND_WORD_ROOM
        first_x = swatches_end - (HEAT_LEVELS + 1) * PITCH + CELL_GAP
        swatch_top = LEGEND_BASELINE - CELL + 2
        return [
            svg.text(GRID_LEFT, LEGEND_BASELINE, "Lines added per day", "note"),
            svg.text(first_x - 6, LEGEND_BASELINE, "Less", "note", "end"),
            *[svg.rect(first_x + level * PITCH, swatch_top, CELL, CELL, f"cell {heat_class(level)}", CELL_RADIUS)
              for level in range(HEAT_LEVELS + 1)],
            svg.text(GRID_RIGHT, LEGEND_BASELINE, "More", "note", "end"),
        ]

    def _languages(self, stats: ProfileStats) -> list[str]:
        shares = shares_of(language_slices(stats))
        elements = [
            svg.rich_text(PADDING, LANGUAGES_BASELINE, [("Languages", "heading"), (" · last 30 days", "note")]),
            svg.clip_path(BAR_CLIP_ID, svg.rect(PADDING, BAR_TOP, BAR_WIDTH, BAR_HEIGHT, radius=BAR_HEIGHT / 2)),
        ]
        if not shares:
            return [*elements, svg.rect(PADDING, BAR_TOP, BAR_WIDTH, BAR_HEIGHT, "other", BAR_HEIGHT / 2)]
        available = BAR_WIDTH - SEGMENT_GAP * (len(shares) - 1)
        segments = []
        x = float(PADDING)
        for index, (piece, share) in enumerate(shares):
            width = max(available * share, 2)
            delay = f"animation-delay:{index * SEGMENT_DELAY_MS}ms"
            segments.append(svg.rect(x, BAR_TOP, width, BAR_HEIGHT, f"segment {fill_class(piece)}",
                                     style=fill_style(piece) + delay))
            x += width + SEGMENT_GAP
        elements.append(svg.group(segments, clip=BAR_CLIP_ID))
        for index, (piece, share) in enumerate(shares):
            x = PADDING + index * LANGUAGE_COLUMN
            elements.append(svg.circle(x + 4, LANGUAGE_ROW_BASELINE - 4, 4, fill_class(piece), fill_style(piece)))
            elements.append(svg.rich_text(x + 14, LANGUAGE_ROW_BASELINE,
                                          [(piece.name, "name"), (f" {percent(share)}", "share")]))
        return elements


def summary_parts(stats: ProfileStats) -> list[tuple[str, str]]:
    history = stats.history
    parts = [(compact(history.total), "strong"), (f" lines written since {format_full_day(history.started_on)}", "")]
    if history.current_streak > 1:
        parts += [(" · ", ""), (str(history.current_streak), "strong"), ("-day streak", "")]
    return parts


def language_slices(stats: ProfileStats) -> list[LanguageSlice]:
    languages = stats.recent.languages
    slices = [LanguageSlice(share.language, share.lines, language_color(share.language))
              for share in languages[:TOP_LANGUAGES]]
    rest = sum(share.lines for share in languages[TOP_LANGUAGES:])
    if rest:
        slices.append(LanguageSlice("Other", rest, None))
    return slices


def shares_of(slices: list[LanguageSlice]) -> list[tuple[LanguageSlice, float]]:
    total = sum(piece.lines for piece in slices)
    return [(piece, piece.lines / total) for piece in slices] if total else []


def fill_class(piece: LanguageSlice) -> str:
    return "other" if piece.color is None else ""


def fill_style(piece: LanguageSlice) -> str:
    return "" if piece.color is None else f"fill:{piece.color};"


def cell_x(week: int) -> float:
    return GRID_LEFT + week * PITCH


def cell_y(weekday: int) -> float:
    return GRID_TOP + weekday * PITCH
