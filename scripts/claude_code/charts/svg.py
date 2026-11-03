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


def line(x1: float, y1: float, x2: float, y2: float, css_class: str) -> str:
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{css_class}"/>'


def rect(x: float, y: float, width: float, height: float, css_class: str, radius: float = 0, style: str = "") -> str:
    style_attribute = f' style="{style}"' if style else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="{radius:.1f}" '
        f'class="{css_class}"{style_attribute}/>'
    )


def column(x: float, top: float, width: float, base: float, css_class: str, style: str = "") -> str:
    radius = min(4.0, width / 2, base - top)
    style_attribute = f' style="{style}"' if style else ""
    path = (
        f"M{x:.1f},{base:.1f} V{top + radius:.1f} Q{x:.1f},{top:.1f} {x + radius:.1f},{top:.1f} "
        f"H{x + width - radius:.1f} Q{x + width:.1f},{top:.1f} {x + width:.1f},{top + radius:.1f} V{base:.1f} Z"
    )
    return f'<path d="{path}" class="{css_class}"{style_attribute}/>'


def polyline(points: list[tuple[float, float]], css_class: str) -> str:
    return f'<path d="{point_commands(points)}" class="{css_class}" pathLength="1"/>'


def area(points: list[tuple[float, float]], base: float, css_class: str) -> str:
    closing = f" L{points[-1][0]:.1f},{base:.1f} L{points[0][0]:.1f},{base:.1f} Z"
    return f'<path d="{point_commands(points)}{closing}" class="{css_class}"/>'


def circle(x: float, y: float, radius: float, css_class: str) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" class="{css_class}"/>'


def point_commands(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}" for index, (x, y) in enumerate(points))
