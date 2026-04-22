import { describe, it, expect } from 'vitest';
import { PRIMARY_NAV_ITEMS } from '../navigation';

describe('PRIMARY_NAV_ITEMS', () => {
  it('has entries', () => {
    expect(PRIMARY_NAV_ITEMS.length).toBeGreaterThan(0);
  });

  it('every item has href, label, and matchPath', () => {
    for (const item of PRIMARY_NAV_ITEMS) {
      expect(item.href, `href missing on "${item.label}"`).toBeTruthy();
      expect(item.label, `label missing on "${item.href}"`).toBeTruthy();
      expect(typeof item.matchPath).toBe('string');
    }
  });

  it('includes top-level pages', () => {
    const hrefs = PRIMARY_NAV_ITEMS.map(i => i.href);
    expect(hrefs).toContain('/');
    expect(hrefs).toContain('/about');
    expect(hrefs).toContain('/services');
    expect(hrefs).toContain('/contact');
  });

  it('services item has children', () => {
    const services = PRIMARY_NAV_ITEMS.find(i => i.href === '/services');
    expect(services?.children?.length).toBeGreaterThan(0);
  });

  it('service children all have href and label', () => {
    const services = PRIMARY_NAV_ITEMS.find(i => i.href === '/services');
    for (const child of services!.children!) {
      expect(child.href).toBeTruthy();
      expect(child.label).toBeTruthy();
    }
  });
});
