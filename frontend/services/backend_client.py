"""Sole backend integration point for the DATA ER UI.

DEMO_MODE=True loads deterministic mock events.
DEMO_MODE=False reads the REAL RocketRide run produced by the harness:

    data/telemetry.jsonl    one row per agent/run event, written by run.mjs
    out/evidence_report.json  findings, chief decisions, audit trail, invariants

Both live in the workspace root (this file sits in frontend/services/), so the
UI and the backend share a filesystem. That is deliberate: the transport is the
simplest thing that is genuinely live, with no extra service to keep up.

UI modules must import poll_events from this file only — never mock_events.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Live by default: this console reads real RocketRide runs.
# Set DATA_ER_DEMO_MODE=1 to fall back to the canned timeline.
DEMO_MODE = False
_env = os.environ.get("DATA_ER_DEMO_MODE")
if _env is not None:
    DEMO_MODE = _env.strip() not in {"0", "false", "False", "no"}

# frontend/services/backend_client.py -> workspace root
ROOT = Path(__file__).resolve().parents[2]
TELEMETRY = ROOT / "data" / "telemetry.jsonl"
EVIDENCE = ROOT / "out" / "evidence_report.json"


def poll_events(run_id: str, cursor: float, elapsed: float) -> list[dict[str, Any]]:
    """Return new events since `cursor` (elapsed seconds), up to `elapsed`.

    `cursor` is the last elapsed timestamp the UI has already applied.
    Pass cursor=-1 on first paint so t=0 hero events are included.
    """
    if DEMO_MODE:
        from services.mock_events import events_between

        return events_between(cursor, elapsed)

    return fetch_live_events(run_id, cursor, elapsed)


# ---------------------------------------------------------------- live reader


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    except Exception:
        return []


def _latest_run_id(events: list[dict[str, Any]], evidence: dict[str, Any]) -> str | None:
    if evidence.get("run_id"):
        return str(evidence["run_id"])
    runs = [e.get("run_id") for e in events if e.get("run_id")]
    return str(runs[-1]) if runs else None


def build_timeline(run_id: str | None = None) -> list[tuple[float, dict[str, Any]]]:
    """Turn one real run into (offset_seconds, Event) pairs.

    Offsets are synthesised in pipeline order rather than taken from wall-clock
    timestamps: the UI animates a six-stage operation, and a faithful replay of
    a 70-second wave would leave five of those stages empty for a minute. The
    VALUES are all real; only the pacing is presentational.
    """
    events = _read_jsonl(TELEMETRY)
    evidence = _read_json(EVIDENCE)
    rid = run_id or _latest_run_id(events, evidence)
    if not rid:
        return []

    mine = [e for e in events if str(e.get("run_id")) == str(rid)]
    agents = [e for e in mine if e.get("agent") not in (None, "RUN", "WAVE")]
    findings = evidence.get("findings", []) or []
    decisions = evidence.get("decisions", []) or []
    audit = evidence.get("audit_trail", []) or []
    invariants = evidence.get("invariants", []) or []
    rolled_back = bool(evidence.get("rollback_triggered"))
    before = evidence.get("before_score", 0)
    after = evidence.get("after_score", before)

    t: list[tuple[float, dict[str, Any]]] = []
    short = str(rid).replace("run_", "")[:12]

    # 1 — intake
    t.append((0.0, {
        "type": "run_started",
        "run_id": short,
        "patient_name": f"PATIENT_{short}",
        "file": os.path.basename(str(evidence.get("dataset") or "sample.csv")),
        "rows": evidence.get("rows_before", 0),
        "columns": 7,
        "size": f"{evidence.get('rows_before', 0)} rows",
    }))
    t.append((0.5, {
        "type": "health_updated", "run_id": short,
        "completeness": int(before), "schema_integrity": int(before),
        "validity": int(before), "uniqueness": int(before),
    }))

    # 2 — diagnose. One bay per specialist; bay ids only when Hotdata really ran.
    hot = [e for e in mine if "hotdata" in str(e.get("note", "")).lower()]
    for i, e in enumerate(agents):
        a = e["agent"]
        base = 1.0 + i * 0.4
        if hot:
            t.append((base, {
                "type": "hotdata_created", "run_id": short, "agent": a,
                "bay_id": f"HD-{short[:3]}-{chr(65 + i)}",
            }))
        t.append((base + 0.1, {"type": "agent_started", "run_id": short, "agent": a}))
        qc = int(e.get("query_count") or 0)
        if qc:
            t.append((base + 0.4, {
                "type": "agent_query", "run_id": short, "agent": a, "query_count": qc,
            }))

    for i, f in enumerate(findings):
        t.append((3.0 + i * 0.25, {
            "type": "diagnosis_found", "run_id": short,
            "agent": f.get("agent", "?"),
            "message": f"{f.get('finding_type', 'issue')} — {str(f.get('evidence', ''))[:90]}",
            "status": f.get("severity", "medium"),
        }))

    fin_base = 3.0 + len(findings) * 0.25 + 0.5
    for i, e in enumerate(agents):
        a = e["agent"]
        n = len([f for f in findings if f.get("agent") == a])
        t.append((fin_base + i * 0.3, {
            "type": "agent_completed", "run_id": short, "agent": a,
            "findings": n, "duration_ms": int(e.get("duration_ms") or 0),
            "status": e.get("outcome", "ok"),
        }))
        if hot:
            t.append((fin_base + i * 0.3 + 0.15, {
                "type": "hotdata_destroyed", "run_id": short, "agent": a,
            }))

    wave = fin_base + len(agents) * 0.3 + 0.5
    wave_ms = max([int(e.get("duration_ms") or 0) for e in agents], default=0)
    t.append((wave, {
        "type": "wave_completed", "run_id": short,
        "duration_ms": wave_ms, "findings": len(findings),
    }))

    # 3 — chief
    t.append((wave + 0.5, {"type": "chief_started", "run_id": short}))
    conflicts = [d for d in decisions if d.get("action") == "ignore"]
    for i, d in enumerate(conflicts):
        t.append((wave + 0.8 + i * 0.2, {
            "type": "conflict_found", "run_id": short,
            "message": str(d.get("reasoning", ""))[:110],
        }))
    ch = wave + 1.2 + len(conflicts) * 0.2
    for i, d in enumerate(decisions):
        t.append((ch + i * 0.15, {
            "type": "chief_decision", "run_id": short,
            "status": d.get("action", "?"),
            "message": f"#{d.get('finding_index')} {d.get('action')} — {str(d.get('reasoning',''))[:80]}",
        }))

    # 4/5 — repair + verify
    rp = ch + len(decisions) * 0.15 + 0.5
    t.append((rp, {
        "type": "repair_started", "run_id": short,
        "auto_fix": int(evidence.get("auto_fixed", 0)),
        "review": int(evidence.get("flagged", 0)),
    }))
    for i, inv in enumerate(invariants):
        t.append((rp + 0.4 + i * 0.15, {
            "type": "agent_status", "run_id": short,
            "status": "ok" if inv.get("ok") else "failed",
            "message": f"{inv.get('name')}: {inv.get('detail')}",
        }))
    vr = rp + 0.6 + len(invariants) * 0.15
    t.append((vr, {
        "type": "repair_rollback" if rolled_back else "repair_verified",
        "run_id": short, "message": f"{len(audit)} audited change(s)",
    }))

    # 6 — discharge
    t.append((vr + 0.5, {
        "type": "health_updated", "run_id": short,
        "completeness": int(after), "schema_integrity": int(after),
        "validity": int(after), "uniqueness": int(after),
    }))
    t.append((vr + 0.9, {
        "type": "run_completed", "run_id": short,
        "diagnoses": len(findings),
        "auto_fix": int(evidence.get("auto_fixed", 0)),
        "review": int(evidence.get("flagged", 0)),
        "critical": len([f for f in findings if f.get("severity") == "high"]),
        "message": f"health {before} -> {after}"
                   + (" (ROLLED BACK)" if rolled_back else ""),
    }))

    t.sort(key=lambda p: p[0])
    return t


_CACHE: dict[str, Any] = {"key": None, "timeline": []}


def fetch_live_events(
    run_id: str,
    cursor: float,
    elapsed: float,
) -> list[dict[str, Any]]:
    """Real RocketRide events, read from the harness output.

    Rebuilt whenever the underlying files change, so starting a new run in the
    terminal shows up in the UI without a restart.
    """
    try:
        stamp = (
            TELEMETRY.stat().st_mtime if TELEMETRY.exists() else 0,
            EVIDENCE.stat().st_mtime if EVIDENCE.exists() else 0,
        )
    except OSError:
        stamp = (0, 0)

    if _CACHE["key"] != stamp:
        _CACHE["key"] = stamp
        _CACHE["timeline"] = build_timeline()

    return [e for off, e in _CACHE["timeline"] if cursor < off <= elapsed]
