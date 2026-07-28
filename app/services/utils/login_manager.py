from fastapi import Depends

from app.models import User
from app.services.srv_user import UserService
from app.utils.exception_handler import CustomException, ExceptionType
from app.core.security import JWTBearer


# Single, module-level bearer instance so ``login_required`` is one stable
# callable object. That lets tests swap authentication out cleanly via
# ``app.dependency_overrides[login_required] = ...`` (a per-endpoint
# ``Depends(AuthenticateRequired())`` instance could not be targeted this way).
_jwt_bearer = JWTBearer()


def login_required(token: str = Depends(_jwt_bearer)) -> User:
    """FastAPI dependency: require a valid Bearer token and return the user.

    Attach to protected routes with ``current_user: User = Depends(login_required)``.
    """
    return UserService().get_me(token)


class AuthenticateRequired:
    def __init__(self, *args):
        self.http_authorization_credentials = None

    def __call__(self, http_authorization_credentials=Depends(JWTBearer())):
        print("========== Authenticate Required ==========", flush=True)
        return UserService().get_me(http_authorization_credentials)


class PermissionRequired:
    def __init__(self, *args):
        self.user = None
        self.permissions = args

    def __call__(self, user: User = Depends(AuthenticateRequired())):
        self.user = user
        if self.user.role not in self.permissions and self.permissions:
            raise CustomException(exception=ExceptionType.FORBIDDEN)
