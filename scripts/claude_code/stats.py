from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from .languages import LanguageClassifier
from .linebar import LifetimeLines
from .models import model_display_name
from .records import TranscriptRecords


@dataclass(frozen=True)
class LanguageShare:
    language: str
    lines: int


@dataclass(frozen=True)
class ModelShare:
    model: str
    requests: int
    output_tokens: int


@dataclass(frozen=True)
class ClaudeCodeSummary:
    first_day: date
    last_day: date
    lines_per_day: list[int]
    languages: list[LanguageShare]
    models: list[ModelShare]
    sessions: int
    output_tokens: int
    files_touched: int
    lifetime: Optional[LifetimeLines]

    @property
    def lines_total(self) -> int:
        return sum(self.lines_per_day)

    @property
    def active_days(self) -> int:
        return sum(1 for lines in self.lines_per_day if lines > 0)

    @property
    def current_streak(self) -> int:
        streak = 0
        days = list(self.lines_per_day)
        if days and days[-1] == 0:
            days.pop()
        for lines in reversed(days):
            if lines == 0:
                break
            streak += 1
        return streak


class ClaudeCodeStatsCalculator:
    def __init__(self, classifier: LanguageClassifier, window_days: int) -> None:
        self._classifier = classifier
        self._window_days = window_days

    def summarize(self, records: TranscriptRecords, today: date, lifetime: Optional[LifetimeLines]) -> ClaudeCodeSummary:
        first_day = today - timedelta(days=self._window_days - 1)
        lines_by_day: Counter[date] = Counter()
        lines_by_language: Counter[str] = Counter()
        files = set()
        for contribution in records.contributions:
            day = contribution.local_day()
            if not first_day <= day <= today or contribution.lines_added == 0:
                continue
            lines_by_day[day] += contribution.lines_added
            if contribution.file_path:
                files.add(contribution.file_path)
            language = self._classifier.classify(contribution.file_path)
            if language:
                lines_by_language[language] += contribution.lines_added

        requests_by_model: Counter[str] = Counter()
        tokens_by_model: defaultdict[str, int] = defaultdict(int)
        sessions = set()
        for request in records.requests:
            if not first_day <= request.local_day() <= today:
                continue
            name = model_display_name(request.model)
            requests_by_model[name] += 1
            tokens_by_model[name] += request.output_tokens
            sessions.add(request.session_id)

        return ClaudeCodeSummary(
            first_day=first_day,
            last_day=today,
            lines_per_day=[lines_by_day[first_day + timedelta(days=offset)] for offset in range(self._window_days)],
            languages=[LanguageShare(language, lines) for language, lines in lines_by_language.most_common()],
            models=[
                ModelShare(model, requests, tokens_by_model[model])
                for model, requests in requests_by_model.most_common()
            ],
            sessions=len(sessions - {""}),
            output_tokens=sum(tokens_by_model.values()),
            files_touched=len(files),
            lifetime=lifetime,
        )
