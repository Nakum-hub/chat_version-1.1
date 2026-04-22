from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.security import create_access_token, verify_password
from app.models.staff import StaffUser
from app.schemas.auth import TokenResponse


def authenticate_user(session: Session, *, email: str, password: str) -> TokenResponse:
    normalized_email = email.strip().lower()
    user = session.scalar(select(StaffUser).where(StaffUser.email == normalized_email))
    if user is None or not verify_password(password, user.password_hash):
        raise AppError(
            code="invalid_credentials",
            message="The provided credentials are invalid.",
            status_code=401,
        )
    if not user.is_active:
        raise AppError(
            code="inactive_user",
            message="This user account is inactive.",
            status_code=403,
        )

    user.last_login_at = datetime.now(timezone.utc)
    session.add(user)
    session.commit()
    session.refresh(user)

    settings = get_settings()
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(
        access_token=token,
        expires_in_seconds=settings.jwt_access_token_expire_minutes * 60,
        user=user,
    )