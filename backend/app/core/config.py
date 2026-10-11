from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ClubHub API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes", "on"):
                return True
            if v.lower() in ("false", "0", "no", "off", "release"):
                return False
        return v

    # Database
    DATABASE_URL: str = "sqlite:///./clubhub.db"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def cors_origins(self) -> List[str]:
        return [self.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
