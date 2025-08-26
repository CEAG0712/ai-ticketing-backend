import os
import requests
import pytest

pytestmark = pytest.mark.smoke

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_healthz_smoke():
    r = requests.get(f"{BASE_URL}/healthz", timeout=5)
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True