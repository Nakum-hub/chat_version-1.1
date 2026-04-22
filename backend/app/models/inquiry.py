from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import InquiryStatus


class Inquiry(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inquiries"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_page: Mapped[str | None] = mapped_column(String(160), nullable=True)
    solution_track_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cta_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    referrer_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(120), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[InquiryStatus] = mapped_column(
        Enum(InquiryStatus, native_enum=False),
        nullable=False,
        default=InquiryStatus.new,
    )
    first_response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    message_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    interest_option_id: Mapped[str] = mapped_column(
        ForeignKey("contact_interest_options.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_to_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("staff_users.id", ondelete="SET NULL"),
        nullable=True,
    )

    interest_option: Mapped["ContactInterestOption"] = relationship(back_populates="inquiries")
    assigned_to: Mapped["StaffUser | None"] = relationship(back_populates="assigned_inquiries")
    audit_events: Mapped[list["InquiryAuditEvent"]] = relationship(
        back_populates="inquiry",
        cascade="all, delete-orphan",
        order_by="InquiryAuditEvent.created_at",
    )

    __table_args__ = (
        Index("ix_inquiries_status_created_at", "status", "created_at"),
        Index("ix_inquiries_interest_option_id_created_at", "interest_option_id", "created_at"),
        Index("ix_inquiries_assigned_to_user_id_created_at", "assigned_to_user_id", "created_at"),
        Index("ix_inquiries_email_created_at", "email", "created_at"),
        Index("ix_inquiries_message_hash_created_at", "message_hash", "created_at"),
    )


class InquiryAuditEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inquiry_audit_events"

    inquiry_id: Mapped[str] = mapped_column(
        ForeignKey("inquiries.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("staff_users.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    inquiry: Mapped[Inquiry] = relationship(back_populates="audit_events")
    actor: Mapped["StaffUser | None"] = relationship(back_populates="inquiry_audits")