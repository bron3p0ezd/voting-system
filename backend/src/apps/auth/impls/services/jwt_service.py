from uuid import UUID

from jwt import InvalidTokenError, decode, encode

from apps.auth.services import JWTService
from config import settings


class JWTServiceImpl(JWTService):
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
