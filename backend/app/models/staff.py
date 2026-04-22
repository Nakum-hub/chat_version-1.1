from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import StaffRole


class StaffUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "staff_users"

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assigned_inquiries: Mapped[list["Inquiry"]] = relationship(back_populates="assigned_to")
    inquiry_audits: Mapped[list["InquiryAuditEvent"]] = relationship(back_populates="actor")