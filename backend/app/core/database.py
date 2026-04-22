from collections.abc import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()


def _create_engine() -> Engine:
    connect_args: dict[str, object] = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        future=True,
        pool_pre_ping=True,
    )


engine = _create_engine()


if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database_ready() -> bool:
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    return True