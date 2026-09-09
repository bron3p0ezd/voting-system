from dataclasses import dataclass


@dataclass(frozen=True)
class ParticipantTokenPolicy:
    cookie_name: str
