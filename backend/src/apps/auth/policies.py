from dataclasses import dataclass

ADMIN_TOKEN_EXPIRES_IN_MINUTES = 60


@dataclass(frozen=True)
class ParticipantTokenPolicy:
    cookie_name: str


@dataclass(frozen=True)
class AdminTokenPolicy:
    expires_in_minutes: int
