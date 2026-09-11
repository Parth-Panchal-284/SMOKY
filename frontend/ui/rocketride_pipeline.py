"""RocketRide six-stage operation pipeline."""

from __future__ import annotations

from models.run_state import PIPELINE_ORDER, RunState

STAGES = (
    ("intake", "1", "INTAKE"),
    ("diagnose", "2", "DIAGNOSE"),
    ("chief", "3", "CHIEF"),
    ("repair", "4", "REPAIR"),
    ("verify", "5", "VERIFY"),
    ("discharge", "6", "DISCHARGE"),
)

CHECK = """<svg viewBox="0 0 12 12" width="12" height="12"><path d="M2 6.2 4.6 9 10 3.2" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def _status(stage: str, current: str) -> str:
    ci = PIPELINE_ORDER.index(current) if current in PIPELINE_ORDER else 1
    si = PIPELINE_ORDER.index(stage)
    if si < ci:
        return "complete"
    if si == ci:
        return "active"
    return "pending"


def _subtitle(stage: str, kind: str, state: RunState) -> str:
    if kind == "pending":
        return "Pending"
    if stage == "intake":
        return "Complete"
    if stage == "diagnose":
        if kind == "complete":
            return "Complete"
        n = state.specialists_running()
        return f"{n} agents running" if n else "Scanning"
    if stage == "chief":
        return "Reviewing" if kind == "active" else "Complete"
    if stage == "repair":
        return "Applying" if kind == "active" else "Complete"
    if stage == "verify":
        return "Checking" if kind == "active" else "Complete"
    if stage == "discharge":
        return "Complete" if kind == "complete" else "Discharging"
    return ""


def render_pipeline(state: RunState) -> str:
    current = state.pipeline_stage if state.pipeline_stage in PIPELINE_ORDER else "diagnose"
    ci = PIPELINE_ORDER.index(current)
    # Fill reaches the active node. 6 nodes → 0..5 spans, plus complete offset.
    fill_pct = (ci / (len(STAGES) - 1)) * 100
    if current == "discharge" and not state.live:
        fill_pct = 100
        # last node complete rather than active
    nodes = []
    for key, num, name in STAGES:
        kind = _status(key, current)
        if key == "discharge" and current == "discharge" and not state.live:
            kind = "complete"
        if key == "intake" and current == "intake":
            kind = "active"
        inner = CHECK if kind == "complete" else num
        sub = _subtitle(key, kind, state)
        nodes.append(
            f"""
            <div class="pipe-node {kind}">
              <div class="pipe-dot">{inner}</div>
              <div class="pipe-name">{name}</div>
              <div class="pipe-sub">{sub}</div>
            </div>
            """
        )
    return f"""
<section class="card pipeline">
  <div class="pipeline-head">ROCKETRIDE // OPERATION PIPELINE</div>
  <div class="pipe-track">
    <div class="pipe-fill" style="width:{fill_pct:.1f}%"></div>
    {''.join(nodes)}
  </div>
</section>
"""
