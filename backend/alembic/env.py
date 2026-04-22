from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.models import (  # noqa: F401 - importing registers SQLAlchemy mappings
    ContactInterestOption,
    ContactProfile,
    EndpointCatalogRow,
    Inquiry,
    InquiryAuditEvent,
    OfficePresenceRegion,
    OfferingTaxonomyLink,
    OutboxEvent,
    ServiceOffering,
    SolutionTrack,
    StaffUser,
    TaxonomyTerm,
)
from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        render_as_batch=settings.database_url.startswith("sqlite"),
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool, future=True)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=settings.database_url.startswith("sqlite"),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()