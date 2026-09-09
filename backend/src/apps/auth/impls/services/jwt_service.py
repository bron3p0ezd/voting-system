from datetime import UTC, datetime, timedelta
from uuid import UUID

from jwt import InvalidTokenError, decode, encode

from apps.auth.services import JWTService
from apps.auth.policies import AdminTokenPolicy
from config import settings


class JWTServiceImpl(JWTService):
    def __init__(self, admin_token_policy: AdminTokenPolicy) -> None:
        self.__admin_token_policy = admin_token_policy

    def create_participant_token(self, participant_id: UUID) -> str:
        return encode(
            {"sub": str(participant_id)},
            settings.PARTICIPANT_JWT_SECRET,
            algorithm=settings.JWT_ALG,
        )

    def get_participant_id(self, token: str) -> UUID | None:
        try:
            payload = decode(
                token,
                settings.PARTICIPANT_JWT_SECRET,
                algorithms=[settings.JWT_ALG],
            )
            return UUID(payload["sub"])
        except (InvalidTokenError, KeyError, TypeError, ValueError):
            return None

    def create_admin_token(self, login: str) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=self.__admin_token_policy.expires_in_minutes)
        return encode(
            {"sub": login, "role": "admin", "exp": expires_at},
            settings.ADMIN_JWT_SECRET,
            algorithm=settings.JWT_ALG,
        )

    def get_admin_login(self, token: str) -> str | None:
        try:
            payload = decode(
                token,
                settings.ADMIN_JWT_SECRET,
                algorithms=[settings.JWT_ALG],
            )
            login = payload["sub"]
            if payload.get("role") != "admin" or not isinstance(login, str):
                return None
            return login
        except (InvalidTokenError, KeyError, TypeError):
            return None
