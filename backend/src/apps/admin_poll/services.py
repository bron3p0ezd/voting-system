from abc import abstractmethod

from apps.admin_poll.dtos import AdminPollDTO, CreateAdminPollDTO
from settings.services import Service


class AdminPollService(Service):
    @abstractmethod
    async def create_poll(self, payload: CreateAdminPollDTO) -> AdminPollDTO: ...

    @abstractmethod
    async def get_polls(self) -> list[AdminPollDTO]: ...
