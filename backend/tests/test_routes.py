import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routes.qr import get_qr_service
from app.schemas.qr import QRCodeResponse


def _make_response(**overrides) -> QRCodeResponse:
    defaults = {
        "id": uuid.uuid4(),
        "url": "https://example.com/",
        "image_url": "https://presigned.url/qr.png",
        "format": "png",
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(overrides)
    return QRCodeResponse(**defaults)


@pytest.fixture
def mock_service() -> AsyncMock:
    return AsyncMock()


@pytest_asyncio.fixture
async def client(mock_service: AsyncMock):
    app.dependency_overrides[get_qr_service] = lambda: mock_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            response = await c.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGenerateEndpoint:
    @pytest.mark.asyncio
    async def test_generate_success(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        expected = _make_response()
        mock_service.generate.return_value = expected

        response = await client.post("/api/generate", json={"url": "https://example.com"})

        assert response.status_code == 201
        assert response.json()["url"] == "https://example.com/"

    @pytest.mark.asyncio
    async def test_generate_invalid_url(self, client: AsyncClient) -> None:
        response = await client.post("/api/generate", json={"url": "not-a-url"})

        assert response.status_code == 422


class TestHistoryEndpoint:
    @pytest.mark.asyncio
    async def test_history(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        mock_service.list_history.return_value = [_make_response(), _make_response()]

        response = await client.get("/api/history")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetQREndpoint:
    @pytest.mark.asyncio
    async def test_get_existing(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        qr = _make_response()
        mock_service.get_by_id.return_value = qr

        response = await client.get(f"/api/qr/{qr.id}")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_missing(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        mock_service.get_by_id.return_value = None

        response = await client.get(f"/api/qr/{uuid.uuid4()}")

        assert response.status_code == 404


class TestDeleteEndpoint:
    @pytest.mark.asyncio
    async def test_delete_existing(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        mock_service.delete.return_value = True

        response = await client.delete(f"/api/qr/{uuid.uuid4()}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_missing(self, client: AsyncClient, mock_service: AsyncMock) -> None:
        mock_service.delete.return_value = False

        response = await client.delete(f"/api/qr/{uuid.uuid4()}")

        assert response.status_code == 404
