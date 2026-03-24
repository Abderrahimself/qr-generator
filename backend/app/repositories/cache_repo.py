import redis.asyncio as redis

from app.repositories.interfaces import CacheRepository


class ValkeyCacheRepository(CacheRepository):
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    async def get(self, key: str) -> str | None:
        value = await self.client.get(key)
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    async def set(self, key: str, value: str, ttl_seconds: int = 86400) -> None:
        await self.client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)
