"""
PM Internship Recommendation Engine - Backend Configuration
"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project
    PROJECT_NAME: str = "PM Internship Recommendation Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False

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
    ALLOWED_ORIGINS: list[str] = ["*"]

    @model_validator(mode='after')
    def validate_secret_key(self) -> 'Settings':
        if self.SECRET_KEY == "dev-secret-key-change-in-production":
            import warnings
            warnings.warn("⚠️  Using insecure default SECRET_KEY! Set SECRET_KEY in .env for production.")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
