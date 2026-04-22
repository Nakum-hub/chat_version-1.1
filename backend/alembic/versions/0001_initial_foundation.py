"""initial cyberfyx backend foundation

Revision ID: 0001_initial_foundation
Revises: None
Create Date: 2026-03-20 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contact_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("profile_key", sa.String(length=40), nullable=False),
        sa.Column("sales_email", sa.String(length=255), nullable=False),
        sa.Column("hr_email", sa.String(length=255), nullable=True),
        sa.Column("primary_phone", sa.String(length=40), nullable=False),
        sa.Column("headquarters_name", sa.String(length=160), nullable=False),
        sa.Column("headquarters_address", sa.Text(), nullable=False),
        sa.Column("map_url", sa.String(length=500), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("profile_key", name=op.f("uq_contact_profiles_profile_key")),
    )

    op.create_table(
        "solution_tracks",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("short_summary", sa.String(length=255), nullable=False),
        sa.Column("hero_title", sa.String(length=255), nullable=False),
        sa.Column("hero_body", sa.Text(), nullable=False),
        sa.Column("cta_label", sa.String(length=120), nullable=False),
        sa.Column("cta_target", sa.String(length=255), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("publication_status", sa.Enum("draft", "published", "archived", name="publication_status", native_enum=False, create_constraint=True), nullable=False, server_default=sa.text("'published'")),
        sa.Column("meta_title", sa.String(length=255), nullable=True),
        sa.Column("meta_description", sa.String(length=255), nullable=True),
        sa.UniqueConstraint("slug", name=op.f("uq_solution_tracks_slug")),
    )

    op.create_table(
        "staff_users",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("super_admin", "sales_admin", "content_admin", "recruiter", "viewer", name="staff_role", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("email", name=op.f("uq_staff_users_email")),
    )

    op.create_table(
        "taxonomy_terms",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("group", sa.Enum("framework_or_standard", "regulation", "capability", "audience", "product_vendor_line", name="taxonomy_group", native_enum=False, create_constraint=True), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("group", "slug", name=op.f("uq_taxonomy_terms_group_slug")),
    )

    op.create_table(
        "office_presence_regions",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("contact_profile_id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["contact_profile_id"], ["contact_profiles.id"], ondelete="CASCADE", name=op.f("fk_office_presence_regions_contact_profile_id_contact_profiles")),
        sa.UniqueConstraint("contact_profile_id", "slug", name=op.f("uq_office_presence_regions_profile_slug")),
    )

    op.create_table(
        "contact_interest_options",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("contact_profile_id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("route_target", sa.String(length=80), nullable=False, server_default=sa.text("'sales'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["contact_profile_id"], ["contact_profiles.id"], ondelete="CASCADE", name=op.f("fk_contact_interest_options_contact_profile_id_contact_profiles")),
        sa.UniqueConstraint("contact_profile_id", "slug", name=op.f("uq_contact_interest_options_profile_slug")),
        sa.UniqueConstraint("contact_profile_id", "display_order", name=op.f("uq_contact_interest_options_profile_display_order")),
    )

    op.create_table(
        "service_offerings",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("kicker", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("publication_status", sa.Enum("draft", "published", "archived", name="publication_status", native_enum=False, create_constraint=True), nullable=False, server_default=sa.text("'published'")),
        sa.ForeignKeyConstraint(["track_id"], ["solution_tracks.id"], ondelete="CASCADE", name=op.f("fk_service_offerings_track_id_solution_tracks")),
        sa.UniqueConstraint("track_id", "slug", name=op.f("uq_service_offerings_track_slug")),
        sa.UniqueConstraint("track_id", "display_order", name=op.f("uq_service_offerings_track_display_order")),
    )

    op.create_table(
        "endpoint_catalog_rows",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("track_id", sa.String(length=36), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("solution_name", sa.String(length=200), nullable=False),
        sa.Column("service_name", sa.String(length=200), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["track_id"], ["solution_tracks.id"], ondelete="CASCADE", name=op.f("fk_endpoint_catalog_rows_track_id_solution_tracks")),
        sa.UniqueConstraint("track_id", "display_order", name=op.f("uq_endpoint_catalog_rows_track_display_order")),
    )

    op.create_table(
        "offering_taxonomy_links",
        sa.Column("offering_id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("term_id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["offering_id"], ["service_offerings.id"], ondelete="CASCADE", name=op.f("fk_offering_taxonomy_links_offering_id_service_offerings")),
        sa.ForeignKeyConstraint(["term_id"], ["taxonomy_terms.id"], ondelete="CASCADE", name=op.f("fk_offering_taxonomy_links_term_id_taxonomy_terms")),
        sa.UniqueConstraint("offering_id", "term_id", name=op.f("uq_offering_taxonomy_links_offering_term")),
    )

    op.create_table(
        "inquiries",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=160), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("source_page", sa.String(length=160), nullable=True),
        sa.Column("solution_track_slug", sa.String(length=120), nullable=True),
        sa.Column("cta_label", sa.String(length=160), nullable=True),
        sa.Column("referrer_url", sa.String(length=500), nullable=True),
        sa.Column("utm_source", sa.String(length=120), nullable=True),
        sa.Column("utm_medium", sa.String(length=120), nullable=True),
        sa.Column("utm_campaign", sa.String(length=120), nullable=True),
        sa.Column("utm_content", sa.String(length=120), nullable=True),
        sa.Column("utm_term", sa.String(length=120), nullable=True),
        sa.Column("status", sa.Enum("new", "triaged", "responded", "closed", "spam", name="inquiry_status", native_enum=False, create_constraint=True), nullable=False, server_default=sa.text("'new'")),
        sa.Column("first_response_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("ip_hash", sa.String(length=128), nullable=True),
        sa.Column("message_hash", sa.String(length=128), nullable=True),
        sa.Column("interest_option_id", sa.String(length=36), nullable=False),
        sa.Column("assigned_to_user_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(["interest_option_id"], ["contact_interest_options.id"], ondelete="RESTRICT", name=op.f("fk_inquiries_interest_option_id_contact_interest_options")),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["staff_users.id"], ondelete="SET NULL", name=op.f("fk_inquiries_assigned_to_user_id_staff_users")),
    )
    op.create_index("ix_inquiries_status_created_at", "inquiries", ["status", "created_at"])
    op.create_index("ix_inquiries_interest_option_id_created_at", "inquiries", ["interest_option_id", "created_at"])
    op.create_index("ix_inquiries_assigned_to_user_id_created_at", "inquiries", ["assigned_to_user_id", "created_at"])
    op.create_index("ix_inquiries_email_created_at", "inquiries", ["email", "created_at"])
    op.create_index("ix_inquiries_message_hash_created_at", "inquiries", ["message_hash", "created_at"])

    op.create_table(
        "inquiry_audit_events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("inquiry_id", sa.String(length=36), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiries.id"], ondelete="CASCADE", name=op.f("fk_inquiry_audit_events_inquiry_id_inquiries")),
        sa.ForeignKeyConstraint(["actor_user_id"], ["staff_users.id"], ondelete="SET NULL", name=op.f("fk_inquiry_audit_events_actor_user_id_staff_users")),
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("topic", sa.String(length=120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.Enum("pending", "processing", "completed", "failed", name="outbox_status", native_enum=False, create_constraint=True), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_index("ix_outbox_events_status_available_at", "outbox_events", ["status", "available_at"])


def downgrade() -> None:
    op.drop_index("ix_outbox_events_status_available_at", table_name="outbox_events")
    op.drop_table("outbox_events")
    op.drop_table("inquiry_audit_events")
    op.drop_index("ix_inquiries_message_hash_created_at", table_name="inquiries")
    op.drop_index("ix_inquiries_email_created_at", table_name="inquiries")
    op.drop_index("ix_inquiries_assigned_to_user_id_created_at", table_name="inquiries")
    op.drop_index("ix_inquiries_interest_option_id_created_at", table_name="inquiries")
    op.drop_index("ix_inquiries_status_created_at", table_name="inquiries")
    op.drop_table("inquiries")
    op.drop_table("offering_taxonomy_links")
    op.drop_table("endpoint_catalog_rows")
    op.drop_table("service_offerings")
    op.drop_table("contact_interest_options")
    op.drop_table("office_presence_regions")
    op.drop_table("taxonomy_terms")
    op.drop_table("staff_users")
    op.drop_table("solution_tracks")
    op.drop_table("contact_profiles")