from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from apps.poll.models import SelectionType


class CreateAdminPollRequest(BaseModel):
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[str]


class AdminPollOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    position: int


class AdminPollResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[AdminPollOptionResponse]


class AdminPollResultItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    option_id: UUID
    text: str
    votes: int
    participant_percentage: Decimal


class AdminPollResultsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    poll_id: UUID
    total_participants: int
    results: list[AdminPollResultItemResponse]
