from datetime import datetime
from typing import Any
from pydantic import EmailStr, Field, field_validator, model_validator

from app.models.enums import InquiryStatus, StaffRole
from app.schemas.common import APIModel, PageMeta

INTEREST_SLUG_ALIASES = {
    "cybersecurity": "cybersecurity-services",
    "endpoint": "endpoint-management-services",
    "endpoint-management": "endpoint-management-services",
    "itsecurity": "it-security-and-continuity",
    "it-security": "it-security-and-continuity",
    "iso": "iso-consultation-services",
    "other": "general-inquiry",
}


class InquiryCreate(APIModel):
    name: str = Field(
        min_length=2,
        max_length=120,
    )
    email: EmailStr
    company: str | None = Field(default=None, max_length=160)
    interest_slug: str = Field(
        min_length=2,
        max_length=80,
    )
    message: str | None = Field(default=None, max_length=5000)
    source_page: str | None = Field(default=None, max_length=160)
    solution_track_slug: str | None = Field(default=None, max_length=120)
    cta_label: str | None = Field(default=None, max_length=160)
    referrer_url: str | None = Field(default=None, max_length=500)
    utm_source: str | None = Field(default=None, max_length=120)
    utm_medium: str | None = Field(default=None, max_length=120)
    utm_campaign: str | None = Field(default=None, max_length=120)
    utm_content: str | None = Field(default=None, max_length=120)
    utm_term: str | None = Field(default=None, max_length=120)

    @model_validator(mode="before")
    @classmethod
    def _map_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" not in data and "full_name" in data:
                data["name"] = data["full_name"]
            
            for alias in ["subject", "interest", "service"]:
                if "interest_slug" not in data and alias in data:
                    data["interest_slug"] = data[alias]
                    break
        return data

    @field_validator("name", "company", "message", "source_page", "solution_track_slug", "cta_label", mode="before")
    @classmethod
    def _strip_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("interest_slug", mode="before")
    @classmethod
    def _normalize_interest_slug(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("interest_slug is required.")
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("interest_slug is required.")
        return INTEREST_SLUG_ALIASES.get(normalized, normalized)


class InquiryCreateResponse(APIModel):
    id: str
    status: InquiryStatus
    message: str


class InquiryAuditEventRead(APIModel):
    id: str
    event_type: str
    note: str | None
    payload: dict | None
    actor_user_id: str | None
    created_at: datetime


class InquiryAssigneeRead(APIModel):
    id: str
    email: EmailStr
    display_name: str
    role: StaffRole


class InquiryRead(APIModel):
    id: str
    name: str
    email: EmailStr
    company: str | None
    message: str | None
    source_page: str | None
    solution_track_slug: str | None
    cta_label: str | None
    referrer_url: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_content: str | None
    utm_term: str | None
    status: InquiryStatus
    first_response_at: datetime | None
    created_at: datetime
    updated_at: datetime
    interest_slug: str
    interest_label: str
    assigned_to: InquiryAssigneeRead | None
    audit_events: list[InquiryAuditEventRead] = Field(default_factory=list)


class InquiryListResponse(APIModel):
    items: list[InquiryRead]
    meta: PageMeta


class InquiryUpdate(APIModel):
    status: InquiryStatus | None = None
    assigned_to_user_id: str | None = None
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("note", mode="before")
    @classmethod
    def _strip_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None
