from fastapi import Depends

from apps.admin_poll.impls.repositories.admin_poll_repository import (
    AdminPollRepositoryImpl,
)
from apps.admin_poll.impls.services.admin_poll_service import AdminPollServiceImpl
from apps.admin_poll.services import AdminPollService
from apps.poll.impls.repositories.poll_repository import PollRepositoryImpl
from apps.poll.impls.repositories.vote_repository import VoteRepositoryImpl
from apps.auth.impls.services.jwt_service import JWTServiceImpl
from apps.poll.impls.services.participant_token_issuer import ParticipantTokenIssuerImpl
from apps.poll.impls.services.participant_token_verifier import ParticipantTokenVerifierImpl
from apps.poll.impls.services.poll_service import PollServiceImpl
from apps.poll.impls.services.vote_service import VoteServiceImpl
from apps.auth.services import JWTService
from apps.auth.policies import ParticipantTokenPolicy
from apps.poll.services import (
    ParticipantTokenIssuer,
    ParticipantTokenVerifier,
    PollService,
    VoteService,
)
from settings.db_manager import DBM, get_sql_dbm


class ServiceFactory:
    def __init__(self, dbm: DBM) -> None:
        self.__dbm = dbm

    def get_poll_service(self) -> PollService:
        repository = PollRepositoryImpl(self.__dbm.session)
        return PollServiceImpl(repository)

    def get_admin_poll_service(self) -> AdminPollService:
        repository = AdminPollRepositoryImpl(self.__dbm.session)
        return AdminPollServiceImpl(repository, self.__dbm)

    def get_participant_token_issuer(self) -> ParticipantTokenIssuer:
        return ParticipantTokenIssuerImpl(
            jwt_service=JWTServiceImpl(),
            policy=ParticipantTokenPolicy(
                cookie_name="participant_token"
            ),
        )

    def get_jwt_service(self) -> JWTService:
        return JWTServiceImpl()

    def get_participant_token_verifier(self) -> ParticipantTokenVerifier:
        return ParticipantTokenVerifierImpl(
            jwt_service=self.get_jwt_service(),
            policy=ParticipantTokenPolicy(cookie_name="participant_token"),
        )

    def get_vote_service(self) -> VoteService:
        return VoteServiceImpl(
            poll_repository=PollRepositoryImpl(self.__dbm.session),
            vote_repository=VoteRepositoryImpl(self.__dbm.session),
            dbm=self.__dbm,
        )


async def get_factory(dbm: DBM = Depends(get_sql_dbm)) -> ServiceFactory:
    return ServiceFactory(dbm)
