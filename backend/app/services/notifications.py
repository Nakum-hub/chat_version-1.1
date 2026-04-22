from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.inquiry import Inquiry
from app.models.outbox import OutboxEvent
from app.models.site import ContactProfile
from app.services.outbox import OutboxHandler

logger = logging.getLogger(__name__)


def get_outbox_handlers() -> dict[str, OutboxHandler]:
    return {
        "inquiry.created": handle_inquiry_created,
        "inquiry.updated": handle_inquiry_updated,
    }


def handle_inquiry_created(session: Session, event: OutboxEvent) -> None:
    inquiry = _load_inquiry(session, event)
    if inquiry is None:
        return

    profile = _load_contact_profile(session)
    recipients = _resolve_recipients(profile=profile, route_target=event.payload.get("route_target"))
    if not recipients:
        logger.info("Skipping inquiry.created notification because no recipients were resolved.", extra={"event_id": event.id})
        return

    subject = f"New Cyberfyx inquiry: {inquiry.interest_option.label}"
    body = "\n".join(
        [
            "A new inquiry was submitted through the Cyberfyx website.",
            "",
            f"Inquiry ID: {inquiry.id}",
            f"Interest: {inquiry.interest_option.label} ({inquiry.interest_option.slug})",
            f"Name: {inquiry.name}",
            f"Email: {inquiry.email}",
            f"Company: {inquiry.company or '-'}",
            f"Source page: {inquiry.source_page or '-'}",
            f"Track: {inquiry.solution_track_slug or '-'}",
            f"CTA label: {inquiry.cta_label or '-'}",
            f"Referrer URL: {inquiry.referrer_url or '-'}",
            "",
            "Message:",
            inquiry.message or "-",
        ]
    )
    _send_email(subject=subject, body=body, recipients=recipients, event=event)


def handle_inquiry_updated(session: Session, event: OutboxEvent) -> None:
    inquiry = _load_inquiry(session, event)
    if inquiry is None:
        return

    profile = _load_contact_profile(session)
    recipients = []
    if inquiry.assigned_to is not None and inquiry.assigned_to.email:
        recipients.append(inquiry.assigned_to.email)
    recipients.extend(_resolve_recipients(profile=profile, route_target=inquiry.interest_option.route_target))
    recipients = _dedupe(recipients)
    if not recipients:
        logger.info("Skipping inquiry.updated notification because no recipients were resolved.", extra={"event_id": event.id})
        return

    changes = event.payload.get("changes") if isinstance(event.payload, dict) else None
    change_lines = []
    if isinstance(changes, dict):
        for field, value in changes.items():
            change_lines.append(f"- {field}: {value}")

    subject = f"Inquiry updated: {inquiry.name} ({inquiry.interest_option.label})"
    body = "\n".join(
        [
            "A Cyberfyx inquiry was updated.",
            "",
            f"Inquiry ID: {inquiry.id}",
            f"Name: {inquiry.name}",
            f"Email: {inquiry.email}",
            f"Current status: {inquiry.status.value}",
            f"Assigned to: {inquiry.assigned_to.display_name if inquiry.assigned_to else '-'}",
            "",
            "Changes:",
            *(change_lines or ["- No field diff was recorded."]),
        ]
    )
    _send_email(subject=subject, body=body, recipients=recipients, event=event)


def _load_inquiry(session: Session, event: OutboxEvent) -> Inquiry | None:
    inquiry_id = event.payload.get("inquiry_id") if isinstance(event.payload, dict) else None
    if not inquiry_id:
        logger.warning("Outbox event is missing inquiry_id.", extra={"event_id": event.id, "topic": event.topic})
        return None

    inquiry = session.scalar(
        select(Inquiry)
        .where(Inquiry.id == inquiry_id)
        .options(
            joinedload(Inquiry.interest_option),
            joinedload(Inquiry.assigned_to),
        )
    )
    if inquiry is None:
        logger.warning("Outbox inquiry target was not found.", extra={"event_id": event.id, "inquiry_id": inquiry_id})
    return inquiry


def _load_contact_profile(session: Session) -> ContactProfile | None:
    return session.scalar(select(ContactProfile).where(ContactProfile.profile_key == "primary"))


def _resolve_recipients(*, profile: ContactProfile | None, route_target: str | None) -> list[str]:
    settings = get_settings()
    recipients = []

    if route_target == "hr" and profile and profile.hr_email:
        recipients.append(profile.hr_email)
    else:
        if settings.smtp_sales_to:
            recipients.append(settings.smtp_sales_to)
        if profile and profile.sales_email:
            recipients.append(profile.sales_email)

    return _dedupe(recipients)


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for value in values:
        normalized = value.strip().lower()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _send_email(*, subject: str, body: str, recipients: list[str], event: OutboxEvent) -> None:
    settings = get_settings()
    if not settings.smtp_enabled:
        logger.info(
            "SMTP is not configured; skipping email delivery for outbox event.",
            extra={"event_id": event.id, "topic": event.topic, "recipients": recipients},
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
