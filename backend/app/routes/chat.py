from fastapi import APIRouter
from ..models import ChatRequest, ChatResponse
from ..services.demo_store import INCIDENTS, SHELTERS

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest):
    text = payload.message.lower()
    active = [i for i in INCIDENTS if i["status"] != "RESOLVED"]
    high_risk = [i for i in active if i["severity"] >= 4]

    if any(word in text for word in ["shelter", "evacuate", "where should i go"]):
        open_shelters = sorted(
            [s for s in SHELTERS if s["status"] == "OPEN"],
            key=lambda s: s["available_capacity"],
            reverse=True,
        )
        shelter = open_shelters[0]
        return ChatResponse(
            answer=(
                f"For this demo, {shelter['name']} is the preferred shelter because it is open "
                f"with {shelter['available_capacity']} spaces available. Route safety still needs to be checked "
                "against current incidents before travel."
            ),
            incident_ids=[i["id"] for i in high_risk],
            suggested_action="Open safe-route planning",
        )

    if any(word in text for word in ["drive", "route", "travel", "north"]):
        return ChatResponse(
            answer=(
                "Travel is possible in the demo scenario, but avoid routes intersecting the Downtown/SJSU "
                "road-flooding incident. Use the route planner to compare candidate routes against active hazards."
            ),
            incident_ids=[i["id"] for i in high_risk],
            suggested_action="Compare safe routes",
        )

    return ChatResponse(
        answer=(
            f"There are {len(active)} active simulated incidents across the four demo zones, "
            f"including {len(high_risk)} high-severity incidents. I can help with nearby hazards, shelters, "
            "or safe travel."
        ),
        incident_ids=[i["id"] for i in high_risk],
    )
