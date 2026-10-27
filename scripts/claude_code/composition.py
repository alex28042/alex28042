from __future__ import annotations

from datetime import date
from pathlib import Path

from .extractors import default_extractor_registry
from .languages import default_language_classifier
from .linebar import LineBarHistory
from .render import ClaudeCodeSectionRenderer
from .stats import ClaudeCodeStatsCalculator
from .transcripts import TranscriptLineParser, TranscriptRepository

WINDOW_DAYS = 30
SECTION_NAME = "claude-code"
HOME = Path.home()
PROJECTS_DIR = HOME / ".claude" / "projects"
CACHE_FILE = HOME / "Library" / "Caches" / "profile-readme" / "transcripts.json"
LINEBAR_STATS_FILE = HOME / "Library" / "Application Support" / "LineBar" / "stats.json"
CLONE_DIR = HOME / "Library" / "Application Support" / "profile-readme" / "alex28042"
REMOTE_URL = "https://github.com/alex28042/alex28042.git"
BRANCH = "main"


def render_claude_code_section(today: date) -> str:
    repository = TranscriptRepository(PROJECTS_DIR, CACHE_FILE, TranscriptLineParser(default_extractor_registry()))
    calculator = ClaudeCodeStatsCalculator(default_language_classifier(), WINDOW_DAYS)
    summary = calculator.summarize(
        repository.load(WINDOW_DAYS),
        today,
        LineBarHistory(LINEBAR_STATS_FILE).lifetime_lines(),
    )
    return ClaudeCodeSectionRenderer().render(summary)
