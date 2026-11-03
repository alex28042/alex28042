from __future__ import annotations

from dataclasses import dataclass

from ..formatting import compact, percent
from ..profile_stats import ProfileStats
from . import svg
from .theme import CATEGORY_SLOTS, category_class

WIDTH = 880
HEIGHT = 268
PADDING = 24
DIVIDER_X = WIDTH / 2
LEFT_END = DIVIDER_X - PADDING
RIGHT_START = DIVIDER_X + PADDING
RIGHT_END = WIDTH - PADDING
STACK_TOP = 82
STACK_HEIGHT = 12
SEGMENT_GAP = 2
LEGEND_TOP = 124
LEGEND_ROW_HEIGHT = 22
ROW_HEIGHT = 26
MODEL_ROWS = 4
MODEL_NAME_WIDTH = 92
MODEL_VALUE_WIDTH = 44
ACTIVITY_TOP = 222
SEGMENT_DELAY_MS = 90


@dataclass(frozen=True)
class Slice:
    name: str
    amount: int
    css_class: str


class BreakdownCard:
    file_name = "claude-code-languages.svg"

    def render(self, stats: ProfileStats) -> str:
        body = [
            *self._languages(stats),
            svg.line(DIVIDER_X, PADDING, DIVIDER_X, HEIGHT - PADDING, "divider"),
            *self._models(stats),
            *self._activity(stats),
        ]
        return svg.document(WIDTH, HEIGHT, self.describe(stats), body)

    def describe(self, stats: ProfileStats) -> str:
        slices = language_slices(stats)
        total = sum(piece.amount for piece in slices) or 1
        shares = ", ".join(f"{piece.name} {percent(piece.amount / total)}" for piece in slices)
        return f"Languages Claude Code wrote in the last 30 days: {shares}"

    def _languages(self, stats: ProfileStats) -> list[str]:
        slices = language_slices(stats)
        total = sum(piece.amount for piece in slices) or 1
        elements = [
            svg.text(PADDING, 38, "Languages", "title"),
            svg.text(PADDING, 58, "Share of lines written · last 30 days", "subtitle"),
            svg.rect(PADDING, STACK_TOP, LEFT_END - PADDING, STACK_HEIGHT, "track", STACK_HEIGHT / 2),
        ]
        available = LEFT_END - PADDING - SEGMENT_GAP * (len(slices) - 1)
        x = float(PADDING)
        for index, piece in enumerate(slices):
            width = max(available * piece.amount / total, 1)
            elements.append(svg.rect(x, STACK_TOP, width, STACK_HEIGHT, f"segment {piece.css_class}", 2,
                                     f"animation-delay:{index * SEGMENT_DELAY_MS}ms"))
            x += width + SEGMENT_GAP
        for index, piece in enumerate(slices):
            y = LEGEND_TOP + index * LEGEND_ROW_HEIGHT
            elements.append(svg.rect(PADDING, y - 9, 10, 10, piece.css_class, 2))
            elements.append(svg.text(PADDING + 18, y, piece.name, "name"))
            elements.append(svg.text(LEFT_END, y, f"{compact(piece.amount)} lines · {percent(piece.amount / total)}",
                                     "value", "end"))
        return elements

    def _models(self, stats: ProfileStats) -> list[str]:
        models = stats.recent.models
        total = sum(model.requests for model in models) or 1
        track_start = RIGHT_START + MODEL_NAME_WIDTH
        track_width = RIGHT_END - MODEL_VALUE_WIDTH - track_start
        elements = [
            svg.text(RIGHT_START, 38, "Models", "title"),
            svg.text(RIGHT_START, 58, "Share of requests · last 30 days", "subtitle"),
        ]
        for index, model in enumerate(models[:MODEL_ROWS]):
            y = STACK_TOP + 10 + index * ROW_HEIGHT
            share = model.requests / total
            elements.append(svg.text(RIGHT_START, y, model.model, "name"))
            elements.append(svg.rect(track_start, y - 8, track_width, 8, "track", 4))
            elements.append(svg.rect(track_start, y - 8, max(track_width * share, 4), 8, "hbar", 4,
                                     f"animation-delay:{index * SEGMENT_DELAY_MS}ms"))
            elements.append(svg.text(RIGHT_END, y, percent(share), "value", "end"))
        return elements

    def _activity(self, stats: ProfileStats) -> list[str]:
        recent = stats.recent
        tiles = [
            (str(recent.sessions), "sessions"),
            (compact(recent.files_touched), "files touched"),
            (compact(recent.output_tokens), "output tokens"),
            (f"{recent.active_days}/{len(recent.lines_per_day)}", "active days"),
        ]
        width = (RIGHT_END - RIGHT_START) / len(tiles)
        elements = []
        for index, (value, label) in enumerate(tiles):
            x = RIGHT_START + index * width
            elements.append(svg.text(x, ACTIVITY_TOP, value, "stat"))
            elements.append(svg.text(x, ACTIVITY_TOP + 18, label, "stat-label"))
        return elements


def language_slices(stats: ProfileStats) -> list[Slice]:
    languages = stats.recent.languages
    slices = [
        Slice(share.language, share.lines, category_class(rank))
        for rank, share in enumerate(languages[:CATEGORY_SLOTS])
    ]
    rest = sum(share.lines for share in languages[CATEGORY_SLOTS:])
    if rest:
        slices.append(Slice("Other", rest, category_class(CATEGORY_SLOTS)))
    return slices
