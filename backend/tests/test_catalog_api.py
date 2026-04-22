"""Tests for the public solution-tracks catalog endpoints."""
from __future__ import annotations

from tests.helpers import extract_collection_items


class TestListSolutionTracks:
    def test_returns_all_published_tracks(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks")
        assert r.status_code == 200
        items = extract_collection_items(r.json())
        assert len(items) == 5

    def test_ordered_by_display_order(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks")
        items = extract_collection_items(r.json())
        orders = [item["display_order"] for item in items]
        assert orders == sorted(orders)

    def test_list_item_fields_present(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks")
        items = extract_collection_items(r.json())
        required = {"slug", "title", "short_summary", "hero_title", "hero_body", "cta_label", "cta_target"}
        for item in items:
            assert required.issubset(item.keys()), f"Missing fields in {item['slug']}"

    def test_no_draft_tracks_returned(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks")
        items = extract_collection_items(r.json())
        # All seeded tracks are published; verify no 'publication_status' leaks
        for item in items:
            assert "publication_status" not in item


class TestGetSolutionTrackDetail:
    def test_cybersecurity_track(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/cybersecurity")
        assert r.status_code == 200
        data = r.json()
        assert data["slug"] == "cybersecurity"
        assert data["hero_title"]
        assert data["hero_body"]

    def test_detail_includes_offerings(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/cybersecurity")
        data = r.json()
        assert "offerings" in data
        assert isinstance(data["offerings"], list)
        assert len(data["offerings"]) > 0

    def test_offering_has_required_fields(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/cybersecurity")
        offerings = r.json()["offerings"]
        required = {"slug", "title", "kicker", "description", "display_order", "taxonomy_terms"}
        for offering in offerings:
            assert required.issubset(offering.keys())

    def test_offering_taxonomy_terms_are_list(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/cybersecurity")
        for offering in r.json()["offerings"]:
            assert isinstance(offering["taxonomy_terms"], list)
            for term in offering["taxonomy_terms"]:
                assert {"group", "slug", "label"}.issubset(term.keys())

    def test_endpoint_track_includes_catalog_rows(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/endpoint-operations")
        assert r.status_code == 200
        data = r.json()
        assert "endpoint_rows" in data
        assert isinstance(data["endpoint_rows"], list)
        assert len(data["endpoint_rows"]) > 0
        row = data["endpoint_rows"][0]
        assert {"product_name", "solution_name", "service_name"}.issubset(row.keys())

    def test_non_endpoint_track_has_empty_catalog_rows(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/cybersecurity")
        assert r.json()["endpoint_rows"] == []

    def test_detail_has_meta_fields(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/it-security")
        data = r.json()
        assert "meta_title" in data
        assert "meta_description" in data

    def test_all_five_track_slugs_resolve(self, client, seeded_db):
        slugs = [
            "cybersecurity",
            "it-security",
            "endpoint-operations",
            "core-industry-services",
            "training",
        ]
        for slug in slugs:
            r = client.get(f"/api/v1/public/solution-tracks/{slug}")
            assert r.status_code == 200, f"Track slug '{slug}' returned {r.status_code}"

    def test_unknown_slug_returns_404(self, client, seeded_db):
        r = client.get("/api/v1/public/solution-tracks/does-not-exist")
        assert r.status_code == 404
