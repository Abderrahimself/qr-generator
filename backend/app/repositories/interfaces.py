from abc import ABC, abstractmethod
from uuid import UUID

from app.models.qr_code import QRCode


class CacheRepository(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None: ...

    @abstractmethod
    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...


class MetadataRepository(ABC):
    @abstractmethod
    async def save(self, qr_code: QRCode) -> QRCode: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> QRCode | None: ...

    @abstractmethod
    async def get_by_url_hash(self, url_hash: str) -> QRCode | None: ...

    @abstractmethod
    async def list_all(self, limit: int = 50, offset: int = 0) -> list[QRCode]: ...

    @abstractmethod
    async def delete(self, id: UUID) -> bool: ...


class StorageRepository(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> None: ...

    @abstractmethod
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...
