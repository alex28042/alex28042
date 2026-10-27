from __future__ import annotations

import json
import os
import time
from dataclasses import astuple
from pathlib import Path
from typing import Iterator, Optional

from .extractors import ExtractorRegistry
from .records import Contribution, ModelRequest, TranscriptRecords

ASSISTANT_MARKER = '"type":"assistant"'
CACHE_VERSION = 1
SYNTHETIC_MODEL = "<synthetic>"


class TranscriptLineParser:
    def __init__(self, extractors: ExtractorRegistry) -> None:
        self._extractors = extractors

    def parse(self, line: str) -> tuple[list[Contribution], Optional[ModelRequest]]:
        if ASSISTANT_MARKER not in line:
            return [], None
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return [], None
        message = entry.get("message")
        timestamp = entry.get("timestamp")
        if entry.get("type") != "assistant" or not isinstance(message, dict) or not timestamp:
            return [], None

        contributions = []
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                contribution = self._extractors.extract(block, timestamp)
                if contribution is not None:
                    contributions.append(contribution)
        return contributions, model_request(entry, message, timestamp)


def model_request(entry: dict, message: dict, timestamp: str) -> Optional[ModelRequest]:
    model = message.get("model")
    usage = message.get("usage")
    key = (entry.get("requestId") or "") + ":" + (message.get("id") or "")
    if not model or model == SYNTHETIC_MODEL or not isinstance(usage, dict) or key == ":":
        return None
    return ModelRequest(key, timestamp, model, int(usage.get("output_tokens") or 0), entry.get("sessionId") or "")


class TranscriptRepository:
    def __init__(self, projects_dir: Path, cache_file: Path, parser: TranscriptLineParser) -> None:
        self._projects_dir = projects_dir
        self._cache_file = cache_file
        self._parser = parser

    def load(self, window_days: int) -> TranscriptRecords:
        cache = self._read_cache()
        oldest_mtime = time.time() - (window_days + 1) * 86400
        fresh_cache = {}
        for path in self._transcript_files():
            stat = path.stat()
            if stat.st_mtime < oldest_mtime:
                continue
            key = str(path)
            cached = cache.get(key)
            if cached and cached["size"] == stat.st_size and cached["mtime"] == stat.st_mtime:
                fresh_cache[key] = cached
            else:
                fresh_cache[key] = self._scan(path, stat)
        self._write_cache(fresh_cache)
        return merge(fresh_cache.values())

    def _transcript_files(self) -> Iterator[Path]:
        for root, _, files in os.walk(self._projects_dir):
            for name in files:
                if name.endswith(".jsonl"):
                    yield Path(root) / name

    def _scan(self, path: Path, stat: os.stat_result) -> dict:
        contributions = []
        requests = {}
        with path.open(encoding="utf-8", errors="replace") as transcript:
            for line in transcript:
                found, request = self._parser.parse(line)
                contributions.extend(astuple(contribution) for contribution in found)
                if request is not None:
                    previous = requests.get(request.key)
                    if previous is None or request.output_tokens > previous[3]:
                        requests[request.key] = astuple(request)
        return {
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "contributions": contributions,
            "requests": list(requests.values()),
        }

    def _read_cache(self) -> dict:
        try:
            content = json.loads(self._cache_file.read_text())
        except (OSError, json.JSONDecodeError):
            return {}
        return content.get("files", {}) if content.get("version") == CACHE_VERSION else {}

    def _write_cache(self, files: dict) -> None:
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._cache_file.with_suffix(".tmp")
        temporary.write_text(json.dumps({"version": CACHE_VERSION, "files": files}))
        temporary.replace(self._cache_file)


def merge(scanned_files) -> TranscriptRecords:
    contributions: dict[str, Contribution] = {}
    requests: dict[str, ModelRequest] = {}
    for scanned in scanned_files:
        for row in scanned["contributions"]:
            contributions.setdefault(row[0], Contribution(*row))
        for row in scanned["requests"]:
            request = ModelRequest(*row)
            previous = requests.get(request.key)
            if previous is None or request.output_tokens > previous.output_tokens:
                requests[request.key] = request
    return TranscriptRecords(list(contributions.values()), list(requests.values()))
