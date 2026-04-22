from urllib.parse import urlparse

from fastapi import APIRouter, Request, status, Depends
from pydantic import ValidationError

from app.api.dependencies import DBSession
from app.core.errors import AppError, build_validation_details
from app.schemas.inquiry import InquiryCreate, InquiryCreateResponse
from app.services.inquiry import InquiryContext, create_inquiry

router = APIRouter(prefix="/inquiries", tags=["public-inquiries"])


async def _parse_inquiry_payload(request: Request) -> InquiryCreate:
    content_type = (request.headers.get("content-type") or "").split(";")[0].strip().lower()

    try:
        if content_type in {"application/x-www-form-urlencoded", "multipart/form-data"}:
            payload_data = dict(await request.form())
        else:
            payload_data = await request.json()
    except Exception as exc:
        raise AppError(
            code="validation_error",
            message="The request payload is invalid.",
            status_code=422,
        ) from exc

    try:
        payload = InquiryCreate.model_validate(payload_data)
    except ValidationError as exc:
        raise AppError(
            code="validation_error",
            message="The request payload is invalid.",
            status_code=422,
            details=build_validation_details(exc.errors()),
        ) from exc

    referrer_url = payload.referrer_url or request.headers.get("referer")
    source_page = payload.source_page
    if source_page is None and referrer_url:
        source_page = urlparse(referrer_url).path or None

    return payload.model_copy(
        update={
            "referrer_url": referrer_url,
            "source_page": source_page,
        }
    )


@router.post("", response_model=InquiryCreateResponse, status_code=status.HTTP_201_CREATED)
async def submit_inquiry( request: Request, session: DBSession, payload: InquiryCreate = Depends(_parse_inquiry_payload) ) -> InquiryCreateResponse:
    inquiry = create_inquiry(
        session,
        payload=payload,
        context=InquiryContext(
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        ),
    )
    return InquiryCreateResponse(
        id=inquiry.id,
        status=inquiry.status,
        message="Your inquiry has been received. The Cyberfyx team will review it shortly.",
    )
