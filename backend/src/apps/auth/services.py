from abc import abstractmethod
from uuid import UUID

from settings.services import Service


class JWTService(Service):
    @abstractmethod
    def create_participant_token(self, participant_id: UUID) -> str: ...

    @abstractmethod
    def get_participant_id(self, token: str) -> UUID | None: ...
