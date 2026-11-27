from __future__ import annotations

from xml.sax.saxutils import escape, quoteattr

from .theme import STYLE


def document(width: int, height: int, title: str, body: list[str]) -> str:
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label={quoteattr(title)}>',
        f"<title>{escape(title)}</title>",
        f"<style>{STYLE}</style>",
        f'<rect class="card" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12"/>',
        *body,
        "</svg>",
        "",
    ])


def text(x: float, y: float, content: str, css_class: str, anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{css_class}" text-anchor="{anchor}">{escape(content)}</text>'


def rich_text(x: float, y: float, parts: list[tuple[str, str]], css_class: str = "") -> str:
    spans = "".join(span(content, part_class) for content, part_class in parts)
    return f'<text x="{x:.1f}" y="{y:.1f}"{class_attribute(css_class)}>{spans}</text>'


def span(content: str, css_class: str) -> str:
    return f'<tspan class="{css_class}">{escape(content)}</tspan>' if css_class else escape(content)


def rect(x: float, y: float, width: float, height: float, css_class: str = "", radius: float = 0, style: str = "") -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{radius:.1f}"'
        f"{class_attribute(css_class)}{style_attribute(style)}/>"
    )


def circle(x: float, y: float, radius: float, css_class: str = "", style: str = "") -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}"{class_attribute(css_class)}{style_attribute(style)}/>'


def group(elements: list[str], css_class: str = "", style: str = "", clip: str = "") -> str:
    clip_attribute = f' clip-path="url(#{clip})"' if clip else ""
    return f"<g{class_attribute(css_class)}{style_attribute(style)}{clip_attribute}>{''.join(elements)}</g>"


def clip_path(identifier: str, shape: str) -> str:
    return f'<clipPath id="{identifier}">{shape}</clipPath>'


def class_attribute(css_class: str) -> str:
    return f' class="{css_class}"' if css_class else ""


def style_attribute(style: str) -> str:
    return f' style="{style}"' if style else ""
