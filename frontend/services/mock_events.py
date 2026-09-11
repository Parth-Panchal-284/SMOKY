"""Deterministic DEMO_MODE timeline. [DEMO ONLY]

Safe to delete once RocketRide is wired through backend_client.poll_events.
Keyed by elapsed seconds from demo start — never random, never blocking.
"""

from __future__ import annotations

from typing import Any

# Hold the judge-ready parallel snapshot before advancing the pipeline.
HERO_HOLD_SECONDS = 10.0

# (offset_seconds, event)
# Offset 0.0 is the Operating Room hero frame from the reference mockup.
TIMELINE: list[tuple[float, dict[str, Any]]] = [
    (
        0.0,
        {
            "type": "run_started",
            "run_id": "042",
            "patient_name": "PATIENT_042",
            "file": "customers.csv",
            "rows": 15482,
            "columns": 18,
            "size": "2.4 MB",
        },
    ),
    (
        0.0,
        {
            "type": "hotdata_created",
            "run_id": "042",
            "agent": "SCHEMA_MD",
            "bay_id": "HD-042-A",
        },
    ),
    (
        0.0,
        {
            "type": "hotdata_created",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
            "bay_id": "HD-042-C",
        },
    ),
    (
        0.0,
        {
            "type": "hotdata_created",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "bay_id": "HD-042-B",
        },
    ),
    (
        0.0,
        {
            "type": "agent_started",
            "run_id": "042",
            "agent": "SCHEMA_MD",
        },
    ),
    (
        0.0,
        {
            "type": "agent_started",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
        },
    ),
    (
        0.0,
        {
            "type": "agent_started",
            "run_id": "042",
            "agent": "ANOMALY_MD",
        },
    ),
    (
        0.0,
        {
            "type": "agent_query",
            "run_id": "042",
            "agent": "SCHEMA_MD",
            "status": "querying",
            "message": "Analyzing column types and format inconsistencies...",
            "query_count": 8,
            "findings": 6,
            "duration_ms": 2300,
            "progress": 72,
        },
    ),
    (
        0.0,
        {
            "type": "agent_query",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
            "status": "querying",
            "message": "Finding potential duplicate clusters using vector search...",
            "query_count": 14,
            "findings": 11,
            "duration_ms": 4700,
            "progress": 51,
        },
    ),
    (
        0.0,
        {
            "type": "agent_query",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "status": "querying",
            "message": "Detecting outliers and unusual patterns...",
            "query_count": 9,
            "findings": 5,
            "duration_ms": 2900,
            "progress": 68,
        },
    ),
    (
        0.0,
        {
            "type": "health_updated",
            "run_id": "042",
            "schema_integrity": 61,
            "validity": 47,
            "uniqueness": 54,
            "completeness": 73,
            "diagnoses": 27,
            "critical": 4,
            "review": 7,
            "auto_fix": 16,
            "condition": "CRITICAL",
            "condition_note": "Stabilizing...",
        },
    ),
    (
        0.0,
        {
            "type": "diagnosis_found",
            "run_id": "042",
            "agent": "SCHEMA_MD",
            "findings": 6,
            "diagnoses": 27,
            "critical": 4,
            "review": 7,
            "auto_fix": 16,
            "timestamp": "12:24:12",
            "message": "Found 3 inconsistent date formats in signup_date",
        },
    ),
    (
        0.0,
        {
            "type": "diagnosis_found",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "findings": 5,
            "timestamp": "12:24:13",
            "message": "Detected 12 rows with negative purchase_amount",
        },
    ),
    (
        0.0,
        {
            "type": "diagnosis_found",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
            "findings": 11,
            "timestamp": "12:24:14",
            "message": "Found 32 potential duplicate clusters",
        },
    ),
    (
        0.0,
        {
            "type": "agent_query",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "status": "querying",
            "source": "HOTDATA",
            "timestamp": "12:24:15",
            "message": "HD-042-B executed query (422ms)",
            "query_count": 9,
            "findings": 5,
            "duration_ms": 2900,
            "progress": 68,
        },
    ),
    (
        0.0,
        {
            "type": "run_started",
            "run_id": "042",
            "timestamp": "12:24:15",
            "source": "ROCKETRIDE",
            "message": "Wave 1 in progress... (3/3 agents running)",
        },
    ),
    # --- after hero hold: specialists complete, then Chief → Repair → Verify → Discharge
    (
        HERO_HOLD_SECONDS + 0.0,
        {
            "type": "agent_completed",
            "run_id": "042",
            "agent": "SCHEMA_MD",
            "timestamp": "12:24:26",
            "message": "SCHEMA_MD complete — 6 structure findings filed",
            "progress": 100,
        },
    ),
    (
        HERO_HOLD_SECONDS + 0.5,
        {
            "type": "hotdata_destroyed",
            "run_id": "042",
            "agent": "SCHEMA_MD",
            "bay_id": "HD-042-A",
            "timestamp": "12:24:27",
            "message": "HD-042-A destroyed — Bay Released",
        },
    ),
    (
        HERO_HOLD_SECONDS + 2.0,
        {
            "type": "agent_completed",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "timestamp": "12:24:28",
            "message": "ANOMALY_MD complete — 5 anomaly findings filed",
        },
    ),
    (
        HERO_HOLD_SECONDS + 2.5,
        {
            "type": "hotdata_destroyed",
            "run_id": "042",
            "agent": "ANOMALY_MD",
            "bay_id": "HD-042-B",
            "timestamp": "12:24:29",
            "message": "HD-042-B destroyed — Bay Released",
        },
    ),
    (
        HERO_HOLD_SECONDS + 4.0,
        {
            "type": "agent_completed",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
            "timestamp": "12:24:30",
            "message": "DUPLICATE_MD complete — 11 duplicate clusters filed",
        },
    ),
    (
        HERO_HOLD_SECONDS + 4.5,
        {
            "type": "hotdata_destroyed",
            "run_id": "042",
            "agent": "DUPLICATE_MD",
            "bay_id": "HD-042-C",
            "timestamp": "12:24:31",
            "message": "HD-042-C destroyed — Bay Released",
        },
    ),
    (
        HERO_HOLD_SECONDS + 5.0,
        {
            "type": "wave_completed",
            "run_id": "042",
            "timestamp": "12:24:32",
            "message": "Wave 1 complete. 3/3 specialists finished.",
        },
    ),
    (
        HERO_HOLD_SECONDS + 6.0,
        {
            "type": "chief_started",
            "run_id": "042",
            "timestamp": "12:24:33",
            "message": "Chief agent reconciling specialist findings...",
        },
    ),
    (
        HERO_HOLD_SECONDS + 7.5,
        {
            "type": "conflict_found",
            "run_id": "042",
            "timestamp": "12:24:35",
            "message": "Chief flagged 2 overlapping duplicate vs anomaly calls",
        },
    ),
    (
        HERO_HOLD_SECONDS + 9.0,
        {
            "type": "chief_decision",
            "run_id": "042",
            "timestamp": "12:24:36",
            "message": "Chief approved repair plan — 16 auto-fix, 7 review",
        },
    ),
    (
        HERO_HOLD_SECONDS + 10.0,
        {
            "type": "repair_started",
            "run_id": "042",
            "timestamp": "12:24:37",
            "message": "Deterministic repair started on customers.csv",
        },
    ),
    (
        HERO_HOLD_SECONDS + 12.0,
        {
            "type": "health_updated",
            "run_id": "042",
            "schema_integrity": 88,
            "validity": 79,
            "uniqueness": 86,
            "completeness": 91,
            "diagnoses": 27,
            "critical": 1,
            "review": 3,
            "auto_fix": 16,
            "condition": "CRITICAL",
            "condition_note": "Responding to repair...",
        },
    ),
    (
        HERO_HOLD_SECONDS + 13.0,
        {
            "type": "repair_verified",
            "run_id": "042",
            "timestamp": "12:24:40",
            "message": "Repair verified — no regressions in checksum",
        },
    ),
    (
        HERO_HOLD_SECONDS + 14.5,
        {
            "type": "health_updated",
            "run_id": "042",
            "schema_integrity": 96,
            "validity": 94,
            "uniqueness": 97,
            "completeness": 95,
            "diagnoses": 27,
            "critical": 0,
            "review": 1,
            "auto_fix": 16,
            "condition": "STABLE",
            "condition_note": "Vitals recovering",
        },
    ),
    (
        HERO_HOLD_SECONDS + 16.0,
        {
            "type": "run_completed",
            "run_id": "042",
            "timestamp": "12:24:43",
            "condition": "STABLE",
            "condition_note": "Cleared for discharge",
            "message": "Run complete. PATIENT_042 discharged.",
        },
    ),
]


def events_between(after: float, until: float) -> list[dict[str, Any]]:
    """Return timeline events with after < t <= until, in order."""
    out: list[dict[str, Any]] = []
    for offset, event in TIMELINE:
        if after < offset <= until:
            out.append(event)
    return out
