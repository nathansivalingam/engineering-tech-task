import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from google.cloud import firestore

app = FastAPI(title="Bright OS Tech Task")
API_KEY = os.getenv("API_KEY", "dev-key") # defaults to "dev-key" for local dev/testing

# Accepts/Rejects Incoming Requests Based on API Key
def require_api_key(x_api_key: str = Header(default="")) -> None:
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Firestore Connection
def get_db():
    project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT")
    if not project:
        raise RuntimeError("Missing GOOGLE_CLOUD_PROJECT (or GCLOUD_PROJECT) env var")
    return firestore.Client(project=project)

# Model Validates Payload Structure and Data Types
class HealthDataIn(BaseModel):
    timestamp: datetime
    steps: int = Field(ge=0)
    calories: float = Field(ge=0)
    sleepHours: float = Field(ge=0)

# Converts DD-MM-YYYY String to UTC Datetime
def parse_ddmmyyyy(date_str: str) -> datetime:
    try:
        dt = datetime.strptime(date_str, "%d-%m-%Y")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must be in DD-MM-YYYY format")

# Ensures Datetime is in UTC
def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

# Feature 1: User Data Ingestion
@app.post("/users/{userId}/health-data", dependencies=[Depends(require_api_key)])
def ingest_health_data(userId: str, payload: HealthDataIn):
    client = get_db()

    ts = to_utc(payload.timestamp)

    doc_ref = (
        client.collection("users")
        .document(userId)
        .collection("healthData")
        .document()
    )

    doc_ref.set(
        {
            "timestamp": ts,
            "steps": payload.steps,
            "calories": payload.calories,
            "sleepHours": payload.sleepHours,
        }
    )

    return {"status": "ok", "id": doc_ref.id}


# Feature 2: User Data Retrieval
@app.get("/users/{userId}/health-data", dependencies=[Depends(require_api_key)])
def get_health_data(
    userId: str,
    start: str = Query(..., description="DD-MM-YYYY"),
    end: str = Query(..., description="DD-MM-YYYY"),
    cursor: Optional[str] = Query(None, description="Firestore doc id cursor"),
):
    start_dt = parse_ddmmyyyy(start)
    end_dt_exclusive = parse_ddmmyyyy(end) + timedelta(days=1)

    client = get_db()
    col = client.collection("users").document(userId).collection("healthData")

    q = (
        col.where("timestamp", ">=", start_dt)
        .where("timestamp", "<", end_dt_exclusive)
        .order_by("timestamp")
        .limit(50)
    )

    # Pagination with Cursor
    if cursor:
        cursor_doc = col.document(cursor).get()
        if not cursor_doc.exists:
            raise HTTPException(status_code=400, detail="Invalid cursor")
        q = q.start_after(cursor_doc)

    docs = list(q.stream())

    items: list[dict[str, Any]] = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        ts = data.get("timestamp")
        if isinstance(ts, datetime):
            data["timestamp"] = ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        items.append(data)

    next_cursor = docs[-1].id if len(docs) == 50 else None
    return {"items": items, "nextCursor": next_cursor}


# Feature 3: Basic Aggregation
@app.get("/users/{userId}/summary", dependencies=[Depends(require_api_key)])
def get_summary(
    userId: str,
    start: str = Query(..., description="DD-MM-YYYY"),
    end: str = Query(..., description="DD-MM-YYYY"),
):
    start_dt = parse_ddmmyyyy(start)
    end_dt_exclusive = parse_ddmmyyyy(end) + timedelta(days=1)

    client = get_db()
    col = client.collection("users").document(userId).collection("healthData")

    q = (
        col.where("timestamp", ">=", start_dt)
        .where("timestamp", "<", end_dt_exclusive)
        .stream()
    )

    total_steps = 0
    calories_sum = 0.0
    sleep_sum = 0.0
    n = 0

    for d in q:
        data = d.to_dict()
        total_steps += int(data.get("steps", 0))
        calories_sum += float(data.get("calories", 0))
        sleep_sum += float(data.get("sleepHours", 0))
        n += 1

    return {
        "totalSteps": total_steps,
        "averageCalories": (calories_sum / n) if n else 0.0,
        "averageSleepHours": (sleep_sum / n) if n else 0.0,
        "count": n,
    }
