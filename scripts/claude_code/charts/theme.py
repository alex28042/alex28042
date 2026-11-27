from __future__ import annotations

FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
HEAT_LEVELS = 4

STYLE = f"""
svg {{
  --surface: #ffffff; --border: #d1d9e0; --ink: #1f2328; --ink-2: #59636e; --edge: rgba(31, 35, 40, 0.05);
  --heat-0: #eff2f5; --heat-1: #f7d9cc; --heat-2: #eeac90; --heat-3: #dd7a53; --heat-4: #b3502b;
  --other: #c8d0d8;
  font-family: {FONT};
}}
@media (prefers-color-scheme: dark) {{
  svg {{
    --surface: #0d1117; --border: #3d444d; --ink: #f0f6fc; --ink-2: #9198a1; --edge: rgba(240, 246, 252, 0.05);
    --heat-0: #151b23; --heat-1: #4a2417; --heat-2: #7f3920; --heat-3: #c2582f; --heat-4: #f08b62;
    --other: #3d444d;
  }}
}}
.card {{ fill: var(--surface); stroke: var(--border); }}
.title {{ fill: var(--ink); font-size: 18px; font-weight: 600; }}
.summary {{ fill: var(--ink-2); font-size: 13px; }}
.strong {{ fill: var(--ink); font-weight: 600; }}
.heading {{ fill: var(--ink); font-size: 14px; font-weight: 600; }}
.note {{ fill: var(--ink-2); font-size: 12px; }}
.axis {{ fill: var(--ink-2); font-size: 11px; }}
.name {{ fill: var(--ink); font-size: 12px; font-weight: 600; }}
.share {{ fill: var(--ink-2); font-size: 12px; font-weight: 400; font-variant-numeric: tabular-nums; }}
.cell {{ stroke: var(--edge); stroke-width: 1; }}
.heat-0 {{ fill: var(--heat-0); }} .heat-1 {{ fill: var(--heat-1); }} .heat-2 {{ fill: var(--heat-2); }}
.heat-3 {{ fill: var(--heat-3); }} .heat-4 {{ fill: var(--heat-4); }} .other {{ fill: var(--other); }}
.week {{ animation: appear 0.5s ease-out both; }}
.segment {{ transform-box: fill-box; transform-origin: left; animation: widen 0.9s cubic-bezier(.2,.8,.2,1) both; }}
@keyframes appear {{ from {{ opacity: 0; }} }}
@keyframes widen {{ from {{ transform: scaleX(0); }} }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
"""


def heat_class(level: int) -> str:
    return f"heat-{level}"
