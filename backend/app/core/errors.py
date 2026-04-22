import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


def build_validation_details(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details = []
    for error in errors:
        location = ".".join(str(part) for part in error.get("loc", []) if part != "body") or None
        details.append(
            {
                "field": location,
                "message": error.get("msg", "Invalid request."),
                "type": error.get("type"),
            }
        )
    return details


def _error_payload(
    *,
    request: Request,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", None)
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": request_id,
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                request=request,
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_error_payload(
                request=request,
                code="validation_error",
                message="The request payload is invalid.",
                details=build_validation_details(exc.errors()),
            ),
        )

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                request=request,
                code="http_error",
                message=str(exc.detail),
            ),
        )

    @app.exception_handler(Exception)
    async def _unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", extra={"request_id": getattr(request.state, "request_id", None)})
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                request=request,
                code="internal_error",
                message="An unexpected server error occurred.",
            ),
        )
