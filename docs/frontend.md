# Frontend Documentation

The Cyberfyx frontend is built with **Astro 4.x**, delivering a high-performance, secure, and SEO-optimized user experience.

## Technical Stack

- **Framework**: Astro 4.16+
- **Styling**: Vanilla CSS with a custom design system.
- **Interactivity**: Vanilla TypeScript (no heavy libraries like React/Vue).
- **Icons**: SVG-based system.
- **Animations**: Canvas-based grid (homepage) and CSS-based glassmorphism effects.

## Project Structure

```text
frontend-astro/
├── src/
│   ├── layouts/        # Shared page layouts (BaseLayout)
│   ├── components/     # Reusable UI components (Header, Footer, Cards)
│   ├── pages/          # Routing & page definitions
│   ├── scripts/        # Client-side TypeScript (theme, navigation, forms)
│   ├── styles/         # CSS tokens, global styles, and utilities
│   └── data/           # Static data used for search and catalog
├── public/             # Static assets (images, logos, textures)
└── astro.config.mjs    # Astro configuration
```

## Key Features

### 🎨 Design System
The site uses a custom-built design system with:
- **Palette**: Navy (`#0A1F3D`) and Orange (`#E78731`).
- **Dark/Light Mode**: User-controllable theme with persistence via `localStorage` and a flicker-preventing script.
- **Glassmorphism**: Backdrop blur effects on cards and navigation to create a premium feel.

### ⚡ Client-Side Interactivity
- **Theme Management**: `theme.ts` handles the light/dark toggle.
- **Navigation**: `nav.ts` provides responsive header behavior and mobile menus.
- **Search**: `search.ts` implements a client-side search indexing and widget for fast discovery.
- **Contact Form**: `contact-form.ts` manages asynchronous form submission to the FastAPI backend.

### 🔍 SEO & Accessibility
- **Semantic HTML**: Proper use of `<header>`, `<footer>`, `<main>`, and hierarchical headings.
- **Pre-rendering**: All marketing content is pre-rendered for maximum search engine visibility and performance.
- **Speed**: Minimal JavaScript overhead and efficient asset loading patterns.

## Configuration & Setup

1. **Environment Variables**: Use `frontend-astro/.env` to configure FastAPI integration.
   ```env
   # Used by build/runtime fetches from Astro frontmatter.
   PUBLIC_API_BASE=http://127.0.0.1:8000

   # Used in local `npm run dev` so `/api/*` is proxied to FastAPI.
   API_PROXY_TARGET=http://127.0.0.1:8000
   ```
2. **Commands**:
   - `npm install`: Install dependencies.
   - `npm run dev`: Start the local development server at `localhost:4321`.
   - `npm run build`: Generate the production-ready static site in `dist/`.
   - `npm run preview`: Preview the production build locally.
