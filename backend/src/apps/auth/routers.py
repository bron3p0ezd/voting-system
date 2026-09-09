from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from apps.auth.schemas import AdminLoginRequest, AdminTokenResponse
from apps.auth.services import AdminAuthService
from settings.di.dependencies import ServiceFactory, get_factory
from settings.urls import AppsUrls


router = APIRouter(prefix="/auth/admin", tags=["Авторизация"])


@router.post(
    "/login",
    name=AppsUrls.login_admin,
    response_model=AdminTokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Неверные учётные данные администратора."},
    },
)
async def login_admin(
    payload: AdminLoginRequest,
    factory: ServiceFactory = Depends(get_factory),
):
    service: AdminAuthService = factory.get_admin_auth_service()
    result = service.authenticate(payload.login, payload.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные администратора.",
        )

    return AdminTokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
    )
