from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from apps.poll.dtos import PollDTO, PollOptionDTO
from apps.poll.models import Poll
from apps.poll.repositories import PollRepository
from settings.alchemy_repositories import AlchemyRepository


class PollRepositoryImpl(PollRepository, AlchemyRepository[Poll]):
    cls_model = Poll

    async def get_by_id(self, poll_id: UUID) -> PollDTO | None:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.options)
            )
            .where(
                self.model.id == poll_id
            )
        )
        result = await self.session.execute(statement)
        poll = result.scalar_one_or_none()

        return PollDTO(
            id=poll.id,
            question=poll.question,
            selection_type=poll.selection_type,
            min_selections=poll.min_selections,
            max_selections=poll.max_selections,
            starts_at=poll.starts_at,
            ends_at=poll.ends_at,
            options=[
                PollOptionDTO(id=option.id, text=option.text, position=option.position)
                for option in poll.options
            ],
        ) if poll is not None else None
