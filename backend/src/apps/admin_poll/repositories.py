from abc import abstractmethod

from uuid import UUID

from apps.admin_poll.dtos import (
    AdminPollDTO,
    AdminPollStatisticsDTO,
    CreateAdminPollDTO,
)
from settings.repositories import ORMRepository


class AdminPollRepository(ORMRepository):
    @abstractmethod
    async def create(self, payload: CreateAdminPollDTO) -> AdminPollDTO: ...

    @abstractmethod
    async def get_all(self) -> list[AdminPollDTO]: ...

    @abstractmethod
    async def get_by_id(self, poll_id: UUID) -> AdminPollDTO | None: ...


class AdminPollStatisticsRepository(ORMRepository):
    @abstractmethod
    async def get_statistics(self, poll_id: UUID) -> AdminPollStatisticsDTO: ...
