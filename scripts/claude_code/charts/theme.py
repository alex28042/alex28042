from __future__ import annotations

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
CATEGORY_SLOTS = 5

STYLE = f"""
svg {{
  --surface: #ffffff; --border: #d0d7de; --grid: #eaeef2;
  --ink: #1f2328; --ink-2: #59636e; --ink-3: #818b98;
  --accent: #8957e5; --accent-soft: rgba(137, 87, 229, 0.16); --track: #eaeef2;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4; --other: #a3a29d;
  font-family: {FONT};
}}
@media (prefers-color-scheme: dark) {{
  svg {{
    --surface: #0d1117; --border: #30363d; --grid: #21262d;
    --ink: #f0f6fc; --ink-2: #9198a1; --ink-3: #656c76;
    --accent: #a371f7; --accent-soft: rgba(163, 113, 247, 0.18); --track: #21262d;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181; --other: #6b6a66;
  }}
}}
.card {{ fill: var(--surface); stroke: var(--border); }}
.title {{ fill: var(--ink); font-size: 16px; font-weight: 600; }}
.subtitle {{ fill: var(--ink-2); font-size: 12px; }}
.stat {{ fill: var(--ink); font-size: 22px; font-weight: 600; }}
.stat-label {{ fill: var(--ink-2); font-size: 11px; }}
.name {{ fill: var(--ink); font-size: 12px; }}
.value {{ fill: var(--ink-2); font-size: 12px; font-variant-numeric: tabular-nums; }}
.axis {{ fill: var(--ink-3); font-size: 10px; font-variant-numeric: tabular-nums; }}
.label {{ fill: var(--ink); font-size: 11px; font-weight: 600; }}
.panel {{ fill: var(--ink-2); font-size: 11px; font-weight: 600; }}
.grid {{ stroke: var(--grid); stroke-width: 1; }}
.divider {{ stroke: var(--border); stroke-width: 1; }}
.track {{ fill: var(--track); }}
.bar {{ fill: var(--accent); transform-box: fill-box; transform-origin: bottom;
  animation: grow 0.7s cubic-bezier(.2,.8,.2,1) both; }}
.hbar {{ fill: var(--accent); transform-box: fill-box; transform-origin: left;
  animation: widen 0.9s cubic-bezier(.2,.8,.2,1) both; }}
.segment {{ transform-box: fill-box; transform-origin: left; animation: widen 0.9s cubic-bezier(.2,.8,.2,1) both; }}
.area {{ fill: var(--accent-soft); animation: fade 1.2s ease-out both; }}
.trend {{ fill: none; stroke: var(--accent); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round;
  stroke-dasharray: 1; animation: draw 1.4s ease-out both; }}
.dot {{ fill: var(--accent); stroke: var(--surface); stroke-width: 2; }}
.s1 {{ fill: var(--s1); }} .s2 {{ fill: var(--s2); }} .s3 {{ fill: var(--s3); }}
.s4 {{ fill: var(--s4); }} .s5 {{ fill: var(--s5); }} .other {{ fill: var(--other); }}
@keyframes grow {{ from {{ transform: scaleY(0); }} }}
@keyframes widen {{ from {{ transform: scaleX(0); }} }}
@keyframes fade {{ from {{ opacity: 0; }} }}
@keyframes draw {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def category_class(rank: int) -> str:
    return f"s{rank + 1}" if rank < CATEGORY_SLOTS else "other"
