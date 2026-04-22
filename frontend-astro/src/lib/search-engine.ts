/**
 * Pure search-engine logic — no DOM, no browser globals.
 * Imported by both scripts/search.ts (browser) and tests.
 */

import type { SearchEntry } from '../data/search-index';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface SearchTerm {
  label: string;
  normalized: string;
  compact: string;
  weight: number;
}

export interface SearchIndexEntry {
  excerpt: string;
  href: string;
  kind: string;
  keywords: string[];
  section: string;
  text: string;
  title: string;
  excerptText: string;
  fullText: string;
  searchTerms: SearchTerm[];
  titleText: string;
}

export interface SearchMatch {
  entry: SearchIndexEntry;
  matchedTerms: string[];
  score: number;
}

type BackendSearchEntry = {
  excerpt?: string;
  href?: string;
  kind?: string;
  keywords?: string[];
  section?: string;
  text?: string;
  title?: string;
  url?: string;
};

// ─── Text helpers ─────────────────────────────────────────────────────────────

export function normalizeText(...parts: Array<string | undefined>) {
  return parts
    .join(' ')
    .toLowerCase()
    .replace(/[^a-z0-9\s./+-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function compactText(value: string) {
  return value.replace(/\s+/g, '');
}

export function deriveSection(href: string) {
  if (href === '/') return 'Home';

  return href
    .replace(/\//g, ' ')
    .trim()
    .replace(/-/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
}

export function splitTopics(text: string) {
  return text
    .split('|')
    .map(value => value.trim())
    .filter(Boolean);
}

export function uniqueTerms(values: string[]) {
  const unique: string[] = [];
  for (const value of values) {
    if (value && !unique.includes(value)) {
      unique.push(value);
    }
  }
  return unique;
}

export function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ─── Index building ───────────────────────────────────────────────────────────

export function buildSearchTerms(entry: {
  href: string;
  kind: string;
  keywords: string[];
  section: string;
  text: string;
  title: string;
}) {
  const terms: SearchTerm[] = [];

  const pushTerm = (label: string, weight: number) => {
    const normalized = normalizeText(label);
    if (!normalized || terms.some(term => term.normalized === normalized)) return;

    terms.push({
      label,
      normalized,
      compact: compactText(normalized),
      weight,
    });
  };

  pushTerm(entry.title, 70);
  pushTerm(entry.kind, 26);
  pushTerm(entry.section, 24);
  for (const keyword of entry.keywords) {
    pushTerm(keyword, 64);
  }
  for (const topic of splitTopics(entry.text)) {
    pushTerm(topic, 52);
  }

  for (const part of entry.href.split('/').filter(Boolean)) {
    pushTerm(part.replace(/-/g, ' '), 18);
  }

  return terms;
}

export function createSearchEntry(params: {
  excerpt?: string;
  href: string;
  kind?: string;
  keywords?: string[];
  section: string;
  text?: string;
  title: string;
}): SearchIndexEntry {
  const excerpt = params.excerpt?.trim() ?? '';
  const keywords = uniqueTerms(Array.isArray(params.keywords) ? params.keywords.filter(Boolean) : []);
  const kind = params.kind?.trim() || 'Page';
  const text = params.text?.trim() ?? '';

  const searchTerms = buildSearchTerms({
    href: params.href,
    kind,
    keywords,
    section: params.section,
    text,
    title: params.title,
  });

  return {
    excerpt,
    href: params.href,
    kind,
    keywords,
    section: params.section,
    text,
    title: params.title,
    excerptText: normalizeText(excerpt),
    fullText: normalizeText(params.title, kind, params.section, keywords.join(' '), text, excerpt, params.href),
    searchTerms,
    titleText: normalizeText(params.title),
  };
}

export function normalizeStaticEntries(entries: SearchEntry[]): SearchIndexEntry[] {
  return entries.map(entry => {
    const section = deriveSection(entry.url);
    return createSearchEntry({
      excerpt: entry.excerpt,
      href: entry.url,
      kind: entry.kind,
      keywords: entry.keywords,
      section,
      text: entry.text,
      title: entry.title,
    });
  });
}

export function normalizeBackendEntry(entry: BackendSearchEntry): SearchIndexEntry | null {
  const href = typeof entry.href === 'string'
    ? entry.href
    : typeof entry.url === 'string'
      ? entry.url
      : null;

  if (!href || typeof entry.title !== 'string') return null;

  const section = typeof entry.section === 'string' && entry.section.trim()
    ? entry.section.trim()
    : deriveSection(href);

  return createSearchEntry({
    excerpt: typeof entry.excerpt === 'string' ? entry.excerpt : undefined,
    href,
    kind: typeof entry.kind === 'string' ? entry.kind : undefined,
    keywords: Array.isArray(entry.keywords) ? entry.keywords : [],
    section,
    text: typeof entry.text === 'string' ? entry.text : undefined,
    title: entry.title,
  });
}

export function normalizeSearchEntries(data: unknown): SearchIndexEntry[] {
  if (!Array.isArray(data)) return [];

  return data
    .map(entry => normalizeBackendEntry((entry ?? {}) as BackendSearchEntry))
    .filter((entry): entry is SearchIndexEntry => entry !== null);
}

// ─── Scoring ──────────────────────────────────────────────────────────────────

function hasWordMatch(value: string, token: string) {
  if (!value || !token) return false;
  return value.split(' ').includes(token);
}

function scoreTerm(term: SearchTerm, token: string) {
  const compactToken = compactText(token);

  if (term.normalized === token || term.compact === compactToken) {
    return term.weight + 30;
  }

  if (hasWordMatch(term.normalized, token)) {
    return term.weight + 16;
  }

  if (term.normalized.startsWith(token) || term.compact.startsWith(compactToken)) {
    return term.weight + 12;
  }

  if (term.normalized.includes(token) || term.compact.includes(compactToken)) {
    return term.weight + 6;
  }

  return 0;
}

function phraseBonus(entry: SearchIndexEntry, normalizedQuery: string) {
  let score = 0;

  for (const term of entry.searchTerms) {
    if (term.normalized === normalizedQuery || term.compact === compactText(normalizedQuery)) {
      score = Math.max(score, 36);
    } else if (term.normalized.startsWith(normalizedQuery)) {
      score = Math.max(score, 24);
    } else if (term.normalized.includes(normalizedQuery)) {
      score = Math.max(score, 14);
    }
  }

  if (entry.titleText.startsWith(normalizedQuery)) {
    score = Math.max(score, 20);
  }

  return score;
}

export function scoreSearchToken(entry: SearchIndexEntry, token: string) {
  let bestScore = 0;
  const labels: string[] = [];

  for (const term of entry.searchTerms) {
    const termScore = scoreTerm(term, token);
    if (termScore > bestScore) {
      bestScore = termScore;
      labels.length = 0;
      labels.push(term.label);
    } else if (termScore === bestScore && termScore > 0 && !labels.includes(term.label)) {
      labels.push(term.label);
    }
  }

  if (bestScore === 0 && entry.fullText.includes(token)) {
    bestScore = 8;
  }

  if (bestScore === 0) {
    return null;
  }

  return { labels, score: bestScore };
}

export function scoreSearchEntry(entry: SearchIndexEntry, queryTokens: string[], normalizedQuery: string): SearchMatch | null {
  let totalScore = 0;
  const matchedTerms: string[] = [];

  for (const token of queryTokens) {
    const tokenMatch = scoreSearchToken(entry, token);
    if (!tokenMatch) {
      return null;
    }

    totalScore += tokenMatch.score;
    for (const label of tokenMatch.labels) {
      if (!matchedTerms.includes(label)) {
        matchedTerms.push(label);
      }
    }
  }

  totalScore += phraseBonus(entry, normalizedQuery);

  return {
    entry,
    matchedTerms: matchedTerms.slice(0, 3),
    score: totalScore,
  };
}

export function runSearch(index: SearchIndexEntry[], query: string): SearchMatch[] {
  const normalizedQuery = normalizeText(query);
  if (!normalizedQuery) return [];

  const queryTokens = normalizedQuery.split(/\s+/).filter(Boolean);
  return index
    .map(entry => scoreSearchEntry(entry, queryTokens, normalizedQuery))
    .filter((match): match is SearchMatch => match !== null)
    .sort((a, b) => b.score - a.score || a.entry.title.localeCompare(b.entry.title))
    .slice(0, 8);
}
