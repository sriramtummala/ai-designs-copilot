# syntax=docker/dockerfile:1.4
# Build context: monorepo root
#   docker build -f apps/web/Dockerfile .
#   docker run -p 3000:80 <image>

# ── Stage 1: build ───────────────────────────────────────────────────────────
FROM node:22-slim AS builder

# Match the packageManager field in root package.json
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate

WORKDIR /app

# Copy workspace manifests before source so install is cached independently
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json                            apps/web/
COPY libs/ui/package.json                             libs/ui/
COPY libs/tokens/package.json                         libs/tokens/

RUN pnpm install --frozen-lockfile

# Copy source for the packages involved in the web build
COPY apps/web/   apps/web/
COPY libs/ui/    libs/ui/
COPY libs/tokens/ libs/tokens/

RUN pnpm --filter @ai-designops/web build

# ── Stage 2: serve with nginx ─────────────────────────────────────────────────
FROM nginx:1.27-alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=builder /app/apps/web/dist  /usr/share/nginx/html
COPY apps/web/nginx.conf                /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
