from __future__ import annotations

import re
from pathlib import Path


class MissingSectionError(Exception):
    pass


class ReadmeFile:
    def __init__(self, path: Path) -> None:
        self._path = path

    def replace_section(self, name: str, content: str) -> bool:
        current = self._path.read_text()
        pattern = re.compile(rf"(<!-- {re.escape(name)}:start -->\n).*?(<!-- {re.escape(name)}:end -->)", re.DOTALL)
        if not pattern.search(current):
            raise MissingSectionError(f"README has no '{name}' markers")
        updated = pattern.sub(lambda match: match.group(1) + content + "\n" + match.group(2), current, count=1)
        if updated == current:
            return False
        self._path.write_text(updated)
        return True
