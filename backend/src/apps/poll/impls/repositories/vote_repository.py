from uuid import UUID

from sqlalchemy import bindparam, func, literal, select, true
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PostgreSQLUUID, insert

from apps.poll.dtos import VoteDTO
from apps.poll.models import PollOption, Vote, VoteSelection
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
        option_ids_parameter = bindparam(
            "option_ids",
            type_=ARRAY(PostgreSQLUUID(as_uuid=True)),
        )
        requested_options = select(
            func.unnest(option_ids_parameter).label("option_id")
        ).cte("requested_options")
        valid_options = (
            select(requested_options.c.option_id)
            .join(PollOption, PollOption.id == requested_options.c.option_id)
            .where(PollOption.poll_id == poll_id)
            .cte("valid_options")
        )
        all_options_belong_to_poll = (
            select(func.count())
            .select_from(valid_options)
            .scalar_subquery()
            == func.cardinality(option_ids_parameter)
        )
        created_vote = (
            insert(self.model)
            .from_select(
                (vote_table.c.poll_id, vote_table.c.participant_key_hash),
                select(literal(poll_id), literal(participant_key_hash)).where(
                    all_options_belong_to_poll
                ),
            )
            .on_conflict_do_nothing(
                constraint="uq_votes_poll_participant_key_hash",
            )
            .returning(
                vote_table.c.id,
                vote_table.c.poll_id,
                vote_table.c.counted_at,
            )
            .cte("created_vote")
        )
        created_selections = insert(VoteSelection).from_select(
            (VoteSelection.vote_id, VoteSelection.option_id),
            select(created_vote.c.id, valid_options.c.option_id).select_from(
                created_vote.join(valid_options, true())
            ),
        ).cte("created_selections")
        statement = select(
            created_vote.c.id,
            created_vote.c.poll_id,
            created_vote.c.counted_at,
        ).add_cte(created_selections)

        result = await self.session.execute(statement, {"option_ids": option_ids})
        persisted_vote = result.one_or_none()
        if persisted_vote is None:
            return None

        _, persisted_poll_id, counted_at = persisted_vote

        return VoteDTO(poll_id=persisted_poll_id, counted_at=counted_at)
