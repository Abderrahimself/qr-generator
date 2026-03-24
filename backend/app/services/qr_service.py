import hashlib
from uuid import UUID

from app.config import settings
from app.models.qr_code import QRCode
from app.repositories.interfaces import (
    CacheRepository,
    MetadataRepository,
    StorageRepository,
)
from app.schemas.qr import QRCodeResponse
from app.services.qr_factory import QRFormatFactory


class QRService:
    def __init__(
        self,
        cache: CacheRepository,
        metadata: MetadataRepository,
        storage: StorageRepository,
    ) -> None:
        self.cache = cache
        self.metadata = metadata
        self.storage = storage
        self.factory = QRFormatFactory

    async def generate(self, url: str, format: str = "png") -> QRCodeResponse:
        url_hash = hashlib.sha256(url.encode()).hexdigest()

        # 1. Check cache
        cached_id = await self.cache.get(url_hash)
        if cached_id:
            existing = await self.metadata.get_by_id(UUID(cached_id))
            if existing:
                return await self._to_response(existing)

        # 2. Generate QR image
        generator = self.factory.get_generator(format)
        image_data = generator.generate(url)

        # 3. Upload to object storage
        object_key = f"qr-codes/{url_hash}.{format}"
        await self.storage.upload(object_key, image_data, generator.content_type)

        # 4. Save metadata
        qr_code = QRCode(
            original_url=url,
            url_hash=url_hash,
            object_key=object_key,
            format=format,
            size_bytes=len(image_data),
        )
        saved = await self.metadata.save(qr_code)

        # 5. Cache the mapping
        await self.cache.set(
            url_hash, str(saved.id), ttl_seconds=settings.cache_ttl_seconds
        )

        return await self._to_response(saved)

    async def get_by_id(self, id: UUID) -> QRCodeResponse | None:
        qr_code = await self.metadata.get_by_id(id)
        if not qr_code:
            return None
        return await self._to_response(qr_code)

    async def list_history(
        self, limit: int = 50, offset: int = 0
    ) -> list[QRCodeResponse]:
        qr_codes = await self.metadata.list_all(limit=limit, offset=offset)
        return [await self._to_response(qr) for qr in qr_codes]

    async def delete(self, id: UUID) -> bool:
        qr_code = await self.metadata.get_by_id(id)
        if not qr_code:
            return False

        # Remove from storage, cache, and metadata
        await self.storage.delete(qr_code.object_key)
        await self.cache.delete(qr_code.url_hash)
        await self.metadata.delete(id)
        return True

    async def _to_response(self, qr_code: QRCode) -> QRCodeResponse:
        image_url = await self.storage.get_presigned_url(qr_code.object_key)
        return QRCodeResponse(
            id=qr_code.id,
            url=qr_code.original_url,
            image_url=image_url,
            format=qr_code.format,
            created_at=qr_code.created_at,
        )
