"""Top header: brand, sponsors, live clock."""

from __future__ import annotations

from html import escape

from models.run_state import RunState

ECG = """
<svg class="brand-ecg" viewBox="0 0 54 18" fill="none" aria-hidden="true">
  <path d="M0 9 H10 L14 9 L18 3 L22 15 L26 9 H34 L37 5 L41 13 L44 9 H54"
        stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

ROCKET = """
<svg viewBox="0 0 24 24" width="14" height="14" fill="none" aria-hidden="true">
  <path d="M12 3c3 2 5 6 5 9-1.2.4-2.5.6-5 .6s-3.8-.2-5-.6c0-3 2-7 5-9Z" fill="currentColor" opacity=".9"/>
  <path d="M9.5 13.5c-.8 1.6-1.2 3-1.2 4.2 1.4-.4 2.5-.6 3.7-.6s2.3.2 3.7.6c0-1.2-.4-2.6-1.2-4.2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
  <circle cx="12" cy="9.2" r="1.2" fill="#EEF3FB"/>
</svg>
"""

HOTDATA = """
<svg viewBox="0 0 24 24" width="14" height="14" fill="none" aria-hidden="true">
  <rect x="5" y="4" width="14" height="16" rx="3" fill="currentColor"/>
  <path d="M9 9h6M9 12h6M9 15h4" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>
</svg>
"""


def render_header(state: RunState) -> str:
    date = escape(state.clock_date or "Fri, Sep 11, 2026")
    time = escape(state.clock_time or "12:26 PM")
    live = "LIVE OPERATION" if state.live else "OPERATION IDLE"
    return f"""
<header class="top-header">
  <div class="brand">
    <div class="brand-row">
      <span class="brand-name">DATA ER</span>
      {ECG}
    </div>
    <div class="brand-sub">OPERATIONAL CONSOLE</div>
  </div>
  <div class="powered">
    <div class="powered-rule"></div>
    <div class="powered-block">
      <div class="powered-label">Powered by</div>
      <div class="powered-row">
        <div class="sponsor">
          <span class="sponsor-mark rocket">{ROCKET}</span>
          RocketRide
        </div>
        <span class="sponsor-x">×</span>
        <div class="sponsor">
          <span class="sponsor-mark hotdata">{HOTDATA}</span>
          Hotdata
        </div>
      </div>
    </div>
  </div>
  <div class="clock">
    <div class="clock-date" id="clock-date">{date}</div>
    <div class="clock-time" id="clock-time">{time}</div>
    <div class="live-op"><span class="dot"></span>{live}</div>
  </div>
</header>
"""
