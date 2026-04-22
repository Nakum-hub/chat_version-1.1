from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.config import get_settings
from app.core.errors import AppError
from app.models.enums import InquiryStatus
from app.models.inquiry import Inquiry, InquiryAuditEvent
from app.models.site import ContactInterestOption, ContactProfile
from app.models.staff import StaffUser
from app.schemas.inquiry import InquiryCreate, InquiryUpdate
from app.services.outbox import enqueue_outbox_event


@dataclass(frozen=True)
class InquiryContext:
    client_ip: str | None
    user_agent: str | None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _hash_value(value: str | None) -> str | None:
    if not value:
        return None
    return sha256(value.encode("utf-8")).hexdigest()


def _message_dedup_basis(payload: InquiryCreate, interest_option_id: str) -> str:
    normalized_message = _normalize_optional(payload.message) or ""
    normalized_company = _normalize_optional(payload.company) or ""
    return "|".join(
        [
            payload.email.strip().lower(),
            interest_option_id,
            normalized_company.lower(),
            normalized_message.lower(),
        ]
    )


def _load_active_interest_option(session: Session, interest_slug: str) -> ContactInterestOption:
    statement = (
        select(ContactInterestOption)
        .join(ContactProfile, ContactInterestOption.contact_profile_id == ContactProfile.id)
        .where(
            ContactProfile.profile_key == "primary",
            ContactProfile.published.is_(True),
            ContactInterestOption.slug == interest_slug,
            ContactInterestOption.is_active.is_(True),
        )
    )
    option = session.scalar(statement)
    if option is None:
        raise AppError(
            code="invalid_interest",
            message="The selected inquiry interest is not valid.",
            status_code=422,
            details=[{"field": "interest_slug", "message": "Unsupported interest option."}],
        )
    return option


def _enforce_rate_limit(session: Session, *, normalized_email: str, ip_hash: str | None) -> None:
    settings = get_settings()
    cutoff = _utcnow() - timedelta(minutes=settings.inquiry_rate_limit_window_minutes)

    filters = [Inquiry.email == normalized_email]
    if ip_hash:
        filters.append(Inquiry.ip_hash == ip_hash)

    recent_count = session.scalar(
        select(func.count(Inquiry.id)).where(
            Inquiry.created_at >= cutoff,
            or_(*filters),
        )
    )
    if int(recent_count or 0) >= settings.inquiry_rate_limit_count:
        raise AppError(
            code="rate_limit_exceeded",
            message="Too many inquiries were submitted recently. Please wait before trying again.",
            status_code=429,
        )


def _enforce_duplicate_window(
    session: Session,
    *,
    normalized_email: str,
    interest_option_id: str,
    message_hash: str | None,
) -> None:
    if message_hash is None:
        return

    settings = get_settings()
    cutoff = _utcnow() - timedelta(hours=settings.inquiry_duplicate_window_hours)
    duplicate = session.scalar(
        select(Inquiry.id).where(
            Inquiry.email == normalized_email,
            Inquiry.interest_option_id == interest_option_id,
            Inquiry.message_hash == message_hash,
            Inquiry.created_at >= cutoff,
        )
    )
    if duplicate is not None:
        raise AppError(
            code="duplicate_inquiry",
            message="A matching inquiry was already submitted recently.",
            status_code=409,
        )


def create_inquiry(session: Session, *, payload: InquiryCreate, context: InquiryContext) -> Inquiry:
    normalized_email = payload.email.strip().lower()
    interest_option = _load_active_interest_option(session, payload.interest_slug)
    message_hash = _hash_value(_message_dedup_basis(payload, interest_option.id))
    ip_hash = _hash_value(context.client_ip)

    _enforce_rate_limit(session, normalized_email=normalized_email, ip_hash=ip_hash)
    _enforce_duplicate_window(
        session,
        normalized_email=normalized_email,
        interest_option_id=interest_option.id,
        message_hash=message_hash,
    )

    inquiry = Inquiry(
        name=payload.name.strip(),
        email=normalized_email,
        company=_normalize_optional(payload.company),
        message=_normalize_optional(payload.message),
        source_page=_normalize_optional(payload.source_page),
        solution_track_slug=_normalize_optional(payload.solution_track_slug),
        cta_label=_normalize_optional(payload.cta_label),
        referrer_url=_normalize_optional(payload.referrer_url),
        utm_source=_normalize_optional(payload.utm_source),
        utm_medium=_normalize_optional(payload.utm_medium),
        utm_campaign=_normalize_optional(payload.utm_campaign),
        utm_content=_normalize_optional(payload.utm_content),
        utm_term=_normalize_optional(payload.utm_term),
        user_agent=_normalize_optional(context.user_agent),
        ip_hash=ip_hash,
        message_hash=message_hash,
        interest_option_id=interest_option.id,
    )
    session.add(inquiry)
    session.flush()

    session.add(
        InquiryAuditEvent(
            inquiry_id=inquiry.id,
            event_type="inquiry_created",
            payload={
                "interest_slug": interest_option.slug,
                "source_page": inquiry.source_page,
                "solution_track_slug": inquiry.solution_track_slug,
                "cta_label": inquiry.cta_label,
            },
        )
    )
    enqueue_outbox_event(
        session,
        topic="inquiry.created",
        payload={
            "inquiry_id": inquiry.id,
            "interest_slug": interest_option.slug,
            "route_target": interest_option.route_target,
        },
    )
    session.commit()
    return get_inquiry_by_id(session, inquiry_id=inquiry.id)


def get_inquiry_by_id(session: Session, *, inquiry_id: str) -> Inquiry:
    statement = (
        select(Inquiry)
        .where(Inquiry.id == inquiry_id)
        .options(
            joinedload(Inquiry.interest_option),
            joinedload(Inquiry.assigned_to),
            selectinload(Inquiry.audit_events),
        )
    )
    inquiry = session.scalar(statement)
    if inquiry is None:
        raise AppError(code="inquiry_not_found", message="The inquiry was not found.", status_code=404)
    return inquiry


def list_inquiries(
    session: Session,
    *,
    status: InquiryStatus | None,
    interest_slug: str | None,
    assigned_to_user_id: str | None,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Inquiry], int]:
    filters = []
    if status is not None:
        filters.append(Inquiry.status == status)
    if assigned_to_user_id:
        filters.append(Inquiry.assigned_to_user_id == assigned_to_user_id)
    if interest_slug:
        filters.append(ContactInterestOption.slug == interest_slug.strip().lower())
    if search:
        like_term = f"%{search.strip().lower()}%"
        filters.append(
            or_(
                func.lower(Inquiry.name).like(like_term),
                func.lower(Inquiry.email).like(like_term),
                func.lower(func.coalesce(Inquiry.company, "")).like(like_term),
            )
        )

    base = select(Inquiry).join(ContactInterestOption, Inquiry.interest_option_id == ContactInterestOption.id)
    if filters:
        base = base.where(*filters)

    total = int(session.scalar(select(func.count()).select_from(base.subquery())) or 0)
    items = list(
        session.scalars(
            base.options(
                joinedload(Inquiry.interest_option),
                joinedload(Inquiry.assigned_to),
                selectinload(Inquiry.audit_events),
            )
            .order_by(Inquiry.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return items, total


def update_inquiry(
    session: Session,
    *,
    inquiry_id: str,
    payload: InquiryUpdate,
    actor: StaffUser,
) -> Inquiry:
    inquiry = get_inquiry_by_id(session, inquiry_id=inquiry_id)
    changes: dict[str, str | None] = {}

    if payload.assigned_to_user_id is not None and payload.assigned_to_user_id != inquiry.assigned_to_user_id:
        assignee = None
        if payload.assigned_to_user_id:
            assignee = session.scalar(select(StaffUser).where(StaffUser.id == payload.assigned_to_user_id))
            if assignee is None or not assignee.is_active:
                raise AppError(
                    code="invalid_assignee",
                    message="The selected assignee is not valid.",
                    status_code=422,
                    details=[{"field": "assigned_to_user_id", "message": "Unknown or inactive staff user."}],
                )
        inquiry.assigned_to_user_id = payload.assigned_to_user_id
        inquiry.assigned_to = assignee
        changes["assigned_to_user_id"] = payload.assigned_to_user_id

    if payload.status is not None and payload.status != inquiry.status:
        previous_status = inquiry.status.value
        inquiry.status = payload.status
        changes["status"] = payload.status.value
        changes["previous_status"] = previous_status
        if payload.status == InquiryStatus.responded and inquiry.first_response_at is None:
            inquiry.first_response_at = _utcnow()

    note = _normalize_optional(payload.note)
    if not changes and note is None:
        raise AppError(
            code="no_changes_provided",
            message="At least one field must change before an inquiry can be updated.",
            status_code=400,
        )

    session.add(
        InquiryAuditEvent(
            inquiry_id=inquiry.id,
            actor_user_id=actor.id,
            event_type="inquiry_updated",
            note=note,
            payload=changes or None,
        )
    )
    if changes:
        enqueue_outbox_event(
            session,
            topic="inquiry.updated",
            payload={"inquiry_id": inquiry.id, "changes": changes, "actor_user_id": actor.id},
        )

    session.add(inquiry)
    session.commit()
    return get_inquiry_by_id(session, inquiry_id=inquiry.id)