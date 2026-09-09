from abc import abstractmethod
from uuid import UUID

from settings.services import Service

from apps.pool.dtos import PollDTO


class PollService(Service):
    @abstractmethod
    async def get_public_poll(self, poll_id: UUID) -> PollDTO: ...
