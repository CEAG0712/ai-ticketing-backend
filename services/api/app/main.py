import logging
from fastapi import FastAPI
from .config import settings
from app.routes.tickets import router as tickets_router  # noqa: E402


logging.basicConfig(level=getattr(logging, settings.effective_log_level, logging.INFO))
logger = logging.getLogger("api")
logger.info("API starting with ENV=%s, LOG_LEVEL=%s, MONGO_DB=%s, USE_MOCK_OPENAI=%s",
            settings.env, settings.effective_log_level, settings.effective_mongo_db, settings.effective_use_mock_openai)

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(tickets_router)
