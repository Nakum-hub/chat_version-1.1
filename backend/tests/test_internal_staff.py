from __future__ import annotations

from .helpers import extract_collection_items


def test_internal_staff_users_list_returns_assignable_users(client, seeded_db, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/api/v1/internal/staff-users", headers=headers)

    assert response.status_code == 200
    users = extract_collection_items(response.json())
    ids = {user["id"] for user in users}

    assert seeded_db.staff_user_id in ids
    assert seeded_db.reviewer_user_id in ids
    assert all("password_hash" not in user for user in users)
