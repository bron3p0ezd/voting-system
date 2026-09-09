from decimal import Decimal
from uuid import UUID

from apps.admin_poll.dtos import (
    AdminPollDTO,
    AdminPollResultItemDTO,
    AdminPollResultsDTO,
    CreateAdminPollDTO,
)
from apps.admin_poll.exceptions import (
    AdminPollNotFoundException,
    InvalidAdminPollException,
)
from apps.admin_poll.repositories import (
    AdminPollRepository,
    AdminPollStatisticsRepository,
)
from apps.admin_poll.services import AdminPollService
from apps.poll.models import SelectionType
from settings.db_manager import DBM


class AdminPollServiceImpl(AdminPollService):
    def __init__(
        self,
        repository: AdminPollRepository,
        statistics_repository: AdminPollStatisticsRepository,
        dbm: DBM,
    ) -> None:
        self.__repository = repository
        self.__statistics_repository = statistics_repository
        self.__dbm = dbm

    async def create_poll(self, payload: CreateAdminPollDTO) -> AdminPollDTO:
        self.__validate_payload(payload)

        poll = await self.__repository.create(payload)
        await self.__dbm.commit()

        return poll

    async def get_polls(self) -> list[AdminPollDTO]:
        return await self.__repository.get_all()

    async def get_poll_results(self, poll_id: UUID) -> AdminPollResultsDTO:
        poll = await self.__repository.get_by_id(poll_id)
        if poll is None:
            raise AdminPollNotFoundException

        statistics = await self.__statistics_repository.get_statistics(poll_id)
        votes_by_option_id = {
            item.option_id: item.votes for item in statistics.option_statistics
        }
        results: list[AdminPollResultItemDTO] = []
        for option in poll.options:
            votes = votes_by_option_id.get(option.id, 0)
            results.append(
                AdminPollResultItemDTO(
                    option_id=option.id,
                    text=option.text,
                    votes=votes,
                    participant_percentage=(
                        Decimal(votes) * Decimal(100)
                        / Decimal(statistics.total_participants)
                        if statistics.total_participants
                        else Decimal(0)
                    ),
                )
            )

        return AdminPollResultsDTO(
            poll_id=poll.id,
            total_participants=statistics.total_participants,
            results=results,
        )

    def __validate_payload(self, payload: CreateAdminPollDTO) -> None:
        if not payload.question.strip() or len(payload.options) < 2:
            raise InvalidAdminPollException
        if any(not option.strip() for option in payload.options):
            raise InvalidAdminPollException
        if payload.ends_at <= payload.starts_at:
            raise InvalidAdminPollException
        if payload.selection_type is SelectionType.SINGLE:
            if payload.min_selections != 1 or payload.max_selections != 1:
                raise InvalidAdminPollException
            return
        if not 0 < payload.min_selections <= payload.max_selections <= len(payload.options):
            raise InvalidAdminPollException
