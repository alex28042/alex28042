from __future__ import annotations

from pathlib import PurePosixPath
from typing import Optional

LANGUAGE_BY_EXTENSION = {
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".swift": "Swift",
    ".rs": "Rust",
    ".py": "Python",
    ".ipynb": "Python",
    ".go": "Go",
    ".dart": "Dart",
    ".sol": "Solidity",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C++",
    ".m": "Objective-C",
    ".cs": "C#",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".html": "HTML",
    ".astro": "Astro",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".css": "CSS",
    ".scss": "CSS",
    ".liquid": "Liquid",
    ".lua": "Lua",
    ".gradle": "Kotlin",
}

LANGUAGE_BY_FILE_NAME = {
    "Dockerfile": "Dockerfile",
    "Containerfile": "Dockerfile",
    "Makefile": "Makefile",
}


class LanguageClassifier:
    def __init__(self, language_by_extension: dict[str, str], language_by_file_name: dict[str, str]) -> None:
        self._language_by_extension = language_by_extension
        self._language_by_file_name = language_by_file_name

    def classify(self, file_path: Optional[str]) -> Optional[str]:
        if not file_path:
            return None
        path = PurePosixPath(file_path)
        if path.name in self._language_by_file_name:
            return self._language_by_file_name[path.name]
        return self._language_by_extension.get(path.suffix.lower())


def default_language_classifier() -> LanguageClassifier:
    return LanguageClassifier(LANGUAGE_BY_EXTENSION, LANGUAGE_BY_FILE_NAME)
