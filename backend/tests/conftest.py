from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import pytest
from pytest import MonkeyPatch
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalog import SolutionTrack
from app.models.enums import InquiryStatus, StaffRole
from app.models.inquiry import Inquiry
from app.models.site import ContactInterestOption, ContactProfile
from app.models.staff import StaffUser


@dataclass(frozen=True)
class SeedData:
    contact_profile_id: str
    track_ids: dict[str, str]
    interest_ids: dict[str, str]
    staff_user_id: str
    reviewer_user_id: str
    inquiry_id: str


@pytest.fixture(scope="session", autouse=True)
def backend_env() -> Iterator[Path]:
    backend_root = Path(__file__).resolve().parents[1]
    db_path = backend_root / ".test-cyberfyx.db"

    patcher = MonkeyPatch()
    patcher.setenv("CYBERFYX_ENVIRONMENT", "test")
    patcher.setenv("CYBERFYX_DEBUG", "false")
    patcher.setenv("CYBERFYX_DATABASE_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
    patcher.setenv("CYBERFYX_CORS_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080")
    patcher.setenv("CYBERFYX_ENABLE_INTERNAL_API", "true")
    patcher.setenv("CYBERFYX_JWT_SECRET_KEY", "test-secret-key-for-cyberfyx-backend")
    patcher.setenv("CYBERFYX_JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    patcher.setenv("CYBERFYX_INQUIRY_RATE_LIMIT_WINDOW_MINUTES", "15")
    patcher.setenv("CYBERFYX_INQUIRY_RATE_LIMIT_COUNT", "5")
    patcher.setenv("CYBERFYX_INQUIRY_DUPLICATE_WINDOW_HOURS", "24")

    yield db_path

    patcher.undo()
    if db_path.exists():
        try:
            db_path.unlink()
        except OSError:
            pass


@pytest.fixture(scope="session")
def backend_modules(backend_env: Path) -> dict[str, Any]:
    config = importlib.import_module("app.core.config")
    config.get_settings.cache_clear()

    database = importlib.import_module("app.core.database")
    security = importlib.import_module("app.core.security")
    base = importlib.import_module("app.models.base")
    seed = importlib.import_module("app.db.seed")

    return {
        "config": config,
        "database": database,
        "security": security,
        "base": base,
        "seed": seed,
    }


@pytest.fixture()
def db_session(backend_modules: dict[str, Any]) -> Iterator[Session]:
    database = backend_modules["database"]
    base = backend_modules["base"]

    base.Base.metadata.drop_all(bind=database.engine)
    base.Base.metadata.create_all(bind=database.engine)

    session = database.SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        base.Base.metadata.drop_all(bind=database.engine)


def _resolve_get_db() -> list[Any]:
    candidates: list[Any] = []
    for module_name in ("app.core.database", "app.api.dependencies"):
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        get_db = getattr(module, "get_db", None)
        if get_db is not None:
            candidates.append(get_db)
    return candidates


@pytest.fixture()
def app_instance(db_session: Session, backend_modules: dict[str, Any]) -> Iterator[Any]:
    api_router = importlib.import_module("app.api.router")
    importlib.reload(api_router)

    app_main = importlib.import_module("app.main")
    app_main = importlib.reload(app_main)
    app = app_main.app

    def override() -> Session:
        return db_session

    for dependency in _resolve_get_db():
        app.dependency_overrides[dependency] = override

    yield app

    app.dependency_overrides.clear()


@pytest.fixture()
def client(app_instance: Any) -> Iterator[Any]:
    from fastapi.testclient import TestClient

    with TestClient(app_instance) as test_client:
        yield test_client


@pytest.fixture()
def seeded_db(db_session: Session, backend_modules: dict[str, Any]) -> SeedData:
    security = backend_modules["security"]
    seed = backend_modules["seed"]

    seed.seed_database(db_session)

    contact_profile = db_session.scalar(select(ContactProfile).where(ContactProfile.profile_key == "primary"))
    assert contact_profile is not None

    interests = list(
        db_session.scalars(
            select(ContactInterestOption)
            .where(ContactInterestOption.contact_profile_id == contact_profile.id)
            .order_by(ContactInterestOption.display_order.asc())
        ).all()
    )
    interest_by_slug = {interest.slug: interest for interest in interests}

    tracks = list(
        db_session.scalars(select(SolutionTrack).order_by(SolutionTrack.display_order.asc(), SolutionTrack.title.asc())).all()
    )

    staff_user = StaffUser(
        email="admin@cyberfyx.net",
        display_name="Cyberfyx Admin",
        password_hash=security.hash_password("ChangeMeLonger123!"),
        role=StaffRole.super_admin,
        is_active=True,
    )
    reviewer_user = StaffUser(
        email="reviewer@cyberfyx.net",
        display_name="Inquiry Reviewer",
        password_hash=security.hash_password("ChangeMeLonger123!"),
        role=StaffRole.sales_admin,
        is_active=True,
    )
    db_session.add_all([staff_user, reviewer_user])
    db_session.flush()

    inquiry = Inquiry(
        name="Jordan Lee",
        email="jordan.lee@example.com",
        company="Northwind Manufacturing",
        message="We need help with audit readiness and endpoint control.",
        source_page="/contact",
        solution_track_slug="endpoint-operations",
        cta_label="Request a consultation",
        referrer_url="https://cyberfyx.net/contact",
        utm_source="organic",
        utm_medium="web",
        utm_campaign="contact",
        utm_content="hero",
        utm_term="endpoint",
        status=InquiryStatus.new,
        user_agent="pytest",
        ip_hash="test-ip-hash",
        message_hash="test-message-hash",
        interest_option_id=interest_by_slug["endpoint-management-services"].id,
        assigned_to_user_id=None,
    )
    db_session.add(inquiry)
    db_session.commit()

    return SeedData(
        contact_profile_id=contact_profile.id,
        track_ids={track.slug: track.id for track in tracks},
        interest_ids={interest.slug: interest.id for interest in interests},
        staff_user_id=staff_user.id,
        reviewer_user_id=reviewer_user.id,
        inquiry_id=inquiry.id,
    )


@pytest.fixture()
def auth_token(client: Any, seeded_db: SeedData) -> str:
    response = client.post(
        "/api/v1/internal/auth/token",
        json={"email": "admin@cyberfyx.net", "password": "ChangeMeLonger123!"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    return payload["access_token"]
