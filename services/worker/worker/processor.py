import time
from typing import Dict, Any

from worker.queue.redis_queue import blpop_job, requeue_with_backoff
from worker.db.mongo import get_ticket, set_classification, mark_error
from worker.llm.openai_client import classify_with_openai

MAX_RETRIES = 2
BACKOFF_BASE_S = 0.5
IDEMPOTENT_SKIP_IF_CLASSIFIED = True


def _backoff(retries: int) -> float:
    return min(BACKOFF_BASE_S * (2 ** retries), 2.0)


def process_job(job: Dict[str, Any]) -> None:
    required = ("ticket_id", "subject", "description", "timestamp", "retries")
    if any(k not in job for k in required):
        if "ticket_id" in job:
            mark_error(job["ticket_id"], "job_invalid")
        return

    ticket_id = job["ticket_id"]
    t = get_ticket(ticket_id)
    if not t:
        mark_error(ticket_id, "ticket_not_found")
        return

    if IDEMPOTENT_SKIP_IF_CLASSIFIED and t.get("classification"):
        return

    retries = int(job.get("retries", 0))
    try:
        result = classify_with_openai(job["subject"], job["description"])
        set_classification(ticket_id, result, result["model"])
        return
    except Exception:
        if requeue_with_backoff(job, max_retries=MAX_RETRIES, retry_sleep_s=_backoff(retries)):
            return
        mark_error(ticket_id, "llm_failure")


def process_one_job(timeout: int = 5) -> bool:
    job = blpop_job(timeout=timeout)
    if not job:
        return False
    process_job(job)
    return True
