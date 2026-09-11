"""Operating Room title row, identity chip, metrics, orchestrating pill."""

from __future__ import annotations

from html import escape

from models.run_state import RunState

PEOPLE = """
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <circle cx="9" cy="8" r="3" stroke="currentColor" stroke-width="1.8"/>
  <circle cx="16.5" cy="9" r="2.4" stroke="currentColor" stroke-width="1.8"/>
  <path d="M3.5 18c.7-2.6 3-4.2 5.5-4.2S14 15.4 14.7 18M14 18c.4-1.5 1.6-2.8 3.3-2.8 1.5 0 2.7 1 3.2 2.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
</svg>
"""

SPIN = """
<svg class="spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2.2" opacity=".25"/>
  <path d="M20 12a8 8 0 0 0-8-8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
</svg>
"""

ROCKET = """
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
  <path d="M12 3c3 2 5 6 5 9-1.2.4-2.5.6-5 .6s-3.8-.2-5-.6c0-3 2-7 5-9Z" fill="currentColor"/>
  <path d="M9.6 13.6c-.8 1.6-1.2 3-1.2 4.1 1.3-.3 2.4-.5 3.6-.5s2.3.2 3.6.5c0-1.1-.4-2.5-1.2-4.1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
</svg>
"""

MINI_ECG = """
<svg class="mini-ecg" viewBox="0 0 54 18" fill="none" aria-hidden="true">
  <path d="M0 9 H10 L14 9 L18 3 L22 15 L26 9 H34 L37 5 L41 13 L44 9 H54"
        stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def render_operation_header(state: RunState) -> str:
    n = state.specialists_running()
    if n == 0:
        line = "Specialists complete — Chief pathway"
        if state.pipeline_stage == "discharge":
            line = "Operation complete"
        elif state.pipeline_stage in ("chief", "repair", "verify"):
            line = "Specialists complete — pipeline advancing"
    elif n == 1:
        line = "1 specialist running"
    else:
        line = f"{n} specialists running in parallel"

    orch = escape(state.rocketride_label)
    rows = f"{state.dataset_rows:,}"
    crit_class = "pill pill-red" if state.patient_health == "CRITICAL" else "pill pill-green"
    spin = SPIN if state.live and n > 0 else ""

    return f"""
<div class="title-block">
  <div class="title-left">
    <div class="title-icon">{PEOPLE}</div>
    <div class="title-copy">
      <h1>OPERATING ROOM</h1>
      <div class="title-meta">
        <div class="specialists-line">
          <span class="dot"></span>
          {escape(line)}
        </div>
        <div class="identity">
          <span class="pid">{escape(state.patient_name)}</span>
          <span class="file">{escape(state.patient_file)}</span>
          <span class="{crit_class}">{escape(state.patient_health)}</span>
        </div>
      </div>
    </div>
  </div>
  <div class="title-right">
    <div class="orch">{spin}{orch}</div>
    <div class="metrics">
      <div class="metric">
        <div class="val">{rows}</div>
        <div class="lbl">ROWS</div>
      </div>
      <div class="metric">
        <div class="val">{state.dataset_cols}</div>
        <div class="lbl">COLUMNS</div>
      </div>
      <div class="metric">
        <div class="val">{escape(state.dataset_size)}</div>
        <div class="lbl">SIZE</div>
      </div>
    </div>
  </div>
</div>
<div class="rr-badge">
  <div class="rr-left">{ROCKET} RocketRide Pipeline Active</div>
  {MINI_ECG}
</div>
"""
