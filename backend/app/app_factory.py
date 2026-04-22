import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import check_database_ready
from app.core.errors import AppError, register_error_handlers
from app.services.site import resolve_frontend_root

settings = get_settings()
API_BASE_META_RE = re.compile(
    r'(<meta\s+name=["\']cyberfyx-api-base["\']\s+content=["\'])([^"\']*)(["\'])',
    flags=re.IGNORECASE,
)


def _within_frontend_root(frontend_root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(frontend_root.resolve())
        return True
    except ValueError:
        return False


def _rewrite_api_base_meta(raw_html: str) -> str:
    return API_BASE_META_RE.sub(r'\1\3', raw_html)


def _safe_frontend_relative_path(request_path: str) -> Path | None:
    normalized = unquote(request_path).strip("/")
    if not normalized:
        return Path()

    relative = PurePosixPath(normalized)
    if any(part in {".", ".."} for part in relative.parts):
        return None

    return Path(*relative.parts)


def _resolve_frontend_document(frontend_root: Path, request_path: str) -> Path | None:
    relative = _safe_frontend_relative_path(request_path)
    if relative is None:
        return None

    candidates = [frontend_root / relative]
    if not relative.suffix:
        candidates.append(frontend_root / relative / "index.html")
        candidates.append(frontend_root / f"{relative}.html")

    for candidate in candidates:
        if candidate.is_file() and _within_frontend_root(frontend_root, candidate):
            return candidate

    return None


def _frontend_response(frontend_root: Path, document: Path) -> FileResponse | HTMLResponse:
    if document.suffix.lower() == ".html":
        raw_html = document.read_text(encoding="utf-8", errors="ignore")
        return HTMLResponse(_rewrite_api_base_meta(raw_html))

    return FileResponse(document)


def _register_frontend(app: FastAPI) -> None:
    frontend_root = resolve_frontend_root()
    if frontend_root is None:
        return

    frontend_root = frontend_root.resolve()

    @app.get("/pages/{page_path:path}", include_in_schema=False)
    def legacy_frontend_page(page_path: str) -> FileResponse:
        normalized = page_path.strip("/")
        if not normalized.endswith(".html"):
            raise HTTPException(status_code=404)

        html_target = _resolve_frontend_document(frontend_root, normalized[:-5])
        if html_target is None:
            raise HTTPException(status_code=404)

        return _frontend_response(frontend_root, html_target)

    @app.get("/{frontend_path:path}", include_in_schema=False)
    def frontend_content(frontend_path: str):
        document = _resolve_frontend_document(frontend_root, frontend_path)
        if document is None:
            raise HTTPException(status_code=404)
        return _frontend_response(frontend_root, document)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
        if settings.environment.lower() != "production"
        else None,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith("/api/v1/internal") or request.url.path == "/api/v1/public/inquiries":
            response.headers["Cache-Control"] = "no-store"
        return response

    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/health/live", tags=["health"])
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def health_ready() -> dict[str, str]:
        try:
            check_database_ready()
        except Exception as exc:
            raise AppError(
                code="database_not_ready",
                message="Database connectivity is not available.",
                status_code=503,
            ) from exc
        return {"status": "ready"}

    _register_frontend(app)

    return app
