import time, logging
from .config import settings

logging.basicConfig(level=getattr(logging, settings.effective_log_level, logging.INFO))
logger = logging.getLogger("worker")
logger.info("Worker starting with ENV=%s, LOG_LEVEL=%s, MONGO_DB=%s, USE_MOCK_OPENAI=%s",
            settings.env, settings.effective_log_level, settings.effective_mongo_db, settings.effective_use_mock_openai)

def main():
    while True:
        logger.debug("worker heartbeat...")
        time.sleep(5)

if __name__ == "__main__":
    main()
