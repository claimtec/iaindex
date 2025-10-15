"""
Configuration settings for the Verification API
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    app_name: str = "IA Index Verification API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://iaindex.com"
    ]

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # Rate Limiting
    rate_limit_per_minute: str = "60/minute"
    rate_limit_per_hour: str = "1000/hour"

    # Verification
    verification_token_expiry_hours: int = 48
    dns_verification_prefix: str = "iaindex-verification"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
