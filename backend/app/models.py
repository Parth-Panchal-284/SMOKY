from typing import Literal
from pydantic import BaseModel, Field

RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
IncidentStatus = Literal["UNVERIFIED", "CORROBORATED", "CONFIRMED", "RESOLVED"]


class Zone(BaseModel):
    id: str
    name: str
    center_lat: float
    center_lng: float
    risk_level: RiskLevel
    incident_count: int = 0


class Shelter(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    capacity: int
    available_capacity: int
    status: str
    zone_id: str


class Report(BaseModel):
    id: str
    source_type: str
    source_name: str
    timestamp: str
    lat: float
    lng: float
    zone_id: str
    text: str
    official: bool = False


class Incident(BaseModel):
    id: str
    zone_id: str
    title: str
    incident_type: str
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    status: IncidentStatus
    lat: float
    lng: float
    source_count: int
    official_confirmation: bool
    summary: str
    last_updated: str
    evidence_report_ids: list[str] = []


class ChatRequest(BaseModel):
    message: str
    lat: float | None = None
    lng: float | None = None


class ChatResponse(BaseModel):
    answer: str
    incident_ids: list[str] = []
    suggested_action: str | None = None


class NavigationRequest(BaseModel):
    origin_lat: float
    origin_lng: float
    destination_shelter_id: str | None = None


class RouteCandidate(BaseModel):
    id: str
    destination_shelter_id: str
    travel_minutes: int
    risk: Literal["LOW", "MEDIUM", "HIGH"]
    intersects_incident_ids: list[str] = []
    recommended: bool = False
    reason: str


class NavigationResponse(BaseModel):
    recommended_shelter_id: str
    routes: list[RouteCandidate]
