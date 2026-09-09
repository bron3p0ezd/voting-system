from uuid import uuid4

from fastapi import Request
from fastapi.responses import Response

from apps.auth.policies import ParticipantTokenPolicy
from apps.poll.services import ParticipantTokenIssuer
from apps.auth.services import JWTService


class ParticipantTokenIssuerImpl(ParticipantTokenIssuer):
    def __init__(
        self,
        jwt_service: JWTService,
        policy: ParticipantTokenPolicy,
    ) -> None:
        self.__jwt_service = jwt_service
        self.__policy = policy

    def issue_if_needed(self, request: Request, response: Response) -> None:
        token = request.cookies.get(self.__policy.cookie_name)
        if token is not None and self.__jwt_service.get_participant_id(token) is not None:
            return

        participant_token = self.__jwt_service.create_participant_token(uuid4())
        response.set_cookie(
            key=self.__policy.cookie_name,
            value=participant_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
