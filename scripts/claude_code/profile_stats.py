from __future__ import annotations

from dataclasses import dataclass

from .history import DailyHistory
from .stats import ClaudeCodeSummary


@dataclass(frozen=True)
class ProfileStats:
    recent: ClaudeCodeSummary
    history: DailyHistory
