from __future__ import annotations

from dataclasses import dataclass

from ..formatting import compact, format_day, format_full_day, format_month, plural
from ..profile_stats import ProfileStats
from . import svg
from .scale import LinearScale, nice_ticks

WIDTH = 880
HEIGHT = 392
PADDING = 24
PLOT_LEFT = 68
PLOT_RIGHT = WIDTH - PADDING
BARS_TOP = 172
BARS_BASE = 274
TOTAL_TOP = 310
TOTAL_BASE = 352
DATE_ROW = 372
BAR_GAP = 2
EDGE_LABEL_ROOM = 48
BAR_DELAY_MS = 6


@dataclass(frozen=True)
class Stat:
    value: str
    label: str


class DailyLinesChart:
    file_name = "claude-code-daily.svg"

    def render(self, stats: ProfileStats) -> str:
        history = stats.history
        body = [
            svg.text(PADDING, 38, "Lines written with Claude Code", "title"),
            svg.text(PADDING, 58, f"Every day since {format_full_day(history.first_day)} · lines added, not commits",
                     "subtitle"),
            *self._stat_row(stats),
            *self._bars(stats),
            *self._running_total(stats),
            *self._dates(stats),
        ]
        return svg.document(WIDTH, HEIGHT, self.describe(stats), body)

    def describe(self, stats: ProfileStats) -> str:
        history = stats.history
        return (
            f"Lines written with Claude Code per day since {format_full_day(history.first_day)}: "
            f"{compact(history.total)} in total, best day {compact(history.lines_per_day[history.peak_index])} "
            f"on {format_day(history.peak_day)}"
        )

    def _stat_row(self, stats: ProfileStats) -> list[str]:
        history = stats.history
        tiles = [
            Stat(compact(history.total), f"lines since {format_day(history.first_day)}"),
            Stat(compact(stats.recent.lines_total), "last 30 days"),
            Stat(plural(history.current_streak, "day"), "current streak"),
            Stat(compact(history.lines_per_day[history.peak_index]), f"best day · {format_day(history.peak_day)}"),
        ]
        width = (WIDTH - 2 * PADDING) / len(tiles)
        elements = []
        for index, tile in enumerate(tiles):
            x = PADDING + index * width
            elements.append(svg.text(x, 102, tile.value, "stat"))
            elements.append(svg.text(x, 120, tile.label, "stat-label"))
        return elements

    def _bars(self, stats: ProfileStats) -> list[str]:
        values = stats.history.lines_per_day
        ticks = nice_ticks(max(values))
        scale = LinearScale(ticks[-1], BARS_BASE, BARS_TOP)
        step = (PLOT_RIGHT - PLOT_LEFT) / len(values)
        bar_width = max(step - BAR_GAP, 1)
        elements = [svg.text(PADDING, BARS_TOP - 14, "LINES PER DAY", "panel")]
        for tick in ticks:
            y = scale(tick)
            elements.append(svg.line(PLOT_LEFT, y, PLOT_RIGHT, y, "grid"))
            elements.append(svg.text(PLOT_LEFT - 8, y + 3, compact(tick), "axis", "end"))
        for index, lines in enumerate(values):
            if lines == 0:
                continue
            x = PLOT_LEFT + index * step + BAR_GAP / 2
            elements.append(svg.column(x, scale(lines), bar_width, BARS_BASE, "bar",
                                       f"animation-delay:{index * BAR_DELAY_MS}ms"))
        peak = stats.history.peak_index
        peak_x = PLOT_LEFT + (peak + 0.5) * step
        anchor = "end" if peak_x > PLOT_RIGHT - EDGE_LABEL_ROOM else "start"
        offset = 6 if anchor == "start" else -6
        elements.append(svg.text(peak_x + offset, scale(values[peak]) + 4, compact(values[peak]), "label", anchor))
        return elements

    def _running_total(self, stats: ProfileStats) -> list[str]:
        totals = stats.history.running_totals
        scale = LinearScale(totals[-1], TOTAL_BASE, TOTAL_TOP)
        step = (PLOT_RIGHT - PLOT_LEFT) / len(totals)
        points = [(PLOT_LEFT + (index + 0.5) * step, scale(total)) for index, total in enumerate(totals)]
        last_x, last_y = points[-1]
        return [
            svg.text(PADDING, TOTAL_TOP - 14, "RUNNING TOTAL", "panel"),
            svg.line(PLOT_LEFT, TOTAL_BASE, PLOT_RIGHT, TOTAL_BASE, "grid"),
            svg.text(PLOT_LEFT - 8, TOTAL_BASE + 3, "0", "axis", "end"),
            svg.area(points, TOTAL_BASE, "area"),
            svg.polyline(points, "trend"),
            svg.circle(last_x, last_y, 4, "dot"),
            svg.text(last_x - 8, last_y - 8, compact(totals[-1]), "label", "end"),
        ]

    def _dates(self, stats: ProfileStats) -> list[str]:
        history = stats.history
        step = (PLOT_RIGHT - PLOT_LEFT) / len(history.lines_per_day)
        elements = [
            svg.text(PLOT_LEFT, DATE_ROW, format_day(history.first_day), "axis"),
            svg.text(PLOT_RIGHT, DATE_ROW, format_day(history.last_day), "axis", "end"),
        ]
        for index in range(len(history.lines_per_day)):
            day = history.day_at(index)
            x = PLOT_LEFT + index * step
            if day.day != 1 or x - PLOT_LEFT < EDGE_LABEL_ROOM or PLOT_RIGHT - x < EDGE_LABEL_ROOM:
                continue
            elements.append(svg.text(x, DATE_ROW, format_month(day), "axis", "middle"))
        return elements
