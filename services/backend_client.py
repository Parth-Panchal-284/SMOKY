"""Sole backend integration point for the DATA ER UI.

DEMO_MODE=True loads deterministic mock events.
When the RocketRide team is ready, set DEMO_MODE=False (or DATA_ER_DEMO_MODE=0)
and replace fetch_live_events() with the real transport.

UI modules must import poll_events from this file only — never mock_events.
"""

from __future__ import annotations

import os
from typing import Any

DEMO_MODE = True
_env = os.environ.get("DATA_ER_DEMO_MODE")
if _env is not None:
    DEMO_MODE = _env.strip() not in {"0", "false", "False", "no"}


def poll_events(run_id: str, cursor: float, elapsed: float) -> list[dict[str, Any]]:
    """Return new events since `cursor` (elapsed seconds), up to `elapsed`.

    `cursor` is the last elapsed timestamp the UI has already applied.
    Pass cursor=-1 on first paint so t=0 hero events are included.
    """
    if DEMO_MODE:
        from services.mock_events import events_between

        return events_between(cursor, elapsed)

    return fetch_live_events(run_id, cursor, elapsed)


def fetch_live_events(
    run_id: str,
    cursor: float,
    elapsed: float,
) -> list[dict[str, Any]]:
    """Hook for the RocketRide / backend team.

    Replace this body with HTTP polling, SSE, or websocket reads.
    Must return a list of event dicts matching models.events.Event.
    Must not block for long. Return [] when nothing is new.
    """
    _ = (run_id, cursor, elapsed)
    return []
