import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from app.models.ticket import TicketCreate
from app.db.mongo import insert_ticket
from app.queue.redis_queue import enqueue_classification_job

router = APIRouter()

def _now_iso8601() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

@router.post("/ticket", status_code=status.HTTP_202_ACCEPTED)
def create_ticket(req: TicketCreate):
    """
    POST /ticket
    - Validate input
    - Persist in Mongo with status="pending"
    - Enqueue Redis job (exact payload contract)
    - Return 202 with {ticket_id, trace_id}
    """
    trace_id = str(uuid.uuid4())

    try:
        ticket_id, _doc = insert_ticket(subject=req.subject, description=req.description)
    except Exception as e:  # Mongo write failure → 500
        raise HTTPException(status_code=500, detail="ticket_persist_failed") from e

    job = {
        "ticket_id": str(ticket_id),            # <ObjectId> string
        "subject": req.subject,
        "description": req.description,
        "timestamp": _now_iso8601(),
        "retries": 0,
    }

    try:
        enqueue_classification_job(job)
    except Exception as e:
        # Queue is part of API boundary: respond 503 so caller can retry.
        # The ticket is durable in Mongo by design.
        raise HTTPException(status_code=503, detail="queue_unavailable") from e

    return {"ticket_id": str(ticket_id), "trace_id": trace_id}
