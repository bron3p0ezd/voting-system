from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from apps.poll.caches import PollCache
from apps.poll.dtos import PollDTO, PollOptionDTO, VoteDTO
from apps.poll.impls.services.vote_service import VoteServiceImpl
from apps.poll.models import SelectionType
from apps.poll.repositories import PollRepository, VoteRepository
from settings.db_manager import DBManager


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


class VoteRepositoryStub(VoteRepository):
    def __init__(self, vote: VoteDTO | None) -> None:
        self.vote = vote
        self.calls = 0

    async def create(
        self,
        poll_id: UUID,
        participant_key_hash: str,
        option_ids: list[UUID],
    ) -> VoteDTO | None:
        self.calls += 1
        return self.vote


class DBManagerStub(DBManager):
    def __init__(self) -> None:
        self.commits = 0

    async def __aenter__(self) -> "DBManagerStub":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    @property
    def session(self):
        raise AssertionError("Сессия не должна использоваться сервисом напрямую.")

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None

    def transaction(self):
        raise AssertionError("Транзакция не должна открываться сервисом напрямую.")


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
async def test_record_vote_validates_cached_poll_and_commits_persisted_vote() -> None:
    poll = build_poll()
    vote = VoteDTO(poll_id=poll.id, counted_at=datetime.now(UTC))
    repository = PollRepositoryStub(None)
    cache = PollCacheStub(poll)
    votes = VoteRepositoryStub(vote)
    dbm = DBManagerStub()
    service = VoteServiceImpl(repository, votes, dbm, cache)

    result = await service.record_vote(poll.id, uuid4(), [poll.options[0].id])

    assert result == vote, "Сервис должен вернуть устойчиво записанный голос."
    assert repository.calls == 0, "При попадании в кэш не должно быть чтения PostgreSQL."
    assert votes.calls == 1, "После валидации должен создаваться один голос."
    assert dbm.commits == 1, "Голос должен подтверждаться ровно одним commit."


@pytest.mark.asyncio
async def test_record_vote_caches_poll_loaded_after_cache_miss() -> None:
    poll = build_poll()
    vote = VoteDTO(poll_id=poll.id, counted_at=datetime.now(UTC))
    repository = PollRepositoryStub(poll)
    cache = PollCacheStub(None)
    service = VoteServiceImpl(repository, VoteRepositoryStub(vote), DBManagerStub(), cache)

    await service.record_vote(poll.id, uuid4(), [poll.options[0].id])

    assert repository.calls == 1, "Промах кэша должен читать опрос из PostgreSQL."
    assert cache.set_calls == 1, "Опрос из PostgreSQL должен быть добавлен в кэш."
