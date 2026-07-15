"""Backend configuration from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # API Configuration
    ANTHROPIC_API_KEY: str
    MODEL: str = "claude-haiku-4-5-20251001"

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./queryengine.db"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # CORS Configuration
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Cost & Quota Configuration
    DAILY_TOKEN_LIMIT: int = 100000  # Tokens per day
    COST_PER_1K_TOKENS: float = 0.003  # $0.003 per 1K tokens for Haiku

    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0
    RETRY_BACKOFF: float = 2.0

    # Query Execution Security
    QUERY_TIMEOUT_SECONDS: int = 10
    MAX_QUERY_ROWS: int = 10000
    MAX_QUERY_COMPLEXITY: int = 3

    # Test Execution Configuration
    TEST_TIMEOUT_SECONDS: int = 5

    class Config:
        env_file = ".env"  # Loads from current directory (backend/.env when running from backend/)
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
