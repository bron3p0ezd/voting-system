from uuid import UUID

from sqlalchemy.dialects.postgresql import insert

from apps.poll.dtos import VoteDTO
from apps.poll.models import Vote, VoteSelection
from apps.poll.repositories import VoteRepository
from settings.alchemy_repositories import AlchemyRepository


class VoteRepositoryImpl(VoteRepository, AlchemyRepository[Vote]):
    cls_model = Vote

    async def create(
        self,
        poll_id: UUID,
        participant_key_hash: str,
        option_ids: list[UUID],
    ) -> VoteDTO | None:
        vote_table = self.model.__table__
        vote_statement = (
            insert(self.model)
            .values(
                poll_id=poll_id,
                participant_key_hash=participant_key_hash,
            )
            .on_conflict_do_nothing(
                constraint="uq_votes_poll_participant_key_hash",
            )
            .returning(
                vote_table.c.id,
                vote_table.c.poll_id,
                vote_table.c.counted_at,
            )
        )
        result = await self.session.execute(vote_statement)
        persisted_vote = result.one_or_none()
        if persisted_vote is None:
            return None

        vote_id, persisted_poll_id, counted_at = persisted_vote

        selections_statement = insert(VoteSelection)
        await self.session.execute(
            selections_statement,
            [
                {"vote_id": vote_id, "option_id": option_id}
                for option_id in option_ids
            ],
        )

        return VoteDTO(poll_id=persisted_poll_id, counted_at=counted_at)
