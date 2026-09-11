"""Specialist agent card with progress ring and Hotdata Bay stepper."""

from __future__ import annotations

import math
from html import escape

from models.run_state import AgentSnapshot
from ui.styles import GREEN, PURPLE

RING_R = 42
RING_C = 2 * math.pi * RING_R

GLYPHS = {
    "SCHEMA_MD": """<svg viewBox="0 0 24 24" fill="none"><rect x="6" y="4" width="12" height="16" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M9 9h6M9 12h6M9 15h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>""",
    "DUPLICATE_MD": """<svg viewBox="0 0 24 24" fill="none"><circle cx="10" cy="12" r="4.2" stroke="currentColor" stroke-width="1.7"/><circle cx="14.5" cy="12" r="4.2" stroke="currentColor" stroke-width="1.7"/></svg>""",
    "ANOMALY_MD": """<svg viewBox="0 0 24 24" fill="none"><path d="M4 16l4.5-4.5 3.2 3.2L20 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 6h5v5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>""",
}

SLOT = {
    "SCHEMA_MD": "agent-schema",
    "DUPLICATE_MD": "agent-duplicate",
    "ANOMALY_MD": "agent-anomaly",
}

CHECK = """<svg viewBox="0 0 12 12" width="9" height="9"><path d="M2 6.2 4.6 9 10 3.2" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def _ring(pct: int, color: str) -> str:
    offset = RING_C * (1 - max(0, min(pct, 100)) / 100.0)
    return f"""
    <div class="ring-wrap">
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <circle class="ring-track" cx="50" cy="50" r="{RING_R}"/>
        <circle class="ring-value" cx="50" cy="50" r="{RING_R}"
          stroke="{color}"
          stroke-dasharray="{RING_C:.2f}"
          stroke-dashoffset="{offset:.2f}"/>
      </svg>
      <div class="ring-label">{pct}%</div>
    </div>
    """


def _step(label: str, kind: str) -> str:
    inner = CHECK if kind == "complete" else ""
    return f"""
    <div class="step {kind}">
      <span class="node">{inner}</span>
      <span class="slabel">{label}</span>
    </div>
    """


def _stepper(agent: AgentSnapshot) -> str:
    create = "complete" if agent.create_state == "complete" else "pending"
    if agent.query_state == "active":
        query = "active"
    elif agent.query_state == "complete":
        query = "complete"
    else:
        query = "pending"
    destroy = "complete" if agent.destroy_state == "complete" else "pending"

    if destroy == "complete":
        width = 64
    elif query in ("active", "complete"):
        width = 32
    elif create == "complete":
        width = 6
    else:
        width = 0

    released = (
        '<div class="bay-released">Bay Released</div>' if agent.bay_released else ""
    )
    return f"""
    <div class="stepper">
      <div class="progress-line" style="width:{width}%"></div>
      {_step("Create", create)}
      {_step("Query", query)}
      {_step("Destroy", destroy)}
    </div>
    {released}
    """


def render_specialist_card(agent: AgentSnapshot) -> str:
    color = PURPLE if agent.accent == "purple" else GREEN
    glyph_cls = "purple" if agent.accent == "purple" else "green"
    slot = SLOT.get(agent.agent_id, "agent-schema")
    status = agent.status if agent.status else "PENDING"
    pill_cls = "pill pill-green"
    if status in ("PENDING",):
        pill_cls = "pill"
    bay_status = agent.bay_status if agent.bay_status else "PENDING"
    bay_pill = "pill pill-blue" if bay_status == "QUERYING" else "pill pill-green"
    if bay_status in ("PENDING", "READY"):
        bay_pill = "pill"
    task_cls = "task-box purple" if agent.accent == "purple" else "task-box"
    latency = f"{agent.latency_s:.1f}s"

    return f"""
<article class="card agent-card {slot}">
  <div class="agent-head">
    <div class="agent-id-row">
      <div class="agent-glyph {glyph_cls}">{GLYPHS.get(agent.agent_id, "")}</div>
      <div>
        <div class="agent-name">{escape(agent.agent_id)}</div>
        <div class="agent-sub">{escape(agent.subtitle)}</div>
      </div>
    </div>
    <span class="{pill_cls}">{escape(status)}</span>
  </div>
  <div class="agent-body">
    {_ring(agent.progress, color)}
    <div class="agent-stats">
      <div class="stat-row"><span class="k">Queries</span><span class="v">{agent.queries}</span></div>
      <div class="stat-row"><span class="k">Findings</span><span class="v">{agent.findings}</span></div>
      <div class="stat-row"><span class="k">Latency</span><span class="v">{latency}</span></div>
    </div>
  </div>
  <div class="{task_cls}">
    <div class="task-label">Current task</div>
    <div class="task-text">{escape(agent.current_task)}</div>
  </div>
  <div class="bay">
    <div class="bay-head">
      <div class="bay-left">
        <div class="bay-k">Hotdata Bay</div>
        <div class="bay-id">{escape(agent.bay_id)}</div>
      </div>
      <span class="{bay_pill}">{escape(bay_status)}</span>
    </div>
    {_stepper(agent)}
  </div>
</article>
"""
