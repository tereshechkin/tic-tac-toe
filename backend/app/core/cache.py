import json
from typing import Any, Optional
from redis.asyncio import Redis
from app.config import settings


class CacheManager:
    """Wrapper for Redis client with common operations."""

    def __init__(self):
        self._client: Optional[Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection."""
        self._client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return self._client

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        if serialize and not isinstance(value, str):
            value = json.dumps(value)
        return await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> int:
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0

    async def expire(self, key: str, ttl: int) -> bool:
        return await self.client.expire(key, ttl)

    async def ping(self) -> bool:
        return await self.client.ping()


cache = CacheManager()
