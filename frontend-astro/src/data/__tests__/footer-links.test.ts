import { describe, it, expect } from 'vitest';
import { FOOTER_LINK_GROUPS } from '../footer-links';

describe('FOOTER_LINK_GROUPS', () => {
  it('has groups', () => {
    expect(FOOTER_LINK_GROUPS.length).toBeGreaterThan(0);
  });

  it('every group has a heading and links', () => {
    for (const group of FOOTER_LINK_GROUPS) {
      expect(group.heading).toBeTruthy();
      expect(group.links.length).toBeGreaterThan(0);
    }
  });

  it('every link has href and label', () => {
    for (const group of FOOTER_LINK_GROUPS) {
      for (const link of group.links) {
        expect(link.href, `href missing in group "${group.heading}"`).toBeTruthy();
        expect(link.label, `label missing in group "${group.heading}"`).toBeTruthy();
      }
    }
  });
});
