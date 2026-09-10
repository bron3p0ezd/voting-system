from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from apps.poll.caches import PollCache
from apps.poll.dtos import PollDTO, PollOptionDTO
from apps.poll.exceptions import PollUnavailableException
from apps.poll.impls.services.poll_service import PollServiceImpl
from apps.poll.models import SelectionType
from apps.poll.repositories import PollRepository


class PollRepositoryStub(PollRepository):
    def __init__(self, poll: PollDTO | None) -> None:
        self.poll = poll
        self.calls = 0

    async def get_by_id(self, poll_id: UUID) -> PollDTO | None:
        self.calls += 1
        return self.poll


class PollCacheStub(PollCache):
    def __init__(self, poll: PollDTO | None) -> None:
        self.poll = poll
        self.get_calls = 0
        self.set_calls = 0

    async def get(self, poll_id: UUID) -> PollDTO | None:
        self.get_calls += 1
        return self.poll

    async def set(self, poll: PollDTO) -> None:
        self.set_calls += 1
        self.poll = poll


def build_poll(starts_at: datetime, ends_at: datetime) -> PollDTO:
    return PollDTO(
        id=uuid4(),
        question="Какой вариант выбрать?",
        selection_type=SelectionType.SINGLE,
        min_selections=1,
        max_selections=1,
        starts_at=starts_at,
        ends_at=ends_at,
        options=[PollOptionDTO(id=uuid4(), text="Первый", position=0)],
    )


@pytest.mark.asyncio
async def test_get_public_poll_returns_cached_poll_without_database_query() -> None:
    now = datetime.now(UTC)
    poll = build_poll(now - timedelta(minutes=1), now + timedelta(minutes=1))
    repository = PollRepositoryStub(None)
    cache = PollCacheStub(poll)

    result = await PollServiceImpl(repository, cache).get_public_poll(poll.id)

    assert result == poll, "Публичный опрос должен возвращаться из кэша."
    assert repository.calls == 0, "При попадании в кэш не должно быть запроса к БД."
    assert cache.get_calls == 1, "Сервис должен сначала проверить кэш."


@pytest.mark.asyncio
async def test_get_public_poll_caches_database_result_after_cache_miss() -> None:
    now = datetime.now(UTC)
    poll = build_poll(now - timedelta(minutes=1), now + timedelta(minutes=1))
    repository = PollRepositoryStub(poll)
    cache = PollCacheStub(None)

    result = await PollServiceImpl(repository, cache).get_public_poll(poll.id)

    assert result == poll, "Сервис должен вернуть найденный в БД опрос."
    assert repository.calls == 1, "При промахе кэша должен быть один запрос к БД."
    assert cache.set_calls == 1, "Найденный опрос должен попасть в кэш."


@pytest.mark.asyncio
async def test_get_public_poll_checks_availability_of_cached_poll() -> None:
    now = datetime.now(UTC)
    poll = build_poll(now - timedelta(minutes=2), now - timedelta(minutes=1))
    repository = PollRepositoryStub(None)
    cache = PollCacheStub(poll)

    with pytest.raises(PollUnavailableException):
        await PollServiceImpl(repository, cache).get_public_poll(poll.id)

    assert repository.calls == 0, "Недоступный кэшированный опрос не должен читать БД."
