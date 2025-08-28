from datetime import datetime, timezone
import os
from typing import Any, Dict, Optional
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId

_client: Optional[MongoClient] = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mongo_uri() -> str:
    try:
        from worker.config import get_settings  # type: ignore
        s = get_settings()
        for attr in ("mongo_uri", "effective_mongo_uri", "MONGO_URI"):
            if hasattr(s, attr):
                return getattr(s, attr)
    except Exception:
        pass
    return os.getenv("MONGO_URI", "mongodb://mongo:27017")


def _mongo_db_name() -> str:
    try:
        from worker.config import get_settings  # type: ignore
        s = get_settings()
        for attr in ("mongo_db", "effective_mongo_db", "MONGO_DB"):
            if hasattr(s, attr):
                return getattr(s, attr)
    except Exception:
        pass
    return os.getenv("MONGO_DB", "ai_ticketing")


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(_mongo_uri())
    return _client


def tickets():
    return get_client()[_mongo_db_name()]["tickets"]


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    oid = ObjectId(ticket_id) if not isinstance(ticket_id, ObjectId) else ticket_id
    return tickets().find_one({"_id": oid})


def set_classification(ticket_id: str, result: Dict[str, Any], model: str) -> Dict[str, Any]:
    """Idempotent write of classification block + status + updated_at."""
    oid = ObjectId(ticket_id)
    update = {
        "$set": {
            "classification": {
                "intent": result["intent"],
                "confidence": float(result["confidence"]),
                "model": model,
                "timestamp": _now_iso(),
            },
            "status": "classified",
            "updated_at": _now_iso(),
        }
    }
    return tickets().find_one_and_update(
        {"_id": oid}, update, return_document=ReturnDocument.AFTER, upsert=False
    )


def mark_error(ticket_id: str, error_type: str) -> Dict[str, Any]:
    oid = ObjectId(ticket_id)
    update = {
        "$set": {
            "status": "error",
            "error": {"type": error_type, "timestamp": _now_iso()},
            "updated_at": _now_iso(),
        }
    }
    return tickets().find_one_and_update(
        {"_id": oid}, update, return_document=ReturnDocument.AFTER, upsert=False
    )
