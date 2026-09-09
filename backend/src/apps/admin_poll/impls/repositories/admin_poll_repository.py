from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from apps.admin_poll.dtos import AdminPollDTO, AdminPollOptionDTO, CreateAdminPollDTO
from apps.admin_poll.repositories import AdminPollRepository
from apps.poll.models import Poll, PollOption
from settings.alchemy_repositories import AlchemyRepository


class AdminPollRepositoryImpl(AdminPollRepository, AlchemyRepository[Poll]):
    cls_model = Poll

    async def create(self, payload: CreateAdminPollDTO) -> AdminPollDTO:
        poll_table = self.model.__table__
        poll_statement = (
            insert(self.model)
            .values(
                question=payload.question,
                selection_type=payload.selection_type,
                min_selections=payload.min_selections,
                max_selections=payload.max_selections,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
            )
            .returning(
                poll_table.c.id,
                poll_table.c.question,
                poll_table.c.selection_type,
                poll_table.c.min_selections,
                poll_table.c.max_selections,
                poll_table.c.starts_at,
                poll_table.c.ends_at,
            )
        )
        poll_result = await self.session.execute(poll_statement)
        poll = poll_result.one()

        option_table = PollOption.__table__
        options_statement = insert(PollOption).returning(
            option_table.c.id,
            option_table.c.text,
            option_table.c.position,
        )
        options_result = await self.session.execute(
            options_statement,
            [
                {"poll_id": poll.id, "text": text, "position": position}
                for position, text in enumerate(payload.options)
            ],
        )

        return AdminPollDTO(
            id=poll.id,
            question=poll.question,
            selection_type=poll.selection_type,
            min_selections=poll.min_selections,
            max_selections=poll.max_selections,
            starts_at=poll.starts_at,
            ends_at=poll.ends_at,
            options=[
                AdminPollOptionDTO(
                    id=option.id,
                    text=option.text,
                    position=option.position,
                )
                for option in options_result
            ],
        )

    async def get_all(self) -> list[AdminPollDTO]:
        statement = (
            select(self.model)
            .options(selectinload(self.model.options))
            .order_by(self.model.starts_at.desc(), self.model.id)
        )
        result = await self.session.execute(statement)

        return [self.__to_dto(poll) for poll in result.scalars().all()]

    def __to_dto(self, poll: Poll) -> AdminPollDTO:
        return AdminPollDTO(
            id=poll.id,
            question=poll.question,
            selection_type=poll.selection_type,
            min_selections=poll.min_selections,
            max_selections=poll.max_selections,
            starts_at=poll.starts_at,
            ends_at=poll.ends_at,
            options=[
                AdminPollOptionDTO(
                    id=option.id,
                    text=option.text,
                    position=option.position,
                )
                for option in poll.options
            ],
        )
