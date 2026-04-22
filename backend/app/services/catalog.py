from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.models.catalog import OfferingTaxonomyLink, ServiceOffering, SolutionTrack
from app.models.enums import PublicationStatus


def list_public_solution_tracks(session: Session) -> list[SolutionTrack]:
    statement = (
        select(SolutionTrack)
        .where(SolutionTrack.publication_status == PublicationStatus.published)
        .order_by(SolutionTrack.display_order.asc(), SolutionTrack.title.asc())
    )
    return list(session.scalars(statement).all())


def get_public_solution_track(session: Session, slug: str) -> SolutionTrack:
    statement = (
        select(SolutionTrack)
        .where(
            SolutionTrack.slug == slug,
            SolutionTrack.publication_status == PublicationStatus.published,
        )
        .options(
            selectinload(SolutionTrack.offerings)
            .selectinload(ServiceOffering.taxonomy_links)
            .selectinload(OfferingTaxonomyLink.term),
            selectinload(SolutionTrack.endpoint_rows),
        )
    )
    track = session.scalar(statement)
    if track is None:
        raise AppError(
            code="solution_track_not_found",
            message="The requested solution track was not found.",
            status_code=404,
        )
    for offering in track.offerings:
        offering.taxonomy_links.sort(key=lambda link: (link.term.group.value, link.term.label.lower()))
    return track