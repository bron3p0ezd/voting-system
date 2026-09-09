from abc import ABC, abstractmethod
from typing import Generic, Literal, Optional, Type

from pydantic import BaseModel

from settings.database import MODEL_TYPE


class Repository(ABC):
    @abstractmethod
    def __init__(self, **kwargs) -> None: ...


class ORMRepository(Repository, Generic[MODEL_TYPE]):
    cls_model: Optional[Type[MODEL_TYPE]] = None
    cls_schema: Optional[Type[BaseModel]] = None

    @abstractmethod
    def __init__(self, **kwargs) -> None: ...
