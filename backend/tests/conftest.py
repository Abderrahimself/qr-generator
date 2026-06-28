import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

# Settings() runs at import time and requires these vars (no defaults). CI has no
# .env file (it's git-ignored), so seed throwaway values before importing the app.
# setdefault means a real .env / real env vars still win for local runs.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("S3_ENDPOINT_URL", "http://localhost:3900")
os.environ.setdefault("S3_ACCESS_KEY", "test")
os.environ.setdefault("S3_SECRET_KEY", "test")

import pytest

from app.models.qr_code import QRCode
from app.repositories.interfaces import (
    CacheRepository,
    MetadataRepository,
    StorageRepository,
)


@pytest.fixture
def mock_cache() -> AsyncMock:
    return AsyncMock(spec=CacheRepository)


@pytest.fixture
def mock_metadata() -> AsyncMock:
    return AsyncMock(spec=MetadataRepository)


@pytest.fixture
def mock_storage() -> AsyncMock:
    return AsyncMock(spec=StorageRepository)


@pytest.fixture
def sample_qr_code() -> QRCode:
    qr = QRCode(
        original_url="https://example.com/",
        url_hash="0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7",
        object_key="0f115db062b7c0dd030b16878c99dea5c354b49dc37b38eb8846179c7783e9d7.png",
        format="png",
        size_bytes=1498,
    )
    qr.id = uuid.uuid4()
    qr.created_at = datetime.now(UTC)
    return qr
