FROM node:20-slim AS base
WORKDIR /app
COPY package*.json ./
RUN rm -f package-lock.json && npm install
COPY . .

# ── Development ──────────────────────────────────────────────
FROM base AS development
EXPOSE 5173
CMD ["npm", "run", "dev"]

# ── Production ───────────────────────────────────────────────
FROM base AS builder
RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]