from fastapi import APIRouter, Query
from ..services.demo_store import REPORTS

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("")
def list_reports(zone_id: str | None = Query(default=None)):
    if zone_id:
        return [item for item in REPORTS if item["zone_id"] == zone_id]
    return REPORTS
