from fastapi import APIRouter
from ..services.demo_store import SHELTERS

router = APIRouter(prefix="/api/shelters", tags=["shelters"])


@router.get("")
def list_shelters():
    return SHELTERS
