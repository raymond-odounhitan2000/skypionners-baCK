from typing import List
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings
import secrets


class Settings(BaseSettings):
    # Application Configuration
    APP_NAME: str = "Skypionners Backend API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Logging
    LOG_LEVEL: str = "INFO"

    @model_validator(mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, dict):
            cors_origins = v.get('BACKEND_CORS_ORIGINS')
            if isinstance(cors_origins, str):
                v['BACKEND_CORS_ORIGINS'] = [i.strip() for i in cors_origins.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

