export interface FooterLink {
  href: string;
  label: string;
}

export interface FooterLinkGroup {
  heading: string;
  links: FooterLink[];
}

export const FOOTER_LINK_GROUPS: FooterLinkGroup[] = [
  {
    heading: 'Quick Links',
    links: [
      { href: '/about', label: 'About Us' },
      { href: '/services', label: 'Our Services' },
      { href: '/industries', label: 'Industries' },
      { href: '/careers', label: 'Careers' },
    ],
  },
  {
    heading: 'Our Services',
    links: [
      { href: '/services/cybersecurity', label: 'Cybersecurity' },
      { href: '/services/it-security', label: 'IT Security' },
      { href: '/services/endpoint-management', label: 'Endpoint Management' },
      { href: '/services', label: 'View All' },
    ],
  },
];
