from __future__ import annotations

import argparse
from os import getenv
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    ContactInterestOption,
    ContactProfile,
    EndpointCatalogRow,
    OfferingTaxonomyLink,
    OfficePresenceRegion,
    ServiceOffering,
    SolutionTrack,
    StaffUser,
    TaxonomyTerm,
)
from app.models.enums import PublicationStatus, StaffRole, TaxonomyGroup


def _upsert(
    session: Session, model: Any, lookup: dict[str, Any], values: dict[str, Any]
) -> tuple[Any, bool]:
    instance = session.scalar(select(model).filter_by(**lookup))
    created = instance is None

    if instance is None:
        instance = model(**lookup, **values)
        session.add(instance)
    else:
        for field, value in values.items():
            if getattr(instance, field) != value:
                setattr(instance, field, value)

    session.flush()
    return instance, created


def _seed_contact_profile(session: Session) -> tuple[ContactProfile, bool]:
    return _upsert(
        session,
        ContactProfile,
        {"profile_key": "primary"},
        {
            "sales_email": "sales@cyberfyx.net",
            "hr_email": "hr@cyberfyx.net",
            "primary_phone": "+91 99726 27214",
            "headquarters_name": "Cyberfyx",
            "headquarters_address": "Fourth Floor, Janardhana Towers, 133/2, Residency Rd, Shanthala Nagar, Ashok Nagar, Bengaluru, Karnataka 560025",
            "map_url": "https://maps.google.com/?q=Cyberfyx,+Fourth+Floor,+Janardhana+Towers,+133/2,+Residency+Rd,+Shanthala+Nagar,+Ashok+Nagar,+Bengaluru,+Karnataka+560025",
            "published": True,
        },
    )


def _seed_regions(session: Session, profile: ContactProfile) -> int:
    region_specs = [
        {"slug": "india", "label": "India", "display_order": 1},
        {"slug": "singapore", "label": "Singapore", "display_order": 2},
        {"slug": "philippines", "label": "Philippines", "display_order": 3},
        {"slug": "dubai", "label": "Dubai", "display_order": 4},
    ]
    created = 0
    for spec in region_specs:
        _, was_created = _upsert(
            session,
            OfficePresenceRegion,
            {"contact_profile_id": profile.id, "slug": spec["slug"]},
            {"label": spec["label"], "display_order": spec["display_order"]},
        )
        created += int(was_created)
    return created


def _seed_interest_options(session: Session, profile: ContactProfile) -> int:
    interest_specs = [
        {
            "slug": "iso-consultation-services",
            "label": "ISO consultation services",
            "route_target": "sales",
            "display_order": 1,
        },
        {
            "slug": "cybersecurity-services",
            "label": "Cybersecurity services",
            "route_target": "sales",
            "display_order": 2,
        },
        {
            "slug": "it-security-and-continuity",
            "label": "IT security and continuity",
            "route_target": "sales",
            "display_order": 3,
        },
        {
            "slug": "endpoint-management-services",
            "label": "Endpoint management services",
            "route_target": "sales",
            "display_order": 4,
        },
        {
            "slug": "patch-management-software",
            "label": "Patch management software",
            "route_target": "sales",
            "display_order": 5,
        },
        {
            "slug": "power-management-software",
            "label": "Power management software",
            "route_target": "sales",
            "display_order": 6,
        },
        {
            "slug": "core-industry-services",
            "label": "Core industry services",
            "route_target": "sales",
            "display_order": 7,
        },
        {
            "slug": "training",
            "label": "Training",
            "route_target": "sales",
            "display_order": 8,
        },
        {
            "slug": "general-inquiry",
            "label": "General inquiry",
            "route_target": "sales",
            "display_order": 9,
        },
    ]
    created = 0
    for spec in interest_specs:
        _, was_created = _upsert(
            session,
            ContactInterestOption,
            {"contact_profile_id": profile.id, "slug": spec["slug"]},
            {
                "label": spec["label"],
                "route_target": spec["route_target"],
                "is_active": True,
                "display_order": spec["display_order"],
            },
        )
        created += int(was_created)
    return created


def _seed_solution_tracks(session: Session) -> tuple[dict[str, SolutionTrack], int]:
    track_specs = [
        {
            "slug": "cybersecurity",
            "title": "Cybersecurity",
            "short_summary": "Testing, privacy, strategic leadership, and attack-path reduction.",
            "hero_title": "Security programs for teams under real audit and threat pressure.",
            "hero_body": "Practical security delivery for regulated organizations that need testing, governance, privacy, and leadership support that translates into working controls.",
            "cta_label": "View cybersecurity",
            "cta_target": "services-cybersecurity.html",
            "display_order": 1,
            "meta_title": "Cybersecurity Services | Cyberfyx",
            "meta_description": "VAPT, privacy, red team support, SOC readiness, and leadership overlays.",
        },
        {
            "slug": "it-security",
            "title": "IT security",
            "short_summary": "Framework implementation, continuity, and audit-ready controls.",
            "hero_title": "Controls that turn standards into operating discipline.",
            "hero_body": "Implementation support for ISO, cloud, continuity, and service-management programs that need to hold up under internal review and customer assurance.",
            "cta_label": "View IT security",
            "cta_target": "services-it-security.html",
            "display_order": 2,
            "meta_title": "IT Security Services | Cyberfyx",
            "meta_description": "ISO 27001, ISO 27701, ISO 22301, cloud governance, and continuity delivery.",
        },
        {
            "slug": "endpoint-operations",
            "title": "Endpoint operations",
            "short_summary": "Endpoint management, monitoring, data-center services, and automation.",
            "hero_title": "Operational control for distributed estates.",
            "hero_body": "Visibility, lifecycle discipline, and automation for teams balancing endpoints, monitoring, cloud operations, and resilience.",
            "cta_label": "View endpoint operations",
            "cta_target": "services-endpoint-management.html",
            "display_order": 3,
            "meta_title": "Endpoint Operations | Cyberfyx",
            "meta_description": "UEM, SIEM, monitoring, SmartDC, backup, and endpoint control programs.",
        },
        {
            "slug": "core-industry-services",
            "title": "Core industry services",
            "short_summary": "Management systems, safety, quality, and supplier-facing audit programs.",
            "hero_title": "Industrial assurance shaped around compliance and continuity.",
            "hero_body": "Quality, safety, supplier assurance, and audit programs for operational environments where evidence and repeatability matter.",
            "cta_label": "View core industry",
            "cta_target": "services-core-industry.html",
            "display_order": 4,
            "meta_title": "Core Industry Services | Cyberfyx",
            "meta_description": "Audit support, management systems, safety, quality, and industrial assurance.",
        },
        {
            "slug": "training",
            "title": "Training",
            "short_summary": "Internal capability building for security, privacy, governance, and recovery teams.",
            "hero_title": "Training that keeps programs usable after launch.",
            "hero_body": "Audience-specific awareness and enablement programs that help teams sustain controls, recover faster, and keep governance practical.",
            "cta_label": "View training",
            "cta_target": "services-training.html",
            "display_order": 5,
            "meta_title": "Cybersecurity Training | Cyberfyx",
            "meta_description": "Security, privacy, compliance, continuity, and governance training programs.",
        },
    ]

    tracks: dict[str, SolutionTrack] = {}
    created = 0
    for spec in track_specs:
        track, was_created = _upsert(
            session,
            SolutionTrack,
            {"slug": spec["slug"]},
            {
                "title": spec["title"],
                "short_summary": spec["short_summary"],
                "hero_title": spec["hero_title"],
                "hero_body": spec["hero_body"],
                "cta_label": spec["cta_label"],
                "cta_target": spec["cta_target"],
                "display_order": spec["display_order"],
                "publication_status": PublicationStatus.published,
                "meta_title": spec["meta_title"],
                "meta_description": spec["meta_description"],
            },
        )
        tracks[track.slug] = track
        created += int(was_created)

    return tracks, created


def _seed_taxonomy_terms(
    session: Session,
) -> tuple[dict[tuple[str, str], TaxonomyTerm], int]:
    term_specs = [
        (TaxonomyGroup.framework_or_standard, "iso-27001", "ISO 27001"),
        (TaxonomyGroup.framework_or_standard, "iso-27701", "ISO 27701"),
        (TaxonomyGroup.framework_or_standard, "iso-22301", "ISO 22301"),
        (TaxonomyGroup.framework_or_standard, "iso-20000-1", "ISO 20000-1"),
        (TaxonomyGroup.framework_or_standard, "iso-9001", "ISO 9001"),
        (TaxonomyGroup.framework_or_standard, "iso-14001", "ISO 14001"),
        (TaxonomyGroup.framework_or_standard, "iso-45001", "ISO 45001"),
        (TaxonomyGroup.framework_or_standard, "soc-2", "SOC 2"),
        (TaxonomyGroup.framework_or_standard, "itil", "ITIL"),
        (TaxonomyGroup.framework_or_standard, "nist", "NIST"),
        (TaxonomyGroup.framework_or_standard, "as9100", "AS9100"),
        (TaxonomyGroup.framework_or_standard, "iatf-16949", "IATF 16949"),
        (TaxonomyGroup.framework_or_standard, "sedex", "SEDEX"),
        (TaxonomyGroup.framework_or_standard, "fsc", "FSC"),
        (TaxonomyGroup.regulation, "pci-dss", "PCI DSS"),
        (TaxonomyGroup.regulation, "gdpr", "GDPR"),
        (TaxonomyGroup.regulation, "hipaa", "HIPAA"),
        (TaxonomyGroup.regulation, "tisax", "TISAX"),
        (TaxonomyGroup.regulation, "csa-star", "CSA STAR"),
        (TaxonomyGroup.capability, "vapt", "VAPT"),
        (TaxonomyGroup.capability, "red-team", "Red team"),
        (TaxonomyGroup.capability, "vciso", "vCISO"),
        (TaxonomyGroup.capability, "dpo", "DPO"),
        (TaxonomyGroup.capability, "uem", "Unified endpoint management"),
        (TaxonomyGroup.capability, "siem", "SIEM"),
        (TaxonomyGroup.capability, "smartdc", "SmartDC"),
        (TaxonomyGroup.capability, "backup", "Backup"),
        (TaxonomyGroup.capability, "cloud-governance", "Cloud governance"),
        (TaxonomyGroup.capability, "continuity", "Continuity"),
        (TaxonomyGroup.capability, "awareness", "Awareness"),
        (TaxonomyGroup.capability, "recovery", "Recovery"),
        (TaxonomyGroup.audience, "regulated-enterprises", "Regulated enterprises"),
        (TaxonomyGroup.audience, "industrial-operations", "Industrial operations"),
        (TaxonomyGroup.audience, "public-sector", "Public sector"),
        (TaxonomyGroup.audience, "enterprise-it", "Enterprise IT"),
        (TaxonomyGroup.product_vendor_line, "ipm-plus", "IPM+"),
        (TaxonomyGroup.product_vendor_line, "smartdc", "SmartDC"),
    ]

    terms: dict[tuple[str, str], TaxonomyTerm] = {}
    created = 0
    for group, slug, label in term_specs:
        term, was_created = _upsert(
            session,
            TaxonomyTerm,
            {"group": group, "slug": slug},
            {"label": label, "description": None},
        )
        terms[(group.value, slug)] = term
        created += int(was_created)

    return terms, created


def _seed_offerings(
    session: Session, tracks: dict[str, SolutionTrack]
) -> tuple[dict[str, ServiceOffering], int]:
    offering_specs = [
        {
            "track_slug": "cybersecurity",
            "slug": "vapt-and-attack-path-reduction",
            "title": "VAPT and attack-path reduction",
            "kicker": "Cybersecurity",
            "description": "Testing and remediation guidance for teams that need practical attack-surface reduction, not just findings.",
            "display_order": 1,
            "terms": ["vapt", "red-team", "pci-dss"],
        },
        {
            "track_slug": "cybersecurity",
            "slug": "privacy-and-governance-leadership",
            "title": "Privacy and governance leadership",
            "kicker": "Cybersecurity",
            "description": "vCISO and DPO-style support for privacy, policy alignment, and decision clarity.",
            "display_order": 2,
            "terms": ["vciso", "dpo", "gdpr", "hipaa"],
        },
        {
            "track_slug": "it-security",
            "slug": "framework-implementation-and-controls",
            "title": "Framework implementation and controls",
            "kicker": "IT security",
            "description": "Implementation support for security and service-management frameworks that need to become daily operating practice.",
            "display_order": 1,
            "terms": ["iso-27001", "iso-27701", "iso-20000-1", "soc-2"],
        },
        {
            "track_slug": "it-security",
            "slug": "continuity-and-cloud-governance",
            "title": "Continuity and cloud governance",
            "kicker": "IT security",
            "description": "Control design for continuity, cloud risk, and assurance programs that need to survive change.",
            "display_order": 2,
            "terms": ["iso-22301", "cloud-governance", "csa-star", "nist"],
        },
        {
            "track_slug": "endpoint-operations",
            "slug": "endpoint-management-and-uem",
            "title": "Endpoint management and UEM",
            "kicker": "Endpoint operations",
            "description": "Unified endpoint management and operational discipline for distributed device estates.",
            "display_order": 1,
            "terms": ["uem", "ipm-plus", "enterprise-it"],
        },
        {
            "track_slug": "endpoint-operations",
            "slug": "monitoring-backup-and-smartdc",
            "title": "Monitoring, backup, and SmartDC",
            "kicker": "Endpoint operations",
            "description": "Visibility and resilience programs that connect monitoring, backup, and data-center operations.",
            "display_order": 2,
            "terms": ["siem", "smartdc", "backup"],
        },
        {
            "track_slug": "core-industry-services",
            "slug": "management-systems-and-audit-support",
            "title": "Management systems and audit support",
            "kicker": "Core industry",
            "description": "Audit readiness and management-system support for industrial and supplier-facing environments.",
            "display_order": 1,
            "terms": ["iso-9001", "iso-14001", "iso-45001", "public-sector"],
        },
        {
            "track_slug": "core-industry-services",
            "slug": "supplier-assurance-and-safety-programs",
            "title": "Supplier assurance and safety programs",
            "kicker": "Core industry",
            "description": "Assurance, documentation, and safety programs that support regulated manufacturing and logistics work.",
            "display_order": 2,
            "terms": ["as9100", "iatf-16949", "sedex", "fsc"],
        },
        {
            "track_slug": "training",
            "slug": "security-and-privacy-awareness",
            "title": "Security and privacy awareness",
            "kicker": "Training",
            "description": "Security, privacy, and governance awareness delivered for different stakeholder groups.",
            "display_order": 1,
            "terms": ["awareness", "gdpr", "hipaa", "soc-2"],
        },
        {
            "track_slug": "training",
            "slug": "continuity-and-recovery-enablement",
            "title": "Continuity and recovery enablement",
            "kicker": "Training",
            "description": "Programs that help teams understand recovery, continuity, and response expectations before an incident forces the lesson.",
            "display_order": 2,
            "terms": ["continuity", "recovery", "nist", "itil"],
        },
    ]

    offerings: dict[str, ServiceOffering] = {}
    created = 0
    for spec in offering_specs:
        track = tracks[spec["track_slug"]]
        offering, was_created = _upsert(
            session,
            ServiceOffering,
            {"track_id": track.id, "slug": spec["slug"]},
            {
                "title": spec["title"],
                "kicker": spec["kicker"],
                "description": spec["description"],
                "display_order": spec["display_order"],
                "publication_status": PublicationStatus.published,
            },
        )
        offerings[offering.slug] = offering
        created += int(was_created)

    return offerings, created


def _seed_endpoint_rows(session: Session, track: SolutionTrack) -> int:
    endpoint_specs = [
        {
            "display_order": 1,
            "product_name": "Unified endpoint management",
            "solution_name": "UEM and device lifecycle control",
            "service_name": "Endpoint governance",
        },
        {
            "display_order": 2,
            "product_name": "Security monitoring",
            "solution_name": "SIEM and alert triage",
            "service_name": "Detection support",
        },
        {
            "display_order": 3,
            "product_name": "Data-center operations",
            "solution_name": "SmartDC visibility and control",
            "service_name": "Operational assurance",
        },
        {
            "display_order": 4,
            "product_name": "Backup and resilience",
            "solution_name": "Cloud and backup coordination",
            "service_name": "Recovery readiness",
        },
    ]
    created = 0
    for spec in endpoint_specs:
        _, was_created = _upsert(
            session,
            EndpointCatalogRow,
            {"track_id": track.id, "display_order": spec["display_order"]},
            {
                "product_name": spec["product_name"],
                "solution_name": spec["solution_name"],
                "service_name": spec["service_name"],
            },
        )
        created += int(was_created)
    return created


def _seed_offering_taxonomy_links(
    session: Session,
    offerings: dict[str, ServiceOffering],
    terms: dict[tuple[str, str], TaxonomyTerm],
) -> int:
    link_map = {
        "vapt-and-attack-path-reduction": ["vapt", "red-team", "pci-dss"],
        "privacy-and-governance-leadership": ["vciso", "dpo", "gdpr", "hipaa"],
        "framework-implementation-and-controls": [
            "iso-27001",
            "iso-27701",
            "iso-20000-1",
            "soc-2",
        ],
        "continuity-and-cloud-governance": [
            "iso-22301",
            "cloud-governance",
            "csa-star",
            "nist",
        ],
        "endpoint-management-and-uem": ["uem", "ipm-plus", "enterprise-it"],
        "monitoring-backup-and-smartdc": ["siem", "smartdc", "backup"],
        "management-systems-and-audit-support": [
            "iso-9001",
            "iso-14001",
            "iso-45001",
            "public-sector",
        ],
        "supplier-assurance-and-safety-programs": [
            "regulated-enterprises",
            "industrial-operations",
        ],
        "security-and-privacy-awareness": ["awareness", "gdpr", "hipaa", "soc-2"],
        "continuity-and-recovery-enablement": [
            "continuity",
            "recovery",
            "nist",
            "itil",
        ],
    }

    created = 0
    for offering_slug, term_slugs in link_map.items():
        offering = offerings[offering_slug]
        for term_slug in term_slugs:
            term = (
                terms.get((TaxonomyGroup.framework_or_standard.value, term_slug))
                or terms.get((TaxonomyGroup.regulation.value, term_slug))
                or terms.get((TaxonomyGroup.capability.value, term_slug))
                or terms.get((TaxonomyGroup.audience.value, term_slug))
                or terms.get((TaxonomyGroup.product_vendor_line.value, term_slug))
            )
            if term is None:
                continue
            _, was_created = _upsert(
                session,
                OfferingTaxonomyLink,
                {"offering_id": offering.id, "term_id": term.id},
                {},
            )
            created += int(was_created)
    return created


def ensure_bootstrap_staff_user(
    session: Session,
    *,
    email: str | None = None,
    password: str | None = None,
    display_name: str = "Cyberfyx Admin",
    role: StaffRole = StaffRole.super_admin,
    is_active: bool = True,
    reset_password: bool = False,
) -> StaffUser | None:
    resolved_email = email or getenv("CYBERFYX_BOOTSTRAP_STAFF_EMAIL")
    resolved_password = password or getenv("CYBERFYX_BOOTSTRAP_STAFF_PASSWORD")

    if not resolved_email or not resolved_password:
        return None

    resolved_email = resolved_email.strip().lower()

    user = session.scalar(select(StaffUser).filter_by(email=resolved_email))
    if user is None:
        user = StaffUser(
            email=resolved_email,
            display_name=display_name,
            password_hash=hash_password(resolved_password),
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.flush()
        return user

    user.display_name = display_name
    user.role = role
    user.is_active = is_active
    if reset_password:
        user.password_hash = hash_password(resolved_password)
    session.flush()
    return user


def seed_database(session: Session) -> dict[str, int]:
    def _seed() -> dict[str, int]:
        created = 0

        profile, was_created = _seed_contact_profile(session)
        created += int(was_created)
        created += _seed_regions(session, profile)
        created += _seed_interest_options(session, profile)

        tracks, tracks_created = _seed_solution_tracks(session)
        created += tracks_created

        terms, terms_created = _seed_taxonomy_terms(session)
        created += terms_created

        offerings, offerings_created = _seed_offerings(session, tracks)
        created += offerings_created

        created += _seed_offering_taxonomy_links(session, offerings, terms)
        created += _seed_endpoint_rows(session, tracks["endpoint-operations"])

        bootstrap = ensure_bootstrap_staff_user(session)
        created += int(bootstrap is not None)

        return {"created": created}

    if session.in_transaction():
        return _seed()

    with session.begin():
        return _seed()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the Cyberfyx backend database.")
    parser.add_argument("--bootstrap-admin-email", dest="bootstrap_admin_email")
    parser.add_argument("--bootstrap-admin-password", dest="bootstrap_admin_password")
    parser.add_argument("--reset-bootstrap-password", action="store_true")
    args = parser.parse_args()

    with SessionLocal() as session:
        result = seed_database(session)
        if args.bootstrap_admin_email and args.bootstrap_admin_password:
            with session.begin():
                ensure_bootstrap_staff_user(
                    session,
                    email=args.bootstrap_admin_email,
                    password=args.bootstrap_admin_password,
                    reset_password=args.reset_bootstrap_password,
                )
        print(f"Seed completed. Created {result['created']} new record(s).")


if __name__ == "__main__":
    main()
