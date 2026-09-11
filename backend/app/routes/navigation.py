from fastapi import APIRouter
from ..models import NavigationRequest, NavigationResponse, RouteCandidate

router = APIRouter(prefix="/api/navigation", tags=["navigation"])


@router.post("", response_model=NavigationResponse)
def navigation(payload: NavigationRequest):
    # Static MVP data. Replace with Google Routes API + hazard/polyline intersection later.
    routes = [
        RouteCandidate(
            id="route-a",
            destination_shelter_id="S1",
            travel_minutes=8,
            risk="HIGH",
            intersects_incident_ids=["I101"],
            recommended=False,
            reason="Fastest route, but it intersects a high-confidence road-flooding incident.",
        ),
        RouteCandidate(
            id="route-b",
            destination_shelter_id="S2",
            travel_minutes=14,
            risk="LOW",
            intersects_incident_ids=[],
            recommended=True,
            reason="Slightly longer, but avoids known high-severity incidents.",
        ),
        RouteCandidate(
            id="route-c",
            destination_shelter_id="S3",
            travel_minutes=17,
            risk="MEDIUM",
            intersects_incident_ids=["I103"],
            recommended=False,
            reason="Passes near a confirmed downed power line.",
        ),
    ]
    return NavigationResponse(recommended_shelter_id="S2", routes=routes)
