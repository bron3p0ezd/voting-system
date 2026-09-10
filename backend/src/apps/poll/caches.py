from abc import abstractmethod
from uuid import UUID

from apps.poll.dtos import PollDTO
from settings.services import Service


class PollCache(Service):
    @abstractmethod
    async def get(self, poll_id: UUID) -> PollDTO | None: ...

    @abstractmethod
    async def set(self, poll: PollDTO) -> None: ...
