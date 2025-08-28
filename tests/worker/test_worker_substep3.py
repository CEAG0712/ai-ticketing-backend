import os, time, json, sys, pathlib
from urllib.parse import urljoin
import requests
from pymongo import MongoClient
from redis import Redis
from bson import ObjectId

# Make the 'worker' package importable
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2] / "services" / "worker"))

API_BASE  = os.getenv("API_BASE", "http://localhost:8000")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB", "ai_ticketing_dev")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

from worker.processor import process_one_job, MAX_RETRIES
# import worker.llm.openai_client as openai_client
import worker.processor as worker_processor

def _flush_queue():
    Redis.from_url(REDIS_URL, decode_responses=True).delete("classification:queue")

def _post_ticket(subject="Refund request", description="Charged twice") -> str:
    r = requests.post(urljoin(API_BASE, "/ticket"), json={"subject": subject, "description": description}, timeout=5)
    r.raise_for_status()
    return r.json()["ticket_id"]

def _mongo_ticket(ticket_id: str):
    return MongoClient(MONGO_URI)[MONGO_DB]["tickets"].find_one({"_id": ObjectId(ticket_id)})

def test_worker_classifies_ticket_success(monkeypatch):
    _flush_queue()
    tid = _post_ticket()

    def fake_classify(subject, description, timeout_s=12.0):
        return {"intent": "billing/refund", "confidence": 0.92, "model": "gpt-4o-mini"}
    monkeypatch.setattr(worker_processor, "classify_with_openai", fake_classify)

    assert process_one_job(timeout=2) is True

    doc = _mongo_ticket(tid)
    assert doc["status"] == "classified"
    assert doc["classification"]["intent"] == "billing/refund"
    assert 0.0 <= doc["classification"]["confidence"] <= 1.0
    assert doc["classification"]["timestamp"].endswith("Z")

def test_worker_retries_then_marks_error(monkeypatch):
    _flush_queue()
    tid = _post_ticket("Network issue", "Router keeps rebooting")

    def flaky(*args, **kwargs):
        raise TimeoutError("simulated")
    monkeypatch.setattr(worker_processor, "classify_with_openai", flaky)

    for _ in range(MAX_RETRIES + 1):
        process_one_job(timeout=1)
        time.sleep(0.05)

    doc = _mongo_ticket(tid)
    assert doc["status"] == "error"
