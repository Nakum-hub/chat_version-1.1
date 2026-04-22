from __future__ import annotations

from typing import Any


def extract_collection_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload

    if not isinstance(payload, dict):
        raise AssertionError(f"Expected collection payload, got {type(payload)!r}")

    for key in ("items", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return value

    raise AssertionError(f"Could not find a collection in payload keys: {sorted(payload.keys())}")


def assert_problem_response(payload: Any, *, code: str) -> None:
    assert isinstance(payload, dict)
    assert "error" in payload
    error = payload["error"]
    assert isinstance(error, dict)
    assert error["code"] == code
    assert "message" in error


def public_inquiry_payload(
    *,
    name: str = "Jordan Lee",
    email: str = "jordan.lee@example.com",
    company: str = "Northwind Manufacturing",
    interest_slug: str = "endpoint-management-services",
    message: str = "We need help with audit readiness and endpoint control.",
    source_page: str = "/contact",
    solution_track_slug: str = "endpoint-operations",
    cta_label: str = "Request a consultation",
    referrer_url: str = "https://cyberfyx.net/contact",
) -> dict[str, str]:
    return {
        "name": name,
        "email": email,
        "company": company,
        "interest_slug": interest_slug,
        "message": message,
        "source_page": source_page,
        "solution_track_slug": solution_track_slug,
        "cta_label": cta_label,
        "referrer_url": referrer_url,
    }
