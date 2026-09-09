from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
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


@dataclass(frozen=True)
class AdminPollResultItemDTO:
    option_id: UUID
    text: str
    votes: int
    participant_percentage: Decimal


@dataclass(frozen=True)
class AdminPollResultsDTO:
    poll_id: UUID
    total_participants: int
    results: list[AdminPollResultItemDTO]


@dataclass(frozen=True)
class AdminPollOptionStatisticsDTO:
    option_id: UUID
    votes: int


@dataclass(frozen=True)
class AdminPollStatisticsDTO:
    total_participants: int
    option_statistics: list[AdminPollOptionStatisticsDTO]
