from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncIterator, Optional, TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession

from settings.database import async_session_maker


class DBManager(ABC):
    @abstractmethod
    async def __aenter__(self) -> "DBManager": ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any
    ) -> None: ...

    @property
    @abstractmethod
    def session(self) -> AsyncSession: ...

    @abstractmethod
    async def commit(self) -> Any: ...

    @abstractmethod
    async def rollback(self) -> Any: ...
    
    @abstractmethod
    def transaction(self) -> AsyncContextManager: ...


DBM: TypeAlias = DBManager



class SQLAlchemyORMRepositoryDBManager(DBManager):
    def __init__(self):
        self.session_factory = async_session_maker
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> "SQLAlchemyORMRepositoryDBManager":
        self._session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any
    ):
        if self._session is None:
            return

        if exc_type is not None:
            await self.rollback()
        await self._session.close()

    @property
    def session(self) -> AsyncSession:
        assert self._session is not None, "session доступен только внутри 'async with'"

        return self._session

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @asynccontextmanager
    async def transaction(self):
        async with self.session.begin():
            yield


async def get_sql_dbm() -> AsyncIterator[DBM]:
    async with SQLAlchemyORMRepositoryDBManager() as dbm:
        yield dbm
