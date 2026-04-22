from fastapi import APIRouter

from app.api.dependencies import DBSession
from app.schemas.site import ContactInterestOptionRead, ContactProfileRead, OfficePresenceRegionRead, SiteSearchEntryRead
from app.services.site import get_public_contact_profile, list_public_search_entries

router = APIRouter(prefix="/site", tags=["public-site"])


@router.get("/contact-profile", response_model=ContactProfileRead)
def read_contact_profile(session: DBSession) -> ContactProfileRead:
    profile = get_public_contact_profile(session)
    return ContactProfileRead(
        profile_key=profile.profile_key,
        sales_email=profile.sales_email,
        hr_email=profile.hr_email,
        primary_phone=profile.primary_phone,
        headquarters_name=profile.headquarters_name,
        headquarters_address=profile.headquarters_address,
        map_url=profile.map_url,
        office_regions=[OfficePresenceRegionRead.model_validate(region) for region in profile.office_regions],
        interest_options=[
            ContactInterestOptionRead.model_validate(option)
            for option in profile.interest_options
            if option.is_active
        ],
    )


@router.get("/contact-interests", response_model=list[ContactInterestOptionRead])
def read_contact_interests(session: DBSession) -> list[ContactInterestOptionRead]:
    profile = get_public_contact_profile(session)
    return [
        ContactInterestOptionRead.model_validate(option)
        for option in profile.interest_options
        if option.is_active
    ]


@router.get("/search-index", response_model=list[SiteSearchEntryRead])
def read_search_index() -> list[SiteSearchEntryRead]:
    return [SiteSearchEntryRead.model_validate(entry) for entry in list_public_search_entries()]
