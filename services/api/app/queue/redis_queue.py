import json
import os
from typing import Dict, Any

from redis import Redis

# Keep key stable across services (documented in Step-2 contracts)
QUEUE_KEY = "classification:queue"

_redis_client: Redis | None = None

def _redis_url() -> str:
    try:
        from app.config import get_settings  # type: ignore
        s = get_settings()
        for attr in ("redis_url", "redis_uri", "REDIS_URL", "REDIS_URI"):
            if hasattr(s, attr):
                return getattr(s, attr)
    except Exception:
        pass
    return os.getenv("REDIS_URL", os.getenv("REDIS_URI", "redis://redis:6379/0"))

def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(_redis_url(), decode_responses=True)
    return _redis_client

def enqueue_classification_job(job: Dict[str, Any]) -> None:
    """
    Push a job onto the classification queue.

    Contract (immutable for this substep):
    {
      "ticket_id": "<ObjectId>",
      "subject": "...",
      "description": "...",
      "timestamp": "<ISO8601>",
      "retries": 0
    }
    """
    payload = json.dumps(job, separators=(",", ":"))
    # FIFO semantics: append to the right; worker can BLPOP from the left
    get_redis().rpush(QUEUE_KEY, payload)
