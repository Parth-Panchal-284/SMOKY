"""Live operation feed with client-side category filters."""

from __future__ import annotations

from html import escape

from models.run_state import RunState

FILTERS = (
    ("all", "All"),
    ("agents", "Agents"),
    ("hotdata", "Hotdata"),
    ("repairs", "Repairs"),
    ("system", "System"),
)

ICONS = {
    "SCHEMA_MD": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><rect x="3" y="2" width="10" height="12" rx="1.5" stroke="currentColor" stroke-width="1.4"/><path d="M5.5 5.5h5M5.5 8h5M5.5 10.5h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>""",
    "ANOMALY_MD": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><path d="M8 2.5 14.5 14h-13L8 2.5Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="M8 6.5v4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><circle cx="8" cy="12.2" r="0.7" fill="currentColor"/></svg>""",
    "DUPLICATE_MD": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><circle cx="6.2" cy="8" r="3" stroke="currentColor" stroke-width="1.3"/><circle cx="9.8" cy="8" r="3" stroke="currentColor" stroke-width="1.3"/></svg>""",
    "HOTDATA": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><ellipse cx="8" cy="4.5" rx="4.5" ry="2" stroke="currentColor" stroke-width="1.3"/><path d="M3.5 4.5v7c0 1.1 2 2 4.5 2s4.5-.9 4.5-2v-7" stroke="currentColor" stroke-width="1.3"/><path d="M3.5 8c0 1.1 2 2 4.5 2s4.5-.9 4.5-2" stroke="currentColor" stroke-width="1.3"/></svg>""",
    "ROCKETRIDE": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><path d="M8 2c2 1.4 3.2 4 3.2 6-1 .3-2 .4-3.2.4S5.8 8.3 4.8 8C4.8 6 6 3.4 8 2Z" fill="currentColor"/><path d="M6.4 9.2c-.5 1.1-.8 2-.8 2.8.9-.2 1.6-.3 2.4-.3s1.5.1 2.4.3c0-.8-.3-1.7-.8-2.8" stroke="currentColor" stroke-width="1.1" stroke-linecap="round"/></svg>""",
    "CHIEF": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><circle cx="6" cy="6" r="2.2" stroke="currentColor" stroke-width="1.3"/><circle cx="11" cy="6.5" r="1.8" stroke="currentColor" stroke-width="1.3"/><path d="M2.8 13c.4-1.7 1.8-2.8 3.4-2.8s3 1.1 3.4 2.8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>""",
    "REPAIR": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><path d="M3 11.5 11.5 3l1.5 1.5L4.5 13 3 11.5Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M10 4.5 12 6.5" stroke="currentColor" stroke-width="1.3"/></svg>""",
    "VERIFY": """<svg viewBox="0 0 16 16" width="14" height="14" fill="none"><circle cx="8" cy="8" r="5.2" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 8.2 7.2 10l3.4-4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}


def render_event_feed(state: RunState) -> str:
    chips = []
    for key, label in FILTERS:
        active = " active" if key == "all" else ""
        chips.append(
            f'<button class="filter{active}" type="button" data-filter="{key}">{label}</button>'
        )

    rows = []
    for item in state.event_feed:
        icon = ICONS.get(item.source, ICONS["ROCKETRIDE"])
        rows.append(
            f"""
            <div class="feed-row" data-cat="{escape(item.category)}">
              <span class="feed-ts">{escape(item.timestamp)}</span>
              <span class="feed-ico src-{escape(item.source)}">{icon}</span>
              <span class="feed-src src-{escape(item.source)}">{escape(item.source)}</span>
              <span class="feed-msg">{escape(item.message)}</span>
            </div>
            """
        )

    empty = ""
    if not rows:
        empty = '<div class="feed-row"><span class="feed-msg">Awaiting operation events…</span></div>'

    return f"""
<section class="card feed">
  <div class="feed-head">
    <h2>LIVE OPERATION FEED</h2>
    <div class="filters">{''.join(chips)}</div>
  </div>
  <div class="feed-list" id="feed-list">
    {''.join(rows) or empty}
  </div>
</section>
"""
