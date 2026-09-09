from datetime import datetime, timezone
from uuid import UUID

from apps.pool.dtos import PollDTO
from apps.pool.exceptions import PollNotFoundException, PollUnavailableException
from apps.pool.repositories import PollRepository
from apps.pool.services import PollService


class PollServiceImpl(PollService):
    def __init__(self, repository: PollRepository) -> None:
        self.__repository = repository

    async def get_public_poll(self, poll_id: UUID) -> PollDTO:
        poll = await self.__repository.get_by_id(poll_id)
        if poll is None:
            raise PollNotFoundException

        now = datetime.now(tz=timezone.utc)
        if not poll.starts_at <= now < poll.ends_at:
            raise PollUnavailableException

        return poll
