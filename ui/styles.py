"""Design tokens, Streamlit chrome-hide CSS, and the Operating Room stylesheet."""

from __future__ import annotations

# Color system
BG = "#F6F8FB"
CARD = "#FFFFFF"
SURFACE = "#F1F5F9"
BORDER = "#DCE5EF"
NAVY = "#17345F"
MUTED = "#64748B"
GREEN = "#16B875"
BLUE = "#2563EB"
RED = "#EF4444"
AMBER = "#F59E0B"
PURPLE = "#7C3AED"
MINT = "#ECFDF5"
TRACK = "#E6EEF6"

STREAMLIT_CHROME_CSS = """
<style>
  #MainMenu, footer, header[data-testid="stHeader"],
  .stDeployButton, [data-testid="stToolbar"],
  [data-testid="stDecoration"], [data-testid="stStatusWidget"],
  #stDecoration, [data-testid="stHeader"] {
    display: none !important;
    visibility: hidden !important;
  }
  .stApp, [data-testid="stAppViewContainer"] {
    background: #F6F8FB !important;
  }
  .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
  }
  div[data-testid="stVerticalBlock"] { gap: 0 !important; }
  section.main > div { padding-top: 0 !important; }
  iframe { border: none !important; }
  [data-testid="stIFrame"],
  div[data-testid="stCustomComponentV1"] {
    position: fixed !important;
    inset: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    max-width: 100vw !important;
    margin: 0 !important;
    z-index: 999;
  }
  [data-testid="stIFrame"] iframe,
  div[data-testid="stCustomComponentV1"] iframe {
    width: 100% !important;
    height: 100% !important;
  }
</style>
"""

APP_CSS = f"""
:root {{
  --bg: {BG};
  --card: {CARD};
  --surface: {SURFACE};
  --border: {BORDER};
  --navy: {NAVY};
  --muted: {MUTED};
  --green: {GREEN};
  --blue: {BLUE};
  --red: {RED};
  --amber: {AMBER};
  --purple: {PURPLE};
  --mint: {MINT};
  --track: {TRACK};
  --shadow: 0 1px 2px rgba(23, 52, 95, 0.04), 0 4px 14px rgba(23, 52, 95, 0.04);
  --radius: 16px;
}}

* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--navy);
  font-family: Inter, "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  height: 100%;
  overflow: hidden;
}}
body {{ min-width: 1100px; }}
.mono {{ font-family: "JetBrains Mono", ui-monospace, monospace; }}

.app {{
  display: grid;
  grid-template-columns: 214px 1fr;
  grid-template-rows: 64px 1fr;
  height: 100%;
  min-height: 100%;
  background: var(--bg);
  overflow: hidden;
}}

/* ========== HEADER ========== */
.top-header {{
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px 0 20px;
  background: #fff;
  border-bottom: 1px solid var(--border);
  gap: 20px;
}}
.brand {{
  display: flex;
  flex-direction: column;
  min-width: 168px;
}}
.brand-row {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.brand-name {{
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.04em;
  color: var(--navy);
  line-height: 1;
}}
.brand-ecg {{
  width: 54px;
  height: 18px;
  color: var(--green);
}}
.brand-sub {{
  margin-top: 4px;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.16em;
  color: var(--muted);
  text-transform: uppercase;
}}
.powered {{
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: center;
}}
.powered-rule {{
  width: 1px;
  height: 32px;
  background: var(--border);
}}
.powered-block {{
  display: flex;
  flex-direction: column;
  gap: 2px;
}}
.powered-label {{
  font-size: 10px;
  color: var(--muted);
  font-weight: 500;
}}
.powered-row {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.sponsor {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--navy);
  letter-spacing: -0.02em;
}}
.sponsor-mark {{
  width: 26px;
  height: 26px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}}
.sponsor-mark.rocket {{
  background: #EEF3FB;
  color: var(--navy);
}}
.sponsor-mark.hotdata {{
  background: var(--purple);
  color: #fff;
  border-radius: 8px;
}}
.sponsor-x {{
  color: var(--muted);
  font-size: 13px;
  font-weight: 500;
}}
.clock {{
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 150px;
}}
.clock-date {{
  font-size: 11px;
  color: var(--muted);
  font-weight: 500;
}}
.clock-time {{
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.15;
  color: var(--navy);
}}
.live-op {{
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--green);
  text-transform: uppercase;
}}
.dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 0 0 rgba(22, 184, 117, 0.55);
  animation: pulse 1.8s ease-out infinite;
}}
@keyframes pulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(22, 184, 117, 0.5); }}
  70% {{ box-shadow: 0 0 0 6px rgba(22, 184, 117, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(22, 184, 117, 0); }}
}}

/* ========== SIDEBAR ========== */
.sidebar {{
  grid-column: 1;
  grid-row: 2;
  display: flex;
  flex-direction: column;
  padding: 18px 14px 18px;
  background: var(--bg);
  border-right: 1px solid transparent;
}}
.nav {{
  display: flex;
  flex-direction: column;
  gap: 6px;
}}
.nav-item {{
  display: grid;
  grid-template-columns: 28px 22px 1fr;
  align-items: center;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 12px;
  color: var(--navy);
  cursor: default;
  user-select: none;
}}
.nav-item .num {{
  font-size: 11px;
  font-weight: 600;
  color: #94A3B8;
  font-variant-numeric: tabular-nums;
}}
.nav-item .nav-ico {{
  width: 18px;
  height: 18px;
  color: var(--navy);
  opacity: 0.85;
}}
.nav-item .nav-text {{
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}}
.nav-item .nav-title {{
  font-size: 13px;
  font-weight: 600;
}}
.nav-item .nav-sub {{
  font-size: 10px;
  color: var(--muted);
  font-weight: 500;
  margin-top: 2px;
}}
.nav-item.active {{
  background: var(--green);
  color: #fff;
  box-shadow: 0 8px 18px rgba(22, 184, 117, 0.28);
  margin: 8px 0;
  grid-template-columns: 22px 1fr;
  gap: 10px;
}}
.nav-item.active .num,
.nav-item.active .nav-sub,
.nav-item.active .nav-ico {{
  color: #fff;
  opacity: 1;
}}
.sidebar-foot {{
  margin-top: auto;
  padding: 12px 10px 4px;
  color: var(--navy);
}}
.sidebar-foot svg {{
  width: 36px;
  height: 16px;
  color: var(--green);
  margin-bottom: 8px;
}}
.sidebar-foot p {{
  margin: 0;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  line-height: 1.45;
}}

/* ========== MAIN ========== */
.main {{
  grid-column: 2;
  grid-row: 2;
  padding: 10px 16px 10px;
  overflow: auto;
  min-height: 0;
}}
.main-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 268px;
  grid-template-rows: auto auto auto auto;
  gap: 10px 12px;
  align-items: stretch;
  min-height: 0;
}}
.title-block {{
  grid-column: 1 / 4;
  grid-row: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}}
.title-left {{
  display: flex;
  align-items: flex-start;
  gap: 12px;
}}
.title-icon {{
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--mint);
  color: var(--green);
  display: grid;
  place-items: center;
  margin-top: 2px;
  flex-shrink: 0;
}}
.title-icon svg {{ width: 18px; height: 18px; }}
.title-copy h1 {{
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.035em;
  line-height: 1.05;
}}
.title-meta {{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 6px;
  flex-wrap: wrap;
}}
.specialists-line {{
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--muted);
  font-weight: 500;
}}
.identity {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.identity .pid {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 11px;
  font-weight: 600;
  color: var(--navy);
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 2px 8px;
  border-radius: 6px;
}}
.identity .file {{
  font-size: 12px;
  color: var(--muted);
}}
.pill {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 999px;
}}
.pill-red {{
  color: var(--red);
  background: #FEECEC;
}}
.pill-green {{
  color: var(--green);
  background: #E7F8EF;
}}
.pill-blue {{
  color: var(--blue);
  background: #E8F0FE;
}}
.title-right {{
  display: flex;
  align-items: center;
  gap: 18px;
}}
.orch {{
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--navy);
  box-shadow: var(--shadow);
  white-space: nowrap;
}}
.orch .spin {{
  width: 16px;
  height: 16px;
  color: var(--blue);
  animation: spin 1.4s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.metrics {{
  display: flex;
  align-items: stretch;
  gap: 0;
}}
.metric {{
  padding: 0 16px;
  text-align: right;
  white-space: nowrap;
  min-width: 78px;
}}
.metric + .metric {{
  border-left: 1px solid var(--border);
}}
.metric .val {{
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}}
.metric .lbl {{
  margin-top: 4px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--muted);
}}
.rr-badge {{
  grid-column: 4;
  grid-row: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 0 4px 2px;
  color: var(--navy);
  font-size: 12px;
  font-weight: 600;
  align-self: end;
}}
.rr-badge .rr-left {{
  display: flex;
  align-items: center;
  gap: 6px;
}}
.rr-badge svg {{ width: 16px; height: 16px; color: var(--navy); }}
.rr-badge .mini-ecg {{
  width: 48px;
  height: 16px;
  color: var(--purple);
}}

/* ========== CARDS ========== */
.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}}
.agent-card {{
  display: flex;
  flex-direction: column;
  padding: 14px 16px 12px;
  min-height: 292px;
  grid-row: 2;
}}
.agent-schema {{ grid-column: 1; }}
.agent-duplicate {{ grid-column: 2; }}
.agent-anomaly {{ grid-column: 3; }}

.agent-head {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}}
.agent-id-row {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.agent-glyph {{
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}}
.agent-glyph.green {{ background: #E7F8EF; color: var(--green); }}
.agent-glyph.purple {{ background: #F1E9FF; color: var(--purple); }}
.agent-glyph svg {{ width: 18px; height: 18px; }}
.agent-name {{
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: -0.02em;
  font-family: "JetBrains Mono", ui-monospace, Inter, monospace;
}}
.agent-sub {{
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 1px;
}}
.agent-body {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}}
.ring-wrap {{
  width: 108px;
  height: 108px;
  flex-shrink: 0;
  position: relative;
}}
.ring-wrap svg {{ width: 100%; height: 100%; }}
.ring-wrap .ring-track {{
  fill: none;
  stroke: var(--track);
  stroke-width: 9;
}}
.ring-wrap .ring-value {{
  fill: none;
  stroke-width: 9;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  transition: stroke-dashoffset 0.7s ease;
}}
.ring-wrap .ring-label {{
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.04em;
  font-variant-numeric: tabular-nums;
}}
.agent-stats {{
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 7px;
  padding-left: 4px;
}}
.stat-row {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 13px;
  color: var(--muted);
}}
.stat-row .k {{ font-weight: 500; }}
.stat-row .v {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-weight: 600;
  color: var(--navy);
  font-size: 13.5px;
}}
.task-box {{
  margin-top: 12px;
  background: var(--mint);
  border-radius: 12px;
  padding: 10px 12px 11px;
}}
.task-box.purple {{
  background: #F6F1FF;
}}
.task-label {{
  font-size: 12px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 4px;
}}
.task-text {{
  font-size: 12px;
  color: #4B6280;
  line-height: 1.4;
}}
.bay {{
  margin-top: auto;
  padding-top: 12px;
}}
.bay-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}}
.bay-left {{
  display: flex;
  flex-direction: column;
  gap: 1px;
}}
.bay-k {{
  font-size: 11px;
  color: var(--muted);
  font-weight: 500;
}}
.bay-id {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 13px;
  font-weight: 700;
  color: var(--navy);
}}
.stepper {{
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: start;
  position: relative;
  margin-top: 4px;
  padding: 0 4px;
}}
.stepper::before {{
  content: "";
  position: absolute;
  left: 18%;
  right: 18%;
  top: 7px;
  height: 2px;
  background: var(--track);
  z-index: 0;
}}
.stepper .progress-line {{
  position: absolute;
  left: 18%;
  top: 7px;
  height: 2px;
  background: var(--green);
  z-index: 1;
  transition: width 0.5s ease;
}}
.step {{
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}}
.step:first-child {{ align-items: center; }}
.step:last-child {{ align-items: center; }}
.step .node {{
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid var(--track);
  background: #fff;
  display: grid;
  place-items: center;
}}
.step.complete .node {{
  background: var(--green);
  border-color: var(--green);
  color: #fff;
}}
.step.active .node {{
  width: 16px;
  height: 16px;
  background: var(--blue);
  border-color: var(--blue);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.16);
  animation: nodepulse 1.8s ease-out infinite;
}}
@keyframes nodepulse {{
  0% {{ box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.28); }}
  70% {{ box-shadow: 0 0 0 7px rgba(37, 99, 235, 0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }}
}}
.step .slabel {{
  font-size: 11px;
  color: var(--muted);
  font-weight: 500;
}}
.step.complete .slabel,
.step.active .slabel {{
  color: var(--navy);
  font-weight: 600;
}}
.step.active .slabel {{ color: var(--blue); }}
.bay-released {{
  margin-top: 6px;
  font-size: 11px;
  font-weight: 700;
  color: var(--green);
  letter-spacing: 0.04em;
}}

/* ========== VITALS ========== */
.vitals {{
  grid-column: 4;
  grid-row: 2;
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
  min-height: 292px;
}}
.vitals-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}}
.vitals-title {{
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--navy);
  white-space: nowrap;
}}
.vitals-title svg {{ color: var(--green); width: 16px; height: 16px; }}
.live-mini {{
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  color: var(--green);
  letter-spacing: 0.08em;
}}
.bars {{
  display: flex;
  flex-direction: column;
  gap: 9px;
}}
.bar-row {{
  display: grid;
  grid-template-columns: 1fr 28px;
  align-items: center;
  column-gap: 8px;
  row-gap: 4px;
}}
.bar-name {{
  font-size: 12px;
  color: var(--navy);
  font-weight: 500;
}}
.bar-track {{
  grid-column: 1 / -1;
  height: 7px;
  background: var(--track);
  border-radius: 99px;
  overflow: hidden;
}}
.bar-fill {{
  height: 100%;
  background: var(--green);
  border-radius: 99px;
  transition: width 0.7s ease;
}}
.bar-val {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 12px;
  font-weight: 600;
  text-align: right;
  color: var(--navy);
}}
.vital-tiles {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
  margin-top: 14px;
}}
.vtile {{
  background: var(--surface);
  border-radius: 8px;
  padding: 6px 4px 7px;
  text-align: center;
}}
.vtile .tl {{
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--muted);
}}
.vtile .tv {{
  font-size: 18px;
  font-weight: 700;
  margin-top: 2px;
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
}}
.vtile.diag .tv {{ color: var(--blue); }}
.vtile.crit .tv {{ color: var(--red); }}
.vtile.rev .tv {{ color: var(--amber); }}
.vtile.fix .tv {{ color: var(--green); }}
.condition-row {{
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
}}
.ecg-panel {{
  background: var(--surface);
  border-radius: 10px;
  display: grid;
  place-items: center;
  padding: 6px;
  min-height: 64px;
}}
.ecg-panel svg {{
  width: 100%;
  height: 48px;
  color: var(--green);
}}
.ecg-line {{
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}}
.ecg-scan {{
  fill: none;
  stroke: #BBF7D0;
  stroke-width: 2.4;
  stroke-linecap: round;
  stroke-dasharray: 28 160;
  animation: ecgscan 2.2s linear infinite;
}}
@keyframes ecgscan {{
  from {{ stroke-dashoffset: 0; }}
  to {{ stroke-dashoffset: -188; }}
}}
.condition {{
  border-radius: 10px;
  padding: 8px 10px;
  background: #FDECEC;
  min-height: 64px;
}}
.condition.stable {{
  background: var(--mint);
}}
.condition .cl {{
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--muted);
}}
.condition .cv {{
  font-size: 16px;
  font-weight: 800;
  color: var(--red);
  letter-spacing: 0.02em;
  margin-top: 2px;
}}
.condition.stable .cv {{ color: var(--green); }}
.condition .cn {{
  font-size: 11px;
  color: var(--muted);
  margin-top: 2px;
}}

/* ========== FEED ========== */
.feed {{
  grid-column: 1 / -1;
  grid-row: 3;
  padding: 12px 16px 10px;
}}
.feed-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}}
.feed-head h2 {{
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
}}
.filters {{
  display: flex;
  align-items: center;
  gap: 4px;
}}
.filter {{
  border: none;
  background: transparent;
  color: var(--muted);
  font-family: Inter, sans-serif;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
  cursor: pointer;
}}
.filter.active {{
  background: #fff;
  color: var(--navy);
  border: 1px solid var(--border);
  box-shadow: 0 1px 2px rgba(23, 52, 95, 0.05);
}}
.feed-list {{
  display: flex;
  flex-direction: column;
}}
.feed-row {{
  display: grid;
  grid-template-columns: 72px 18px 118px 1fr;
  align-items: center;
  gap: 8px;
  padding: 7px 2px;
  border-top: 1px solid #EEF3F8;
  font-size: 12.5px;
  animation: fadein 0.35s ease;
}}
.feed-row:first-child {{ border-top: none; }}
@keyframes fadein {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to {{ opacity: 1; transform: none; }}
}}
.feed-ts {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  color: var(--muted);
  font-size: 12px;
}}
.feed-ico {{
  width: 16px;
  height: 16px;
  display: grid;
  place-items: center;
}}
.feed-src {{
  font-family: "JetBrains Mono", ui-monospace, monospace;
  font-size: 12px;
  font-weight: 700;
}}
.feed-msg {{
  color: var(--navy);
  font-size: 12.5px;
}}
.src-SCHEMA_MD {{ color: var(--green); }}
.src-ANOMALY_MD {{ color: #F59E0B; }}
.src-DUPLICATE_MD {{ color: #F97316; }}
.src-HOTDATA {{ color: var(--purple); }}
.src-ROCKETRIDE, .src-CHIEF {{ color: var(--navy); }}
.src-REPAIR, .src-VERIFY {{ color: var(--blue); }}

/* ========== PIPELINE ========== */
.pipeline {{
  grid-column: 1 / -1;
  grid-row: 4;
  padding: 10px 16px 8px;
}}
.pipeline-head {{
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--navy);
  margin-bottom: 10px;
}}
.pipe-track {{
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  position: relative;
  padding: 0 8px;
}}
.pipe-track::before {{
  content: "";
  position: absolute;
  left: 8%;
  right: 8%;
  top: 14px;
  height: 2px;
  background: var(--track);
}}
.pipe-fill {{
  position: absolute;
  left: 8%;
  top: 14px;
  height: 2px;
  background: var(--green);
  z-index: 1;
  transition: width 0.6s ease;
}}
.pipe-node {{
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
}}
.pipe-dot {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--track);
  background: #fff;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--muted);
}}
.pipe-node.complete .pipe-dot {{
  background: var(--green);
  border-color: var(--green);
  color: #fff;
}}
.pipe-node.active .pipe-dot {{
  background: var(--blue);
  border-color: var(--blue);
  color: #fff;
  box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.35);
  animation: nodepulse 1.8s ease-out infinite;
}}
.pipe-name {{
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--navy);
}}
.pipe-node.pending .pipe-name {{ color: #94A3B8; }}
.pipe-sub {{
  font-size: 11px;
  color: var(--muted);
  margin-top: -2px;
}}
.pipe-node.complete .pipe-sub {{ color: var(--green); font-weight: 600; }}
.pipe-node.active .pipe-sub {{ color: var(--blue); font-weight: 600; }}

@media (max-width: 1280px) {{
  .main-grid {{
    grid-template-columns: 1fr 1fr;
  }}
  .title-block {{ grid-column: 1 / -1; }}
  .rr-badge {{ grid-column: 1 / -1; justify-content: flex-end; }}
  .agent-schema, .agent-duplicate, .agent-anomaly, .vitals {{
    grid-row: auto;
  }}
  .agent-schema {{ grid-column: 1; }}
  .agent-duplicate {{ grid-column: 2; }}
  .agent-anomaly {{ grid-column: 1; }}
  .vitals {{ grid-column: 2; }}
  .feed, .pipeline {{ grid-column: 1 / -1; grid-row: auto; }}
}}
"""
