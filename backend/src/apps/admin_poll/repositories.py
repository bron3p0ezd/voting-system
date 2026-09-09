from abc import abstractmethod

from apps.admin_poll.dtos import AdminPollDTO, CreateAdminPollDTO
from settings.repositories import ORMRepository


class AdminPollRepository(ORMRepository):
    @abstractmethod
    async def create(self, payload: CreateAdminPollDTO) -> AdminPollDTO: ...

    @abstractmethod
    async def get_all(self) -> list[AdminPollDTO]: ...
