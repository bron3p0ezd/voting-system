from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from settings.di.dependencies import ServiceFactory, get_factory


security_scheme = HTTPBearer(auto_error=False)


def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    factory: Annotated[ServiceFactory, Depends(get_factory)],
) -> str:
    jwt_service = factory.get_jwt_service()
    if credentials is None or jwt_service.get_admin_login(credentials.credentials) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация администратора.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
