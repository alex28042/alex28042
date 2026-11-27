from __future__ import annotations

LANGUAGE_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Java": "#b07219",
    "Kotlin": "#a97bff",
    "Swift": "#f05138",
    "Rust": "#dea584",
    "Python": "#3572a5",
    "Go": "#00add8",
    "Dart": "#00b4ab",
    "Solidity": "#aa6746",
    "Ruby": "#701516",
    "PHP": "#4f5d95",
    "C": "#555555",
    "C++": "#f34b7d",
    "Objective-C": "#438eff",
    "C#": "#178600",
    "SQL": "#e38c00",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "Astro": "#ff5a03",
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
    "CSS": "#663399",
    "Liquid": "#67b8de",
    "Lua": "#000080",
    "Dockerfile": "#384d54",
    "Makefile": "#427819",
}
FALLBACK_COLOR = "#8b949e"


def language_color(language: str) -> str:
    return LANGUAGE_COLORS.get(language, FALLBACK_COLOR)
