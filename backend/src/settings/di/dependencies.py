from fastapi import Depends

from apps.pool.impls.repositories.poll_repository import PollRepositoryImpl
from apps.auth.impls.services.jwt_service import JWTServiceImpl
from apps.pool.impls.services.participant_token_issuer import ParticipantTokenIssuerImpl
from apps.pool.impls.services.poll_service import PollServiceImpl
from apps.auth.policies import ParticipantTokenPolicy
from apps.pool.services import ParticipantTokenIssuer, PollService
from settings.db_manager import DBM, get_sql_dbm


class ServiceFactory:
    def __init__(self, dbm: DBM) -> None:
        self.__dbm = dbm

    def get_poll_service(self) -> PollService:
        repository = PollRepositoryImpl(self.__dbm.session)
        return PollServiceImpl(repository)

    def get_participant_token_issuer(self) -> ParticipantTokenIssuer:
        return ParticipantTokenIssuerImpl(
            jwt_service=JWTServiceImpl(),
            policy=ParticipantTokenPolicy(
                cookie_name="participant_token"
            ),
        )


async def get_factory(dbm: DBM = Depends(get_sql_dbm)) -> ServiceFactory:
    return ServiceFactory(dbm)
