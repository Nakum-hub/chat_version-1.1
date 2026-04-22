# Plan: Migrate Cyberfyx Frontend to Astro

## Context

The Cyberfyx website currently has two frontend prototypes on separate branches:
- **`origin/test`** — user's preferred design: Navy `#0A1F3D` + Orange `#E78731`, Neulis Sans, dark/light theme toggle, glass-card UI, canvas grid animation, client-side site search. Clean but content is generic.
- **`origin/webpro`** — more polished content: enterprise B2B copy, ISO framework specifics, IBM Plex Mono accents, eyebrow/proof-pill patterns, full FastAPI contact form integration. Design relies on Three.js + GSAP (heavy, not SSG-friendly).

Goal: build a production-quality Astro 4.x site that takes **test branch's design system** (palette, dark mode, glass cards, canvas, search) and **webpro's content quality** (copy, structure, API integration). The result should be sleek and impressive for a cybersecurity firm — better than either prototype.

---

## Approach

- **Astro 4.x, output: static** — fully SSG, no React/Vue/Svelte
- **Vanilla TypeScript** for all client interactivity (no GSAP/Three.js — drop them)
- Located at `prototype/frontend-astro/` alongside existing prototypes
- 11 pages matching both branches
- API base configured via `PUBLIC_API_BASE` env var → `<meta name="cyberfyx-api-base">`

---

## Project Structure

```
prototype/frontend-astro/
├── astro.config.mjs
├── package.json            { astro: ^4.16, typescript: ^5.5 }
├── tsconfig.json           (extends astro/tsconfigs/strict, path aliases)
├── .env.example            PUBLIC_API_BASE=http://localhost:8001
├── public/
│   ├── favicon.svg         ← webpro
│   ├── cyberfyx-logo.svg   ← webpro
│   ├── logo.png            ← test (dark mode / fallback)
│   ├── images/
│   │   └── consulting-session.webp  ← webpro
│   └── textures/           ← webpro SVG backgrounds (optional decorative)
└── src/
    ├── layouts/
    │   └── BaseLayout.astro    SEO, anti-flash script, fonts, CSS, scripts
    ├── components/
    │   ├── Header.astro        nav, dropdown, theme toggle, search trigger
    │   ├── Footer.astro        4-col grid, data-contact-* attrs
    │   ├── SkipLink.astro
    │   ├── BackToTop.astro
    │   ├── PageHero.astro      inner-page 2-col hero with aside card
    │   ├── SectionHeader.astro eyebrow + headline + lede
    │   ├── GlassCard.astro     backdrop-blur card
    │   ├── FooterCta.astro     reusable bottom CTA band
    │   └── contact/
    │       └── ContactForm.astro
    ├── scripts/
    │   ├── theme.ts            dark/light toggle (client:load)
    │   ├── nav.ts              header scroll hide, mobile drawer, dropdown (client:load)
    │   ├── hero-grid.ts        canvas animation from test branch (client:load, home only)
    │   ├── animations.ts       IntersectionObserver fade-up + counter (client:idle)
    │   ├── search.ts           site search widget from test branch (client:idle)
    │   └── contact-form.ts     API submit + mailto fallback from webpro (client:load)
    ├── data/
    │   └── search-index.ts     typed SearchEntry[] — one per page, text from webpro copy
    ├── styles/
    │   ├── tokens.css          all CSS custom properties, both themes
    │   ├── global.css          imports tokens, reset, typography, components
    │   └── utilities.css       .container, .sr-only, .mono, .eyebrow, .lede, grids
    └── pages/
        ├── index.astro
        ├── about.astro
        ├── industries.astro
        ├── careers.astro
        ├── contact.astro
        └── services/
            ├── index.astro
            ├── cybersecurity.astro
            ├── it-security.astro
            ├── endpoint-management.astro
            ├── core-industry.astro
            └── training.astro
```

---

## Design System (CSS Merge Rules)

| Zone | Source | Notes |
|---|---|---|
| Color tokens, dark mode | **test** | `#0A1F3D` navy + `#E78731` orange, `[data-theme="dark"]` |
| Typography scale | **webpro** | `clamp()` h1–h6, `var(--font-display)` Neulis Sans |
| `.eyebrow`, `.mono` | **webpro** | IBM Plex Mono, orange pseudo-line |
| `.glass-card` | **test** | backdrop-filter blur; hover lift |
| `.surface` / service cards | **webpro** | elevated panels for inner pages |
| Header + nav | **test** | scroll-hide, glass blur, dark mode variants |
| Mobile nav drawer | **webpro** | accessible slide-in drawer |
| `.btn-*` | **test** | pill buttons, navy/orange |
| Hero layout | **test** | 2-col + canvas |
| Proof rail, stat cards | **webpro** | eyebrow patterns |
| Site search | **test** | entire `.site-search*` block |
| Contact form | **webpro** | `.field`, `.input`, status states |
| Footer grid | **webpro** | 4-col |

**Fonts loaded:**
```
Neulis Sans (300–800) + IBM Plex Mono (400–500) via Google Fonts
```
Use webpro's non-blocking `media="print" onload` pattern.

---

## Critical Implementation Details

### Anti-Flash Theme Script (`BaseLayout.astro`)
```html
<script is:inline>
  (function(){
    const t = localStorage.getItem('cyberfyx-theme') ||
      (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    if (t === 'dark') document.documentElement.setAttribute('data-theme','dark');
  })();
</script>
```
Must be before the stylesheet link. `is:inline` prevents Astro bundling.

### API Base (`BaseLayout.astro`)
```astro
<meta name="cyberfyx-api-base" content={import.meta.env.PUBLIC_API_BASE ?? ''}>
```
`contact-form.ts` reads this. Empty string → mailto fallback (no script change needed).

### Active Nav State (`Header.astro`)
Each page passes `currentPage` prop. Use `class:list={["nav-link", { active: currentPage === 'about' }]}`. Replaces the scroll-based approach from the test branch (doesn't work across pages).

### Client Script Directives

| Script | Directive | Reason |
|---|---|---|
| `theme.ts` | `client:load` | Immediate — toggle must work on paint |
| `nav.ts` | `client:load` | Mobile menu must be interactive |
| `hero-grid.ts` | `client:load` | Canvas starts on DOMContentLoaded |
| `contact-form.ts` | `client:load` | Form submission must be ready |
| `animations.ts` | `client:idle` | Non-critical on first paint |
| `search.ts` | `client:idle` | Non-critical on first paint |

`hero-grid.ts` guards with `if (!document.getElementById('hero-grid-canvas')) return;` — safe no-op on non-home pages.

---

## Pages and Content Sources

| Page | Layout | Content Source | Key Sections |
|---|---|---|---|
| `/` | BaseLayout | webpro copy, test structure | Hero + canvas, proof rail, stats, 5 solution cards, industry grid, delivery steps, footer CTA |
| `/about` | PageHero | webpro | Vision/mission, how-we-work, programme coverage |
| `/services` | PageHero | webpro | Selector band, 5 service cards, engagement model |
| `/services/cybersecurity` | PageHero | webpro lede + test service list | VAPT, vCISO, DPO, GRC, PCI DSS specifics |
| `/services/it-security` | PageHero | webpro lede + test service list | ISO 27001/27701/22301, cloud governance |
| `/services/endpoint-management` | PageHero | webpro lede + test service list | UEM, patching, monitoring, NOC |
| `/services/core-industry` | PageHero | webpro lede + test service list | ISO, SEDEX, FSC, fire safety, audits |
| `/services/training` | PageHero | webpro lede + test service list | GDPR, HIPAA, PCI DSS, ITIL, COBIT formats |
| `/industries` | PageHero | webpro | 6 industry windows with framework tags |
| `/careers` | PageHero | webpro | Working style, career area cards, HR CTA |
| `/contact` | BaseLayout | webpro | Split: contact info left, ContactForm right |

---

## Implementation Order

1. **Scaffold** — `npm create astro@latest`, config files, empty page structure
2. **Design system** — `tokens.css`, `global.css`, `utilities.css`
3. **BaseLayout** — anti-flash, fonts, SEO meta, slot
4. **Header + Footer + nav.ts + theme.ts** — shell works end-to-end
5. **Home page** — all 7 sections, canvas animation, animations.ts
6. **Reusable components** — PageHero, SectionHeader, GlassCard, FooterCta
7. **Inner pages** — services/, about, industries, careers (shortest first)
8. **Contact page + contact-form.ts** — test against FastAPI backend
9. **Site search** — search-index.ts + search.ts
10. **QA** — Lighthouse ≥90 perf, ≥95 a11y; `astro check`; dark+light visual pass; reduced-motion; keyboard nav

---

## SEO Titles

| Page | `<title>` |
|---|---|
| Home | `Cyberfyx \| Cybersecurity and Operational Resilience` |
| About | `About Cyberfyx \| Advisory, Delivery, and Operational Depth` |
| Services | `Solutions \| Cyberfyx` |
| Cybersecurity | `Cybersecurity \| Cyberfyx` |
| IT Security | `IT Security \| Cyberfyx` |
| Endpoint Ops | `Endpoint Operations \| Cyberfyx` |
| Core Industry | `Core Industry Services \| Cyberfyx` |
| Training | `Training \| Cyberfyx` |
| Industries | `Industries \| Cyberfyx Sector Coverage` |
| Careers | `Careers \| Cyberfyx` |
| Contact | `Contact Cyberfyx \| Start a Security Conversation` |

---

## Verification

```bash
cd prototype/frontend-astro
npm run dev          # smoke test all 11 routes
npm run build        # verify all pages SSG without error
npm run preview      # Lighthouse audit on built output
npx astro check      # TypeScript errors
```

End-to-end: fill out contact form on `/contact` with FastAPI backend running at `localhost:8001` (set `PUBLIC_API_BASE` in `.env`). Verify 201 response and success message. Set `PUBLIC_API_BASE=` (empty) and verify mailto fallback opens.
