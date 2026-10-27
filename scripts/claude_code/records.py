from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, timezone
from typing import Optional


@dataclass(frozen=True)
class Contribution:
    tool_use_id: str
    timestamp: str
    file_path: Optional[str]
    lines_added: int

    def local_day(self) -> date:
        return local_day_of(self.timestamp)


@dataclass(frozen=True)
class ModelRequest:
    key: str
    timestamp: str
    model: str
    output_tokens: int
    session_id: str

    def local_day(self) -> date:
        return local_day_of(self.timestamp)


@dataclass(frozen=True)
class TranscriptRecords:
    contributions: list[Contribution]
    requests: list[ModelRequest]


def local_day_of(timestamp: str) -> date:
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone().date()
