from pydantic import EmailStr, Field

from app.schemas.common import APIModel


class OfficePresenceRegionRead(APIModel):
    slug: str
    label: str
    display_order: int


class ContactInterestOptionRead(APIModel):
    slug: str
    label: str
    route_target: str
    display_order: int


class ContactProfileRead(APIModel):
    profile_key: str
    sales_email: EmailStr
    hr_email: EmailStr | None
    primary_phone: str
    headquarters_name: str
    headquarters_address: str
    map_url: str
    office_regions: list[OfficePresenceRegionRead]
    interest_options: list[ContactInterestOptionRead]


class SiteSearchEntryRead(APIModel):
    href: str
    title: str
    kind: str
    section: str
    text: str
    excerpt: str | None = None
    keywords: list[str] = Field(default_factory=list)
