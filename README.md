# SMOKY

SMOKY is a hackathon prototype for geographically organized disaster intelligence and safer navigation.

The core product turns fragmented reports from public, citizen, responder, mapping, and official sources into evolving geographic incidents. Source connectors stay source-specific at ingestion, but analysis is organized by geographic zone so evidence from different sources can corroborate the same physical event.

## Current milestone

This first scaffold contains:

- Four simulated San Jose zones.
- Simulated reports from X, Instagram, Facebook, citizens, and responders.
- Four sample incidents with confidence/status/evidence metadata.
- Four demo shelters.
- FastAPI endpoints for zones, incidents, reports, shelters, chat, and navigation.
- React/Vite dashboard with zone filtering, live situation map mock, incident feed, evidence drawer, and chat shell.
- Static hazard-aware route comparison endpoint.
- Integration placeholders for RocketRide, HotData, Rote, Google Maps, and Snyk.

All current disaster data is simulated and should be clearly presented as demo data.

## Architecture

```text
Source adapters -> normalized reports -> geographic zone routing
                                     -> RocketRide zone analysis
                                     -> HotData isolated per-run analytics
                                     -> canonical incident state
                                     -> dashboard / chat / navigation

Successful response procedure -> Rote Play
Application/dependency security -> Snyk
```

## Run backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Next milestone

1. Connect RocketRide Cloud.
2. Create `zone_analysis.pipe`.
3. Add HotData node and load one zone's normalized reports per pipeline run.
4. Run Z1-Z4 analyses concurrently from the backend.
5. Replace static incidents with pipeline output.
6. Add Google Maps/Routes for real map visualization and candidate routes.
7. Add simulated timed event ingestion.
8. Capture one successful flood assessment procedure with Rote.
9. Run Snyk on the repo.
