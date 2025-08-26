import os
import time
import pytest
import requests

pytestmark = pytest.mark.contract

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@pytest.mark.xfail(strict=True, reason="Step 4 not implemented: /ticket enqueue + Mongo persist + worker update")
def test_ticket_flow_contract():
    payload = {
        "subject": "Refund request",
        "description": "Charged twice"
    }
    # 1) Ingest ticket -> expect 202 and a ticket_id in response
    r = requests.post(f"{BASE_URL}/ticket", json=payload, timeout=5)
    assert r.status_code == 202
    data = r.json()
    ticket_id = data["ticket_id"]

    # 2) (Optional polling step) Wait briefly for worker to classify
    time.sleep(1.0)

    # 3) Fetch ticket back (Step 4 will implement a GET)
    g = requests.get(f"{BASE_URL}/ticket/{ticket_id}", timeout=5)
    assert g.status_code == 200
    ticket = g.json()
    assert ticket["subject"] == payload["subject"]
    assert "classification" in ticket and ticket["classification"] is not None
