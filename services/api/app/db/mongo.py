import os
from datetime import datetime, timezone
from typing import Tuple, Dict, Any

from pymongo import MongoClient
from bson import ObjectId

try:
    from app.config import get_settings  # type: ignore
    _settings = get_settings()
except Exception:
    _settings = None  # Will use env vars

_client: MongoClient | None = None

def _mongo_uri() -> str:
    # Try Settings first, then env, then docker-compose default
    for attr in ("mongo_uri", "MONGO_URI", "effective_mongo_uri"):
        if _settings and hasattr(_settings, attr):
            return getattr(_settings, attr)
    return os.getenv("MONGO_URI", "mongodb://mongo:27017")

def _mongo_db_name() -> str:
    for attr in ("mongo_db", "effective_mongo_db"):
        if _settings and hasattr(_settings, attr):
            return getattr(_settings, attr)
    return os.getenv("MONGO_DB", "ai_ticketing")

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(_mongo_uri())
    return _client

def get_db():
    return get_client()[_mongo_db_name()]

def tickets_col():
    return get_db()["tickets"]

def _now_iso8601() -> str:
    # ISO 8601 with Z suffix for UTC (matches contract)
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def insert_ticket(subject: str, description: str) -> Tuple[ObjectId, Dict[str, Any]]:
    doc = {
        "subject": subject,
        "description": description,
        "status": "pending",
        "created_at": _now_iso8601(),
        "updated_at": _now_iso8601(),
    }
    result = tickets_col().insert_one(doc)
    inserted_id: ObjectId = result.inserted_id
    # ensure the contract shape includes _id when read later
    doc["_id"] = inserted_id
    return inserted_id, doc