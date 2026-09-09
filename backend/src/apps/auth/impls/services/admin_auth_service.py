from hmac import compare_digest

from apps.auth.policies import AdminTokenPolicy
from apps.auth.services import AdminAuthService, AdminAuthenticationResult, JWTService
from config import settings


class AdminAuthServiceImpl(AdminAuthService):
    def __init__(self, jwt_service: JWTService, token_policy: AdminTokenPolicy) -> None:
        self.__jwt_service = jwt_service
        self.__token_policy = token_policy

    def authenticate(self, login: str, password: str) -> AdminAuthenticationResult | None:
        is_valid = compare_digest(login, settings.ADMIN_LOGIN) and compare_digest(
            password,
            settings.ADMIN_PASSWORD,
        )
        if not is_valid:
            return None

        return AdminAuthenticationResult(
            access_token=self.__jwt_service.create_admin_token(login),
            expires_in=self.__token_policy.expires_in_minutes * 60,
        )
