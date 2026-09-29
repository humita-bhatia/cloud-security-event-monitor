from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .database import init_db, recent_events, recent_alerts, counts
from .queue import publish_event

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Cloud Security Event Monitor")

SERVERS = {
    "Server-01": "10.0.0.11",
    "Server-02": "10.0.0.12",
    "Server-03": "10.0.0.13",
}
EVENT_TYPES = ("LOGIN_SUCCESS", "LOGIN_FAILURE", "FILE_ACCESS")


class EventIn(BaseModel):
    server: Literal["Server-01", "Server-02", "Server-03"]
    event_type: Literal["LOGIN_SUCCESS", "LOGIN_FAILURE", "FILE_ACCESS"]
    ip: str | None = None


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events")
def create_event(event: EventIn):
    payload = event.model_dump()
    payload["ip"] = payload.get("ip") or SERVERS[payload["server"]]
    payload["timestamp"] = datetime.now(timezone.utc).isoformat()
    publish_event(payload)
    return {"message": "Event queued", "event": payload}


@app.get("/api/events")
def events():
    return recent_events()


@app.get("/api/alerts")
def alerts():
    return recent_alerts()


@app.get("/api/stats")
def stats():
    return counts()


@app.get("/api/servers")
def servers():
    return [{"name": name, "ip": ip} for name, ip in SERVERS.items()]


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(BASE_DIR / "static" / "index.html")
