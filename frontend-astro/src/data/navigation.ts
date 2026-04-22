export interface NavChildLink {
  href: string;
  label: string;
}

export interface NavItem {
  href: string;
  label: string;
  matchPath: string;
  children?: NavChildLink[];
}

export const PRIMARY_NAV_ITEMS: NavItem[] = [
  { href: '/', label: 'Home', matchPath: '' },
  { href: '/about', label: 'About', matchPath: 'about' },
  {
    href: '/services',
    label: 'Services',
    matchPath: 'services',
    children: [
      { href: '/services/cybersecurity', label: 'Cybersecurity' },
      { href: '/services/it-security', label: 'IT Security' },
      { href: '/services/endpoint-management', label: 'Endpoint Management' },
      { href: '/services/core-industry', label: 'Core Industry' },
      { href: '/services/training', label: 'Training' },
    ],
  },
  { href: '/industries', label: 'Industries', matchPath: 'industries' },
  { href: '/careers', label: 'Careers', matchPath: 'careers' },
  { href: '/contact', label: 'Contact', matchPath: 'contact' },
];
