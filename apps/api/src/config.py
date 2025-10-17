"""
Configuration settings for the Verification API
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Union
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

    # CORS - can be set as comma-separated string in env var
    cors_origins: Union[List[str], str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "https://iaindex.com"
        ]
    )

    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # Supabase
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2

    # Rate Limiting
    rate_limit_per_minute: str = "60/minute"
    rate_limit_per_hour: str = "1000/hour"

    # Verification
    verification_token_expiry_hours: int = 48
    dns_verification_prefix: str = "iaindex-verification"

    # Cloudflare (for rendering service)
    cloudflare_account_id: str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
    cloudflare_api_token: str = os.getenv("CLOUDFLARE_API_TOKEN", "")

    # S3 (for snapshots)
    s3_bucket_snapshots: str = os.getenv("S3_BUCKET_SNAPSHOTS", "aiindex-snapshots")

    # OpenAI (for embeddings)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Pinecone (for vector search)
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "aiindex-vectors")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")

    # C2PA (for provenance)
    c2pa_private_key_path: str = os.getenv("C2PA_PRIVATE_KEY_PATH", "")
    c2pa_certificate_path: str = os.getenv("C2PA_CERTIFICATE_PATH", "")

    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle comma-separated string from env var
            if v:
                return [origin.strip() for origin in v.split(',')]
            # Empty string means use defaults
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "https://iaindex.com"
            ]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()
