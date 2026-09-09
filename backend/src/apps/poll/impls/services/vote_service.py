from datetime import datetime, timezone
from hashlib import sha256
from uuid import UUID


from apps.poll.dtos import VoteDTO
from apps.poll.exceptions import (
    DuplicateVoteException,
    InvalidVoteException,
    PollNotFoundException,
    PollUnavailableException,
)
from apps.poll.models import SelectionType
from apps.poll.repositories import PollRepository, VoteRepository
from apps.poll.services import VoteService
from settings.db_manager import DBM


class VoteServiceImpl(VoteService):
    def __init__(
        self,
        poll_repository: PollRepository,
        vote_repository: VoteRepository,
        dbm: DBM,
    ) -> None:
        self.__poll_repository = poll_repository
        self.__vote_repository = vote_repository
        self.__dbm = dbm

    async def record_vote(
        self,
        poll_id: UUID,
        participant_id: UUID,
        option_ids: list[UUID],
    ) -> VoteDTO:
        poll = await self.__poll_repository.get_by_id(poll_id)
        if poll is None:
            raise PollNotFoundException

        now = datetime.now(tz=timezone.utc)
        if not poll.starts_at <= now < poll.ends_at:
            raise PollUnavailableException

        self.__validate_selection(
            option_ids,
            poll.selection_type,
            poll.min_selections,
            poll.max_selections,
            {option.id for option in poll.options},
        )

        vote = await self.__vote_repository.create(
            poll_id,
            sha256(str(participant_id).encode()).hexdigest(),
            option_ids,
        )
        if vote is None:
            raise DuplicateVoteException

        await self.__dbm.commit()

        return vote

   
    def __validate_selection(
        self,
        option_ids: list[UUID],
        selection_type: SelectionType,
        min_selections: int,
        max_selections: int,
        poll_option_ids: set[UUID],
    ) -> None:
        count = len(option_ids)
        if len(set(option_ids)) != count:
            raise InvalidVoteException
        if not set(option_ids).issubset(poll_option_ids):
            raise InvalidVoteException
        if selection_type is SelectionType.SINGLE and count != 1:
            raise InvalidVoteException
        if (
            selection_type is SelectionType.MULTIPLE
            and not min_selections <= count <= max_selections
        ):
            raise InvalidVoteException
