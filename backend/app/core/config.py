"""Application configuration settings using Pydantic Settings.
"""

import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_default_artifacts_dir() -> str:
    if getattr(sys, "frozen", False):
        bundle_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidate = bundle_dir / "ml" / "artifacts"
        if candidate.exists():
            return str(candidate)
        candidate_internal = bundle_dir / "_internal" / "ml" / "artifacts"
        if candidate_internal.exists():
            return str(candidate_internal)
    return "ml/artifacts"


def _resolve_default_data_dir() -> str:
    if getattr(sys, "frozen", False):
        bundle_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        candidate = bundle_dir / "ml" / "data"
        if candidate.exists():
            return str(candidate)
        candidate_internal = bundle_dir / "_internal" / "ml" / "data"
        if candidate_internal.exists():
            return str(candidate_internal)
    return "ml/data"


class Settings(BaseSettings):
    """Global configuration settings for MailShield."""

    PROJECT_NAME: str = "MailShield"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "2.1.0"
    ENVIRONMENT: str = "development"  # "development", "production", "desktop"

    # Security & Auth
    SECRET_KEY: str = "mailshield-insecure-default-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./mailshield.db"

    # ML Artifacts and Data directory
    ARTIFACTS_DIR: str = _resolve_default_artifacts_dir()
    DATA_DIR: str = _resolve_default_data_dir()
    DEFAULT_MODEL: str = "logistic_regression"
    DEFAULT_THRESHOLD: float = 0.5

    # File uploads
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: list[str] = [".txt", ".eml"]

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Desktop mode flag
    MAILSHIELD_MODE: str = "standard"  # "standard", "desktop"

    # Google OAuth 2.0 & Gmail Integration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI_WEB: str = "http://localhost:5173/gmail/callback"
    GOOGLE_REDIRECT_URI_DESKTOP: str = "http://127.0.0.1:8000/api/v1/gmail/callback/desktop"

    # Dedicated Token Encryption Keys
    TOKEN_ENCRYPTION_KEY: str = ""
    TOKEN_ENCRYPTION_KEY_FALLBACK: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
