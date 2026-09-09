from abc import abstractmethod
from uuid import UUID

from fastapi import Request
from fastapi.responses import Response

from settings.services import Service

from apps.poll.dtos import PollDTO, VoteDTO


class PollService(Service):
    @abstractmethod
    async def get_public_poll(self, poll_id: UUID) -> PollDTO: ...


class ParticipantTokenIssuer(Service):
    @abstractmethod
    def issue_if_needed(self, request: Request, response: Response) -> None: ...


class ParticipantTokenVerifier(Service):
    @abstractmethod
    def get_participant_id(self, request: Request) -> UUID: ...


class VoteService(Service):
    @abstractmethod
    async def record_vote(
        self,
        poll_id: UUID,
        participant_id: UUID,
        option_ids: list[UUID],
    ) -> VoteDTO: ...
