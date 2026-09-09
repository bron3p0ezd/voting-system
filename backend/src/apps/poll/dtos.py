from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from apps.poll.models import SelectionType


@dataclass(frozen=True)
class PollOptionDTO:
    id: UUID
    text: str
    position: int


@dataclass(frozen=True)
class PollDTO:
    id: UUID
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[PollOptionDTO]


@dataclass(frozen=True)
class VoteDTO:
    poll_id: UUID
    counted_at: datetime
