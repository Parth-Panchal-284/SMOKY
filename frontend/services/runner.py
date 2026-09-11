"""Launch and track real RocketRide runs from the console.

The console does not reimplement the pipeline: it shells out to the same
harness (`run.mjs`) a developer runs by hand, so the UI and the terminal
cannot drift apart. The run continues even if the browser tab closes —
pipelines execute on RocketRide's servers, and the harness is just a client.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
UPLOADS = ROOT / "data" / "uploads"
RUNS = ROOT / "out" / "runs"
LIVE_LOG = ROOT / "out" / "run.log"


def save_upload(name: str, data: bytes) -> Path:
    UPLOADS.mkdir(parents=True, exist_ok=True)
    safe = "".join(c for c in name if c.isalnum() or c in "._-") or "upload.csv"
    path = UPLOADS / f"{int(time.time())}_{safe}"
    path.write_bytes(data)
    return path


def start_run(csv_path: Path, mode: str = "both") -> dict[str, Any]:
    """Fire the harness in the background. Returns the run id immediately."""
    run_id = f"run_ui_{time.strftime('%H%M%S')}"
    log = ROOT / "out" / f"{run_id}.stdout"
    ROOT.joinpath("out").mkdir(exist_ok=True)

    cmd = [
        "node", "--env-file=.env", "run.mjs",
        "--mode", mode,
        "--csv", str(csv_path.relative_to(ROOT)) if csv_path.is_relative_to(ROOT) else str(csv_path),
        "--run-id", run_id,
    ]
    with log.open("wb") as fh:
        subprocess.Popen(
            cmd, cwd=str(ROOT), stdout=fh, stderr=subprocess.STDOUT,
            start_new_session=True,     # survives the Streamlit worker
        )
    return {"run_id": run_id, "log": log, "cmd": " ".join(cmd), "started": time.time()}


def is_running() -> bool:
    try:
        out = subprocess.run(
            ["pgrep", "-f", "run.mjs"], capture_output=True, text=True, timeout=5
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def live_log(tail: int = 40) -> str:
    try:
        lines = LIVE_LOG.read_text().splitlines()
        return "\n".join(lines[-tail:])
    except Exception:
        return ""


def stage_from_log(text: str) -> str:
    """Map harness output onto the console's six stages."""
    if not text:
        return "intake"
    for marker, stage in (
        ("wrote out/cleaned.csv", "discharge"),
        ("=== VERIFY", "verify"),
        ("=== REPAIR", "repair"),
        ("=== RECONCILE", "chief"),
        ("=== DIAGNOSIS", "diagnose"),
    ):
        if marker in text:
            return stage
    return "intake"


def past_runs() -> list[dict[str, Any]]:
    """Every archived run, newest first."""
    if not RUNS.exists():
        return []
    out = []
    for p in sorted(RUNS.glob("*.json"), key=lambda q: q.stat().st_mtime, reverse=True):
        try:
            r = json.loads(p.read_text())
            r["_path"] = str(p)
            r["_csv"] = str(p.with_suffix(".csv"))
            r["_when"] = time.strftime("%H:%M:%S", time.localtime(p.stat().st_mtime))
            out.append(r)
        except Exception:
            continue
    return out
