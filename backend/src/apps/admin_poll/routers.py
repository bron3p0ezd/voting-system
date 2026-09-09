from fastapi import APIRouter, Depends, HTTPException, status

from apps.admin_poll.dtos import CreateAdminPollDTO
from apps.admin_poll.exceptions import InvalidAdminPollException
from apps.admin_poll.schemas import AdminPollResponse, CreateAdminPollRequest
from apps.admin_poll.services import AdminPollService
from settings.di.dependencies import ServiceFactory, get_factory
from settings.urls import AppsUrls


router = APIRouter(prefix="/admin/polls", tags=["Список опросов"])


@router.post(
    "",
    name=AppsUrls.create_admin_poll,
    response_model=AdminPollResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Некорректные параметры опроса."},
    },
)
async def create_poll(
    payload: CreateAdminPollRequest,
    factory: ServiceFactory = Depends(get_factory),
):
    service: AdminPollService = factory.get_admin_poll_service()
    try:
        poll = await service.create_poll(
            CreateAdminPollDTO(
                question=payload.question,
                selection_type=payload.selection_type,
                min_selections=payload.min_selections,
                max_selections=payload.max_selections,
                starts_at=payload.starts_at,
                ends_at=payload.ends_at,
                options=payload.options,
            )
        )
    except InvalidAdminPollException as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректные параметры опроса.",
        ) from error

    return AdminPollResponse.model_validate(poll)


@router.get(
    "",
    name=AppsUrls.get_admin_polls,
    response_model=list[AdminPollResponse],
    status_code=status.HTTP_200_OK,
)
async def get_polls(
    factory: ServiceFactory = Depends(get_factory),
):
    service: AdminPollService = factory.get_admin_poll_service()
    polls = await service.get_polls()

    return [AdminPollResponse.model_validate(poll) for poll in polls]
