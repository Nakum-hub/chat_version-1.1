from pydantic import Field

from app.schemas.common import APIModel


class TaxonomyTermRead(APIModel):
    group: str
    slug: str
    label: str
    description: str | None


class ServiceOfferingRead(APIModel):
    slug: str
    title: str
    kicker: str
    description: str
    display_order: int
    taxonomy_terms: list[TaxonomyTermRead] = Field(default_factory=list)


class EndpointCatalogRowRead(APIModel):
    product_name: str
    solution_name: str
    service_name: str
    display_order: int


class SolutionTrackListItem(APIModel):
    slug: str
    title: str
    short_summary: str
    hero_title: str
    hero_body: str
    cta_label: str
    cta_target: str
    display_order: int


class SolutionTrackDetail(SolutionTrackListItem):
    meta_title: str | None
    meta_description: str | None
    offerings: list[ServiceOfferingRead] = Field(default_factory=list)
    endpoint_rows: list[EndpointCatalogRowRead] = Field(default_factory=list)