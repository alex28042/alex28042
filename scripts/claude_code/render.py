from __future__ import annotations

import hashlib
from dataclasses import dataclass
from xml.sax.saxutils import quoteattr

RAW_BASE_URL = "https://raw.githubusercontent.com/alex28042/alex28042/main"
VERSION_LENGTH = 10


@dataclass(frozen=True)
class ChartImage:
    path: str
    content: str
    description: str


class ClaudeCodeSectionRenderer:
    def render(self, charts: list[ChartImage]) -> str:
        return "\n".join(image_tag(chart) for chart in charts)


def image_tag(chart: ChartImage) -> str:
    return f"<img src={quoteattr(image_url(chart))} width=\"100%\" alt={quoteattr(chart.description)} />"


def image_url(chart: ChartImage) -> str:
    version = hashlib.sha256(chart.content.encode()).hexdigest()[:VERSION_LENGTH]
    return f"{RAW_BASE_URL}/{chart.path}?v={version}"
