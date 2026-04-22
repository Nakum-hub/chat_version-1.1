from __future__ import annotations

from sqlalchemy import select

from app.models.enums import OutboxStatus
from app.models.outbox import OutboxEvent
from app.services.notifications import get_outbox_handlers
from app.services.outbox import process_pending_outbox_events

from .helpers import public_inquiry_payload


def test_outbox_worker_completes_pending_inquiry_notifications_without_smtp(client, db_session, seeded_db):
    response = client.post(
        "/api/v1/public/inquiries",
        json=public_inquiry_payload(
            name="Outbox Check",
            email="outbox.check@example.com",
            interest_slug="cybersecurity-services",
            message="Validate worker processing for inquiry notifications."
        ),
    )
    assert response.status_code == 201

    created_event = db_session.scalar(
        select(OutboxEvent)
        .where(OutboxEvent.status == OutboxStatus.pending)
        .order_by(OutboxEvent.created_at.desc())
    )
    assert created_event is not None
    assert created_event.topic == "inquiry.created"

    processed = process_pending_outbox_events(db_session, handlers=get_outbox_handlers())

    assert processed
    db_session.refresh(created_event)
    assert created_event.status == OutboxStatus.completed
    assert created_event.processed_at is not None
    assert created_event.last_error is None
