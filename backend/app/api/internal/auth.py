from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError

from app.api.dependencies import DBSession, get_current_user
from app.core.errors import AppError, build_validation_details
from app.models.staff import StaffUser
from app.schemas.auth import StaffUserRead, TokenRequest, TokenResponse
from app.services.auth import authenticate_user

router = APIRouter(prefix="/auth", tags=["internal-auth"])


@router.post("/token", response_model=TokenResponse)
async def issue_token(request: Request, session: DBSession) -> TokenResponse:
    content_type = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
    try:
        if content_type == "application/x-www-form-urlencoded":
            form_data = await request.form()
            payload = TokenRequest.model_validate(
                {
                    "email": form_data.get("email") or form_data.get("username"),
                    "password": form_data.get("password"),
                }
            )
        else:
            try:
                request_data = await request.json()
            except Exception as exc:
                raise AppError(
                    code="validation_error",
                    message="The request payload is invalid.",
                    status_code=422,
                ) from exc
            payload = TokenRequest.model_validate(request_data)
    except ValidationError as exc:
        raise AppError(
            code="validation_error",
            message="The request payload is invalid.",
            status_code=422,
            details=build_validation_details(exc.errors()),
        ) from exc
    return authenticate_user(session, email=payload.email, password=payload.password)


@router.get("/me", response_model=StaffUserRead)
def read_current_user(current_user: Annotated[StaffUser, Depends(get_current_user)]) -> StaffUserRead:
    return StaffUserRead.model_validate(current_user)
