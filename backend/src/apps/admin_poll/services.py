from abc import abstractmethod

from uuid import UUID

from apps.admin_poll.dtos import (
    AdminPollDTO,
    AdminPollResultsDTO,
    CreateAdminPollDTO,
)
from settings.services import Service


class AdminPollService(Service):
    @abstractmethod
    async def create_poll(self, payload: CreateAdminPollDTO) -> AdminPollDTO: ...

    @abstractmethod
    async def get_polls(self) -> list[AdminPollDTO]: ...

    @abstractmethod
    async def get_poll_results(
        self,
        poll_id: UUID,
        include_empty: bool,
    ) -> AdminPollResultsDTO: ...
