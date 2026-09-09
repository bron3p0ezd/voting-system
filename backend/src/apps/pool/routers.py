from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from apps.pool.exceptions import PollNotFoundException, PollUnavailableException
from apps.pool.schemas import PollResponse
from apps.pool.services import ParticipantTokenIssuer, PollService
from settings.di.dependencies import ServiceFactory, get_factory
from settings.urls import AppsUrls


router = APIRouter(prefix="/polls", tags=["Опросы"])


@router.get(
    "/{poll_id}",
    name=AppsUrls.get_poll,
    response_model=PollResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Опрос не найден."},
        status.HTTP_410_GONE: {"description": "Опрос недоступен."},
    },
)
async def get_poll(
    poll_id: UUID,
    request: Request,
    response: Response,
    factory: ServiceFactory = Depends(get_factory),
):
    service: PollService = factory.get_poll_service()
    participant_token_issuer: ParticipantTokenIssuer = (
        factory.get_participant_token_issuer()
    )

    try:
        poll = await service.get_public_poll(poll_id)
    except PollNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Опрос не найден.",
        ) from error
    except PollUnavailableException as error:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Опрос недоступен.",
        ) from error

    participant_token_issuer.issue_if_needed(request, response)

    return PollResponse.model_validate(poll)
