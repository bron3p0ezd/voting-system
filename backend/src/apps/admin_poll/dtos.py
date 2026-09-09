from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from apps.poll.models import SelectionType


@dataclass(frozen=True)
class CreateAdminPollDTO:
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[str]


@dataclass(frozen=True)
class AdminPollOptionDTO:
    id: UUID
    text: str
    position: int


@dataclass(frozen=True)
class AdminPollDTO:
    id: UUID
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[AdminPollOptionDTO]
