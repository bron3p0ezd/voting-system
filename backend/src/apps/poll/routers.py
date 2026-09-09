from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from apps.poll.exceptions import (
    DuplicateVoteException,
    InvalidVoteException,
    InvalidParticipantTokenException,
    PollNotFoundException,
    PollUnavailableException,
)
from apps.poll.schemas import PollResponse, VoteRequest, VoteResponse
from apps.poll.services import (
    ParticipantTokenIssuer,
    ParticipantTokenVerifier,
    PollService,
    VoteService,
)
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


@router.post(
    "/{poll_id}/votes",
    name=AppsUrls.create_vote,
    response_model=VoteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Некорректный выбор вариантов."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Cookie участника отсутствует или недействительна. Обновите страницу."},
        status.HTTP_404_NOT_FOUND: {"description": "Опрос не найден."},
        status.HTTP_409_CONFLICT: {"description": "Голос уже учтён."},
        status.HTTP_410_GONE: {"description": "Опрос недоступен."},
    },
)
async def create_vote(
    poll_id: UUID,
    payload: VoteRequest,
    request: Request,
    factory: ServiceFactory = Depends(get_factory),
):
    vote_service: VoteService = factory.get_vote_service()
    participant_token_verifier: ParticipantTokenVerifier = (
        factory.get_participant_token_verifier()
    )
    try:
        participant_id = participant_token_verifier.get_participant_id(request)
    except InvalidParticipantTokenException as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cookie участника отсутствует или недействительна. Обновите страницу.",
        ) from error

    try:
        vote = await vote_service.record_vote(poll_id, participant_id, payload.option_ids)
    except InvalidVoteException as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный выбор вариантов.",
        ) from error
    except PollNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Опрос не найден.",
        ) from error
    except DuplicateVoteException as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ваш голос уже учтён.",
        ) from error
    except PollUnavailableException as error:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Опрос недоступен.",
        ) from error

    return VoteResponse(poll_id=vote.poll_id, counted_at=vote.counted_at)
