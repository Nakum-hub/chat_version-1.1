import { describe, it, expect } from 'vitest';
import { searchIndex } from '../search-index';

describe('searchIndex', () => {
  it('has entries', () => {
    expect(searchIndex.length).toBeGreaterThan(0);
  });

  it('has no duplicate URLs', () => {
    const urls = searchIndex.map(e => e.url);
    const unique = new Set(urls);
    expect(unique.size).toBe(urls.length);
  });

  it('every entry has required fields', () => {
    for (const entry of searchIndex) {
      expect(entry.title, `title missing on ${entry.url}`).toBeTruthy();
      expect(entry.url, `url missing on entry "${entry.title}"`).toBeTruthy();
      expect(entry.kind, `kind missing on ${entry.url}`).toBeTruthy();
      expect(entry.excerpt, `excerpt missing on ${entry.url}`).toBeTruthy();
      expect(Array.isArray(entry.keywords), `keywords not array on ${entry.url}`).toBe(true);
    }
  });

  it('includes expected pages', () => {
    const urls = new Set(searchIndex.map(e => e.url));
    expect(urls.has('/')).toBe(true);
    expect(urls.has('/contact')).toBe(true);
    expect(urls.has('/services/cybersecurity')).toBe(true);
    expect(urls.has('/services/it-security')).toBe(true);
    expect(urls.has('/services/endpoint-management')).toBe(true);
    expect(urls.has('/services/training')).toBe(true);
    expect(urls.has('/industries')).toBe(true);
  });

  it('does not expose admin page', () => {
    const urls = searchIndex.map(e => e.url);
    expect(urls).not.toContain('/admin');
  });

  it('contact entry has expected content', () => {
    const contact = searchIndex.find(e => e.url === '/contact');
    expect(contact).toBeDefined();
    expect(contact!.kind).toBe('Contact');
    expect(contact!.keywords).toContain('Contact');
    expect(contact!.keywords).toContain('Get Quote');
  });

  it('cybersecurity entry has VAPT keyword', () => {
    const entry = searchIndex.find(e => e.url === '/services/cybersecurity');
    expect(entry!.keywords).toContain('VAPT');
  });

  it('it-security entry has ISO 27001 keyword', () => {
    const entry = searchIndex.find(e => e.url === '/services/it-security');
    expect(entry!.keywords).toContain('ISO 27001');
  });
});
