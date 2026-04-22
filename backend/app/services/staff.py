from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import StaffRole
from app.models.staff import StaffUser


def list_staff_users(
    session: Session,
    *,
    role: StaffRole | None,
    search: str | None,
    active_only: bool,
    limit: int,
) -> list[StaffUser]:
    statement = select(StaffUser)

    if active_only:
        statement = statement.where(StaffUser.is_active.is_(True))
    if role is not None:
        statement = statement.where(StaffUser.role == role)
    if search:
        like_term = f"%{search.strip().lower()}%"
        statement = statement.where(
            or_(
                func.lower(StaffUser.display_name).like(like_term),
                func.lower(StaffUser.email).like(like_term),
            )
        )

    statement = statement.order_by(StaffUser.display_name.asc(), StaffUser.email.asc()).limit(limit)
    return list(session.scalars(statement).all())
