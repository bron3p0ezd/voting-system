from abc import abstractmethod
from uuid import UUID

from settings.repositories import ORMRepository

from apps.pool.dtos import PollDTO


class PollRepository(ORMRepository):
    @abstractmethod
    async def get_by_id(self, poll_id: UUID) -> PollDTO | None: ...
