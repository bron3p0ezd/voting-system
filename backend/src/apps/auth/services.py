from abc import abstractmethod
from dataclasses import dataclass
from uuid import UUID

from settings.services import Service


class JWTService(Service):
    @abstractmethod
    def create_participant_token(self, participant_id: UUID) -> str: ...

    @abstractmethod
    def get_participant_id(self, token: str) -> UUID | None: ...

    @abstractmethod
    def create_admin_token(self, login: str) -> str: ...

    @abstractmethod
    def get_admin_login(self, token: str) -> str | None: ...


@dataclass(frozen=True)
class AdminAuthenticationResult:
    access_token: str
    expires_in: int


class AdminAuthService(Service):
    @abstractmethod
    def authenticate(self, login: str, password: str) -> AdminAuthenticationResult | None: ...
