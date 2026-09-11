"""DATA ER — Operating Room console.

Custom HTML/CSS rendered through Streamlit. Demo state lives in session_state.
RocketRide integration happens only via services.backend_client.poll_events.
"""

from __future__ import annotations

import time
from datetime import datetime

import streamlit as st

from models.run_state import RunState, apply_event
from services.backend_client import poll_events
from ui.shell import render_app_html
from ui.styles import STREAMLIT_CHROME_CSS

st.set_page_config(
    layout="wide",
    page_title="DATA ER",
    page_icon="🏥",
    initial_sidebar_state="collapsed",
)

st.markdown(STREAMLIT_CHROME_CSS, unsafe_allow_html=True)


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


@st.fragment(run_every=1.0)
def operating_room() -> None:
    try:
        state = _tick()
        html = render_app_html(state)
        st.iframe(html, width="stretch", height=920)
    except Exception as exc:  # noqa: BLE001 — surface demo failures in the UI
        st.exception(exc)


operating_room()
