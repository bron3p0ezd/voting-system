from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from apps.poll.dtos import PollDTO, PollOptionDTO
from apps.poll.impls.caches.redis_poll_cache import RedisPollCache
from apps.poll.models import SelectionType
from settings.cache import CacheClient


class RedisClientStub(CacheClient):
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttl_seconds: int | None = None

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self.values[key] = value
        self.ttl_seconds = ex

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


def build_poll() -> PollDTO:
    now = datetime.now(UTC)
    return PollDTO(
        id=uuid4(),
        question="Какой вариант выбрать?",
        selection_type=SelectionType.SINGLE,
        min_selections=1,
        max_selections=1,
        starts_at=now - timedelta(minutes=1),
        ends_at=now + timedelta(minutes=1),
        options=[PollOptionDTO(id=uuid4(), text="Первый", position=0)],
    )


@pytest.mark.asyncio
async def test_redis_poll_cache_round_trips_public_poll() -> None:
    client = RedisClientStub()
    cache = RedisPollCache(client, ttl_seconds=60)
    poll = build_poll()

    await cache.set(poll)
    cached_poll = await cache.get(poll.id)

    assert cached_poll == poll, "Redis-кэш должен возвращать сохранённый опрос."
    assert client.ttl_seconds == 60, "Redis-запись должна иметь заданный TTL."


@pytest.mark.asyncio
async def test_redis_poll_cache_deletes_corrupted_value() -> None:
    client = RedisClientStub()
    cache = RedisPollCache(client, ttl_seconds=60)
    poll_id = uuid4()
    client.values[f"poll:public:{poll_id}"] = "{"

    cached_poll = await cache.get(poll_id)

    assert cached_poll is None, "Повреждённая Redis-запись не должна попадать в API."
    assert not client.values, "Повреждённая Redis-запись должна быть удалена."
