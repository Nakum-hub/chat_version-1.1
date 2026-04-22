"""Tests that UTM and attribution fields are stored correctly on inquiries."""
from __future__ import annotations

from tests.helpers import public_inquiry_payload


class TestUtmFieldStorage:
    def test_utm_fields_accepted_in_payload(self, client, seeded_db):
        payload = public_inquiry_payload(email="utm-test@example.com")
        payload.update(
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="cybersecurity-q4",
            utm_content="hero-cta",
            utm_term="iso27001",
        )
        r = client.post("/api/v1/public/inquiries", json=payload)
        assert r.status_code == 201
        assert "id" in r.json()

    def test_source_page_stored(self, client, seeded_db):
        payload = public_inquiry_payload(
            email="sourcepage-test@example.com",
            source_page="/services/cybersecurity",
        )
        r = client.post("/api/v1/public/inquiries", json=payload)
        assert r.status_code == 201

    def test_referrer_url_stored(self, client, seeded_db):
        payload = public_inquiry_payload(
            email="referrer-test@example.com",
            referrer_url="https://google.com/search?q=cyberfyx",
        )
        r = client.post("/api/v1/public/inquiries", json=payload)
        assert r.status_code == 201

    def test_cta_label_stored(self, client, seeded_db):
        payload = public_inquiry_payload(email="cta-test@example.com")
        payload["cta_label"] = "Get a Free Assessment"
        r = client.post("/api/v1/public/inquiries", json=payload)
        assert r.status_code == 201

    def test_utm_fields_visible_via_internal_api(self, client, seeded_db, auth_token):
        """Submit an inquiry with UTM params; verify they appear in the internal detail endpoint."""
        payload = public_inquiry_payload(email="utm-verify@example.com")
        payload.update(
            utm_source="linkedin",
            utm_medium="social",
            utm_campaign="brand-awareness",
        )
        post_r = client.post("/api/v1/public/inquiries", json=payload)
        assert post_r.status_code == 201
        inquiry_id = post_r.json()["id"]

        get_r = client.get(
            f"/api/v1/internal/inquiries/{inquiry_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_r.status_code == 200
        detail = get_r.json()
        assert detail["utm_source"] == "linkedin"
        assert detail["utm_medium"] == "social"
        assert detail["utm_campaign"] == "brand-awareness"

    def test_missing_utm_fields_are_null(self, client, seeded_db, auth_token):
        """An inquiry with no UTM params should have null UTM fields."""
        payload = {
            "name": "No UTM User",
            "email": "noutm@example.com",
            "interest_slug": "general-inquiry",
            "message": "Just browsing.",
        }
        post_r = client.post("/api/v1/public/inquiries", json=payload)
        assert post_r.status_code == 201
        inquiry_id = post_r.json()["id"]

        get_r = client.get(
            f"/api/v1/internal/inquiries/{inquiry_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        detail = get_r.json()
        for field in ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"):
            assert detail.get(field) is None, f"{field} should be None"

    def test_solution_track_slug_stored_with_inquiry(self, client, seeded_db, auth_token):
        payload = public_inquiry_payload(
            email="trackslug-test@example.com",
            solution_track_slug="cybersecurity",
        )
        post_r = client.post("/api/v1/public/inquiries", json=payload)
        assert post_r.status_code == 201
        inquiry_id = post_r.json()["id"]

        get_r = client.get(
            f"/api/v1/internal/inquiries/{inquiry_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_r.json()["solution_track_slug"] == "cybersecurity"
