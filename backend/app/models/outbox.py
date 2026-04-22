from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import OutboxStatus


class OutboxEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "outbox_events"
    __table_args__ = (
        Index("ix_outbox_events_status_available_at", "status", "available_at"),
    )

    topic: Mapped[str] = mapped_column(String(120), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[OutboxStatus] = mapped_column(
        Enum(OutboxStatus, native_enum=False),
        nullable=False,
        default=OutboxStatus.pending,
    )
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)