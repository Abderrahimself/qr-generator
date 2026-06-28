from uuid import UUID

from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.qr_code import QRCode
from app.repositories.interfaces import MetadataRepository


class PostgresMetadataRepository(MetadataRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, qr_code: QRCode) -> QRCode:
        self.session.add(qr_code)
        await self.session.commit()
        await self.session.refresh(qr_code)
        return qr_code

    async def get_by_id(self, id: UUID) -> QRCode | None:
        return await self.session.get(QRCode, id)

    async def get_by_url_hash(self, url_hash: str) -> QRCode | None:
        result = await self.session.execute(
            select(QRCode).where(QRCode.url_hash == url_hash)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[QRCode]:
        result = await self.session.execute(
            select(QRCode)
            .order_by(QRCode.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def delete(self, id: UUID) -> bool:
        result = await self.session.execute(
            sa_delete(QRCode).where(QRCode.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0  # type: ignore[attr-defined]  # CursorResult has rowcount
