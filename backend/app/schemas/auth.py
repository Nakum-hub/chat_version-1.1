from datetime import datetime

from pydantic import EmailStr, Field

from app.models.enums import StaffRole
from app.schemas.common import APIModel


class StaffUserRead(APIModel):
    id: str
    email: EmailStr
    display_name: str
    role: StaffRole
    is_active: bool
    last_login_at: datetime | None


class TokenRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user: StaffUserRead