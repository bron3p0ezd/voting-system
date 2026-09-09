from uuid import UUID

from fastapi import Request

from apps.auth.policies import ParticipantTokenPolicy
from apps.auth.services import JWTService
from apps.poll.exceptions import InvalidParticipantTokenException
from apps.poll.services import ParticipantTokenVerifier


class ParticipantTokenVerifierImpl(ParticipantTokenVerifier):
    def __init__(
        self,
        jwt_service: JWTService,
        policy: ParticipantTokenPolicy,
    ) -> None:
        self.__jwt_service = jwt_service
        self.__policy = policy

    def get_participant_id(self, request: Request) -> UUID:
        token = request.cookies.get(self.__policy.cookie_name)
        participant_id = self.__jwt_service.get_participant_id(token) if token else None
        if participant_id is None:
            raise InvalidParticipantTokenException

        return participant_id
