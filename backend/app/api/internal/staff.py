from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import DBSession, require_roles
from app.models.enums import StaffRole
from app.models.staff import StaffUser
from app.schemas.auth import StaffUserRead
from app.services.staff import list_staff_users

router = APIRouter(prefix="/staff-users", tags=["internal-staff"])

AllowedInternalUser = Annotated[
    StaffUser,
    Depends(
        require_roles(
            StaffRole.super_admin,
            StaffRole.sales_admin,
            StaffRole.content_admin,
            StaffRole.recruiter,
            StaffRole.viewer,
        )
    ),
]


@router.get("", response_model=list[StaffUserRead])
def read_staff_users(
    session: DBSession,
    current_user: AllowedInternalUser,
    role: StaffRole | None = None,
    search: str | None = None,
    active_only: bool = True,
    limit: int = Query(default=100, ge=1, le=200),
) -> list[StaffUserRead]:
    users = list_staff_users(
        session,
        role=role,
        search=search,
        active_only=active_only,
        limit=limit,
    )
    return [StaffUserRead.model_validate(user) for user in users]
