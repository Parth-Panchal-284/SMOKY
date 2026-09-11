from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _load(name: str):
    with (DATA_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


ZONES = _load("zones.json")
SHELTERS = _load("shelters.json")
REPORTS = _load("demo_reports.json")
INCIDENTS = _load("incidents.json")


def zone_with_counts():
    result = []
    for zone in ZONES:
        item = dict(zone)
        item["incident_count"] = sum(
            1 for incident in INCIDENTS if incident["zone_id"] == zone["id"] and incident["status"] != "RESOLVED"
        )
        result.append(item)
    return result
