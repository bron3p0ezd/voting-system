from typing import Optional, Type

from sqlalchemy.ext.asyncio import AsyncSession

from settings.repositories import (
    MODEL_TYPE,
    ORMRepository,
)


class AlchemyRepository(ORMRepository[MODEL_TYPE]):
    def __init__(self, session: AsyncSession, model: Optional[Type[MODEL_TYPE]] = None) -> None:
        orm_model: Optional[Type[MODEL_TYPE]] = model or self.__class__.cls_model
        if not orm_model:
            raise ValueError("Необходимо передать модель в класс или __init__.")
        self.model: Type[MODEL_TYPE] = orm_model
        self.session = session
