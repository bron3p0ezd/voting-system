from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from apps.poll.models import SelectionType


class PollOptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    text: str
    position: int


class PollResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    selection_type: SelectionType
    min_selections: int
    max_selections: int
    starts_at: datetime
    ends_at: datetime
    options: list[PollOptionResponse]


class VoteRequest(BaseModel):
    option_ids: list[UUID]


class VoteResponse(BaseModel):
    poll_id: UUID
    counted_at: datetime
