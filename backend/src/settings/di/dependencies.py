from fastapi import Depends

from apps.pool.impls.repositories.poll_repository import PollRepositoryImpl
from apps.pool.impls.services.poll_service import PollServiceImpl
from apps.pool.services import PollService
from settings.db_manager import DBM, get_sql_dbm


class ServiceFactory:
    def __init__(self, dbm: DBM) -> None:
        self.__dbm = dbm

    def get_poll_service(self) -> PollService:
        repository = PollRepositoryImpl(self.__dbm.session)
        return PollServiceImpl(repository)


async def get_factory(dbm: DBM = Depends(get_sql_dbm)) -> ServiceFactory:
    return ServiceFactory(dbm)
