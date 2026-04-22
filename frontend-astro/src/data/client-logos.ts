export type ClientLogo = {
  src: string;
  alt: string;
  name: string;
  cardWidth?: number;
  cardHeight?: number;
  cardPadding?: string;
  maxHeight?: number;
  scale?: number;
  tone?: 'dark' | 'light' | 'neutral';
};

type ClientLogoGroup = {
  description: string;
  folder: string;
  label: string;
  files: string[];
};

const logoGroups: ClientLogoGroup[] = [
  {
    folder: 'cybersecurity-clients',
    label: 'Cybersecurity clients',
    description: 'Security programs and transformation engagements',
    files: [
      'anoop ceramics.png',
      'cyber bee.png',
      'eton solutions.png',
      'incture.png',
      'kewaunee.png',
      'pine labs.png',
      'platform 3 solutions.png',
      'tech pennar.png',
      'zkteco.png',
    ],
  },
  {
    folder: 'endpoint-clients',
    label: 'Endpoint clients',
    description: 'Endpoint modernization and operational rollout programs',
    files: [
      'accenture.png',
      'aditya birla capital.png',
      'aditya birla group.png',
      'avendus.png',
      'hdfc.png',
      'icici lombard.png',
      'india post.png',
      'kluber lubrication.png',
      'larsen & toubro.png',
      'lic.png',
      'nkgsb.png',
      'rangsons aerospace.png',
      'reliance.png',
      'sbi.png',
      'societe general.png',
      'tata aig insurance.png',
      'tata power ddl.png',
      'vardhman textiles.png',
    ],
  },
];

const logoPresentation: Record<string, { cardWidth?: number; cardHeight?: number; cardPadding?: string; maxHeight?: number; scale?: number; tone?: ClientLogo['tone'] }> = {
  'anoop ceramics.png': { tone: 'light', scale: 1.12, cardWidth: 212, maxHeight: 50 },
  'cyber bee.png': { tone: 'light', scale: 1.02 },
  'eton solutions.png': { tone: 'light', scale: 1.04 },
  'incture.png': { scale: 1.18, cardWidth: 170, maxHeight: 42 },
  'kewaunee.png': { tone: 'light', scale: 1.16, cardWidth: 262, cardPadding: '0.55rem 0.75rem', maxHeight: 56 },
  'pine labs.png': { tone: 'dark', cardWidth: 206, maxHeight: 48 },
  'platform 3 solutions.png': { scale: 1.12, cardWidth: 188, maxHeight: 48 },
  'tech pennar.png': { tone: 'dark' },
  'zkteco.png': { scale: 1.65, cardWidth: 188, cardPadding: '0.45rem 0.65rem', maxHeight: 56 },
  'accenture.png': { tone: 'dark' },
  'aditya birla capital.png': { cardWidth: 214, maxHeight: 52, scale: 1.08 },
  'aditya birla group.png': { cardWidth: 198, maxHeight: 56, scale: 1.1 },
  'avendus.png': { tone: 'light', scale: 1.1, cardWidth: 214, maxHeight: 52 },
  'hdfc.png': { cardWidth: 224, maxHeight: 50, scale: 1.08 },
  'icici lombard.png': { cardWidth: 214, maxHeight: 50, scale: 1.08 },
  'india post.png': { cardWidth: 164, cardPadding: '0.1rem 0.2rem', maxHeight: 80, scale: 1.18 },
  'kluber lubrication.png': { tone: 'dark', cardWidth: 228, cardPadding: '0.12rem 0.24rem', maxHeight: 78, scale: 1.18 },
  'larsen & toubro.png': { tone: 'dark', cardWidth: 228, maxHeight: 50, scale: 1.12 },
  'nkgsb.png': { scale: 1.18, cardWidth: 220, maxHeight: 52 },
  'rangsons aerospace.png': { tone: 'dark', scale: 1.18, cardWidth: 204, maxHeight: 50 },
  'reliance.png': { scale: 1.18, cardWidth: 228, maxHeight: 52 },
  'societe general.png': { tone: 'dark', cardWidth: 224, maxHeight: 50, scale: 1.1 },
  'lic.png': { cardWidth: 212, maxHeight: 58, scale: 1.08 },
  'tata aig insurance.png': { cardWidth: 186, cardPadding: '0.45rem 0.55rem', maxHeight: 68, scale: 1.14 },
  'tata power ddl.png': { cardWidth: 214, maxHeight: 58, scale: 1.08 },
  'vardhman textiles.png': { tone: 'dark', cardWidth: 224, cardPadding: '0.18rem 0.28rem', maxHeight: 66, scale: 1.06 },
};

function formatLogoName(fileName: string) {
  const baseName = fileName.replace(/\.[^.]+$/, '');
  return baseName
    .split(/[\s_-]+/)
    .filter(Boolean)
    .map(token => (token.length <= 3 ? token.toUpperCase() : `${token.charAt(0).toUpperCase()}${token.slice(1)}`))
    .join(' ');
}

function createLogo(folder: string, fileName: string): ClientLogo {
  const name = formatLogoName(fileName);
  const presentation = logoPresentation[fileName] ?? {};

  return {
    name,
    alt: `${name} logo`,
    src: encodeURI(`/client-logos/${folder}/${fileName}`),
    cardWidth: presentation.cardWidth,
    cardHeight: presentation.cardHeight,
    cardPadding: presentation.cardPadding,
    maxHeight: presentation.maxHeight,
    scale: presentation.scale,
    tone: presentation.tone ?? 'neutral',
  };
}

export const clientLogoGroups = logoGroups.map(group => ({
  folder: group.folder,
  label: group.label,
  description: group.description,
  logos: group.files.map(fileName => createLogo(group.folder, fileName)),
}));

export const cybersecurityClientLogos = clientLogoGroups.find(g => g.folder === 'cybersecurity-clients')?.logos ?? [];
export const endpointClientLogos = clientLogoGroups.find(g => g.folder === 'endpoint-clients')?.logos ?? [];
