"""Patient vitals panel: health bars, diagnosis tiles, ECG, condition."""

from __future__ import annotations

from html import escape

from models.run_state import RunState

HEART = """
<svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true">
  <path d="M3 12h3l2-5 3 10 2-5h3l2-4 2 4h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

WARN = """
<svg viewBox="0 0 24 24" width="14" height="14" fill="none" aria-hidden="true">
  <path d="M12 3.5 22 20H2L12 3.5Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>
  <path d="M12 9v5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
  <circle cx="12" cy="16.5" r="0.9" fill="currentColor"/>
</svg>
"""

ECG = """
<svg viewBox="0 0 120 48" fill="none" aria-hidden="true">
  <path class="ecg-line" d="M0 24 H18 L24 24 L30 8 L38 40 L46 24 H58 L64 14 L70 34 L76 24 H120"/>
  <path class="ecg-scan" d="M0 24 H18 L24 24 L30 8 L38 40 L46 24 H58 L64 14 L70 34 L76 24 H120"/>
</svg>
"""

BARS = (
    ("schema_integrity", "Schema Integrity"),
    ("validity", "Validity"),
    ("uniqueness", "Uniqueness"),
    ("completeness", "Completeness"),
)


def render_patient_vitals(state: RunState) -> str:
    rows = []
    for key, label in BARS:
        val = int(state.health_metrics.get(key, 0))
        rows.append(
            f"""
            <div class="bar-row">
              <div class="bar-name">{label}</div>
              <div class="bar-val">{val}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{val}%"></div></div>
            </div>
            """
        )
    d = state.diagnoses
    cond_cls = "condition" if state.patient_health == "CRITICAL" else "condition stable"
    live = "LIVE" if state.live else "IDLE"
    return f"""
<aside class="card vitals">
  <div class="vitals-head">
    <div class="vitals-title">{HEART} PATIENT VITALS</div>
    <div class="live-mini"><span class="dot"></span>{live}</div>
  </div>
  <div class="bars">
    {''.join(rows)}
  </div>
  <div class="vital-tiles">
    <div class="vtile diag"><div class="tl">DIAGNOSES</div><div class="tv">{d['total']}</div></div>
    <div class="vtile crit"><div class="tl">CRITICAL</div><div class="tv">{d['critical']}</div></div>
    <div class="vtile rev"><div class="tl">REVIEW</div><div class="tv">{d['review']}</div></div>
    <div class="vtile fix"><div class="tl">AUTO-FIX</div><div class="tv">{d['auto_fix']}</div></div>
  </div>
  <div class="condition-row">
    <div class="ecg-panel">{ECG}</div>
    <div class="{cond_cls}">
      <div class="cl">{WARN} CONDITION</div>
      <div class="cv">{escape(state.patient_health)}</div>
      <div class="cn">{escape(state.condition_note)}</div>
    </div>
  </div>
</aside>
"""
