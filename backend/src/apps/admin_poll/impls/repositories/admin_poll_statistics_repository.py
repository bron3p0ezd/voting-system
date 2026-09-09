from uuid import UUID

from sqlalchemy import func, select

from apps.admin_poll.dtos import (
    AdminPollOptionStatisticsDTO,
    AdminPollStatisticsDTO,
)
from apps.admin_poll.repositories import AdminPollStatisticsRepository
from apps.poll.models import Vote, VoteSelection
from settings.alchemy_repositories import AlchemyRepository


class AdminPollStatisticsRepositoryImpl(
    AdminPollStatisticsRepository,
    AlchemyRepository[Vote],
):
    cls_model = Vote

    async def get_statistics(self, poll_id: UUID) -> AdminPollStatisticsDTO:
        total_statement = select(func.count(self.model.id)).where(
            self.model.poll_id == poll_id
        )
        total_result = await self.session.execute(total_statement)

        votes_statement = (
            select(
                VoteSelection.option_id,
                func.count(VoteSelection.vote_id).label("votes"),
            )
            .join(self.model, self.model.id == VoteSelection.vote_id)
            .where(self.model.poll_id == poll_id)
            .group_by(VoteSelection.option_id)
        )
        votes_result = await self.session.execute(votes_statement)

        return AdminPollStatisticsDTO(
            total_participants=total_result.scalar_one(),
            option_statistics=[
                AdminPollOptionStatisticsDTO(option_id=row.option_id, votes=row.votes)
                for row in votes_result
            ],
        )
