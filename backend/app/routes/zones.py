from fastapi import APIRouter
from ..services.demo_store import zone_with_counts

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("")
def list_zones():
    return zone_with_counts()
