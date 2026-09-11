"""DATA ER — Operating Room console.

Custom HTML/CSS rendered through Streamlit. Demo state lives in session_state.
RocketRide integration happens only via services.backend_client.poll_events.

Navigation note: the styled sidebar is rendered inside the Operating Room's
iframe, so its links cannot call back into Streamlit. Page switching is done
with a native Streamlit control above it — the five screens the sidebar
advertises are all real, and every one reads the same live run output.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from models.run_state import RunState, apply_event
from services.backend_client import poll_events, ROOT, TELEMETRY, EVIDENCE
from services.telemetry import load as load_telemetry
from ui.shell import render_app_html
from ui.styles import STREAMLIT_CHROME_CSS

st.set_page_config(
    layout="wide",
    page_title="DATA ER",
    page_icon="🏥",
    initial_sidebar_state="collapsed",
)

st.markdown(STREAMLIT_CHROME_CSS, unsafe_allow_html=True)

# The shell CSS zeroes block padding and vertical gaps to make the iframe sit
# flush, which also flattens any native Streamlit widget to nothing. The page
# selector has to opt back out of that.
st.markdown(
    """
<style>
  div[data-testid="stHorizontalBlock"]:has(div[data-testid="stRadio"]),
  div[data-testid="stRadio"] { display: block !important; visibility: visible !important; }
  div[data-testid="stRadio"] {
    background: #fff; border-bottom: 1px solid #E6EEF6;
    padding: 8px 20px 6px !important; margin: 0 !important;
  }
  div[data-testid="stRadio"] > div { gap: 6px !important; flex-wrap: wrap; }
  div[data-testid="stRadio"] label {
    font-size: 12.5px !important; font-weight: 600;
    padding: 5px 12px !important; border-radius: 7px;
    border: 1px solid #E6EEF6; background: #F6F8FB; cursor: pointer;
  }
  div[data-testid="stRadio"] label:hover { border-color: #16A34A; }
  /* the page bodies (not the iframe) need their padding back */
  div[data-testid="stVerticalBlock"]:has(> div [data-testid="stDataFrame"]),
  div[data-testid="stVerticalBlock"]:has(> div [data-testid="stMetric"]) {
    padding: 10px 20px !important; gap: 10px !important;
  }
  [data-testid="stMetric"] {
    background: #fff; border: 1px solid #E6EEF6; border-radius: 9px; padding: 10px 12px !important;
  }
  h3, .stSubheader { padding: 12px 20px 0 !important; }
</style>
""",
    unsafe_allow_html=True,
)

PAGES = [
    "01 · Triage",
    "02 · Operating Room",
    "03 · Chief Review",
    "04 · Results",
    "05 · Telemetry",
]


# ------------------------------------------------------------------ live state


def _init_state() -> None:
    if "run_state" not in st.session_state:
        st.session_state.run_state = RunState()
        st.session_state.event_cursor = -1.0
        st.session_state.demo_t0 = time.time()
        st.session_state.run_id = "042"


def _sync_clock(state: RunState) -> None:
    now = datetime.now()
    state.clock_date = now.strftime("%a, %b %d, %Y")
    hour = now.strftime("%I").lstrip("0") or "12"
    state.clock_time = f"{hour}:{now.strftime('%M %p')}"


def _tick() -> RunState:
    _init_state()
    state: RunState = st.session_state.run_state
    elapsed = time.time() - st.session_state.demo_t0
    state.run_duration = elapsed
    events = poll_events(
        st.session_state.run_id,
        float(st.session_state.event_cursor),
        elapsed,
    )
    for event in events:
        apply_event(state, event)
    st.session_state.event_cursor = elapsed
    _sync_clock(state)
    return state


def _evidence() -> dict:
    try:
        return json.loads(EVIDENCE.read_text())
    except Exception:
        return {}


def _csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    try:
        import csv

        with path.open() as fh:
            r = csv.DictReader(fh)
            rows = list(r)
            return (r.fieldnames or []), rows
    except Exception:
        return [], []


# ----------------------------------------------------------------------- pages


@st.fragment(run_every=1.0)
def operating_room() -> None:
    try:
        state = _tick()
        html = render_app_html(state)
        st.iframe(html, width="stretch", height=920)
    except Exception as exc:  # noqa: BLE001 — surface demo failures in the UI
        st.exception(exc)


def triage() -> None:
    st.subheader("Triage — Upload & Profile")
    ev = _evidence()
    src = ROOT / "data" / "sample.csv"
    header, rows = _csv_rows(src)

    c = st.columns(4)
    c[0].metric("Rows", ev.get("rows_before", len(rows)))
    c[1].metric("Columns", len(header))
    c[2].metric("Baseline health", ev.get("before_score", "—"))
    c[3].metric("Dataset", src.name)

    st.caption(f"Source: `{src}` — the dataset the last run diagnosed.")
    if rows:
        st.dataframe(rows, width="stretch", height=420)
    else:
        st.info("No dataset found. Run the harness first.")


def chief_review() -> None:
    st.subheader("Chief Review — Resolve & Approve")
    ev = _evidence()
    decisions = ev.get("decisions") or []
    findings = ev.get("findings") or []
    if not decisions:
        st.info("No chief decisions in the last run.")
        return

    c = st.columns(4)
    c[0].metric("Findings", ev.get("total_findings", len(findings)))
    c[1].metric("Auto-fixed", ev.get("auto_fixed", 0))
    c[2].metric("Flagged", ev.get("flagged", 0))
    c[3].metric("Ignored", ev.get("ignored", 0))

    table = []
    for d in decisions:
        i = d.get("finding_index")
        f = findings[i] if isinstance(i, int) and i < len(findings) else {}
        table.append({
            "#": i,
            "agent": f.get("agent", d.get("agent", "?")),
            "finding": f.get("finding_type", ""),
            "severity": f.get("severity", ""),
            "action": d.get("action", ""),
            "transform": d.get("transform", ""),
            "reasoning": str(d.get("reasoning", ""))[:160],
        })
    st.dataframe(table, width="stretch", height=420)

    rejected = ev.get("rejected_decisions") or []
    if rejected:
        st.caption("Refused by the allow-list — the refusal is part of the audit trail:")
        st.dataframe(rejected, width="stretch")


def results() -> None:
    st.subheader("Results — Report & Export")
    ev = _evidence()
    before = ev.get("before_score", 0)
    after = ev.get("after_score", 0)
    rolled = ev.get("rollback_triggered")

    c = st.columns(4)
    c[0].metric("Health", after, delta=round(after - before, 1) if before else None)
    c[1].metric("Rows", f"{ev.get('rows_before','—')} → {ev.get('rows_after','—')}")
    c[2].metric("Audited changes", len(ev.get("audit_trail") or []))
    c[3].metric("Verification", "ROLLED BACK" if rolled else "VERIFIED")

    for inv in ev.get("invariants") or []:
        (st.success if inv.get("ok") else st.error)(
            f"{'PASS' if inv.get('ok') else 'FAIL'} — {inv.get('name')}: {inv.get('detail')}"
        )

    st.markdown("**Audit trail** — every change, with before and after values")
    audit = ev.get("audit_trail") or []
    if audit:
        st.dataframe(audit, width="stretch", height=300)
    else:
        st.info("No changes were applied in the last run.")

    cleaned = ROOT / "out" / "cleaned.csv"
    if cleaned.exists():
        st.download_button(
            "Download cleaned.csv", cleaned.read_bytes(),
            file_name="cleaned.csv", mime="text/csv",
        )
    if EVIDENCE.exists():
        st.download_button(
            "Download evidence_report.json", EVIDENCE.read_bytes(),
            file_name="evidence_report.json", mime="application/json",
        )


@st.fragment(run_every=3.0)
def telemetry() -> None:
    """Live cross-session telemetry — re-reads on every tick, so a run that
    finishes in the terminal shows up here without a reload."""
    st.subheader("Telemetry — Agent Performance")
    t = load_telemetry()
    runs = t["runs"]

    c = st.columns(5)
    c[0].metric("Sessions", len(runs))
    c[1].metric("Events", t["event_count"])
    best = t["best_speedup"]
    c[2].metric("Best speedup", f"{best:.2f}×" if best else "—")
    last = runs[-1] if runs else {}
    c[3].metric("Latest health", last.get("after_score", "—"))
    c[4].metric("Rollbacks", sum(1 for r in runs if r.get("outcome") == "rolled_back"))

    st.caption(
        f"Live from `{TELEMETRY.name}` · also published to `dataer/telemetry.json` "
        f"in the RocketRide cloud store · refreshes every 3s"
    )

    left, right = st.columns(2)

    with left:
        st.markdown("**Parallel vs sequential** (latest run, ms)")
        modes = last.get("modes") or {}
        if modes:
            st.bar_chart({k: [int(v)] for k, v in modes.items() if v}, height=220)
            if modes.get("parallel") and modes.get("sequential"):
                sp = modes["sequential"] / modes["parallel"]
                st.success(
                    f"{sp:.2f}× faster in parallel — saved "
                    f"{modes['sequential'] - modes['parallel']} ms"
                )
        else:
            st.info("Run `--mode both` to populate the comparison.")

    with right:
        st.markdown("**Specialist performance** (avg ms per run)")
        agents = t["agents"]
        if agents:
            st.bar_chart(
                {a: [int(g["avg_ms"])] for a, g in agents.items()}, height=220
            )
            slowest = max(agents.items(), key=lambda kv: kv[1]["avg_ms"])[0]
            st.caption(f"Bottleneck: **{slowest}**")
        else:
            st.info("No agent events yet.")

    st.markdown("**Health score across sessions**")
    series = [r for r in runs if r.get("after_score") is not None]
    if series:
        st.line_chart(
            {
                "before": [r.get("before_score", 0) for r in series],
                "after": [r.get("after_score", 0) for r in series],
            },
            height=240,
        )
    else:
        st.info("No scored runs yet.")

    st.markdown("**Run history**")
    # Every cell as str: Arrow rejects a column mixing ints with an em-dash
    # placeholder ("Conversion failed for column findings with type object").
    def _s(v):
        return "—" if v in (None, "") else str(v)

    hist = [
        {
            "run_id": _s(r.get("run_id")),
            "health": f"{_s(r.get('before_score'))} → {_s(r.get('after_score'))}",
            "findings": _s(r.get("findings")),
            "fixed": _s(r.get("fixed")),
            "parallel_ms": _s((r.get("modes") or {}).get("parallel")),
            "sequential_ms": _s((r.get("modes") or {}).get("sequential")),
            "outcome": _s(r.get("outcome")),
        }
        for r in reversed(runs)
    ]
    st.dataframe(hist, width="stretch", height=260)


# ------------------------------------------------------------------------ main

# ---- navigation --------------------------------------------------------------
# The shell CSS hides/flattens native widgets, and the Operating Room's
# run_every fragment re-renders over a radio before its state propagates. Query
# params sidestep both: they survive the rerun and cannot be styled away.
#
#   ?page=triage | operating | chief | results | telemetry
KEYS = ["triage", "operating", "chief", "results", "telemetry"]
LABELS = dict(zip(KEYS, PAGES))

qp = st.query_params
current = str(qp.get("page") or "operating").lower()
if current not in KEYS:
    current = "operating"

nav = " &nbsp;·&nbsp; ".join(
    (f"<b style='color:#16A34A'>{LABELS[k]}</b>" if k == current
     else f"<a href='?page={k}' target='_self' style='color:#5B6B7F;text-decoration:none'>{LABELS[k]}</a>")
    for k in KEYS
)
st.markdown(
    "<div style=\"background:#fff;border-bottom:1px solid #E6EEF6;padding:9px 20px;"
    "font:600 12.5px/1.2 system-ui,sans-serif;position:sticky;top:0;z-index:999\">"
    + nav + "</div>",
    unsafe_allow_html=True,
)

if current == "triage":
    triage()
elif current == "operating":
    operating_room()
elif current == "chief":
    chief_review()
elif current == "results":
    results()
else:
    telemetry()
