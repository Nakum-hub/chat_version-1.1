from fastapi import APIRouter

from app.api.internal.auth import router as internal_auth_router
from app.api.internal.inquiries import router as internal_inquiries_router
from app.api.internal.staff import router as internal_staff_router
from app.api.public.catalog import router as public_catalog_router
from app.api.public.inquiries import router as public_inquiries_router
from app.api.public.site import router as public_site_router
from app.core.config import get_settings

api_router = APIRouter()
api_router.include_router(public_site_router, prefix="/api/v1/public")
api_router.include_router(public_catalog_router, prefix="/api/v1/public")
api_router.include_router(public_inquiries_router, prefix="/api/v1/public")

if get_settings().enable_internal_api:
    api_router.include_router(internal_auth_router, prefix="/api/v1/internal")
    api_router.include_router(internal_inquiries_router, prefix="/api/v1/internal")
    api_router.include_router(internal_staff_router, prefix="/api/v1/internal")
