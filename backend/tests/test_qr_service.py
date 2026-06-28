import hashlib
import uuid
from unittest.mock import AsyncMock

import pytest

from app.models.qr_code import QRCode
from app.services.qr_service import QRService


@pytest.fixture
def service(mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock) -> QRService:
    return QRService(cache=mock_cache, metadata=mock_metadata, storage=mock_storage)


class TestGenerate:
    @pytest.mark.asyncio
    async def test_cache_hit_returns_existing(
        self, service: QRService, mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        url = "https://example.com/"
        url_hash = hashlib.sha256(url.encode()).hexdigest()

        mock_cache.get.return_value = str(sample_qr_code.id)
        mock_metadata.get_by_id.return_value = sample_qr_code
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.png"

        result = await service.generate(url)

        mock_cache.get.assert_awaited_once_with(url_hash)
        mock_metadata.get_by_id.assert_awaited_once_with(sample_qr_code.id)
        mock_storage.upload.assert_not_awaited()
        assert result.id == sample_qr_code.id

    @pytest.mark.asyncio
    async def test_cache_miss_generates_and_stores(
        self, service: QRService, mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        url = "https://example.com/"

        mock_cache.get.return_value = None
        mock_metadata.save.return_value = sample_qr_code
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.png"

        result = await service.generate(url)

        mock_storage.upload.assert_awaited_once()
        mock_metadata.save.assert_awaited_once()
        mock_cache.set.assert_awaited_once()
        assert result.url == url

    @pytest.mark.asyncio
    async def test_generate_returns_correct_format(
        self, service: QRService, mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        sample_qr_code.format = "svg"
        mock_cache.get.return_value = None
        mock_metadata.save.return_value = sample_qr_code
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.svg"

        result = await service.generate("https://example.com/", format="svg")

        assert result.format == "svg"


    @pytest.mark.asyncio
    async def test_cache_hit_but_metadata_deleted_regenerates(
        self, service: QRService, mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        url = "https://example.com/"

        mock_cache.get.return_value = str(sample_qr_code.id)
        mock_metadata.get_by_id.return_value = None  # stale cache
        mock_metadata.save.return_value = sample_qr_code
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.png"

        result = await service.generate(url)

        mock_storage.upload.assert_awaited_once()
        mock_metadata.save.assert_awaited_once()
        assert result.id == sample_qr_code.id


class TestListHistory:
    @pytest.mark.asyncio
    async def test_returns_list(
        self, service: QRService, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        mock_metadata.list_all.return_value = [sample_qr_code]
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.png"

        result = await service.list_history()

        assert len(result) == 1
        assert result[0].id == sample_qr_code.id

    @pytest.mark.asyncio
    async def test_empty_history(self, service: QRService, mock_metadata: AsyncMock) -> None:
        mock_metadata.list_all.return_value = []

        result = await service.list_history()

        assert result == []


class TestGetById:
    @pytest.mark.asyncio
    async def test_existing_returns_response(
        self, service: QRService, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        mock_metadata.get_by_id.return_value = sample_qr_code
        mock_storage.get_presigned_url.return_value = "https://presigned.url/qr.png"

        result = await service.get_by_id(sample_qr_code.id)

        assert result is not None
        assert result.id == sample_qr_code.id

    @pytest.mark.asyncio
    async def test_missing_returns_none(self, service: QRService, mock_metadata: AsyncMock) -> None:
        mock_metadata.get_by_id.return_value = None

        result = await service.get_by_id(uuid.uuid4())

        assert result is None


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_existing(
        self, service: QRService, mock_cache: AsyncMock, mock_metadata: AsyncMock, mock_storage: AsyncMock, sample_qr_code: QRCode
    ) -> None:
        mock_metadata.get_by_id.return_value = sample_qr_code
        mock_metadata.delete.return_value = True

        result = await service.delete(sample_qr_code.id)

        assert result is True
        mock_storage.delete.assert_awaited_once_with(sample_qr_code.object_key)
        mock_cache.delete.assert_awaited_once_with(sample_qr_code.url_hash)

    @pytest.mark.asyncio
    async def test_delete_missing_returns_false(self, service: QRService, mock_metadata: AsyncMock) -> None:
        mock_metadata.get_by_id.return_value = None

        result = await service.delete(uuid.uuid4())

        assert result is False
