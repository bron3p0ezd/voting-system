from sqlalchemy.exc import SQLAlchemyError

from apps.admin_poll.dtos import AdminPollDTO, CreateAdminPollDTO
from apps.admin_poll.exceptions import InvalidAdminPollException
from apps.admin_poll.repositories import AdminPollRepository
from apps.admin_poll.services import AdminPollService
from apps.poll.models import SelectionType
from settings.db_manager import DBM


class AdminPollServiceImpl(AdminPollService):
    def __init__(self, repository: AdminPollRepository, dbm: DBM) -> None:
        self.__repository = repository
        self.__dbm = dbm

    async def create_poll(self, payload: CreateAdminPollDTO) -> AdminPollDTO:
        self.__validate_payload(payload)

        poll = await self.__repository.create(payload)
        await self.__dbm.commit()

        return poll

    async def get_polls(self) -> list[AdminPollDTO]:
        return await self.__repository.get_all()

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
