"""Immutable-ish run snapshot + event reducer.

UI reads RunState. Backend integration only produces Event dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENT_IDS = ("SCHEMA_MD", "DUPLICATE_MD", "ANOMALY_MD")

AGENT_META = {
    "SCHEMA_MD": {
        "subtitle": "Structure Analysis",
        "accent": "green",
        "bay_id": "HD-042-A",
        "task": "Analyzing column types and format inconsistencies...",
    },
    "DUPLICATE_MD": {
        "subtitle": "Entity Resolution",
        "accent": "purple",
        "bay_id": "HD-042-C",
        "task": "Finding potential duplicate clusters using vector search...",
    },
    "ANOMALY_MD": {
        "subtitle": "Statistical Scan",
        "accent": "green",
        "bay_id": "HD-042-B",
        "task": "Detecting outliers and unusual patterns...",
    },
}

PIPELINE_ORDER = (
    "intake",
    "diagnose",
    "chief",
    "repair",
    "verify",
    "discharge",
)


@dataclass
class AgentSnapshot:
    agent_id: str
    subtitle: str
    accent: str
    status: str = "PENDING"
    progress: int = 0
    queries: int = 0
    findings: int = 0
    latency_s: float = 0.0
    current_task: str = ""
    bay_id: str = ""
    bay_status: str = "PENDING"
    create_state: str = "pending"  # pending | complete
    query_state: str = "pending"  # pending | active | complete
    destroy_state: str = "pending"  # pending | complete
    bay_released: bool = False


@dataclass
class FeedItem:
    timestamp: str
    source: str
    message: str
    category: str  # all | agents | hotdata | repairs | system


@dataclass
class RunState:
    run_id: str = "042"
    patient_name: str = "PATIENT_042"
    patient_file: str = "customers.csv"
    pipeline_stage: str = "intake"
    schema_agent: AgentSnapshot = field(
        default_factory=lambda: _blank_agent("SCHEMA_MD")
    )
    duplicate_agent: AgentSnapshot = field(
        default_factory=lambda: _blank_agent("DUPLICATE_MD")
    )
    anomaly_agent: AgentSnapshot = field(
        default_factory=lambda: _blank_agent("ANOMALY_MD")
    )
    patient_health: str = "CRITICAL"
    health_metrics: dict[str, int] = field(
        default_factory=lambda: {
            "schema_integrity": 0,
            "validity": 0,
            "uniqueness": 0,
            "completeness": 0,
        }
    )
    diagnoses: dict[str, int] = field(
        default_factory=lambda: {
            "total": 0,
            "critical": 0,
            "review": 0,
            "auto_fix": 0,
        }
    )
    event_feed: list[FeedItem] = field(default_factory=list)
    hotdata_bays: dict[str, str] = field(default_factory=dict)
    parallel_mode: bool = True
    run_duration: float = 0.0
    dataset_rows: int = 15482
    dataset_cols: int = 18
    dataset_size: str = "2.4 MB"
    condition_note: str = "Stabilizing..."
    rocketride_label: str = "RocketRide Orchestrating..."
    live: bool = True
    clock_date: str = ""
    clock_time: str = ""

    def agent(self, agent_id: str) -> AgentSnapshot:
        if agent_id == "SCHEMA_MD":
            return self.schema_agent
        if agent_id == "DUPLICATE_MD":
            return self.duplicate_agent
        if agent_id == "ANOMALY_MD":
            return self.anomaly_agent
        raise KeyError(agent_id)

    def set_agent(self, snapshot: AgentSnapshot) -> None:
        if snapshot.agent_id == "SCHEMA_MD":
            self.schema_agent = snapshot
        elif snapshot.agent_id == "DUPLICATE_MD":
            self.duplicate_agent = snapshot
        elif snapshot.agent_id == "ANOMALY_MD":
            self.anomaly_agent = snapshot
        else:
            raise KeyError(snapshot.agent_id)

    def specialists_running(self) -> int:
        return sum(
            1
            for a in (self.schema_agent, self.duplicate_agent, self.anomaly_agent)
            if a.status in ("RUNNING", "QUERYING")
        )

    def agents(self) -> tuple[AgentSnapshot, AgentSnapshot, AgentSnapshot]:
        return self.schema_agent, self.duplicate_agent, self.anomaly_agent


def _blank_agent(agent_id: str) -> AgentSnapshot:
    meta = AGENT_META[agent_id]
    return AgentSnapshot(
        agent_id=agent_id,
        subtitle=meta["subtitle"],
        accent=meta["accent"],
        current_task=meta["task"],
        bay_id=meta["bay_id"],
    )


def _source_category(source: str) -> str:
    if source in AGENT_IDS:
        return "agents"
    if source == "HOTDATA":
        return "hotdata"
    if source in ("REPAIR", "VERIFY"):
        return "repairs"
    return "system"


def _append_feed(
    state: RunState,
    timestamp: str,
    source: str,
    message: str,
    category: str | None = None,
) -> None:
    if not message:
        return
    item = FeedItem(
        timestamp=timestamp or "--:--:--",
        source=source,
        message=message,
        category=category or _source_category(source),
    )
    # Keep chronological log; avoid exact duplicates at the same timestamp.
    for existing in state.event_feed:
        if (
            existing.timestamp == item.timestamp
            and existing.source == item.source
            and existing.message == item.message
        ):
            return
    state.event_feed.append(item)


def _fmt_latency(duration_ms: int | None, fallback: float) -> float:
    if duration_ms is None:
        return fallback
    return round(duration_ms / 1000.0, 1)


def apply_event(state: RunState, event: dict[str, Any]) -> RunState:
    """Apply one backend event. Mutates and returns the same RunState."""
    etype = event.get("type", "")
    ts = event.get("timestamp", "")
    agent_id = event.get("agent", "")
    message = event.get("message", "")

    if etype == "run_started":
        state.run_id = str(event.get("run_id", state.run_id))
        state.patient_name = event.get("patient_name", state.patient_name)
        state.patient_file = event.get("file", state.patient_file)
        if "rows" in event:
            state.dataset_rows = int(event["rows"])
        if "columns" in event:
            state.dataset_cols = int(event["columns"])
        if "size" in event:
            state.dataset_size = str(event["size"])
        state.pipeline_stage = "diagnose"
        state.parallel_mode = True
        state.live = True
        state.rocketride_label = "RocketRide Orchestrating..."
        if message:
            _append_feed(
                state,
                ts or "12:24:15",
                event.get("source", "ROCKETRIDE"),
                message,
                "system",
            )

    elif etype == "hotdata_created":
        bay_id = event.get("bay_id", "")
        if agent_id:
            agent = state.agent(agent_id)
            agent.bay_id = bay_id or agent.bay_id
            agent.bay_status = "READY"
            agent.create_state = "complete"
            agent.query_state = "pending"
            agent.destroy_state = "pending"
            agent.bay_released = False
            state.hotdata_bays[agent_id] = agent.bay_id
        if message:
            _append_feed(state, ts, "HOTDATA", message, "hotdata")

    elif etype == "agent_started":
        if agent_id:
            agent = state.agent(agent_id)
            agent.status = "RUNNING"
            agent.current_task = message or agent.current_task
            if agent.create_state == "complete":
                agent.query_state = "active"
                agent.bay_status = "QUERYING"
        if message and ts:
            _append_feed(state, ts, agent_id or "ROCKETRIDE", message)

    elif etype in ("agent_query", "agent_status"):
        if agent_id:
            agent = state.agent(agent_id)
            agent.status = "RUNNING"
            if "query_count" in event:
                agent.queries = int(event["query_count"])
            if "findings" in event:
                agent.findings = int(event["findings"])
            if "duration_ms" in event:
                agent.latency_s = _fmt_latency(event["duration_ms"], agent.latency_s)
            if "progress" in event:
                agent.progress = int(event["progress"])
            if message and event.get("source") != "HOTDATA":
                agent.current_task = message
            agent.bay_status = event.get("status", "querying").upper()
            if agent.bay_status == "QUERYING":
                agent.query_state = "active"
                agent.create_state = "complete"
        _append_feed(
            state,
            ts,
            event.get("source", "HOTDATA") if event.get("source") else "HOTDATA",
            message if event.get("source") == "HOTDATA" else "",
            "hotdata" if event.get("source") == "HOTDATA" else None,
        )

    elif etype == "diagnosis_found":
        if agent_id:
            agent = state.agent(agent_id)
            if "findings" in event:
                agent.findings = int(event["findings"])
            else:
                agent.findings += 1
        if "diagnoses" in event:
            state.diagnoses["total"] = int(event["diagnoses"])
        if "critical" in event:
            state.diagnoses["critical"] = int(event["critical"])
        if "review" in event:
            state.diagnoses["review"] = int(event["review"])
        if "auto_fix" in event:
            state.diagnoses["auto_fix"] = int(event["auto_fix"])
        _append_feed(state, ts, agent_id or "ROCKETRIDE", message, "agents")

    elif etype == "agent_completed":
        if agent_id:
            agent = state.agent(agent_id)
            agent.status = "DONE"
            agent.progress = 100
            agent.current_task = message or "Analysis complete."
            agent.query_state = "complete"
            agent.bay_status = "COMPLETE"
        _append_feed(state, ts, agent_id or "ROCKETRIDE", message or f"{agent_id} complete")

    elif etype == "hotdata_destroyed":
        if agent_id:
            agent = state.agent(agent_id)
            agent.create_state = "complete"
            agent.query_state = "complete"
            agent.destroy_state = "complete"
            agent.bay_released = True
            agent.bay_status = "RELEASED"
        bay_id = event.get("bay_id", "")
        _append_feed(
            state,
            ts,
            "HOTDATA",
            message or (f"{bay_id} released" if bay_id else "Hotdata bay destroyed"),
            "hotdata",
        )

    elif etype == "wave_completed":
        state.parallel_mode = False
        state.rocketride_label = "RocketRide wave complete"
        _append_feed(
            state,
            ts,
            "ROCKETRIDE",
            message or "Wave 1 complete. Handing off to Chief.",
            "system",
        )

    elif etype == "chief_started":
        state.pipeline_stage = "chief"
        state.rocketride_label = "RocketRide · Chief review"
        _append_feed(
            state,
            ts,
            "CHIEF",
            message or "Chief agent reconciling specialist findings...",
            "system",
        )

    elif etype == "conflict_found":
        _append_feed(
            state,
            ts,
            "CHIEF",
            message or "Conflict found between specialist diagnoses",
            "system",
        )

    elif etype == "chief_decision":
        _append_feed(
            state,
            ts,
            "CHIEF",
            message or "Chief approved repair plan",
            "system",
        )

    elif etype == "repair_started":
        state.pipeline_stage = "repair"
        state.rocketride_label = "RocketRide · Repairing"
        _append_feed(
            state,
            ts,
            "REPAIR",
            message or "Deterministic repair started",
            "repairs",
        )

    elif etype == "repair_verified":
        state.pipeline_stage = "verify"
        state.rocketride_label = "RocketRide · Verifying"
        _append_feed(
            state,
            ts,
            "VERIFY",
            message or "Repair verified",
            "repairs",
        )

    elif etype == "repair_rollback":
        state.pipeline_stage = "repair"
        _append_feed(
            state,
            ts,
            "REPAIR",
            message or "Repair rolled back",
            "repairs",
        )

    elif etype == "health_updated":
        for key in ("schema_integrity", "validity", "uniqueness", "completeness"):
            if key in event:
                state.health_metrics[key] = int(event[key])
        if "condition" in event:
            state.patient_health = str(event["condition"])
        if "condition_note" in event:
            state.condition_note = str(event["condition_note"])
        if "diagnoses" in event:
            state.diagnoses["total"] = int(event["diagnoses"])
        if "critical" in event:
            state.diagnoses["critical"] = int(event["critical"])
        if "review" in event:
            state.diagnoses["review"] = int(event["review"])
        if "auto_fix" in event:
            state.diagnoses["auto_fix"] = int(event["auto_fix"])

    elif etype == "run_completed":
        state.pipeline_stage = "discharge"
        state.live = False
        state.rocketride_label = "RocketRide · Discharged"
        state.patient_health = event.get("condition", "STABLE")
        state.condition_note = event.get("condition_note", "Cleared for discharge")
        _append_feed(
            state,
            ts,
            "ROCKETRIDE",
            message or "Run complete. Patient discharged.",
            "system",
        )

    return state
