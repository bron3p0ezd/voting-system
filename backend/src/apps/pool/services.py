from abc import abstractmethod
from uuid import UUID

from fastapi import Request
from fastapi.responses import Response

from settings.services import Service

from apps.pool.dtos import PollDTO


class PollService(Service):
    @abstractmethod
    async def get_public_poll(self, poll_id: UUID) -> PollDTO: ...


class ParticipantTokenIssuer(Service):
    @abstractmethod
    def issue_if_needed(self, request: Request, response: Response) -> None: ...
