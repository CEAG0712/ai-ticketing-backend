import json
import os
import time
from typing import Any, Dict, Optional
from redis import Redis

QUEUE_KEY = "classification:queue"  # contract with API producer

_redis: Optional[Redis] = None


def _redis_url() -> str:
    try:
        from worker.config import get_settings  # type: ignore
        s = get_settings()
        for attr in ("redis_url", "redis_uri", "REDIS_URL", "REDIS_URI"):
            if hasattr(s, attr):
                return getattr(s, attr)
    except Exception:
        pass
    return os.getenv("REDIS_URL", os.getenv("REDIS_URI", "redis://redis:6379/0"))


def get_client() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(_redis_url(), decode_responses=True)
    return _redis


def blpop_job(timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Blocking left-pop to pair with API's RPUSH (FIFO)."""
    item = get_client().blpop(QUEUE_KEY, timeout=timeout)
    if not item:
        return None
    _, raw = item
    return json.loads(raw)


def requeue_with_backoff(job: Dict[str, Any], max_retries: int, retry_sleep_s: float = 0.0) -> bool:
    """Increment job['retries'] and requeue at tail; returns False if max exceeded."""
    retries = int(job.get("retries", 0)) + 1
    if retries > max_retries:
        return False
    job["retries"] = retries
    if retry_sleep_s > 0:
        time.sleep(retry_sleep_s)
    get_client().rpush(QUEUE_KEY, json.dumps(job, separators=(",", ":")))
    return True
