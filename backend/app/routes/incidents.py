from fastapi import APIRouter, HTTPException, Query
from ..services.demo_store import INCIDENTS

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("")
def list_incidents(zone_id: str | None = Query(default=None)):
    if zone_id:
        return [item for item in INCIDENTS if item["zone_id"] == zone_id]
    return INCIDENTS


@router.get("/{incident_id}")
def get_incident(incident_id: str):
    for item in INCIDENTS:
        if item["id"] == incident_id:
            return item
    raise HTTPException(status_code=404, detail="Incident not found")
