from fastapi import APIRouter

from app.api.dependencies import DBSession
from app.models.catalog import ServiceOffering, SolutionTrack
from app.models.enums import PublicationStatus
from app.schemas.catalog import (
    EndpointCatalogRowRead,
    ServiceOfferingRead,
    SolutionTrackDetail,
    SolutionTrackListItem,
    TaxonomyTermRead,
)
from app.services.catalog import get_public_solution_track, list_public_solution_tracks

router = APIRouter(prefix="/solution-tracks", tags=["public-catalog"])


def _serialize_offering(offering: ServiceOffering) -> ServiceOfferingRead:
    return ServiceOfferingRead(
        slug=offering.slug,
        title=offering.title,
        kicker=offering.kicker,
        description=offering.description,
        display_order=offering.display_order,
        taxonomy_terms=[
            TaxonomyTermRead.model_validate(link.term)
            for link in sorted(offering.taxonomy_links, key=lambda link: (link.term.group.value, link.term.label.lower()))
        ],
    )


def _serialize_track_detail(track: SolutionTrack) -> SolutionTrackDetail:
    return SolutionTrackDetail(
        slug=track.slug,
        title=track.title,
        short_summary=track.short_summary,
        hero_title=track.hero_title,
        hero_body=track.hero_body,
        cta_label=track.cta_label,
        cta_target=track.cta_target,
        display_order=track.display_order,
        meta_title=track.meta_title,
        meta_description=track.meta_description,
        offerings=[
            _serialize_offering(offering)
            for offering in track.offerings
            if offering.publication_status == PublicationStatus.published
        ],
        endpoint_rows=[EndpointCatalogRowRead.model_validate(row) for row in track.endpoint_rows],
    )


@router.get("", response_model=list[SolutionTrackListItem])
def read_solution_tracks(session: DBSession) -> list[SolutionTrackListItem]:
    tracks = list_public_solution_tracks(session)
    return [SolutionTrackListItem.model_validate(track) for track in tracks]


@router.get("/{slug}", response_model=SolutionTrackDetail)
def read_solution_track(slug: str, session: DBSession) -> SolutionTrackDetail:
    track = get_public_solution_track(session, slug=slug)
    return _serialize_track_detail(track)