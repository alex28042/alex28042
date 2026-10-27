from __future__ import annotations

import re
from typing import Optional, Protocol

from .line_counting import line_count, lines_added
from .records import Contribution


class ContributionExtractor(Protocol):
    tool_name: str

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        ...


class EditExtractor:
    def __init__(self) -> None:
        self.tool_name = "Edit"

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        tool_input = tool_use.get("input") or {}
        new_text = tool_input.get("new_string")
        if not isinstance(new_text, str):
            return None
        old_text = tool_input.get("old_string") or ""
        return Contribution(tool_use["id"], timestamp, tool_input.get("file_path"), lines_added(old_text, new_text))


class WriteExtractor:
    def __init__(self) -> None:
        self.tool_name = "Write"

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        tool_input = tool_use.get("input") or {}
        content = tool_input.get("content")
        if not isinstance(content, str):
            return None
        return Contribution(tool_use["id"], timestamp, tool_input.get("file_path"), line_count(content))


class MultiEditExtractor:
    def __init__(self) -> None:
        self.tool_name = "MultiEdit"

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        tool_input = tool_use.get("input") or {}
        edits = tool_input.get("edits")
        if not isinstance(edits, list) or not edits:
            return None
        added = sum(
            lines_added(edit.get("old_string") or "", edit.get("new_string") or "")
            for edit in edits
            if isinstance(edit, dict)
        )
        return Contribution(tool_use["id"], timestamp, tool_input.get("file_path"), added)


class NotebookEditExtractor:
    def __init__(self) -> None:
        self.tool_name = "NotebookEdit"

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        tool_input = tool_use.get("input") or {}
        if tool_input.get("edit_mode") == "delete":
            return None
        source = tool_input.get("new_source")
        if not isinstance(source, str):
            return None
        return Contribution(tool_use["id"], timestamp, tool_input.get("notebook_path"), line_count(source))


HEREDOC_HEADER = re.compile(r"""<<-?\s*(['"]?)([A-Za-z_][A-Za-z0-9_]*)\1""")
REDIRECT_TARGET = re.compile(r""">\s*("[^"]+"|'[^']+'|\S+)""")
TEE_TARGET = re.compile(r"""\btee\b\s+(-a\s+)?("[^"]+"|'[^']+'|\S+)""")


class BashHeredocExtractor:
    def __init__(self) -> None:
        self.tool_name = "Bash"

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        command = (tool_use.get("input") or {}).get("command")
        if not isinstance(command, str):
            return None

        lines = command.split("\n")
        added = 0
        first_target: Optional[str] = None
        index = 0
        while index < len(lines):
            header = lines[index]
            index += 1
            delimiter = heredoc_delimiter(header)
            target = heredoc_target(header)
            if delimiter is None or target is None:
                continue
            body = []
            while index < len(lines) and lines[index].strip() != delimiter:
                body.append(lines[index])
                index += 1
            index += 1
            added += line_count("\n".join(body))
            first_target = first_target or target

        if added == 0:
            return None
        return Contribution(tool_use["id"], timestamp, first_target, added)


def heredoc_delimiter(header: str) -> Optional[str]:
    match = HEREDOC_HEADER.search(header)
    return match.group(2) if match else None


def heredoc_target(header: str) -> Optional[str]:
    redirect = REDIRECT_TARGET.search(header)
    if redirect and not redirect.group(1).startswith("/dev/"):
        return redirect.group(1).strip("\"'")
    tee = TEE_TARGET.search(header)
    if tee:
        return tee.group(2).strip("\"'")
    return None


class ExtractorRegistry:
    def __init__(self, extractors: list[ContributionExtractor]) -> None:
        self._by_tool = {extractor.tool_name: extractor for extractor in extractors}

    def extract(self, tool_use: dict, timestamp: str) -> Optional[Contribution]:
        extractor = self._by_tool.get(tool_use.get("name", ""))
        if extractor is None or not tool_use.get("id"):
            return None
        return extractor.extract(tool_use, timestamp)


def default_extractor_registry() -> ExtractorRegistry:
    return ExtractorRegistry([
        EditExtractor(),
        WriteExtractor(),
        MultiEditExtractor(),
        NotebookEditExtractor(),
        BashHeredocExtractor(),
    ])
