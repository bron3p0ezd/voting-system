from abc import ABC, abstractmethod


class CacheClient(ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes | str | None: ...

    @abstractmethod
    async def set(self, key: str, value: str, *, ex: int) -> object: ...

    @abstractmethod
    async def delete(self, key: str) -> object: ...
