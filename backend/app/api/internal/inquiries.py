from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import DBSession, require_roles
from app.models.enums import InquiryStatus, StaffRole
from app.models.inquiry import Inquiry
from app.models.staff import StaffUser
from app.schemas.inquiry import (
    InquiryAssigneeRead,
    InquiryAuditEventRead,
    InquiryListResponse,
    InquiryRead,
    InquiryUpdate,
)
from app.schemas.common import PageMeta
from app.services.inquiry import get_inquiry_by_id, list_inquiries, update_inquiry

router = APIRouter(prefix="/inquiries", tags=["internal-inquiries"])

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

MutatingInternalUser = Annotated[
    StaffUser,
    Depends(
        require_roles(
            StaffRole.super_admin,
            StaffRole.sales_admin,
            StaffRole.recruiter,
        )
    ),
]


def _serialize_inquiry(inquiry: Inquiry) -> InquiryRead:
    assigned_to = None
    if inquiry.assigned_to is not None:
        assigned_to = InquiryAssigneeRead.model_validate(inquiry.assigned_to)

    return InquiryRead(
        id=inquiry.id,
        name=inquiry.name,
        email=inquiry.email,
        company=inquiry.company,
        message=inquiry.message,
        source_page=inquiry.source_page,
        solution_track_slug=inquiry.solution_track_slug,
        cta_label=inquiry.cta_label,
        referrer_url=inquiry.referrer_url,
        utm_source=inquiry.utm_source,
        utm_medium=inquiry.utm_medium,
        utm_campaign=inquiry.utm_campaign,
        utm_content=inquiry.utm_content,
        utm_term=inquiry.utm_term,
        status=inquiry.status,
        first_response_at=inquiry.first_response_at,
        created_at=inquiry.created_at,
        updated_at=inquiry.updated_at,
        interest_slug=inquiry.interest_option.slug,
        interest_label=inquiry.interest_option.label,
        assigned_to=assigned_to,
        audit_events=[InquiryAuditEventRead.model_validate(event) for event in inquiry.audit_events],
    )


@router.get("", response_model=InquiryListResponse)
def read_inquiries(
    session: DBSession,
    current_user: AllowedInternalUser,
    status: InquiryStatus | None = None,
    interest_slug: str | None = None,
    assigned_to_user_id: str | None = None,
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> InquiryListResponse:
    items, total = list_inquiries(
        session,
        status=status,
        interest_slug=interest_slug,
        assigned_to_user_id=assigned_to_user_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return InquiryListResponse(
        items=[_serialize_inquiry(item) for item in items],
        meta=PageMeta(limit=limit, offset=offset, total=total),
    )


@router.get("/{inquiry_id}", response_model=InquiryRead)
def read_inquiry(inquiry_id: str, session: DBSession, current_user: AllowedInternalUser) -> InquiryRead:
    inquiry = get_inquiry_by_id(session, inquiry_id=inquiry_id)
    return _serialize_inquiry(inquiry)


@router.patch("/{inquiry_id}", response_model=InquiryRead)
def patch_inquiry(
    inquiry_id: str,
    payload: InquiryUpdate,
    session: DBSession,
    current_user: MutatingInternalUser,
) -> InquiryRead:
    inquiry = update_inquiry(session, inquiry_id=inquiry_id, payload=payload, actor=current_user)
    return _serialize_inquiry(inquiry)