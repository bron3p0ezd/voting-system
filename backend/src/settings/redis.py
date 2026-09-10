from redis.asyncio import Redis

from config import settings
from settings.cache import CacheClient


class RedisCacheClientImpl(CacheClient):
    def __init__(self, client: Redis) -> None:
        self.__client = client

    async def get(self, key: str) -> bytes | str | None:
        return await self.__client.get(key)

    async def set(self, key: str, value: str, *, ex: int) -> object:
        return await self.__client.set(key, value, ex=ex)

    async def delete(self, key: str) -> object:
        return await self.__client.delete(key)


redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)
redis_cache_client = RedisCacheClientImpl(redis_client)
