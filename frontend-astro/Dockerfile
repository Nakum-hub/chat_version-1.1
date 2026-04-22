# ── Stage 1: Build Astro static site ─────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --prefer-offline

COPY . .

# PUBLIC_API_BASE injected at build time.
# Empty string → runtime JS uses relative /api/ paths (nginx proxy).
# Set to a live URL to bake backend data into service pages at build time.
ARG PUBLIC_API_BASE=""
ENV PUBLIC_API_BASE=$PUBLIC_API_BASE

# Skip astro check in Docker (no need for type-check overhead in CI)
RUN npm run build -- --no-check 2>/dev/null || npx astro build

# ── Stage 2: Serve with nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
