/**
 * Build-time API utilities - runs during `astro build` in component frontmatter.
 * Falls back to null on any error; callers use fallback data.
 */

const BUILD_TIMEOUT_MS = 6000;

async function buildFetch<T>(url: string): Promise<T | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), BUILD_TIMEOUT_MS);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ─── Type definitions matching backend schemas ────────────────────────────────

export interface TaxonomyTerm {
  group: string;
  slug: string;
  label: string;
  description: string | null;
}

export interface ServiceOffering {
  slug: string;
  title: string;
  kicker: string;
  description: string;
  display_order: number;
  taxonomy_terms: TaxonomyTerm[];
}

export interface EndpointCatalogRow {
  product_name: string;
  solution_name: string;
  service_name: string;
  display_order: number;
}

export interface SolutionTrackDetail {
  slug: string;
  title: string;
  short_summary: string;
  hero_title: string;
  hero_body: string;
  cta_label: string;
  cta_target: string;
  display_order: number;
  meta_title: string | null;
  meta_description: string | null;
  offerings: ServiceOffering[];
  endpoint_rows: EndpointCatalogRow[];
}

export interface OfficeRegion {
  slug: string;
  label: string;
  display_order: number;
}

export interface ContactProfile {
  profile_key: string;
  sales_email: string;
  hr_email: string | null;
  primary_phone: string;
  headquarters_name: string;
  headquarters_address: string;
  map_url: string;
  office_regions: OfficeRegion[];
  interest_options: Array<{
    slug: string;
    label: string;
    route_target: string;
    display_order: number;
  }>;
}

// ─── Public API fetchers ──────────────────────────────────────────────────────

const API_BASE = import.meta.env.PUBLIC_API_BASE ?? '';

export async function fetchTrackData(slug: string): Promise<SolutionTrackDetail | null> {
  if (!API_BASE) return null;
  return buildFetch<SolutionTrackDetail>(
    `${API_BASE}/api/v1/public/solution-tracks/${slug}`
  );
}

export async function fetchContactProfile(): Promise<ContactProfile | null> {
  if (!API_BASE) return null;
  return buildFetch<ContactProfile>(`${API_BASE}/api/v1/public/site/contact-profile`);
}
