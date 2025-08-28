import json
import os
from typing import Dict, Any
import httpx


def _api_key() -> str:
    try:
        from worker.config import get_settings  # type: ignore
        s = get_settings()
        for attr in ("openai_api_key", "OPENAI_API_KEY"):
            if hasattr(s, attr):
                return getattr(s, attr)
    except Exception:
        pass
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not configured")
    return key


def _model_name() -> str:
    try:
        from worker.config import get_settings  # type: ignore
        s = get_settings()
        if hasattr(s, "openai_model"):
            return getattr(s, "openai_model")
    except Exception:
        pass
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _build_messages(subject: str, description: str) -> list[dict]:
    system = (
        "You are an AI classifier for support tickets. "
        "Return ONLY compact JSON: {\"intent\": \"<label>\", \"confidence\": 0.0-1.0}."
    )
    user = f"Subject: {subject}\nDescription: {description}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _parse_json_maybe_codeblock(text: str) -> Dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        lines = [ln for ln in t.splitlines() if not ln.strip().startswith("```")]
        t = "\n".join(lines).strip()
    return json.loads(t)


def classify_with_openai(subject: str, description: str, timeout_s: float = 12.0) -> Dict[str, Any]:
    """Returns {"intent": str, "confidence": float, "model": str}."""
    model = _model_name()
    headers = {"Authorization": f"Bearer {_api_key()}"}
    body = {"model": model, "temperature": 0, "messages": _build_messages(subject, description)}
    with httpx.Client(timeout=timeout_s) as client:
        r = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        data = _parse_json_maybe_codeblock(content)
        intent = str(data["intent"]).strip()
        confidence = float(data["confidence"])
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence out of range")
        return {"intent": intent, "confidence": confidence, "model": model}
