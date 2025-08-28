import os
import time
import json
from urllib.parse import urljoin

import requests
from pymongo import MongoClient
from redis import Redis

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ai_ticketing")
REDIS_URL = os.getenv("REDIS_URL", os.getenv("REDIS_URI", "redis://localhost:6379/0"))

def test_post_ticket_contract_and_enqueue():
    # 1) Call API
    payload = {"subject": "Refund request", "description": "Charged twice"}
    r = requests.post(urljoin(API_BASE, "/ticket"), json=payload, timeout=5)
    assert r.status_code == 202
    body = r.json()
    assert set(body.keys()) == {"ticket_id", "trace_id"}
    assert len(body["ticket_id"]) >= 24
    assert len(body["trace_id"]) >= 8

    # 2) Mongo doc exists with status and timestamps
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    doc = db["tickets"].find_one({"_id": body["ticket_id"]})  # if _id is ObjectId string, fallback:
    if not doc:
        from bson import ObjectId
        doc = db["tickets"].find_one({"_id": ObjectId(body["ticket_id"])})
    assert doc is not None
    assert doc["status"] == "pending"
    assert isinstance(doc["created_at"], str) and "T" in doc["created_at"]
    assert isinstance(doc["updated_at"], str) and "T" in doc["updated_at"]

    # 3) Redis has a job with exact payload shape (allow brief propagation time)
    time.sleep(0.2)
    rds = Redis.from_url(REDIS_URL, decode_responses=True)
    # Peek the tail (most recent item)
    raw = rds.lindex("classification:queue", -1)
    assert raw is not None
    job = json.loads(raw)
    assert job["ticket_id"] == body["ticket_id"]
    assert job["subject"] == payload["subject"]
    assert job["description"] == payload["description"]
    assert job["retries"] == 0
    assert isinstance(job["timestamp"], str) and "T" in job["timestamp"]