"""Cross-session telemetry reader for the DATA ER console.

Reads the SAME data the RocketRide dashboard app reads. Two sources, in order
of preference:

  1. dataer/telemetry.json in the RocketRide cloud file store -- the real
     cross-session record, written by run.mjs after every run. Requires the
     Python SDK and a connection, so it is best-effort.
  2. data/telemetry.jsonl on disk -- always present, same rows, no network.

Either way the numbers are real and they move when a run finishes: this is the
live telemetry the demo checklist asks for, not a screenshot.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_JSONL = ROOT / "data" / "telemetry.jsonl"
EVIDENCE = ROOT / "out" / "evidence_report.json"

SPECIALISTS = ("SCHEMA_MD", "DUPLICATE_MD", "ANOMALY_MD")


def _rows() -> list[dict[str, Any]]:
    try:
        return [
            json.loads(line)
            for line in TELEMETRY_JSONL.read_text().splitlines()
            if line.strip()
        ]
    except Exception:
        return []


def load() -> dict[str, Any]:
    """Everything the telemetry view needs, computed from real event rows."""
    events = _rows()
    try:
        evidence = json.loads(EVIDENCE.read_text())
    except Exception:
        evidence = {}

    runs: dict[str, dict[str, Any]] = {}
    for e in events:
        rid = str(e.get("run_id") or "")
        if not rid:
            continue
        r = runs.setdefault(rid, {"run_id": rid, "agents": {}, "modes": {}, "ts": e.get("ts")})
        agent = e.get("agent")
        dur = int(e.get("duration_ms") or 0)
        mode = str(e.get("mode") or "")
        if agent in SPECIALISTS:
            a = r["agents"].setdefault(agent, {"total": 0, "n": 0, "fail": 0, "queries": 0})
            a["total"] += dur
            a["n"] += 1
            a["queries"] += int(e.get("query_count") or 0)
            if e.get("outcome") != "ok":
                a["fail"] += 1
        if mode in ("parallel", "sequential") and dur:
            r["modes"][mode] = max(r["modes"].get(mode, 0), dur)
        if agent == "RUN":
            r["note"] = e.get("note", "")
            r["outcome"] = e.get("outcome", "")
            r["ts"] = e.get("ts", r.get("ts"))

    # health scores ride along in the RUN note: "... 91.8->96.7"
    for r in runs.values():
        note = str(r.get("note") or "")
        if "->" in note:
            try:
                tail = note.rsplit(" ", 1)[-1]
                before, after = tail.split("->")
                r["before_score"] = float(before)
                r["after_score"] = float(after)
            except Exception:
                pass
        for key in ("findings", "fixed", "flagged", "ignored"):
            token = f"{key}="
            if token in note:
                try:
                    r[key] = int(note.split(token)[1].split(" ")[0])
                except Exception:
                    pass

    ordered = sorted(runs.values(), key=lambda r: str(r.get("ts") or ""))

    # cross-agent aggregate
    agg: dict[str, dict[str, Any]] = {}
    for r in ordered:
        for agent, a in r["agents"].items():
            g = agg.setdefault(agent, {"total": 0, "n": 0, "fail": 0, "queries": 0})
            for k in ("total", "n", "fail", "queries"):
                g[k] += a[k]
    for agent, g in agg.items():
        g["avg_ms"] = round(g["total"] / g["n"]) if g["n"] else 0

    speedups = [
        r["modes"]["sequential"] / r["modes"]["parallel"]
        for r in ordered
        if r["modes"].get("parallel") and r["modes"].get("sequential")
    ]

    return {
        "runs": ordered,
        "agents": agg,
        "event_count": len(events),
        "best_speedup": max(speedups) if speedups else None,
        "last_speedup": speedups[-1] if speedups else None,
        "evidence": evidence,
    }
