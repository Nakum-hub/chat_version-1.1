from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.models.enums import StaffRole
from app.models.staff import StaffUser

DBSession = Annotated[Session, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    session: DBSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> StaffUser:
    if credentials is None:
        raise AppError(code="not_authenticated", message="Authentication is required.", status_code=401)

    token_payload = decode_access_token(credentials.credentials)
    user = session.scalar(select(StaffUser).where(StaffUser.id == token_payload["sub"]))
    if user is None or not user.is_active:
        raise AppError(code="invalid_user", message="The authenticated user is not available.", status_code=401)
    return user


def require_roles(*allowed_roles: StaffRole) -> Callable[[StaffUser], StaffUser]:
    def _require(current_user: Annotated[StaffUser, Depends(get_current_user)]) -> StaffUser:
        if current_user.role not in allowed_roles:
            raise AppError(
                code="forbidden",
                message="You do not have permission to perform this action.",
                status_code=403,
            )
        return current_user

    return _require