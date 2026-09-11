from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import zones, incidents, reports, shelters, chat, navigation

app = FastAPI(title="SMOKY Disaster Intelligence API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones.router)
app.include_router(incidents.router)
app.include_router(reports.router)
app.include_router(shelters.router)
app.include_router(chat.router)
app.include_router(navigation.router)


@app.get("/health")
def health():
    return {"status": "ok", "mode": "simulated-demo"}
