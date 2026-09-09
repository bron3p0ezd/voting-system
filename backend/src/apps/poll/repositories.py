from abc import abstractmethod
from uuid import UUID

from settings.repositories import ORMRepository

from apps.poll.dtos import PollDTO, VoteDTO


class PollRepository(ORMRepository):
    @abstractmethod
    async def get_by_id(self, poll_id: UUID) -> PollDTO | None: ...


class VoteRepository(ORMRepository):
    @abstractmethod
    async def create(
        self,
        poll_id: UUID,
        participant_key_hash: str,
        option_ids: list[UUID],
    ) -> VoteDTO: ...
