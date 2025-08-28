import time, logging
from .config import settings
from worker.processor import process_one_job


logging.basicConfig(level=getattr(logging, settings.effective_log_level, logging.INFO))
logger = logging.getLogger("worker")
logger.info("Worker starting with ENV=%s, LOG_LEVEL=%s, MONGO_DB=%s, USE_MOCK_OPENAI=%s",
            settings.env, settings.effective_log_level, settings.effective_mongo_db, settings.effective_use_mock_openai)

def main():
    while True:
        processed = process_one_job(timeout=2)
        if not processed:
            time.sleep(0.25)

if __name__ == "__main__":
    main()
