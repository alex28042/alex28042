from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from xml.sax.saxutils import quoteattr

from .formatting import format_full_day

RAW_BASE_URL = "https://raw.githubusercontent.com/alex28042/alex28042/main"
VERSION_LENGTH = 10


@dataclass(frozen=True)
class ChartImage:
    path: str
    content: str
    description: str


class ClaudeCodeSectionRenderer:
    def render(self, charts: list[ChartImage], refreshed_on: date) -> str:
        return "\n".join([
            "<div align=\"center\">",
            "",
            *[image_tag(chart) for chart in charts],
            "",
            f"<sub>Every line Claude Code writes on my laptop · refreshed hourly · {format_full_day(refreshed_on)}</sub>",
            "",
            "</div>",
        ])


def image_tag(chart: ChartImage) -> str:
    return f"<img src={quoteattr(image_url(chart))} width=\"100%\" alt={quoteattr(chart.description)} />"


def image_url(chart: ChartImage) -> str:
    version = hashlib.sha256(chart.content.encode()).hexdigest()[:VERSION_LENGTH]
    return f"{RAW_BASE_URL}/{chart.path}?v={version}"
