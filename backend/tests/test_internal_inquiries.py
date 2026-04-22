from __future__ import annotations

from .helpers import assert_problem_response, extract_collection_items


def test_internal_auth_token_requires_known_staff_credentials(client, seeded_db):
    response = client.post(
        "/api/v1/internal/auth/token",
        json={"email": "admin@cyberfyx.net", "password": "ChangeMeLonger123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_internal_inquiries_requires_auth(client, seeded_db):
    response = client.get("/api/v1/internal/inquiries")

    assert response.status_code == 401
    assert_problem_response(response.json(), code="not_authenticated")


def test_internal_inquiries_list_and_patch_audit_trail(client, db_session, seeded_db, auth_token):
    from app.models.inquiry import Inquiry, InquiryAuditEvent
    from sqlalchemy import func, select

    headers = {"Authorization": f"Bearer {auth_token}"}

    list_response = client.get("/api/v1/internal/inquiries", headers=headers)
    assert list_response.status_code == 200

    inquiries = extract_collection_items(list_response.json())
    assert any(inquiry["id"] == seeded_db.inquiry_id for inquiry in inquiries)

    before_audit_count = db_session.scalar(
        select(func.count()).select_from(InquiryAuditEvent).where(InquiryAuditEvent.inquiry_id == seeded_db.inquiry_id)
    )

    patch_response = client.patch(
        f"/api/v1/internal/inquiries/{seeded_db.inquiry_id}",
        headers=headers,
        json={
            "status": "triaged",
            "assigned_to_user_id": seeded_db.reviewer_user_id,
            "note": "Reviewed and assigned for follow-up.",
        },
    )

    assert patch_response.status_code == 200
    updated = patch_response.json()
    assert updated["status"] == "triaged"
    assert updated["assigned_to"]["id"] == seeded_db.reviewer_user_id

    after_audit_count = db_session.scalar(
        select(func.count()).select_from(InquiryAuditEvent).where(InquiryAuditEvent.inquiry_id == seeded_db.inquiry_id)
    )
    assert after_audit_count == before_audit_count + 1

    refreshed = db_session.get(Inquiry, seeded_db.inquiry_id)
    assert refreshed is not None
    assert refreshed.status.value == "triaged"
    assert refreshed.assigned_to_user_id == seeded_db.reviewer_user_id
