"""
PM Internship Recommendation Engine - Backend Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project
    PROJECT_NAME: str = "PM Internship Recommendation Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pm_internship"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # AI APIs
    GROQ_API_KEY: str | None = None

    # Supabase (Media Storage)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    # ML Engine
    ML_MODEL_PATH: str = "./ml/models"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CONTENT_WEIGHT: float = 0.6
    COLLABORATIVE_WEIGHT: float = 0.4
    TOP_K_RECOMMENDATIONS: int = 5

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
