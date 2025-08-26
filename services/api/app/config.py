from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os


class Settings(BaseSettings):

    env:str = "dev"
    log_level: Optional[str] = None

    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: Optional[str] = None
    mongo_db_dev: str = "ai_ticketing_dev"
    mongo_db_test: str = "ai_ticketing_test"

    # Redis
    redis_uri: str = "redis://redis:6379/0"

    use_mock_openai: Optional[bool] = None

    model_config = SettingsConfigDict(env_file=".env" if os.getenv("LOAD_DOTENV") == "1" else None,
        extra="ignore"
    )

    @property
    def effective_log_level(self) -> str:
        if self.log_level:
            return self.log_level
        return "INFO" if self.env == "dev" else "WARNING"

    @property
    def effective_mongo_db(self) -> str:
        if self.mongo_db:
            return self.mongo_db
        return self.mongo_db_dev if self.env == "dev" else self.mongo_db_test

    @property
    def effective_use_mock_openai(self) -> bool:
        if self.use_mock_openai is not None:
            return bool(self.use_mock_openai)
        return self.env == "test"

settings = Settings()