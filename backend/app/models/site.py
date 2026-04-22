from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ContactProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contact_profiles"
    __table_args__ = (UniqueConstraint("profile_key", name="uq_contact_profiles_profile_key"),)

    profile_key: Mapped[str] = mapped_column(String(40), nullable=False, default="primary")
    sales_email: Mapped[str] = mapped_column(String(255), nullable=False)
    hr_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    primary_phone: Mapped[str] = mapped_column(String(40), nullable=False)
    headquarters_name: Mapped[str] = mapped_column(String(160), nullable=False)
    headquarters_address: Mapped[str] = mapped_column(Text, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    office_regions: Mapped[list["OfficePresenceRegion"]] = relationship(
        back_populates="contact_profile",
        cascade="all, delete-orphan",
        order_by="OfficePresenceRegion.display_order",
    )
    interest_options: Mapped[list["ContactInterestOption"]] = relationship(
        back_populates="contact_profile",
        cascade="all, delete-orphan",
        order_by="ContactInterestOption.display_order",
    )


class OfficePresenceRegion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "office_presence_regions"
    __table_args__ = (
        UniqueConstraint("contact_profile_id", "slug", name="uq_office_presence_regions_profile_slug"),
    )

    contact_profile_id: Mapped[str] = mapped_column(
        ForeignKey("contact_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    contact_profile: Mapped[ContactProfile] = relationship(back_populates="office_regions")


class ContactInterestOption(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contact_interest_options"
    __table_args__ = (
        UniqueConstraint("contact_profile_id", "slug", name="uq_contact_interest_options_profile_slug"),
        UniqueConstraint("contact_profile_id", "display_order", name="uq_contact_interest_options_profile_display_order"),
    )

    contact_profile_id: Mapped[str] = mapped_column(
        ForeignKey("contact_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    route_target: Mapped[str] = mapped_column(String(80), nullable=False, default="sales")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    contact_profile: Mapped[ContactProfile] = relationship(back_populates="interest_options")
    inquiries: Mapped[list["Inquiry"]] = relationship(back_populates="interest_option")