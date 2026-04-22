import { searchIndex as staticIndex, type SearchEntry } from '../data/search-index';

const POPULAR_SEARCHES = [
  'ISO 27001',
  'VAPT',
  'SOC 2',
  'Endpoint',
  'Training',
  'Get Quote',
];

interface SearchTerm {
  label: string;
  normalized: string;
  compact: string;
  weight: number;
}

interface SearchIndexEntry {
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

interface SearchMatch {
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

let resolvedIndex: SearchIndexEntry[] = normalizeStaticEntries(staticIndex);

async function initSearchIndex(apiBaseUrl: string) {
  try {
    const resolvedApiBaseUrl = resolveClientApiBaseUrl(apiBaseUrl);
    const res = await fetch(`${resolvedApiBaseUrl}/api/v1/public/site/search-index`);
    if (!res.ok) return;

    const data = await res.json();
    const normalized = normalizeSearchEntries(data);
    if (normalized.length > 0) {
      resolvedIndex = normalized;
    }
  } catch {
    // Keep the bundled static index if the backend search API is unavailable.
  }
}

function bootSearch() {
  initSiteSearch();

  const metaTag = document.querySelector('meta[name="cyberfyx-api-base"]');
  const apiBaseUrl = metaTag ? (metaTag.getAttribute('content') ?? '') : '';
  void initSearchIndex(apiBaseUrl);
}

document.addEventListener('DOMContentLoaded', bootSearch);
document.addEventListener('astro:page-load', bootSearch);

function initSiteSearch() {
  const searchWrapperNode = document.querySelector('[data-site-search]') as HTMLDivElement | null;
  if (!searchWrapperNode || searchWrapperNode.dataset.searchInit === '1') return;

  const inputNode = searchWrapperNode.querySelector('.site-search-input') as HTMLInputElement | null;
  const resultsNode = searchWrapperNode.querySelector('.site-search-results') as HTMLDivElement | null;
  const closeButtonNode = searchWrapperNode.querySelector('.site-search-close') as HTMLButtonElement | null;

  if (!inputNode || !resultsNode || !closeButtonNode) return;

  const searchWrapper = searchWrapperNode;
  const input = inputNode;
  const results = resultsNode;
  const closeButton = closeButtonNode;
  let lastResults: SearchMatch[] = [];

  searchWrapper.dataset.searchInit = '1';

  function renderResults(query = '') {
    const normalizedQuery = normalizeText(query);
    if (!normalizedQuery) {
      lastResults = [];
      results.innerHTML = renderEmptyState();
      return;
    }

    const queryTokens = normalizedQuery.split(/\s+/).filter(Boolean);
    lastResults = resolvedIndex
      .map(entry => scoreSearchEntry(entry, queryTokens, normalizedQuery))
      .filter((match): match is SearchMatch => match !== null)
      .sort((left, right) => right.score - left.score || left.entry.title.localeCompare(right.entry.title))
      .slice(0, 8);

    if (!lastResults.length) {
      results.innerHTML = renderNoResultsState();
      return;
    }

    results.innerHTML = lastResults.map(match => renderSearchResult(match)).join('');
  }

  function openSearch() {
    searchWrapper.classList.add('open');
    renderResults(input.value);
  }

  function closeSearch({ clear = false } = {}) {
    if (clear) {
      input.value = '';
      lastResults = [];
    }
    searchWrapper.classList.remove('open');
  }

  function runChipSearch(query: string) {
    input.value = query;
    openSearch();
    input.focus();
  }

  input.addEventListener('focus', () => {
    openSearch();
  });

  input.addEventListener('input', () => {
    openSearch();
  });

  closeButton.addEventListener('click', () => {
    closeSearch({ clear: true });
    input.focus();
  });

  document.addEventListener('click', event => {
    if (searchWrapper.classList.contains('open') && !searchWrapper.contains(event.target as Node)) {
      closeSearch();
    }
  });

  results.addEventListener('click', event => {
    const target = event.target as HTMLElement;
    const chip = target.closest('[data-search-chip]') as HTMLElement | null;
    if (chip) {
      event.preventDefault();
      event.stopPropagation();
      runChipSearch(chip.dataset.searchChip ?? '');
      return;
    }

    const resultLink = target.closest('.site-search-result');
    if (resultLink) {
      closeSearch();
    }
  });

  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      input.focus();
      openSearch();
    }

    if (event.key === 'Escape' && searchWrapper.classList.contains('open')) {
      closeSearch();
      input.blur();
    }

    if (event.key === 'Enter' && document.activeElement === input && searchWrapper.classList.contains('open') && lastResults[0]) {
      event.preventDefault();
      window.location.href = lastResults[0].entry.href;
    }
  });

  renderResults();
}

function renderEmptyState() {
  return `
    <div class="site-search-empty">
      <strong>Popular searches</strong>
      <p>Search by framework, service, or action.</p>
      <div class="site-search-chip-list">
        ${POPULAR_SEARCHES.map(chip => renderSearchChip(chip)).join('')}
      </div>
    </div>
  `;
}

function renderNoResultsState() {
  return `
    <div class="site-search-empty">
      <strong>No direct match</strong>
      <p>Try a framework, service, or action instead.</p>
      <div class="site-search-chip-list">
        ${POPULAR_SEARCHES.slice(0, 4).map(chip => renderSearchChip(chip)).join('')}
      </div>
    </div>
  `;
}

function renderSearchChip(label: string) {
  return `<button class="site-search-chip" type="button" data-search-chip="${escapeHtml(label)}">${escapeHtml(label)}</button>`;
}

function renderSearchResult(match: SearchMatch) {
  const { entry, matchedTerms } = match;
  const tags = matchedTerms.length
    ? `<div class="site-search-result-tags">${matchedTerms.map(term => `<span class="site-search-result-tag">${escapeHtml(term)}</span>`).join('')}</div>`
    : '';

  return `
    <a class="site-search-result" href="${escapeHtml(entry.href)}">
      <div class="site-search-result-header">
        <strong>${escapeHtml(entry.title)}</strong>
        <span class="site-search-kind">${escapeHtml(entry.kind)}</span>
      </div>
      <small class="site-search-result-copy">${escapeHtml(entry.excerpt || entry.section)}</small>
      ${tags}
    </a>
  `;
}

function scoreSearchEntry(entry: SearchIndexEntry, queryTokens: string[], normalizedQuery: string): SearchMatch | null {
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

function scoreSearchToken(entry: SearchIndexEntry, token: string) {
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

  return {
    labels,
    score: bestScore,
  };
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

function hasWordMatch(value: string, token: string) {
  if (!value || !token) return false;
  return value.split(' ').includes(token);
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function resolveClientApiBaseUrl(apiBaseUrl: string) {
  if (!apiBaseUrl || typeof window === 'undefined') {
    return apiBaseUrl;
  }

  const isLocalApp = ['127.0.0.1', 'localhost'].includes(window.location.hostname);
  if (!isLocalApp) {
    return apiBaseUrl;
  }

  try {
    const target = new URL(apiBaseUrl);
    if (['127.0.0.1', 'localhost'].includes(target.hostname)) {
      return '';
    }
  } catch {
    return apiBaseUrl;
  }

  return apiBaseUrl;
}

function normalizeText(...parts: Array<string | undefined>) {
  return parts
    .join(' ')
    .toLowerCase()
    .replace(/[^a-z0-9\s./+-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function compactText(value: string) {
  return value.replace(/\s+/g, '');
}

function deriveSection(href: string) {
  if (href === '/') return 'Home';

  return href
    .replace(/\//g, ' ')
    .trim()
    .replace(/-/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
}

function splitTopics(text: string) {
  return text
    .split('|')
    .map(value => value.trim())
    .filter(Boolean);
}

function uniqueTerms(values: string[]) {
  const unique: string[] = [];
  for (const value of values) {
    if (value && !unique.includes(value)) {
      unique.push(value);
    }
  }
  return unique;
}

function buildSearchTerms(entry: {
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

function createSearchEntry(params: {
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

function normalizeStaticEntries(entries: SearchEntry[]): SearchIndexEntry[] {
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

function normalizeBackendEntry(entry: BackendSearchEntry): SearchIndexEntry | null {
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

function normalizeSearchEntries(data: unknown): SearchIndexEntry[] {
  if (!Array.isArray(data)) return [];

  return data
    .map(entry => normalizeBackendEntry((entry ?? {}) as BackendSearchEntry))
    .filter((entry): entry is SearchIndexEntry => entry !== null);
}
