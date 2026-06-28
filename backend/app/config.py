from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root is two levels up from this file (backend/app/config.py → qr-generator/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # FastAPI
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"

    # PostgreSQL
    database_url: str

    # Valkey
    valkey_host: str = "localhost"
    valkey_port: int = 6379
    cache_ttl_seconds: int = 86400

    # Garage (S3-compatible)
    s3_endpoint_url: str
    s3_public_url: str = ""   # Public-facing URL for presigned URLs (defaults to s3_endpoint_url)
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str = "qr-codes"
    s3_region: str = "garage"

    @property
    def s3_presign_url(self) -> str:
        return self.s3_public_url or self.s3_endpoint_url

    # QR defaults
    qr_default_format: str = "png"
    qr_default_size: int = 10
    qr_default_border: int = 4

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()  # type: ignore[call-arg]  # values come from env/.env at runtime
