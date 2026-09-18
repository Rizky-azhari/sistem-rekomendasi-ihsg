from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "IHSG Smart Stock Recommendation System"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Supabase / PostgreSQL settings
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""
    DATABASE_URL: str = ""
    JWT_SECRET: str = "ihsg-smart-stock-secret-jwt-key-2026"


    # SMTP Email Settings (for verification code delivery)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""

    @property
    def DEFAULT_IDX_STOCKS(self) -> List[str]:
        """Returns IDX80 tickers — the only supported universe."""
        from app.config.idx80_tickers import get_all_idx80_tickers
        return get_all_idx80_tickers()

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()
