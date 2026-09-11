"""Backend event contract for DATA ER.

UI components consume these shapes only. Do not import RocketRide internals here.
"""

from __future__ import annotations

from typing import Any, TypedDict

EVENT_TYPES = (
    "run_started",
    "hotdata_created",
    "agent_started",
    "agent_query",
    "agent_status",
    "diagnosis_found",
    "agent_completed",
    "hotdata_destroyed",
    "wave_completed",
    "chief_started",
    "conflict_found",
    "chief_decision",
    "repair_started",
    "repair_verified",
    "repair_rollback",
    "health_updated",
    "run_completed",
)


class Event(TypedDict, total=False):
    type: str
    run_id: str
    agent: str
    status: str
    message: str
    query_count: int
    findings: int
    duration_ms: int
    progress: int
    bay_id: str
    timestamp: str
    patient_name: str
    file: str
    rows: int
    columns: int
    size: str
    schema_integrity: int
    validity: int
    uniqueness: int
    completeness: int
    diagnoses: int
    critical: int
    review: int
    auto_fix: int
    condition: str
    condition_note: str
    source: str
    category: str
    pipeline_stage: str
    extra: dict[str, Any]
