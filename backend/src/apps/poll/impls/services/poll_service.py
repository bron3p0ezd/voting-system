from datetime import datetime, timezone
from uuid import UUID

from apps.poll.caches import PollCache
from apps.poll.dtos import PollDTO
from apps.poll.exceptions import PollNotFoundException, PollUnavailableException
from apps.poll.repositories import PollRepository
from apps.poll.services import PollService


class PollServiceImpl(PollService):
    def __init__(self, repository: PollRepository, cache: PollCache) -> None:
        self.__repository = repository
        self.__cache = cache

    async def get_public_poll(self, poll_id: UUID) -> PollDTO:
        poll = await self.__cache.get(poll_id)
        if poll is None:
            poll = await self.__repository.get_by_id(poll_id)
            if poll is not None:
                await self.__cache.set(poll)
        if poll is None:
            raise PollNotFoundException

        now = datetime.now(tz=timezone.utc)
        if not poll.starts_at <= now < poll.ends_at:
            raise PollUnavailableException

        return poll
