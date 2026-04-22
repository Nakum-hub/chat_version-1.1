from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import PublicationStatus, TaxonomyGroup


class SolutionTrack(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "solution_tracks"
    __table_args__ = (UniqueConstraint("slug", name="uq_solution_tracks_slug"),)

    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    short_summary: Mapped[str] = mapped_column(String(255), nullable=False)
    hero_title: Mapped[str] = mapped_column(String(255), nullable=False)
    hero_body: Mapped[str] = mapped_column(Text, nullable=False)
    cta_label: Mapped[str] = mapped_column(String(120), nullable=False)
    cta_target: Mapped[str] = mapped_column(String(255), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, native_enum=False),
        nullable=False,
        default=PublicationStatus.published,
    )
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    offerings: Mapped[list["ServiceOffering"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
        order_by="ServiceOffering.display_order",
    )
    endpoint_rows: Mapped[list["EndpointCatalogRow"]] = relationship(
        back_populates="track",
        cascade="all, delete-orphan",
        order_by="EndpointCatalogRow.display_order",
    )


class ServiceOffering(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "service_offerings"
    __table_args__ = (
        UniqueConstraint("track_id", "slug", name="uq_service_offerings_track_slug"),
        UniqueConstraint("track_id", "display_order", name="uq_service_offerings_track_display_order"),
    )

    track_id: Mapped[str] = mapped_column(ForeignKey("solution_tracks.id", ondelete="CASCADE"), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    kicker: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    publication_status: Mapped[PublicationStatus] = mapped_column(
        Enum(PublicationStatus, native_enum=False),
        nullable=False,
        default=PublicationStatus.published,
    )

    track: Mapped[SolutionTrack] = relationship(back_populates="offerings")
    taxonomy_links: Mapped[list["OfferingTaxonomyLink"]] = relationship(
        back_populates="offering",
        cascade="all, delete-orphan",
    )


class EndpointCatalogRow(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "endpoint_catalog_rows"
    __table_args__ = (
        UniqueConstraint("track_id", "display_order", name="uq_endpoint_catalog_rows_track_display_order"),
    )

    track_id: Mapped[str] = mapped_column(ForeignKey("solution_tracks.id", ondelete="CASCADE"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    solution_name: Mapped[str] = mapped_column(String(200), nullable=False)
    service_name: Mapped[str] = mapped_column(String(200), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)

    track: Mapped[SolutionTrack] = relationship(back_populates="endpoint_rows")


class TaxonomyTerm(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "taxonomy_terms"
    __table_args__ = (UniqueConstraint("group", "slug", name="uq_taxonomy_terms_group_slug"),)

    group: Mapped[TaxonomyGroup] = mapped_column(Enum(TaxonomyGroup, native_enum=False), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    offering_links: Mapped[list["OfferingTaxonomyLink"]] = relationship(
        back_populates="term",
        cascade="all, delete-orphan",
    )


class OfferingTaxonomyLink(TimestampMixin, Base):
    __tablename__ = "offering_taxonomy_links"
    __table_args__ = (
        UniqueConstraint("offering_id", "term_id", name="uq_offering_taxonomy_links_offering_term"),
    )

    offering_id: Mapped[str] = mapped_column(
        ForeignKey("service_offerings.id", ondelete="CASCADE"),
        primary_key=True,
    )
    term_id: Mapped[str] = mapped_column(
        ForeignKey("taxonomy_terms.id", ondelete="CASCADE"),
        primary_key=True,
    )

    offering: Mapped[ServiceOffering] = relationship(back_populates="taxonomy_links")
    term: Mapped[TaxonomyTerm] = relationship(back_populates="offering_links")