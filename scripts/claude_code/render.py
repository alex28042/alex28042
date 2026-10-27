from __future__ import annotations

from datetime import date
from urllib.parse import quote

from .stats import ClaudeCodeSummary

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
BLOCKS = " ▁▂▃▄▅▆▇█"
BAR_WIDTH = 40
CHART_HEIGHT = 6
MAX_LANGUAGES = 8
MAX_MODELS = 5
PALETTE = ["6e40c9", "8957e5", "a371f7", "d2a8ff"]


class ClaudeCodeSectionRenderer:
    def render(self, summary: ClaudeCodeSummary) -> str:
        return "\n".join([
            "### Shipping with Claude Code",
            "",
            "<div align=\"center\">",
            "",
            self._headline_badges(summary),
            "",
            "```",
            self._daily_chart(summary),
            "```",
            "",
            "```",
            self._languages_chart(summary),
            "```",
            "",
            "```",
            self._models_chart(summary),
            "```",
            "",
            self._secondary_badges(summary),
            "",
            f"<sub>Counted from my local Claude Code sessions: every line Claude writes to a file through Edit, Write "
            f"or a heredoc. Rolling 30 days, refreshed every hour. Last update {format_full_day(summary.last_day)}.</sub>",
            "",
            "</div>",
        ])

    def _headline_badges(self, summary: ClaudeCodeSummary) -> str:
        badges = [badge("Lines · last 30 days", compact(summary.lines_total), PALETTE[0], "claude")]
        if summary.lifetime is not None:
            since = f"{MONTHS[summary.lifetime.since.month - 1]} {summary.lifetime.since.year}"
            badges.append(badge(f"Since {since}", f"{compact(summary.lifetime.lines_added)} lines", PALETTE[1], "anthropic"))
        badges.append(badge("Active days", f"{summary.active_days}/{len(summary.lines_per_day)}", PALETTE[2]))
        badges.append(badge("Streak", plural(summary.current_streak, "day"), PALETTE[3], dark_text=True))
        return "\n".join(badges)

    def _secondary_badges(self, summary: ClaudeCodeSummary) -> str:
        top_model = summary.models[0].model if summary.models else "—"
        return "\n".join([
            badge("Main model", top_model, PALETTE[0], "claude", style="flat-square"),
            badge("Sessions", str(summary.sessions), PALETTE[1], style="flat-square"),
            badge("Files touched", compact(summary.files_touched), PALETTE[2], style="flat-square"),
            badge("Output tokens", compact(summary.output_tokens), PALETTE[3], "anthropic", style="flat-square", dark_text=True),
        ])

    def _daily_chart(self, summary: ClaudeCodeSummary) -> str:
        values = summary.lines_per_day
        peak = max(values) or 1
        levels = [round(value / peak * CHART_HEIGHT * 8) for value in values]
        levels = [max(level, 1) if value > 0 else 0 for level, value in zip(levels, values)]
        axis_width = len(compact(peak))

        rows = [f" Lines written per day · {format_day(summary.first_day)} → {format_day(summary.last_day)}", ""]
        for row in range(CHART_HEIGHT, 0, -1):
            floor = (row - 1) * 8
            cells = " ".join(BLOCKS[min(max(level - floor, 0), 8)] for level in levels)
            label = compact(peak) if row == CHART_HEIGHT else ""
            rows.append(f" {label.rjust(axis_width)} │ {cells}".rstrip())
        rows.append(f" {'0'.rjust(axis_width)} └─" + "──" * len(values))
        return "\n".join(rows)

    def _languages_chart(self, summary: ClaudeCodeSummary) -> str:
        shares = [(share.language, share.lines) for share in summary.languages]
        visible = shares[:MAX_LANGUAGES]
        rest = sum(lines for _, lines in shares[MAX_LANGUAGES:])
        if rest:
            visible.append(("Other", rest))
        total = sum(lines for _, lines in shares) or 1
        peak = max((lines for _, lines in visible), default=1)

        rows = [" Languages · last 30 days", ""]
        for language, lines in visible:
            rows.append(
                f" {language:<13}{bar(lines / peak)} {compact(lines).rjust(6)} lines  {percent(lines / total).rjust(6)}"
            )
        return "\n".join(rows)

    def _models_chart(self, summary: ClaudeCodeSummary) -> str:
        visible = summary.models[:MAX_MODELS]
        total = sum(model.requests for model in summary.models) or 1
        peak = max((model.requests for model in visible), default=1)

        rows = [" Models · last 30 days", ""]
        for model in visible:
            rows.append(
                f" {model.model:<13}{bar(model.requests / peak)} {compact(model.requests).rjust(6)} calls  "
                f"{percent(model.requests / total).rjust(6)}"
            )
        return "\n".join(rows)


def badge(label: str, message: str, color: str, logo: str = "", dark_text: bool = False, style: str = "for-the-badge") -> str:
    url = f"https://img.shields.io/badge/{badge_text(label)}-{badge_text(message)}-{color}?style={style}"
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
    return f"{ratio * 100:.1f}%"


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def format_day(day: date) -> str:
    return f"{MONTHS[day.month - 1]} {day.day}"


def format_full_day(day: date) -> str:
    return f"{format_day(day)}, {day.year}"
