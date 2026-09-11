"""Left navigation. Operating Room is the only active screen."""

from __future__ import annotations

NAV = [
    ("01", "Triage", "Upload & Profile", "home", False),
    ("02", "Operating Room", "Live Diagnostics", "heart", True),
    ("03", "Chief Review", "Resolve & Approve", "users", False),
    ("04", "Results", "Report & Export", "report", False),
    ("05", "Telemetry", "Agent Performance", "chart", False),
]

ICONS = {
    "home": """<svg viewBox="0 0 24 24" fill="none"><path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-8.5Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>""",
    "heart": """<svg viewBox="0 0 24 24" fill="none"><path d="M3 12h3l2-5 3 10 2-5h3l2-4 2 4h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
    "users": """<svg viewBox="0 0 24 24" fill="none"><circle cx="9" cy="8" r="3" stroke="currentColor" stroke-width="1.7"/><circle cx="17" cy="9" r="2.4" stroke="currentColor" stroke-width="1.7"/><path d="M4 18c.6-2.4 2.6-4 5-4s4.4 1.6 5 4M14 18c.3-1.4 1.4-2.6 3-2.6 1.4 0 2.5.9 3 2.2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>""",
    "report": """<svg viewBox="0 0 24 24" fill="none"><rect x="5" y="3.5" width="14" height="17" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>""",
    "chart": """<svg viewBox="0 0 24 24" fill="none"><path d="M5 19V10M10 19V5M15 19v-7M20 19V8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>""",
}

FOOT_ECG = """
<svg viewBox="0 0 54 18" fill="none" aria-hidden="true">
  <path d="M0 9 H10 L14 9 L18 3 L22 15 L26 9 H34 L37 5 L41 13 L44 9 H54"
        stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def render_sidebar() -> str:
    items = []
    for num, title, sub, icon, active in NAV:
            cls = "nav-item active" if active else "nav-item"
            num_html = "" if active else f'<span class="num">{num}</span>'
            items.append(
                f"""
                <div class="{cls}" title="{title}">
                  {num_html}
                  <span class="nav-ico">{ICONS[icon]}</span>
                  <span class="nav-text">
                    <span class="nav-title">{title}</span>
                    <span class="nav-sub">{sub}</span>
                  </span>
                </div>
                """
            )
    return f"""
<aside class="sidebar">
  <nav class="nav">
    {''.join(items)}
  </nav>
  <div class="sidebar-foot">
    {FOOT_ECG}
    <p>SAME DATA.<br>SMARTER DECISIONS.</p>
  </div>
</aside>
"""
